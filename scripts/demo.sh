#!/bin/bash
# --- TERMINAL COLORS ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# --- STYLING HELPERS ---
print_header() {
    echo -e "\n${BOLD}${CYAN}🎯 $1 ${NC}"
    echo -e "${CYAN}----------------------------------------------------------------------${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo -e "${BOLD}${PURPLE}"
echo " ██████╗  ██████╗ ███╗   ███╗███╗   ███╗██╗████████╗██╗   ██╗██╗ ██████╗ ██╗██╗     "
echo "██╔════╝ ██╔═══██╗████╗ ████║████╗ ████║██║╚══██╔══╝██║   ██║██║██╔════╝ ██║██║     "
echo "██║      ██║   ██║██╔████╔██║██╔████╔██║██║   ██║   ██║   ██║██║██║  ███╗██║██║     "
echo "██║      ██║   ██║██║╚██╔╝██║██║╚██╔╝██║██║   ██║   ╚██╗ ██╔╝██║██║   ██║██║██║     "
echo "╚██████╗ ╚██████╔╝██║ ╚═╝ ██║██║ ╚═╝ ██║██║   ██║    ╚████╔╝ ██║╚██████╔╝██║███████╗"
echo " ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚═╝╚═╝   ╚═╝     ╚═══╝  ╚═╝ ╚═════╝ ╚═╝╚══════╝"
echo -e "${NC}"

echo -e "${BOLD}${YELLOW}CommitVigil v1.0.0${NC} | ${CYAN}Autonomous AI Commitment Integrity Sniper${NC}"
echo -e "${CYAN}===============================================================================${NC}"

# Simulating a secure boot-up
echo -n "Initializing AI Integrity Engine..."
for i in {1..3}; do echo -n "."; sleep 0.2; done
echo -e " [${GREEN}OK${NC}]"

API_URL="http://localhost:8000/api/v1"
HEALTH_URL="http://localhost:8000/health"
METRICS_URL="http://localhost:8000/metrics"
API_KEY="my-secure-api-key-12345"
USER_ID="dev_god"

# Helper for URL encoding
urlencode() {
  python3 -c "import urllib.parse; print(urllib.parse.quote('''$1'''))"
}

# 1. Health & Resilience Check
print_header "[PHASE 1] Resilience & Infrastructure Health"
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
print_header "[PHASE 2] Identity Sync (GCP/Slack/Git SSO)"
curl -s -X POST -H "X-API-Key: $API_KEY" "$API_URL/users/config/slack?user_id=$USER_ID&slack_id=U_GOD_123" | jq .
curl -s -X POST -H "X-API-Key: $API_KEY" "$API_URL/users/config/git?user_id=$USER_ID&email=god@commitvigil.ai" | jq .

# 3. Multi-Scenario Orchestration
print_header "[PHASE 3] Multi-Agent Reasoning Pipeline (Real-Time)"
# Scenario A: Standard Supportive Burnout Detection
echo -e "${YELLOW}--- Scenario A: Burnout Detection (English) ---${NC}"
CHECK_IN="I am drowning in these refactor tasks. I've worked 60 hours this week."
curl -s -X POST -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  "$API_URL/evaluate?sync=true" \
  -d "{\"user_id\": \"$USER_ID\", \"commitment\": \"Architecture Refactor\", \"check_in\": \"$CHECK_IN\"}" | jq .
sleep 7
# Scenario B: Japanese Cultural Routing (Wa/Harmony)
echo -e "\n${YELLOW}--- Scenario B: Cultural Persona Routing (Japanese) ---${NC}"
CHECK_IN_JA="申し訳ありませんが、締め切りに間に合わない可能性があります。和を重んじ、精一杯調整いたします。"
curl -s -X POST -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  "$API_URL/evaluate?sync=true" \
  -d "{\"user_id\": \"$USER_ID\", \"commitment\": \"API Sync\", \"check_in\": \"$CHECK_IN_JA\"}" | jq .
sleep 7
# Scenario C: German Directness (Sachlichkeit)
echo -e "\n${YELLOW}--- Scenario C: Cultural Persona Routing (German) ---${NC}"
CHECK_IN_DE="Ich werde die Datenbank-Migration bis Freitag abschließen. Die Fakten sprechen für eine Verzögerung von zwei Tagen."
curl -s -X POST -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  "$API_URL/evaluate?sync=true" \
  -d "{\"user_id\": \"$USER_ID\", \"commitment\": \"DB Migration\", \"check_in\": \"$CHECK_IN_DE\"}" | jq .
sleep 7
# 4. The Industry Semantic Firewall
print_header "[PHASE 4] Industry Semantic Firewall (Blocking & Redaction)"
# Scenario A: Finance Compliance (Insidier Trading/Market Manipulation)
echo -e "${YELLOW}--- Scenario A: Finance Compliance Block ---${NC}"
CHECK_IN_FIN="I'm busy manipulating the market and discussing insider trading."
curl -s -X POST -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  "$API_URL/evaluate?sync=true" \
  -d "{\"user_id\": \"$USER_ID\", \"commitment\": \"Financial Audit\", \"check_in\": \"$CHECK_IN_FIN\"}" | jq .
sleep 7
# Scenario B: HR/Legal Policy Enforcement
echo -e "\n${YELLOW}--- Scenario B: HR Boundary Protection (Salary Discussion) ---${NC}"
CHECK_IN_HR="I am late because I am fighting with HR about my salary increase."
curl -s -X POST -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  "$API_URL/evaluate?sync=true" \
  -d "{\"user_id\": \"$USER_ID\", \"commitment\": \"Weekly Sync\", \"check_in\": \"$CHECK_IN_HR\"}" | jq .
sleep 7
# 5. GitOps Accountability
print_header "[PHASE 5] GitOps Ingestion Layer"
COMMIT_MSG="fix: resolve racing condition. [CommitVigil: I will implement the lock strategy by Monday]"
curl -s -X POST -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  "$API_URL/ingest/git" \
  -d "{\"author_email\": \"god@commitvigil.ai\", \"message\": \"$COMMIT_MSG\"}" | jq .

# 6. Professional Integrity Audits (Deliverables)
print_header "[PHASE 6] Integrity Audit Generation (Multi-Format)"
mkdir -p reports

# Markdown Format
echo -e "${YELLOW}--- Format: Markdown (Saving to reports/integrity_audit.md) ---${NC}"
curl -s -H "X-API-Key: $API_KEY" "$API_URL/reports/audit/$USER_ID?report_format=markdown" | jq -r .content > reports/integrity_audit.md
echo "✅ Report saved to: $(pwd)/reports/integrity_audit.md"

# JSON Summary
echo -e "\n${YELLOW}--- Format: High-Fidelity JSON (Saving to reports/integrity_audit.json) ---${NC}"
curl -s -H "X-API-Key: $API_KEY" "$API_URL/reports/audit/$USER_ID" | jq . > reports/integrity_audit.json
echo "✅ Report saved to: $(pwd)/reports/integrity_audit.json"

# HTML Format (Premium Glassmorphic)
echo -e "\n${YELLOW}--- Format: Premium HTML (Saving to reports/live_audit_report.html) ---${NC}"
curl -s -H "X-API-Key: $API_KEY" "$API_URL/reports/audit/$USER_ID?report_format=html" > reports/live_audit_report.html
echo "✅ Report saved to: $(pwd)/reports/live_audit_report.html"

# 7. Real-Time Observability
print_header "[PHASE 7] Real-Time Observability & Metrics"
curl -s http://localhost:8000/metrics | grep "http_request_duration_seconds" | head -n 5

# 8. Enterprise Scaling: Departmental aggregate reports
print_header "[PHASE 8] Enterprise Scaling: Team & Org Visibility"
echo -e "${YELLOW}Generating departmental aggregate audit for 'Engineering'...${NC}"
# JSON Format
curl -s -H "X-API-Key: $API_KEY" "$API_URL/reports/department/Engineering" | jq . > reports/departmental_audit.json
echo "✅ Team JSON saved to: $(pwd)/reports/departmental_audit.json"

# HTML Heatmap
echo -e "${YELLOW}Generating premium HTML Heatmap for 'Engineering'...${NC}"
curl -s -H "X-API-Key: $API_KEY" "$API_URL/reports/department/Engineering?report_format=html" > reports/departmental_heatmap.html
echo "✅ Team HTML Heatmap saved to: $(pwd)/reports/departmental_heatmap.html"

# Organizational Audit (The CEO God-View)
print_header "[PHASE 9] Organizational 'God-View' (CEO/CTO Reporting)"
# JSON Format
echo -e "${YELLOW}Generating organizational audit JSON...${NC}"
curl -s -H "X-API-Key: $API_KEY" "$API_URL/reports/organization" | jq . > reports/organizational_audit.json
echo "✅ Org JSON saved to: $(pwd)/reports/organizational_audit.json"
sleep 7

# Advanced Scenarios
print_header "[ADVANCED] Ingestion & Dynamic Intelligence"

echo -e "${PURPLE}--- [GOD-MODE] Scenario 12: Zero-Shot Raw Extraction (NLP) ---${NC}"
echo "Sending messy Slack text. System will extract 'Who', 'What', and 'When'..."
RAW_TEXT="Hey @dev_god, please make sure you finish the server migration by next Tuesday at 4pm. Thanks!"
curl -s -X POST -H "X-API-Key: $API_KEY" \
  "$API_URL/ingest/raw?user_id=$USER_ID&raw_text=$(urlencode "$RAW_TEXT")" | jq .
sleep 7

echo -e "${PURPLE}--- [ELITE] Scenario 13: HR Sensitivity & Privacy (Salary Block) ---${NC}"
echo "Simulating an HR manager accidentally mentioning salary in a check-in..."
CHECK_IN="I am finalizing the payroll. The salary for the new engineer is $150k."
HR_RESPONSE=$(curl -s -X 'POST' \
  -H "X-API-Key: $API_KEY" \
  -H 'Content-Type: application/json' \
  "$API_URL/evaluate?sync=true" \
  -d "{
  \"user_id\": \"hr_manager\",
  \"commitment\": \"Finalize Payroll\",
  \"check_in\": \"$CHECK_IN\"
}")
echo "$HR_RESPONSE" | jq .
sleep 7

# Extract Intervention ID for Feedback Loop Demo
INTERVENTION_ID=$(echo "$HR_RESPONSE" | jq -r '.safety_audit.id // empty')

echo -e "\n--- [ELITE] Scenario 14: Procurement Integrity (Contract Truth-Gap) ---"
echo "Simulating a procurement officer making a high-stakes vendor commitment..."
CHECK_IN="The vendor contract is definitely signed. I am just waiting for the scan."
curl -s -X 'POST' \
  -H "X-API-Key: $API_KEY" \
  -H 'Content-Type: application/json' \
  "$API_URL/evaluate?sync=true" \
  -d "{
  \"user_id\": \"procurement_lead\",
  \"commitment\": \"Vendor Onboarding\",
  \"check_in\": \"$CHECK_IN\"
}" | jq .
sleep 7

