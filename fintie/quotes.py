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

        Get http://market.finance.sina.com.cn/downxls.phq?date=2017-06-20&symbol=sz000001

    * 腾讯财经成交明细（从20170103开始提供）

        Get http://stock.gtimg.cn/data/index.phq?appn=detail&action=download&c=sh601633&d=20170606
        Get http://stock.gtimg.cn/data/index.phq?appn=detail&action=download&c=sz000651&d=20170606

分钟bar获取通道包括：
日bar获取通道包括：

    http://www.cninfo.com.cn/cninfo-new/index


TODO: add default http headers
headers = {"X-Forwarded-For": ipAddress}

"""
import os
import io
import logging
import asyncio
from datetime import date, datetime, timedelta
from dateutil.parser import parse as parse_dt

import aiohttp
import pandas as pd

from .interface import DataProxy
from .utils import daterange


logger = logging.getLogger(__file__)


class HistQuotesProxy(DataProxy):
    char_buy = 1
    char_sell = 2
    char_neuter = 0

    def __init__(self, root_dir):
        super().__init__()
        self.start_date = datetime.strptime(
            '2005-01-01 00:00:01', '%Y-%m-%d %H:%M:%S').date()
        self.end_date = date.today()
        curr_time = datetime.now()
        if curr_time.hour >= 19:
            self.end_date = date.today() + timedelta(days=1)
        self.root_dir = root_dir
        self.stock_codes = None

    async def init(self, loop=None):
        if not loop:
            loop = asyncio.get_event_loop()
        self.loop = loop

    async def get_tick_quotes_sina(self, code, day, session):
        """从新浪获取某只股票一天的tick行情数据

        Get http://market.finance.sina.com.cn/downxls.phq?date=2017-06-20&symbol=sz000001
        """
        if isinstance(day, (date, datetime)):
            day = day.strftime('%Y-%m-%d')

        y, m, d = int(day[:4]), int(day[5:7]), int(day[8:])
        url = 'http://market.finance.sina.com.cn/downxls.phq'
        params = {'symbol': code, 'date': day}
        try:
            async with session.get(
                    url, headers=self.dfl_headers, params=params) as resp:
                raw = await resp.read()
        except aiohttp.ServerTimeoutError:
            logger.info('连接({})超时'.format(url))
            return None
        except asyncio.TimeoutError:
            logger.info('读取({})超时'.format(url))
            return None
        dataio = io.StringIO(raw.decode('gbk'))
        df = pd.read_csv(dataio, sep='\t')
        df = df.rename(
            columns={
                '成交时间': 'time', '成交价': 'price',
                '价格变动': 'price_change', '成交量(手)': 'volume',
                '成交额(元)': 'turnover', '性质': 'character'})

        df['time'] = df['time'].apply(
            lambda x: pd.to_datetime(x, format='%H:%M:%S').replace(
                year=y, month=m, day=d))

        df.set_index('time', inplace=True)
        df['volume'] = df['volume'] * 100
        df.character.replace({
            '买盘': self.char_buy,
            '卖盘': self.char_sell,
            '中性盘': self.char_neuter}, inplace=True)
        return df.iloc[::-1]

    async def get_tick_quotes_qq(self, code, day, session):
        """从腾讯获取某只股票一天的tick行情数据

        腾讯财经成交明细（从20170103开始提供）
        Get http://stock.gtimg.cn/data/index.phq?appn=detail&action=download&c=sh601633&d=20170606
        Get http://stock.gtimg.cn/data/index.phq?appn=detail&action=download&c=sz000651&d=20170606
        """
        if isinstance(day, (date, datetime)):
            day = day.strftime('%Y%m%d')
        elif len(day.split('-')) != 1:
            day = ''.join(day.split('-'))

        y, m, d = int(day[:4]), int(day[5:7]), int(day[8:])
        url = 'http://stock.gtimg.cn/data/index.phq'
        params = {'appn': 'detail', 'action': 'download', 'c': code, 'd': day}
        try:
            async with session.get(
                    url, headers=self.dfl_headers, params=params) as resp:
                raw = await resp.read()
        except aiohttp.ServerTimeoutError:
            logger.info('连接({})超时'.format(url))
            return None
        except asyncio.TimeoutError:
            logger.info('读取({})超时'.format(url))
            return None
        dataio = io.StringIO(raw.decode('gbk'))
        df = pd.read_csv(dataio, sep='\t')
        df = df.rename(
            columns={
                '成交时间': 'time', '成交价格': 'price',
                '价格变动': 'price_change', '成交量(手)': 'volume',
                '成交额(元)': 'turnover', '性质': 'character'})

        df['time'] = df['time'].apply(
            lambda x: pd.to_datetime(x, format='%H:%M:%S').replace(
                year=y, month=m, day=d))

        df.set_index('time', inplace=True)
        df['volume'] = df['volume'] * 100
        df.character.replace({
            '买盘': self.char_buy,
            '卖盘': self.char_sell,
            '中性': self.char_neuter}, inplace=True)
        return df

    async def get_tick_quotes(self, code, day, session):
        """获取某只股票一天的tick行情数据

        获取的数据包含如下列:

            * time
            * price
            * price_change
            * volume
            * turnover,
            * character: buy/sell/mid
        """
        try:
            df = await self.get_tick_quotes_sina(code, day, session)
        except:
            try:
                df = await self.get_tick_quotes_qq(code, day, session)
            except:
                logger.warn('获取{}@{}行情错误'.format(code, day))
                return None
        return df

    async def get_curr_quotes_sina(self, code, session):
        url = r'http://hq.sinajs.cn'
        params = {'format': 'text', 'list': code}
        try:
            async with session.get(
                    url, headers=self.dfl_headers, params=params) as resp:
                raw_data = await resp.text()
        except aiohttp.ServerTimeoutError:
            logger.info('连接({})超时'.format(url))
            return None
        except asyncio.TimeoutError:
            logger.info('读取({})超时'.format(url))
            return None
        code, data = raw_data.split('=')
        data = data.split(',')
        return dict(
                code=code,
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
            logger.info('连接({})超时'.format(url))
            return None
        except asyncio.TimeoutError:
            logger.info('读取({})超时'.format(url))
            return None
        code, data = raw_data.split('=')
        data = data.split('~')
        return dict(
                code=code.split('_')[-1],
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

    def merge_data(self, freq):
        """合并数据存储

        除不同频度的数据存储在不同的文件外，
        同一频度不同时间的数据
        """
        pass

    async def update_data(self, force=False, stock_list=None,
                          start_date=None, end_date=None):
        if start_date:
            if isinstance(start_date, datetime):
                start_day = start_date.date()
            elif isinstance(start_date, date):
                start_day = start_date
            else:
                start_day = datetime.strptime(start_date, '%Y-%m-%d').date()
            self.start_date = start_day

        if end_date:
            if isinstance(end_date, datetime):
                end_day = end_date.date()
                if end_date.hour >= 19:
                    end_day = end_date + timedelta(days=1)
            elif isinstance(end_date, date):
                end_day = end_date
            else:
                end_day = datetime.strptime(end_date, '%Y-%m-%d').date()
            self.end_date = end_day

        if stock_list:
            self.stock_codes = stock_list

        async with aiohttp.ClientSession(
                loop=self.loop,
                read_timeout=5 * 60,
                conn_timeout=30) as session:

            for code in self.stock_codes:
                subpath = code[-2:]
                tick_path = os.path.join(self.root_dir, 'tick', subpath)
                os.makedirs(tick_path, exist_ok=True)
                minute_path = os.path.join(self.root_dir, 'minute', subpath)
                os.makedirs(minute_path, exist_ok=True)
                day_path = os.path.join(self.root_dir, 'day', subpath)
                os.makedirs(day_path, exist_ok=True)
                index_path = os.path.join(self.root_dir, 'index', subpath)
                os.makedirs(index_path, exist_ok=True)

                try:
                    index_df = pd.read_hdf(
                        os.path.join(index_path, code+'.hdf'),
                        'index', start=-1)

                    store_end = index_df.index.date[-1]
                    if self.start_date <= store_end:
                        self.start_date = store_end + timedelta(days=1)
                except (KeyError, FileNotFoundError):
                    pass

                tick_store = pd.HDFStore(
                    os.path.join(tick_path, code+'.hdf'))
                minute_store = pd.HDFStore(
                    os.path.join(minute_path, code+'.hdf'))
                day_store = pd.HDFStore(
                    os.path.join(day_path, code+'.hdf'))
                index_store = pd.HDFStore(
                    os.path.join(index_path, code+'.hdf'))

                tick_starts = []
                minute_starts = []
                day_index = []
                for day in daterange(self.start_date, self.end_date):
                    if day.weekday() >= 5:    # 周末没有行情
                        continue

                    df_tick = await self.get_tick_quotes(code, day, session)
                    if not isinstance(df_tick, pd.DataFrame):
                        logger.warn('No quotes found for %s @%s', code, day)
                        continue

                    df_minute = self.resample(
                        df_tick, freq='1T', label='right')
                    df_day = self.resample(df_tick, freq='1d', label='left')

                    try:
                        tick_starts.append(
                            tick_store.get_storer('quote').nrows)
                    except AttributeError:
                        tick_starts.append(0)
                    df_tick.to_hdf(tick_store, 'quote',
                                   mode='a', format='t', append=True)

                    try:
                        minute_starts.append(
                            minute_store.get_storer('quote').nrows)
                    except AttributeError:
                        minute_starts.append(0)
                    df_minute.to_hdf(minute_store, 'quote',
                                     mode='a', format='t', append=True)

                    df_day.to_hdf(day_store, 'quote',
                                  mode='a', format='t', append=True)
                    day_index.append(pd.to_datetime(day))

                if day_index:
                    new_index = pd.DataFrame(data={
                        'tick_start': tick_starts,
                        'minute_start': minute_starts}, index=day_index)
                    new_index.to_hdf(index_store, 'index',
                                     mode='a', format='t', append=True)

                tick_store.close()
                minute_store.close()
                day_store.close()
                index_store.close()

    async def query_curr_quotes(self, code):
        """实时盘口获取"""
        async with aiohttp.ClientSession(
                loop=self.loop,
                read_timeout=5 * 60,
                conn_timeout=30) as session:
            try:
                data = await self.get_curr_quotes_sina(code, session)
            except Exception as e:
                try:
                    data = await self.get_curr_quotes_qq(code, session)
                except Exception as e:
                    logger.warn('获取盘口{}行情错误:{}'.format(code, e))
                    return None
        return data

    async def query_today_tick(self, code, session):
        """获取当日分笔数据"""
        pass

    async def query_data(self, code, freq, start, end, cols=None):
        """查询历史行情数据

        code: 股票代码
        freq: 行情频率，支持
                tick 成交详情级别
                1m...nm 分钟级别
                1d...nd 天级别
        start/end: 起止日期，date/datetime类型，'%Y-%m-%d'格式字符串
        cols: tick [price, price_change, volume, turnover, character]
              day/minute [high, low, open, close, turnover, volume]
              默认 None 返回所有列

        return: DataFrame，index 为 datatime
        """
        if isinstance(start, (date, datetime)):
            start_day = start.strftime('%Y-%m-%d')
        else:
            start_day = start
        if isinstance(end, (date, datetime)):
            end_day = end.strftime('%Y-%m-%d')
        else:
            end_day = end

        subpath = code[-2:]
        resample_freq = None

        if 'd' in freq:
            df = pd.read_hdf(
                os.path.join(self.root_dir, 'day', subpath, code+'.hdf'),
                'quote',
                where='index>={} & index<{}'.format(start_day, end_day))

            if freq[:-1] and freq[:-1] != '1':
                resample_freq = freq[:-1] + 'd'

        else:
            index_df = pd.read_hdf(
                os.path.join(self.root_dir, 'index', subpath, code+'.hdf'),
                'index',
                where='index>={} & index<={}'.format(start_day, end_day))

            if freq == 'tick':
                start_pos = index_df.iloc[0].tick_start
                end_pos = index_df.iloc[-1].tick_start
                df = pd.read_hdf(
                    os.path.join(self.root_dir, 'tick', subpath, code+'.hdf'),
                    'quote', start=start_pos, stop=end_pos)
            elif 'm' in freq:
                start_pos = index_df.iloc[0].minute_start
                end_pos = index_df.iloc[-1].minute_start
                df = pd.read_hdf(
                    os.path.join(self.root_dir, 'minute',
                                 subpath, code+'.hdf'),
                    'quote', start=start_pos, stop=end_pos)

                if freq[:-1] and freq[:-1] != '1':
                    resample_freq = freq[:-1] + 'T'
            else:
                return None

        if resample_freq:
            df = self.resample(df, resample_freq)

        if cols and cols != 'all':
            return df[cols]

        return df


def test():
    loop = asyncio.get_event_loop()
    hq = HistQuotesProxy('/tmp/quotes')
    loop.run_until_complete(
        hq.init(loop))
    loop.run_until_complete(
        hq.update_data(
            stock_list=['sz000001', 'sz000002', 'sh600000', 'sh600001'],
            start_date='2008-08-12', end_date='2008-08-19'))

    loop.run_until_complete(
        hq.update_data(
            stock_list=['sz000001', 'sz000002', 'sh600000', 'sh600001'],
            start_date='2008-08-16', end_date='2008-08-26'))

    loop.run_until_complete(
        hq.query_data(
            'sz000002', '5m',
            start='20080813', end='20080827'))

    loop.run_until_complete(
        hq.query_data(
            'sz000002', '2d',
            start='20080813', end='20080827'))
    real_quotes = loop.run_until_complete(
        hq.get_curr_quotes('sz000002'))
    print(real_quotes)
