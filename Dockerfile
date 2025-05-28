FROM python:3.11 AS base

ADD app $ROOT/app

# Set working directory
WORKDIR $ROOT/app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry

# Copy dependencies files
COPY pyproject.toml poetry.lock* ./

# install dependencies (no dev-deps in prod)
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi --no-root

RUN poetry self update 1.8.4

# copy app sources
COPY . /app

# Expose API and database ports
EXPOSE 8000
EXPOSE 5432
EXPOSE 6379

# Add commands
COPY commands $ROOT/commands
RUN chmod +x $ROOT/commands/*
ENV PATH="$ROOT/commands:$PATH"

ENTRYPOINT [ "entrypoint.sh" ]
CMD [ "start.sh" ]
