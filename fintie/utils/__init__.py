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
import asyncio

from dateutil.relativedelta import relativedelta
from dateutil.parser import parse as parse_datetime

from fintie.env import get_http_session, _init_in_session


def convert_number(num_str, cls=int):
    """带逗号格式的数值字符串转为数值类型

    :params num_str: 数值字符串
    :params cls: 数值类型，默认为 `int`
    :returns: cls 类型的数值
    """
    return cls(num_str.replace(",", ""))


def iter_dt(start_dt, end_dt, include_start=True, include_end=False, **kwargs):
    """按步进值迭代一个日期范围的 Generator ，默认步进值是一天

    **NOTICE** 如果需要迭代的步进值小于一天，请传递 `datetime` 类型

    :params start_date: 开始日期
    :params end_date: 结束日期
    :params include_start: 是否包含开始时间
    :params include_end: 是否包含结束时间
    :params kwargs: 传递给 `dateutil.relativedelta` 的参数，用于计算步进值
    """
    if not kwargs:
        kwargs = {"days": 1}

    current_dt = start_dt
    if not include_start:
        current_dt += relativedelta(**kwargs)
    if include_end:
        end_dt += relativedelta(**kwargs)

    while current_dt < end_dt:
        yield current_dt
        current_dt += relativedelta(**kwargs)


def parse_dt(date_str, return_date=False):
    """解析字符串为 Date 类型，失败报 TypeError/ValueError 异常

    :params date_str: 要解析的时间日期字符串
    :params return_date: 如果为 `True` 返回 `datetime.date` 类型，否则返回 `datetime.datetime`
    :returns: `datetime` 如果 return_date 是 `False` ，否则返回 `date`
    """
    dtime = parse_datetime(date_str)
    if return_date:
        return dtime.date()
    return dtime


async def wrap_session_run(func, *args, **kwargs):
    async with get_http_session() as session:
        ret = await func(session, *args, **kwargs)
        _init_in_session.clear()
        return ret


def async2sync_run(*aws, return_exceptions=True, loop=None):
    """将异步函数转为同步函数

    :params aws: 异步协程列表
    :params return_exceptions: 是否运行返回异常，不 允许的话任何一个协程异常都会导致本函数异常
    :returns: 一个列表包含了所有协程的返回值
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(
        asyncio.gather(*aws, loop=loop, return_exceptions=return_exceptions)
    )


def fetch_http_data(func, *args, **kwargs):
    """将异步的http取数据接口转为同步方式"""
    return async2sync_run(wrap_session_run(func, *args, **kwargs))[0]


def add_doc(doc):
    """一个给函数添加文档字符串的装饰器函数"""
    def func_wrapper(func):
        func.__doc__ = doc
        return func
    return func_wrapper
