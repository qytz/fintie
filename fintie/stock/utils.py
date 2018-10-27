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


FILTER_DICT = {
    "ASTOCKS": {"SH": "^SH6", "SZ": "^SZ00|^SZ30"},  # A股
    "BSTOCKS": {"SH": "^SH9", "SZ": "^SZ2"},  # B股
    "INDEX": {"SH": "^SH00", "SZ": "^SZ399"},  # 指数
    "ETF": {"SH": "^SH51", "SZ": "^SZ15|^SZ16"},
    "CB": {"SH": "^SH100|^SH110|^SSH112|^SH113", "SZ": "^SZ12"},  # 可转债
    "ALL": {"SH": "^SH", "SZ": "^SZ"},
}


def filter_by_symbol(df, symbol_type="ALL", market="ALL"):
    """根据 symbol 过滤返回符合条件的数据

    df 至少应包含 symbol 列，该列类型为字符串，内容规则如下：

        * SHxxxxxx    上海股票交易所代码
        * SZxxxxxx    深圳股票交易所代码

    symbol_type: ASTOCKS/BSTOCKS/INDEX/ETF/CB/ALL

        * ASTOCKS: A股股票
        * BSTOCKS: B股股票
        * INDEX: 指数
        * ETF: ETF基金
        * CB: CONVERTIBLE BONDS，可转债

    market: SZ/SH/ALL

        * SZ: 深圳股票交易所
        * SH: 上海股票交易所
        * ALL: 所有


    股票代码

    * 上海证券交易所

        ========   =========
        首位代码    产品定义
        ========   =========
        0           国债／指数
        00          上证指数、沪深300指数、中证指数
        １          债券
        ２          回购
        ３          期货
        ４          备用
        ５          基金／权证
        ６          A股
        ７          非交易业务（发行、权益分配）
        ８          备用
        ９          B股
        ========   =========

    * 深圳证券交易所

        ========   =========
        首位代码    产品定义
        ========   =========
        00          A股证券
        002~004     中小板
        1           债券
        2           B股
        30          创业板证券
        39          综合指数、成份指数
        ========   =========
    """
    if symbol_type == "ALL" and market == "ALL":
        return df
    if symbol_type not in FILTER_DICT:
        symbol_type = "ALL"
    if market in FILTER_DICT[symbol_type]:
        pat = FILTER_DICT[symbol_type][market]
    else:
        pat = "|".join(FILTER_DICT[symbol_type].values())
    return df[df.symbol.str.contains(pat)]