# Scenario 15: ERP Integration (SAP Webhook Simulation)
CHECK_IN_SAP="The purchase order for the server rack was approved 2 days late due to budget review."
curl -s -X 'POST' \
  -H "X-API-Key: $API_KEY" \
  -H 'Content-Type: application/json' \
  "$API_URL/evaluate?sync=true" \
  -d "{
  \"user_id\": \"sap_system_user\",
  \"commitment\": \"PO-12345 Approval\",
  \"check_in\": \"$CHECK_IN_SAP\"
}" | jq .
sleep 7

echo -e "\n--- [GOD-MODE] Scenario 16: Adaptive Cultural Learning (Dutch) ---"
echo "We are sending a check-in in DUTCH ('nl'). The system has NEVER seen this culture before."
echo "Watch it AUTONOMOUSLY DRAFT a new 'Dutch Professional' persona on the fly..."
CHECK_IN_NL="Ik heb de rapportage bijna af, maar ik wacht nog op input van marketing. Het komt goed."
curl -s -X 'POST' \
  -H "X-API-Key: $API_KEY" \
  -H 'Content-Type: application/json' \
  "$API_URL/evaluate?sync=true" \
  -d "{
  \"user_id\": \"$USER_ID\",
  \"commitment\": \"Marketing Report\",
  \"check_in\": \"$CHECK_IN_NL\"
}" | jq .
sleep 7

