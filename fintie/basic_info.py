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
import asyncio
import aiohttp
import logging
from lxml import html
from datetime import datetime
from openpyxl import load_workbook

from plumbum import cli
from .cli import FinApp, FinTie
from .web import WebClient


logger = logging.getLogger(__file__)


@FinTie.subcommand('instrument_info')
class StockInfoCmd(FinApp, WebClient):
    # --- get_stock_info ---
    _list = True
    _delist = True
    _infos = True

    async def get_stock_info_cninfo(self, code, session):
        """从巨潮咨询获取股票的基本信息

        巨潮咨询网：http://www.cninfo.com.cn/information/companyinfo_n.html?fulltext?szmb000001
        """
        f_code = ''
        if code.startswith('sh60') or code.startswith('sh90'):
            f_code = 'shmb' + code[2:]
        elif code.startswith('sz300'):
            f_code = 'szcn' + code[2:]
        elif code.startswith('sz002'):
            f_code = 'szsme' + code[2:]
        elif code.startswith('sz00') or code.startswith('sz200'):
            f_code = 'szmb' + code[2:]
        else:
            return None

        url = 'http://www.cninfo.com.cn/information/brief/{}.html'.format(
            f_code)
        try:
            async with session.get(url, headers=self.dfl_headers) as \
                    resp:
                data = await resp.text()
        except aiohttp.ServerTimeoutError:
            logger.info('连接({})超时'.format(url))
            return None
        except asyncio.TimeoutError:
            logger.info('读取({})超时'.format(url))
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
        info['list_date'] = datetime.strptime(attrd['上市时间：'], '%Y-%m-%d')
        info['company_name'] = attrd['公司全称：']
        info['website'] = attrd['公司网址：']
        info['reg_addr'] = attrd['注册地址：']
        info['work_addr'] = attrd['办公地址']
        info['issue_price'] = float(attrd['发行价格（元）：'].replace(',', ''))
        info['reg_cap'] = float(attrd['注册资本(万元)：'].replace(',', '')) * 10000
        info['intro'] = ''
        info['business'] = ''
        info['concept'] = ''
        info['industry'] = ''
        info['found_date'] = None

        return info

    async def get_stock_info_sina(self, code, session):
        """从新浪财经获取股票的基本信息

        新浪财经：http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpInfo/stockid/000001.phtml
        """
        def _get_td_text(td):
            txts = []
            for txt in td.xpath('.//text()'):
                if txt.isspace():
                    continue
                txts.append(txt.strip())
            return '||'.join(txts)

        url = ('http://vip.stock.finance.sina.com.cn/corp/go.php/'
               'vCI_CorpInfo/stockid/{}.phtml').format(code[2:])
        try:
            async with session.get(url, headers=self.dfl_headers) as \
                    resp:
                data = await resp.text()
        except aiohttp.ServerTimeoutError:
            logger.info('连接({})超时'.format(url))
            return None
        except asyncio.TimeoutError:
            logger.info('读取({})超时'.format(url))
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
        info['list_date'] = datetime.strptime(attrd['上市日期：'], '%Y-%m-%d')
        info['company_name'] = attrd['公司名称：']
        info['website'] = attrd['公司网址：']
        info['intro'] = attrd['公司简介：']
        info['business'] = attrd['经营范围：']
        info['reg_addr'] = attrd['注册地址：']
        info['work_addr'] = attrd['办公地址：']
        info['issue_price'] = float(attrd['发行价格：'].replace(',', ''))
        info['reg_cap'] = reg_cap
        info['found_date'] = datetime.strptime(attrd['成立日期：'], '%Y-%m-%d')

        info['concept'] = ''
        info['industry'] = ''

        return info

    async def get_stock_info_qq(self, code, session):
        """从腾讯财经获取股票的基本信息

        腾讯财经：http://stock.finance.qq.com/corp1/profile.php?zqdm=000001
        """
        url = 'http://stock.finance.qq.com/corp1/profile.php?zqdm={}'.format(
            code[2:])
        try:
            async with session.get(url, headers=self.dfl_headers) as \
                    resp:
                data = await resp.text(encoding='gbk')
        except aiohttp.ServerTimeoutError:
            logger.info('连接({})超时'.format(url))
            return None
        except asyncio.TimeoutError:
            logger.info('读取({})超时'.format(url))
            return None
        tree = html.fromstring(data)
        items = []
        for item in tree.xpath('//table[2]/tr/td'):
            if item.text:
                items.append(item.text)
            else:
                items.append(item.xpath('a//text()'))
        # 跳过第一个tr -- table head
        # d = {items[i]: items[i+1] for i in range(1, len(items), 2)}
        attrd = {}
        for i in range(1, len(items), 2):
            if isinstance(items[i], list):
                key = items[i][0].strip()
            else:
                key = items[i].strip()
            if isinstance(items[i + 1], list):
                val = '||'.join(items[i + 1])
            else:
                val = items[i + 1].strip()
            attrd[key] = val
        info = {}
        info['company_name'] = attrd['法定名称']
        info['list_date'] = datetime.strptime(attrd['上市日期'], '%Y-%m-%d')
        info['website'] = attrd['公司网址']
        info['intro'] = attrd['公司沿革']
        info['business'] = attrd['经营范围']
        info['reg_addr'] = attrd['注册地址']
        info['work_addr'] = attrd['办公地址']
        info['issue_price'] = float(attrd['发行价格(元)'].replace(',', ''))
        info['reg_cap'] = float(attrd['注册资本(万元)'].replace(',', '')) * 10000
        info['concept'] = attrd['所属板块']
        info['industry'] = attrd['所属行业']
        info['found_date'] = datetime.strptime(attrd['成立日期'], '%Y-%m-%d')

        return info

    async def get_stock_info(self, code, session):
        """获取上市公司基础信息"""
        # 默认从腾讯财经/cninfo/新浪财经获取股票信息，失败则报警
        ret = await self.get_stock_info_qq(code, session)
        if ret is not None:
            return ret
        ret = await self.get_stock_info_sina(code, session)
        if ret is not None:
            return ret
        ret = await self.get_stock_info_cninfo(code, session)
        if ret is None:
            logger.error('获取/更新股票列表失败')
        return ret
    # --- get_stock_info ---

    def main(self, *args):
        self._data_dir = os.path.join(self._root_dir, 'calendar')
        os.makedirs(self._data_dir, exist_ok=True)

        loop = asyncio.get_event_loop()
        fund = loop.run_until_complete(self.get_market_calendar(self._start_date, self._end_date))

    @cli.switch(['-l', '--list'])
    def set_list(self):
        """获取上市公司列表"""
        self._list = True

    @cli.switch(['-d', '--delist'])
    def set_start_date(self):
        """获取退市公司列表"""
        self._delist = True

    @cli.switch(['-i', '--info'], conut, list=True, arttype=str)
    def set_info(self, info):
        """获取单个上市公司的信息"""
        self._infos = True


if __name__ == '__main__':
    StockInfoCmd()
