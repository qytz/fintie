# -*- coding: utf-8 -*-
# This file is part of fintie.

# Copyright (C) 2018-present qytz <hhhhhf@foxmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""行情获取模块

本模块负责获取股票的历史交易行情信息。
获取到的行情信息不包括今天的行情（18点之后可获取今天的行情）
会获取三种频度的数据，其他频度的数据基于这三种进行resample：

    * 成交明细
    * 分钟bar数据
    * 日bar数据

存储方式，历史年份每年的数据存储一个bcolz的ctable，当年每月存储一个bcolz的ctable，
年份结束的时候合并成一个整年的ctable归档；当月的数据在每天更新并重新生成。

成交明细获取通道包括：

    * 新浪财经成交明细（历史数据教全，优先从此通道获取）

        Get http://market.finance.sina.com.cn/downxls.php?date=2017-06-20&symbol=sz000001

    * 腾讯财经成交明细（从20170103开始提供）

        Get http://stock.gtimg.cn/data/index.php?appn=detail&action=download&c=sh601633&d=20170606
        Get http://stock.gtimg.cn/data/index.php?appn=detail&action=download&c=sz000651&d=20170606

分钟bar获取通道包括：
日bar获取通道包括：

    http://www.cninfo.com.cn/cninfo-new/index


TODO: add default http headers
headers = {"X-Forwarded-For": ipAddress}

