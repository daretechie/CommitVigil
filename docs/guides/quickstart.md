# Quick Start Guide ⚡

Get CommitVigil running in under 5 minutes.

## 🐳 Running with Docker (Recommended)
The fastest way to spin up the full stack (API + Worker + Redis + Postgres):

```bash
docker compose up --build
```

## 🏗️ Local Setup
1.  **Install dependencies**:
    ```bash
    # Recommendation: Use uv for high-performance dependency resolution
    uv sync
    # OR standard poetry
    poetry install
    ```
2.  **Configure Environment**:
    Create a `.env` file based on `.env.example`. 
    > **Important**: Set `API_KEY_SECRET` to a secure value for production. Set `AUTH_ENABLED=False` for local testing without auth.
3.  **Run the API**:
    ```bash
    poetry run uvicorn src.main:app --reload
    ```
4.  **Run the Worker**:
    ```bash
    poetry run arq src.worker.WorkerSettings
    ```

---

## 🧪 Quality and Stability
CommitVigil enforces military-grade engineering standards:
- **Mock Mode**: Set `LLM_PROVIDER="mock"` in `.env` to run the entire system with zero token cost.
- **Strict Typing**: The system is fully compliant with `mypy` strict type checking. Run `poetry run mypy src/` to verify correctness.
- **Coverage**: All critical agents maintain a high test coverage threshold.

```bash
# Run tests with clean output
uv run pytest
```
