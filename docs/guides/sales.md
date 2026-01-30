# Sales Enablement Guide 🚀

CommitVigil isn't just a tool; it's a platform with built-in sales intelligence to help you close enterprise deals.

---

## 1. The "Drift Scenario" Generator
Prospects often don't realize how much "Engagement Slippage" costs them. Use the **Prospecting Agent** to generate industry-specific examples of failed commitments.

### Usage
```bash
curl -X POST "$API_URL/sales/prospect?company_name=AcmeCorp&industry=healthcare"
```

### Output Value
*   **Realistic Scenarios**: The AI will generate examples like *"Lead Researcher promised safety data by Friday but no commit was found."*
*   **Targeted Role**: It automatically targets the persona (e.g., CTO, VP Eng) relevant to that industry.

---

## 2. Multi-Currency ROI Calculator
Close deals faster by showing the math. The calculator supports `USD`, `EUR`, and `GBP`.

### Usage
```bash
curl -X GET "$API_URL/sales/roi-calculator?team_size=50&avg_salary=120000&currency=EUR"
```

### Key Metrics
*   **Annual Savings**: The raw cash value of recovered time.
*   **Payback Period**: Usually < 1 month for teams > 10.
*   **Efficiency Gain**: The % improvement in delivery velocity.

---

## 3. The Executive Brief (The "Closer")
Generate a premium, glassmorphic HTML one-pager to send as a follow-up after your demo.

### Steps
1.  Run the generation command:
    ```bash
    curl -X POST "$API_URL/sales/executive-brief?company_name=BigBank..." > brief.html
    ```
2.  Print to PDF.
3.  Email to the Champion/Decision Maker.

---

## 🔒 Internal Use Only
*   **Demo Mode**: Ensure `DEMO_MODE=false` in production to use real reasoning.
*   **Rate Limits**: The sales endpoints are rate-limited to 10 requests/minute.
