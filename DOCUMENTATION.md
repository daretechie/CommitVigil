# CommitGuard AI: Comprehensive Documentation 📚

Welcome to the internal mechanics of CommitGuard AI. This document provides a deep dive into the **Unified Enforcer** architecture—the bridge between chat-based behavioral analysis and GitOps technical accountability.

---

## 🏗️ Architecture Overview: The Unified Enforcer

CommitGuard AI is built on a **High-Fidelity Event-Driven Architecture**:
1.  **FastAPI Entrypoint**: Multi-source ingestion (Slack threads + Git Webhooks).
2.  **Redis Broker**: Handshakes the data to background workers via **ARQ**.
3.  **The Intelligence (Brain)**:
    - `ExcuseDetector`: Analyzing the "Human Layer" (Sentiment).
    - `SlippageAnalyst`: Analyzing the "Code Layer" (Promise-vs-Reality).
    - `TruthGapDetector`: Correlating the two for 360-degree accountability.
4.  **Persistence Layer**: PostgreSQL (via SQLModel) stores unified identities and historical scores.
5.  **Intervention Layer**: Outbound Slack Webhooks with precision @mentions.

---

## 🚦 Core Workflows

### 1. Ingestion: Behavioral vs. GitOps
- **Behavioral**: Call `POST /ingest/raw`. Extracts who/what/when from chat.
- **GitOps**: Call `POST /ingest/git`. Extracts commitments from commit messages and PR descriptions.
- **Identity Fusion**: Use `POST /users/config/git` and `/slack` to link emails and Slack IDs to a single human owner.

### 2. The "Unified Accountability Loop"
1.  **Evaluation**: Triggered via `POST /evaluate`.
2.  **Slippage Check**: The agent cross-references the check-in sentiment against recent technical evidence.
3.  **Truth Gap Analysis**: If a user claims 90% progress but Git shows 0 changes, the `TruthGapDetector` flags a discrepancy.
4.  **Tone Selection**: `ToneAdapter` scales pressure (Supportive for fatigue, Confrontational for deflection).
5.  **Intervention**: If risk is High/Critical, an autonomous Slack follow-up is triggered.

---

## 💬 Integration Guide

### Setting up @Mentions & Git Mapping
To unify a developer's identity:
1.  **Slack**: Find Member ID (e.g., `U12345`). Map with `POST /users/config/slack`.
2.  **Git**: Map their dev email with `POST /users/config/git`.
3.  **Result**: CommitGuard now knows that `dev@company.com` on GitHub is the same person as `@John` on Slack.

---

## 🧪 Testing and Quality
CommitGuard AI enforces a **90% coverage threshold**.
- **Unit Tests**: Test individual agent logic in `src/agents/`.
- **Performance Tests**: Verify the correlation logic in `tests/test_performance.py`.
- **Mock Mode**: Set `LLM_PROVIDER="mock"` to run full-suite tests without hitting API credits.

---

## 🚀 Scaling for Production
- **Database**: Pre-configured for **PostgreSQL**. Update your `DATABASE_URL` in `.env`.
- **Concurrency**: Scale by increasing `worker` replicas in `docker-compose.yml`.
- **Observability**: Live metrics at `:8000/metrics`.
