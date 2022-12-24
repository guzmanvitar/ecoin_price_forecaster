# Guzman's Mutt Data Exam

Guzman Vitar's exam for the Mutt Data selection process.

## Getting started

### Installing virtual environments and getting dependencies

1. **Poetry**

Before we start to code, we'll need to set up a virtual environment to handle the project dependencies separately
from our system's Python packages. This will ensure that whatever we run on our local machine will be
reproducible in any teammate's machine.

We'll be using `poetry` to to install and manage dependencies. We will also install `pyenv` (see [here](https://github.com/pyenv/pyenv-installer)) to manage python versions.

The codebase uses `Python 3.10.4`. So after installing `pyenv` and `poetry` run
```bash
pyenv install 3.10.4
pyenv shell 3.10.4
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
to setup hooks.

2. **Docker & docker compose**

Going one step further from poetry lock files, we wish to have our code containerized to really ensure a deterministic
build, no matter where we execute. We'll use docker and docker compose to containerize our code.

This repo starts with a Dockerfile and a docker-compose.yaml that creates a container with your source code and notebooks,
using the same poetry lock file, so you can switch from poetry development to docker with ease.

To initialize just run
```bash
    docker compose-up
```

## Project Organization

Main folder and file structure for the project (the tree is non comprehensive)
```
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── ready          <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries.
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `001-sc-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, links to Notion or other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting.
    │
    ├── src
    │   │
    │   ├── data           <- Scripts to download or generate data.
    │   │
    │   ├── crawler        <- Scripts to scrape data.
    │   │
    │   ├── models         <- Scripts to train models and make predictions.
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations.
    │
    ├── pyproject.toml     <- File to manage dependencies and some tool's configurations.
    │
    ├── docker-compose.yml <- Docker compose file
    │
    └── .pre-commit-config <- File to setup git pre commit hooks.

```
## The challenge

1. **Coingecko crawler**

For the crawler logic we're going in 'all guns a-blazing', using `scrapy` to get the data from the API.
I know, it's a bit of an overkill, but it will solve the storage and bulk processing of the data further down the
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

3. **Workflow scheduling**

For the next part, we kept building over our code, adding the workflow scheduling logic; we used airflow for this.

But wait a minute, I hear you say: Isn't a simple CRON entry enough for this problem? Well, my shrewd friend, while its true that
CRON is the most codingtime eficient and straightforward (and requested) tool for the job, it has the fatal flaw of being terrible boring compared to airflow.

In any case, as per the current configuration, all you need to do is docker compose up, navigate to airflow-webserver in port 8080 and activate the dags.

**sad note:** Had my fun, now im paying for it. My DockerOperator tasks are having trouble conecting to the scraping database within docker compose, I'll come back and fix this issue if I have enough time.
