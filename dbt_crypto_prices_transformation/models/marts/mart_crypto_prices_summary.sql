WITH price_changes AS (
    SELECT
        symbol,
        date,
        clean_price AS price,
        LAG(clean_price) OVER (PARTITION BY symbol ORDER BY date) AS prev_price,
        clean_market_cap AS market_cap,
        clean_volume_24h AS volume_24h
    FROM {{ ref('silver_crypto_prices') }}
)

SELECT
    symbol,
    date,
    price,
    prev_price,
    ROUND(CAST((price - prev_price) / prev_price * 100 AS numeric), 2) AS price_variation,
    market_cap,
    volume_24h,

    -- Tendência do preço: Up, Down ou Stable
    CASE 
        WHEN price > prev_price THEN 'Up'
        WHEN price < prev_price THEN 'Down'
        ELSE 'Stable'
    END AS price_trend,

    -- Média móvel do preço nos últimos 7 dias
    ROUND(CAST(AVG(price) OVER (
        PARTITION BY symbol 
        ORDER BY date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS numeric), 2) AS moving_avg_7d

FROM price_changes
WHERE prev_price IS NOT NULL
