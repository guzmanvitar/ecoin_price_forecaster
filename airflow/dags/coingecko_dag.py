"""Impelements airflow dag for scraping scheduling.

Uses DockerOperator to spin up our python poetry images and execute scraping tasks.

Note: Requires permission configuration to allow airflow user (501:0) to access the docker socket.
"""

from datetime import date, datetime, timedelta

from airflow.operators.docker_operator import DockerOperator
from airflow.operators.dummy_operator import DummyOperator

from airflow import DAG

default_args = {
    "email": ["guzmanvitar@muttdata.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="coingecko_scraping",
    description="DAG for recurrent coingecko scraping",
    default_args=default_args,
    schedule=timedelta(days=1),
    start_date=datetime(2022, 12, 23, 3),  # TODO: fix timezone
    catchup=False,
    tags=["scrapers"],
) as dag:
    start = DummyOperator(task_id="start_dag")

    current_date = date.today().strftime("%d-%m-%Y")

    bitcoin_scraping = DockerOperator(
        task_id="bitcoin_scraping",
        image="exam-guzman-vitar_python_poetry",
        auto_remove=True,
        command=f"python src/crawler/crawl.py --coin_id bitcoin --start_date '{current_date}'",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
    )

    ethereum_scraping = DockerOperator(
        task_id="ethereum_scraping",
        image="exam-guzman-vitar_python_poetry",
        auto_remove=True,
        command=f"python src/crawler/crawl.py --coin_id ethereum --start_date '{current_date}'",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
    )

    cardano_scraping = DockerOperator(
        task_id="cardano_scraping",
        image="exam-guzman-vitar_python_poetry",
        auto_remove=True,
        command=f"python src/crawler/crawl.py --coin_id cardano --start_date '{current_date}'",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
    )

    close = DummyOperator(task_id="close_dag")

    # Set dependencies between tasks
    start >> [bitcoin_scraping, ethereum_scraping, cardano_scraping]
    [bitcoin_scraping, ethereum_scraping, cardano_scraping] >> close
