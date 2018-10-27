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
"""行情获取模块

本模块负责获取股票的历史交易行情信息。

获取通道包括：

    Get https://stock.xueqiu.com/v5/stock/chart/kline.json

    params::

        "symbol": 代码
        "begin": 时间戳
        "period": 频率,
        "type": 复权类型,
        "count": 数量,
        "indicator": "kline,ma,macd,kdj,boll,rsi,wr,bias,cci,psy",

加载::

    from pathlib import Path
    import pandas as pd

    with Path('data.json').open() as f:
        quotes = json.load(f)

    df = pd.DataFrame(data=quotes['item'], column=quotes['column'])
    df.timestamp = pd.to_datetime(df.timestamp, unit='ms')
    df.set_index('timestamp', inplace=True)

TODO

    * add default http headers

      headers = {"X-Forwarded-For": ipAddress}

    * 163 - 日K线数据

      Get http://quotes.money.163.com/service/chddata.html?code=1000333&start=20130918&end=20180803&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP
"""
import os
import json
import logging
from pathlib import Path
from datetime import datetime

import click
import pandas as pd

from .cli import stock_cli_group, MODULE_DATA_DIR
from ..env import _init_in_session
from ..config import get_config
from ..utils import parse_dt, fetch_http_data, add_doc


logger = logging.getLogger(__file__)
__all__ = ["async_get_hist_quotes", "get_hist_quotes"]


SUPPORTED_FREQ = (
    "1m",
    "5m",
    "15m",
    "30m",
    "60m",
    "120m",
    "day",
    "week",
    "month",
    "quarter",
    "year",
)
FQ_TYPE = ("before", "after", "normal")


async def _init(session, force=False):
    if force or not _init_in_session.get("xueqiu"):
        _init_in_session["xueqiu"] = True
        await session.get("https://xueqiu.com")
    return True


async def async_get_hist_quotes(
    session,
    symbol,
    ref_dt,
    count=100,
    freq="1m",
    fq_type="before",
    data_path=None,
    return_df=True,
):
    """
    小于 day 频率的数据，会有时间限制，只能取最近的数据，请谨慎使用

    :param session: `aiohttp.ClientSession` 对象，同步接口不需要传
    :param symbol: 股票代码
    :param ref_dt: 行情数据参考日期，count 传负是截止日期，传正为开始日期
    :param count: 要取的行情数据的条数
    :param freq: 数据频率：1m/5m/15m/30m/60m/120m/day/week/month/quarter/year
    :param fq_type: before/after/normal 前复权、后复权、不复权
    :param data_path: 数据保存路径
    :param return_df: 是否返回 `pandas.DataFrame` 对象，False 返回原始数据

    :returns: 行情原始数据或带有行情数据的 `pandas.DataFrame` 对象，见 return_df 参数
    """
    assert freq in SUPPORTED_FREQ
    await _init(session)
    url = "https://stock.xueqiu.com/v5/stock/chart/kline.json"
    params = {
        "symbol": "SZ002353",
        "begin": int(ref_dt.timestamp()) * 1000,
        "period": freq,
        "type": fq_type,
        "count": count,
        "indicator": "kline,ma,macd,kdj,boll,rsi,wr,bias,cci,psy",
    }
    async with session.get(url, params=params) as resp:
        if resp.status != 200:
            logger.warning("get history quotes from %s failed: %s", url, resp.status)
            return None
        data = await resp.json()
        if data.get("error_code", -1) != 0:
            logger.warning("get history quotes from %s failed: %s", url, resp.status)
            return None
        quotes = data.get("data", {})

    if data_path:
        file_path = Path(data_path) / MODULE_DATA_DIR / symbol / "hist_quotes"
        os.makedirs(file_path, exist_ok=True)
        data_fname = (
            "-".join(
                (symbol, freq, ref_dt.strftime("%Y%m%d%H%M%S"), str(count), fq_type)
            )
            + ".json"
        )
        data_file = file_path / data_fname
        with data_file.open("w") as dataf:
            json.dump(quotes, dataf, indent=4, ensure_ascii=False)

    if not return_df:
        return quotes

    df = pd.DataFrame(data=quotes["item"], columns=quotes["column"])
    df.timestamp = pd.to_datetime(df.timestamp, unit="ms")
    df.set_index("timestamp", inplace=True)
    return df


@add_doc(async_get_hist_quotes.__doc__)
def get_hist_quotes(*args, **kwargs):
    ret = fetch_http_data(async_get_hist_quotes, *args, **kwargs)
    if isinstance(ret, Exception):
        raise ret
    return ret


@stock_cli_group.command("hist-quotes")
@click.option("-s", "--symbol", required=True)
@click.option(
    "-ed", "--end-dt", default=str(datetime.now()), show_default=True, help="行情截止时间"
)
@click.option("-c", "--count", default=200, show_default=True, help="行情条数")
@click.option(
    "-fq",
    "--freq",
    default="day",
    type=click.Choice(SUPPORTED_FREQ),
    show_default=True,
    help="行情的频率",
)
@click.option(
    "-ft",
    "--fq-type",
    default="before",
    type=click.Choice(FQ_TYPE),
    show_default=True,
    help="复权类型",
)
@click.option(
    "-f",
    "--save-path",
    type=click.Path(exists=False),
    show_default=True,
    default=get_config("data_path", os.getcwd()),
)
@click.option("-p/-np", "--print/--no-print", "show", default=True)
def hist_quotes_cli(symbol, end_dt, count, freq, fq_type, save_path, show):
    """从雪球获取历史行情数据

    day 以下的 freq 会有条数和时间限制，只能获取最近的数据
    """
    end_dt = parse_dt(end_dt)
    data = get_hist_quotes(symbol, end_dt, -count, freq, fq_type, save_path)
    if show:
        click.echo(data)


if __name__ == "__main__":
    hist_quotes_cli()
