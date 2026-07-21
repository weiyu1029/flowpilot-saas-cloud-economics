# FlowPilot SaaS Cloud Economics

> An interactive **Business Analysis + Product Analytics + FinOps + AWS** portfolio case study that connects SaaS product usage, subscription revenue, customer behavior, and cloud infrastructure cost.

## Portfolio objective

FlowPilot is a fictional B2B workflow-automation SaaS company. Product adoption is growing, but infrastructure cost is increasing faster than recurring revenue. This project turns synthetic customer, subscription, feature-usage, and AWS-style cost data into decision-ready insights for Product, Finance, Customer Success, and Cloud Operations.

The dashboard answers five practical questions:

1. Which features drive the most cloud cost?
2. Which features have high cost but weak adoption?
3. Which customers consume more infrastructure than their subscription economics support?
4. Which AWS services and environments create the most cost pressure?
5. Which pricing, architecture, and governance actions should be prioritized?

## Live dashboard

**Deployment status:** Streamlit-ready. The public app URL will be added here after deployment.

Streamlit configuration:

- Branch: `main`
- Main file path: `streamlit_app.py`
- Secrets required: none

## Dashboard experience

1. **Executive Overview** — MRR, cloud cost, infrastructure margin, cost per customer, budget variance, service mix, and leadership findings.
2. **Feature Economics** — adoption-versus-cost quadrant, unit economics, and feature optimization priorities.
3. **Customer Profitability** — cost-to-revenue ratio, margin-risk accounts, revenue at risk, and pricing-review candidates.
4. **FinOps & Optimization** — environment cost, actual versus budget, recommendations, and an interactive savings simulator.
5. **Decision Assistant** — deterministic, traceable answers grounded in dashboard metrics.
6. **Data & Architecture** — data model, AWS target architecture, governance, and downloadable analytical data.

## AWS-aligned target architecture

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

### Service rationale

- **Amazon S3** — scalable analytical object storage.
- **AWS Lambda / AWS Glue** — managed, repeatable data transformation.
- **Amazon Athena** — serverless SQL with visible scan-cost optimization opportunities.
- **CloudWatch and SNS** — pipeline monitoring and operational alerting.
- **AWS Budgets** — cost-threshold governance.
- **IAM least privilege and encryption** — access control and data protection.
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

The application generates deterministic synthetic data with seed `42` for:

- 240 SaaS customers
- 18 monthly periods
- Starter, Professional, and Enterprise plans
- Five industries and three regions
- Eight product features
- AWS-service cost attribution
- Feature adoption, active users, usage units, MRR, and allocated cloud cost

The scenario intentionally contains an AI Assistant cost spike, high-cost/low-adoption features, margin-risk customers, and excess development spend. It contains no real customer or personal information.

## Run locally

```bash
git clone <repository-url>
cd <repository-folder>
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploy to Streamlit Community Cloud

1. Sign in to Streamlit Community Cloud with GitHub.
2. Select **Create app**.
3. Choose this repository and branch `main`.
4. Set the main file path to `streamlit_app.py`.
5. Choose a public subdomain and deploy.
6. Add the deployed URL to the **Live dashboard** section above.

No API keys or application secrets are required.

## Portfolio story

> I built a cloud-aware SaaS economics solution that maps product usage to AWS-style infrastructure cost and subscription revenue. The dashboard helps Product, Finance, Customer Success, and Cloud Operations identify feature optimization opportunities, customer margin risk, pricing-review candidates, and cost-governance actions. I used deterministic synthetic data, explainable KPI thresholds, and a traceable decision assistant so every recommendation can be tied back to evidence.

## Resume bullets

- Built an interactive SaaS product-usage and cloud-cost optimization dashboard using Python, Streamlit, Plotly, and AWS-aligned FinOps concepts.
- Designed KPI logic for feature adoption, cost per active user, customer cost-to-revenue ratio, infrastructure gross margin, and budget variance.
- Developed stakeholder-specific views for Product, Finance, Customer Success, and Cloud Operations, including pricing-review and architecture-optimization recommendations.
- Modeled an AWS analytics architecture using S3, Lambda/Glue, Athena, CloudWatch, SNS, Budgets, IAM least privilege, and encryption principles.

## Security, ethics, and limitations

- No real customer data or personally identifiable information.
- No AWS credentials, API keys, private keys, or hidden external services.
- Costs are illustrative and are not current AWS price quotes.
- The Decision Assistant is deterministic and does not fabricate evidence.
- This is a portfolio case study, not a production billing or financial-reporting system.

## Recommended repository name

`flowpilot-saas-cloud-economics`

## License

MIT License.
