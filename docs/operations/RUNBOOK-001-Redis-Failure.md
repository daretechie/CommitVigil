# RUNBOOK-001: Handling Redis Connection Failures

## Overview
Redis is used for Rate Limiting (`fastapi-limiter`) and Background Job Queueing (`arq`). A Redis failure degrades system performance but should not cause a total API blackout.

## Symptoms
- Logs: `redis_connection_failed` warnings.
- API: Returns `503 Service Unavailable` on `/evaluate` endpoints.
- Prometheus: `background_jobs_pending` metrics stop updating.

## Emergency Mitigation

### 1. Identify the Scope
- If **API is up** but **Worker is down**: Commitments will accumulate in Redis. Scale up the `worker` deployment.
- If **Redis is down**: The API will fail to enqueue jobs.

### 2. Manual Recovery (Docker)
```bash
docker compose restart redis
docker compose logs -f redis
```

### 3. Kubernetes Recovery
```bash
kubectl rollout restart deployment commitvigil-redis
```

### 4. Verification Check
Call the health endpoint:
```bash
curl http://localhost:8000/health
```
Verify `"redis": "healthy"` inside the `dependencies` block of the JSON response.

## Post-Failure Analysis
Check Token Usage logs to ensure no duplicate withdrawals occurred during the reconnection window.
