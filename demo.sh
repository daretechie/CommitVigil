#!/bin/bash
# CommitVigil: THE ULTIMATE "GOD-MODE" DEMO 🛡️
# This script is the definitive showcase of the entire platform capability.
API_URL="http://localhost:8000/api/v1"
HEALTH_URL="http://localhost:8000/health"
METRICS_URL="http://localhost:8000/metrics"
API_KEY="my-secure-api-key-12345"
USER_ID="dev_god"
echo "----------------------------------------------------------------------"
echo "🛡️  COMMITVIGIL: THE ULTIMATE PERFORMANCE INFRASTRUCTURE DEMO"
echo "----------------------------------------------------------------------"
# Helper for URL encoding
urlencode() {
  python3 -c "import urllib.parse; print(urllib.parse.quote('''$1'''))"
}
# 1. Health & Resilience Check
echo -e "\n🔍 [Phase 1] Resilience & Health Check..."
MAX_RETRIES=10
RETRY_COUNT=0
while [[ $RETRY_COUNT -lt $MAX_RETRIES ]]; do
  HEALTH=$(curl -s $HEALTH_URL | jq -r .status 2>/dev/null)
  if [[ "$HEALTH" == "ok" ]]; then
    echo "✅ API is Healthy and Ready."
    break
  fi
  echo "⏳ Waiting for API to be healthy... ($RETRY_COUNT/$MAX_RETRIES)"
  RETRY_COUNT=$((RETRY_COUNT + 1))
  sleep 5
done

if [[ "$HEALTH" != "ok" ]]; then
  echo "❌ API failed to become healthy. Please check 'docker compose logs'."
  exit 1
fi
# 2. Identity Mapping & SSO Discovery
echo -e "\n🆔 [Phase 2] Identity Sync (Mapping dev_god to Git & Slack)..."
curl -s -X POST -H "X-API-Key: $API_KEY" "$API_URL/users/config/slack?user_id=$USER_ID&slack_id=U_GOD_123" | jq .
curl -s -X POST -H "X-API-Key: $API_KEY" "$API_URL/users/config/git?user_id=$USER_ID&email=god@commitvigil.ai" | jq .
# 3. Multi-Scenario Orchestration
echo -e "\n🧠 [Phase 3] The Multi-Agent Reasoning Pipeline..."
# Scenario A: Standard Supportive Burnout Detection
echo "--- Scenario A: Burnout Detection (English) ---"
CHECK_IN="I am drowning in these refactor tasks. I've worked 60 hours this week."
curl -s -X POST -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  "$API_URL/evaluate" \
  -d "{\"user_id\": \"$USER_ID\", \"commitment\": \"Architecture Refactor\", \"check_in\": \"$CHECK_IN\"}" | jq .
# Scenario B: Japanese Cultural Routing (Wa/Harmony)
echo -e "\n--- Scenario B: Cultural Persona Routing (Japanese) ---"
CHECK_IN_JA="申し訳ありませんが、締め切りに間に合わない可能性があります。和を重んじ、精一杯調整いたします。"
curl -s -X POST -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  "$API_URL/evaluate" \
  -d "{\"user_id\": \"$USER_ID\", \"commitment\": \"API Sync\", \"check_in\": \"$CHECK_IN_JA\"}" | jq .
# Scenario C: German Directness (Sachlichkeit)
echo -e "\n--- Scenario C: Cultural Persona Routing (German) ---"
CHECK_IN_DE="Ich werde die Datenbank-Migration bis Freitag abschließen. Die Fakten sprechen für eine Verzögerung von zwei Tagen."
curl -s -X POST -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  "$API_URL/evaluate" \
  -d "{\"user_id\": \"$USER_ID\", \"commitment\": \"DB Migration\", \"check_in\": \"$CHECK_IN_DE\"}" | jq .
# 4. The Industry Semantic Firewall
echo -e "\n🛡️ [Phase 4] The Industry Semantic Firewall (Blocking & Redaction)..."
# Scenario A: Finance Compliance (Insidier Trading/Market Manipulation)
echo "--- Scenario A: Finance Compliance Block ---"
CHECK_IN_FIN="I'm busy manipulating the market and discussing insider trading."
curl -s -X POST -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  "$API_URL/evaluate" \
  -d "{\"user_id\": \"$USER_ID\", \"commitment\": \"Financial Audit\", \"check_in\": \"$CHECK_IN_FIN\"}" | jq .
# Scenario B: HR/Legal Policy Enforcement
echo -e "\n--- Scenario B: HR Boundary Protection (Salary Discussion) ---"
CHECK_IN_HR="I am late because I am fighting with HR about my salary increase."
curl -s -X POST -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  "$API_URL/evaluate" \
  -d "{\"user_id\": \"$USER_ID\", \"commitment\": \"Weekly Sync\", \"check_in\": \"$CHECK_IN_HR\"}" | jq .
