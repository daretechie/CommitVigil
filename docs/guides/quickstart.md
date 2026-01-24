# Quick Start Guide ⚡

Get CommitGuard AI running in under 5 minutes.

## 🐳 Running with Docker (Recommended)
The fastest way to spin up the full stack (API + Worker + Redis + Postgres):

```bash
docker-compose up --build
```

## 🏗️ Local Poetry Setup
1.  **Install dependencies**:
    ```bash
    poetry install
    ```
2.  **Configure Environment**:
    Create a `.env` file based on `.env.example`.
3.  **Run the API**:
    ```bash
    poetry run uvicorn src.main:app --reload
    ```
4.  **Run the Worker**:
    ```bash
    poetry run arq src.worker.WorkerSettings
    ```

---

## 🧪 Running the Test Suite
Standardized tests are enforced with 90%+ coverage.
```bash
poetry run pytest
```
