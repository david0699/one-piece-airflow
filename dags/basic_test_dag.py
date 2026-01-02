from airflow import DAG
from airflow.operators.python import PythonOperator
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

    hello = PythonOperator(
        task_id="say_hello",
        python_callable=say_hello
    )