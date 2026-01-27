# CommitVigil: The Autonomous Accountability Platform 🛡️

![CommitVigil Hero](docs/assets/hero.jpg)

<!-- Badges: Enterprise Metrics -->
[![Tests](https://github.com/daretechie/CommitVigil/actions/workflows/ci.yml/badge.svg)](https://github.com/daretechie/CommitVigil/actions/workflows/ci.yml)
![Throughput](https://img.shields.io/badge/throughput_benchmark-1250%20msg%2Fsec-blue?style=for-the-badge)
![Latency](https://img.shields.io/badge/target_P95_latency-<500ms-success?style=for-the-badge)
![Cost Savings](https://img.shields.io/badge/avg_token_savings-85%25-orange?style=for-the-badge)
![ROI](https://img.shields.io/badge/est_net_ROI-%24558%2Fmonth-gold?style=for-the-badge)

> **"One Engine. Two Worlds. Total Accountability."**

[**Full Documentation 📚**](https://daretechie.github.io/CommitVigil/) | [**Live Site 🌐**](https://daretechie.github.io/CommitVigil/) | [**Safety Validation Report 🛡️**](https://daretechie.github.io/CommitVigil/validation/safety_validation_report/)

---


## 🎭 Dual-Persona Versatility

CommitVigil is a multi-agent system designed for high-stakes enforcement. It adapts its identity based on the operational environment:

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

### 🛡️ 2026 Enterprise Upgrade: Elite Guardrails
The system now includes research-backed advanced features for global operations:
- **Continuous Learning Pipeline**: Persists manager decisions to calculate **Intervention Acceptance Rates** and refine AI strategies.
- **Cultural Persona Routing**: Automatically adapts tone for **Japanese (*Wa*)**, **German (*Sachlichkeit*)**, **French (Eloquence)**, **British English**, and **Spanish**.
- **Industry Semantic Firewall**: Intent-based security for **Healthcare (HIPAA)** and **Finance (SEC)** compliance.

## 🏗️ The Four-Stage Autonomous Pipeline
Every commitment—whether from Slack or a Git Commit—passes through a deterministic reasoning loop:

1.  **Excuse Detection (`ExcuseDetector`)**: Classifies sentiment (Legitimate vs. Deflection vs. Burnout).
2.  **Predictive Risk Assessment (`RiskScorer`)**: Quantifies failure probability based on historical reliability.
3.  **Language & Culture Router**: Identifies the primary language and selects the appropriate cultural persona.
4.  **Safety Supervisor (`Overwatch`)**: Audits final communications for HR/Legal ethics and **Industry-Specific Semantic Compliance**.

---

## 🛠️ Core Tech Stack
- **Framework**: FastAPI (Python 3.12+)
- **LLM Orchestration**: Instructor + Pydantic (Deterministic JSON)
- **Quality**: Strict MyPy typing + Ruff
- **Infrastructure**: PostgreSQL + Redis + ARQ
- **Observability**: Prometheus + Structlog

---

## 📊 Professional Integrity Audits

Need a deep-dive into your team's commitment reliability? I offer **one-time AI-powered audits** for remote engineering teams. 

- **Extract "Shadow Debt"**: Identify technical promises made in commits that never made it to a PR.
- **Predict Burnout**: Recognize linguistic patterns of fatigue before they impact velocity.
- **Reliability Scoring**: Get a multi-dimensional scorecard for your squads.

📧 **[Contact me for an Audit](mailto:adelekedare2012@gmail.com)** to see a sample report and book a 1-hour squad analysis.

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
