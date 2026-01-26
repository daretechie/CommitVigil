# Production & Enterprise Deployment Guide 🚀

Scaling CommitGuard AI to 1000+ users requires moving from a local monolithic setup to a distributed, high-availability architecture.

## 🏗️ Enterprise Architecture

For large-scale teams, we separate the **Ingestion Layer** (API) from the **Processing Layer** (Workers).

1.  **API Layer**: Stateless FastAPI pods behind a Load Balancer (AWS ALB / Nginx).
2.  **Processing Layer**: Distributed `arq` workers scaling horizontally based on queue depth.
3.  **State Layer**: Managed Redis (AWS ElastiCache) and PostgreSQL (AWS RDS).

---

## ☸️ Kubernetes Orchestration

We provide production-ready K8s manifests in [`infra/k8s/`](file:///home/daretechie/DevProject/GitHub/CommitGuard-AI/infra/k8s/).

### Key Scaling Features:
- **Replica Sets**: Run multiple API instances to handle high traffic.
- **Auto-Scaling (HPA)**: Workers automatically scale from **2 to 20+ pods** based on CPU usage or queue backlog.
- **Resource Constraints**: Strict CPU/Memory limits to prevent noisy-neighbor issues on shared clusters.

### Deployment Command:
```bash
kubectl apply -f infra/k8s/
```

---

## 🔄 Automated Org-Wide Ingestion

Managers don't need to manually ingest commits. Use **GitHub Webhooks** at the Organization level:

1.  Go to **GitHub Organization Settings** -> **Webhooks**.
2.  Add a new webhook:
    - **Payload URL**: `https://api.commitguard.yourcloud.com/api/v1/ingest/git`
    - **Content Type**: `application/json`
    - **Secret**: Your fixed `API_KEY_SECRET`
    - **Events**: Select `Pushes`.

**Result**: Every commit from every repo in your organization is automatically processed for accountability.

---

## 🆔 Bulk Identity Sync (SSO)

Mapping 1000+ users via `curl` is inefficient. Implement a **Mapping Sync Service**:

- **Active Directory / Google Workspace**: Write a small cronjob that polls your employee list and calls:
  - `POST /api/v1/users/config/slack` (Email -> Slack ID)
  - `POST /api/v1/users/config/git` (Email -> Git Email)
- **Automatic Discovery**: CommitGuard can be configured to use the Slack `users.lookupByEmail` API to auto-map users on their first commitment.

---

## 📊 Monitoring & Observability

Enterprise deployment includes **Prometheus + Grafana** integration:

- **SLIs (Service Level Indicators)**:
  - `background_jobs_pending`: How many commitments are waiting for AI processing?
  - `ai_token_usage_total`: Cost tracking per team/department.
  - `intervention_acceptance_rate`: How often are managers acting on AI pings?

---

## 💰 FinOps: Optimizing LLM Costs

At 1000+ users, token costs can add up. CommitGuard helps you optimize:

1.  **Provider Switching**: Use **Groq (Llama 3.3 70b)** for high-speed, low-cost extraction, and **OpenAI (GPT-4o)** only for complex tone adaptation.
2.  **Mock Mode for Non-Critical Repos**: Use `LLM_PROVIDER="mock"` for internal experimental repositories to save budget.
3.  **Caching**: CommitGuard can be extended with a vector cache (like RedisVL) to reuse extracted tasks from similar commit messages.

---

> [!IMPORTANT]
> Always deploy in a **Zero-Trust** environment using encrypted secrets and private network VPCs for the Database and Redis.
