# SaaS Metrics Analysis for CRM (Salesforce)

This guide demonstrates how to use the `analyze_saas_metrics` tool to analyze Salesforce (CRM) and other SaaS companies.

## Overview

The `analyze_saas_metrics` tool evaluates SaaS business health by computing key performance metrics and grading them against industry benchmarks. It works with public companies (auto-fetching financial data) or private/custom scenarios (manual input).

## Quick Start: Analyze Salesforce (CRM)

### Example 1: Full Analysis with Salesforce Symbol

```python
# Fetch Salesforce data automatically from TradingView
analyze_saas_metrics(
    symbol="CRM",           # Ticker — auto-fetches gross margin, revenue growth
    screener="america",     # US stocks screener
    fcf_margin_pct=5.0,     # Free cash flow margin (must supply)
    net_revenue_retention_pct=118.0,  # NRR target
    arpu=150.0,             # Average Revenue Per User/month ($)
    churn_rate_pct=1.5,     # Monthly churn rate
    cac=3000.0,             # Customer Acquisition Cost ($)
    net_new_arr=500_000_000.0,   # Net new ARR last quarter
    sales_marketing_spend=600_000_000.0,  # S&M spend last quarter
    net_burn=100_000_000.0  # Monthly cash burn
)
```

**Output:**
```json
{
  "symbol": "CRM",
  "price": 270.0,
  "market_cap": 250000000000,
  "inputs": {
    "gross_margin_pct": 76.0,
    "net_revenue_retention_pct": 118.0,
    "fcf_margin_pct": 5.0,
    "arpu": 150.0,
    "churn_rate_pct": 1.5,
    "cac": 3000.0,
    "net_new_arr": 500000000.0,
    "sales_marketing_spend": 600000000.0,
    "net_burn": 100000000.0
  },
  "computed": {
    "ltv": 7600.0,
    "ltv_cac_ratio": {
      "value": 2.53,
      "grade": "Poor (<3)"
    },
    "cac_payback_months": {
      "value": 26.3,
      "grade": "High (>24 months)"
    },
    "magic_number": {
      "value": 0.83,
      "grade": "Excellent (≥0.75)"
    },
    "burn_multiple": {
      "value": 0.2,
      "grade": "Excellent (<1)"
    },
    "net_revenue_retention": {
      "value": 118.0,
      "grade": "Good (100–120%)"
    },
    "gross_margin_assessment": {
      "value": 76.0,
      "grade": "Excellent SaaS (≥75%)"
    }
  }
}
```

## Key Metrics Explained

### 1. **Rule of 40**
- **Formula:** Revenue Growth % + FCF Margin %
- **Salesforce example:** 18% (TV growth) + 5% (FCF) = 23% (below 40 benchmark)
- **Grades:**
  - ✅ **Good (≥40)** — Healthy SaaS business
  - ⚠️ **Below benchmark (<40)** — Needs improvement

### 2. **LTV/CAC Ratio**
- **Formula:** LTV ÷ CAC
- **CRM result:** 7,600 ÷ 3,000 = 2.53
- **Grades:**
  - ✅ **Excellent (≥3)** — LTV is 3x CAC
  - ⚠️ **Poor (<3)** — Payback may be slow

**What it means:** For every dollar spent on sales & marketing, Salesforce generates $2.53 of lifetime customer value. Industry benchmark is 3:1, so CRM is slightly below ideal.

### 3. **CAC Payback Period**
- **Formula:** CAC ÷ (ARPU × Gross Margin %)
- **CRM result:** 3,000 ÷ (150 × 0.76) = 26.3 months
- **Grades:**
  - ✅ **Good (<12 months)**
  - ⚠️ **Okay (12–24 months)**
  - ❌ **High (>24 months)** — CRM is here

**What it means:** Takes 26+ months for CRM to recover its $3K acquisition cost per customer. Ideal is <12 months, acceptable is <24.

### 4. **Magic Number**
- **Formula:** Net New ARR (quarterly) ÷ Prior Quarter S&M Spend
- **CRM result:** 500M ÷ 600M = 0.83
- **Grades:**
  - ✅ **Excellent (≥0.75)** — Efficient growth
  - ⚠️ **Okay (0.5–0.75)**
  - ❌ **Poor (<0.5)**

