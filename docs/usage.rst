Usage
=====

命令行模式
--------------

类似于其他的 `Linux` 命令行，具体使用见帮助::

    ➜  ~ fintie stock list-quotes
    配置文件(~/.config/fintie)不存在，配置设置为空
                    amount change    code current hasexist   high high52w    low low52w      marketcapital  name percent   pettm type     volume
    symbol
    SZ002703   1.9345087E7   0.36  002703    3.93    false   3.93   11.04   3.56   3.15    3.10330341948E9  浙江世宝   10.08           11    5012710
    SH601162   5.0454054E7   0.46  601162    5.03    false   5.03    5.03   5.03   2.15         2.60554E10  天风证券   10.07   66.71   11   10030627
    SZ002725   3.1738561E7   0.68  002725    7.44    false   7.44   14.29   6.89    6.1          1.90464E9  跃岭股份   10.06   85.69   11    4370724
    SH603508   2.3323164E7   1.75  603508   31.75    false  32.98   54.81  30.83  29.52             5.08E9  思维列控    5.83   30.73   11     728995
    ...                ...    ...     ...     ...      ...    ...     ...    ...    ...                ...   ...     ...     ...  ...        ...
    SZ002563    5.519006E7  -0.87  002563    7.82    false   8.02    14.9   7.82   6.94    2.1112809014E10  森马服饰  -10.01   15.11   11    7026634
    SZ002668      378777.0  -1.18  002668   10.61    false  10.61   21.25  10.61  10.37  1.150242225108E10  奥马电器  -10.01   24.99   11      35700
    SZ002766   7.2889188E7  -0.68  002766    6.11    false   6.47   18.44   6.11   5.76    2.57691702554E9  索菱股份  -10.01   25.98   11   11736800
    SZ000691   5.2487015E7   -0.4  000691    3.58    false    3.8    8.13   3.58   2.91        1.1573066E9  亚太实业  -10.05  118.18   11   14362700

    [5524 rows x 15 columns]
    (ms) ➜  ~ fintie stock picker-xq areacode=CN440000 pct=0_1 eps.20180630=ALL
    配置文件(~/.config/fintie)不存在，配置设置为空
    {'areacode': 'CN440000', 'pct': '0_1', 'eps.20180630': 'ALL'}
              current                  eps exchange  hasExist                        id   name   pct   volume
    symbol
    SZ300738    39.50    {'20180630': 0.4}       SZ     False  5a61ca9ce4b0ccdd7efc66b1   奥飞数据  0.38     4.88
    SZ300737     8.72   {'20180630': 0.22}       SZ     False  5a69b3cfe4b0ccdd7efc66b6   科顺股份  0.35    20.01
    SZ300735    14.43   {'20180630': 0.25}       SZ     False  5a461aa2e4b085b00b16fbd0   光弘科技  0.21    31.53
    SZ300716    12.47   {'20180630': 0.19}       SZ     False  5a042fd3e4b0b3a1533e0d36   国立科技  0.65    24.93
    ...           ...                  ...      ...       ...                       ...    ...   ...      ...
    SH600428     3.27   {'20180630': 0.03}       SH     False  52dce039e4b0413d505ca423   中远海特  0.00    84.98
    SH600242    13.00   {'20180630': 0.09}       SH     False  52dcdf35e4b0413d505ca2fd   中昌数据  0.08     8.62
    SH600036    28.03   {'20180630': 1.77}       SH     False  52dcde02e4b0413d505ca1a0   招商银行  0.65  1561.79
    SH600030    16.68   {'20180630': 0.46}       SH     False  52dcddfae4b0413d505ca199   中信证券  0.18  2179.21

    [158 rows x 8 columns]
    (ms) ➜  ~

研究模式
----------

