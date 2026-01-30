# Manager Guide: Human-In-The-Loop (HITL) Feedback Loop

## Overview
CommitGuard AI's "Safety Supervisor" monitors all communications. Sometimes, the AI might be too strict (e.g., blocking a legitimate technical discussion) or too lenient. The Feedback Loop allows managers to override AI decisions, which in turn trains the underlying model.

## How it Works
1. When an intervention is triggered (Block or Correction), it is logged with a unique `intervention_id`.
2. A manager reviews the audit trail via the Dashboard or API.
3. The manager submits feedback (Accept, Reject, or Modify).

## API Integration
To submit feedback via the API, use the `POST /api/v1/feedback/safety` endpoint.

### Example Request
```json
{
  "intervention_id": "uuid-1234-5678",
  "user_id": "dev_rockstar",
  "manager_id": "manager_alice",
  "action_taken": "accepted",
  "final_message_sent": "I understand you're busy, let's sync on Monday.",
  "comments": "Correction was perfect, helped maintain professional tone."
}
```

## Dashboard Usage
1. Navigate to the **Safety Audit Console**.
2. Filter for "Pending Review" or "Recent Interventions".
3. Click **Accept** or **Edit & Send**.

## Impact on Reliability Score
Rejecting an AI failure detection might restore a user's reliability score if the "failure" was incorrectly flagged by the agent.

## Continuous Learning
The AI recalibrates its `min_confidence_threshold` based on the **Manager Acceptance Rate**. If managers frequently reject interventions in a specific department, the "Supervisor" becomes more conservative in that context.
