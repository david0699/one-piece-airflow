# ARCHITECTURE

## Purpose

This repository runs a local Airflow ingestion stack for extracting One Piece API data and writing raw JSONL files to mounted storage. It also includes a Spark/Hive analytics container for downstream experimentation and transformation work.

## System Overview

Primary flow:

1. Airflow loads DAGs from `dags/`.
2. DAGs read runtime configuration from Airflow Variables and Connections.
3. `onepiece_api_ingest_dag` builds endpoint URLs from the `API` variable and the `onepiece_api` connection.
4. TaskFlow tasks call helpers from `packages/api_utils`.
5. API responses are normalized to `list[dict]`.
6. Raw records are written under `/data/raw/{endpoint}/ingestion_date={ds}/data.jsonl`.
7. The local `data/` directory receives those files through the Docker volume mount.

## Runtime Containers

- `airflow-apiserver`: exposes the Airflow UI/API on port `8080`.
- `airflow-scheduler`: schedules DAG runs.
- `airflow-dag-processor`: parses DAG files.
- `airflow-worker`: executes Celery tasks.
- `airflow-triggerer`: runs deferrable triggers.
- `airflow-init`: initializes the metadata DB and imports `config/variables.yaml`.
- `postgres`: Airflow metadata database.
- `redis`: Celery broker.
- `analytics`: Spark/Hive utility container for local analytics work.

## Code Layout

- `dags/`: DAG definitions and orchestration logic.
- `packages/api_utils/`: reusable API client, parser, fetch, and writer helpers.
- `config/`: Airflow config and variables.
- `data/`: local mounted data directory.
- `spark-jars/`: host-side JAR repository mounted into `analytics` as `/opt/spark-jars`.
- `tests/`: Python tests for local helpers.

## Dependency Boundaries

- DAGs should orchestrate work and keep business logic thin.
- API fetching, parsing, and writing logic belongs in `packages/api_utils`.
- Runtime configuration belongs in Airflow Variables and Connections.
- Generated data belongs in `data/`, not in source code.
- Spark-specific dependency JARs belong in `spark-jars/`, with explicit versioned filenames.

## Data Contracts

Raw ingestion output:

- Format: JSONL.
- Location in containers: `/data/raw/{endpoint}/ingestion_date={ds}/data.jsonl`.
- Location on host: `data/raw/{endpoint}/ingestion_date={ds}/data.jsonl`.
- Partition key: `ingestion_date`.
- Expected record shape: one JSON object per line after API response simplification.

## Airflow Configuration

- `config/variables.yaml` defines the `API` and `INGESTION` variables.
- The `API.CONN_ID` value points to the Airflow connection used to build the base API URL.
- `docker-compose.yaml` sets `PYTHONPATH=/opt/airflow/packages`, allowing DAGs to import `api_utils`.
- The custom Airflow image installs provider packages in `Dockerfile`.

## Spark Analytics Context

The `analytics` container is separate from Airflow execution. Use it for local Spark and Hive experiments, validations, and future transformations.

JAR handling:

- Put connector, storage, table-format, and driver JARs in `spark-jars/`.
- Use versioned filenames such as `delta-spark_2.12-3.2.0.jar`.
- Reference them inside the container from `/opt/spark-jars`.
- Avoid replacing generic filenames during tests because that hides which dependency version was used.

## Change Guidance

- For DAG changes, inspect `dags/`, `config/variables.yaml`, and the relevant helper modules.
- For ingestion behavior, modify `packages/api_utils` first and keep DAG code focused on orchestration.
- For Docker runtime behavior, inspect `docker-compose.yaml`, `Dockerfile`, and `Dockerfile.analytics`.
- For Spark work, inspect `spark-jars/`, `Dockerfile.analytics`, and any future Spark job directories before changing dependencies.
- For tests, prefer focused unit tests around helper behavior and import checks for DAG safety.
