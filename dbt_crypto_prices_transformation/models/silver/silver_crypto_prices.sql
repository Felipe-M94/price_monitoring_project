WITH cleaned_data AS (
    SELECT
        symbol,
        name,
        CAST(price AS FLOAT) AS price,
        CAST(market_cap AS FLOAT) AS market_cap,
        CAST(volume_24h AS FLOAT) AS volume_24h,
        CAST(last_updated AS TIMESTAMP) AS last_updated,
        CAST(date AS TIMESTAMP) AS date,
        COALESCE(price, NULL) AS clean_price,
        COALESCE(market_cap, NULL) AS clean_market_cap,
        COALESCE(volume_24h, NULL) AS clean_volume_24h
    FROM {{ ref('stg_crypto_prices') }}
)

SELECT *
FROM cleaned_data
