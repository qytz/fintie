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
import json
import asyncio
import logging
from datetime import datetime

import aiohttp
from lxml import html

from plumbum import cli
from .cli import FinApp, FinTie
from .web import WebClient


logger = logging.getLogger(__file__)


@FinTie.subcommand('instrument_info')
class StockInfoCmd(FinApp, WebClient):
    # --- get_stock_info ---
    _code = ''

    async def get_stock_info_cninfo(self, code, session):
        """从巨潮咨询获取股票的基本信息

        巨潮咨询网：http://www.cninfo.com.cn/information/companyinfo_n.html?fulltext?szmb000001
        """
        logger.info('Starting get stock info for %s from cninfo', self._code)
        f_code = ''
        if code.startswith('60') or code.startswith('90'):
            f_code = 'shmb' + code
        elif code.startswith('300'):
            f_code = 'szcn' + code
        elif code.startswith('002'):
            f_code = 'szsme' + code
        elif code.startswith('00') or code.startswith('200'):
            f_code = 'szmb' + code
        else:
            logger.info('Get stock info for %s from cninfo failed: invalid code', self._code)
            return None

        url = 'http://www.cninfo.com.cn/information/brief/{}.html'.format(
            f_code)
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
        attrd = {}
        key = None
        for txt in tree.xpath('//div[@class="clear"]/table/tr/td/text()'):
            if key is None:
                key = txt.strip()
            else:
                attrd[key] = txt.strip()
                key = None
        info = {}
        # info['list_date'] = datetime.strptime(attrd['上市时间：'], '%Y-%m-%d')
        info['list_date'] = attrd['上市时间：']
        info['company_name'] = attrd['公司全称：']
        info['website'] = attrd['公司网址：']
        info['reg_addr'] = attrd['注册地址：']
        info['issue_price'] = float(attrd['发行价格（元）：'].replace(',', ''))
        info['reg_cap'] = float(attrd['注册资本(万元)：'].replace(',', '')) * 10000
        info['intro'] = ''
        info['business'] = ''
        info['concept'] = ''
        info['industry'] = ''
        info['found_date'] = None
        logger.info('Get stock info for %s from cninfo complete', self._code)

        return info

    async def get_stock_info_sina(self, code, session):
        """从新浪财经获取股票的基本信息

        新浪财经：http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpInfo/stockid/000001.phtml
        """
        logger.info('Starting get stock info for %s from sina', self._code)
        def _get_td_text(td):
            txts = []
            for txt in td.xpath('.//text()'):
                if txt.isspace():
                    continue
                txts.append(txt.strip())
            return '||'.join(txts)

        url = ('http://vip.stock.finance.sina.com.cn/corp/go.php/'
               'vCI_CorpInfo/stockid/{}.phtml').format(code)
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

        attrd = {}
        key = None
        for td in tree.xpath("//table[@id='comInfo1']/tr/td"):
            if not key:
                key = _get_td_text(td)
            else:
                attrd[key] = _get_td_text(td)
                key = None

        reg_cap = attrd['注册资本：']
        if reg_cap.endswith('万元'):
            reg_cap = float(reg_cap[:-len('万元')].replace(',', '')) * 10000
        else:
            reg_cap = float(reg_cap)
        info = {}
        # info['list_date'] = datetime.strptime(attrd['上市日期：'], '%Y-%m-%d')
        info['list_date'] = attrd['上市日期：']
        info['company_name'] = attrd['公司名称：']
        info['website'] = attrd['公司网址：']
        info['intro'] = attrd['公司简介：']
        info['business'] = attrd['经营范围：']
        info['reg_addr'] = attrd['注册地址：']
        info['work_addr'] = attrd['办公地址：']
        info['issue_price'] = float(attrd['发行价格：'].replace(',', ''))
        info['reg_cap'] = reg_cap
        # info['found_date'] = datetime.strptime(attrd['成立日期：'], '%Y-%m-%d')
        info['found_date'] = attrd['成立日期：']

        info['concept'] = ''
        info['industry'] = ''
        logger.info('Get stock info for %s from sina complete', self._code)

        return info

    async def get_stock_info(self):
        """获取上市公司基础信息"""
        # 默认从腾讯财经/cninfo/新浪财经获取股票信息，失败则报警
        logger.info('Starting get stock info for %s', self._code)
        async with aiohttp.ClientSession(read_timeout=5 * 60, conn_timeout=30) as session:
            info = await self.get_stock_info_sina(self._code, session)
            if info is None:
                info = await self.get_stock_info_cninfo(self._code, session)

        if info is None:
            logger.error('Get stock %s info failed', self._code)

        date = datetime.now().date()
        dest_file = os.path.join(self._data_dir, f'{self._code}.{date}.json')
        with open(dest_file, 'w') as dataf:
            json.dump(info, dataf, indent=4, ensure_ascii=False)
        logger.info('Get stock info for %s complete, data saved to %s', self._code, dest_file)
    # --- get_stock_info ---

    def main(self, *args):
        self._data_dir = os.path.join(self._root_dir, 'instruments_info')
        os.makedirs(self._data_dir, exist_ok=True)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.get_stock_info())

    @cli.switch(['-c', '--code'], argtype=str, mandatory=True)
    def set_code(self, code):
        """instrument code"""
        self._code = code.split('.')[-1]

if __name__ == '__main__':
    StockInfoCmd()
