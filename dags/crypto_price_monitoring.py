from math import e
from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor  # type: ignore
from airflow.providers.http.operators.http import SimpleHttpOperator  # type: ignore
from airflow.providers.postgres.hooks.postgres import PostgresHook  # type: ignore
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.models import Variable
from datetime import datetime, timedelta, timezone
import json
from typing import List, Tuple
import logging

from numpy import tri

# Configuração de logging
logger = logging.getLogger(__name__)

api_key = Variable.get("CMC_API_KEY")


def process_crypto_data(response_text: str) -> List[Tuple]:
    """Processa os dados da API e retorna formatado para bulk insert"""
    try:
        data = json.loads(response_text)
        if "data" not in data or not isinstance(data["data"], list):
            raise ValueError("Dados inválidos")

        current_timestamp = datetime.now(timezone.utc).isoformat()

        return [
            (
                crypto["name"],
                crypto["symbol"],
                crypto["quote"]["USD"]["price"],
                current_timestamp,
                current_timestamp,
                crypto["quote"]["USD"]["market_cap"],
                crypto["quote"]["USD"]["volume_24h"],
                crypto["last_updated"],
            )
            for crypto in data.get("data", [])
        ]
    except Exception as e:
        logger.error(f"Erro ao processar dados: {str(e)}")
        raise


def insert_crypto_data(**context) -> None:
    """Faz insert em lote usando PostgresHook"""
    conn = None  # Inicializa a variável

    try:
        ti = context["ti"]
        response_text = ti.xcom_pull(task_ids="fetch_crypto_prices")

        if not response_text:
            raise ValueError("Dados da API não recebidos")

        records = process_crypto_data(response_text)

        pg_hook = PostgresHook(postgres_conn_id="crypto_postgres")
        conn = pg_hook.get_conn()

        with conn.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO crypto_prices (name, symbol, price, timestamp, created_at, market_cap, volume_24h, last_updated)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (name, symbol) 
                DO UPDATE SET price = EXCLUDED.price,
                            timestamp = EXCLUDED.timestamp, 
                            market_cap = EXCLUDED.market_cap, 
                            volume_24h = EXCLUDED.volume_24h, 
                            last_updated = EXCLUDED.last_updated;
                """,
                records,
            )
        conn.commit()

        logger.info(f"Inserted {len(records)} records")

    except Exception as e:
        logger.error(f"Erro no insert: {str(e)}")
        raise

    finally:
        if conn:
            conn.close()


default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=10),
}

with DAG(
    "optimized_crypto_monitoring",
    default_args=default_args,
    description="Monitoramento otimizado de preços de criptomoedas",
    schedule_interval="@hourly",
    start_date=datetime(2025, 3, 24, tzinfo=timezone.utc),
    catchup=False,
    max_active_tasks=3,
    tags=["crypto", "optimized"],
) as dag:

    check_api = HttpSensor(
        task_id="check_api_availability",
        http_conn_id="coinmarketcap_api",
        endpoint="v1/cryptocurrency/listings/latest",
        headers={"X-CMC_PRO_API_KEY": api_key},
        method="GET",
        response_check=lambda response: response.status_code == 200,
        poke_interval=30,
        timeout=300,
        mode="poke",
    )

    fetch_prices = SimpleHttpOperator(
        task_id="fetch_crypto_prices",
        http_conn_id="coinmarketcap_api",
        endpoint="v1/cryptocurrency/listings/latest",
        method="GET",
        headers={
            "X-CMC_PRO_API_KEY": api_key,
            "Accept": "application/json",
        },
        response_filter=lambda response: (
            response.text if response.status_code == 200 else None
        ),
        response_check=lambda response: response.status_code == 200,
        do_xcom_push=True,
    )

    store_prices = PythonOperator(
        task_id="store_crypto_data",
        python_callable=insert_crypto_data,
    )

    run_dbt_models = BashOperator(
        task_id="run_dbt_models",
        bash_command="/home/airflow/.local/bin/dbt run --profiles-dir /opt/airflow/dbt/profiles --project-dir /opt/airflow/dbt",
        env={"DBT_PROFILES_DIR": "/opt/airflow/dbt/profiles"},
    )

    run_dbt_tests = BashOperator(
        task_id="run_dbt_tests",
        bash_command="/home/airflow/.local/bin/dbt test --profiles-dir /opt/airflow/dbt/profiles --project-dir /opt/airflow/dbt",
        trigger_rule="all_success",
    )

    generate_dbt_docs = BashOperator(
        task_id="generate_dbt_docs",
        bash_command="/home/airflow/.local/bin/dbt docs generate --profiles-dir /opt/airflow/dbt/profiles --project-dir /opt/airflow/dbt",
        trigger_rule="all_success",
    )

    check_api >> fetch_prices >> store_prices >> run_dbt_models

    run_dbt_models >> run_dbt_tests
    run_dbt_models >> generate_dbt_docs
