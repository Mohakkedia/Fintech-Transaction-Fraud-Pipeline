WITH transactions AS (
    SELECT * FROM {{ ref('stg_transactions') }}
),

cardholders AS (
    SELECT * FROM {{ ref('stg_cardholders') }}
),

chargebacks AS (
    SELECT * FROM {{ ref('stg_chargebacks') }}
),

-- 1. Compute time and amount differences between consecutive transactions
transactions_lagged AS (
    SELECT
        t.*,
        -- Seconds since previous transaction by this cardholder
        DATEDIFF(
            second, 
            LAG(t.transaction_timestamp) OVER (PARTITION BY t.cardholder_id ORDER BY t.transaction_timestamp), 
            t.transaction_timestamp
        ) AS seconds_since_prev_tx,
        
        -- Flag duplicates: same amount and same merchant within 5 minutes (300s)
        CASE 
            WHEN LAG(t.transaction_amount) OVER (PARTITION BY t.cardholder_id, t.merchant_name ORDER BY t.transaction_timestamp) = t.transaction_amount
            AND DATEDIFF(
                second, 
                LAG(t.transaction_timestamp) OVER (PARTITION BY t.cardholder_id, t.merchant_name ORDER BY t.transaction_timestamp), 
                t.transaction_timestamp
            ) <= 300
            THEN 1
            ELSE 0
        END AS is_duplicate_5min
    FROM transactions t
),

-- 2. Join cardholder limits and check constraints
transaction_risk_evaluated AS (
    SELECT
        t.*,
        c.cardholder_name,
        c.credit_risk_score,
        c.kyc_status,
        c.daily_spending_limit,
        
        -- Flag individual transaction exceeding the limit
        CASE 
            WHEN t.transaction_amount > c.daily_spending_limit THEN 1 
            ELSE 0 
        END AS is_amount_over_limit,
        
        -- Flag velocity: transaction happens less than 60s after the prior transaction
        CASE 
            WHEN t.seconds_since_prev_tx IS NOT NULL AND t.seconds_since_prev_tx <= 60 THEN 1 
            ELSE 0 
        END AS is_velocity_warning
    FROM transactions_lagged t
    LEFT JOIN cardholders c ON t.cardholder_id = c.cardholder_id
),

-- 3. Connect chargeback dispute flags
final_risk_mart AS (
    SELECT
        t.*,
        CASE WHEN cb.transaction_id IS NOT NULL THEN 1 ELSE 0 END AS is_disputed,
        cb.dispute_timestamp,
        cb.dispute_category,
        
        -- Combined risk score calculation (simple heuristics for classification)
        (t.is_duplicate_5min * 3) + 
        (t.is_velocity_warning * 2) + 
        (t.is_amount_over_limit * 4) +
        (CASE WHEN t.kyc_status != 'APPROVED' THEN 3 ELSE 0 END) +
        (CASE WHEN t.credit_risk_score < 400 THEN 2 ELSE 0 END) AS transaction_risk_score
    FROM transaction_risk_evaluated t
    LEFT JOIN chargebacks cb ON t.transaction_id = cb.transaction_id
)

SELECT * FROM final_risk_mart
