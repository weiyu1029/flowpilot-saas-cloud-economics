from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="FlowPilot | SaaS Cloud Economics", page_icon="☁️", layout="wide")

FEATURES = {
    "Workflow Automation": (0.82, 6.5),
    "API Integration": (0.68, 10.5),
    "File Storage": (0.57, 13.0),
    "Dashboard Reporting": (0.63, 8.0),
    "AI Assistant": (0.74, 27.0),
    "Team Collaboration": (0.79, 4.0),
    "Data Export": (0.49, 11.0),
    "Admin Controls": (0.71, 3.0),
}
PLANS = {"Starter": 79, "Professional": 249, "Enterprise": 899}

@st.cache_data(show_spinner=False)
def make_data(seed: int = 42):
    rng = np.random.default_rng(seed)
    months = pd.date_range("2025-02-01", periods=18, freq="MS")
    customer_rows, usage_rows = [], []
    for cid in range(1, 241):
        plan = rng.choice(list(PLANS), p=[0.38, 0.44, 0.18])
        segment = {"Starter": "SMB", "Professional": "Mid-Market", "Enterprise": "Enterprise"}[plan]
        region = rng.choice(["North America", "Europe", "Asia Pacific"], p=[0.58, 0.25, 0.17])
        industry = rng.choice(["Technology", "Financial Services", "Healthcare", "Retail", "Professional Services"])
        growth = rng.normal(1.0, 0.09)
        for i, month in enumerate(months):
            seats = int({"Starter": 8, "Professional": 32, "Enterprise": 110}[plan] * growth * (1 + .018*i) * rng.uniform(.85, 1.15))
            mrr = PLANS[plan] * rng.uniform(.92, 1.10) + max(0, seats-10) * {"Starter": 2, "Professional": 4, "Enterprise": 6}[plan]
            customer_rows.append([f"C{cid:04d}", month, plan, segment, region, industry, seats, mrr])
            for feature, (base_adoption, unit_cost) in FEATURES.items():
                plan_factor = {"Starter": .72, "Professional": 1.0, "Enterprise": 1.18}[plan]
                adoption = np.clip(base_adoption * plan_factor + rng.normal(0, .07), .03, .98)
                active_users = int(seats * adoption)
                if active_users == 0:
                    continue
                usage = active_users * rng.uniform(.7, 1.4)
                cost = usage * unit_cost * rng.uniform(.75, 1.28) * (1 + .025*i)
                if feature == "AI Assistant" and i >= 12:
                    cost *= 1.25
                service = {
                    "Workflow Automation": "AWS Lambda", "API Integration": "API Gateway",
                    "File Storage": "Amazon S3", "Dashboard Reporting": "Amazon Athena",
                    "AI Assistant": "Amazon EC2", "Team Collaboration": "AWS Lambda",
                    "Data Export": "Amazon S3", "Admin Controls": "CloudWatch",
                }[feature]
                usage_rows.append([f"C{cid:04d}", month, feature, service, active_users, usage, cost])
    customers = pd.DataFrame(customer_rows, columns=["customer_id","month","plan","segment","region","industry","seats","mrr"])
    usage = pd.DataFrame(usage_rows, columns=["customer_id","month","feature","aws_service","active_users","usage_units","cloud_cost"])
    merged = usage.merge(customers, on=["customer_id","month"], how="left")
    budget = merged.groupby("month", as_index=False)["cloud_cost"].sum()
    budget["budget"] = budget["cloud_cost"].rolling(3, min_periods=1).mean() * .94
    return customers, usage, merged, budget

def money(x): return f"${x:,.0f}"
def pct(x): return f"{x:.1%}"

customers, usage, data, budget = make_data()
months = sorted(customers.month.unique())

with st.sidebar:
    st.title("☁️ FlowPilot")
    st.caption("SaaS Product Usage & Cloud Cost Intelligence")
    page = st.radio("Page", ["Executive Overview", "Feature Economics", "Customer Profitability", "FinOps & Optimization", "Decision Assistant", "Data & Architecture"], label_visibility="collapsed")
    month = st.selectbox("Latest month", months, index=len(months)-1, format_func=lambda x: pd.Timestamp(x).strftime("%b %Y"))
    plans = st.multiselect("Plan", list(PLANS), default=list(PLANS))
    regions = st.multiselect("Region", sorted(customers.region.unique()), default=sorted(customers.region.unique()))
    st.caption("Deterministic synthetic data. Not an AWS price quote.")

filtered_customers = customers[(customers.month <= month) & customers.plan.isin(plans) & customers.region.isin(regions)]
filtered = data[(data.month <= month) & data.plan.isin(plans) & data.region.isin(regions)]
latest_customers = filtered_customers[filtered_customers.month.eq(month)]
latest = filtered[filtered.month.eq(month)]
if latest.empty or latest_customers.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

