# Ethics, Privacy & Professionalism 🛡️

CommitGuard AI is a high-pressure accountability tool, but it is built with the **"Supportive First"** philosophy. Addressing feedback on the human implications of AI-driven enforcement is critical for enterprise adoption.

---

## 1. Ethical Tone Escalation
One of our most discussed features is the **"Confrontational"** tone. Here is how we handle it ethically:

*   **The Empathy Buffer**: The system is hardcoded to prioritize `SUPPORTIVE` tones if anything resembling burnout or personal distress is detected.
*   **The Burnout Safety Valve**: If the `ExcuseDetector` identifies signs of fatigue, the system **blocks** confrontational escalation and triggers a "Burnout Alert" for the manager instead. 
*   **Tone Drift & Cooling-off**: To prevent morale fatigue, the system implements **mathematical tone-damping**. If a user receives **3 consecutive "Firm" or "Confrontational" follow-ups**, the logic automatically locks the agent into a `NEUTRAL` or `SUPPORTIVE` state for 48 hours (configurable via `COOLING_OFF_PERIOD_HOURS`).

## 2. Nuanced Hard-Blocking (The "Ethics Firewall")
We explicitly distinguish between "Business Aggression" and "HR Violations." The **Safety Supervisor** enforces a **Semantic Firewall**:
*   **BLOCKED (HR Territory)**: Discussions involving `Salary`, `PIP` (Performance Improvement Plans), `Firing`, or `Legal Threats` are immediately blocked. This is a hard-coded safety guarantee.
*   **ALLOWED (Business Territory)**: Aggressive discussions about `Pricing Models`, `Budgeting`, or `Resource Allocation` are permitted as valid professional discourse.



## 2. Cultural & Contextual Sensitivity
"Deflection" is relative. What is seen as blunt in one culture is polite in another:

*   **Sensitivity Calibration**: CommitGuard supports **Cultural Tone Profiles**. Managers can calibrate the "Pressure Sensitivity" of the agents to match their specific team norms (e.g., High-Directness vs. High-Context locales).
*   **Domain-Specific Jargon**: The NLP models are refined to recognize that certain industry vernacular (e.g., *"I'm swamped"*) may be a routine status update rather than an excuse in specific high-velocity teams.

## 3. Privacy & Data Integrity

Monitoring at the granularity of Slack threads and Git commits requires a strict privacy stance:

*   **Scoped Monitoring**: CommitGuard is designed to monitor designated `#project` channels, not private DMs or unrelated chatter.
*   **Source-Level Only**: Commit monitoring is restricted to commit messages and PR metadata—not the proprietary logic within the source code files themselves.
*   **Identity Anonymization**: Internal IDs are used for analysis; real names can be masked in the database if necessary.

## 3. Handling Ambiguity (The "100% Visibility" Claim) 🧠
Ambiguity is the greatest challenge in Engineering NLP. Here is how we move toward high accuracy:

*   **Confidence Scores**: Every extraction (Commitment, Risk, Excuse) is accompanied by a `confidence_score`.
*   **Human-in-the-Loop (HITL)**: If a score falls below **0.75**, the system flags the extraction as "Ambiguous" and asks the manager for manual validation instead of taking autonomous action.
*   **Semantic Context**: By correlating Git activity with Slack messages, we resolve ambiguity. If a dev says *"I'll handle it,"* but we see a corresponding Git branch with the task name, the "soft commitment" is confirmed.

---

## 🚀 Deployment & The Future
**Why build this?**
CommitGuard was inspired by the "Slack Stall"—the invisible friction where professional promises disappear into the scroll history of remote teams. It turns "I'll get to it" into a technical obligation.

**Real-World Testing**:
The next phase of the project involves a **Private Beta** where the `TruthGapDetector` will be tested against real-world ambiguous data to refine its "Precision Accountability" engine.
