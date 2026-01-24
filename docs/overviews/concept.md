# The Accountability Specialist Concept 🛰️

CommitGuard AI is designed around a single philosophical pillar: **Human accountability is the hardest thing to automate, so we built an agent that handles the emotional labor for you.**

## 🎯 The Portfolio Angle
This project isn't just a "wrapper." It demonstrates:
- **Agentic Workflows**: Decisions are not hardcoded if/else statements; they are reasoned by LLMs based on historical context.
- **Stateful Intelligence**: The system "remembers" user behavior across sessions.
- **Enterprise Hardening**: Built with industrial standards (PostgreSQL, Redis, Ruff, 90%+ Testing).

## 🛠️ Operational Workflow
1.  **Ingestion**: A manager pings an endpoint with raw Slack text.
2.  **extraction**: The agent identifies the human owner and the commitment details.
3.  **Monitoring**: The background worker schedules a "Heartbeat Check."
4.  **Intervention**: If the check-in sounds risky, the agent pings the user on Slack.
