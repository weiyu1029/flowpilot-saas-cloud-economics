# KPI Dictionary

| KPI | Formula | Grain | Interpretation | Guardrail |
|---|---|---|---|---|
| MRR | Sum of active subscription MRR | Month / portfolio | Recurring revenue run rate | Synthetic, not GAAP reporting |
| ARR run rate | MRR × 12 | Month / portfolio | Annualized recurring revenue | Run-rate only |
| Total cloud cost | Direct feature cost + shared infrastructure cost | Month / portfolio | Illustrative AWS-style spend | Not an AWS bill estimate |
| Cost-to-revenue ratio | Allocated cloud cost ÷ MRR | Customer-month | Infrastructure unit economics | >25% = Margin Risk |
| Estimated gross margin | 1 − cost-to-revenue ratio | Customer-month / portfolio | Gross margin after allocated cloud infrastructure | Excludes non-cloud COGS |
| Feature adoption rate | Adopted eligible customers ÷ eligible customers | Feature-month | Breadth of feature use | Eligibility depends on plan/release |
| Cost per active user | Feature cloud cost ÷ active feature users | Feature-month | Feature unit efficiency | Compare within context |
| Cost share | Feature cost ÷ total feature-attributed cost | Feature-month | Contribution to direct feature cost | Shared overhead excluded |
| Revenue at risk | MRR for Margin Risk accounts | Customer-month | Commercial exposure requiring review | Not predicted churn |
| Customer health score | Weighted usage, adoption, support, risk, and economics score | Customer-month | Prioritization signal | Explainable heuristic, not ML prediction |
| Budget variance | Actual cost − budget | Month | Over/under budget | Negative means under budget |
| Estimated recommendation impact | Savings + revenue uplift | Recommendation | Prioritization estimate | Scenario estimate, not guaranteed |
