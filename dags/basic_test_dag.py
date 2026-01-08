from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime

import logging

def say_hello():
    logging.info("Hello from Airflow 3")

with DAG(
    dag_id="basic_test_dag",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    is_paused_upon_creation=False,
) as dag:

    hello_from_python = PythonOperator(
        task_id="say_hello",
        python_callable=say_hello
    )

    hello_from_bash = BashOperator(
        task_id="say_hello_bash",
        bash_command='echo "Hello from Airflow Bash Operator"'
    )

    hello_from_python >> hello_from_bash