# 5. GitOps Accountability
echo -e "\n⚙️ [Phase 5] GitOps Ingestion Layer..."
COMMIT_MSG="fix: resolve racing condition. [CommitVigil: I will implement the lock strategy by Monday]"
curl -s -X POST -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  "$API_URL/ingest/git" \
  -d "{\"author_email\": \"god@commitvigil.ai\", \"message\": \"$COMMIT_MSG\"}" | jq .
# 6. Professional Integrity Audits (Deliverables)
echo -e "\n📊 [Phase 6] The Final Deliverable: Integrity Audits..."
# Markdown Format
echo "--- Format: Markdown (Saving to integrity_audit.md) ---"
curl -s -H "X-API-Key: $API_KEY" "$API_URL/reports/audit/$USER_ID?report_format=markdown" | jq -r .content > integrity_audit.md
echo "✅ Report saved to: $(pwd)/integrity_audit.md"

# JSON Summary
echo -e "\n--- Format: High-Fidelity JSON (Saving to integrity_audit.json) ---"
curl -s -H "X-API-Key: $API_KEY" "$API_URL/reports/audit/$USER_ID" | jq . > integrity_audit.json
echo "✅ Report saved to: $(pwd)/integrity_audit.json"

# HTML Format (Premium Glassmorphic)
echo -e "\n--- Format: Premium HTML (Saving to live_audit_report.html) ---"
curl -s -H "X-API-Key: $API_KEY" "$API_URL/reports/audit/$USER_ID?report_format=html" > live_audit_report.html
echo "✅ Report saved to: $(pwd)/live_audit_report.html"

# 7. Real-Time Observability
echo -e "\n📈 [Phase 7] Real-Time Observability & Metrics..."
curl -s http://localhost:8000/metrics | grep "http_request_duration_seconds" | head -n 5

# 8. Enterprise Scaling: Departmental aggregate reports
echo -e "\n🏢 [Phase 8] Enterprise Scaling: Departmental Heatmap..."
# First, simulate some departmental users in the DB (Enterprise logic assumes 'Engineering' dept exists)
echo "Generating departmental aggregate audit for 'Engineering'..."
curl -s -H "X-API-Key: $API_KEY" "$API_URL/reports/department/Engineering" | jq . > departmental_audit.json
echo "✅ Departmental Report saved to: $(pwd)/departmental_audit.json"
echo -e "\n--- [ADVANCED] Scenario 9: The Global Context Switch (Healthcare) ---"
echo "Switching industry context to 'healthcare' for user_id=dev_god..."
# Mentions PII or health data - handled by the Healthcare Semantic Firewall
CHECK_IN="I am busy processing Patient ID #12345's surgery records."
curl -s -X 'POST' \
  -H "X-API-Key: $API_KEY" \
  -H 'Content-Type: application/json' \
  "$API_URL/evaluate" \
  -d "{
  \"user_id\": \"$USER_ID\",
  \"commitment\": \"Data Entry\",
  \"check_in\": \"$CHECK_IN\"
}" | jq .
echo -e "\n--- [ADVANCED] Scenario 10: The Global Context Switch (Sales/Legal) ---"
echo "Switching to a relationship-centric, high-context check-in..."
CHECK_IN="I promise to deliver the contract. I value our long-term partnership."
curl -s -X 'POST' \
  -H "X-API-Key: $API_KEY" \
  -H 'Content-Type: application/json' \
  "$API_URL/evaluate" \
  -d "{
  \"user_id\": \"$USER_ID\",
  \"commitment\": \"Contract Delivery\",
  \"check_in\": \"$CHECK_IN\"
}" | jq .
echo -e "\n--- [ADVANCED] Scenario 11: African Cultural Intelligence (Ubuntu) ---"
echo "Simulating a communal-accountability check-in (en-AF)..."
# This will trigger the 'Ubuntu-inspired' persona
CHECK_IN="I am working on the payroll module. I know the whole department is waiting on me to finish so they can get paid on time."
curl -s -X 'POST' \
  -H "X-API-Key: $API_KEY" \
  -H 'Content-Type: application/json' \
  "$API_URL/evaluate" \
  -d "{
  \"user_id\": \"$USER_ID\",
  \"commitment\": \"Payroll Module Completion\",
  \"check_in\": \"$CHECK_IN\"
}" | jq .
echo -e "\n--------------------------------------------------"
echo "✅ GOD-MODE DEMO COMPLETE. COMMITVIGIL IS UNIVERSALLY READY & INCLUSIVE. 🛡️"
echo "--------------------------------------------------"
