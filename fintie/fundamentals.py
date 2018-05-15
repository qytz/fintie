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
"""上市公司财务数据

本模块负责获取上市公司财务数据
包含利润、资产、现金三大表

信息获取通道包括：

    * http://www.cninfo.com.cn/cninfo-new/index

"""
import io
import csv
import json
import logging
import zipfile
import asyncio
import aiohttp
from datetime import datetime

from plumbum import cli
from .cli import FinTie
from .web import WebClient


logger = logging.getLogger(__file__)


class FundamentalCrawler(WebClient):
    """财务报表抓取类"""
    async def get_fundamental_qq(self, code, start_year, end_year):
        """从腾讯财经抓取财务报表"""
        pass

    async def get_fundamental_sina(self, code, start_year, end_year):
        """从新浪财经抓取财务报表"""
        pass

    async def get_fundamental_cninfo(self, code, start_year, end_year):
        """从cninfo获取某只股票的历史财务数据
            'lrb': 利润表
            'fzb': 资产表
            'llb': 现金表
        """
        logger.debug('geting fundamental from cninfo')
        url = 'http://www.cninfo.com.cn/cninfo-new/data/query'
        async with self._session.post(url,
                                      headers=self.dfl_headers,
                                      data={
                                          "keyWord": code,
                                          "maxNum": "10",
                                          "hq_or_cw": "2"
                                          }) as resp:
            comps = await resp.json()
            if not comps:
                logger.warning('get company info failed')
                return None

            comp = comps[0]
            min_year = int(comp['startTime'])
            if start_year < min_year:
                logger.warning('set start year from %s to %s', start_year, min_year)
                start_year = min_year

        query_url = 'http://www.cninfo.com.cn/cninfo-new/data/download'
        query_data = {
            "K_code": '',
            "market": comp['market'],
            "type": 'lrb',
            "code": comp['code'],
            "orgid": comp['orgId'],
            "minYear": start_year,
            "maxYear": end_year,
            "hq_code": '',      # 用于获取行情数据的代码
            "hq_k_code": '',
            "cw_code": comp['code'],    # 用于获取财报的代码
            "cw_k_code": '',
            }

        fund_info = {
            'lrb': [],
            'fzb': [],
            'llb': [],
            }
        for fund_type in fund_info:
            query_data['type'] = fund_type
            async with self._session.post(query_url,
                                          headers=self.dfl_headers,
                                          data=query_data) as resp:
                data = await resp.read()

            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                for finfo in zf.filelist:
                    csv_data = zf.read(finfo.filename)
                    csv_data = csv_data.decode('gbk')
                    dialect = csv.Sniffer().sniff(csv_data)
                    first = True
                    for info in csv.reader(csv_data.splitlines(), dialect):
                        if fund_info[fund_type] and first:  # 只需要一个表头
                            first = False
                            continue
                        fund_info[fund_type].append(info)
        return fund_info

    async def get_fundamental(self, code, start_year, end_year, sources=None):
        source_maps = {
            'cninfo': self.get_fundamental_cninfo,
            'sina': self.get_fundamental_sina,
            'qq': self.get_fundamental_qq
            }

        async with aiohttp.ClientSession(read_timeout=5 * 60, conn_timeout=30) as session:
            self._session = session
            if not sources:
                sources = ['cninfo', 'sina', 'qq']
            for source in sources:
                if source not in source_maps:
                    logger.warning('invalid data source ignored')
                    continue
                try:
                    return await source_maps[source](code, start_year, end_year)
                except Exception as e:
                    logger.warning('get data from %s error: %s', source, e)
        self._session = None

        logger.warning('get data from all sources failed')
        return None


@FinTie.subcommand('fundamental')
class FundamentalCmd(cli.Application):
    _start = 2017
    _end = datetime.now().year

    def main(self, *args):
        self.fundamental_crawler = FundamentalCrawler()
        loop = asyncio.get_event_loop()
        fund = loop.run_until_complete(self.fundamental_crawler.get_fundamental(self._code, self._start, self._end))
        print(json.dumps(fund, indent=4))

    @cli.switch(['-c', '--code'], argtype=str, mandatory=True)
    def set_code(self, code):
        """instrument code"""
        self._code = code

    @cli.switch(['-s', '--start'], argtype=int)
    def set_start(self, start):
        """start year"""
        self._start = start

    @cli.switch(['-e', '--end'], argtype=int)
    def set_end(self, end):
        """end year"""
        self._end = end


if __name__ == '__main__':
    FundamentalCmd()
