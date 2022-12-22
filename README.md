# Guzman's Mutt Data Exam

Guzman Vitar's exam for the Mutt Data selection process.

## Getting started

### Installing virtual environments and getting dependencies
1. *Poetry*

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

2. *Docker & docker compose*

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
