# CommitVigil: The Accountability Specialist 🛡️

![CommitVigil Hero](assets/hero.jpg)


> **"I provide 'Accountability as a Service.' My agent predicts when a team member is likely to fail *before* the deadline and intervenes with the right behavioral tone to ensure delivery."**

## 🆘 The Problem
In modern distributed teams, the **"Slack Stall"** is the #1 drain on project velocity. Project Managers are overwhelmed by vague promises like *"I'll get to it soon,"* which are often forgotten, leading to missed sprints and "bad guy" escalations.

## ✅ The Solution
CommitVigil is a standalone, agentic service designed to monitor and enforce professional commitments. Every commitment passes through a **4-Stage Reasoning Pipeline**:

1.  **Extraction**: Automatically parses Slack threads or Git commits to identify {who, what, when}.
2.  **Excuse Analysis**: Categorizes sentiment (Legitimate vs. Deflection vs. Burnout).
3.  **Risk Scoring**: Quantifies failure probability based on historical reliability.
4.  **Safety Overwatch**: Audits interventions for ethics, tone drift, and HR compliance.
5.  **Professional Reporting**: Generates high-impact "Integrity Audits" for management reviews.

---

## 🏗️ Architecture at a Glance
CommitVigil is built on a **Decoupled Event-Driven Architecture**:
- **FastAPI Entrypoint**: High-speed ingestion for Slack and Git webhooks.
- **Redis & ARQ**: Distributed background processing for high-volume orchestration.
- **The Brain**: Multi-agent LLM reasoning loop.
- **PostgreSQL**: Industrial-grade persistence with atomic row-locking for score integrity.
