# Behavioral vs. GitOps Accountability 🎭

CommitGuard AI is built as a **Dual-Mode Platform**. While the internal engine (the "Brain") is a single set of standardized agents, it can be applied to two very different high-value problems.

---

## 1. Behavioral Accountability (Chat & Management)
**Target**: Project Managers, CEOs, and Distributed Team Leads.
**Focus**: The "Human Layer."

In this mode, CommitGuard monitors natural language communication (Slack, Discord, Teams).
- **The Problem**: Users make vague, "soft" promises that are easy to forget.
- **The Intervention**: The agent detects **Burnout** or **Deflection** in follow-up chat messages.
- **Example**: *"I'm really tired, the bugs are harder than I thought, might miss it."* -> **Tone: Supportive.**

---

## 2. GitOps Accountability (Code & CI/CD)
**Target**: CTOs, Tech Leads, and Engineering Managers.
**Focus**: The "Code Layer."

In this mode, CommitGuard monitors commit messages, PR descriptions, and code comments.
- **The Problem**: Developers leave "TODOs" or promises like *"I'll fix this in the next PR"* which accumulate into brittle technical debt.
- **The Intervention**: The agent extracts these promises from the source level and maps them to the developer's Git identity.
- **Example**: *"Fixing auth logic. I'll refactor the DB connector by Friday."* -> **Commitment Extracted.**

---

## 🏗️ The Unified Engine
Both modes leverage the same high-tier infrastructure:
1.  **Ingestion API**: Generic endpoints that handle any unstructured text.
2.  **Specialized Agents**: `ExcuseDetector`, `RiskScorer`, and `ToneAdapter`.
3.  **Persistence**: SQLModel saves every interaction to track historical reliability over time.
4.  **Notifications**: Real-world Slack Webhooks with `@mentions`.

**By mastering both modes, CommitGuard AI provides an end-to-end "Accountability as a Service" solution for modern engineering organizations.**
