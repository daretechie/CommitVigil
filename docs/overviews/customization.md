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
*   **Scenario Libraries**: We recommend teams build a library of "Ambiguous Slack Messages" relevant to their industry to help refine their local instance of the `CommitmentExtractor`.

---

## 📦 Open Source Strategy
We plan to release **Anonymized Scenario Sets**—a dataset of human-labeled engineering commitments—to help the community build more empathetic and accurate accountability agents.