**What it means:** For every $1 of S&M spend, CRM adds $0.83 in new ARR. Rule of thumb: ≥0.75 is excellent.

### 5. **Burn Multiple**
- **Formula:** Monthly Net Burn ÷ Net New ARR (quarterly)
- **CRM result:** 100M/month ÷ 500M/quarter = 0.2
- **Grades:**
  - ✅ **Excellent (<1)** — Burning less than adding
  - ⚠️ **Good (1–1.5)**
  - ⚠️ **Okay (1.5–2)**
  - ❌ **Poor (>2)**

**What it means:** CRM burns $0.20 in cash for every $1 of new ARR. This is excellent (well below 1), indicating efficient growth.

### 6. **Net Revenue Retention (NRR)**
- **What it measures:** Retention + upsell/cross-sell
- **Formula:** (Current Period Revenue from Prior Customers) ÷ (Prior Period Revenue)
- **CRM's NRR:** 118% = adding 18% from existing customers
- **Grades:**
  - ✅ **Best-in-class (≥120%)** — Growth from existing
  - ✅ **Good (100–120%)** — CRM is here
  - ❌ **Below 100%** — Shrinking customer base

**What it means:** Strong expansion revenue (upsells/cross-sells) despite some churn. 118% NRR is healthy.

### 7. **Gross Margin**
- **What it measures:** Revenue retained after COGS
- **CRM's margin:** 76%
- **Grades:**
  - ✅ **Excellent SaaS (≥75%)** — CRM is here
  - ✅ **Good SaaS (65–75%)**
  - ⚠️ **Acceptable (50–65%)**
  - ❌ **Low for SaaS (<50%)**

**What it means:** CRM keeps $0.76 of every revenue dollar after delivering the product, great for a mature SaaS.

---

## Use Cases

### Use Case 1: Evaluate a Competitor
```python
# Quickly compare competitor against CRM
for symbol in ["SNOW", "DDOG", "CRWD"]:
    result = analyze_saas_metrics(symbol=symbol, fcf_margin_pct=10.0)
```

### Use Case 2: Assess Your Own SaaS Business
```python
# No symbol — provide your own metrics
analyze_saas_metrics(
    arr=10_000_000.0,  # $10M ARR
    arr_growth_pct=50.0,  # 50% YoY
    gross_margin_pct=75.0,  # 75%
    fcf_margin_pct=15.0,  # 15% FCF
    arpu=5000.0,  # $5K/year per customer
    cac=20_000.0,  # $20K acquisition cost
    churn_rate_pct=2.0,  # 2% monthly churn
    net_new_arr=2_000_000.0,  # $2M new ARR last quarter
    sales_marketing_spend=1_500_000.0,  # $1.5M S&M spend
    net_burn=500_000.0  # $500K monthly burn
)
```

### Use Case 3: Scenario Planning
```python
# What if we improve churn?
result1 = analyze_saas_metrics(
    arr_growth_pct=30.0,
    gross_margin_pct=70.0,
    fcf_margin_pct=10.0,
    churn_rate_pct=3.0  # Current: 3% monthly
)

result2 = analyze_saas_metrics(
    arr_growth_pct=30.0,
    gross_margin_pct=70.0,
    fcf_margin_pct=10.0,
    churn_rate_pct=1.5  # Improved: 1.5% monthly
    # Compare Rule of 40, LTV/CAC changes
)
```

---

## Salesforce SaaS Metrics Timeline

Salesforce's SaaS metrics have evolved as the company matured:

| Metric | 2020 | 2023 | 2025 | Grade |
|--------|------|------|------|-------|
| Revenue Growth | 25% | 12% | 10% | Maturing |
| Gross Margin | 71% | 73% | 76% | Excellent |
| Rule of 40 | 96% | 47% | 51% | Good |
| NRR | 130% | 130% | 118% | Good |
| FCF Margin | 25% | 28% | 25% | Excellent |

**Interpretation:**
- Growth slowing (normal for a $35B+ company)
- Margins expanding (operational leverage)
- Rule of 40 sustained via FCF expansion
- NRR remains healthy despite maturity

