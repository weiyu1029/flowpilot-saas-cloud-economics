# FlowPilot Portfolio Case Study

## 1. Problem statement

FlowPilot is a fictional B2B workflow-automation SaaS company. Customer activity and feature consumption are increasing, but infrastructure cost is growing faster than recurring revenue. Leadership lacks a shared view connecting product usage, customer economics, and cloud spend.

## 2. Stakeholders

| Stakeholder | Decision need |
|---|---|
| Executive leadership | Is growth profitable and within budget? |
| Product Management | Which features should be scaled, optimized, repriced, or retired? |
| Finance / FinOps | What drives cloud spend and where can savings be realized? |
| Customer Success | Which customers create margin risk or need plan changes? |
| Engineering / Cloud Operations | Which technical cost pools should be optimized first? |

## 3. Core user stories

- As an executive, I want to compare MRR and cloud cost so I can assess infrastructure margin.
- As a Product Manager, I want to compare feature adoption and cost so I can prioritize the roadmap.
- As a FinOps analyst, I want budget variance and cost-driver views so I can target savings.
- As a Customer Success leader, I want customer cost-to-revenue ratios so I can identify pricing-review candidates.
- As an engineer, I want traceable recommendations so I can connect technical actions to business impact.

## 4. KPI definitions

### Infrastructure Gross Margin

`(MRR - Allocated Cloud Cost) / MRR`

Used to evaluate whether SaaS revenue sufficiently covers cloud infrastructure.

### Cost-to-Revenue Ratio

`Allocated Customer Cloud Cost / Customer MRR`

Thresholds:

- Healthy: below 15%
- Monitor: 15% to 25%
- Margin Risk: above 25%

### Feature Adoption Rate

`Customers Using Feature / Eligible Customers`

Used with feature cost to create four decision quadrants:

- Efficient Winner
- Scale Carefully
- Monitor
- Optimize / Reprice

### Budget Variance

`Actual Cloud Cost - Budget`

Used for monthly FinOps governance.

## 5. Data design

The deployed app produces deterministic synthetic data using seed 42:

- 240 customers
- 18 months
- Three subscription plans
- Five industries
- Three regions
- Eight product features
- Customer-month and customer-month-feature grains
- AWS service attribution

No real customer, billing, or personal data is used.

## 6. AWS implementation blueprint

```text
S3 raw zone
  → Lambda / Glue validation and transformation
  → S3 processed and curated zones
  → Glue Data Catalog
  → Athena SQL analysis
  → Streamlit / QuickSight dashboards
  → CloudWatch, SNS, and AWS Budgets alerts
```

Security design:

- IAM least privilege
- S3 Block Public Access
- Encryption at rest with S3/KMS
- TLS in transit
- No long-lived AWS credentials in the app
- CloudTrail for API activity and CloudWatch for operational monitoring

Cost controls:

- Parquet and partitioning to reduce Athena scan volume
- S3 lifecycle policies
- Scheduled shutdown of non-production compute
- AWS Budgets thresholds
- Cost-allocation tags
- Rightsizing and Compute Optimizer review

## 7. Main findings modeled in the scenario

1. AI Assistant has the largest controllable compute cost and should be evaluated for caching, model routing, and usage-based pricing.
2. Development resources consume an excessive share of cost and should use scheduled shutdown and rightsizing.
3. File Storage and Data Export can fall into the high-cost / lower-adoption quadrant, supporting lifecycle and product-design review.
4. Customers above the 25% cost-to-revenue threshold should be reviewed for plan fit, usage limits, or contract changes.
5. Athena query design should use Parquet, partitions, and column pruning.

## 8. Recommendation framework

Every recommendation is structured as:

`Observed signal → Root cause hypothesis → Business impact → Action → Owner → Priority`

This avoids presenting dashboards as decoration and makes the project decision-oriented.

## 9. Interview story

> I wanted to build an AWS portfolio project that was relevant to Business Analyst and Product Analyst roles rather than only demonstrating infrastructure setup. I created a SaaS cloud-economics dashboard that connects subscription revenue, product adoption, customer usage, and AWS-style cloud cost. I designed explainable KPIs such as infrastructure gross margin, feature cost per active user, and customer cost-to-revenue ratio. The dashboard gives different views to executives, Product, Finance, Customer Success, and Cloud Operations, and includes a scenario simulator for estimating savings. I also mapped the solution to an AWS architecture using S3, Lambda or Glue, Athena, CloudWatch, SNS, Budgets, IAM least privilege, and encryption. The result is a portfolio project that demonstrates business framing, analytics, cloud literacy, and decision communication.

## 10. Future roadmap

- Replace synthetic data with AWS Cost and Usage Report data.
- Store curated data in partitioned Parquet on S3.
- Query with Athena and compare scan costs before and after optimization.
- Add automated Lambda validation and CloudWatch alarms.
- Add QuickSight as an AWS-native BI layer.
- Add plan-level forecasting and anomaly detection.
- Add dbt-style testing and data lineage documentation.
