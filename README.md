# Full Stack ML Challenge

# Challenge Description
A machine learning challenge focused on structured data and forecasting. Participants will need to develop a machine learning model capable of predicting the price of ecoins based on historical price data and any other feature they deem useful. The model should be able to handle multiple ecoins and predict their prices for a given time period in the future.

Participants are required to develop a system for data collection and preprocessing, which includes scraping historic ecoin price data from coingecko and performing some data analysis using SQL. A toy sample of data is sufficient for the purposes of the challenge.

High performance in terms of accuracy is not expected for this challenge, participants should focus on building a complete end-to-end solution rather than optimizing the model's performance.

The solution should be deployed to a cloud environment, allowing for easy access and interaction with the trained model. Participants should consider the necessary infrastructure, deployment processes, and any additional components required for seamless integration and scalability.

The challenge is partially based on a [Mutt Data](https://muttdata.ai/) challenge. The base structure of the repo is adapted from Cookie Cutter Data Science and from [Tryolab's](https://tryolabs.com/) `project-base` template.

# My solution
## Getting started with the repo

### Installing virtual environments and getting dependencies

1. **Poetry**

Before we even start to code, we need to set up a virtual environment to handle the project dependencies separately
from our system's Python packages. This will ensure that whatever we run on our local machine will be
reproducible in any teammate's machine.

I use `poetry` to to install and manage dependencies. I also use `pyenv` (see [here](https://github.com/pyenv/pyenv-installer)) to manage python versions.

The codebase uses `Python 3.10.9`. So after installing `pyenv` and `poetry` run
```bash
pyenv install 3.10.9
pyenv shell 3.10.9
pyenv which python | xargs poetry env use
poetry config virtualenvs.in-project true
poetry install
```
to create a virtual environment, and install all dependencies to it. Then, close the terminal and activate the `poetry` env with
```bash
    poetry shell
```
Once inside the shell we'll also run
```bash
    pre-commit install
```
to setup git hooks.

2. **Docker & Kubernetes**

Going one step further from poetry lock files, we want to have our code containerized to really ensure a deterministic
build, no matter where we execute. This repo uses docker to containerize the code and kubernetes to orechestrate containers.

To locally test the kubernetes cluster you can install `minikube` (see [here](https://minikube.sigs.k8s.io/docs/start/)).

Custom images used in yamls in kubernetes are stored in my personal GCP Container Registry. You can either ping me for
credentials or build the images from the Dockerfiles, push to your own CR and modify the kubernetes yamls accordingly.

To login to docker using gcp credentials run:
```bash
    cat .secrets/gcp_service_account_creds.json | docker login -u _json_key --password-stdin https://gcr.io
```

To use the credentials in kubernetes run:
```bash
    kubectl create secret docker-registry gcr-json-key --docker-server=gcr.io --docker-username=_json_key --docker-password="$(cat .secrets/gcp_service_account_creds.json)" --docker-email=any@valid.email
```

You can check everything is working as its supposed to by running the postgres db and local python env deployments:
```bash
    kubectl apply -f postgres-db.yaml
    kubectl apply -f kubernetes/python-env.yaml
```

The python-env containers are installed wth the latest poetry lock available in this repo. Anything you can run locally you should
be able to run inside these containers. To access the containers you can kubectl exec into the corresponding pod and container, or
you can access the jupyter lab at:
```bash
minikube service python-env --url
```

Whatever the method, once inside the container try for one simple test:
```bash
python src/db_scripts/test_database_connection.py
```

## Ecoin Price Forecaster

1. **Coingecko Crawler**
The first part of the challenge consists on extracting a toy training dataset of historic coin prices from coingecko.

For the crawler logic we're going in 'all guns a-blazing', using `scrapy` to get the data from the API.
It's a bit of an overkill, but it will solve the storage and bulk processing of the data further down the
line, it also supports concurrent processing, and it generally scales really well to more complex tasks.

Scrapy crawler logic is in the `src.crawler` module. The root of the `scrapy` project is the project's root directory.
All `scrapy` commands should be run from there.

The preferred way to run spiders is from `src/crawler/crawl.py`. The script supports command line arguments for
coin identifier, start date and end date. If no end date is provided, only start date is scraped, in all other cases, the full range
of dates is extracted. For example, to get the data for bitcoin, between the dates "2017-12-15" and "2017-12-30", run
```bash
python src/crawler/crawl.py --coin_id bitcoin --start_date "2017-12-15" --end_date "2017-12-30"
```
Check the crawl script's `--help` for more information.

2. **Database Setup**
In the second part we keep building on the solution by adding a postgres database that stores the scraped prices.

We are using sqlalchemy to define the postgres database, and docker/ kubernetes to run the db and connect the crawler with the storage.

At this point we just needed to enable scrapy pipelines to populate our database directly with the items we scrape. Mind you, as
the database is defined in kubernetes, to test this part, you'll need to create the postgress and python-env pods and run the crawler script inside the python-env pod as described in the getting started section.

Once inside the container you can just run the scraping script from last section with the db_store option set to true. To populate your db with data from 2019 to current data, you can try:
```bash
python src/crawler/crawl.py --coin_id bitcoin --start_date "2019-01-01" --end_date $(date -d "today" +%F) --db_store True
```
Note: Coingecko's API is awfully sensible to request load so scrapy has been configured to avoid being blocked. On current configuration, without spending on an enterprise account, the scraping will take around eight hours to complete.

3. **Crawler Scheduling**
In order to keep our data updated we'll run the scraper everyday for bitcoin and ethereum coins.

To schedule this jobs we'll use kubernetes cronjobs. To enable just run:
```bash
kubectl apply -f kubernetes/bitcoin-crawler.yaml
kubectl apply -f kubernetes/ethereum-crawler.yaml
```

4. **Data Analysis**
Solution for the SQL data analysis excercises are provided in the form of .sql files. To test the queries you can access
the postgres pod and execute the sql files. Inside the postgres container run:
```bash
psql postgresdb admin -f home/query1.sql
psql postgresdb admin -f home/query2.sql
```

5. **Model Training & Maintenance**
A base class for the forecasting models was implemented in the `src.models.forecasters` module. The base class offers
functionality for data loading and visualization.

For our first forecaster I've implemented a standard SARIMA model. Note that the the ecoin timeseries don't present significant auto
correlation on many lags. We're still using this model as a first aproximation and as a baseline for further modeling.

To test the train models script for a coin, having accessed the python env container, run:
`python src/models/train_forecasters.py -c <coin-name>`

To keep the models up to date with the latest data a retrain cronjob was implemented for bitcoin and ethereum. A historic is
also kept for rollback purposes. To start the cronjobs run:
```bash
kubectl apply -f kubernetes/bitcoin-train.yaml
kubectl apply -f kubernetes/ethereum-train.yaml
kubectl apply -f kubernetes/models-volume-claim.yaml
```

6. **Model Availalability**
To save the forecasting models a REST API was built. The API has one endpoint that receives a coin and a target date and
returns a json with all dates from the day after the model was trained to the target date as keys and forecasted prices
as values.

The API is also deployed as a kubernetes deployment; to start it run:
```bash
kubectl apply -f kubernetes/forecasting-api.yaml
```

## Project Organization
This is not comprehensive.

Main folder and file structure for the project (the tree is non comprehensive)
```
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── ready          <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `001-sc-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, links to Notion or other explanatory materials.
    │
    │
    ├── src
    │   │
    │   ├── db_scripts     <- Database related scripts
    │   │
    │   └── crawler        <- Scripts to scrape data.
    │   │
    │   └── models         <- Scripts related forecasting models
    │
    │
    ├── pyproject.toml     <- File to manage dependencies and some tool's configurations.
    │
    ├── docker-compose.yml <- Docker compose file
    │
    └── .pre-commit-config <- File to setup git pre commit hooks.

```