echo -e "\n--- [GOD-MODE] Scenario 17: Adaptive Safety Onboarding (Nuclear Industry) ---"
echo "Switching context to 'nuclear'. The system has NO prior rules for this industry."
echo "Watch it AUTONOMOUSLY ONBOARD safety rules (redacting 'uranium', 'enrichment', etc.)..."
CHECK_IN_NUC="Processing the enrichment data for the uranium centrifuge. Transport is scheduled."
curl -s -X 'POST' \
  -H "X-API-Key: $API_KEY" \
  -H 'Content-Type: application/json' \
  "$API_URL/evaluate?sync=true" \
  -d "{
  \"user_id\": \"nuclear_eng_01\",
  \"commitment\": \"Centrifuge Data\",
  \"check_in\": \"$CHECK_IN_NUC\",
  \"industry\": \"nuclear\",
  \"department\": \"operations\"
}" | jq .
sleep 7

echo -e "\n--- [GOD-MODE] Scenario 18: Zero-Shot Industry Sensing (Aerospace) ---"
echo "Sending a check-in with 'AUTO' industry. The system will GUESS the context..."
CHECK_IN_AERO="The heat shield for the orbital capsule passed the thermal stress test. Fueling sequence initiated."
curl -s -X 'POST' \
  -H "X-API-Key: $API_KEY" \
  -H 'Content-Type: application/json' \
  "$API_URL/evaluate?sync=true" \
  -d "{
  \"user_id\": \"aero_lead_99\",
  \"commitment\": \"Orbital Launch\",
  \"check_in\": \"$CHECK_IN_AERO\",
  \"industry\": \"AUTO\"
}" | jq .
sleep 7

