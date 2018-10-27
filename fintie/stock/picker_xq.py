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
"""提供选股器接口

信息获取通道包括：

* https://xueqiu.com/hq/screener/CN
* https://xueqiu.com/hq/screener/US

沪深选股参数说明

    对于不需要过滤但需要返回的字段请传递 `field=ALL` ，否则对应字段的值也不会返回

    * 字段一览，参数名为 field

      `参考字段一览列表 <../_static/picker_xq_fields.json>`_

      获取地址 https://xueqiu.com/stock/screener/fields.json?category=SH

      如下字段的参数名为 `filed.period` ，其中 period 为财务报表的结束日期::

          财务报表里的所有指标
          财务比率里的所有指标
          基本指标 - 净资产收益率(%)     roediluted.20180630
          基本指标 - 净利润(万)          netprofit.20180630
          基本指标 - 每股净资产          bps.20180630
          基本指标 - 每股收益            eps.20180630

    * 地域一览，选股参数字段名为 `areacode` ，值为 `keycode`

      `参考地域一览列表 <../_static/picker_xq_areas.json>`_

      获取地址 https://xueqiu.com/stock/screener/areas.json

    * 行业一览，选股参数字段名为 `indcode` ，值为 `level2code`

      `参考行业一览列表 <../_static/picker_xq_industries.json>`_

      获取地址 https://xueqiu.com/stock/screener/industries.json?category=SH

    * 交易所一览，选股参数字段名为 `exchange`

      SH/SZ  -- 沪市/深市

加载已保存的数据::

    import pandas as pd
    from pathlib import Path

    df = pd.read_json(Path('20181018165415.json')
    df.set_index(["symbol"], inplace=True)
    # df.drop_duplicates(inplace=True)
    df.apply(pd.to_numeric, errors="coerce") # convert to numertic types

    # df['day'] = date.today()
    # df["day"] = datetime.now().replace(hour=16, minute=0, second=0, microsecond=0)
    # set index
    # df.set_index(["symbol", "day"], inplace=True)
"""
import os
import time
import json
import copy
import asyncio
import logging
from pathlib import Path
from datetime import datetime

import click
import pandas as pd

from .cli import stock_cli_group, MODULE_DATA_DIR
from ..config import get_config
from ..env import _init_in_session
from ..utils import fetch_http_data


logger = logging.getLogger(__file__)
__all__ = ["async_pick_stocks", "async_get_field_values", "pick_stocks"]


async def _init(session, force=False):
    if force or not _init_in_session.get("xueqiu"):
        _init_in_session["xueqiu"] = True
        await session.get("https://xueqiu.com")
    return True


async def async_get_field_values(session, field, return_df=True):
    """
    https://xueqiu.com/stock/screener/values.json?category=SH&field=pettm&_=1540617201640
    获取该字段值的列表
    """
    await _init(session)

    url = "https://xueqiu.com/stock/screener/values.json"
    params = {"category": "SH", "field": field}
    params["_"] = int(time.time() * 1000)
    data = []
    async with session.get(url, params=params) as resp:
        if resp.status != 200:
            logger.error("pick stock from %s failed: %s", url, resp.status)
            return None

        resp_json = await resp.json()
        if "list" not in resp_json:
            logger.error("pick stocks unknown result: %s", resp_json)
        else:
            data = resp_json["list"]

    if not return_df:
        return data

    return pd.DataFrame(data, columns=(field,))


