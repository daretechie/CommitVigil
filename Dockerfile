# Use a slim Python 3.12 image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
RUN pip install poetry
COPY pyproject.toml .
RUN poetry config virtualenvs.create false && poetry install --no-root

# Copy project
COPY . .

# Exposure (FastAPI default)
EXPOSE 8000

# We use docker-compose to decide whether to run 'uvicorn' or 'arq'