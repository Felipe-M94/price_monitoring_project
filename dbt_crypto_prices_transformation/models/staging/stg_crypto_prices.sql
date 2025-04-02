WITH raw_crypto AS (
    SELECT
        name,
        symbol,
        CAST(price AS FLOAT) AS price,
        CAST(market_cap AS FLOAT) AS market_cap,
        CAST(volume_24h AS FLOAT) AS volume_24h,
        CAST(last_updated AS TIMESTAMP) AS last_updated,
        CAST(timestamp AS TIMESTAMP) AS ingestion_timestamp
    FROM {{ source('crypto', 'crypto_prices') }}
    WHERE price IS NOT NULL AND price > 0
)

SELECT
    name,
    symbol,
    price,
    market_cap,
    volume_24h,
    last_updated,
    ingestion_timestamp,
    ingestion_timestamp::DATE AS date
FROM raw_crypto
