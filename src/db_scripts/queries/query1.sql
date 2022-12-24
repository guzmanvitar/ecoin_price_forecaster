WITH monthly_data AS (
    SELECT
        coin_id,
        CONCAT(CAST(DATE_PART('year', date) AS VARCHAR(4)), '-',
            CAST(DATE_PART('month', date) AS VARCHAR(2))) year_month,
        usd_price
    FROM
        coingecko_scraped_data)
SELECT
    coin_id,
    year_month,
    AVG(usd_price) usd_price_avg
FROM
    monthly_data
GROUP BY
    coin_id,
    year_month;