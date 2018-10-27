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
"""提供股本信息查询

信息获取通道包括：

    * 当日财务指标    http://xueqiu.com/S/SH600559/MRCWZB
    * 股票收益率指标  http://xueqiu.com/S/SH600559/GPSYLZB

    * 主要财务指标    https://xueqiu.com/S/SH600559/ZYCWZB
    * 单季财务指标    http://xueqiu.com/S/SH600559/DJCWZB
    * 综合损益表      http://xueqiu.com/S/SH600559/GSLRB
    * 资产负债表      http://xueqiu.com/S/SH600559/ZCFZB
    * 现金流量表      http://xueqiu.com/S/SH600559/XJLLB


加载已保存的数据::

    # 主要财务指标/单季财务指标/综合损益表/资产负债表/现金流量表

    import pandas as pd
    from pathlib import Path

    df = pd.read_json(Path('xxx.json')
    # optional, set index
    if "reportdate" if df:
        df.set_index("reportdate", inplace=True)
    else:
        df.set_index("enddate", inplace=True)
        or
        df.set_index("begindate", inplace=True)

    # 当日财务指标/股票收益率指标
    import json

    from pathlib import Path
    with open(Path("xxx.json")) as f:
        data = json.load(f)
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
__all__ = ["async_get_funda", "get_funda"]
FUNDA_TABLES = {
    # 当日财务指标
    "MRCWZB": "https://xueqiu.com/stock/f10/dailypriceextend.json",
    # 股票收益率指标
    "GPSYLZB": "https://xueqiu.com/stock/f10/yieldindic.json",
    # 主要财务指标
    "ZYCWZB": "https://xueqiu.com/stock/f10/finmainindex.json",
    # 单季财务指标
    "DJCWZB": "https://xueqiu.com/stock/f10/finqindic.json",
    # 综合损益表
    "GSLRB": "https://xueqiu.com/stock/f10/incstatement.json",
    # 资产负债表
    "ZCFZB": "https://xueqiu.com/stock/f10/balsheet.json",
    # 现金流量表
    "XJLLB": "https://xueqiu.com/stock/f10/cfstatement.json",
}


async def _init(session, force=False):
    if force or not _init_in_session.get("xueqiu"):
        _init_in_session["xueqiu"] = True
        await session.get("https://xueqiu.com")
    return True


async def async_get_funda(session, symbol, table, data_path=None, return_df=True):
    """
    从雪球获取财务数据

    :param session: `aiohttp.ClientSession` 对象，同步接口不需要传
    :param symbol: 股票代码
    :param table: 财务数据类型

                  MRCWZB    # 当日财务指标
                  GPSYLZB   # 股票收益率指标
                  ZYCWZB    # 主要财务指标
                  DJCWZB    # 单季财务指标
                  GSLRB     # 综合损益表
                  ZCFZB     # 资产负债表
                  XJLLB     # 现金流量表

    :param data_path: 数据保存路径
    :param return_df: 是否返回 `pandas.DataFrame` 对象，False 返回原始数据

    :returns: 原始数据或 `pandas.DataFrame` 对象，见 return_df 参数，
              如果是 MRCWZB/GPSYLZB table，直接返回字典，reture_df 参数无效
              失败则返回 `None`
    """
    assert table in FUNDA_TABLES
    await _init(session)

    page_size = 10000
    curr_page = 1
    params = {"_": 0, "symbol": symbol, "page": curr_page, "size": page_size}

    logger.info("start download funda2 from xueqiu for %s...", table)
    url = FUNDA_TABLES[table]
    params["_"] = int(time.time() * 1000)

    list_data = False
    date_str = str(date.today())
    async with session.get(url, params=params) as resp:
        if resp.status != 200:
            logger.warning("get funda2 from %s failed: %s", url, resp.status)
            return None
        funda_data = await resp.json()
        if "list" in funda_data:
            list_data = True
            funda_data = funda_data.get("list")

    if not funda_data:
        logger.warn("no funda2 data downloaded for %s from %s, return None", table, url)
        return None
    logger.info("download funda2 table %s from %s finish", table, url)
    if data_path:
        data_path = Path(data_path) / MODULE_DATA_DIR / "funda2"
        os.makedirs(data_path, exist_ok=True)
        data_fname = "-".join((symbol, table, date_str)) + ".json"
        data_file = data_path / data_fname
        with data_file.open("w") as dataf:
            json.dump(funda_data, dataf, indent=4, ensure_ascii=False)

    if not return_df or not list_data:
        return funda_data

    df = pd.DataFrame(funda_data)
    # set index
    # try:
    #     df.set_index("reportdate", inplace=True)
    # except KeyError:
    #     df.set_index("enddate", inplace=True)
    return df


@add_doc(async_get_funda.__doc__)
def get_funda(*args, **kwargs):
    ret = fetch_http_data(async_get_funda, *args, **kwargs)
    if isinstance(ret, Exception):
        raise ret
    return ret


@stock_cli_group.command("funda2")
@click.option("-s", "--symbol", required=True)
@click.option(
    "-t",
    "--table",
    type=click.Choice(FUNDA_TABLES),
    default="MRCWZB",
    show_default=True,
)
@click.option(
    "-f",
    "--save-path",
    type=click.Path(exists=False),
    default=get_config("data_path", os.getcwd()),
    show_default=True,
)
@click.option("-p/-np", "--print/--no-print", "show", default=True)
def funda2_cli(symbol, table, save_path, show):
    """从雪球获取财报数据"""
    data = get_funda(symbol, table, save_path)
    if show:
        click.echo(data)


if __name__ == "__main__":
    funda2_cli()
