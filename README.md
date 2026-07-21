# FlowPilot SaaS Product Usage & Cloud Cost Optimization Dashboard

A portfolio-grade **Business Analysis + Product Analytics + FinOps + AWS** case study. The app connects SaaS subscription revenue, product adoption, customer behavior, and AWS-style infrastructure cost to produce decision-ready recommendations.

## Live dashboard

The repository is ready for Streamlit Community Cloud deployment. Use:

- Repository: `weiyu1029/practice_1`
- Branch: `main`
- Main file: `streamlit_app.py`

## Business problem

FlowPilot is a fictional B2B workflow-automation SaaS company. Product usage is growing, but cloud cost is rising faster than recurring revenue. Leadership needs to answer:

- Which features drive the most cloud cost?
- Which features have high cost but weak adoption?
- Which customers consume more infrastructure than their subscription economics support?
- Which AWS services and environments create cost pressure?
- Which pricing, architecture, and governance actions should be prioritized?

## Dashboard pages

1. **Executive Overview** — MRR, cloud cost, infrastructure margin, cost per customer, budget variance, service mix, and leadership findings.
2. **Feature Economics** — adoption-versus-cost quadrant, unit economics, and feature optimization priorities.
3. **Customer Profitability** — cost-to-revenue ratio, margin-risk accounts, revenue at risk, and pricing-review candidates.
4. **FinOps & Optimization** — environment cost, actual versus budget, recommendations, and an interactive savings simulator.
5. **Decision Assistant** — deterministic, traceable answers grounded in dashboard metrics.
6. **Data & Architecture** — data model, AWS target architecture, governance, and downloadable analytical data.

## AWS target architecture

```text
Synthetic SaaS data
        ↓
Amazon S3 (raw / processed / curated)
        ↓
AWS Lambda or AWS Glue
        ↓
AWS Glue Data Catalog
        ↓
Amazon Athena
        ↓
Streamlit or Amazon QuickSight
        ↓
CloudWatch + SNS + AWS Budgets
```

### Why these services?

- **Amazon S3** — scalable analytical object storage.
- **AWS Lambda / AWS Glue** — managed and repeatable transformation.
- **Amazon Athena** — serverless SQL with visible scan-cost optimization opportunities.
- **CloudWatch and SNS** — pipeline monitoring and alerting.
- **AWS Budgets** — cost-threshold governance.
- **Streamlit** — interactive public portfolio delivery without exposing AWS credentials.

## KPI framework

| KPI | Formula | Decision supported |
|---|---|---|
| Cost-to-Revenue Ratio | Allocated Cloud Cost / MRR | Customer margin risk and pricing review |
| Infrastructure Gross Margin | (MRR - Cloud Cost) / MRR | Company and plan economics |
| Feature Adoption Rate | Active Customers / Eligible Customers | Product prioritization |
| Cost per Active User | Feature Cost / Active Users | Unit-cost efficiency |
| Budget Variance | Actual Cloud Cost - Budget | FinOps governance |

## Synthetic data design

The app creates deterministic synthetic data with seed `42` for:

- 240 SaaS customers
- 18 monthly periods
- Starter, Professional, and Enterprise plans
- Five industries and three regions
- Eight product features
- AWS service cost attribution
- Feature adoption, active users, usage units, MRR, and allocated cloud cost

The data intentionally includes realistic signals such as an AI Assistant cost spike, high-cost/low-adoption features, margin-risk customers, and excess development spend. It contains no real customer information.

## Run locally

```bash
git clone https://github.com/weiyu1029/practice_1.git
cd practice_1
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploy to Streamlit Community Cloud

1. Sign in to Streamlit Community Cloud with GitHub.
2. Click **Create app**.
3. Select `weiyu1029/practice_1`.
4. Select branch `main`.
5. Set main file path to `streamlit_app.py`.
6. Choose a subdomain and deploy.

No secrets are required. Because the repository is currently private, Streamlit must be granted access to private repositories. For a public portfolio, change the repository visibility to public before sharing the app.

## Portfolio story

> I built a cloud-aware SaaS economics solution that maps product usage to AWS-style infrastructure cost and subscription revenue. The dashboard helps Product, Finance, Customer Success, and Cloud Operations identify feature optimization opportunities, customer margin risk, pricing-review candidates, and cost-governance actions. I used deterministic synthetic data, explainable KPI thresholds, and a traceable decision assistant so every recommendation can be tied back to evidence.

## Resume bullets

- Built an interactive SaaS product-usage and cloud-cost optimization dashboard using Python, Streamlit, Plotly, and AWS-aligned FinOps concepts.
- Designed KPI logic for feature adoption, cost per active user, customer cost-to-revenue ratio, infrastructure gross margin, and budget variance.
- Developed stakeholder-specific views for Product, Finance, Customer Success, and Cloud Operations, including pricing-review and architecture-optimization recommendations.
- Modeled an AWS analytics architecture using S3, Lambda/Glue, Athena, CloudWatch, SNS, Budgets, IAM least privilege, and encryption principles.

## Security and ethics

- No real customer data or personally identifiable information.
- No AWS credentials, API keys, or private keys.
- Costs are illustrative and are not current AWS price quotes.
- The decision assistant is deterministic and does not fabricate evidence.

## License

MIT License.
