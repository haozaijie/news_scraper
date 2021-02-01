-- then run 'psql -f init_table.sql'

BEGIN;

ALTER USER haozaijie PASSWORD 'password';

DROP SCHEMA IF EXISTS news_scraper;

DROP TABLE IF EXISTS news_scraper.raw ;
DROP TABLE IF EXISTS news_scraper.daily_count ;
DROP TABLE IF EXISTS news_scraper.sentiment ;

CREATE SCHEMA news_scraper;

CREATE TABLE news_scraper.raw (
    date date NOT NULL,
    headline varchar(100) NOT NULL,
    body varchar(100),
    source varchar(10) NOT NULL,
    PRIMARY KEY (date, headline, source)
);

CREATE TABLE news_scraper.daily_count (
    date date NOT NULL,
    cnn INTEGER,
    wsj INTEGER,
    PRIMARY KEY (date)
);

CREATE TABLE news_scraper.sentiment (
    date date NOT NULL,
    weighted_polarity_CNN FLOAT,
    weighted_polarity_WSJ FLOAT,
    weighted_subjectivity_CNN FLOAT,
    weighted_subjectivity_WSJ FLOAT,
    PRIMARY KEY (date) 
);

COMMIT;
