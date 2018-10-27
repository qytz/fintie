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
"""提供股东信息查询

信息获取通道包括：

    * 主要股东

      http://xueqiu.com/S/SZ002353/ZYGD

    * 流通股东

      http://xueqiu.com/S/SZ002353/LTGD

    * 限售股东

      http://xueqiu.com/S/SZ002353/XSGDMD

加载已保存的数据::

    import json
    import pandas as pd
    from pathlib import Path

    with Path('xxx.json').open() as f:
        data = json.load(f)

    # 股东户数统计
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
__all__ = [
    "async_get_gudong",
    "async_get_gudong_count",
    "get_gudong",
    "get_gudong_count",
]
GUDONG_TYPES = {
    "main": "https://xueqiu.com/stock/f10/shareholder.json",
    "public": "https://xueqiu.com/stock/f10/otsholder.json",
    "limit": "https://xueqiu.com/stock/f10/limskholder.json",
    "count": "https://xueqiu.com/stock/f10/shareholdernum.json",
}


async def _init(session, force=False):
    if force or not _init_in_session.get("xueqiu"):
        _init_in_session["xueqiu"] = True
        await session.get("https://xueqiu.com")
    return True


async def async_get_gudong_count(session, symbol, data_path=None, return_df=True):
    """
    从雪球获取股东户数数据

    :param session: `aiohttp.ClientSession` 对象，同步接口不需要传
    :param symbol: 股票代码
    :param data_path: 数据保存路径
    :param return_df: 是否返回 `pandas.DataFrame` 对象，False 返回原始数据

    :returns: 原始数据或 `pandas.DataFrame` 对象，见 return_df 参数，
              失败则返回 `None`
    """
    json_data = await async_get_gudong(
        session, symbol, gd_type="count", data_path=data_path
    )
    if "list" not in json_data:
        logger.error("get gudong count failed for %s failed: %s", symbol, json_data)
    if not return_df:
        return json_data["list"]
    return pd.DataFrame(json_data["list"])


async def async_get_gudong(session, symbol, gd_type, data_path=None):
    """
    从雪球获取股东数据

    :param session: `aiohttp.ClientSession` 对象，同步接口不需要传
    :param symbol: 股票代码
    :param gd_type: 股东类型

                    * main    主要股东
                    * public  流通股东
                    * limit   限售股东

    :param data_path: 数据保存路径

    :returns: 原始数据 `dict`
              失败则返回 `None`
    """
    assert gd_type in GUDONG_TYPES
    await _init(session)

    page_size = 10000
    curr_page = 1
    params = {"_": 0, "symbol": symbol, "page": curr_page, "size": page_size}

    logger.info("start download gudong from xueqiu for %s...", symbol)
    url = GUDONG_TYPES[gd_type]
    params["_"] = int(time.time() * 1000)

    date_str = str(date.today())
    async with session.get(url, params=params) as resp:
        if resp.status != 200:
            logger.warning("get gudong from %s failed: %s", url, resp.status)
            return None
        data = await resp.json()
        if "list" not in data:
            logger.warn(
                "no gudong data downloaded for %s from %s: % ", symbol, url, data
            )
        gudong_data = data["list"]

    if not gudong_data:
        logger.warn(
            "no gudong data downloaded for %s from %s, return None", symbol, url
        )
        return None

    logger.info("download gudong for %s from %s finish", symbol, url)
    if data_path:
        data_path = Path(data_path) / MODULE_DATA_DIR / "gudong"
        os.makedirs(data_path, exist_ok=True)
        data_fname = "-".join((symbol, gd_type, date_str)) + ".json"
        data_file = data_path / data_fname
        with data_file.open("w") as dataf:
            json.dump(gudong_data, dataf, indent=4, ensure_ascii=False)

    return gudong_data


@add_doc(async_get_gudong.__doc__)
def get_gudong(*args, **kwargs):
    ret = fetch_http_data(async_get_gudong, *args, **kwargs)
    if isinstance(ret, Exception):
        raise ret
    return ret


@add_doc(async_get_gudong_count.__doc__)
def get_gudong_count(*args, **kwargs):
    ret = fetch_http_data(async_get_gudong_count, *args, **kwargs)
    if isinstance(ret, Exception):
        raise ret
    return ret


@stock_cli_group.command("gudong")
@click.option("-s", "--symbol", required=True)
@click.option(
    "-t",
    "--type",
    "gd_type",
    help="股东类型",
    type=click.Choice(GUDONG_TYPES),
    default="main",
    show_default=True,
)
@click.option(
    "-f",
    "--save-path",
    type=click.Path(exists=False),
    default=get_config("data_path", os.getcwd()),
    show_default=True,
)
@click.option("-p/-np", "--print/--no-print", "show", default=False)
def gudong_cli(symbol, gd_type, save_path, show):
    """从雪球获取股东数据"""
    data = get_gudong(symbol, gd_type, save_path)
    if show:
        click.echo(data)


if __name__ == "__main__":
    gudong_cli()