ipython 中导入 `fintie` 后使用，需使用封装过的同步接口，具体支持的数据见文档::

    ➜  ~ ipython
    Python 3.7.0 | packaged by conda-forge | (default, Jul 23 2018, 21:39:36)
    Type 'copyright', 'credits' or 'license' for more information
    IPython 7.1.1 -- An enhanced Interactive Python. Type '?' for help.

    In [1]: from datetime import datetime, timedelta, date

    In [2]: from fintie import stock
    配置文件(~/.config/fintie)不存在，配置设置为空

    In [3]: filter_dict = {'current': "ALL", "fmc":"ALL", "eps.20180630":"ALL", "bps.20180630": "ALL", "roediluted.20180630": "ALL", "volume":"ALL"}

    In [4]: df = stock.pick_stocks(filter_dict=filter_dict)

    In [5]: print(df[:3])
                             bps  current                 eps exchange      fmc  hasExist                        id  name   pct          roediluted  volume
    symbol
    SZ300749  {'20180630': 4.37}    27.60  {'20180630': 0.28}       SZ   7.8660     False  5baa116ce4b07f0b4a739de8  顶固集创 -5.15  {'20180630': 6.72}  190.68
    SZ300748  {'20180630': 2.23}    22.95  {'20180630': 0.14}       SZ   9.5472     False  5ba4cb54e4b07f0b4a739de5  金力永磁 -4.10  {'20180630': 6.38}  296.39
    SZ300694   {'20180630': 4.1}    23.10  {'20180630': 0.36}       SZ  12.4347     False  5bc46fa9c1362b7c0e7cc120  蠡湖股份 -0.22  {'20180630': 9.29}  383.60

    In [6]: df = stock.get_list_quotes()

    In [7]: print(df[:3])
                   amount change    code current hasexist  high high52w   low low52w    marketcapital  name percent  pettm type   volume
    symbol
    SZ002703    1.86383E7   0.36  002703    3.93    false  3.93   11.04  3.56   3.15  3.10330341948E9  浙江世宝   10.08          11  4832866
    SH601162  4.9397754E7   0.46  601162    5.03    false  5.03    5.03  5.03   2.15       2.60554E10  天风证券   10.07  66.71   11  9820627
    SZ002725  3.1498993E7   0.68  002725    7.44    false  7.44   14.29  6.89    6.1        1.90464E9  跃岭股份   10.06  85.69   11  4338524

    In [8]: df = stock.get_live_info("SZ002353")

    In [9]: df
    Out[9]:
    {'market': {'status_id': 5,
      'region': 'CN',
      'status': '交易中',
      'time_zone': 'Asia/Shanghai'},
     'quote': {'symbol': 'SZ002353',
      'code': '002353',
      'high52w': 23.34,
      'avg_price': 19.77,
      'type': 11,
      ...
      'exchange': 'SZ',
      'pe_forecast': 39.072,
      'time': 1540865460000,
      'total_shares': 957853992,
      'open': 20.1,
      'status': 1},
     'others': {'pankou_ratio': 46.41},
     'tags': [{'description': '深港通', 'value': 3},
      {'description': '融', 'value': 6},
      {'description': '空', 'value': 7}]}

    In [10]: df = stock.get_fhsp?
    Signature: stock.get_fhsp(*args, **kwargs)
    Docstring:
    从雪球获取分红送配股数据

    :param session: `aiohttp.ClientSession` 对象，同步接口不需要传
    :param symbol: 股票代码
    :param data_path: 数据保存路径
    :param return_df: 是否返回 `pandas.DataFrame` 对象，False 返回原始数据

    :returns: 原始数据或 `pandas.DataFrame` 对象，见 return_df 参数，
              失败则返回 `None`
    File:      /workstation/osc/qytz/fintie/fintie/stock/fenhong.py
    Type:      function

    In [11]: df = stock.get_fhsp("SZ002353")

    In [12]: print(df)
      bonusimpdate bonusskaccday bonussklistdate bonusskratio bonusyear  cdividend      ...      symbol taxcdividend taxfdividendbh tranaddskaccday  tranaddsklistdate tranaddskraio
    0     20180504          None            None         None      2017        1.2      ...        None        1.200            0.0            None               None           NaN
    1     20170602          None            None         None      2016        0.3      ...        None        0.300            0.0            None               None           NaN
    2     20160513          None            None         None      2015        0.3      ...        None        0.300            0.0            None               None           NaN
    3     20150520          None            None         None      2014        2.0      ...        None        1.900            0.0            None               None           NaN
    4     20140531          None            None         None      2013        2.5      ...        None        2.375            0.0        20140609           20140609           5.0
    5     20130522          None            None         None      2012        2.5      ...        None        2.375            0.0        20130528           20130528           3.0
    6     20120410          None            None         None      2011        3.0      ...        None        2.700            0.0        20120417           20120417          10.0
    7     20110414          None            None         None      2010        8.0      ...        None        7.200            0.0        20110421           20110421          10.0
    8     20100603          None            None         None      2009        6.0      ...        None        5.400            0.0            None               None           NaN

    [9 rows x 20 columns]

    In [13]:

Notebook 使用
-------------------
根据 `Async Notebook 的问题 <https://github.com/jupyter/notebook/issues/3397>`_ ，需要升级到最新版本的
`Notebook` ，并使用异步数据获取接口。

`使用Notebook的例子 <_static/notebook_sample.ipynb>`_

实时分析模式
---------------

在你的分析框架中直接通过导入 `fintie` 后调用 api 来获取数据并分析。