"""
import os
import io
import time
import json
import logging
import asyncio
from datetime import date, datetime, timedelta

from sqlalchemy import create_engine
from dateutil.parser import parse as parse_dt

import aiohttp
import pandas as pd
from plumbum import cli

from .utils import iter_date, parse_date
from .cli import FinApp, FinTie
from .web import WebClient


logger = logging.getLogger(__file__)


@FinTie.subcommand('quotes')
class QuotesApp(FinApp, WebClient):
    _start_date = date.today() - timedelta(days=1)
    _end_date = date.today()
    _codes = []
    _freq = 'day'

    char_buy = 1
    char_sell = 2
    char_neuter = 0

    async def get_tick_quotes_sina(self, code, quotes_date, session):
        """从新浪获取某只股票一天的tick行情数据

        Get http://market.finance.sina.com.cn/downxls.php?date=2017-06-20&symbol=sz000001
        """
        logger.info('Starting downlowd %s@%s quotes from sina', code, quotes_date)
        code = ''.join(code.split('.'))
        if isinstance(quotes_date, (date, datetime)):
            quotes_date = quotes_date.strftime('%Y-%m-%d')

        year, month, day = int(quotes_date[:4]), int(quotes_date[5:7]), int(quotes_date[8:10])
        url = 'http://market.finance.sina.com.cn/downxls.php'
        params = {'symbol': code, 'date': quotes_date}
        try:
            async with session.get(url,
                                   headers=self.dfl_headers,
                                   params=params) as resp:
                raw = await resp.read()
        except aiohttp.ServerTimeoutError:
            logger.warning('connection (%s) timeout', url)
            return None
        except asyncio.TimeoutError:
            logger.warning('read from (%s) timeout', url)
            return None
        dataio = io.StringIO(raw.decode('gbk'))
        df = pd.read_csv(dataio, sep='\t')
        df = df.rename(columns={
            '成交时间': 'time',
            '成交价格': 'price',
            '价格变动': 'price_change',
            '成交量(手)': 'volume',
            '成交额(元)': 'turnover',
            '性质': 'character'})

        df['time'] = df['time'].apply(
            lambda x: pd.to_datetime(x, format='%H:%M:%S').replace(
                year=year, month=month, day=day))

        df.set_index('time', inplace=True)
        df['volume'] = df['volume'] * 100
        df.character.replace({
            '买盘': self.char_buy,
            '卖盘': self.char_sell,
            '中性盘': self.char_neuter}, inplace=True)
        logger.info('Downlowd %s@%s quotes from sina complete', code, quotes_date)
        return df.iloc[::-1]

    async def get_tick_quotes_qq(self, code, quotes_date, session):
        """从腾讯获取某只股票一天的tick行情数据

        腾讯财经成交明细（从20170103开始提供）
        Get http://stock.gtimg.cn/data/index.php?appn=detail&action=download&c=sh601633&d=20170606
        Get http://stock.gtimg.cn/data/index.php?appn=detail&action=download&c=sz000651&d=20170606
        """
        logger.info('Starting downlowd %s@%s quotes from qq', code, quotes_date)
        code = ''.join(code.split('.'))
        if isinstance(quotes_date, (date, datetime)):
            quotes_date = quotes_date.strftime('%Y%m%d')
        elif len(quotes_date.split('-')) != 1:
            quotes_date = ''.join(quotes_date.split('-'))

        year, month, day = int(quotes_date[:4]), int(quotes_date[4:6]), int(quotes_date[6:8])
        url = 'http://stock.gtimg.cn/data/index.php'
        params = {'appn': 'detail', 'action': 'download', 'c': code, 'd': quotes_date}
        try:
            async with session.get(url,
                                   headers=self.dfl_headers, params=params) as resp:
                raw = await resp.read()
        except aiohttp.ServerTimeoutError:
            logger.warning('connection (%s) timeout', url)
            return None
        except asyncio.TimeoutError:
            logger.warning('read from (%s) timeout', url)
            return None
        dataio = io.StringIO(raw.decode('gbk'))
        df = pd.read_csv(dataio, sep='\t')
        df = df.rename(
            columns={
                '成交时间': 'time',
                '成交价格': 'price',
                '价格变动': 'price_change',
                '成交量(手)': 'volume',
                '成交额(元)': 'turnover',
                '性质': 'character'})

        df['time'] = df['time'].apply(
            lambda x: pd.to_datetime(x, format='%H:%M:%S').replace(
                year=year, month=month, day=day))

        df.set_index('time', inplace=True)
        df['volume'] = df['volume'] * 100
        df.character.replace({
            '买盘': self.char_buy,
            '卖盘': self.char_sell,
            '中性': self.char_neuter}, inplace=True)
        logger.info('Downlowd %s@%s quotes from qq complete', code, quotes_date)
        return df

    async def get_tick_quotes_163(self, code, quotes_date, session):
        """从网易财经获取某只股票一天的tick行情数据

        网易财经成交明细
        sz: 1
        sh: 0
        Get http://quotes.money.163.com/cjmx/2018/20180529/1000001.xls
        Get http://quotes.money.163.com/cjmx/2018/20180530/0600000.xls
        """
        pass

    async def get_tick_quotes_day(self, code, day, session):
        try:
            df = await self.get_tick_quotes_sina(code, day, session)
        except Exception as e:
            logger.warning('get %s@%s quotes from sina failed: %s', code, day, e)
            try:
                df = await self.get_tick_quotes_qq(code, day, session)
            except Exception as e:
                logger.warning('get %s@%s quotes from qq failed: %s', code, day, e)
                return None
        return df

    async def get_tick_quotes(self, session):
        """获取某只股票一天的tick行情数据

        获取的数据包含如下列:

            * time
            * price
            * price_change
            * volume
            * turnover,
            * character: buy/sell/mid
        """
        for code in self._codes:
            db_file = os.path.join(self._data_dir,
                                   f'tick.{code}.db')
            engine = create_engine('sqlite:///' + db_file)

            for day in iter_date(self._start_date, self._end_date):
                if day.weekday() >= 5:    # 周末没有行情
                    continue

                df = await self.get_tick_quotes_day(code, day, session)
                if not isinstance(df, pd.DataFrame):
                    logger.warning('No quotes found for %s @%s', code, day)
                    continue
                df.to_sql('tick', engine, chunksize=1000, if_exists='append', index=True)

    async def get_curr_quotes_sina(self, code, session):
        url = r'http://hq.sinajs.cn'
        params = {'format': 'text', 'list': code}
        try:
            async with session.get(url,
                                   headers=self.dfl_headers,
                                   params=params) as resp:
                raw_data = await resp.text()
        except aiohttp.ServerTimeoutError:
            logger.warning('connection (%s) timeout', url)
            return None
        except asyncio.TimeoutError:
            logger.warning('read from (%s) timeout', url)
            return None
        code, data = raw_data.split('=')
        data = data.split(',')

        return dict(code=code,
                    name=data[0],
                    open=float(data[1]),
                    close=float(data[2]),
                    now=float(data[3]),
                    high=float(data[4]),
                    low=float(data[5]),
                    # buy=float(data[6]),
                    # sell=float(data[7]),
                    turnover=float(data[8]),
                    volume=float(data[9]),
                    bids=[
                        (float(data[11]), int(data[10])),   # bid1...bid5
                        (float(data[13]), int(data[12])),
                        (float(data[15]), int(data[14])),
                        (float(data[17]), int(data[16])),
                        (float(data[19]), int(data[18]))],
                    asks=[
                        (float(data[21]), int(data[20])),   # ask1...ask5
                        (float(data[23]), int(data[22])),
                        (float(data[25]), int(data[24])),
                        (float(data[27]), int(data[26])),
                        (float(data[29]), int(data[28]))],
                    dt=parse_dt(data[30] + ' ' + data[31]))

    async def get_curr_quotes_qq(self, code, session):
        url = r'http://qt.gtimg.cn'
        params = {'q': code}
        try:
            async with session.get(
                    url, headers=self.dfl_headers, params=params) as resp:
                raw_data = await resp.text()
        except aiohttp.ServerTimeoutError:
            logger.warning('connection (%s) timeout', url)
            return None
        except asyncio.TimeoutError:
            logger.warning('read from (%s) timeout', url)
            return None
        code, data = raw_data.split('=')
        data = data.split('~')
        return dict(code=code.split('_')[-1],
                    name=data[1],
                    open=float(data[5]),
                    close=float(data[4]),
                    now=float(data[3]),
                    high=float(data[33]),
                    low=float(data[34]),
                    # buy=float(data[7]),
                    # sell=float(data[8]),
                    turnover=float(data[38]) if data[38] else None,
                    volume=float(data[6]) * 100,

                    bids=[
                        (float(data[9]), int(float(data[10]) * 100)),
                        (float(data[11]), int(float(data[12]) * 100)),
                        (float(data[13]), int(float(data[14]) * 100)),
                        (float(data[15]), int(float(data[16]) * 100)),
                        (float(data[17]), int(float(data[18]) * 100))],
                    asks=[
                        (float(data[19]), int(float(data[20]) * 100)),
                        (float(data[21]), int(float(data[22]) * 100)),
                        (float(data[23]), int(float(data[24]) * 100)),
                        (float(data[25]), int(float(data[26]) * 100)),
                        (float(data[27]), int(float(data[28]) * 100))],
                    dt=parse_dt(data[30]))

    async def get_curr_quotes_163(self, code, session):
        """
        http://api.money.126.net/data/feed/0601398,money.api
        """
        code = code
        if code.startswith('sz'):
            code = '1' + code.split('.')[-1]
        url = f'http://api.money.126.net/data/feed/{code},money.api'
        try:
            async with session.get(url,
                                   headers=self.dfl_headers) as resp:
                quotes = await resp.json()
        except aiohttp.ServerTimeoutError:
            logger.warning('connection (%s) timeout', url)
            return None
        except asyncio.TimeoutError:
            logger.warning('read from (%s) timeout', url)
            return None
        return quotes

    async def get_curr_quotes(self, session):
        """实时盘口获取"""
        code = self._codes[0]
        while True:
            data = None
            try:
                data = await self.get_curr_quotes_163(code, session)
            except Exception as e:
                logger.warning('get current quotes for %s from 163 failed:%s', code, e)

                try:
                    data = await self.get_curr_quotes_sina(code, session)
                except Exception as e:
                    logger.warning('get current quotes for %s from sina failed:%s', code, e)
                    try:
                        data = await self.get_curr_quotes_qq(code, session)
                    except Exception as e:
                        logger.warning('get current quotes for %s from qq failed:%s', code, e)
            if data:
                print(json.dumps(data, indent=4, ensure_ascii=False))
            time.sleep(0.5)
        return data

    async def get_minute_quotes(self, session):
        pass

    async def get_day_quotes(self, session):
        """从网易财经获取某只股票一天的tick行情数据

        网易财经成交明细
        sz: 1
        sh: 0
        http://quotes.money.163.com/service/chddata.html?code=1000001&start=19910102&end=20180530&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP
        http://quotes.money.163.com/service/chddata.html?code=0600000&start=19991110&end=20180530&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP

        # 指数
        http://quotes.money.163.com/service/chddata.html?code=0000001&start=19901219&end=20180530&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;VOTURNOVER;VATURNOVER
        http://quotes.money.163.com/service/chddata.html?code=0000819&start=20050104&end=20180530&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;VOTURNOVER;VATURNOVER
        """
        pass
        pass

    @staticmethod
    def resample(df, freq, label='right'):
        """将tick数据resample为其他频率的数据，

        freq: pandas.DataFrame.resample 的 rule 参数格式
              T/min 分钟频率
              H 小时频率

        label: 同 pandas.DataFrame.resample 的 label

        转换后的数据为包含如下列的 pd.DataFrame：

            * high
            * low
            * open
            * close
            * turnover
            * volume

        """
        resampler = df.resample(freq, label=label)

        if 'high' not in df.columns:
            new_df = pd.DataFrame({
                'high': resampler.price.max(),
                'low': resampler.price.min(),
                'open': resampler.price.first(),
                'close': resampler.price.last(),
                'turnover': resampler.turnover.sum(),
                'volume': resampler.volume.sum()
                }, index=resampler.first().index)
        else:
            new_df = pd.DataFrame({
                'high': resampler.high.max(),
                'low': resampler.low.min(),
                'open': resampler.open.first(),
                'close': resampler.close.last(),
                'turnover': resampler.turnover.sum(),
                'volume': resampler.volume.sum()
                }, index=resampler.first().index)
        return new_df[new_df.volume > 0]

    async def get_quotes(self):
        async with aiohttp.ClientSession(read_timeout=5 * 60, conn_timeout=30) as session:
            if self._freq == 'tick':
                await self.get_tick_quotes(session)
            elif self._freq == 'minute':
                await self.get_minute_quotes(session)
            elif self._freq == 'day':
                await self.get_day_quotes(session)
            else:
                if len(self._codes) > 1:
                    logger.warning('Realtime tick quote support only one instrument for now, '
                                   'using: %s', self._codes[0])
                    await self.get_curr_quotes(session)

    def main(self, *args):
        self._data_dir = os.path.join(self._root_dir, 'quotes')
        os.makedirs(self._data_dir, exist_ok=True)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.get_quotes())

    @cli.switch(['-s', '--start'], argtype=parse_date)
    def set_start_date(self, start_date):
        """start date"""
        self._start_date = start_date

    @cli.switch(['-e', '--end'], argtype=parse_date)
    def set_end_date(self, end_date):
        """end date"""
        self._end_date = end_date

    @cli.switch(['-c', '--code'], argtype=str, mandatory=True, list=True)
    def set_code(self, code):
        """instrument code"""
        self._codes.extend(code)

    @cli.switch(['-f', '--freq'], argtype=str)
    def set_freq(self, freq):
        """quotes frequency"""
        assert freq in ('tick', 'minute', 'day')
        self._freq = freq


if __name__ == '__main__':
    QuotesApp()