async def async_pick_stocks(session, data_path=None, return_df=True, **kwargs):
    """
    雪球选股器接口，此接口支持的参数较多，具体请参考 API 文档

    返回一个 pd.DataFrame
    出错，返回 None

    :param session: `aiohttp.ClientSession` 对象，同步接口不需要传
    :param kwargs: 选股参数，支持的字段名见 `API 文档`
    :param data_path: 数据保存路径
    :param return_df: 是否返回 `pandas.DataFrame` 对象，False 返回原始数据
    :returns: 行情原始数据或带有行情数据的 `pandas.DataFrame` 对象，见 return_df 参数

    取值方法
    GET https://xueqiu.com/stock/screener/screen.json

    parameters:
        category: SH/US  -- 沪深/美股   required
        orderby:symbol   -- 排序字段    required
        oder:desc        -- 升降排序    required
        exchange: SH/SZ  -- 沪市/深市
        areacode: 地域板块
        indcode: 行业
        filter_fileds: min_max
        current:ALL     当前价
        pct:ALL         本日涨跌幅
        volume:ALL      本日成交量
        page:1
        size: 30
        _:timestamp
    """
    await _init(session)

    page_size = 100000
    curr_page = page_cnt = 1
    params = {
        "category": "SH",
        "orderby": "symbol",
        "order": "desc",
        "current": "ALL",  # 当前价
        "pct": "ALL",  # 本日涨跌幅
        "volume": "ALL",  # 本日成交量
        "page": curr_page,
        "size": page_size,
        # "exchange": SH/SZ  -- 沪市/深市
        # "areacode": 地域板块
        # "indcode": 行业
        # "filter_fileds": min_max
    }
    params.update(kwargs)

    url = "https://xueqiu.com/stock/screener/screen.json"

    stock_list = []
    logger.info("start pick stocks, params: %s", params)
    while curr_page <= page_cnt:
        params["page"] = curr_page
        params["_"] = int(time.time() * 1000)

        logger.info("Fetching first page")
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                logger.error("pick stock from %s failed: %s", url, resp.status)
                return None

            resp_json = await resp.json()
            total_cnt = resp_json["count"]
            if "list" not in resp_json:
                logger.error("pick stocks unknown result: %s", resp_json)
                break

            page_cnt = total_cnt // page_size + 1 if total_cnt % page_size != 0 else 0
            if page_cnt != 1:
                stock_list.extend(resp_json["list"])
            else:
                stock_list = resp_json["list"]
        curr_page += 1

    if not stock_list:
        logger.warn("pick stock no result")
    logger.info("pick stocks from %s finish", url)

    if data_path:
        data_path = Path(data_path) / MODULE_DATA_DIR / "picker_xueqiu"
        os.makedirs(data_path, exist_ok=True)
        data_fname = "picker" + "-" + datetime.now().strftime("%Y%m%d%H%M%S") + ".json"
        data_file = data_path / data_fname
        with data_file.open("w") as dataf:
            json.dump(stock_list, dataf, indent=4, ensure_ascii=False)

    if not return_df:
        return stock_list

    df = pd.DataFrame(stock_list)
    df.set_index(["symbol"], inplace=True)
    df.dropna(axis="columns", how="all", inplace=True)
    # convert to numertic types
    # df.apply(pd.to_numeric, errors="ignore")
    return df


def pick_stocks(*args, **kwargs):
    ret = fetch_http_data(async_pick_stocks, *args, **kwargs)
    if isinstance(ret, Exception):
        raise ret
    return ret


@stock_cli_group.command("picker-xq")
@click.option(
    "-f",
    "--save-path",
    type=click.Path(exists=False),
    default=get_config("data_path", os.getcwd()),
    show_default=True,
)
@click.option("-p/-np", "--print/--no-print", "show", default=True)
@click.argument("fields", nargs=-1)
def pick_stocks_cli(save_path, show, fields):
    """雪球选股器

    fields 选股筛选条件，具体支持的字段见API文档描述，
    格式为 field=val, 多个字段空格分割: areacode=CN110000 exchange=SH ...
    """
    kwargs = {}
    for field in fields:
        try:
            key, val = field.split("=")
        except ValueError:
            click.echo(f"{field} invalid skipped")
            continue
        kwargs[key] = val
    data = pick_stocks(save_path, **kwargs)
    if show:
        click.echo(data)


if __name__ == "__main__":
    pick_stocks_cli()
