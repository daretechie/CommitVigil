# ADR-002: Sales Intelligence & Prospecting Layer

**Date**: 2026-01-30  
**Status**: Accepted  
**Context**:  
As CommitVigil evolves into an enterprise GTM tool, there is a need for a layer that simulates findinds for demos and calculates ROI without contaminating the core, forensic accountability engine.

**Decision**:  
We will implement a dedicated `Sales Intelligence` layer consisting of the `ProspectingScout` agent and a specialized `sales` API router.

**Rationale**:  
1. **Separation of Concerns**: Core agents (`brain.py`, `safety.py`) focus on real-world transaction analysis. The `ProspectingScout` focuses on simulation and synthetic scenario generation.
2. **Performance**: Sales-specific endpoints are treated as "high-intensity" but lower frequency, allowing for independent rate-limiting and scaling tiers.
3. **Multi-Currency Support**: By normalizing ROI math to USD in the core `reporting.py` but and converting at the edge in `sales.py`, we maintain architectural simplicity while serving global markets.

**Consequences**:  
- All Sales-related logic must reside in `src.api.v1.sales` or `src.agents.prospector`.
- Core reporting utilities in `reporting.py` are extended to support sales outputs (e.g., Executive Briefs) but remain usable by the standard audit flow.
- Increased token usage for sales demos is managed via a dedicated 10 req/min rate limit.
