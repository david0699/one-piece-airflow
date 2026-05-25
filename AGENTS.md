# AGENTS.md

## Project Context

This is a local Apache Airflow project for ingesting One Piece API data into mounted JSONL files.

Important project context is stored in:
- `agents/ARCHITECTURE.md`
- ~~`agents/conventions.md`~~
- ~~`agents/runbook.md`~~
- `agents/DECISIONS.md`
- `agents/TASKS.md`

Read these files before making significant changes.

Main components:
- `dags/`: Airflow DAG definitions.
- `packages/api_utils/`: local Python package used by DAG tasks.
- `config/variables.yaml`: Airflow Variables imported by `airflow-init`.
- `data/`: mounted runtime data output, with raw ingested files under `/data/raw`.
- `spark-jars/`: local JAR repository mounted into the Spark analytics container at `/opt/spark-jars`.
- `docker-compose.yaml`: local Airflow 3.1.5 stack using CeleryExecutor, Postgres, Redis, and an `analytics` container.
- `Dockerfile`: custom Airflow image with Postgres, Spark, Hive, and FAB providers.
- `Dockerfile.analytics`: Spark/Hive utility image.

## Working Style

- Be concise and direct.
- Prefer minimal diffs and readable code.
- Preserve the existing project layout unless there is a clear reason to change it.
- As the project grows, occasionally propose updates to files under `agents/` based on recurring coding practices, workflow patterns, architecture changes, or other stable conventions detected in the repository.
- Do not make destructive changes without asking first.
- Do not revert user changes unless explicitly requested.
- Use `rg` / `rg --files` for repository searches.
- Prefer production-ready code with explicit error handling.

## Python and Package Layout

- Python source lives under `packages/`.
- The package is configured in `pyproject.toml` with `package-dir = {"" = "packages"}`.
- Airflow containers set `PYTHONPATH=/opt/airflow/packages`.
- Import local helpers from `api_utils`, for example:
  - `from api_utils import fetch_data_from_api, write_data_to_jsonl`
- Keep helpers small, typed where useful, and easy to test outside Airflow.
- Avoid broad exception swallowing. If catching exceptions, log useful context and re-raise unless recovery is intentional.

## Airflow Conventions

- DAG files live in `dags/`.
- Prefer TaskFlow API (`@dag`, `@task`) for new production DAGs, matching `onepiece_api_ingest_dag.py`.
- Keep DAG parse-time work lightweight. Avoid network calls, file writes, large imports, or expensive computation at import time.
- Read runtime configuration from Airflow Variables and Connections instead of hardcoding endpoints or credentials.
- Keep task outputs small. Do not push large API payloads through XCom.
- Use templated Airflow context values explicitly when writing partitioned data paths, e.g. `ingestion_date={{ ds }}`.
- For sensors, prefer `reschedule` mode for long waits; `poke` is acceptable only for short local checks.
- Make DAG/task IDs stable and descriptive.

## Data and IO

- Runtime data is mounted to `/data` in containers and `data/` locally.
- Raw API output currently writes to `/data/raw/{endpoint}/ingestion_date={ds}/data.jsonl`.
- Preserve partitioned directory structure unless changing downstream consumers too.
- JSONL should be one valid JSON object per physical line. Avoid pretty-printing JSONL records.
- Do not commit generated data, logs, caches, or local environment files.

## Docker and Local Airflow

- Use Docker Compose for the local Airflow stack.
- Common commands:
  - `docker compose build`
  - `docker compose up airflow-init`
  - `docker compose up`
  - `docker compose down`
- Airflow UI is exposed on port `8080`.
- `config/variables.yaml` is imported during `airflow-init`.
- The local stack is for development only; do not treat Compose defaults as production settings.

## Testing and Validation

- Prefer targeted tests for changed helpers in `packages/api_utils/`.
- Run tests with:
  - `pytest`
- If imports fail locally, install the package in editable mode or set `PYTHONPATH=packages`.
- For DAG changes, validate that DAG files import cleanly in the Airflow container when practical.
- For Docker or provider changes, rebuild the relevant image before declaring the change verified.

## Spark and Analytics Notes

- The `analytics` service provides Spark 3.5.1 and Hive 3.1.3 for local experimentation.
- `spark-jars/` contains JAR files for the Spark container. Keep versioned JARs here when testing different connector, driver, or dependency versions.
- The directory is mounted into the `analytics` container as `/opt/spark-jars`; reference JARs from that container path in `spark-submit`, Spark configs, or shell sessions.
- Prefer explicit JAR filenames with versions instead of overwriting generic names, so version-specific runs are reproducible.
- When adding Spark jobs:
  - Avoid `collect()` on non-trivial datasets.
  - Pay attention to shuffles and partition counts.
  - Use broadcast joins for genuinely small dimension data.
  - Explain performance implications for joins, repartitions, and writes.
  - Prefer immutable, functional transformations over mutation-heavy code.

## Known Repository Details

- `config/airflow.cfg` is a large generated Airflow config; avoid unrelated churn there.
- `logs/`, `.pytest_cache/`, `venv/`, and `.DS_Store` are local artifacts.
- There is currently a test import path that may need attention: tests should import from the exposed `api_utils` package, not a non-existent `api_utils.api_utils` module.
