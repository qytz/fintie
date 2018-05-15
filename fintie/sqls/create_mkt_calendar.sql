CREATE TABLE IF NOT EXISTS mkt_calendar (
    day   DATE,
    events JSONB,

    PRIMARY KEY (day)
);
