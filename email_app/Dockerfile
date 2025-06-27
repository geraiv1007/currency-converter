FROM python:3.13-slim
RUN pip install --upgrade pip && pip install poetry
WORKDIR /email_app
COPY poetry.lock pyproject.toml .
RUN poetry install --no-root
COPY email_app ./email_app/
COPY mail.env .