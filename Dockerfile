# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    libpq-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-root --no-interaction --no-ansi

# Final stage
FROM python:3.12-slim

# Install tini for better signal handling
RUN apt-get update && apt-get install -y --no-install-recommends tini && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create a non-root user
RUN groupadd -r commitvigil && useradd -r -g commitvigil commitvigil

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy app code with proper ownership to avoid slow chown later
COPY --chown=commitvigil:commitvigil . .

# User setup
USER commitvigil

EXPOSE 8000

ENTRYPOINT ["/usr/bin/tini", "--"]

# We use docker compose to decide whether to run 'uvicorn' or 'arq'