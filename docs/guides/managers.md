# The Accountability Handbook: A Guide for Managers 👔

CommitGuard AI is a tool of empowerment, not surveillance. For a Human-in-the-Loop (HITL) system to work, managers must know how to translate AI flags into professional leadership.

---

## 1. Interpreting the Flags
When CommitGuard flags an **"Ambiguity"** or a **"Truth Gap,"** it is a prompt for a conversation, not a citation for failure.

*   **Flag: "Ambiguous Commitment"**
    *   *AI Logic*: The user's words were too vague to extract a deadline.
    *   *Manager Action*: Don't scold. Instead, reply: *"Hey [Name], I saw your update. To help me clear any blockers, could you give me a rough target for when you'll have this in review?"*
    *   *Goal*: Precision, not pressure.

*   **Flag: "Truth Gap Detected"**
    *   *AI Logic*: Verbal claims don't match Git evidence.
    *   *Manager Action*: Assume there is a technical blocker. Ask: *"I noticed the repo hasn't updated since our chat. Are there any local environment issues or merge conflicts I should jump in on?"*
    *   *Goal*: Removing blockers, not investigating honesty.

---

## 2. Managing the "Human-in-the-Loop" (HITL)
High-stakes interventions should never be 100% autonomous.

1.  **Review the Confidence Score**: If the AI has a `confidence_score` of 0.8 but flags a high risk, verify if the user's recent Slack messages were sarcastic or high-context.
2.  **Calibrate for Morale**: If the team has just finished a "Death March" (long sprint), manually increase the **Supportive Threshold** to allow for natural recovery.
3.  **Cross-Cultural Norms**: Ensure your specific team's "Directness Level" is reflected in the agent's tone settings.

---

## 3. Best Practices for Professionalism
*   **Public vs. Private**: CommitGuard monitors public channels, but follow-up interventions for **high-risk signals** should often be moved to a 1-on-1 private DM thread once the manager is alerted.
*   **Celebrate the Reliability**: When someone consistently hits 100% on their Reliability Score, use the report as a basis for formal recognition. Accountability is as much about **Praise** as it is about Progress.
## 4. Configuring Your Team's Voice 🎚️
Managers can adjust the system's "psychological pressure" via environment variables:

*   **`CULTURAL_DIRECTNESS_LEVEL`**: Set to `low` for high-context or sensitive teams. This forces the LLM to use more indirect, softer language even when flagging risks.
*   **`COOLING_OFF_PERIOD_HOURS`**: Adjust the duration of the "Tone Damping" state (Default: 48 hours).

---

## 5. The Performance Integrity Audit 📊
Managers can now generate high-value, professional audit reports for their team members. This is the primary tool for quarterly reviews or high-stakes interventions.

### How to Generate a Sellable PDF:
1.  **Request the Audit**: Call the API with `report_format=html`.
2.  **Save as PDF**: Open the HTML file in your browser and use **Print to PDF**.
3.  **Deliver**: The report features a "Truth Gap" analysis and a "burnout risk" scorecard designed for professional executive presentation.

> [!TIP]
> Use the **Markdown** format for embedding audit summaries directly into GitHub Pull Request comments for collective accountability.
