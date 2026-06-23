WITH source AS (
    SELECT * FROM {{ source('raw_data', 'chargebacks') }}
),

staged AS (
    SELECT
        transaction_id,
        CAST(dispute_timestamp AS TIMESTAMP_NTZ) AS dispute_timestamp,
        UPPER(TRIM(dispute_category)) AS dispute_category
    FROM source
)

SELECT * FROM staged
