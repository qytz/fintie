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
"""本模块负责获取股票的历史交易行情信息。

获取通道包括：

    * 基础信息，包含最新行情快照

      https://stock.xueqiu.com/v5/stock/quote.json?symbol=SZ002353&extend=detail

    * 最近的 100 条成交记录

      https://stock.xueqiu.com/v5/stock/history/trade.json?symbol=SZ002353&count=100

    * 实时-盘口

      https://stock.xueqiu.com/v5/stock/realtime/pankou.json?symbol=SZ002353


数据加载

    trades::

        import json
        from pathlib import Path

        import pandas as pd

        with Path('SZ002353-trade-20181019201938.json').open() as f:
            quotes = json.load(f)

        df = pd.DataFrame(data=quotes["items"])
        df.timestamp = pd.to_datetime(df.timestamp, unit="ms")
        df.set_index("timestamp", inplace=True)


TODO:

    * add default http headers

      headers = {"X-Forwarded-For": ipAddress}
"""
import os
import json
import logging
from pathlib import Path
from datetime import datetime

import click
import pandas as pd

from .cli import stock_cli_group, MODULE_DATA_DIR
from ..config import get_config
from ..env import _init_in_session
from ..utils import fetch_http_data, add_doc


__all__ = [
    "async_get_trade_info",
    "async_get_pankou",
    "async_get_live_info",
    "get_trade_info",
    "get_pankou",
    "get_live_info",
]
logger = logging.getLogger(__file__)
INIT_URLS = ["https://xueqiu.com"]
QUOTE_TYPES = ("pankou", "trades", "live-info")


async def _init(session, force=False):
    if force or not _init_in_session.get("xueqiu"):
        _init_in_session["xueqiu"] = True
        await session.get("https://xueqiu.com")
    return True


async def async_get_trade_info(session, symbol, data_path=None, return_df=True):
    """获取最近的交易记录

    :param session: `aiohttp.ClientSession` 对象，同步接口不需要传
    :param symbol: 股票代码
    :param data_path: 数据保存路径
    :param return_df: 是否返回 `pandas.DataFrame` 对象，False 返回原始数据

    :returns: 行情原始数据或带有行情数据的 `pandas.DataFrame` 对象，见 return_df 参数
    """
    await _init(session)

    url = "https://stock.xueqiu.com/v5/stock/history/trade.json"
    params = {"symbol": symbol}
    async with session.get(url, params=params) as resp:
        if resp.status != 200:
            logger.warning("get live trades from %s failed: %s", url, resp.status)
            return None
        data_json = await resp.json()
        if data_json.get("error_code", -1) != 0:
            logger.warning(
                "get live trades from %s failed, error_code: %s", url, resp.status
            )
            return None
        quotes = data_json["data"]

    if data_path:
        data_path = Path(data_path) / MODULE_DATA_DIR / symbol / "live_quotes"
        os.makedirs(data_path, exist_ok=True)
        try:
            ref_dt = datetime.fromtimestamp(quotes["items"][0]["timestamp"] / 1000)
        except (KeyError, TypeError):
            ref_dt = datetime.now()

        data_fname = (
            "-".join((symbol, "trade", ref_dt.strftime("%Y%m%d%H%M%S"))) + ".json"
        )
        data_file = data_path / data_fname
        with data_file.open("w") as dataf:
            json.dump(quotes, dataf, indent=4, ensure_ascii=False)

    if not return_df:
        return quotes

    df = pd.DataFrame(data=quotes["items"])
    df.timestamp = pd.to_datetime(df.timestamp, unit="ms")
    df.set_index("timestamp", inplace=True)
    return df


