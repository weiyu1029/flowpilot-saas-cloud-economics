# Findings and Recommendations

## Executive diagnosis — June 2026
- MRR is **$751,800**, up **0.2%** month over month.
- Cloud cost is **$178,102**, down **3.2%** month over month.
- Cloud cost represents **23.7%** of MRR, implying an estimated infrastructure gross margin of **76.3%**.
- The portfolio is **$14,087 under budget**.
- **88** customers are in the Margin Risk tier, representing **$273,050 MRR**.

## Feature economics
- **AI Assistant:** 74.9% adoption, $49,396 monthly feature cost, $6.08 per active user, **Optimization Priority**.
- **Dashboard Reporting:** 85.5% adoption, $27,055 monthly feature cost, $2.67 per active user, **Scale Carefully**.
- **Advanced Analytics:** 47.7% adoption, $18,201 monthly feature cost, $5.73 per active user, **Optimization Priority**.
- **File Storage:** 49.9% adoption, $13,263 monthly feature cost, $2.20 per active user, **Optimization Priority**.
- **Team Collaboration:** 93.8% adoption, $8,349 monthly feature cost, $0.73 per active user, **Efficient Winner**.
- **API Integration:** 81.5% adoption, $7,445 monthly feature cost, $0.89 per active user, **Efficient Winner**.

## Interpretation
1. **AI Assistant is the largest feature cost pool.** Its high adoption proves customer value, but the unit-cost profile calls for caching, model routing, token controls, and monetization guardrails rather than blunt removal.
2. **Dashboard Reporting is valuable but expensive at scale.** Query optimization and BI caching should precede product restrictions.
3. **Advanced Analytics and File Storage are portfolio optimization priorities.** Their cost profile is high relative to adoption, making onboarding, retention policy, and packaging the relevant levers.
4. **Customer margin risk is not the same as churn risk.** The dashboard treats it as a pricing/service-cost prioritization signal and preserves human review.
5. **Being under budget does not prove efficiency.** The service and environment views still reveal optimization opportunities and unusual cost patterns.

## Prioritized action backlog
1. **High-usage accounts are underpriced** — Launch a pricing review for accounts above the 25% cost-to-revenue threshold and add usage-based API/AI overages. Estimated monthly impact: **$15,018**; owner: Finance + Customer Success; confidence: Medium.
2. **AI Assistant cost is growing faster than monetization** — Introduce semantic caching, prompt/token limits, usage telemetry, and an AI usage add-on above plan allowances. Estimated monthly impact: **$21,415**; owner: Product + Engineering + Finance; confidence: High.
3. **Athena queries scan more data than necessary** — Convert curated datasets to Parquet, partition by month, select only required columns, and enforce query workgroups. Estimated monthly impact: **$11,142**; owner: Data Engineering; confidence: High.
4. **File retention policy creates high cost relative to adoption** — Apply S3 lifecycle policies, intelligent tiering, retention limits, and customer-facing storage quotas. Estimated monthly impact: **$5,550**; owner: Cloud Operations + Product; confidence: High.
5. **Advanced Analytics has low adoption and relatively high unit cost** — Improve onboarding and validate willingness-to-pay before increasing infrastructure investment. Estimated monthly impact: **$5,456**; owner: Product + Customer Success; confidence: Medium.
6. **Log ingestion and retention are not governed tightly** — Reduce verbose logs, apply retention policies, separate audit and debug logs, and alert on ingestion anomalies. Estimated monthly impact: **$2,058**; owner: Engineering + Security; confidence: High.
7. **Development resources remain active outside working hours** — Schedule non-production shutdowns, set per-environment budgets, and require owner/expiration tags. Estimated monthly impact: **$1,711**; owner: Cloud Operations; confidence: High.
8. **Shared compute requires rightsizing and commitment review** — Use Compute Optimizer, rightsizing, Auto Scaling, and Savings Plans only after baseline demand is stable. Estimated monthly impact: **$2,357**; owner: Cloud Operations + Finance; confidence: Medium.

## Estimated opportunity
The eight synthetic recommendations sum to **$64,708 per month**. This is a scenario-based opportunity estimate, not a financial forecast or guaranteed savings commitment.
