# Slack Integration Guide 💬

Transform the agent into a visible collaborator by bridging it to your Slack workspace.

## 1. Webhook Setup
To receive notifications, you need an **Incoming Webhook URL**:
1.  Go to [Slack API Apps](https://api.slack.com/apps).
2.  Create a new app (from scratch).
3.  Enable **Incoming Webhooks**.
4.  Add a new webhook to your channel and copy the URL.

## 2. Configuration
Add the URL to your `.env`:
```bash
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/T000.../B000.../XXXX..."
```

## 3. User @Mentions (Identity Mapping)
CommitGuard can ping users directly using their **Slack Member ID**.

### How to map a user:
Call the configuration endpoint with the user's Slack ID (found in their Slack Profile -> More -> Copy Member ID):

```bash
POST /users/config/slack?user_id=john_dev&slack_id=U12345678
```

### The Result
When an alert is triggered, Slack turns the ID into a real mention:
> 🔔 **CommitGuard Alert for @John:** Checking in on commitment: fix the CSS bugs
