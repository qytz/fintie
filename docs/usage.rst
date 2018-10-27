Usage
=====

命令行模式
--------------

类似于其他的 `Linux` 命令行，具体使用见帮助::

    ~ fintie --help
    Usage: fintie [OPTIONS] COMMAND [ARGS]...

      Console script for fintie

      Copyright (C) 2017-present qytz <hhhhhf@foxmail.com>

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain a
      copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

      Project url: https://github.com/qytz/fintie

    Options:
      -v, --verbose
      -c, --conf PATH       配置文件  [default: ~/.config/fintie]
      -d, --data-path PATH  数据存储路径，会覆盖 conf 文件里的设置
      --help                Show this message and exit.

    Commands:
      stock  股票相关的数据

研究模式
----------

ipython 中导入 `fintie` 后使用，需使用封装过的同步接口，具体支持的数据见文档::

    ~ ipython
    Python 3.7.0 | packaged by conda-forge | (default, Jul 23 2018, 21:39:36) 
    Type 'copyright', 'credits' or 'license' for more information
    IPython 6.5.0 -- An enhanced Interactive Python. Type '?' for help.

    In [1]: from fintie import stock

    In [2]: stock.get_list_quotes?
    Signature: stock.get_list_quotes(*args, **kwargs)
    Docstring:
    获取每日行情概览信息，只能获取当天的
    返回一个 pd.DataFrame
    出错，返回 None

    :param session: `aiohttp.ClientSession` 对象，同步接口不需要传
    :param symbol: 股票代码
    :param data_type: stock: 沪深股票 cb: 可转债 eft: ETF基金 fenji: 分级基金
    :param data_path: 数据保存路径
    :param return_df: 是否返回 `pandas.DataFrame` 对象，False 返回原始数据

    :returns: 行情原始数据或带有行情数据的 `pandas.DataFrame` 对象，见 return_df 参数
    File:      /workstation/osc/qytz/fintie/fintie/stock/list_quotes.py
    Type:      function

    In [3]:

实时分析模式
---------------

在你的分析框架中直接通过导入 `fintie` 后调用 api 来获取数据并分析。
