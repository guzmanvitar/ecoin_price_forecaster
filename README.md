# Full stack ML challenge

# Challenge description
A two-project machine learning challenge that aims to test skills involved in the development of end-to-end ML projects, from data extraction and model development to serving and deploying the solution in the cloud. The challenge consists of two projects:

1. The first project of the machine learning challenge involves ecoin price forecasting. Participants will need to develop a machine learning model capable of predicting the price of a specific ecoin based on its historical price data and any other feature they deem useful. The model should be able to handle multiple ecoins and predict their prices for a given time period in the future.

Participants are required to develop a system for data collection and preprocessing, which includes scraping historic ecoin price data from coingecko. A toy sample of data is sufficient for the purposes of the challenge.

The machine learning model should be designed to handle multiple ecoins and forecast their prices for a specified time period in the future. High performance in terms of accuracy is not expected for this challenge, participants should focus on building a complete end-to-end solution rather than optimizing the model's performance.

Finally, the solution should be deployed to a cloud environment, allowing for easy access and interaction with the trained model. Participants should consider the necessary infrastructure, deployment processes, and any additional components required for seamless integration and scalability.

2. The NLP project involves building a sentiment analysis system to track sentiment in real-time from a set of Twitter topics. Participants will need to develop a machine learning model capable of classifying tweets based on their sentiment, categorizing them as positive, negative, or neutral.

Participants are required to develop a system for data collection and preprocessing. This includes designing a mechanism to collect and process tweets in real time related to the specified topics from the Twitter API. The collected data should undergo preprocessing steps, such as text cleaning, tokenization, and removing noise, to ensure high-quality input for training the sentiment analysis model.

Furthermore, the solution should be deployed to a cloud environment, enabling real-time sentiment analysis of incoming tweets. Participants should consider the necessary infrastructure, deployment processes, and any additional components required for seamless integration and scalability.

To provide a comprehensive view of the sentiment analysis results, participants are also required to create a dashboard that visualizes the sentiment analysis outputs in real-time. The dashboard should provide an intuitive and user-friendly interface to monitor and analyze the sentiment trends related to the specified topics on Twitter.

Throughout the project, participants will be evaluated based on their ability to build a complete end-to-end solution, including data collection, preprocessing, model development and training, cloud deployment, and real-time visualization. Emphasis will be placed on the overall system architecture, data quality, and the effectiveness of the sentiment analysis model.

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

2. **Docker & kubernetes**

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

## Project 1: Ecoin price forecaster

1. **Coingecko crawler**
The first part of the challenge consists on extracting a toy training dataset of historic coin prices from coingecko.

For the crawler logic we're going in 'all guns a-blazing', using `scrapy` to get the data from the API.
It's a bit of an overkill, but it will solve the storage and bulk processing of the data further down the
line, it also supports concurrent processing, and it generally scales really well to more complex tasks.

Scrapy crawler logic is in the `src.crawler` module. The root of the `scrapy` project is the project's root directory.
All `scrapy` commands should be run from there.

The preferred way to run spiders is from `src/crawler/crawl.py`. The script supports command line arguments for
coin identifier, start date and end date. If no end date is provided, only one date is scraped, in all other cases, the full range
of dates is extracted. For example, to get the data for bitcoin, between the dates "2017-12-15" and "2017-12-30", run
```bash
python src/crawler/crawl.py --coin_id bitcoin --start_date "2017-12-15" --end_date "2017-12-30"
```
Check the crawl script's `--help` for more information.

2. **Database setup**
In the second part we are asked to keep building on the solution by adding a postgres database that stores the scraped prices.

We are using sqlalchemy to define the postgres database, and docker/ docker compose to run the db and orquestrate the crawler with the storage.

At this point we just needed to enable scrapy pipelines to populate our database directly with the items we scrape. Mind you, as
the database is generated through docker compose, in order for this part to work, you'll need to run on docker compose (as
oposed to your poetry environment).

Run `docker-compose up`, then run docker exec to the python_poetry service, or just navigate to jupyter lab in port 8787 (the password
for jupyter is eureka). Once in the comand line you can just run the scraping script from last section with the db_store option set to
true. To populate your db with a fair amount of data, you can try:
```bash
python src/crawler/crawl.py --coin_id bitcoin --start_date "2019-01-01" --end_date "2022-12-15" --db_store True
```
note: coingecko's API is pretty sensible to request load, scrapy has been configured to push the limits, but the previous scraping will
still take around 15 minutes to complete.

3. **Scheduling and orchestration**
For the next part, we are asked to add scheduling to run the scraper daily.

For the scheduling logic we're going to use airflow. But wait a minute, I hear you say: Isn't a simple CRON entry enough for this problem? Well, my shrewd friend, while its true that CRON is the most codingtime eficient and straightforward (and requested) tool for the job, it has the fatal flaw of being terrible boring compared to airflow.

In any case, as per the current configuration, all you need to do is docker compose up, navigate to airflow-webserver in port 8080 and activate the dags.

4. **Data Analysis**

Data analysis is provided in the form of .sql files. The files are shared through compose with the scraping_database service. To test the queries you can access
the postgres service and execute the sql files; having previously started docker compose run:
```bash
docker exec -it scraping_database bash
psql postgresdb admin -f home/query1.sql
psql postgresdb admin -f home/query2.sql
```

## Project 2: Real time twitter sentiment analysis
1. **Twitter streaming**

A twitter streaming script that checks for twits based on a list of filters is implemented using tweepy. The script runs automatically with the
filter "christmas" when initializing docker compose. It can also be run on any list of filters locally through:
```bash
python src/twitter_streaming/twitter_tracker.py -t filter1 filter2 ... filtern
```

TODO: Part 2 of excercise 4 involving spark processing is not implemented.


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
    │   ├── crawler        <- Scripts to scrape data.
    │   │
    │   └── twitter_
    │          streaming.  <- Scripts related to twitter stream functionality
    │
    │
    ├── pyproject.toml     <- File to manage dependencies and some tool's configurations.
    │
    ├── docker-compose.yml <- Docker compose file
    │
    └── .pre-commit-config <- File to setup git pre commit hooks.

```