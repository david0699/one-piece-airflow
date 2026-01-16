from airflow.sdk import Variable, dag, task
from airflow.hooks.base import BaseHook
from datetime import datetime
from pathlib import Path
from api_utils import fetch_data_from_api, write_data_to_jsonl

import logging

@dag(
    dag_id="onepiece_api_ingest_dag",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
)
def run_dag():

    API_CONFIG = Variable.get("API", deserialize_json=True)
    INGESTION_CONFIG = Variable.get("INGESTION", deserialize_json=True)
    API_CONN = BaseHook.get_connection(API_CONFIG["CONN_ID"])

    API_URL = f"{API_CONN.schema}://{API_CONN.host}/v2"
    API_ENDPOINTS_DICT = API_CONFIG["ENDPOINTS"]                                 
    API_LANG = API_CONFIG["LANGUAGE"]

    INGESTION_TIMEOUT = INGESTION_CONFIG["TIMEOUT_SECONDS"]
    INGESTION_RETRIES = INGESTION_CONFIG["RETRIES"]

    ENDPOINTS = tuple(API_ENDPOINTS_DICT.keys())

    @task()
    def fetch_and_log_data(endpoint: str, ds: str) -> None:
        api_endpoint = f"{API_URL}/{API_ENDPOINTS_DICT[endpoint]}/{API_LANG}"
        target_path = Path(f"/data/raw/{endpoint}/ingestion_date={ds}/data.jsonl")
        
        logging.info(
            "Starting ingestion for endpoint=%s",
            endpoint,
        )

        data = fetch_data_from_api(api_endpoint, timeout=INGESTION_TIMEOUT)

        record_count = len(data)
        #if record_count == 0:
        #    raise ValueError(f"No records fetched for endpoint={endpoint}. Failing task.")
        
        logging.info(
            "Fetched %d records for endpoint=%s",
            record_count,
            endpoint,
        )

        write_data_to_jsonl(data, target_path)

        logging.info(
            "Successfully wrote %d records to %s",
            record_count,
            target_path,
        )


    list(
        fetch_and_log_data
            .override(task_id=f"fetch_{endpoint}_data")
            (endpoint=endpoint, ds="{{ ds }}")
        for endpoint in ENDPOINTS
    )

dag = run_dag()