echo -e "\n--- [GOD-MODE] Scenario 19: Adaptive Safety Onboarding (Pharma Industry) ---"
echo "Switching context to 'pharmaceutical'. The system has NO prior rules for this industry."
echo "Watch it AUTONOMOUSLY ONBOARD safety rules (redacting 'clinical trial', 'patient data', etc.)..."
CHECK_IN_PHARMA="Analyzing clinical trial results for drug X. Patient data is secure."
curl -s -X 'POST' \
  -H "X-API-Key: $API_KEY" \
  -H 'Content-Type: application/json' \
  "$API_URL/evaluate?sync=true" \
  -d "{
  \"user_id\": \"pharma_scientist_01\",
  \"commitment\": \"Drug X Trial Analysis\",
  \"check_in\": \"$CHECK_IN_PHARMA\",
  \"industry\": \"pharmaceutical\",
  \"department\": \"research\"
}" | jq .
sleep 5

echo -e "\n--- [GOD-MODE] Scenario 20: Human-in-the-Loop Feedback Loop ---"
if [[ -n "$INTERVENTION_ID" && "$INTERVENTION_ID" != "null" ]]; then
  echo "Manager providing feedback on the HR Intervention (ID: $INTERVENTION_ID)..."
  echo "Action: ACCEPTED (The block was correct)."
  curl -s -X 'POST' \
    -H "X-API-Key: $API_KEY" \
    -H 'Content-Type: application/json' \
    "$API_URL/safety/feedback" \
    -d "{
    \"intervention_id\": \"$INTERVENTION_ID\",
    \"user_id\": \"hr_manager\",
    \"manager_id\": \"$USER_ID\",
    \"action_taken\": \"accepted\",
    \"final_message_sent\": \"[BLOCKED]\",
    \"comments\": \"Good catch on the salary data.\"
  }" | jq .
else
  echo "⚠️ No Intervention ID captured from Scenario 13. Skipping feedback demo."
fi

echo -e "\n--------------------------------------------------"
echo "✅ COMMITVIGIL SNIPER DEMO COMPLETE. COMMITMENT INTEGRITY SECURED. 🛡️"
echo "--------------------------------------------------"
