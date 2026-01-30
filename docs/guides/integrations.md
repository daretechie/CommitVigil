# Integration & Pluggability Guide 🔌

CommitVigil is designed with a **"Source-Agnostic"** core. While Slack and Git are the primary supported platforms, the system can be easily extended to any tool that supports Webhooks or REST APIs.

---

## 1. Inbound Ingestion (Incoming Data)
The system can ingest commitments from any source via the `/api/v1/ingest/raw` endpoint.

### Examples:
*   **Jira**: Set up a Jira Webhook that triggers on "Issue Commented" and send the comment body to CommitVigil.
*   **Linear**: Sync Linear comments to track engineering promises made in task descriptions.
*   **Calendly**: Map calendar bookings to commitments (e.g., "I will have the demo ready by the meeting time").

### How to Implement:
Simply call the endpoint with the raw text and a `user_id`:
```bash
curl -X POST "$API_URL/api/v1/ingest/raw?user_id=john_dev&raw_text=I promise to fix the DB by Friday"
```

---

## 2. Outbound Notifications (Interventions)
Currently, CommitVigil uses the `SlackConnector` for follow-ups. However, the architecture is modular.

### Adding a New Tool (e.g., MS Teams or Discord):
1.  **Create a Connector**: Add a new file in `src/core/` (e.g., `teams.py`) following the `SlackConnector` pattern.
2.  **Update the Worker**: In `src/worker.py`, update the `send_follow_up` function to route messages to your new connector:

```python
# src/worker.py
async def send_follow_up(user_id: str, message: str, slack_id: str | None = None, teams_webhook: str | None = None):
    if teams_webhook:
        await TeamsConnector.send(message, teams_webhook)
    else:
        await SlackConnector.send_notification(message, slack_id)
```

---

## 3. The "Tool-Agnostic" Brain
The core reasoning engine (`CommitVigilBrain`) never interacts with Slack or Git directly. It processes **semantic commitments** and returns **behavioral decisions**. This means you can swap the entire communication layer without touching the AI logic.

### Supported Data Formats:
*   **JSON API**: For direct application integration.
*   **Markdown**: For documentation and PR reviews.
*   **HTML**: For executive reporting.

---

## 🚀 Future Golden Paths
*   **Jira Adapter**: Automatically close Jira tickets when the "Fulfillment Analysis" confirms the task is done in Git.
*   **Email Gateway**: Send "Professional Nudges" via SendGrid for high-context executive summaries.
