from __future__ import annotations

from datetime import datetime
import json
from shlex import split as shlex_split
import subprocess

from airflow.sdk import Variable, dag, task
from airflow.providers.standard.operators.empty import EmptyOperator


def _encode_cli_args(values: dict[str, str]) -> str:
    return ";".join(f"{key}:{value}" for key, value in values.items() if value != "")


def _run_process(
    spark_submit_command: str,
    main_class: str,
    jar_path: str,
    process_name: str,
    payload: str,
    capture_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    cmd = [
        *shlex_split(spark_submit_command),
        "--class",
        main_class,
        jar_path,
        process_name,
        payload,
    ]
    return subprocess.run(
        cmd,
        check=True,
        text=True,
        capture_output=capture_output,
    )


@dag(
    dag_id="onepiece_bronze_hive_bootstrap_dag",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
)
def bronze_hive_bootstrap() -> None:
    @task()
    def check_tables() -> dict[str, list[str]]:
        api_config = Variable.get("API", deserialize_json=True)
        bronze_hive_config = Variable.get("BRONZE_HIVE", deserialize_json=True)
        configured_tables = list(api_config["ENDPOINTS"].keys())

        payload = _encode_cli_args(
            {
                "database": bronze_hive_config["DATABASE"],
                "tables": ",".join(configured_tables),
                "extraArgs": bronze_hive_config.get("EXTRA_ARGS", ""),
            }
        )
        result = _run_process(
            spark_submit_command=bronze_hive_config["SPARK_SUBMIT_COMMAND"],
            main_class=bronze_hive_config["MAIN_CLASS"],
            jar_path=bronze_hive_config["JAR_PATH"],
            process_name=bronze_hive_config["CHECK_TABLES_PROCESS"],
            payload=payload,
            capture_output=True,
        )

        output = (result.stdout or "").strip()
        parsed = json.loads(output) if output else {}
        existing_tables = [
            table for table in parsed.get("existing_tables", []) if table in configured_tables
        ]
        missing_tables = [table for table in configured_tables if table not in existing_tables]
        return {"existing_tables": existing_tables, "missing_tables": missing_tables}

    @task.branch()
    def choose_bootstrap_path(table_state: dict[str, list[str]]) -> str:
        return "run_bootstrap" if table_state["missing_tables"] else "skip_bootstrap"

    @task(task_id="run_bootstrap")
    def run_bootstrap() -> list[str]:
        from airflow.sdk import get_current_context

        context = get_current_context()
        task_instance = context["ti"]
        table_state = task_instance.xcom_pull(task_ids="check_tables")
        missing_tables = table_state["missing_tables"] if table_state else []
        if not missing_tables:
            return []

        bronze_hive_config = Variable.get("BRONZE_HIVE", deserialize_json=True)
        payload = _encode_cli_args(
            {
                "database": bronze_hive_config["DATABASE"],
                "tables": ",".join(missing_tables),
                "extraArgs": bronze_hive_config.get("EXTRA_ARGS", ""),
            }
        )
        _run_process(
            spark_submit_command=bronze_hive_config["SPARK_SUBMIT_COMMAND"],
            main_class=bronze_hive_config["MAIN_CLASS"],
            jar_path=bronze_hive_config["JAR_PATH"],
            process_name=bronze_hive_config["BOOTSTRAP_PROCESS"],
            payload=payload,
        )
        return missing_tables

    @task()
    def msck_repair_tables(new_tables: list[str]) -> None:
        if not new_tables:
            return

        bronze_hive_config = Variable.get("BRONZE_HIVE", deserialize_json=True)
        payload = _encode_cli_args(
            {
                "database": bronze_hive_config["DATABASE"],
                "tables": ",".join(new_tables),
                "extraArgs": bronze_hive_config.get("EXTRA_ARGS", ""),
            }
        )
        _run_process(
            spark_submit_command=bronze_hive_config["SPARK_SUBMIT_COMMAND"],
            main_class=bronze_hive_config["MAIN_CLASS"],
            jar_path=bronze_hive_config["JAR_PATH"],
            process_name=bronze_hive_config["MSCK_REPAIR_PROCESS"],
            payload=payload,
        )

    table_state = check_tables()
    bootstrap_path = choose_bootstrap_path(table_state)
    skip_bootstrap = EmptyOperator(task_id="skip_bootstrap")
    bootstrap_tables = run_bootstrap()
    repair_tables = msck_repair_tables(bootstrap_tables)

    table_state >> bootstrap_path >> [bootstrap_tables, skip_bootstrap]
    bootstrap_tables >> repair_tables


dag = bronze_hive_bootstrap()
