FROM python:3.10.4

# Export env variables
ENV PROJECT src
ENV HOME /home

# Install poetry
RUN pip install poetry>=1.0.0

# create a project directory inside project home
ENV PROJECT_DIR $HOME/$PROJECT
RUN mkdir $PROJECT_DIR && \
    chown $UID:$GID $PROJECT_DIR && \
    chmod u+x $PROJECT_DIR

WORKDIR $PROJECT_DIR

# Copy poetry installation files
COPY --chown=$UID:$GID poetry.lock $PROJECT_DIR/
COPY --chown=$UID:$GID pyproject.toml $PROJECT_DIR/

# Copy project and notebook files
COPY --chown=$UID:$GID ./$PROJECT/ $PROJECT_DIR/$PROJECT
COPY --chown=$UID:$GID ./notebooks/ $PROJECT_DIR/notebooks

# Install poetry dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# expose port for jupyter lab
EXPOSE 8787

# define password for jupyter
ENV JUPYTER_TOKEN eureka