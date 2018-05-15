-- 市场代码
-- 深交所	SZ
-- 上交所	SH
-- 中金所	CFE
-- 郑商所	CZC
-- 大商所	DCE
-- 上期所	SHF
-- 上金所	SGE
-- 中证指数	CSI
-- 港交所	HK

CREATE TABLE IF NOT EXISTS markets(
    symbol      VARCHAR NOT NULL,   -- 市场代码
    name        VARCHAR,            -- 市场名称
    nationcode  VARCHAR DEFAULT "CN",   -- 国家代码
    timezone    INTEGER DEFAULT 8,      -- 时区
    perioids    TIME[][],          -- 交易时段列表

    PRIMARY KEY (symbol)
);