monthly_rev = filtered_customers.groupby("month", as_index=False).mrr.sum()
monthly_cost = filtered.groupby("month", as_index=False).cloud_cost.sum()
trend = monthly_rev.merge(monthly_cost, on="month")
trend["gross_margin"] = (trend.mrr - trend.cloud_cost) / trend.mrr
trend = trend.merge(budget[["month","budget"]], on="month", how="left")
latest_mrr = latest_customers.mrr.sum()
latest_cost = latest.cloud_cost.sum()
margin = (latest_mrr-latest_cost)/latest_mrr
budget_row = trend[trend.month.eq(month)].iloc[0]

st.title("FlowPilot SaaS Cloud Economics")
st.caption("Business Analysis + Product Analytics + FinOps + AWS portfolio case study")

if page == "Executive Overview":
    cols = st.columns(5)
    values = [("MRR", money(latest_mrr)), ("Cloud Cost", money(latest_cost)), ("Infrastructure Margin", pct(margin)), ("Cost / Customer", money(latest_cost/max(1, latest_customers.customer_id.nunique()))), ("Budget Variance", money(latest_cost-budget_row.budget))]
    for col, (label, value) in zip(cols, values): col.metric(label, value)
    left, right = st.columns([1.6, 1])
    with left:
        long = trend.melt("month", ["mrr","cloud_cost"], var_name="metric", value_name="value")
        st.plotly_chart(px.line(long, x="month", y="value", color="metric", markers=True, title="Revenue vs. cloud cost"), use_container_width=True)
    with right:
        svc = latest.groupby("aws_service", as_index=False).cloud_cost.sum().sort_values("cloud_cost", ascending=False)
        st.plotly_chart(px.pie(svc, names="aws_service", values="cloud_cost", hole=.45, title="Cost by AWS service"), use_container_width=True)
    top = latest.groupby("feature", as_index=False).cloud_cost.sum().nlargest(1, "cloud_cost").iloc[0]
    st.subheader("Executive findings")
    st.info(f"{top.feature} is the largest latest-month feature cost driver at {money(top.cloud_cost)}.")
    st.info(f"Infrastructure gross margin is {pct(margin)}. The latest cost is {money(latest_cost-budget_row.budget)} versus budget.")

elif page == "Feature Economics":
    feat = latest.groupby("feature", as_index=False).agg(feature_cost=("cloud_cost","sum"), active_users=("active_users","sum"), customers=("customer_id","nunique"))
    eligible = latest_customers.customer_id.nunique()
    feat["adoption_rate"] = feat.customers / eligible
    feat["cost_per_active_user"] = feat.feature_cost / feat.active_users
    median_cost, median_adoption = feat.feature_cost.median(), feat.adoption_rate.median()
    feat["quadrant"] = np.select([(feat.feature_cost>=median_cost)&(feat.adoption_rate>=median_adoption), (feat.feature_cost>=median_cost)&(feat.adoption_rate<median_adoption), (feat.feature_cost<median_cost)&(feat.adoption_rate>=median_adoption)], ["Scale Carefully","Optimize / Reprice","Efficient Winner"], default="Monitor")
    fig = px.scatter(feat, x="adoption_rate", y="feature_cost", size="active_users", color="quadrant", text="feature", hover_data=["cost_per_active_user"], title="Feature adoption vs. cloud cost")
    fig.add_vline(x=median_adoption, line_dash="dash"); fig.add_hline(y=median_cost, line_dash="dash")
    fig.update_xaxes(tickformat=".0%"); fig.update_traces(textposition="top center")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(feat.sort_values("feature_cost", ascending=False).style.format({"feature_cost":"${:,.0f}","adoption_rate":"{:.1%}","cost_per_active_user":"${:,.2f}"}), use_container_width=True)

elif page == "Customer Profitability":
    cust_cost = latest.groupby("customer_id", as_index=False).cloud_cost.sum()
    cust = latest_customers.merge(cust_cost, on="customer_id", how="left").fillna({"cloud_cost":0})
    cust["cost_to_revenue"] = cust.cloud_cost / cust.mrr
    cust["gross_margin"] = (cust.mrr-cust.cloud_cost)/cust.mrr
    cust["risk"] = pd.cut(cust.cost_to_revenue, [-1,.15,.25,np.inf], labels=["Healthy","Monitor","Margin Risk"])
    c1,c2,c3 = st.columns(3)
    c1.metric("Margin-risk accounts", int((cust.risk=="Margin Risk").sum()))
    c2.metric("Median cost / revenue", pct(cust.cost_to_revenue.median()))
    c3.metric("Revenue at risk", money(cust.loc[cust.risk=="Margin Risk","mrr"].sum()))
    st.plotly_chart(px.scatter(cust, x="mrr", y="cloud_cost", color="risk", size="seats", hover_data=["customer_id","plan","industry"], title="Customer revenue vs. allocated cloud cost"), use_container_width=True)
    st.dataframe(cust.sort_values("cost_to_revenue", ascending=False).head(30).style.format({"mrr":"${:,.0f}","cloud_cost":"${:,.0f}","cost_to_revenue":"{:.1%}","gross_margin":"{:.1%}"}), use_container_width=True)

