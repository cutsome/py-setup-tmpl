# build ステージ
FROM --platform=amd64 python:3.10 as build

# poetry を使って、パッケージインストール
COPY poetry.lock pyproject.toml /

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python \
  && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry \
  && poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-root


# prd ステージ
FROM --platform=amd64 python:3.10-slim as prd

ENV PYTHONPATH /app

# psql コマンドインストール
RUN apt-get update \
  && apt-get install -y --no-install-recommends postgresql-client \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# build ステージより、パッケージコピー
COPY --from=build /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# ソースコードコピー
COPY ./app /app
WORKDIR /app
