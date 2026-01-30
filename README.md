# CommitVigil: The Autonomous Accountability Platform 🛡️

![CommitVigil Hero](docs/assets/hero.jpg)

<!-- Badges: Enterprise Metrics -->
[![Tests](https://github.com/daretechie/CommitVigil/actions/workflows/ci.yml/badge.svg)](https://github.com/daretechie/CommitVigil/actions/workflows/ci.yml)
![Throughput](https://img.shields.io/badge/throughput_benchmark-1250%20msg%2Fsec-blue?style=for-the-badge)
![Latency](https://img.shields.io/badge/target_P95_latency-<500ms-success?style=for-the-badge)
![Cost Savings](https://img.shields.io/badge/avg_token_savings-85%25-orange?style=for-the-badge)
![ROI](https://img.shields.io/badge/est_net_ROI-%24558%2Fmonth-gold?style=for-the-badge)
![Security](https://img.shields.io/badge/Security-Audit_Passed-success?style=for-the-badge)
![Test Coverage](https://img.shields.io/badge/Coverage-85%25-success?style=for-the-badge)

> **"The truth lives in the code. Accountability vive in the engine."**

[**Full Documentation 📚**](https://daretechie.github.io/CommitVigil/) | [**Live Site 🌐**](https://daretechie.github.io/CommitVigil/) | [**Safety Validation Report 🛡️**](https://daretechie.github.io/CommitVigil/validation/safety_validation_report/) | [**Manager Feedback Guide 🎮**](docs/guides/feedback_loop.md) | [**Integration Guide 🔌**](docs/guides/integrations.md)

---

## 🆘 The Problem
In modern distributed teams, the **"Slack Stall"** is the #1 drain on project velocity. 
Managers are overwhelmed by vague promises—*"I'll get to it soon,"* or *"It's almost done"*—which are often forgotten or delayed, leading to missed sprints and expensive "bad guy" escalations.

## ✅ The Solution
CommitVigil is a standalone, AI-powered **Accountability Specialist**. It doesn't just "monitor"—it **predicts** failure before it happens by mapping verbal commitments in Slack/Teams to actual technical reality in Git/Jira.

### 🎯 The "Truth-Gap" Engine
Our multi-agent system extracts {who, what, when} from conversations and cross-references them with technical metadata to identify:
*   **Burnout Signals**: Spotting over-commitment before it leads to regression.
*   **Commitment Drift**: Quantifying the delta between "what was promised" and "what was pushed."
*   **Behavioral Nudges**: Automatically adapting intervention tone based on culture and urgency.

---

## 💼 Hire for "Integrity Audit" Services
Want to verify your team's velocity before a major release or acquisition? I offer specialized **Accountability Consulting** using this CommitVigil engine:
*   **Forensic Audits**: Truth-gap detection between Slack/Jira and Git reality.
*   **Burnout Prevention**: Strategic agentic follow-ups to protect at-risk developers.
*   **Boardroom Reporting**: Professional, glassmorphic HTML ROI briefs for C-level visibility.

[**Inquire on Upwork 🚀**](https://www.upwork.com/)

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

### 🛡️ 2026 Enterprise Upgrade: Autonomous Adaptation
The system now includes self-evolving capabilities for global operations:
- **Autonomous Context Sensing**: Automatically detects **Industry** (e.g., Gaming, Biotech) and **Department** (e.g., R&D, Sales) from communication patterns.
- **Hierarchical Safety Enforcement**: Applies rules from specific (Department) to broad (Industry) to generic.
- **Stabilization Layer**: Autonomous rules start as **Unverified** and trigger Human-in-the-Loop review. Once confirmed, context is **Locked** for stability.
- **Cultural Persona Routing**: Automatically adapts tone for **Japanese (*Wa*)**, **German (*Sachlichkeit*)**, **French (Eloquence)**, **British English**, and **Spanish**.


## 🏗️ The Four-Stage Autonomous Pipeline
Every commitment—whether from Slack or a Git Commit—passes through a deterministic reasoning loop:

1.  **Excuse Detection (`ExcuseDetector`)**: Classifies sentiment (Legitimate vs. Deflection vs. Burnout).
2.  **Predictive Risk Assessment (`RiskScorer`)**: Quantifies failure probability based on historical reliability.
3.  **Language & Culture Router**: Identifies the primary language and selects the appropriate cultural persona.
4.  **Safety Supervisor (`Overwatch`)**: Audits final communications for HR/Legal ethics and **Industry-Specific Semantic Compliance**.

### 💼 Phase 6: Enterprise Sales Intelligence (New)
Transform your security audit into a revenue engine.
- **Automated Prospecting**: The `ProspectingScout` agent generates realistic "Drift Scenarios" for demos based on industry (e.g., Finance, Energy).
- **Multi-Currency ROI**: Interactive calculator for predicting savings in USD, EUR, and GBP.
- **Executive Briefs**: Generates premium HTML one-pagers for C-Level meetings.

---

## 🛠️ Core Tech Stack
- **Framework**: FastAPI (Python 3.12+)
- **LLM Orchestration**: Instructor + Pydantic (Deterministic JSON)
- **Quality**: Strict MyPy typing + Ruff
- **Infrastructure**: PostgreSQL + Redis + ARQ
- **Observability**: Prometheus + Structlog

---

## 📂 Project Structure

```text
CommitVigil/
├── src/                # Core Application Logic
├── tests/              # Comprehensive Test Suite
├── infra/              # Infrastructure & Config (Prometheus, K8s, migrations)
├── scripts/            # Ops & Demo Utilities (demo.sh)
├── docs/               # Technical Documentation & ADRs
└── README.md           # This document
```


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
## 🤝 Contributing
CommitVigil is open source! We welcome contributions to our "Truth-Gap" engine and cultural personas. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Built for High-Performance Teams and Elite Portfolios.*