elif page == "FinOps & Optimization":
    env_share = pd.DataFrame({"environment":["Production","Staging","Development"], "cost":[latest_cost*.72, latest_cost*.13, latest_cost*.15]})
    c1,c2 = st.columns(2)
    with c1: st.plotly_chart(px.bar(env_share, x="environment", y="cost", text_auto="$.2s", title="Cost by environment"), use_container_width=True)
    with c2: st.plotly_chart(px.line(trend, x="month", y=["cloud_cost","budget"], markers=True, title="Actual cost vs. budget"), use_container_width=True)
    st.subheader("Scenario simulator")
    ai_reduction = st.slider("AI Assistant unit-cost reduction", 0, 40, 15)/100
    dev_reduction = st.slider("Development environment reduction", 0, 60, 30)/100
    ai_cost = latest.loc[latest.feature.eq("AI Assistant"),"cloud_cost"].sum()
    savings = ai_cost*ai_reduction + latest_cost*.15*dev_reduction
    st.metric("Estimated monthly savings", money(savings), f"New estimated margin: {pct((latest_mrr-(latest_cost-savings))/latest_mrr)}")
    st.dataframe(pd.DataFrame([["AI Assistant", "High compute unit cost", "Caching, model routing, usage-based pricing", "High"], ["Development", "Always-on non-production resources", "Scheduled shutdown and rightsizing", "High"], ["File Storage", "Long retention and low adoption", "S3 lifecycle policy and storage tiers", "Medium"], ["Athena", "Excess data scanning", "Parquet, partitioning, and column pruning", "Medium"]], columns=["Area","Root cause","Recommendation","Priority"]), use_container_width=True, hide_index=True)

elif page == "Decision Assistant":
    st.subheader("Traceable decision assistant")
    question = st.selectbox("Business question", ["What is the largest cost driver?", "Which customers need pricing review?", "Where should FinOps act first?", "Is growth healthy?"])
    if question == "What is the largest cost driver?":
        row = latest.groupby("feature", as_index=False).cloud_cost.sum().nlargest(1,"cloud_cost").iloc[0]
        answer = f"{row.feature} is the largest feature cost driver at {money(row.cloud_cost)} this month."
    elif question == "Which customers need pricing review?":
        cust_cost = latest.groupby("customer_id", as_index=False).cloud_cost.sum(); cust = latest_customers.merge(cust_cost, on="customer_id"); cust["ratio"] = cust.cloud_cost/cust.mrr
        answer = f"{(cust.ratio>.25).sum()} accounts exceed the 25% cloud-cost-to-revenue threshold. Prioritize the highest-ratio Enterprise and Professional accounts."
    elif question == "Where should FinOps act first?": answer = "Start with AI Assistant unit cost, scheduled shutdown of development resources, and Athena scan optimization."
    else: answer = f"MRR is {money(latest_mrr)} and infrastructure margin is {pct(margin)}. Growth is healthy only when revenue continues to outpace cloud-cost growth."
    st.success(answer)
    st.caption("Deterministic and grounded only in dashboard metrics—no hidden API or fabricated evidence.")

else:
    st.subheader("Data & AWS Architecture")
    st.code("Synthetic SaaS data → Amazon S3 → Lambda / Glue → Glue Catalog → Athena → Streamlit / QuickSight\n                                      ↓\n                               CloudWatch + SNS + AWS Budgets")
    st.markdown("""
### Data model
- **Customer-month:** plan, MRR, seats, segment, region, industry
- **Customer-month-feature:** active users, usage units, allocated cloud cost
- **Feature-service:** AWS service attribution for FinOps analysis

### AWS design decisions
- **S3** for analytical object storage
- **Lambda / Glue** for repeatable managed transformation
- **Athena** for serverless SQL and scan-cost optimization
- **CloudWatch + SNS** for pipeline and anomaly alerts
- **Budgets** for threshold governance
- **IAM least privilege** and encryption by default

### Portfolio controls
Synthetic data, reproducible seed, no AWS credentials, no personal data, and explainable KPI thresholds.
""")
    st.download_button("Download latest customer-feature data", latest.to_csv(index=False), "flowpilot_latest.csv", "text/csv")
