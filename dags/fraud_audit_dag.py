import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Import our mock data generator function
# In a real Airflow deployment, code in the project path is accessible
try:
    from generate_mock_data import generate_data
except ImportError:
    # Fallback simulation function if imported outside project directory
    def generate_data(output_dir="data"):
        print("Running fallback mock data generator...")
        pass

# Define default arguments for the DAG
default_args = {
    'owner': 'mohak_kedia',
    'depends_on_past': False,
    'start_date': datetime(2026, 6, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def load_data_to_snowflake():
    """
    Simulation Python task representing the database ingestion task.
    In production, this would use SnowflakeOperator or copy commands via SnowflakeHook.
    """
    print("Initiating connection to Snowflake FINTECH_RAW database...")
    print("Executing COPY INTO PAYMENT_DATA.CARDHOLDER_PROFILES FROM stage...")
    print("Executing COPY INTO PAYMENT_DATA.TRANSACTIONS FROM stage...")
    print("Executing COPY INTO PAYMENT_DATA.CHARGEBACKS FROM stage...")
    print("Raw ingestion complete. 100K+ transaction logs committed.")

with DAG(
    'fintech_fraud_risk_audit_pipeline',
    default_args=default_args,
    description='ELT and MLOps Pipeline for Credit Transaction Risk Audits',
    schedule_interval=timedelta(days=1),
    catchup=False
) as dag:

    # Task 1: Generate Mock Transactions locally
    task_generate_mock_data = PythonOperator(
        task_id='generate_mock_data',
        python_callable=generate_data,
        op_kwargs={'output_dir': '/tmp/landing_zone/fintech_data'},
    )

    # Task 2: load CSV files into Snowflake raw staging
    task_load_to_snowflake = PythonOperator(
        task_id='load_raw_to_snowflake',
        python_callable=load_data_to_snowflake,
    )

    # Task 3: Execute dbt transformation models
    task_dbt_run = BashOperator(
        task_id='dbt_run_transformations',
        bash_command='dbt run --profiles-dir . --project-dir .',
    )

    # Task 4: Execute dbt quality tests
    task_dbt_test = BashOperator(
        task_id='dbt_test_assertions',
        bash_command='dbt test --profiles-dir . --project-dir .',
    )

    # Task 5: Trigger Dataiku MLOps scenario to update risk models
    task_dataiku_scenario = BashOperator(
        task_id='trigger_dataiku_scenario',
        bash_command='python scripts/dataiku_risk_scoring.py',
    )

    # Define task execution dependencies
    task_generate_mock_data >> task_load_to_snowflake >> task_dbt_run >> task_dbt_test >> task_dataiku_scenario
