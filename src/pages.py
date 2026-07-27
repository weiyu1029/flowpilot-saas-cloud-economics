"""Page rendering functions for the FlowPilot portfolio application."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data import filter_by_customer_month_keys, monthly_portfolio, recompute_feature_metrics
from src.insights import SAMPLE_QUESTIONS, answer_question
from src.ui import PALETTE, QUADRANT_COLORS, RISK_COLORS, compact, delta_money, footer, hero, insight_card, money, percent

PLOT_CONFIG = {"displayModeBar": False, "responsive": True}


def _latest_pair(df: pd.DataFrame):
    ordered = df.sort_values("month")
    latest = ordered.iloc[-1]
    previous = ordered.iloc[-2] if len(ordered) > 1 else None
    return latest, previous


def executive_page(data, filtered_customer, feature_metrics, filters):
    hero(
        "FlowPilot Cloud Economics Command Center",
        "Connect SaaS product adoption, subscription revenue, AWS-style infrastructure cost, and prioritized FinOps actions.",
        ["Business Analysis", "Product Analytics", "AWS", "FinOps", "Synthetic Data"],
    )
    portfolio = monthly_portfolio(filtered_customer)
    if portfolio.empty:
        st.warning("No data matches the selected filters.")
        return
    latest, previous = _latest_pair(portfolio)
    prev_mrr = previous["mrr_usd"] if previous is not None else None
    prev_cost = previous["allocated_cloud_cost_usd"] if previous is not None else None

    cols = st.columns(6)
    cols[0].metric("MRR", money(latest["mrr_usd"]), delta_money(latest["mrr_usd"], prev_mrr))
    cols[1].metric("Cloud cost", money(latest["allocated_cloud_cost_usd"]), delta_money(latest["allocated_cloud_cost_usd"], prev_cost), delta_color="inverse")
    cols[2].metric("Gross margin", percent(latest["estimated_gross_margin_pct"]), f"Cost ratio {percent(latest['cost_to_revenue_ratio'])}")
    cols[3].metric("Active customers", f"{int(latest['active_customers']):,}")
    cols[4].metric("Margin-risk customers", f"{int(latest['margin_risk_customers']):,}", money(latest["revenue_at_risk_usd"]) + " MRR at risk", delta_color="inverse")
    cols[5].metric("Customer health", f"{latest['avg_health_score']:.1f}/100")

    left, right = st.columns([1.45, 1])
    with left:
        trend = portfolio.copy()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trend["month"], y=trend["mrr_usd"], name="MRR", mode="lines+markers", line=dict(color=PALETTE["blue"], width=3)))
        fig.add_trace(go.Scatter(x=trend["month"], y=trend["allocated_cloud_cost_usd"], name="Allocated cloud cost", mode="lines+markers", line=dict(color=PALETTE["red"], width=3)))
        fig.update_layout(title="Revenue and cloud-cost trend", yaxis_tickprefix="$", hovermode="x unified", legend_orientation="h", margin=dict(l=10, r=10, t=55, b=10), height=390)
        st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)
    with right:
        latest_service = data["service_monthly"][data["service_monthly"]["month"] == data["service_monthly"]["month"].max()]
        service = latest_service.groupby("aws_service", as_index=False)["cost_usd"].sum().nlargest(8, "cost_usd")
        fig = px.bar(service.sort_values("cost_usd"), x="cost_usd", y="aws_service", orientation="h", title="Latest company-wide AWS service cost", labels={"cost_usd": "Cost (USD)", "aws_service": ""}, color="cost_usd", color_continuous_scale="Blues")
        fig.update_layout(coloraxis_showscale=False, margin=dict(l=10, r=10, t=55, b=10), height=390)
        st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)

    st.subheader("Executive signals")
    c1, c2, c3 = st.columns(3)
    latest_feature = feature_metrics[feature_metrics["month"] == feature_metrics["month"].max()]
    top_cost = latest_feature.sort_values("feature_cloud_cost_usd", ascending=False).iloc[0]
    top_risk = latest_feature[latest_feature["economics_quadrant"] == "Optimization Priority"].sort_values("cost_per_active_user_usd", ascending=False).iloc[0]
    with c1:
        insight_card("Largest feature cost pool", f"{top_cost['feature_name']} contributes {money(top_cost['feature_cloud_cost_usd'])} in direct monthly cost and {percent(top_cost['cost_share_pct'])} of feature-attributed spend.")
    with c2:
        insight_card("Optimization priority", f"{top_risk['feature_name']} combines {percent(top_risk['feature_adoption_rate'])} adoption with {money(top_risk['cost_per_active_user_usd'], 2)} cost per active user.")
    with c3:
        latest_budget = data["budgets"].sort_values("month").iloc[-1]
        insight_card("Budget position", f"Company-wide actual cost is {money(latest_budget['actual_cost_usd'])}, {('over' if latest_budget['variance_usd'] > 0 else 'under')} budget by {money(abs(latest_budget['variance_usd']))}.")

    st.subheader("Cost and growth diagnostic")
    diagnostic = portfolio.copy()
    diagnostic["mrr_growth"] = diagnostic["mrr_usd"].pct_change()
    diagnostic["cost_growth"] = diagnostic["allocated_cloud_cost_usd"].pct_change()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=diagnostic["month"], y=diagnostic["mrr_growth"], name="MRR growth", marker_color=PALETTE["green"]))
    fig.add_trace(go.Bar(x=diagnostic["month"], y=diagnostic["cost_growth"], name="Cloud-cost growth", marker_color=PALETTE["amber"]))
    fig.update_layout(barmode="group", yaxis_tickformat=".0%", hovermode="x unified", title="Month-over-month growth: revenue vs cloud cost", legend_orientation="h", height=360, margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)
    footer()


def feature_page(data, filtered_customer, feature_metrics, filters):
    hero("Product Feature Economics", "Evaluate feature adoption, unit cost, cost growth, and investment priority.", ["Product", "Unit Economics", "Feature Adoption"])
    if feature_metrics.empty:
        st.warning("No data matches the selected filters.")
        return
    latest_month = feature_metrics["month"].max()
    latest = feature_metrics[feature_metrics["month"] == latest_month].copy()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Feature-attributed cost", money(latest["feature_cloud_cost_usd"].sum()))
    k2.metric("Median adoption", percent(latest["feature_adoption_rate"].median()))
    k3.metric("Highest unit cost", money(latest["cost_per_active_user_usd"].max(), 2))
    k4.metric("Optimization-priority features", int((latest["economics_quadrant"] == "Optimization Priority").sum()))

    left, right = st.columns([1.4, 1])
    with left:
        fig = px.scatter(
            latest,
            x="feature_adoption_rate", y="cost_per_active_user_usd", size="feature_cloud_cost_usd",
            color="economics_quadrant", text="feature_name", hover_data=["active_users", "cost_share_pct"],
            color_discrete_map=QUADRANT_COLORS,
            title=f"Feature adoption vs cost per active user — {latest_month:%B %Y}",
            labels={"feature_adoption_rate": "Feature adoption", "cost_per_active_user_usd": "Cost per active user (USD)", "economics_quadrant": "Economics quadrant"},
        )
        fig.update_traces(textposition="top center")
        fig.update_xaxes(tickformat=".0%")
        fig.update_layout(height=500, margin=dict(l=10, r=10, t=60, b=10), legend_orientation="h")
        st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)
    with right:
        cost_rank = latest.sort_values("feature_cloud_cost_usd")
        fig = px.bar(cost_rank, x="feature_cloud_cost_usd", y="feature_name", orientation="h", color="economics_quadrant", color_discrete_map=QUADRANT_COLORS, title="Direct monthly cost by feature", labels={"feature_cloud_cost_usd": "Cost (USD)", "feature_name": ""})
        fig.update_layout(height=500, margin=dict(l=10, r=10, t=60, b=10), showlegend=False)
        st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)

    feature_choice = st.selectbox("Deep-dive feature", latest.sort_values("feature_cloud_cost_usd", ascending=False)["feature_name"].tolist())
    trend = feature_metrics[feature_metrics["feature_name"] == feature_choice].sort_values("month")
    a, b = st.columns(2)
    with a:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trend["month"], y=trend["feature_cloud_cost_usd"], mode="lines+markers", name="Cost", line=dict(color=PALETTE["red"], width=3)))
        fig.update_layout(title=f"{feature_choice}: cloud-cost trend", yaxis_tickprefix="$", height=350, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)
    with b:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trend["month"], y=trend["feature_adoption_rate"], mode="lines+markers", name="Adoption", line=dict(color=PALETTE["blue"], width=3), fill="tozeroy"))
        fig.update_layout(title=f"{feature_choice}: adoption trend", yaxis_tickformat=".0%", height=350, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)

    table = latest[["feature_name", "product_area", "feature_adoption_rate", "active_users", "feature_cloud_cost_usd", "cost_per_active_user_usd", "mom_cost_growth_pct", "economics_quadrant"]].sort_values("feature_cloud_cost_usd", ascending=False)
    st.dataframe(
        table,
        hide_index=True,
        width="stretch",
        column_config={
            "feature_adoption_rate": st.column_config.ProgressColumn("Adoption", format="percent", min_value=0, max_value=1),
            "feature_cloud_cost_usd": st.column_config.NumberColumn("Cloud cost", format="$%.0f"),
            "cost_per_active_user_usd": st.column_config.NumberColumn("Cost / active user", format="$%.2f"),
            "mom_cost_growth_pct": st.column_config.NumberColumn("MoM cost growth", format="percent"),
        },
    )
    footer()


def customer_page(data, filtered_customer, feature_metrics, filters):
    hero("Customer Profitability Monitor", "Prioritize margin-risk accounts, pricing reviews, and Customer Success outreach.", ["Customer Success", "Revenue Operations", "Pricing"])
    if filtered_customer.empty:
        st.warning("No data matches the selected filters.")
        return
    latest_month = filtered_customer["month"].max()
    latest = filtered_customer[filtered_customer["month"] == latest_month].copy()
    latest["bubble_size"] = latest["active_users"].clip(lower=1)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Customers", f"{latest['customer_id'].nunique():,}")
    c2.metric("MRR", money(latest["mrr_usd"].sum()))
    c3.metric("Allocated cost", money(latest["allocated_cloud_cost_usd"].sum()))
    c4.metric("Revenue at risk", money(latest["revenue_at_risk_usd"].sum()))
    c5.metric("Median health score", f"{latest['customer_health_score'].median():.1f}")

    fig = px.scatter(
        latest,
        x="mrr_usd", y="allocated_cloud_cost_usd", size="bubble_size", color="margin_risk_tier",
        hover_name="company_name", hover_data=["plan_type", "industry", "region", "active_users", "feature_adoption_rate", "cost_to_revenue_ratio"],
        color_discrete_map=RISK_COLORS,
        title=f"Customer revenue vs allocated cloud cost — {latest_month:%B %Y}",
        labels={"mrr_usd": "Monthly recurring revenue (USD)", "allocated_cloud_cost_usd": "Allocated cloud cost (USD)", "margin_risk_tier": "Risk tier"},
        log_x=True,
    )
    # 25% margin-risk line.
    x_vals = np.linspace(max(1, latest["mrr_usd"].min()), latest["mrr_usd"].max(), 200)
    fig.add_trace(go.Scatter(x=x_vals, y=x_vals * 0.25, mode="lines", name="25% risk threshold", line=dict(color=PALETTE["red"], dash="dash")))
    fig.update_layout(height=520, legend_orientation="h", margin=dict(l=10, r=10, t=60, b=10))
    st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)

    left, right = st.columns(2)
    with left:
        plan = latest.groupby("plan_type", as_index=False).agg(mrr=("mrr_usd", "sum"), cost=("allocated_cloud_cost_usd", "sum"), customers=("customer_id", "nunique"))
        plan["gross_margin"] = 1 - plan["cost"] / plan["mrr"]
        fig = px.bar(plan, x="plan_type", y="gross_margin", color="plan_type", text=plan["gross_margin"].map(lambda x: f"{x:.1%}"), title="Estimated infrastructure gross margin by plan", labels={"gross_margin": "Gross margin", "plan_type": "Plan"})
        fig.update_yaxes(tickformat=".0%")
        fig.update_layout(showlegend=False, height=380, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)
    with right:
        segment = latest.groupby("company_size_segment", as_index=False).agg(mrr=("mrr_usd", "sum"), cost=("allocated_cloud_cost_usd", "sum"))
        segment["cost_ratio"] = segment["cost"] / segment["mrr"]
        fig = px.bar(segment, x="company_size_segment", y="cost_ratio", text=segment["cost_ratio"].map(lambda x: f"{x:.1%}"), title="Cost-to-revenue ratio by customer segment", labels={"cost_ratio": "Cost-to-revenue ratio", "company_size_segment": "Segment"}, color="cost_ratio", color_continuous_scale="RdYlGn_r")
        fig.update_yaxes(tickformat=".0%")
        fig.update_layout(coloraxis_showscale=False, height=380, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)

    st.subheader("Priority account worklist")
    worklist = latest.sort_values(["margin_risk_tier", "cost_to_revenue_ratio", "mrr_usd"], ascending=[False, False, False]).copy()
    worklist["recommended_action"] = np.select(
        [
            worklist["cost_to_revenue_ratio"] > 0.25,
            worklist["feature_adoption_rate"] < 0.45,
            worklist["high_severity_tickets"] > 0,
        ],
        ["Pricing review / usage overage", "Adoption and onboarding plan", "Executive support escalation"],
        default="Monitor",
    )
    st.dataframe(
        worklist[["company_name", "plan_type", "region", "mrr_usd", "allocated_cloud_cost_usd", "cost_to_revenue_ratio", "feature_adoption_rate", "customer_health_score", "margin_risk_tier", "recommended_action"]].head(40),
        hide_index=True, width="stretch",
        column_config={
            "mrr_usd": st.column_config.NumberColumn("MRR", format="$%.0f"),
            "allocated_cloud_cost_usd": st.column_config.NumberColumn("Cloud cost", format="$%.0f"),
            "cost_to_revenue_ratio": st.column_config.ProgressColumn("Cost / revenue", format="percent", min_value=0, max_value=0.6),
            "feature_adoption_rate": st.column_config.ProgressColumn("Feature adoption", format="percent", min_value=0, max_value=1),
            "customer_health_score": st.column_config.ProgressColumn("Health score", format="%.0f", min_value=0, max_value=100),
        },
    )
    footer()


def finops_page(data, filtered_customer, feature_metrics, filters):
    hero("AWS FinOps & Reliability", "Track service-level spend, environment waste, budget variance, and operational anomalies.", ["FinOps", "Cloud Operations", "Reliability"])
    service = data["service_monthly"]
    service = service[service["month"].between(filters["start_month"], filters["end_month"])]
    budgets = data["budgets"][data["budgets"]["month"].between(filters["start_month"], filters["end_month"])]
    latest_month = service["month"].max()
    latest = service[service["month"] == latest_month]
    latest_budget = budgets[budgets["month"] == budgets["month"].max()].iloc[0]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Actual cloud cost", money(latest["cost_usd"].sum()))
    c2.metric("Budget", money(latest_budget["budget_usd"]))
    c3.metric("Budget variance", money(latest_budget["variance_usd"]), percent(latest_budget["variance_pct"]), delta_color="inverse")
    c4.metric("Non-production cost", money(latest[latest["environment"] != "production"]["cost_usd"].sum()))
    c5.metric("Detected anomalies", int((data["anomalies"]["month"] == latest_month).sum()))

    left, right = st.columns([1.3, 1])
    with left:
        env = service.groupby(["month", "environment"], as_index=False)["cost_usd"].sum()
        fig = px.area(env, x="month", y="cost_usd", color="environment", title="Cloud cost by environment", labels={"cost_usd": "Cost (USD)", "environment": "Environment"}, color_discrete_map={"production": PALETTE["blue"], "development": PALETTE["amber"], "staging": PALETTE["cyan"]})
        fig.update_layout(height=420, hovermode="x unified", legend_orientation="h", margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)
    with right:
        budget_plot = budgets.copy()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=budget_plot["month"], y=budget_plot["actual_cost_usd"], name="Actual", marker_color=PALETTE["blue"]))
        fig.add_trace(go.Scatter(x=budget_plot["month"], y=budget_plot["budget_usd"], name="Budget", line=dict(color=PALETTE["red"], width=3, dash="dash")))
        fig.update_layout(title="Budget vs actual cost", yaxis_tickprefix="$", hovermode="x unified", legend_orientation="h", height=420, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)

    service_matrix = service.groupby(["aws_service", "environment"], as_index=False)["cost_usd"].sum()
    fig = px.treemap(service_matrix, path=["environment", "aws_service"], values="cost_usd", color="cost_usd", color_continuous_scale="Blues", title="Cost composition by environment and AWS service")
    fig.update_layout(height=520, margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)

    left, right = st.columns(2)
    with left:
        anomaly = data["anomalies"].copy()
        anomaly = anomaly[anomaly["month"].between(filters["start_month"], filters["end_month"])]
        st.subheader("Cost anomaly register")
        st.dataframe(anomaly.sort_values("month", ascending=False).head(30), hide_index=True, width="stretch", column_config={"deviation_pct": st.column_config.NumberColumn("Deviation", format="percent"), "metric_value": st.column_config.NumberColumn("Observed", format="$%.0f"), "rolling_mean": st.column_config.NumberColumn("3-month mean", format="$%.0f")})
    with right:
        incidents = data["incidents"]
        incidents = incidents[incidents["month"].between(filters["start_month"], filters["end_month"])]
        severity = incidents.groupby("severity", as_index=False).agg(incidents=("incident_id", "count"), downtime=("downtime_minutes", "sum"))
        fig = px.bar(severity, x="severity", y="incidents", color="downtime", title="Reliability incidents by severity", labels={"incidents": "Incident count", "severity": "Severity", "downtime": "Downtime (min)"}, color_continuous_scale="OrRd")
        fig.update_layout(height=380, coloraxis_colorbar_title="Downtime", margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)

    st.info("Company-wide infrastructure and budget charts intentionally ignore customer segment filters because shared platform cost is managed at the account/environment level.")
    footer()


def optimization_page(data, filtered_customer, feature_metrics, filters):
    hero("Optimization Center", "Turn analytics into prioritized actions with quantified savings, revenue opportunity, owners, effort, and risk.", ["Recommendations", "Prioritization", "Business Impact"])
    recs = data["recommendations"].copy().sort_values("priority_score", ascending=False)
    total_savings = recs["estimated_monthly_savings_usd"].sum()
    total_revenue = recs["estimated_monthly_revenue_uplift_usd"].sum()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Potential monthly savings", money(total_savings))
    c2.metric("Potential monthly revenue uplift", money(total_revenue))
    c3.metric("Total monthly impact", money(total_savings + total_revenue))
    c4.metric("High-confidence actions", int((recs["confidence"] == "High").sum()))

    fig = px.scatter(
        recs,
        x="effort", y="estimated_total_monthly_impact_usd", size="priority_score", color="category",
        hover_name="issue", hover_data=["owner", "confidence", "implementation_risk"],
        category_orders={"effort": ["Low", "Medium", "High"]},
        title="Impact vs implementation effort",
        labels={"estimated_total_monthly_impact_usd": "Estimated monthly impact (USD)", "effort": "Implementation effort"},
    )
    fig.update_layout(height=480, legend_orientation="h", margin=dict(l=10, r=10, t=60, b=10))
    st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)

    st.subheader("Prioritized action portfolio")
    st.dataframe(
        recs[["recommendation_id", "category", "issue", "evidence", "recommended_action", "owner", "effort", "implementation_risk", "estimated_monthly_savings_usd", "estimated_monthly_revenue_uplift_usd", "estimated_total_monthly_impact_usd", "confidence", "status"]],
        hide_index=True, width="stretch",
        column_config={
            "estimated_monthly_savings_usd": st.column_config.NumberColumn("Savings", format="$%.0f"),
            "estimated_monthly_revenue_uplift_usd": st.column_config.NumberColumn("Revenue uplift", format="$%.0f"),
            "estimated_total_monthly_impact_usd": st.column_config.NumberColumn("Total impact", format="$%.0f"),
        },
    )

    st.subheader("90-day implementation roadmap")
    roadmap = pd.DataFrame([
        ["0–30 days", "Quick wins", "Development shutdown schedules; CloudWatch retention; S3 lifecycle pilot; Athena workgroup guardrails", "Cloud Operations + Data Engineering"],
        ["31–60 days", "Product economics", "AI caching and token controls; storage quota UX; Advanced Analytics onboarding experiment", "Product + Engineering"],
        ["61–90 days", "Commercial model", "High-usage account pricing reviews; AI/API overage design; benefits tracking", "Finance + Customer Success"],
    ], columns=["Horizon", "Theme", "Actions", "Owners"])
    st.dataframe(roadmap, hide_index=True, width="stretch")
    footer()


def data_architecture_page(data, filtered_customer, feature_metrics, filters):
    hero("Data Quality & AWS Architecture", "Show that the dashboard is governed, reproducible, secure, observable, and cost-aware.", ["Data Lineage", "Security", "Reliability", "IaC"])
    dq = data["data_quality"]
    pass_rate = (dq["status"] == "PASS").mean()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Data-quality checks", len(dq))
    c2.metric("Pass rate", percent(pass_rate))
    c3.metric("Raw usage rows", compact(len(data["usage"])))
    c4.metric("Allocated cost rows", compact(len(data["cost_allocations"])))

    st.markdown("### Architecture")
    st.code(
        """Synthetic SaaS data / AWS CUR-like data
                 ↓
       Amazon S3 raw zone
                 ↓
    AWS Lambda validation + ETL
                 ↓
     S3 processed / curated zones
                 ↓
  Glue Data Catalog + Amazon Athena
                 ↓
  Streamlit / Amazon QuickSight
                 ↓
