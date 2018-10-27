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
""" 本模块负责获取上市公司财务数据，包含利润、资产负债、现金流量三大表及摘要和主要财务指标。

信息获取通道包括：

    * http://quotes.money.163.com/service/zcfzb_000333.html
    * http://quotes.money.163.com/service/lrb_000333.html
    * http://quotes.money.163.com/service/xjllb_000333.html
    * http://quotes.money.163.com/service/cwbbzy_000333.html
    * http://quotes.money.163.com/service/zycwzb_000333.html?type=report

加载已保存数据::

    import pandas as pd
    from pathlib import Path
    df = pd.read_csv(Path("xxx.json"), index_col=0)
"""
import os
import logging
import asyncio
from pathlib import Path

import click
import aiohttp
import pandas as pd

from .cli import stock_cli_group, MODULE_DATA_DIR
from ..config import get_config
from ..utils import fetch_http_data, add_doc


logger = logging.getLogger(__file__)
__all__ = [
    "get_funda_tab",
    "async_get_funda_tab",
    "get_fundamentals",
    "async_get_fundamentals",
]


async def _init(session):
    return True


async def async_get_funda_tab(session, symbol, tab_name, return_df=True):
    """获取某表的财务数据

    :param session: `aiohttp.ClientSession` 对象，同步接口不需要传
    :param symbol: 股票代码
    :param tab_name: lrb/zcfzb/xjllb/cwbbzy/zycwzb
    :param data_path: 数据保存路径
    :param return_df: 是否返回 `pandas.DataFrame` 对象，False 返回原始数据

    :returns: 原始财务数数据或带有财务数据的 `pandas.DataFrame` 对象，见 return_df 参数
    """
    assert tab_name in ("lrb", "zcfzb", "xjllb", "cwbbzy", "zycwzb")

    await _init(session)
    symbol_163 = symbol
    if symbol_163.startswith("SZ") or symbol_163.startswith("SH"):
        symbol_163 = symbol[2:]
    url = f"http://quotes.money.163.com/service/{tab_name}_{symbol_163}.html"
    try:
        async with await session.get(url) as resp:
            if resp.status != 200:
                logger.warning(
                    "Download funda for %s.%s from url failed: http %s",
                    symbol,
                    tab_name,
                    url,
                    resp.status,
                )
                return None
            data = await resp.text()
            encoding = resp.get_encoding()
    except (aiohttp.ServerTimeoutError, asyncio.TimerHandle):
        logger.warning("get %s for %s failed: timeout", tab_name, symbol)

    if not return_df:
        return data
    return pd.read_csv(data, encoding=encoding, index_col=0)


async def async_get_fundamentals(session, symbols, data_path):
    """获取财务数据

    :param session: `aiohttp.ClientSession` 对象，同步接口不需要传
    :param symbol: 股票代码
    :param data_path: 数据保存路径

    :returns: Nothing
    """

    async def get_one_funda(symbol, tab_name, path):
        data = await async_get_funda_tab(session, symbol, tab_name, return_df=False)
        save_file = path / (tab_name + ".csv")
        with save_file.open("w") as f:
            f.write(data)

    await _init(session)
    aws = []
    logger.info("Getting fundamental from 163")
    for symbol in symbols:
        symbol_data_dir = Path(data_path) / MODULE_DATA_DIR / symbol / "fundamental"
        os.makedirs(symbol_data_dir, exist_ok=True)
        for tab_name in ("lrb", "zcfzb", "xjllb", "cwbbzy", "zycwzb"):
            aws.append(get_one_funda(symbol, tab_name, symbol_data_dir))
    rets = await asyncio.gather(*aws, return_exceptions=True)
    for ret in rets:
        if isinstance(ret, Exception):
            raise ret

    return True


@add_doc(async_get_funda_tab.__doc__)
def get_funda_tab(*args, **kwargs):
    ret = fetch_http_data(async_get_funda_tab, *args, **kwargs)
    if isinstance(ret, Exception):
        raise ret
    return ret


@add_doc(async_get_fundamentals.__doc__)
def get_fundamentals(*args, **kwargs):
    ret = fetch_http_data(async_get_fundamentals, *args, **kwargs)
    if isinstance(ret, Exception):
        raise ret
    return ret


@stock_cli_group.command("funda")
@click.option(
    "-f",
    "--save-path",
    type=click.Path(exists=False),
    default=get_config("data_path", os.getcwd()),
    show_default=True,
)
@click.argument("symbols", nargs=-1, required=True)
def fundamental_cli(symbols, save_path):
    """从163获取财务报表及财务指标信息"""
    get_fundamentals(symbols, save_path)


if __name__ == "__main__":
    fundamental_cli()
