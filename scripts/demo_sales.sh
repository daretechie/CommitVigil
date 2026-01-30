#!/bin/bash
# --- TERMINAL COLORS ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${BOLD}${CYAN}💰 $1 ${NC}"
    echo -e "${CYAN}----------------------------------------------------------------------${NC}"
}

API_URL="http://localhost:8000/api/v1"
API_KEY="my-secure-api-key-12345"

echo -e "${BOLD}${GREEN}CommitVigil Sales Intelligence Demo${NC}"
echo -e "${YELLOW}Demonstrating Automated Prospecting & ROI Logic${NC}\n"

# 1. Automated Prospecting
print_header "1. Automated Prospecting Agent (The 'ProspectingScout')"
echo -e "${BLUE}Scenario: Sales Rep prepping for a call with a VP at a FinTech firm.${NC}"
echo "Generating drift scenarios for 'FinTech' industry..."

curl -s -X POST -H "X-API-Key: $API_KEY" \
  "$API_URL/sales/prospect?company_name=MegaBank&target_role=VP%20Engineering&team_size=50&industry=fintech" | jq .

sleep 3

echo -e "\n${BLUE}Scenario: Sales Rep prepping for an Energy Sector pitch.${NC}"
echo "Generating drift scenarios for 'Energy' industry..."
curl -s -X POST -H "X-API-Key: $API_KEY" \
  "$API_URL/sales/prospect?company_name=GreenEnergy&target_role=CTO&team_size=120&industry=energy" | jq .

sleep 3

# 2. ROI Calculator
print_header "2. Multi-Currency ROI Calculator"
echo -e "${BLUE}Calculating ROI for a 50-person team in USD...${NC}"
curl -s -X GET -H "X-API-Key: $API_KEY" \
  "$API_URL/sales/roi-calculator?team_size=50&avg_salary=160000&currency=USD" | jq .

sleep 2

echo -e "\n${BLUE}Calculating ROI for a 20-person team in EUR (Euro)...${NC}"
curl -s -X GET -H "X-API-Key: $API_KEY" \
  "$API_URL/sales/roi-calculator?team_size=20&avg_salary=90000&currency=EUR" | jq .

sleep 2

echo -e "\n${BLUE}Calculating ROI for a 100-person team in GBP (British Pound)...${NC}"
curl -s -X GET -H "X-API-Key: $API_KEY" \
  "$API_URL/sales/roi-calculator?team_size=100&avg_salary=75000&currency=GBP" | jq .

# 3. Executive Brief Generation
print_header "3. Generating C-Level Executive Brief (HTML)"
echo -e "${BLUE}Generating premium HTML brief for 'TechCorp' (SaaS)...${NC}"
mkdir -p reports
curl -s -X POST -H "X-API-Key: $API_KEY" \
  "$API_URL/sales/executive-brief?company_name=TechCorp&target_role=CIO&team_size=200&industry=SaaS&currency=USD" \
  > reports/executive_brief_techcorp.html

echo -e "✅ Brief saved to reports/executive_brief_techcorp.html"

echo -e "\n${GREEN}✅ Sales Demo Complete.${NC}"
