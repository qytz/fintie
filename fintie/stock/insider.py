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
"""提供内部交易信息查询

信息获取通道包括：

    * http://xueqiu.com/hq/insider/SZ002353

加载已保存的数据::

    import pandas as pd
    from pathlib import Path

    df = pd.read_json(Path('xxx.json')
"""
import os
import time
import json
import asyncio
import logging
from pathlib import Path
from datetime import date

import click
import pandas as pd

from .cli import stock_cli_group, MODULE_DATA_DIR
from ..config import get_config
from ..env import _init_in_session
from ..utils import fetch_http_data, add_doc


logger = logging.getLogger(__file__)
__all__ = ["async_get_inside_trade", "get_inside_trade"]


async def _init(session, force=False):
    if force or not _init_in_session.get("xueqiu"):
        _init_in_session["xueqiu"] = True
        await session.get("https://xueqiu.com")
    return True


async def async_get_inside_trade(session, symbol, data_path=None, return_df=True):
    """
    从雪球获取内部交易数据

    :param session: `aiohttp.ClientSession` 对象，同步接口不需要传
    :param symbol: 股票代码
    :param data_path: 数据保存路径
    :param return_df: 是否返回 `pandas.DataFrame` 对象，False 返回原始数据

    :returns: 原始数据或 `pandas.DataFrame` 对象，见 return_df 参数，
              失败则返回 `None`
    """
    await _init(session)

    page_size = 10000
    curr_page = 1
    params = {"_": 0, "symbol": symbol, "page": curr_page, "size": page_size}

    logger.info("start download inside_trade from xueqiu for %s...", symbol)
    url = "https://xueqiu.com/stock/f10/skholderchg.json"
    params["_"] = int(time.time() * 1000)

    date_str = str(date.today())
    async with session.get(url, params=params) as resp:
        if resp.status != 200:
            logger.warning("get inside_trade from %s failed: %s", url, resp.status)
            return None
        data = await resp.json()
        if "list" not in data:
            logger.warn("no inside_trade data downloaded for %s from %s: % ", symbol, url, data)
        inside_trade_data = data["list"]

    if not inside_trade_data:
        logger.warn("no inside_trade data downloaded for %s from %s, return None", symbol, url)
        return None

    logger.info("download inside_trade for %s from %s finish", symbol, url)
    if data_path:
        data_path = Path(data_path) / MODULE_DATA_DIR / "inside_trade"
        os.makedirs(data_path, exist_ok=True)
        data_fname = "-".join((symbol, date_str)) + ".json"
        data_file = data_path / data_fname
        with data_file.open("w") as dataf:
            json.dump(inside_trade_data, dataf, indent=4, ensure_ascii=False)

    if not return_df:
        return inside_trade_data

    df = pd.DataFrame(inside_trade_data)
    # set index
    # df.set_index("bonusimpdate", inplace=True)
    return df


@add_doc(async_get_inside_trade.__doc__)
def get_inside_trade(*args, **kwargs):
    ret = fetch_http_data(async_get_inside_trade, *args, **kwargs)
    if isinstance(ret, Exception):
        raise ret
    return ret


@stock_cli_group.command("inside_trade")
@click.option("-s", "--symbol", required=True)
@click.option(
    "-f",
    "--save-path",
    type=click.Path(exists=False),
    default=get_config("data_path", os.getcwd()),
    show_default=True,
)
@click.option("-p/-np", "--print/--no-print", "show", default=True)
def inside_trade_cli(symbol, save_path, show):
    """从雪球获取内部交易数据"""
    data = get_inside_trade(symbol, save_path)
    if show:
        click.echo(data)


if __name__ == "__main__":
    inside_trade_cli()
