WITH source AS (
    SELECT * FROM {{ source('raw_data', 'transactions') }}
),

staged AS (
    SELECT
        transaction_id,
        cardholder_id,
        -- Cast string timestamp to TIMESTAMP format
        CAST(timestamp AS TIMESTAMP_NTZ) AS transaction_timestamp,
        -- Ensure amount is represented as float/decimal
        CAST(amount AS NUMBER(10,2)) AS transaction_amount,
        UPPER(TRIM(merchant_category)) AS merchant_category,
        TRIM(merchant_id) AS merchant_id,
        TRIM(merchant_name) AS merchant_name,
        TRIM(city) AS transaction_city
    FROM source
)

SELECT * FROM staged
