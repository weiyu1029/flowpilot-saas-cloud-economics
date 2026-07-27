"""Deterministic analytics copilot used without any external API key."""
from __future__ import annotations

import re
import pandas as pd

from src.ui import money, percent

SAMPLE_QUESTIONS = [
    "Why did cloud cost change in the latest month?",
    "Which feature is the highest optimization priority?",
    "Which AWS service costs the most?",
    "How many customers are margin risk?",
    "What should we do about AI Assistant cost?",
    "Which plan has the strongest gross margin?",
    "What are the top three recommendations?",
    "Did we exceed budget in the latest month?",
]


def _latest_and_prior(df: pd.DataFrame, value_col: str):
    months = sorted(df["month"].dropna().unique())
    latest_month = months[-1]
    prior_month = months[-2] if len(months) > 1 else None
    latest = df[df["month"] == latest_month][value_col].sum()
    prior = df[df["month"] == prior_month][value_col].sum() if prior_month is not None else None
    return pd.Timestamp(latest_month), float(latest), float(prior) if prior is not None else None


def answer_question(
    question: str,
    customer_monthly: pd.DataFrame,
    feature_metrics: pd.DataFrame,
    service_monthly: pd.DataFrame,
    recommendations: pd.DataFrame,
    budgets: pd.DataFrame,
) -> str:
    q = re.sub(r"\s+", " ", question.lower()).strip()
    latest_month = customer_monthly["month"].max()
    latest_customer = customer_monthly[customer_monthly["month"] == latest_month]
    latest_feature = feature_metrics[feature_metrics["month"] == feature_metrics["month"].max()]
    latest_service = service_monthly[service_monthly["month"] == service_monthly["month"].max()]

    if any(word in q for word in ["why", "change", "increase", "decrease", "latest month"]):
        month, current, prior = _latest_and_prior(customer_monthly, "allocated_cloud_cost_usd")
        if prior is None:
            return f"The latest filtered cloud cost is {money(current)} for {month:%B %Y}."
        delta = current - prior
        direction = "increased" if delta >= 0 else "decreased"
        top_features = latest_feature.nlargest(3, "feature_cloud_cost_usd")[["feature_name", "feature_cloud_cost_usd"]]
        drivers = ", ".join(f"{r.feature_name} ({money(r.feature_cloud_cost_usd)})" for r in top_features.itertuples())
        return (
            f"Allocated cloud cost {direction} by {money(abs(delta))} ({abs(delta/prior):.1%}) to {money(current)} in {month:%B %Y}. "
            f"The largest current feature cost pools are {drivers}. Review the feature trend and anomaly pages before attributing causation."
        )

    if "feature" in q or "optimization priority" in q:
        row = latest_feature.sort_values(["economics_quadrant", "cost_per_active_user_usd"], ascending=[True, False])
        priority = latest_feature[latest_feature["economics_quadrant"] == "Optimization Priority"].sort_values("feature_cloud_cost_usd", ascending=False)
        if priority.empty:
            priority = latest_feature.sort_values("cost_per_active_user_usd", ascending=False)
        r = priority.iloc[0]
        return (
            f"{r['feature_name']} is the strongest current optimization candidate: {percent(r['feature_adoption_rate'])} adoption, "
            f"{money(r['feature_cloud_cost_usd'])} monthly direct cost, and {money(r['cost_per_active_user_usd'], 2)} per active user. "
            f"Its portfolio classification is **{r['economics_quadrant']}**."
        )

    if "service" in q or "aws" in q:
        service = latest_service.groupby("aws_service", as_index=False)["cost_usd"].sum().sort_values("cost_usd", ascending=False).iloc[0]
        return f"The highest-cost AWS service in the latest month is **{service['aws_service']}** at {money(service['cost_usd'])}. Use the FinOps page to break it down by environment and cost category."

    if any(term in q for term in ["margin risk", "customer risk", "at risk"]):
        risk = latest_customer[latest_customer["margin_risk_tier"] == "Margin Risk"]
        return (
            f"There are **{len(risk):,} margin-risk customers** in the current filtered portfolio, representing "
            f"{money(risk['mrr_usd'].sum())} MRR. Their median cost-to-revenue ratio is {percent(risk['cost_to_revenue_ratio'].median())}."
        )

    if "ai assistant" in q or "bedrock" in q or "token" in q:
        ai = latest_feature[latest_feature["feature_name"] == "AI Assistant"].iloc[0]
        return (
            f"AI Assistant has {percent(ai['feature_adoption_rate'])} adoption and costs {money(ai['feature_cloud_cost_usd'])} per month, "
            f"or {money(ai['cost_per_active_user_usd'], 2)} per active user. Recommended controls are semantic caching, token limits, model routing, "
            f"usage telemetry, and an AI overage price above plan allowances."
        )

    if "plan" in q or "gross margin" in q:
        plan = latest_customer.groupby("plan_type", as_index=False).agg(mrr_usd=("mrr_usd", "sum"), cost=("allocated_cloud_cost_usd", "sum"))
        plan["gross_margin"] = 1 - plan["cost"] / plan["mrr_usd"]
        best = plan.sort_values("gross_margin", ascending=False).iloc[0]
        return f"The strongest current plan-level gross margin is **{best['plan_type']}** at {percent(best['gross_margin'])}, based on allocated cloud infrastructure cost."

    if "recommend" in q or "top three" in q or "action" in q:
        top = recommendations.nlargest(3, "priority_score")
        bullets = "\n".join(
            f"{i+1}. **{r.issue}** — {r.recommended_action} Estimated monthly impact: {money(r.estimated_total_monthly_impact_usd)}."
            for i, r in enumerate(top.itertuples())
        )
        return f"Top recommended actions:\n\n{bullets}"

    if "budget" in q or "variance" in q:
        latest = budgets.sort_values("month").iloc[-1]
        status = "over" if latest["variance_usd"] > 0 else "under"
        return (
            f"The latest month is {status} budget by {money(abs(latest['variance_usd']))} ({abs(latest['variance_pct']):.1%}). "
            f"Actual cost is {money(latest['actual_cost_usd'])} versus a {money(latest['budget_usd'])} budget."
        )

    return (
        "I can answer questions about cost changes, feature economics, AWS service cost, customer margin risk, "
        "AI Assistant economics, plan margin, budgets, and prioritized recommendations. Try one of the sample questions."
    )
