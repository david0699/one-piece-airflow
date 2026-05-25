from __future__ import annotations

from datetime import datetime
from shlex import split as shlex_split
import subprocess

from airflow.sdk import Variable, dag, task


def _encode_cli_args(values: dict[str, str]) -> str:
    return ";".join(f"{key}:{value}" for key, value in values.items() if value != "")


@dag(
    dag_id="onepiece_bronze_hive_bootstrap_dag",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
)
def bronze_hive_bootstrap() -> None:
    @task()
    def run_bootstrap() -> None:
        api_config = Variable.get("API", deserialize_json=True)
        bronze_hive_config = Variable.get("BRONZE_HIVE", deserialize_json=True)

        endpoints = ",".join(api_config["ENDPOINTS"].keys())
        payload = _encode_cli_args(
            {
                "mode": bronze_hive_config["BOOTSTRAP_MODE"],
                "database": bronze_hive_config["DATABASE"],
                "endpoints": endpoints,
                "extraArgs": bronze_hive_config.get("EXTRA_ARGS", ""),
            }
        )

        cmd = [
            *shlex_split(bronze_hive_config["SPARK_SUBMIT_COMMAND"]),
            "--class",
            bronze_hive_config["MAIN_CLASS"],
            bronze_hive_config["JAR_PATH"],
            payload,
        ]

        subprocess.run(cmd, check=True)

    run_bootstrap()


dag = bronze_hive_bootstrap()
