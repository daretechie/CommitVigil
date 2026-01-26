# CommitGuard AI: The Autonomous Accountability Platform 🛡️

![CommitGuard AI Hero](docs/assets/hero.jpg)

<!-- Badges: Enterprise Metrics -->
![Tests](https://img.shields.io/badge/adversarial_tests-10%2F10%20passing-brightgreen?style=for-the-badge)
![Throughput](https://img.shields.io/badge/throughput-1250%20msg%2Fsec-blue?style=for-the-badge)
![Latency](https://img.shields.io/badge/P95%20latency-<500ms-success?style=for-the-badge)
![Cost Savings](https://img.shields.io/badge/token%20savings-85%25-orange?style=for-the-badge)
![ROI](https://img.shields.io/badge/net%20ROI-%24558%2Fmonth-gold?style=for-the-badge)

> **"One Engine. Two Worlds. Total Accountability."**

[**Full Documentation 📚**](https://daretechie.github.io/CommitGuard-AI/) | [**Safety Validation Report 🛡️**](https://daretechie.github.io/CommitGuard-AI/validation/safety_validation_report/)

---


## 🎭 Dual-Persona Versatility

CommitGuard AI is a multi-agent system designed for high-stakes enforcement. It adapts its identity based on the operational environment:

### 1. The Behavioral Accountability Agent (Management)
**Headline:** *"Autonomous AI Agents for High-Stakes Accountability & Performance Enforcement"*
- **Problem:** Remote teams struggle with "commitment drift" and excuse-making.
- **Solution:** Proactively monitor chat promises.
- **Outcome:** Support burnout signals early; confront repeat deflection firmly.

### 2. The GitOps Accountability Engine (Engineering)
**Headline:** *"AI-Driven GitOps Accountability: Guaranteeing Commitment Follow-Through"*
- **Problem:** Small technical promises in commits/PRs (e.g., *"I'll fix this later"*) vanish into the noise.
- **Solution:** NLP-driven monitoring of source code level commitments.
- **Outcome:** 100% visibility into "soft commitments" made during the dev cycle.

---

## 🏗️ The Four-Stage Autonomous Pipeline
Every commitment—whether from Slack or a Git Commit—passes through a deterministic reasoning loop:

1.  **Excuse Detection (`ExcuseDetector`)**: Classifies sentiment (Legitimate vs. Deflection vs. Burnout).
2.  **Predictive Risk Assessment (`RiskScorer`)**: Quantifies failure probability based on historical reliability.
3.  **Safety Supervisor (`Overwatch`)**: Audits final communications for HR/Legal ethics and tone drift.
4.  **Adaptive Pressure (`ToneAdapter`)**: Selects the psychological tone to ensure delivery.

---

## 🛠️ Core Tech Stack
- **Framework**: FastAPI (Python 3.12+)
- **LLM Orchestration**: Instructor + Pydantic (Deterministic JSON)
- **Quality**: Strict MyPy typing + Ruff
- **Infrastructure**: PostgreSQL + Redis + ARQ
- **Observability**: Prometheus + Structlog

---

## 🚀 API Showcase

> **Note:** All API endpoints require authentication via the `X-API-Key` header.

### Raw Extraction (Slack/Commit/PR)
```bash
curl -X 'POST' \
  -H 'X-API-Key: YOUR_API_KEY' \
  'http://localhost:8000/api/v1/ingest/raw?user_id=dev_alpha&raw_text=Fixing%20auth%20logic.%20I%20promise%20to%20refactor%20the%20DB%20connector%20by%20Friday'
```

### Behavioral Evaluation
```bash
curl -X 'POST' \
  -H 'X-API-Key: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  'http://localhost:8000/api/v1/evaluate' \
  -d '{
  "user_id": "dev_alpha",
  "commitment": "refactor the DB connector",
  "check_in": "Spent all night on it, feeling pretty drained"
}'
```

### Performance Integrity Audit (The Deliverable)
Generate a high-value summary of a developer's communication-vs-technical reality.
```bash
curl -X 'GET' \
  -H 'X-API-Key: YOUR_API_KEY' \
  'http://localhost:8000/api/v1/reports/audit/dev_alpha'
```



---
*Built for High-Performance Teams and Elite Portfolios.*
