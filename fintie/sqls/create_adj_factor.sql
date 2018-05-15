-- 复权因子
CREATE TABLE IF NOT EXISTS adj_factor_stock (
    day         DATE NOT NULL,
    symbol      VARCHAR(12) NOT NULL,
    factor      INTEGER,

    PRIMARY KEY (symbol, day)
);


-- 分红送股
CREATE TABLE IF NOT EXISTS dividend_stock (
    symbol              VARCHAR(12) NOT NULL,
    div_enddate         INTEGER,    -- 分红年度
    ann_date            DATE,       -- 预案公告日期
    publish_date        DATE,       -- 实施公告日期
    record_date         DATE,       -- 股权登记日
    exdiv_date          DATE,       -- 除权除息日
    cash                INTEGER,    -- 税前每股分红，单位：分
    cash_tax            INTEGER,    -- 税后每股分红，单位：分
    share_ratio         FLOAT,      -- 送股比例（每股）
    share_trans_ratio   FLOAT,      -- 转赠比例（每股）
    cashpay_date        DATE,       -- 派现日
    bonus_list_date     DATE,       -- 送股上市日

    PRIMARY KEY (symbol, record_date)
);


-- 停复牌
CREATE TABLE IF NOT EXISTS suspend_stock (
    symbol      VARCHAR(12) NOT NULL,
    ann_date    DATE,           -- 停牌公告日期
    susp_date   DATE,           -- 停牌开始日期
    susp_time   TIMESTAMP,      -- 停牌开始时间
    resu_date   TIMESTAMP,      -- 复牌日期
    resu_time   TIMESTAMP,      -- 复牌时间
    susp_reason TIMESTAMP,      -- 停牌原因

    PRIMARY KEY (symbol, record_date)
);
