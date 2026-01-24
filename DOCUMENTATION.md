# CommitGuard AI: Comprehensive Documentation 📚

Welcome to the internal mechanics of CommitGuard AI. This document provides a deep dive into how to use the platform, how the agentic reasoning works, and how to scale the system.

---

## 🏗️ Architecture Overview

CommitGuard AI is built on a **Decoupled Event-Driven Architecture**:
1.  **FastAPI Entrypoint**: Receives natural language or structured data.
2.  **Redis Broker**: Handshakes the data to background workers via ARQ.
3.  **The Brain (Agents)**: A suite of specialized LLM agents that analyze sentiment, risk, and burnout.
4.  **Persistence Layer**: PostgreSQL (via SQLModel) stores historical reliability and Slack identity mapping.
5.  **Intervention Layer**: Outbound Slack Webhooks perform directed @mentions.

---

## 🚦 Core Workflows

### 1. The "Commitment Ingestion" Flow
When a user makes a vague promise in a public channel:
- **Action**: Call `POST /ingest/raw`.
- **Mechanics**: The `CommitmentExtractor` agent parses the text. It identifies the **Who** (Owner), **What** (Task), and **When** (Deadline).
- **Result**: A structured record is ready for tracking.

### 2. The "Accountability Loop"
This is the heartbeat of the platform.
- **Action**: Call `POST /evaluate`.
- **Step 1: Excuse Analysis**: The agent determines if a delay is "Legitimate," "Deflection," or a "Burnout Signal."
- **Step 2: Risk Scoring**: A score (0-1) is generated based on the check-in sentiment and historical reliability.
- **Step 3: Burnout Detection**: The agent looks for linguistic markers of fatigue or loss of copability.
- **Step 4: Adaptation**: The `ToneAdapter` selects a communication style:
    - `Supportive`: For high-performers showing burnout signs.
    - `Firm`: For repeat deflectors.
- **Step 5: Intervention**: A background job is scheduled. If the risk remains high, a **Slack Alert** is sent.

---

## 💬 Slack Integration Guide

### Setting up @Mentions
To make the agent mention specific people:
1. Find the user's **Slack Member ID** (Click profile -> More -> Copy member ID).
2. Call the mapping endpoint:
   ```bash
   POST /users/config/slack?user_id=internal_id&slack_id=U12345678
   ```
3. From now on, any alert for `internal_id` will ping `@User` in Slack.

---

## 🧪 Testing and Quality
CommitGuard AI enforces a **90% coverage threshold**.
- **Unit Tests**: Test individual agent logic in `src/agents/`.
- **Integration Tests**: Verify the loop from API to Database.
- **Mock Mode**: Set `LLM_PROVIDER="mock"` in `.env` to run tests without hitting your API credits.

---

## 🚀 Scaling for Production
- **Database**: The system is pre-configured for **PostgreSQL**. Simply update your `DATABASE_URL`.
- **Concurrency**: Scale your background processing by spinning up multiple `worker` containers in `docker-compose.yml`.
- **Observability**: Monitor system health at `:8000/metrics` via the integrated Prometheus exporter.
