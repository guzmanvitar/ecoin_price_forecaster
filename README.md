# Ecoin Price Forecaster

This project provides an end-to-end pipeline for forecasting the prices of ecoins, integrating data collection, preprocessing, model training, and deployment in a cloud environment.

## Project Overview

The primary goal of this project is to predict the prices of various ecoins using historical data and other relevant features. This pipeline includes data ingestion, storage, analysis, model training, and API deployment, providing an endpoint to visualize results.

## How It Works

1. **Data Collection and Preprocessing**:
   - A custom Python-based `scrapy` crawler extracts historical ecoin prices from the Coingecko API. The data is processed and stored in a PostgreSQL database for further analysis.

2. **Data Analysis and Exploration**:
   - SQL scripts are used to perform initial analysis and insights generation from the collected data.

3. **Model Development and Training**:
   - A forecasting pipeline is implemented, with a SARIMA model as the initial baseline. The pipeline includes functionality for data visualization, training, and maintenance.

4. **Scheduled Updates**:
   - Kubernetes cron jobs are set up to keep the data and models updated, ensuring continuous availability of accurate forecasts.

5. **API Deployment**:
   - A REST API provides access to the trained forecasting models. Users can query the API for price predictions based on specific coins and target dates.

## Repo Setup

### 1. Setting Up the Environment

#### Poetry

The project uses `poetry` for dependency management and `pyenv` for Python version control.

To set up the environment, ensure `pyenv` and `poetry` are installed, and then run:

```bash
pyenv install 3.10.9
pyenv shell 3.10.9
pyenv which python | xargs poetry env use
poetry config virtualenvs.in-project true
poetry install
```

Activate the environment with:

```bash
poetry shell
```

Set up Git hooks with:

```bash
pre-commit install
```

### 2. Docker & Kubernetes

This project uses Docker for containerization and Kubernetes for orchestration.

#### Setting Up Minikube

Install [Minikube](https://minikube.sigs.k8s.io/docs/start/) for local Kubernetes testing, then start a local cluster:

```bash
minikube start
```

#### Setting Up Secrets

Custom images in the Kubernetes YAML files are stored in a GCP Container Registry.

To run the code, you’ll need a gcp_service_account_creds.json file, which should be saved in the .secrets directory. Please contact me for this file.

To log in to Docker with the credentials, use:

```bash
cat .secrets/gcp_service_account_creds.json | docker login -u _json_key --password-stdin https://southamerica-east1-docker.pkg.dev
```

In Kubernetes, create secrets for Docker and the GCP service account with:
```bash
kubectl create secret docker-registry gcr-json-key \
--docker-server=southamerica-east1-docker.pkg.dev \
--docker-username=_json_key \
--docker-password="$(cat .secrets/gcp_service_account_creds.json)" \
--docker-email=any@valid.email
```


#### Testing the Environment

Verify the setup by running the Python environment container in Kubernetes:

```bash
kubectl apply -f kubernetes/python-env.yaml
```

Access Jupyter Lab to ensure proper container functionality:

```bash
minikube service python-env --url
```

## Running the Code

1. **Database Setup**:
   - PostgreSQL is used for storing data, with SQLAlchemy for ORM. The data needed for training and inference will be
   populated directly into de DB during scraping. To start the database run
    ```bash
    kubectl apply -f kubernetes/postgres-db.yaml
    ```

2. **Data Collection**:
   - We use `scrapy` to extract historical ecoin data. The preferred way to run spiders is from src/crawler/crawl.py. The script supports command line arguments for coin identifier, start date and end date. If no end date is provided, only start date is scraped, in all other cases, the full range of dates is extracted.
   For example, to populate the database with historical data, kubectl exec into the python env and run:
   ```bash
   python src/crawler/crawl.py --coin_id bitcoin --start_date "2020-01-01" --end_date $(date -d "today" +%F) --db_store True
   python src/crawler/crawl.py --coin_id ethereum --start_date "2020-01-01" --end_date $(date -d "today" +%F) --db_store True
   ```

3. **Scheduled Updates**:
   - Use Kubernetes cron jobs to keep data and models updated:
   ```bash
   kubectl apply -f kubernetes/bitcoin-crawler.yaml
   kubectl apply -f kubernetes/ethereum-crawler.yaml
   ```

4. **Model Training**:
   - Train forecasting models with:
   ```bash
   python src/models/train_forecasters.py -c bitcoin
   python src/models/train_forecasters.py -c ethereum
   ```

   - Schedule retraining with Kubernetes cron jobs:
   ```bash
   kubectl apply -f kubernetes/models-volume-claim.yaml
   kubectl apply -f kubernetes/bitcoin-train.yaml
   kubectl apply -f kubernetes/ethereum-train.yaml
   ```

5. **API Deployment**:
   - To serve the forecasting models a REST API was built. The API has one endpoint that receives a coin and a target date and returns a json with all dates from the day after the model was trained to the target date as keys and forecasted prices as values. To start the API run:
   ```bash
   kubectl apply -f kubernetes/forecasting-api.yaml
   ```

## Project Organization
```
├── README.md            <- Project documentation.
├── data
│   ├── interim          <- Intermediate data transformations.
│   ├── ready            <- Final datasets for modeling.
│   └── raw              <- Original data dumps.
│
├── notebooks            <- Jupyter notebooks for analysis.
├── references           <- Documentation and resources.
├── src
│   ├── db_scripts       <- Database-related scripts.
│   ├── crawler          <- Data scraping scripts.
│   └── models           <- Forecasting models and training scripts.
├── pyproject.toml       <- Dependency management configuration.
├── docker-compose.yml   <- Local Docker Compose setup.
└── .pre-commit-config   <- Git pre-commit hooks configuration.
```