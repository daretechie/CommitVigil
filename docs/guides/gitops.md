# GitOps Accountability Guide 🛠️

In the engineering world, commitments aren't just made in Slack; they are made in **Source Code**.

## 🔴 The Problem
Technical debt often accumulates because of "soft promises" made in code comments or commit messages:
- *"TODO: Refactor this DB connector."*
- *"I'll fix this auth bug in the next PR."*
- *"Temporary hack, will clean up tonight."*

These promises "vanish" because no project management tool monitors them.

## 🟢 The Solution: CommitGuard GitOps
CommitGuard monitors your repository at the source level.

### 1. Extraction from Commits
If a commit message contains a promise (Who/What/When), the **CommitmentExtractor** identifies it as a formal obligation. 

> [!NOTE]
> The extractor uses a `commitment_found` flag to identify messages with NO clear task, preventing the agent from hallucinating promises.

```bash
POST /api/v1/ingest/git
Headers: X-API-Key: YOUR_API_KEY
Body:
{
  "author_email": "dev@company.com",
  "message": "Fixing CSS. I promise to refactor the login logic by Friday."
}
```

### 2. Fulfillment Analysis (Slippage)
The **SlippageAnalyst** looks at the subsequent PR. 
*   **The Check**: Did the promised refactor actually happen?
*   **The Result**: If the code doesn't match the promise, the agent flags **"Shadow Debt"** and alerts the team.

### 3. Truth Gap Detection
When you provide a check-in via Slack, CommitGuard cross-references it with your recent Git activity.
*   **User**: *"I'm almost done refactoring."*
*   **Git**: *0 lines changed in 48 hours.*
*   **Agent**: *"I noticed no code changes. Is there a blocker I can help with?"* (Tone: Supportive but firm).
### 4. Identity Mapping (Crucial Step)
To link your Git commits to your Slack profile, you must map your email to your user ID:

```bash
curl -X POST \
  -H 'X-API-Key: YOUR_API_KEY' \
  'http://localhost:8000/api/v1/users/config/git?user_id=Daretechie&email=your-email@example.com'
```

Once mapped, `identity_matched` will return `true` in ingest responses, and the agent will know exactly who to ping in Slack.

---

> [!TIP]
> Use the same `user_id` across both Slack and Git mapping to ensure a unified accountability profile.