async def async_get_pankou(session, symbol, data_path=None):
    """获取最新的盘口数据
    :param session: `aiohttp.ClientSession` 对象，同步接口不需要传
    :param symbol: 股票代码
    :param data_path: 数据保存路径

    :returns: 盘口数据 `dict`
    """
    await _init(session)

    url = "https://stock.xueqiu.com/v5/stock/realtime/pankou.json"
    params = {"symbol": symbol}
    async with session.get(url, params=params) as resp:
        if resp.status != 200:
            logger.warning("get live pankou from %s failed: %s", url, resp.status)
            return None
        data_json = await resp.json()
        if data_json.get("error_code", -1) != 0:
            logger.warning(
                "get live pankou from %s failed, error_code: %s", url, resp.status
            )
            return None
        quotes = data_json["data"]

    if data_path:
        data_path = Path(data_path) / MODULE_DATA_DIR / symbol / "live_quotes"
        os.makedirs(data_path, exist_ok=True)
        try:
            ref_dt = datetime.fromtimestamp(quotes["timestamp"] / 1000)
        except (KeyError, TypeError):
            ref_dt = datetime.now()

        data_fname = (
            "-".join((symbol, "pankou", ref_dt.strftime("%Y%m%d%H%M%S"))) + ".json"
        )
        data_file = data_path / data_fname
        with data_file.open("w") as dataf:
            json.dump(quotes, dataf, indent=4, ensure_ascii=False)

    return quotes


async def async_get_live_info(session, symbol, data_path=None):
    """获取最新的基本信息，包括最新价格市值等

    :param session: `aiohttp.ClientSession` 对象，同步接口不需要传
    :param symbol: 股票代码
    :param data_path: 数据保存路径

    :returns: 基本信息数据 `dict`
    """
    await _init(session)

    url = "https://stock.xueqiu.com/v5/stock/quote.json"
    params = {"symbol": symbol, "extend": "detail"}
    async with session.get(url, params=params) as resp:
        if resp.status != 200:
            logger.warning("get live trade info from %s failed: %s", url, resp.status)
            return None
        data_json = await resp.json()
        if data_json.get("error_code", -1) != 0:
            logger.warning(
                "get live trade info from %s failed, error_code: %s", url, resp.status
            )
            return None
        quotes = data_json["data"]

    if data_path:
        data_path = Path(data_path) / MODULE_DATA_DIR / symbol / "live_quotes"
        os.makedirs(data_path, exist_ok=True)
        try:
            ref_dt = datetime.fromtimestamp(quotes["quote"]["timestamp"] / 1000)
        except (KeyError, TypeError):
            ref_dt = datetime.now()

        data_fname = (
            "-".join((symbol, "quotes", ref_dt.strftime("%Y%m%d%H%M%S"))) + ".json"
        )
        data_file = data_path / data_fname
        with data_file.open("w") as dataf:
            json.dump(quotes, dataf, indent=4, ensure_ascii=False)

    return quotes


@add_doc(async_get_trade_info.__doc__)
def get_trade_info(*args, **kwargs):
    ret = fetch_http_data(async_get_trade_info, *args, **kwargs)
    if isinstance(ret, Exception):
        raise ret
    return ret


@add_doc(async_get_pankou.__doc__)
def get_pankou(*args, **kwargs):
    ret = fetch_http_data(async_get_pankou, *args, **kwargs)
    if isinstance(ret, Exception):
        raise ret
    return ret


@add_doc(async_get_live_info.__doc__)
def get_live_info(*args, **kwargs):
    ret = fetch_http_data(async_get_live_info, *args, **kwargs)
    if isinstance(ret, Exception):
        raise ret
    return ret


@stock_cli_group.command("live-quotes")
@click.option("-s", "--symbol", required=True)
@click.option(
    "-t", "--type", "quotes_type", type=click.Choice(QUOTE_TYPES), default="pankou"
)
@click.option(
    "-f",
    "--save-path",
    type=click.Path(exists=False),
    show_default=True,
    default=get_config("data_path", os.getcwd()),
)
@click.option("-p/-np", "--print/--no-print", "show", default=True)
def live_quotes_cli(symbol, quotes_type, save_path, show):
    """从雪球获取实时行情"""
    if quotes_type == "trades":
        data = get_trade_info(symbol, save_path)
    elif quotes_type == "info":
        data = get_live_info(symbol, save_path)
    elif quotes_type == "pankou":
        data = get_pankou(symbol, save_path)
    else:
        data = None

    if show:
        if isinstance(data, (list, dict)):
            click.echo(json.dumps(data, indent=4, ensure_ascii=False))
        else:
            click.echo(data)


if __name__ == "__main__":
    live_quotes_cli()
