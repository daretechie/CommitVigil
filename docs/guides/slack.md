# Slack Integration Guide 💬

Transform the agent into a visible collaborator by bridging it to your Slack workspace.

## 1. Webhook Setup (Step-by-Step)

### Step 1: Access Slack API
1. Open your browser and navigate to **[api.slack.com/apps](https://api.slack.com/apps)**
2. Sign in with your Slack workspace credentials if prompted

### Step 2: Create a New App
1. Click the green **"Create New App"** button
2. Select **"From scratch"** (not from a manifest)
3. Fill in the form:
   - **App Name:** `CommitVigil` (or any name you prefer)
   - **Pick a workspace:** Select your Slack workspace from the dropdown
4. Click **"Create App"**

### Step 3: Enable Incoming Webhooks
1. After creating the app, you'll land on the **Basic Information** page
2. In the left sidebar under **"Features"**, click **"Incoming Webhooks"**
3. Toggle the switch **ON** at the top of the page
4. You'll see a confirmation: *"Incoming Webhooks are On"*

### Step 4: Add Webhook to Channel
1. Scroll down to **"Webhook URLs for Your Workspace"**
2. Click **"Add New Webhook to Workspace"**
3. A popup will ask: *"Where should CommitVigil post?"*
4. Select your target channel (e.g., `#engineering`, `#accountability`)
5. Click **"Allow"**
6. Copy the generated webhook URL:
   ```
   https://hooks.slack.com/services/YOUR_WORKSPACE_ID/YOUR_APP_ID/YOUR_WEBHOOK_TOKEN
   ```

## 2. Configuration

Add the webhook URL to your `.env` file:
```bash
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/WORKSPACE_ID/APP_ID/TOKEN"
```

Restart the service to apply changes:
```bash
docker-compose down && docker-compose up --build
```

## 3. Test the Webhook

Verify connectivity with a simple curl command:
```bash
curl -X POST \
  -H 'Content-Type: application/json' \
  -d '{"text": "🛡️ CommitVigil is connected!"}' \
  'YOUR_WEBHOOK_URL'
```

You should see `ok` in the terminal and the message in your Slack channel.

## 4. User @Mentions (Identity Mapping)

CommitVigil can ping users directly using their **Slack Member ID**.

### How to Find a Slack Member ID
1. Open Slack and go to the user's profile
2. Click **"More"** (three dots)
3. Select **"Copy Member ID"**

### How to Map a User
Call the configuration endpoint:
```bash
curl -X POST \
  -H 'X-API-Key: YOUR_API_KEY' \
  'http://localhost:8000/api/v1/users/config/slack?user_id=john_dev&slack_id=U12345678'
```

### The Result
When an alert is triggered, Slack turns the ID into a real mention:
> 🔔 **CommitVigil Alert for @John:** Checking in on commitment: fix the CSS bugs

---

> [!TIP]
> You can create multiple webhooks for different channels (e.g., `#urgent-alerts` for critical issues, `#commitment-log` for routine tracking).
