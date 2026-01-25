# CommitGuard AI: The Autonomous Accountability Platform 🛡️

![CommitGuard AI Hero](docs/assets/hero.jpg)

> **"One Engine. Two Worlds. Total Accountability."**

[**Full Documentation 📚**](https://daretechie.github.io/CommitGuard-AI/)

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

## 🏗️ The Three-Stage Autonomous Pipeline
Every commitment—whether from Slack or a Git Commit—passes through a deterministic reasoning loop:

1.  **Excuse Detection (`ExcuseDetector`)**: Classifies sentiment (Legitimate vs. Deflection vs. Burnout).
2.  **Predictive Risk Assessment (`RiskScorer`)**: Quantifies failure probability based on historical reliability.
3.  **Adaptive Pressure (`ToneAdapter`)**: Selects the psychological tone (Supportive → Firm → Confrontational) to ensure delivery.

---

## 🛠️ Core Tech Stack
- **Framework**: FastAPI (Python 3.12+)
- **LLM Orchestration**: Instructor + Pydantic (Deterministic JSON)
- **Infrastructure**: PostgreSQL + Redis + ARQ
- **Observability**: Prometheus + Structlog

---

## 🚀 API Showcase
### Raw Extraction (Slack/Commit/PR)
```bash
curl -X 'POST' \
  'http://localhost:8000/ingest/raw?user_id=dev_alpha&raw_text=Fixing%20auth%20logic.%20I%20promise%20to%20refactor%20the%20DB%20connector%20by%20Friday'
```

### Behavioral Evaluation
```bash
curl -X 'POST' \
  'http://localhost:8000/evaluate' \
  -d '{
  "user_id": "dev_alpha",
  "commitment": "refactor the DB connector",
  "check_in": "Spent all night on it, feeling pretty drained"
}'
```

---
*Built for High-Performance Teams and Elite Portfolios.*
