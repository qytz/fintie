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
from datetime import timedelta
from dateutil.parser import parse


def convert_number(num_str, cls=int):
    """带逗号格式的数值字符串转为数值类型"""
    return cls(num_str.replace(',', ''))


def iter_date(start_date, end_date):
    """按天变动的日期 Generator"""
    for day in range(int((end_date - start_date).days)):
        yield start_date + timedelta(day)


def parse_date(date_str):
    """解析字符串为 Date 类型，失败报 TypeError"""
    try:
        dtime = parse(date_str)
    except ValueError:
        raise TypeError('Invalid date string')
    return dtime.date()


def parse_datetime(date_str):
    """解析字符串为 datetime 类型，失败报 TypeError"""
    try:
        dtime = parse(date_str)
    except ValueError:
        raise TypeError('Invalid date string')
    return dtime