CloudWatch + SNS + AWS Budgets
                 ↓
Optional Bedrock / Claude / OpenAI RAG assistant""",
        language="text",
    )

    left, right = st.columns(2)
    with left:
        st.markdown("### Data-quality controls")
        st.dataframe(dq, hide_index=True, width="stretch")
    with right:
        st.markdown("### Security and governance controls")
        controls = pd.DataFrame([
            ["Identity", "IAM roles and least privilege", "No long-lived access keys in app code"],
            ["Storage", "S3 Block Public Access + encryption", "Separate raw, processed, and curated zones"],
            ["Network", "Private data layer; restricted administration", "Only required ports and paths"],
            ["Audit", "CloudTrail + CloudWatch", "API activity, ETL logs, alarms, retention"],
            ["Cost", "Budgets, tags, lifecycle, query limits", "Owner/environment/feature allocation"],
            ["Reliability", "Idempotent ETL + failed-event handling", "Replayable data and visible failures"],
        ], columns=["Control area", "Design", "Portfolio evidence"])
        st.dataframe(controls, hide_index=True, width="stretch")

    st.markdown("### Data lineage")
    lineage = pd.DataFrame([
        ["customers + subscriptions", "Customer and revenue grain", "customer_monthly", "Profitability and risk"],
        ["product_usage_monthly", "Feature adoption and activity", "feature_monthly", "Feature economics"],
        ["cloud_cost_allocations", "Activity-based cost allocation", "customer_monthly / feature_monthly", "Unit economics"],
        ["infrastructure_costs + budgets", "Account and environment spend", "service_environment_monthly", "FinOps"],
        ["incidents", "Reliability and business impact", "executive_monthly", "Operational context"],
    ], columns=["Source", "Transformation purpose", "Curated mart", "Business output"])
    st.dataframe(lineage, hide_index=True, width="stretch")

    with st.expander("Repository implementation evidence"):
        st.markdown(
            "- Deterministic synthetic-data generator\n"
            "- Parquet and CSV outputs\n"
            "- Automated data-quality tests\n"
            "- GitHub Actions CI\n"
            "- CloudFormation reference architecture\n"
            "- Athena DDL and analytical views\n"
            "- Least-privilege IAM examples\n"
            "- Deployment, architecture, KPI, data-dictionary, and interview documentation"
        )
    footer()


def copilot_page(data, filtered_customer, feature_metrics, filters):
    hero("Business Insights Copilot", "Ask natural-language business questions. This deployed demo uses deterministic, source-grounded analytics and requires no API key.", ["Explainable", "No API Key", "Grounded in Curated Metrics"])
    st.markdown('<div class="section-note">This is intentionally a deterministic analytics assistant. The repository also documents how to add Amazon Bedrock, Claude, or OpenAI through Streamlit secrets without exposing credentials.</div>', unsafe_allow_html=True)

    selected = st.selectbox("Start with a sample question", ["Choose a question…"] + SAMPLE_QUESTIONS)
    typed = st.chat_input("Ask about cloud cost, features, customers, plans, budgets, or recommendations")
    question = typed or (selected if selected != "Choose a question…" else None)

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        response = answer_question(question, filtered_customer, feature_metrics, data["service_monthly"], data["recommendations"], data["budgets"])
        st.session_state.messages.append({"role": "assistant", "content": response})

    if not st.session_state.messages:
        st.info("Choose a sample question or type your own question to generate a grounded explanation.")
    for msg in st.session_state.messages[-10:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    with st.expander("How the copilot remains trustworthy"):
        st.markdown(
            "1. It calculates answers from curated tables instead of inventing metrics.\n"
            "2. Every response is limited to supported business questions.\n"
            "3. Cost rates are explicitly labeled synthetic.\n"
            "4. A production LLM version should add retrieval, citations, authorization, evaluation, monitoring, and human review."
        )
    footer()
