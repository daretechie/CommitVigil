# Agentic Reasoning Logic 🧠

CommitVigil uses three distinct layers of reasoning to decide how to intervene.

## 1. Excuse Analysis (`ExcuseDetector`)
The agent categorizes the check-in sentiment:
- **Legitimate**: Family emergencies, personal health.
- **Deflection**: "Too busy," "I forgot," "I'll do it later."
- **Burnout Signal**: Linguistic markers of deep fatigue or loss of interest.

## 2. Predictive Risk Scoring (`RiskScorer`)
The agent generates a score (0.0 - 1.0) based on:
- The **Confidence** of the current check-in.
- The **Historical Reliability** of the user (stored in PostgreSQL).
- The **Category** of the excuse.

## 3. Tone Adaptation (`ToneAdapter`)
The final decision is a personalized intervention:
- **Tone: Supportive** - If risk is high but burnout is detected.
- **Tone: Firm** - If risk is high and the user has a history of deflection.
- **Tone: Neutral** - For standard updates.
- **Tone: Confrontational** - For repeat deflection.

## 4. Safety Audit (`SafetySupervisor`)
The "Overwatch" layer acts as a final sanity check before any intervention is sent. It enforces the **Industry-Specific Semantic Firewall**:
- **Departmental Granularity**: Applies rules specific to `Finance:Trading` or `Tech:R&D` before falling back to industry-wide policies.
- **Autonomous Onboarding**: If a new organizational context is detected, the agent generates preliminary safety rules and flags them for human review.
- **Healthcare (HIPAA)**: Hard-blocks unauthorized PII or clinical mandates.
- **Finance (SEC)**: Prevents market manipulation or non-compliant financial advice.

## 5. Context Sensing (`ContextScout`)
A specialized agent that continuously analyzes communication patterns to detect the operational environment:
- **Industry & Department**: Automatically identifies if a user is in "Legal", "Engineering", or "Sales".
- **Confidence Scoring**: Assigns a 0-100% confidence to every detection.
- **Stabilization**: If confidence is low or the context is new, it triggers a **Human-in-the-Loop** verification request.


## 5. Cultural Persona Architecture
CommitVigil adapts the **ToneAdapter** to the cultural context of the user:
- **Japanese (`ja`)**: High-context, polite, and face-saving interventions.
- **German (`de`)**: Direct, technical, and objective accountability.
- **African Ubuntu (`en-AF`)**: Communal, relationship-centric, and narrative-driven check-ins.
- **British (`en-UK`)**: Nuanced, polite persistence.

---

### Example Decision
> **Input**: *"I'm really tired, the bugs are harder than I thought, might miss it."*
>
> **Agent Decision**:
> - **Category**: Burnout Signal
> - **Risk**: High (0.85)
> - **Tone**: Supportive
> - **Action**: *"Hey @User, I'm detecting some burnout signs. Let's look at the scope together before the deadline."*
