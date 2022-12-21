# ml_project_template

Repo template for Machine Learning projects.

## Getting started

### Installing a virtual environment and getting dependencies
In order to set up the project, a virtual environment will be set up to handle the project dependencies without touching your system Python's packages.

You need `poetry` to install and manage dependencies. You should also install `pyenv` (see [here](https://github.com/pyenv/pyenv-installer)) to manage python versions.

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

---
Partially adapted from Cookie Cutter Data Science and from Tryolab's `project-base` template.