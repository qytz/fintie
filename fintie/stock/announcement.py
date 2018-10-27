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
"""本模块负责获取上市公司公告文件

信息获取通道：

    post http://www.cninfo.com.cn/cninfo-new/announcement/query

    post form::

        category: category_ndbg_szsh;category_bndbg_szsh;
        column:
        limit:
        pageNum: 1
        pageSize: 30
        searchkey: // 搜索关键字
        seDate: // 查询日期: 2018-07-28 或者 2018-03-13+~+2018-07-28
        sortName:
        sortType:
        stock: 300121
        tabName: fulltext

    category 类型

        * name="category_ndbg_szsh" title="年度报告"
        * name="category_bndbg_szsh" title="半年度报告"
        * name="category_yjdbg_szsh" title="一季度报告"
        * name="category_sjdbg_szsh" title="三季度报告"
        * name="category_scgkfx_szsh" title="首次公开发行及上市"
        * name="category_pg_szsh" title="配股"
        * name="category_zf_szsh" title="增发"
        * name="category_kzhz_szsh" title="可转换债券"
        * name="category_qzxg_szsh" title="权证相关公告"
        * name="category_qtrz_szsh" title="其他融资"
        * name="category_qyfpxzcs_szsh" title="权益及限制出售股份"
        * name="category_gqbd_szsh" title="股权变动"
        * name="category_jy_szsh" title="交易"
        * name="category_gddh_szsh" title="股东大会"
        * name="category_cqfxyj_szsh" title="澄清风险业绩预告"
        * name="category_tbclts_szsh" title="特别处理和退市"
        * name="category_bcgz_szsh" title="补充及更正"
        * name="category_zjjg_szsh" title="中介机构报告"
        * name="category_ssgszd_szsh" title="上市公司制度"
        * name="category_zqgg_szsh" title="债券公告"
        * name="category_qtzdsx_szsh" title="其它重大事项"
        * name="category_tzzgx_szsh" title="投资者关系信息"
        * name="category_dshgg_szsh" title="董事会公告"
        * name="category_jshgg_szsh" title="监事会公告"

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
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

import click
import aiohttp

from .cli import stock_cli_group, MODULE_DATA_DIR
from ..config import get_config
from ..utils import parse_dt, fetch_http_data, add_doc


logger = logging.getLogger(__file__)
__all__ = ["get_announcements", "async_get_announcements"]


async def _init(session):
    return True


async def _get_one_announcement(session, url, fname):
    try:
        resp = await session.get(url)
        if resp.status != 200:
            logger.warning(
                "Download announcement %s from url failed: http %s", url, resp.status
            )
            return None
        raw_data = await resp.read()
    except (aiohttp.ServerTimeoutError, asyncio.TimerHandle):
        logger.warning("Download announcement %s failed：timeout", fname)
        return None
    with Path(fname).open("wb") as statf:
        statf.write(raw_data)
    return True


async def async_get_announcements(
    session,
    symbol,
    categories,
    data_path,
    start_date=None,
    end_date=None,
    search_key="",
):
    """获取公告文件

    :param session: `aiohttp.ClientSession` 对象，同步接口不需要传
    :param symbol: 股票代码
    :param categories: 公告文件类别
    :param data_path: 数据保存路径
    :param start_date: 公共查询起始时间
    :param end_date: 公告查询截止时间
    :param search_key: 公告查询搜索关键字
    :returns: None 接口用于下载公告原文进行人工分析，不返回任何数据

    catetories::

        all         所有类别
        ndbg        年度报告
        bndbg       半年度报告
        yjdbg       一季度报告
        sjdbg       三季度报告
        scgkfx      首次公开发行及上市
        pg          配股
        zf          增发
        kzhz        可转换债券
        qzxg        权证相关公告
        qtrz        其他融资
        qyfpxzcs    权益及限制出售股份
        gqbd        股权变动
        jy          交易
        gddh        股东大会
        cqfxyj      澄清风险业绩预告
        tbclts      特别处理和退市
        bcgz        补充及更正
        zjjg        中介机构报告
        ssgszd      上市公司制度
        zqgg        债券公告
        qtzdsx      其它重大事项
        tzzgx       投资者关系信息
        dshgg       董事会公告
        jshgg       监事会公告

    """
    await _init(session)
    cate_list = [f"category_{cat}_szsh" for cat in categories]
    category_str = ";".join(cate_list) + ";"
    date_str = ""
    if start_date and end_date:
        date_str = f"{start_date}+~+{end_date}"

    page_size = 30
    page_cnt = 1
    page_num = 1

    logger.info("Downloading announcements data for %s", symbol)
    query_url = "http://www.cninfo.com.cn/information/companyinfo_n.html"
    await session.get(query_url)
    post_url = "http://www.cninfo.com.cn/cninfo-new/announcement/query"

    cninfo_symbol = symbol
    if cninfo_symbol.startswith("SZ") or cninfo_symbol.startswith("SH"):
        cninfo_symbol = cninfo_symbol[2:]
    post_form = {
        "category": category_str,
        "column": "",
        "limit": "",
        "pageNum": 1,
        "pageSize": page_size,
        "searchkey": search_key,
        "seDate": date_str,
        "sortName": "",
        "sortType": "",
        "stock": cninfo_symbol,
        "tabName": "fulltext",
    }

    announcements = []
    logger.info("Downloading announcements meta data for %s", symbol)
    while page_num <= page_cnt:
        post_form["pageNum"] = [page_num]
        try:
            async with session.post(post_url, data=post_form) as resp:
                if resp.status != 200:
                    logger.warning(
                        "Download announcement metadata from %s failed: http %s",
                        post_url,
                        resp.status,
                    )
                    break
                data = await resp.json()
                if "totalAnnouncement" in data:
                    total_cnt = data["totalAnnouncement"]
                elif "totalRecordNum" in data:
                    total_cnt = data["totalRecordNum"]
                else:
                    logger.warning(
                        "Download announcements meta data for %s failed: %s",
                        symbol,
                        data,
                    )
                    break
                page_cnt = total_cnt // page_num
                if total_cnt % page_num != 0:
                    page_cnt += 1
                if "announcements" in data:
                    announcements.extend(data["announcements"])
        except (aiohttp.ServerTimeoutError, asyncio.TimeoutError) as e:
            logger.warning(
                "Download announcements meta data for %s timeout: %s", symbol, e
            )
            continue
        page_num += 1

    if not announcements:
        logger.warning("no announcements data found for %s", symbol)
        return
    logger.info("Download announcements meta data for %s finished", symbol)

    symbol_data_dir = Path(data_path) / MODULE_DATA_DIR / symbol / "announcements"
    os.makedirs(symbol_data_dir, exist_ok=True)
    meta_file = symbol_data_dir / f"{symbol}_meta.json"
    with meta_file.open("w") as dataf:
        json.dump(announcements, dataf, indent=4, ensure_ascii=False)

    aws = []
    logger.info("Downloading announcements files for %s", symbol)
    for announcement in announcements:
        logger.info(
            "Downloading %s from %s",
            announcement["announcementTitle"],
            announcement["adjunctUrl"],
        )
        annou_name = announcement.get("announcementTitle", None)
        if not annou_name:
            annou_name = announcement.get("announcementId", None)
        if not annou_name:
            annou_name = announcement.get("orgId", None)
        if not annou_name:
            logger.warning("No file name found, skipped: %s", announcement)
            continue
        annou_time = ""
        if "announcementTime" in announcement:
            annou_time = datetime.fromtimestamp(announcement["announcementTime"] / 1000)
            annou_time = annou_time.strftime("%Y%m%d%H%M%S")
        ftype = announcement.get("adjunctType", "raw")
        fpath = symbol_data_dir / f"{annou_name}-{annou_time}.{ftype}"

        url = "http://www.cninfo.com.cn/" + announcement["adjunctUrl"]
        aws.append(_get_one_announcement(session, url, fpath))
    await asyncio.gather(*aws, return_exceptions=True)
    logger.info("Download announcements files for %s finished", symbol)
    return None


@add_doc(async_get_announcements.__doc__)
def get_announcements(*args, **kwargs):
    ret = fetch_http_data(async_get_announcements, *args, **kwargs)
    if isinstance(ret, Exception):
        raise ret
    return ret


@stock_cli_group.command("announce", short_help="获取公告原文")
@click.option("-s", "--symbol", type=str, required=True)
@click.option(
    "-st",
    "--start",
    default=str(date.today().replace(month=1, day=1) - relativedelta(years=3)),
    show_default=True,
)
@click.option("-ed", "--end", default=str(date.today()), show_default=True)
@click.option(
    "-ct", "--category", default="ndbg,bndbg,yjdbg,sjdbg", show_default=True, type=str
)
@click.option("-se", "--search", default=True)
@click.option(
    "-f",
    "--file-path",
    "save_path",
    type=click.Path(exists=False),
    default=get_config("data_path", os.getcwd()),
)
def announcements_cli(symbol, start, end, save_path, category, search):
    """从cninfo获取公告原文

    symbol: 使用雪球网的代码格式

    announcements category

    \b
        all         所有类别
        ndbg        年度报告
        bndbg       半年度报告
        yjdbg       一季度报告
        sjdbg       三季度报告
        scgkfx      首次公开发行及上市
        pg          配股
        zf          增发
        kzhz        可转换债券
        qzxg        权证相关公告
        qtrz        其他融资
        qyfpxzcs    权益及限制出售股份
        gqbd        股权变动
        jy          交易
        gddh        股东大会
        cqfxyj      澄清风险业绩预告
        tbclts      特别处理和退市
        bcgz        补充及更正
        zjjg        中介机构报告
        ssgszd      上市公司制度
        zqgg        债券公告
        qtzdsx      其它重大事项
        tzzgx       投资者关系信息
        dshgg       董事会公告
        jshgg       监事会公告
    """
    start_dt = parse_dt(start, return_date=True)
    end_dt = parse_dt(end, return_date=True)

    data = get_announcements(
        symbol, category.split(","), save_path, start_dt, end_dt, search_key=""
    )
    if isinstance(data, Exception):
        raise data


if __name__ == "__main__":
    announcements_cli()