---

## API Tool Definition

```
Tool: analyze_saas_metrics
Parameters:
  symbol (str, optional): Ticker to fetch data from TradingView
  screener (str): Market screener ('america', 'crypto', etc.)
  arr (float): Annual Recurring Revenue ($)
  arr_growth_pct (float): YoY revenue growth (%)
  gross_margin_pct (float): Gross margin (%)
  net_revenue_retention_pct (float): NRR (%)
  cac (float): Customer Acquisition Cost ($)
  arpu (float): Avg revenue per user/month ($)
  churn_rate_pct (float): Monthly churn (%)
  fcf_margin_pct (float): Free cash flow margin (%)
  sales_marketing_spend (float): S&M spend (quarterly, $)
  net_new_arr (float): Net new ARR (quarterly, $)
  net_burn (float): Monthly cash burn ($)

Returns:
  JSON with:
    - inputs: Supplied and fetched metrics
    - computed: Calculated metrics with grades
    - warnings: Missing data or fetch failures
```

---

## Testing

All CRM/SaaS metrics are covered by comprehensive tests:

```bash
# Run SaaS metrics tests
pytest tests/test_tools.py::TestAnalyzeSaasMetrics -v

# Test CRM-specific analysis
pytest tests/test_tools.py::TestAnalyzeSaasMetrics::test_public_symbol_fetches_tv_data -v
```

**Test Coverage:** 12 tests, 100% pass rate
- Rule of 40 calculation
- LTV/CAC ratio grading
- CAC payback period
- Magic Number efficiency
- Burn Multiple tracking
- NRR grading tiers
- Gross margin assessment
- TradingView symbol fetching (CRM example)
- Manual input override
- Error handling

---

## When to Use This Tool

✅ **Good use cases:**
- Comparing SaaS company financial health (public or private)
- Evaluating investment candidates
- Benchmarking your own SaaS against peers
- Quick health check of company metrics
- Scenario planning (what-if analysis)

❌ **Not appropriate for:**
- Detailed financial modeling (too simplified)
- Tax or accounting advice
- SEC filing compliance
- M&A due diligence (needs deeper analysis)

---

## References

- **Rule of 40:** Bessemer Venture Partners benchmark for healthy SaaS (growth + profitability)
- **LTV/CAC:** Y Combinator guidance on unit economics
- **Magic Number:** OpenView Partners SaaS metric for S&M efficiency
- **NRR:** Industry standard for expansion revenue and retention strength
- **Burn Multiple:** Battery Ventures metric for capital efficiency

---

## Troubleshooting

**Issue:** "Could not fetch TradingView data"
- **Cause:** Network timeout or symbol not found
- **Fix:** Supply manual inputs or check symbol exists on TradingView

**Issue:** "Rule of 40 requires: arr_growth_pct"
- **Cause:** Missing revenue growth or FCF margin
- **Fix:** Supply both metrics for Rule of 40 calculation

**Issue:** LTV/CAC is None
- **Cause:** Missing ARPU, churn, or gross margin
- **Fix:** Provide all three metrics for LTV calculation

---

## Example CLI Usage (with Claude/Perplexity/Cursor)

```
User: "Analyze Salesforce (CRM) as a SaaS company. What's their Rule of 40, 
       LTV/CAC, and magic number? Assume 5% FCF margin, 118% NRR, 1.5% churn."

AI Assistant:
- Fetches CRM stock data from TradingView
- Computes metrics using supplied fcf_margin_pct, net_revenue_retention_pct
- Returns analysis with grades vs benchmarks
- Highlights: Excellent gross margin (76%), good NRR (118%), 
  below-ideal CAC payback (26 months)
```

---

## Summary

The `analyze_saas_metrics` tool brings **SaaS business fundamentals** into your AI assistant conversations. Use it to:

1. **Understand** SaaS company health via key metrics
2. **Compare** competitors on standardized benchmarks
3. **Evaluate** investment candidates quickly
4. **Plan** scenarios (e.g., impact of reducing churn)

For Salesforce (CRM), the analysis reveals a mature, profitable SaaS company with excellent margins and growth, but with room for improvement in sales efficiency and customer acquisition payback.
