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
"""上市公司公告抓取

本模块负责获取上市公司公告文件
并提供分析与公告信息提取

信息获取通道包括：

"""
import io
import csv
import asyncio
import aiohttp
import logging
import zipfile


from .interface import DataProxy


logger = logging.getLogger(__file__)


class StatementProxy(DataProxy):
    async def get_statements(self, code, start_year, end_year):
        """获取公告文件"""
        pass


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_com_list(loop))
