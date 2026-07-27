# Business Requirements Document

## Executive need
FlowPilot is a fictional B2B workflow-automation SaaS company. Leadership needs a shared view of how product usage drives AWS-style infrastructure cost and customer-level unit economics.

## Business objectives
1. Connect product adoption, cloud cost, subscription revenue, and reliability.
2. Identify high-cost / low-adoption features.
3. Identify high-usage / low-revenue accounts.
4. Track budget performance and abnormal cost movement.
5. Prioritize actions using impact, effort, risk, confidence, and owner.
6. Demonstrate a secure, observable, cost-conscious AWS analytics pattern.

## Latest synthetic baseline (June 2026)
- MRR: **$751,800.23**
- Cloud cost: **$178,102.21**
- Cost-to-revenue ratio: **23.7%**
- Estimated infrastructure gross margin: **76.3%**
- Active customers: **433**
- Margin-risk customers: **88**
- MRR at risk: **$273,050.35**

## In scope
- Deterministic synthetic customer, subscription, usage, support, incident, budget, and AWS-style cost data.
- Automated local pipeline that generates raw and curated CSV/Parquet datasets.
- Seven-page Streamlit analytics application.
- Data-quality tests, app smoke tests, CI, container support, and reference AWS infrastructure.
- Explainable rule-based Insights Copilot with no API key required.

## Out of scope
- Real customer PII or production billing data.
- Production-grade chargeback, accounting, or pricing decisions.
- Real-time Kafka/Spark platform.
- Legal or compliance certification.
- Actual AWS rate estimation; synthetic rates are illustrative.

## Success criteria
- Every displayed KPI has a documented formula and data lineage.
- The dashboard answers at least six executive/product/finance/customer-success questions.
- All data-quality and application tests pass.
- No secrets or private customer data are required.
- The app can be deployed from a GitHub repository to Streamlit Community Cloud.
