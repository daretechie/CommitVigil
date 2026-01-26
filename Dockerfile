# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Final stage
FROM python:3.12-slim

WORKDIR /app

# Create a non-root user
RUN groupadd -r commitguard && useradd -r -g commitguard commitguard

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

# Ensure the database file is writable by the non-root user if using SQLite
RUN touch commitguard.db && chown commitguard:commitguard commitguard.db && chmod 600 commitguard.db
RUN chown -R commitguard:commitguard /app

USER commitguard

EXPOSE 8000

# We use docker-compose to decide whether to run 'uvicorn' or 'arq'