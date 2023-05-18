/*
Get the current market cap and the average uptake after three consecutive periods of price drop
for every coin in the scraping database
*/
WITH price_lags AS (
    SELECT
        coin_id,
        usd_price,
        LAG(usd_price, 1) OVER (PARTITION BY coin_id ORDER BY date ASC) lag1,
        LAG(usd_price, 2) OVER (PARTITION BY coin_id ORDER BY date ASC) lag2,
        LAG(usd_price, 3) OVER (PARTITION BY coin_id ORDER BY date ASC) lag3,
        LAG(usd_price, 4) OVER (PARTITION BY coin_id ORDER BY date ASC) lag4
    FROM
        coingecko_scraped_data),
ranked AS (
    SELECT
        coin_id,
        full_response->'market_data'->'market_cap'->'usd' market_cap,
        RANK() OVER(PARTITION BY coin_id ORDER BY date DESC) as date_rank
    FROM
        coingecko_scraped_data),
current_market_cap AS (
    SELECT
        coin_id,
        market_cap current_market_cap
    FROM
        ranked
    WHERE
        date_rank = 1),
avg_uptake_price AS (
    SELECT
        coin_id,
        AVG(usd_price - lag1) avg_uptake_price
    FROM
        price_lags
    WHERE
        lag1 IS NOT NULL
        AND usd_price > lag1
        AND lag1 < lag2
        AND lag2 < lag3
        AND lag3 < lag4
    GROUP BY
        coin_id)
SELECT
    a.coin_id,
    a.avg_uptake_price,
    c.current_market_cap
FROM
    avg_uptake_price a
JOIN
    current_market_cap c
ON
    a.coin_id = c.coin_id;