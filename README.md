# FinTech Transaction Fraud & Risk Audit Pipeline

An end-to-end data engineering and analytics pipeline built to audit credit card transactions, compute risk metrics, and trigger automated predictive modeling runs.

## Architecture Overview
The pipeline follows a modern DataOps structure utilizing a Medallion Architecture:

```
+------------------------+
| Mock Data Generator    | (Python local ingestion zone)
+------------------------+
            |
            v  (raw CSVs)
+------------------------+
|   Apache Airflow       | (Ingests data via Snowflake COPY INTO commands)
+------------------------+
            |
            v
+------------------------+
| Snowflake Database     | (FINTECH_RAW.PAYMENT_DATA tables)
+------------------------+
            |
            v
+------------------------+
|      dbt Core          | (Transforms & models data: Raw -> Staging -> Marts)
+------------------------+
            |
            v
+------------------------+
| Snowflake Analytics    | (FINTECH_ANALYTICS.MARTS.fct_transaction_risk)
+------------------------+
            |
            v
+------------------------+
|    Dataiku DSS         | (Programmatic API trigger to update classifier model)
+------------------------+
```

---

## Technical Stack & Competencies
*   **Database Warehouse:** Snowflake (Medallion architecture split into `RAW` and `ANALYTICS` databases).
*   **Transformation & Modeling:** dbt Core (staging, marts, custom SQL macros, and tests).
*   **Workflow Orchestration:** Apache Airflow (DAGs mapping ingestion, dbt compilation, testing, and training).
*   **MLOps & Analytics:** Dataiku DSS (API-driven model retraining and data science workflows).
*   **Scripting & ETL:** Python & SQL (modular functions and ANSI SQL analytics queries).

---

## Directory Structure
```
fintech_fraud_pipeline/
├── data/                       # Generated landing zone mock CSV files
├── dags/
│   └── fraud_audit_dag.py      # Apache Airflow orchestration workflow
├── models/
│   ├── staging/
│   │   ├── src_payment_data.yml # Snowflake raw source schema definition
│   │   ├── stg_cardholders.sql  # Cardholder metadata staging model
│   │   ├── stg_chargebacks.sql  # Chargeback/Disputes staging model
│   │   └── stg_transactions.sql # Transaction logs staging model
│   ├── marts/
│   │   └── fct_transaction_risk.sql # Mart fact table calculating risk metrics
│   └── schema.yml              # Automated data quality tests
├── scripts/
│   └── dataiku_risk_scoring.py # Dataiku DSS programmatic SDK script
├── dbt_project.yml             # dbt configuration metadata
├── generate_mock_data.py       # Python script generating transactional mock tables
├── profiles.yml                # local dbt-to-Snowflake profile credentials template
└── setup.sql                   # Snowflake warehouse, database, table, and RBAC config
```

---

## Pipeline Features (dbt Analytical Heuristics)
In [fct_transaction_risk.sql](models/marts/fct_transaction_risk.sql), we implement custom SQL analytic functions to calculate risk flags:
1.  **Velocity Check:** Flags cardholders executing multiple transactions within 60 seconds.
2.  **Duplicate Check:** Flags transactions with matching cardholders, merchant names, and amounts within a 5-minute window.
3.  **Spending Limit Breach:** Flags transactions that exceed the cardholder's approved daily spending limit.
4.  **Chargeback Ingestion:** Joins dispute codes (`FRAUDULENT`, `UNRECOGNIZED`, etc.) to target classifications.

---

## Getting Started

### 1. Database Setup (Snowflake)
Execute [setup.sql](setup.sql) in your Snowflake worksheet to create the loading warehouses, databases, schemas, tables, and roles.

### 2. Ingest Data
Generate the dataset locally:
```bash
python generate_mock_data.py
```
This writes raw transactions, profiles, and chargeback files to the `/data` folder.

### 3. Run dbt Transformations
Configure your credentials in `profiles.yml` and execute the transformations:
```bash
# Run models
dbt run --profiles-dir . --project-dir .

# Run testing assertions (Unique keys, Null checks)
dbt test --profiles-dir . --project-dir .
```

### 4. Trigger MLOps Retraining
Run the Dataiku MLOps scenario:
```bash
python scripts/dataiku_risk_scoring.py
```
This triggers DSS to fetch the freshly computed dbt risk metrics from Snowflake and retrain the classification model.
