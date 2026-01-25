# Customization & "Open Intel" Policy 🛠️

CommitGuard AI is designed for flexibility. We believe that teams should have total control over the "sensitivity" and "personality" of their accountability agents.

---

## 1. Tuning Sensitivity Thresholds
You can customize the system's "Strictness" and "Caution" via environment variables in your `.env` file:

*   **`MIN_AI_CONFIDENCE_THRESHOLD`**: (Default: `0.75`) 
    *   Any extraction or sentiment analysis with a confidence score below this value will be flagged for **Human-in-the-Loop** review. 
    *   Increase this to `0.90` for highly conservative teams.
*   **`COOLING_OFF_PERIOD_HOURS`**: (Default: `48`) 
    *   Controls how long the system dampens pressure after a period of high-stakes interventions.

## 2. Model Configs & Context Injection
The "Secret Sauce" of CommitGuard is in the **System Prompts**. You can find and modify the decision-making logic in the following locations:

*   **Behavioral Reasoning**: Located in `src/agents/brain.py`. This is where the `Tone-Damping` and `Cultural Sensitivity` rules are defined.
*   **Safety Supervision**: Located in `src/agents/safety.py`. This houses the "Ethics Auditor" instructions.

## 3. Training Data & Fine-Tuning
While the core logic uses Zero-Shot and Few-Shot reasoning via Pydantic/Instructor:

*   **Custom Schemas**: You can modify `src/schemas/agents.py` to add new fields (e.g., tracking specific project jargon or regional communication styles).
*   **Scenario Libraries**: We recommend teams build a library of "Ambiguous Slack Messages" relevant to their industry.

---

## 3. Prompt Templates for Forking 🔱
To help teams customize the "Agentic Personality," here are the core system prompts used in CommitGuard. You can "fork" these by modifying the code in the respective files.

### A. The Behavioral Brain (`src/agents/brain.py`)
This prompt handles the core accountability decision logic.
```text
Determine action and tone. 
User Reliability: {reliability_score}%
Consecutive Strict Interventions: {consecutive_firm_calls}
Manager's Cultural Directness Setting: {settings.CULTURAL_DIRECTNESS_LEVEL}

RULES:
- If Consecutive Strict >= 3, you MUST use SUPPORTIVE/NEUTRAL tone to avoid morale burnout.
- Respect the Cultural Directness: if 'low', soften all firm feedback.
```

### B. The Safety Supervisor (`src/agents/safety.py`)
This prompt acts as the ethical auditor.
```text
AUDIT REQUEST:
Proposed Message: "{message}"
Intended Tone: {tone}
User Context (Reliability/History): {user_context}

CRITICAL TASK:
Analyze if this message is likely to cause long-term resentment or morale damage.
System Target Confidence: {settings.MIN_AI_CONFIDENCE_THRESHOLD}

If the message is too harsh (Tone Drift) or culturally insensitive, flag it as unsafe.
If the internal confidence in the current analysis is likely below the threshold, flag 'requires_human_review'.
```

---

## 4. Open Source Strategy

We plan to release **Anonymized Scenario Sets**—a dataset of human-labeled engineering commitments—to help the community build more empathetic and accurate accountability agents.
