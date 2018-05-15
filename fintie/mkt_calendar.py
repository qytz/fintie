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

from .utils import daterange
from .interface import DataProxy


logger = logging.getLogger(__file__)


class CalendarProxy(DataProxy):
    def __init__(self):
        self.tbl_name = 'mkt_calendar'

    async def init(self, ctx):
        self._ctx = ctx
        self.db = self._ctx.get_db('instruments')
        self._wsession = self._ctx.web_session

        fpath = os.path.realpath(__file__)
        sql_file = os.path.join(fpath, 'sqls', 'create_mkt_calendar.sql')
        with open(sql_file) as f:
            sql_text = f.read()
        await self.db.execute(sql_text)

    # --- get_stock_info ---
    async def get_events(self, day):
        """从巨潮信息网获取某天的交易日历
        """
        if isinstance(day, (date, datetime)):
            day = day.strftime('%Y-%m-%d')
        url = 'http://www.cninfo.com.cn/cninfo-new/memo/memoQuery'
        try:
            async with self._ctx.post(url, headers=self.dfl_headers,
                                      data={'queryDate': day}) as resp:
                data = await resp.text()
        except aiohttp.ServerTimeoutError:
            logger.info('连接({})超时'.format(url))
            return None
        except asyncio.TimeoutError:
            logger.info('读取({})超时'.format(url))
            return None
        return data

    async def update_data(self, force=False, start_date=None, end_date=None):
        # 强制更新，清除原有数据后再爬取
        if force:
            await self.db.execute('TRUNCATE TABLE {};'.format(self.tbl_name))

        events_list = []
        if start_date:
            if isinstance(start_date, datetime):
                start_day = start_date.date()
            elif isinstance(start_date, date):
                start_day = start_date
            else:
                start_day = datetime.strptime(start_date, '%Y-%m-%d').date()

        if end_date:
            if isinstance(end_date, datetime):
                end_day = end_date.date()
                if end_date.hour >= 19:
                    end_day = end_date + timedelta(days=1)
            elif isinstance(end_date, date):
                end_day = end_date
            else:
                end_day = datetime.strptime(end_date, '%Y-%m-%d').date()

        record1 = await self.db.fetch(
            'SELECT day FROM {} order by day limit 1;'.format(
                self.tbl_name))
        if record1:
            first_day = record1[0][0]

            record2 = await self.db.fetch(
                'SELECT day FROM {} order by day DESC limit 1;'.format(
                    self.tbl_name))
            last_day = record2[0][0]

            if start_day > first_day:
                start_day = last_day + timedelta(days=1)
            else:
                end_day = first_day

        for day in daterange(start_day, end_day):
            events = await self.get_events(day)
            events_list.append((day, events))

        await self.db.executemany("""INSERT INTO {} (day, events)
    VALUES ($1, $2);""".format(self.tbl_name), events_list)

    async def query_data(self, day):
        """查询某一天的市场事件"""
        if isinstance(day, datetime):
            day = day.date()
        elif isinstance(day, date):
            pass
        else:
            day = datetime.strptime(day, '%Y-%m-%d').date()

        record = await self.db.fetch(
                "SELECT events FROM {} where day = $1;".format(self.tbl_name),
                day)
        if record:
            return record[0]

        # 在数据库中不存在，尝试直接从网络获取
        events = await self.get_events(day)
        return json.loads(events)


def test():
    import asyncpg

    cal = CalendarProxy()
    loop = asyncio.get_event_loop()

    ctx = DataProxy()
    loop.run_until_complete(
        cal.init(db, loop=loop))
    loop.run_until_complete(
        cal.update_data(start_date='2017-07-23', end_date='2017-07-28'))
    loop.run_until_complete(
        cal.update_data(start_date='2017-07-25', end_date='2017-07-31'))

    result = loop.run_until_complete(
        cal.query_data(day='2017-07-30'))
    print(result)
    result = loop.run_until_complete(
        cal.query_data(day='2017-08-27'))
    print('--')
    print(result)
