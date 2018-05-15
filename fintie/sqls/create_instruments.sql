CREATE TABLE IF NOT EXISTS instruments (
    symbol      VARCHAR NOT NULL,   -- 代码
    instype     INTEGER,            -- 类型
    market      VARCHAR,            -- 交易所
    buylot      INTEGER,            -- 最小买入单位，单位：分
    selllot     INTEGER,            -- 最小卖出单位，单位：分
    pricetick   INTEGER,            -- 最小价格变动单位，单位：分
    multiplier  INTEGER,            -- 合约乘数
    underlying  VARCHAR,            -- 对应标的

    list_date   DATE,               -- 上市日期
    delist_date DATE,               -- 退市日期
    issue_price INTEGER,            -- 发行价格
    currency    VARCHAR,            -- 货币
    product     VARCHAR,            -- 合约品种

    PRIMARY KEY (symbol)
);


-- 证券类型定义
-- 股票    1
-- 封闭式基金  2
-- LOF基金 3
-- ETF基金 4
-- 分级基金    5
-- 国债商品    6
-- 商品    7
-- 可转债  8
-- 回购    10
-- 国债    11
-- 地方政府债  12
-- 金融债  13
-- 企业债  14
-- 公司债  15
-- 资产支持证券    16
-- 可交换债    17
-- 可分离转债存债  18
-- 政府支持机构债  19
-- 转股换股    20
-- 指数    100
-- 股指期货    101
-- 国债期货    102
-- 商品期货    103
-- 股指ETF期权 201
-- 股指期货期权    202
-- 商品期货期权    203
