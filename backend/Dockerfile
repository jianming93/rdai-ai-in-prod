FROM python:3.10.13-slim

# Poetry's configuration:
ENV POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local' \
  POETRY_VERSION=1.7.1

WORKDIR /app

RUN curl -sSL https://install.python-poetry.org | python3 -
COPY pyproject.toml .

RUN poetry install --only-root

COPY . . 

# ENTRYPOINT [ "poetry" ]
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9090" ]
