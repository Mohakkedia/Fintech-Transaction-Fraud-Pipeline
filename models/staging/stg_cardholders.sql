WITH source AS (
    SELECT * FROM {{ source('raw_data', 'cardholder_profiles') }}
),

staged AS (
    SELECT
        cardholder_id,
        TRIM(name) AS cardholder_name,
        CAST(credit_risk_score AS INT) AS credit_risk_score,
        UPPER(TRIM(kyc_status)) AS kyc_status,
        CAST(daily_limit AS NUMBER(10,2)) AS daily_spending_limit
    FROM source
)

SELECT * FROM staged
