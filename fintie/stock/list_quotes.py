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
"""获取市场行情一览

信息获取通道包括：

    * https://xueqiu.com/stock/cata/stocklist.json
    * https://xueqiu.com/fund/quote/list.json

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
from ..utils import fetch_http_data, add_doc


logger = logging.getLogger(__file__)
__all__ = ["async_get_list_qutes", "get_list_quotes"]


async def _init(session, force=False):
    if force or not _init_in_session.get("xueqiu"):
        _init_in_session["xueqiu"] = True
        await session.get("https://xueqiu.com")
    return True


async def async_get_list_qutes(
    session, data_type="stock", data_path=None, return_df=True
):
    """
    获取每日行情概览信息，只能获取当天的
    返回一个 pd.DataFrame
    出错，返回 None

    :param session: `aiohttp.ClientSession` 对象，同步接口不需要传
    :param symbol: 股票代码
    :param data_type: stock: 沪深股票 cb: 可转债 eft: ETF基金 fenji: 分级基金
    :param data_path: 数据保存路径
    :param return_df: 是否返回 `pandas.DataFrame` 对象，False 返回原始数据

    :returns: 行情原始数据或带有行情数据的 `pandas.DataFrame` 对象，见 return_df 参数
    """
    await _init(session)

    quotes = []
    page_size = 90
    curr_page = page_cnt = 1
    params = {
        "_": 0,
        "order": "desc",
        "orderby": "percent",
        "page": curr_page,
        "size": page_size,
    }
    quotes_url = "https://xueqiu.com/stock/cata/stocklist.json"
    if data_type == "stock":
        params["type"] = "11,12"
    elif data_type == "cb":
        params["exchange"] = "CN"
        params["industry"] = "可转债"
    elif data_type == "etf":
        params["parent_type"] = 13
        params["type"] = 135
        params["orderBy"] = "percent"
        quotes_url = "https://xueqiu.com/fund/quote/list.json"
    elif data_type == "fenji":
        params["parent_type"] = 1
        params["type"] = 14
        params["orderBy"] = "percent"
        quotes_url = "https://xueqiu.com/fund/quote/list.json"

    logger.info("start download live quotes from xueqiu for %s...", data_type)

    async def fetch_one_page(url, params):
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                logger.warning(
                    "Download list_quotes from url failed: http %s", url, resp.status
                )
                return None
            return await resp.json()

    def process_one_page(resp_json, quotes):
        if not resp_json:
            return 0
        if data_type in ("stock", "cb"):
            if not resp_json["success"]:
                logger.error("Get daily quotes for %s failed: %s", data_type, resp_json)
            total_cnt = resp_json["count"]["count"]
        elif data_type in ("etf",):
            if "error_code" in resp_json:
                logger.error("Get daily quotes for %s failed: %s", data_type, resp_json)
            total_cnt = resp_json["count"]
        elif data_type in ("fenji",):
            if "error_code" in resp_json:
                logger.error("Get daily quotes for %s failed: %s", data_type, resp_json)
            total_cnt = resp_json["count"]
        quotes.extend(resp_json["stocks"])
        return total_cnt

    aws = []
    while curr_page <= page_cnt:
        params["page"] = curr_page
        params["_"] = int(time.time() * 1000)

        logger.info("Fetching first page")
        resp_json = await fetch_one_page(quotes_url, params)
        total_cnt = process_one_page(resp_json, quotes)

        page_cnt = total_cnt // page_size + 1 if total_cnt % page_size != 0 else 0
        logger.info("First page process finish, total_page: %s page_cnt")
        curr_page += 1

        if page_cnt > 2:
            for index in range(curr_page, page_cnt + 1):
                new_params = copy.copy(params)
                new_params["page"] = index
                aws.append(fetch_one_page(quotes_url, new_params))
            curr_page = index + 1

    if aws:
        pages = await asyncio.gather(*aws, return_exceptions=True)
        for page in pages:
            if not isinstance(page, Exception):
                process_one_page(page, quotes)

    if not quotes:
        logger.warn("no data downloaded for %s, return None", data_type)
    logger.info("download xueqiu daily quotes for %s finish", data_type)

    if data_path:
        data_path = Path(data_path) / MODULE_DATA_DIR / "list_quotes"
        os.makedirs(data_path, exist_ok=True)
        data_fname = data_type + "-" + datetime.now().strftime("%Y%m%d%H%M%S") + ".json"
        data_file = data_path / data_fname
        with data_file.open("w") as dataf:
            json.dump(quotes, dataf, indent=4, ensure_ascii=False)

    if not return_df:
        return quotes

    df = pd.DataFrame(quotes)
    # df['day'] = date.today()
    # df["day"] = datetime.now().replace(hour=16, minute=0, second=0, microsecond=0)
    # set index
    # df.set_index(["symbol", "day"], inplace=True)
    df.set_index(["symbol"], inplace=True)
    df.drop_duplicates(inplace=True)
    # convert to numertic types
    df.apply(pd.to_numeric, errors="ignore")
    return df


@add_doc(async_get_list_qutes.__doc__)
def get_list_quotes(*args, **kwargs):
    ret = fetch_http_data(async_get_list_qutes, *args, **kwargs)
    if isinstance(ret, Exception):
        raise ret
    return ret


@stock_cli_group.command("list-quotes")
@click.option("-t", "--data-type", default="stock", show_default=True)
@click.option(
    "-f",
    "--save-path",
    type=click.Path(exists=False),
    default=get_config("data_path", os.getcwd()),
    show_default=True,
)
@click.option("-p/-np", "--print/--no-print", "show", default=True)
def list_quotes_cli(data_type, save_path, show):
    """从雪球获取最新的行情快照

    对于交易时间，可以获取实时的数据；
    非交易时间则获取上一交易日的数据。

    \b
    data_type
        stock: 沪深股票
        cb: 可转债
        eft: ETF基金
        fenji: 分级基金
    """
    data = get_list_quotes(data_type, save_path)
    if show:
        click.echo(data)


if __name__ == "__main__":
    list_quotes_cli()
