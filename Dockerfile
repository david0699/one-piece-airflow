FROM apache/airflow:3.1.5-python3.10

USER airflow

RUN pip install --no-cache-dir \
    apache-airflow-providers-postgres \
    apache-airflow-providers-apache-spark \
    apache-airflow-providers-apache-hive \
    apache-airflow-providers-fab