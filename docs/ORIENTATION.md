# Repository Orientation: CommitVigil AI 🛡️

Welcome to CommitVigil. This repository has been rigorously cleaned and structured to ensure maximum clarity and maintainability.

## 🏗️ Architectural Invariants

### 1. Separation of Reasoning
All AI logic resides in `src/agents/`. 
- **The Brain** (`brain.py`): Orchestrates the 5-stage pipeline.
- **The Safety Supervisor** (`safety.py`): Acts as a semantic firewall.
- **The Context Scout** (`scout.py`): Senses industry/departmental context.

### 2. DTO & Persistence Stability
We use **SQLModel** in `src/schemas/agents.py`. These classes serve as both database models and API data transfer objects. Do not duplicate schemas unless absolutely necessary for versioning.

### 3. Asynchronous Backbone
All long-running evaluations are offloaded to **ARQ workers** (`src/worker.py`). The API should never block on an LLM call.

## 📂 Key Directories

| Directory | Purpose |
| :--- | :--- |
| `src/core/` | Low-level cross-cutting concerns (DB, Config, Logging). |
| `infra/` | Configuration templates (K8s, Prometheus). |
| `docs/adr/` | Architectural Decision Records. Read these before suggesting major changes. |
| `tests/` | Use `pytest` for all verification. Adversarial tests are critical for safety. |

## 🧪 Quick Setup

1. **Install Dependencies**: `poetry install`
2. **Environment**: Copy `.env.example` to `.env` and provide your `OPENAI_API_KEY`.
3. **Run Services**: `docker-compose up -d`
4. **Run Sample**: `./scripts/demo.sh`

## 🧹 Maintenance Rules

- **Zero Tolerance for Junk**: Do not commit exploratory scripts or `.db` files to the root.
- **Test-Driven Refactor**: Always run the full suite (`pytest`) before submitting PRs.
- **Self-Documenting Fixes**: If a bug is architectural, record it as an ADR.
