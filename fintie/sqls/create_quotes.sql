CREATE TYPE tick_character AS ENUM ('buy', 'sell', 'mid');
CREATE TABLE IF NOT EXISTS tick_stock_quotes (
    time        TIMESTAMP NOT NULL,
    symbol      VARCHAR(12) NOT NULL,
    price       INTEGER,
    turnover    INTEGER,            -- 成交额，单位：分
    volume      INTEGER,            -- 成交量，单位：股
    character   tick_character,
    PRIMARY KEY (symbol, time)
);


CREATE TABLE IF NOT EXISTS minute_stock_quotes (
    time        TIMESTAMP NOT NULL,
    symbol      VARCHAR(12) NOT NULL,
    high        INTEGER,            -- 单位：分
    low         INTEGER,            -- 单位：分
    open        INTEGER,            -- 单位：分
    close       INTEGER,            -- 单位：分
    turnover    INTEGER,            -- 成交额，单位：分
    volume      INTEGER,            -- 成交量，单位：股
    PRIMARY KEY (symbol, time)
);

-- This creates a hypertable that is partitioned by time
--   using the values in the `time` column.
-- SELECT create_hypertable('conditions', 'time');
-- OR you can additionally partition the data on another
--   dimension (what we call 'space partitioning').
-- E.g., to partition `location` into 4 partitions:
SELECT create_hypertable('minute_stock_quotes',
                         'time',
                          chunk_time_interval => interval '1 month',
                          partitioning_column => 'symbol',
                          number_partitions => 8,
                          if_not_exists => TRUE);


CREATE TABLE IF NOT EXISTS day_stock_quotes (
    time        TIMESTAMP NOT NULL,
    symbol      VARCHAR(12) NOT NULL,
    high        INTEGER,            -- 单位：分
    low         INTEGER,            -- 单位：分
    open        INTEGER,            -- 单位：分
    close       INTEGER,            -- 单位：分
    turnover    BIGINT,             -- 成交额，单位：分
    volume      INTEGER,            -- 成交量，单位：股
    hlimit      INTEGER,            -- 单位：分
    llimit      INTEGER,            -- 单位：分
    PRIMARY KEY (symbol, time)
);
SELECT create_hypertable('day_stock_quotes',
                         'time',
                          chunk_time_interval => interval '1 year',
                          partitioning_column => 'symbol',
                          number_partitions => 8,
                          if_not_exists => TRUE);
