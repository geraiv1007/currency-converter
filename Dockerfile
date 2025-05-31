FROM python:3.12-slim
RUN pip install --upgrade pip\
 && pip install poetry
WORKDIR /currency_converter
COPY poetry.lock pyproject.toml .
RUN poetry install --no-root
COPY app ./app/
COPY .env alembic.ini main.py .
#RUN poetry run alembic upgrade head