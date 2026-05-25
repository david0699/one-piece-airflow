# One Piece Airflow

Local Apache Airflow project for ingesting data from the One Piece API into mounted raw storage, with a separate Spark/Hive analytics container for downstream experimentation.

## Overview

The current ingestion flow is:

1. Airflow loads DAGs from `dags/`.
2. `onepiece_api_ingest_dag` reads API and ingestion settings from Airflow Variables.
3. The DAG reads the `onepiece_api` Airflow connection to build the API base URL.
4. One task is generated per configured endpoint.
5. Each task fetches API data through `packages/api_utils`.
6. API responses are simplified to `list[dict]`.
7. Raw output is written under `/data/raw/{endpoint}/ingestion_date={ds}/data.jsonl`.

Host-side data lands under `data/raw/...` through the Docker volume mount.

## Repository Layout

- `dags/`: Airflow DAG definitions.
- `packages/api_utils/`: local Python package used by DAG tasks.
- `config/variables.yaml`: Airflow Variables imported during `airflow-init`.
- `config/airflow.cfg`: local Airflow configuration.
- `data/`: mounted runtime data output.
- `spark-jars/`: host-side JAR directory mounted into the Spark container at `/opt/spark-jars`.
- `agents/`: project context docs for architecture, decisions, and task tracking.
- `tests/`: Python tests for helper modules.
- `docker-compose.yaml`: local Airflow, Postgres, Redis, and Spark/Hive stack.
- `Dockerfile`: custom Airflow image.
- `Dockerfile.analytics`: Spark/Hive analytics image.

## Stack

- Apache Airflow `3.1.5`
- Python `3.10`
- CeleryExecutor
- PostgreSQL `16`
- Redis `7.2-bookworm`
- Spark `3.5.1`
- Hive `3.1.3`
- Java `11`

## Configuration

Airflow Variables are defined in `config/variables.yaml` and imported by the `airflow-init` service.

Current variable groups:

- `API`: connection ID, language, and endpoint mapping.
- `INGESTION`: timeout and retry settings.

The ingestion DAG expects an Airflow connection named `onepiece_api`. The DAG builds the base URL from that connection using:

```python
f"{API_CONN.schema}://{API_CONN.host}/v2"
```

For the current endpoint paths, configure the connection so the generated URLs match the API host, for example `https://api.api-onepiece.com/v2/...`.

## Local Setup

Create a local `.env` file if needed. For macOS or Linux, a minimal local value is usually:

```bash
AIRFLOW_UID=50000
```

Build the images:

```bash
docker compose build
```

Initialize Airflow metadata and import variables:

```bash
docker compose up airflow-init
```

Start the local stack:

```bash
docker compose up
```

Open Airflow at:

```text
http://localhost:8080
```

Default local credentials come from `docker-compose.yaml` unless overridden:

```text
airflow / airflow
```

Stop the stack:

```bash
docker compose down
```

## DAGs

### `onepiece_api_ingest_dag`

Production-oriented ingestion DAG using TaskFlow API.

- Schedule: manual (`schedule=None`).
- Catchup: disabled.
- Source config: `API` and `INGESTION` Airflow Variables.
- Connection: `onepiece_api`.
- Output: `/data/raw/{endpoint}/ingestion_date={ds}/data.jsonl`.

Configured endpoints currently include characters, fruits, sagas, chapters, tomes, episodes, dials, movies, swords, hakis, crews, boats, arcs, locations, and Luffy-specific endpoints.

### `basic_test_dag`

Manual test DAG for validating the API connection through an HTTP sensor and a simple Python task.

## Python Package

The local package is defined under `packages/api_utils` and exposed through `pyproject.toml`.

Airflow containers set:

```text
PYTHONPATH=/opt/airflow/packages
```

Primary helpers:

- `get_json`: performs HTTP GET and raises for non-success responses.
- `simplify_raw_data`: extracts `list[dict]` from supported API response formats.
- `fetch_data_from_api`: fetches, simplifies, and logs response structure.
- `write_data_to_jsonl`: writes records to the target output path.

## Data Layout

Raw ingestion output:

```text
data/raw/{endpoint}/ingestion_date={YYYY-MM-DD}/data.jsonl
```

Current intended lakehouse direction:

- Bronze: raw API extracts in `data/raw`.
- Silver: validated, cleaned, normalized Delta tables.
- Gold: curated business-ready outputs or aggregates.

## Spark And Hive

The `analytics` service is a separate Spark/Hive container for local analytics and future transformation work.

It mounts:

- `data/` to `/data`
- `spark-jars/` to `/opt/spark-jars`

Use `spark-jars/` for connector, storage, driver, or table-format JARs. Keep explicit versioned filenames so Spark runs are reproducible when testing different dependency versions.

Example shell access:

```bash
docker compose exec analytics bash
```

Example JAR reference inside the container:

```text
/opt/spark-jars/delta-spark_2.12-3.2.0.jar
```

## Tests

Run local tests with:

```bash
PYTHONPATH=packages pytest
```

If the package is installed in editable mode, plain `pytest` should also work.

## Project Context Docs

Read these before significant changes:

- `AGENTS.md`: agent working instructions.
- `agents/ARCHITECTURE.md`: architecture map and boundaries.
- `agents/DECISIONS.md`: accepted decisions and workflow constraints.
- `agents/TASKS.md`: current task tracker.

Important workflow decisions:

- Do not push to a remote repository without explicit owner approval.
- Do not run `git rebase` without explicit owner approval.
- Significant changes should reference relevant decision IDs from `agents/DECISIONS.md`.

## Current Roadmap

Current tracked tasks include:

- Build a DAG for technical validations and Silver-layer cleaning.
- Build DAG/processes to create Hive external tables.
- Add a daily Bronze-to-Silver Delta table pipeline for curated data exploitation.

