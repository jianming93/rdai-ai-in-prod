FROM python:3.10.13-slim

ARG GRADIO_SERVER_PORT=7070

# Poetry's configuration:
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/opt/poetry' \
    POETRY_VERSION=1.7.1 \
    GRADIO_ANALYTICS_ENABLED=false \
    GRADIO_SERVER_PORT=${GRADIO_SERVER_PORT}

# System deps:
RUN apt-get update \
  && apt-get install curl -y \
  && curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="$POETRY_HOME/bin:$PATH"

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml /app/

RUN poetry install --no-dev

COPY . .

ENTRYPOINT [ "python" ]
CMD [ "main.py" ]
