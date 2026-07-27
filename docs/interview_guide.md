# Interview Guide

## 30-second version
I built a SaaS product-usage and cloud-cost optimization dashboard that connects subscription revenue, feature adoption, AWS-style infrastructure cost, reliability, and customer unit economics. The portfolio includes a deterministic data pipeline, seven stakeholder views, data-quality and app tests, CI, and a serverless AWS reference architecture.

## 90-second version
I had already completed a supply-chain analytics project, so I intentionally chose a SaaS problem to demonstrate domain transfer. I modeled a fictional workflow-automation company with 480 synthetic customers and 18 months of subscriptions, usage, support, incidents, budgets, and cloud cost. The dashboard helps Product evaluate feature economics, Finance track unit economics and budgets, Customer Success identify high-cost accounts, and Engineering prioritize FinOps and reliability actions. For June 2026, the model shows $751,800 MRR, $178,102 cloud cost, and an estimated 76.3% infrastructure gross margin. I also documented an AWS serverless implementation using S3, Lambda or Glue, Athena, CloudWatch, SNS, Budgets, and least-privilege IAM.

## STAR structure
- **Situation:** cloud cost was growing without a shared link to product and customer value.
- **Task:** create a decision system, not merely a set of charts.
- **Action:** defined stakeholders/KPIs, generated reproducible data, built curated models and seven dashboard views, tested the app, and prioritized explainable recommendations.
- **Result:** surfaced margin-risk customers, high-cost feature pools, budget position, anomaly evidence, and a synthetic $64,708/month action pipeline.

## Questions to expect
1. Why synthetic data? — Reproducibility, privacy, controlled scenarios, and public portfolio safety.
2. Why Streamlit? — Fast stakeholder-facing analytics with Python and GitHub-based deployment.
3. Why not QuickSight? — QuickSight is a credible AWS-native option; Streamlit is lower-friction for a public portfolio and custom narrative.
4. Why S3/Athena? — Intermittent analytical workload, serverless operations, and transparent bytes-scanned optimization.
5. How is cost allocated? — Direct feature-attributed usage plus a weighted share of shared infrastructure; definitions are documented and synthetic.
6. What would change in production? — Real CUR/usage events, governed dimensions, IAM Identity Center, Lake Formation, orchestration, tests, and formal FinOps allocation.
7. Is the Copilot generative AI? — The included version is deterministic and explainable; production can add grounded Claude/OpenAI/Bedrock retrieval with evaluation and access controls.
8. Biggest limitation? — Synthetic rates and allocation assumptions must not be interpreted as actual AWS pricing or audited finance.
