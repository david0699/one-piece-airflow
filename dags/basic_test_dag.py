from airflow.sdk import Variable
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.hooks.http import HttpHook
from datetime import datetime

import logging

def get_data():
    hook = HttpHook(method='GET', http_conn_id='onepiece_api')
    response = hook.run(endpoint='/v2/characters/en')
    logging.info(f"API Response Status: {response.status_code}")
    logging.info(f"API Response Content: {response.text}")
    logging.info(f"API Response Type: {type(response.json())}")

with DAG(
    dag_id="basic_test_dag",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    is_paused_upon_creation=False,
) as dag:

    http_sensor = HttpSensor(
        task_id="check_api",
        http_conn_id="onepiece_api",
        endpoint="/v2/characters/en",
        poke_interval=10,
        timeout=30,
        response_check=lambda response: response.status_code == 200,
        mode="poke",
    )

    hello_from_python = PythonOperator(
        task_id="get_api_data",
        python_callable=get_data
    )

    hello_from_bash = BashOperator(
        task_id="say_hello_bash",
        bash_command='echo "Hello from Airflow Bash Operator"'
    )

    http_sensor >> hello_from_python >> hello_from_bash