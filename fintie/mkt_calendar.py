#-*- coding: utf-8 -*-
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
"""每日市场事件

获取每日市场事件，事件类型包括：

    * 停牌、复牌
    * 首发新股上市
    * 首发新股招股书刊登
    * 首发新股网上发行
    * 中签率公告
    * 授予股份上市
    * 股东资格登记
    * 股东大会召开
    * 网络投票开始、网络投票结束
    * 分红转增股权登记、分红转增除权除息、分红转增红利发放、分红转增股份上市
    * 增发新股招股书刊登

等，信息获取通道包括：

    http://www.cninfo.com.cn/cninfo-new/memo?queryDate=2017-07-19
"""
import os
import json
import asyncio
import logging
from datetime import datetime, date, timedelta

import aiohttp
from plumbum import cli

from .utils import iter_date, parse_date
from .cli import FinApp, FinTie
from .web import WebClient


logger = logging.getLogger(__file__)


@FinTie.subcommand('calendar')
class CalendarApp(FinApp, WebClient):
    _end_date = date.today()
    _start_date = _end_date - timedelta(days=10)

    async def get_market_calendar(self, start, end):
        """从巨潮信息网获取某天的交易日历"""
        datas = {}
        async with aiohttp.ClientSession(read_timeout=5 * 60, conn_timeout=30) as session:
            for day in iter_date(start, end):
                day_str = day.strftime('%Y-%m-%d')
                url = 'http://www.cninfo.com.cn/cninfo-new/memo/memoQuery'
                logger.info('Downloading calendar data for %s', day_str)
                try:
                    async with session.post(url,
                                            headers=self.dfl_headers,
                                            data={'queryDate': day_str}) as resp:
                        data = await resp.json()
                except aiohttp.ServerTimeoutError:
                    logger.warning('Download calendar data for %s failed：connection(%s) timeout',
                                   day_str,
                                   url)
                    continue
                except asyncio.TimeoutError:
                    logger.warning('Download calendar data for %s failed：read(%s) timeout',
                                   day_str,
                                   url)
                    continue
                datas[day_str] = data

        dest_file = os.path.join(self._data_dir, f'calendar.{start}-{end}.json')
        with open(dest_file, 'w') as dataf:
            json.dump(datas, dataf, indent=4, ensure_ascii=False)
        logger.info('calendar data has been saved to: %s', dest_file)

        return True

    def main(self, *args):
        self._data_dir = os.path.join(self._root_dir, 'calendar')
        os.makedirs(self._data_dir, exist_ok=True)

        loop = asyncio.get_event_loop()
        fund = loop.run_until_complete(self.get_market_calendar(self._start_date, self._end_date))

    @cli.switch(['-s', '--start'], argtype=parse_date)
    def set_start_date(self, date):
        """start date"""
        self._start_date = date

    @cli.switch(['-e', '--end'], argtype=parse_date)
    def set_end_date(self, date):
        """start date"""
        self._end_date = date


if __name__ == '__main__':
    CalendarApp()
