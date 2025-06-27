FROM python:3.13-slim
RUN apt-get update && apt-get install -y curl && apt-get clean
RUN pip install --upgrade pip && pip install poetry
WORKDIR /currency_app
COPY poetry.lock pyproject.toml .
RUN poetry install --no-root
COPY currency_app ./currency_app/
COPY currency.env alembic.ini .