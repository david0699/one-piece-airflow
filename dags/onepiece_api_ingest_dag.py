from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import Variable, chain
from airflow.decorators import dag, task
from datetime import datetime
from api_utils import fetch_data_from_api

import logging

API_CONFIG = Variable.get("API", deserialize_json=True)
INGESTION_CONFIG = Variable.get("INGESTION", deserialize_json=True)

API_URL = API_CONFIG["URL"]
API_ENDPOINTS_DICT = API_CONFIG["ENDPOINTS"]                                 
API_LANG = API_CONFIG["LANGUAGE"]

INGESTION_TIMEOUT = INGESTION_CONFIG["TIMEOUT_SECONDS"]
INGESTION_RETRIES = INGESTION_CONFIG["RETRIES"]

ENDPOINTS = tuple(API_ENDPOINTS_DICT.keys())

@dag(
    dag_id="onepiece_api_ingest_dag",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
)
def run_dag():

    @task()
    def fetch_and_log_data(**kwargs):
        endpoint = kwargs["endpoint"]
        api_endpoint = f"{API_URL}/{API_ENDPOINTS_DICT[endpoint]}/{API_LANG}"
        data = fetch_data_from_api(api_endpoint)
        logging.info(f"Fetched data for endpoint {endpoint}: {data}")

    list(
        fetch_and_log_data
            .override(task_id=f"fetch_{endpoint}_data")
            (endpoint=endpoint)
        for endpoint in ENDPOINTS
    )

dag = run_dag()