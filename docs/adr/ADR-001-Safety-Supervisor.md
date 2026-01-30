# ADR-001: Safety Supervisor (Semantic Firewall) Design

## Status
Accepted

## Context
CommitVigil AI generates autonomous interventions (messages to users). In enterprise environments (Healthcare, Finance, Tech R&D), these messages can accidentally violate HR policies, leak PII, or give non-compliant advice. A single agent (Brain) might fail to perceive these boundaries due to "jailbreak" attempts or model drift.

## Decision
We implement a **Safety Supervisor** (Semantic Firewall) as a mandatory secondary reasoning layer.

### Key Principles:
1. **Separation of Concerns**: The 'Brain' focuses on accountability; the 'Supervisor' focuses on compliance.
2. **Industry-Specific Rule Injection**: Rules are dynamically fetched from the database based on the user's `industry` and `department`.
3. **Hard Blocking**: High-risk violations (e.g., PII leak, legal liability) trigger an immediate `HARD_BLOCK` which prevents any message from being sent and escalates to a human manager.
4. **Autonomous Onboarding**: If a message belongs to an unknown context, the Supervisor generates temporary rules but flags the entire interaction as "Unverified" (Stabilization Layer).

## Consequences
- **Latency**: Adds ~500ms-1s per evaluation cycle.
- **Safety**: Significantly reduces the risk of AI-generated liability.
- **Complexity**: Requires a well-indexed database and a Redis cache for rule lookup to remain performance-neutral under load.
