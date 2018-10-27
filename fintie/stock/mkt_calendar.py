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
"""每日市场事件

获取每日市场事件，事件类型包括：

    * 停牌、复牌
    * 首发新股上市
    * 首发新股招股书刊登
    * 首发新股网上发行
    * 中签率公告
    * 授予股份上市
    * 股东资格登记
    * 股东大会召开
    * 网络投票开始、网络投票结束
    * 分红转增股权登记、分红转增除权除息、分红转增红利发放、分红转增股份上市
    * 增发新股招股书刊登

等，信息获取通道包括：

    http://www.cninfo.com.cn/cninfo-new/memo?queryDate=2017-07-19

加载已保存的数据::

    import json

    from pathlib import Path
    with open(Path("xxx.json")) as f:
        data = json.load(f)
"""
import os
import json
import asyncio
import logging
from pathlib import Path
from datetime import date, timedelta

import click
import aiohttp

from .cli import stock_cli_group, MODULE_DATA_DIR
from ..config import get_config
from ..utils import iter_dt, parse_dt, fetch_http_data, add_doc


__all__ = ["async_get_market_events", "get_market_events"]
logger = logging.getLogger(__file__)


async def _init(session, force=False):
    return True


async def async_get_market_events(session, start, end, data_path=None):
    """从巨潮信息网获取某天的交易日历

    :param session: `aiohttp.ClientSession` 对象，同步接口不需要传
    :param start: 日历数据开始时间
    :param end: 日历数据结束时间
    :param data_path: 数据保存路径

    :returns: 日历数据 `dict`
    """
    datas = {}
    await _init(session)

    async def fetch_one_day(day_str):
        url = "http://www.cninfo.com.cn/cninfo-new/memo/memoQuery"
        try:
            async with session.post(url, data={"queryDate": day_str}) as resp:
                datas[day_str] = await resp.json()
        except (aiohttp.ServerTimeoutError, asyncio.TimerHandle) as e:
            logger.warning("Download calendar event data for %s failed：%s.", day_str, e)

    aws = []
    for day in iter_dt(start, end, include_end=True):
        day_str = day.strftime("%Y-%m-%d")
        aws.append(fetch_one_day(day_str))
    await asyncio.gather(*aws, return_exceptions=True)
    logger.info("calendar event data from %s to %s has been downloaded.", start, end)

    if data_path:
        file_path = Path(data_path) / MODULE_DATA_DIR / "market_events"
        os.makedirs(file_path, exist_ok=True)
        data_file = (
            file_path / f"{start.strftime('%Y%m%d')}-{end.strftime('%Y%m%d')}.json"
        )
        with data_file.open("w") as dataf:
            json.dump(datas, dataf, indent=4, ensure_ascii=False)
        logger.info("calendar data has been saved to: %s", data_file)
    return datas


@add_doc(async_get_market_events.__doc__)
def get_market_events(*args, **kwargs):
    ret = fetch_http_data(async_get_market_events, *args, **kwargs)
    if isinstance(ret, Exception):
        raise ret
    return ret


@stock_cli_group.command("cale")
@click.option(
    "-st", "--start", default=str(date.today() - timedelta(days=30)), show_default=True
)
@click.option("-ed", "--end", default=str(date.today()), show_default=True)
@click.option(
    "-f",
    "--save-path",
    type=click.Path(exists=False),
    default=get_config("data_path", os.getcwd()),
    show_default=True,
)
@click.option("-p/-np", "--print/--no-print", "show", default=True)
def market_events_cli(start, end, save_path, show):
    """从cninfo获取日历事件"""
    start_dt = parse_dt(start)
    end_dt = parse_dt(end)
    data = get_market_events(start_dt, end_dt, save_path)
    if show:
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    market_events_cli()
