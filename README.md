# Guzman's Mutt Data Exam

Guzman Vitar's exam for the Mutt Data selection process.

## Getting started

### Installing virtual environments and getting dependencies

1. **Poetry**

Before you start to code, we'll need to set up a virtual environment to handle the project dependencies separately
from your system's Python packages. This will ensure that whatever you run on your local machine will be
reproducible in any teammate's machine.

We'll be using `poetry` to to install and manage dependencies. You should also install `pyenv` (see [here](https://github.com/pyenv/pyenv-installer)) to manage python versions.

The codebase uses `Python 3.10.4`. So after installing `pyenv` and `pyenv` run
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
    pre-commit install
```

2. **Docker & docker compose**

Going one step further from poetry lock files, we wish to have our code containerized to really ensure a deterministic
build, no matter where we run our code. We'll use docker and docker compose to containerize our code.

You already have a Dockerfile and a docker-compose.yaml that creates a container with your source code and notebooks
using the same poetry lock file, so you can switch from poetry development to docker with easy.

To initialize just run
```bash
    docker compose up
```

## Project Organization

Main folder and file structure for the project.
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
    ├── ml_project_template
    │   │
    │   ├── data           <- Scripts to download or generate data.
    │   │
    │   ├── models         <- Scripts to train models and make predictions.
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations.
    │
    ├── pyproject.toml     <- File to manage dependencies and some tool's configurations.
    │
    ├── tox.ini            <- File to manage vscode configuration.
    │
    └── .pre-commit-config <- File to setup git pre commit hooks.

```
## The challenge

1. **Coingecko crawler**

For the crawler logic we're going in all guns a'blazing, using `scrapy` to get the data from the API.
I know, it's a bit of an overkill, but it solves the storage and bulk processing of the data further down the
line, it also supports concurrent processing, and it generally scales really well to more complex tasks.

Scrapy crawler logic is in the `src.crawler` module, which uses. The root of the `scrapy` project is the project's root directory. All `scrapy` commands should be run from there.

The preferred way to run spiders is from `src/crawler/crawl.py`. The script supports command line arguments for
coin identifier, start date and end date. If no end is provided, only one date is scraped, if not, the full range of dates is extracted. For example, to get the data for bitcoin, between the dates "15-12-2017" and "30-12-2017", run
```python
python src/crawler/crawl.py --coin_id bitcoin --start_date "15-12-2017" --end_date "30-12-2017"
```
Check the crawl script's `--help` for more information.

2. **Database setup**

We are using sqlalchemy to define the postgres database, and docker/ docker compose to run the db and orquestrate the crawler with the storage.

At this point we just need to enable scrapy pipelines to populate our database directly with the items we scrape. Mind you, as
the database is generated through docker compose, in order for this part to work, you'll need to run on docker compose (as
oposed to your poetry environment).

Run `docker compose up`, you can then run the scraping script from last section in the python container.

3. **Workflow scheduling**

For the next part, we'll build over our code adding the workflow scheduling logic; we'll be using airflow for this. But wait a minute,
I hear you say: Isn´t a simple CRON entry enough for this problem? Well, while its true that CRON is the most time eficient and
straightforward (and requested) tool for the job, it has the downside of beying terrible boring as compared to airflow.

As per the current configuration, all you need to do is docker compose up, navigate to airflow-webserver in port 8080 and activate the dags.

**sad note:** Had my fun, now im paying for it. My DockerOperator tasks are having trouble conecting to the scraping database within docker compose,
I'll come back and fix this issue if I have enough time.