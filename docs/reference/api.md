# API Reference 📖

CommitVigil provides a clean RESTful interface for all operations.

## 📥 Commitment Ingestion

::: src.api.routes.ingest_raw_commitment
    options:
      show_root_heading: true
      show_source: false

## 🚦 Accountability Evaluation

::: src.api.routes.evaluate_commitment
    options:
      show_root_heading: true
      show_source: false

## ⚙️ User Configuration

::: src.api.routes.map_slack_user
    options:
      show_root_heading: true
      show_source: false

## 📊 Performance Audits

::: src.api.routes.get_performance_audit
    options:
      show_root_heading: true
      show_source: false

### Exporting Reports
The audit endpoint supports three formats via the `report_format` query parameter:
- **`json`** (Default): Standard API response for integration.
- **`markdown`**: A structured document ready for GitHub or Jira.
- **`html`**: A premium, "PDF-ready" glassmorphic design for professional delivery.

## 🔄 Continuous Learning
::: src.api.routes.log_safety_feedback
    options:
      show_root_heading: true
      show_source: false

---
*Built for High-Performance Teams and Elite Portfolios. 🛡️🚀*
