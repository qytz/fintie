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
"""上市公司列表

本模块负责获取上市公司列表，包括上市公司代码及名称，
上市日期、退市日期、行业、分类、概念板块等信息。

信息获取通道包括：

    * 巨潮咨询网：http://www.cninfo.com.cn/cninfo-new/information/companylist
    * 上交所：http://www.sse.com.cn/assortment/stock/list/share/
    * 深交所官网：http://www.szse.cn/main/marketdata/jypz/colist/
    * 巨潮咨询网：http://www.cninfo.com.cn/information/companyinfo_n.html?fulltext?szmb000001
    * 腾讯财经：http://stockhtm.finance.qq.com/sstock/quotpage/q/000001.htm#6
    * 新浪财经：http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpInfo/stockid/000001.phtml
"""
import os
import io
import csv
import json
import asyncio
import logging
from datetime import datetime

import aiohttp
from lxml import html
from plumbum import cli
from openpyxl import load_workbook

from .cli import FinApp, FinTie
from .web import WebClient


logger = logging.getLogger(__file__)


@FinTie.subcommand('instrument_list')
class InstrumentListCmd(FinApp, WebClient):
    """获取上市/退市代码列表"""
    # --- get_stock_info ---
    _list = True
    _delist = True

    # --- get_stock_list ---
    async def get_stock_listed_cninfo(self, session):
        """从cninfo获取股票列表数据

        * 巨潮咨询网：http://www.cninfo.com.cn/cninfo-new/information/companylist
        """
        logger.info('Starting download listed stock list from cninfo')
        url = 'http://www.cninfo.com.cn/cninfo-new/information/companylist'
        try:
            async with session.get(url, headers=self.dfl_headers) as \
                    resp:
                data = await resp.text()
        except aiohttp.ServerTimeoutError:
            logger.warning('connection (%s) timeout', url)
            return None
        except asyncio.TimeoutError:
            logger.warning('read from (%s) timeout', url)
            return None

        tree = html.fromstring(data)
        szmb_list = tree.xpath("//div[@id='con-a-1']/ul/li/a")
        szsme_list = tree.xpath("//div[@id='con-a-2']/ul/li/a")
        szcn_list = tree.xpath("//div[@id='con-a-3']/ul/li/a")
        shmb_list = tree.xpath("//div[@id='con-a-4']/ul/li/a")

        def _get_codes(code_list, code_postfix):
            ret = {}
            for code_info in code_list:
                # url = code_info.get('href')
                code, name = code_info.text.split(maxsplit=1)
                ret[code + code_postfix] = {
                    'code': code + code_postfix,
                    'name': name,
                }
            return ret

        sz_stocks = _get_codes(szmb_list, '.sz')
        sz_stocks.update(_get_codes(szsme_list, '.sz'))
        sz_stocks.update(_get_codes(szcn_list, '.sz'))
        sh_stocks = _get_codes(shmb_list, '.sh')

        logger.info('Download listed stock list from cninfo complete')
        return {
            'sz': sz_stocks,
            'sh': sh_stocks,
        }

    async def get_stock_listed_se(self, session):
        """从交易所官方网站获取股票列表

        * 上交所：http://www.sse.com.cn/assortment/stock/list/share/
        * 深交所官网：http://www.szse.cn/main/marketdata/jypz/colist/
        """
        logger.info('Starting download listed stock list from exchange offical site')
        sh_info = {}
        sz_info = {}
        # stockType=1: A股 stockType=2: B股
        logger.info('Starting download listed sz stock list')
        for stock_type in [1, 2]:
            url = ('http://query.sse.com.cn/security/stock/'
                   'downloadStockListFile.do?csrcCode=&stockCode=&'
                   'areaName=&stockType={}').format(stock_type)
            referer = 'http://www.sse.com.cn/assortment/stock/list/share/'
            headers = self.dfl_headers.copy()
            headers['Referer'] = referer
            try:
                async with session.get(url, headers=headers) as resp:
                    data = await resp.text()
            except aiohttp.ServerTimeoutError:
                logger.warning('connection (%s) timeout', url)
                return None
            except asyncio.TimeoutError:
                logger.warning('read from (%s) timeout', url)
                return None
            except:
                return None
            dialect = csv.Sniffer().sniff(data)
            for info in csv.reader(data.splitlines(), dialect):
                if len(info) < 7 or info[0].strip() == '公司代码':
                    logger.debug('skip table header')
                    continue
                code = info[2].strip() + '.sh'
                sh_info[code] = {
                    'code': code,
                    'name': info[3].strip(),
                    # 'company_name': info[1].strip(),
                    # 'list_date': datetime.strptime(info[4].strip(),
                    #                                '%Y-%m-%d'),
                }

        logger.info('Download listed sz stock list complete')
        # TABKEY=tab1 所有列表
        # TABKEY=tab2 A股列表
        # TABKEY=tab3 B股列表
        logger.info('Starting download listed sh stock list')
        url = ('http://www.szse.cn/szseWeb/ShowReport.szse?SHOWTYPE=xlsx&'
               'CATALOGID=1110&tab2PAGENO=1&ENCODE=1&TABKEY=tab1')
        try:
            async with session.get(url, headers=headers) as resp:
                data = await resp.read()
        except aiohttp.ServerTimeoutError:
            logger.warning('connection (%s) timeout', url)
            return None
        except asyncio.TimeoutError:
            logger.warning('read from (%s) timeout', url)
            return None

        wb = load_workbook(io.BytesIO(data))
        ws = wb.active
        for val in ws.values:
            if val[0].strip() == '公司代码':
                logger.debug('skip table header')
                continue
            if val[5].strip():
                code = val[5].strip() + '.sz'
                sz_info[code] = {
                    'code': code,
                    'name': val[6].strip(),
                    # 'website': val[-1].strip(),
                    # 'company_name': val[1].strip(),
                    # 'list_date': datetime.strptime(info[7].strip(),
                    #                                '%Y-%m-%d'),
                }
            if val[10].strip():
                code = val[10].strip() + '.sz'
                sz_info[code] = {
                    'code': code,
                    'name': val[11].strip(),
                    # 'website': val[-1].strip(),
                    # 'company_name': val[1].strip(),
                    # 'list_date': datetime.strptime(info[12].strip(),
                    #                                '%Y-%m-%d'),
                }
        logger.info('Download listed sh stock list complete')
        return {
            'sz': sz_info,
            'sh': sh_info,
        }

    async def get_stock_listed(self, session):
        """获取上市公司列表"""
        # 默认从cninfo/szse,sse获取上市公司列表，失败则报警
        logger.info('Starting download listed stock list')
        ret = await self.get_stock_listed_se(session)
        if ret is not None:
            return ret
        ret = await self.get_stock_listed_cninfo(session)
        if ret is not None:
            return ret

        logger.info('Download listed stock list failed')
        return ret
    # --- get_stock_list ---

    async def get_stock_delisted(self, session):
        """获取退市公司列表

        目前支持从 cninfo 获取
        # TODO: 发掘更多的获取退市列表的数据源
        """
        logger.info('Starting download delisted stock list')
        delist_stocks = {}
        url = 'http://www.cninfo.com.cn/cninfo-new/information/delistinglist-1'
        for market in ('sz', 'sh'):
            try:
                async with session.get(url,
                                       headers=self.dfl_headers,
                                       params={'market': market}) as resp:
                    # text = await resp.text()
                    # print(text)
                    data = await resp.json()
            except aiohttp.ServerTimeoutError:
                logger.warning('connection (%s) timeout', url)
                return delist_stocks
            except asyncio.TimeoutError:
                logger.warning('read from (%s) timeout', url)
                return delist_stocks
            else:
                for sec in data:
                    code = sec['y_seccode_0007'] + '.' + market
                    delist_stocks[code] = sec['f008d_0007']
        logger.info('Download delisted stock list complete')
        return delist_stocks

    async def get_stock_lists(self):
        """获取标的列表"""
        info = {}
        async with aiohttp.ClientSession(read_timeout=5 * 60, conn_timeout=30) as session:
            if self._list:
                info['list_insturments'] = await self.get_stock_listed(session)
            if self._delist:
                info['delist_insturments'] = await self.get_stock_delisted(session)

        date = datetime.now().date()
        dest_file = os.path.join(self._data_dir, f'instrument_lists.{date}.json')
        with open(dest_file, 'w') as dataf:
            json.dump(info, dataf, indent=4, ensure_ascii=False)
        logger.info('instrument_lists data has been saved to: %s', dest_file)

    def main(self, *args):
        self._data_dir = os.path.join(self._root_dir, 'instrument_lists')
        os.makedirs(self._data_dir, exist_ok=True)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.get_stock_lists())

    @cli.switch(['-l', '--list'])
    def set_list(self):
        """获取上市公司列表"""
        self._list = True

    @cli.switch(['-d', '--delist'])
    def set_delist(self):
        """获取上市公司列表"""
        self._delist = True


if __name__ == '__main__':
    InstrumentListCmd()
