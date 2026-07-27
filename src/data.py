"""Data loading and filtering utilities for the Streamlit application."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CURATED = ROOT / "data" / "curated"


@st.cache_data(show_spinner=False)
def load_datasets() -> dict[str, pd.DataFrame]:
    names = {
        "customers": RAW / "customers.parquet",
        "subscriptions": RAW / "subscriptions_monthly.parquet",
        "usage": RAW / "product_usage_monthly.parquet",
        "cost_allocations": RAW / "cloud_cost_allocations_monthly.parquet",
        "infrastructure": RAW / "infrastructure_costs_monthly.parquet",
        "budgets": RAW / "budgets_monthly.parquet",
        "incidents": RAW / "incidents.parquet",
        "feature_metadata": RAW / "feature_metadata.parquet",
        "customer_monthly": CURATED / "customer_monthly.parquet",
        "feature_monthly": CURATED / "feature_monthly.parquet",
        "service_monthly": CURATED / "service_environment_monthly.parquet",
        "executive": CURATED / "executive_monthly.parquet",
        "recommendations": CURATED / "recommendations.parquet",
        "anomalies": CURATED / "anomalies.parquet",
        "data_quality": CURATED / "data_quality_report.parquet",
    }
    data = {key: pd.read_parquet(path) for key, path in names.items()}
    for df in data.values():
        for col in ["month", "signup_date", "churn_date", "release_date", "incident_date", "renewal_month", "as_of_month"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
    return data


def apply_filters(customer_monthly: pd.DataFrame, filters: dict[str, Any]) -> pd.DataFrame:
    df = customer_monthly.copy()
    df = df[df["month"].between(filters["start_month"], filters["end_month"])]
    for col, key in [
        ("region", "regions"),
        ("industry", "industries"),
        ("company_size_segment", "segments"),
        ("plan_type", "plans"),
    ]:
        selected = filters.get(key, [])
        if selected:
            df = df[df[col].isin(selected)]
    return df


def filter_by_customer_month_keys(df: pd.DataFrame, filtered_customer_monthly: pd.DataFrame) -> pd.DataFrame:
    keys = filtered_customer_monthly[["month", "customer_id"]].drop_duplicates()
    return df.merge(keys, on=["month", "customer_id"], how="inner")


def recompute_feature_metrics(
    usage: pd.DataFrame,
    costs: pd.DataFrame,
    feature_metadata: pd.DataFrame,
    filtered_customer_monthly: pd.DataFrame,
) -> pd.DataFrame:
    u = filter_by_customer_month_keys(usage, filtered_customer_monthly)
    c = filter_by_customer_month_keys(costs, filtered_customer_monthly)
    if u.empty:
        return pd.DataFrame()
    eligible = u.groupby(["month", "feature_name"], as_index=False).agg(
        eligible_customers=("customer_id", "nunique"),
        active_users=("active_users", "sum"),
        workflow_runs=("workflow_runs", "sum"),
        api_calls=("api_calls", "sum"),
        storage_gb=("storage_gb", "sum"),
        compute_minutes=("compute_minutes", "sum"),
        ai_tokens_million=("ai_tokens_million", "sum"),
        athena_scanned_gb=("athena_scanned_gb", "sum"),
    )
    adopted = (
        u[u["feature_used_flag"]]
        .groupby(["month", "feature_name"])["customer_id"]
        .nunique()
        .rename("adopted_customers")
        .reset_index()
    )
    direct = c.groupby(["month", "feature_name"], as_index=False)["cost_usd"].sum().rename(columns={"cost_usd": "feature_cloud_cost_usd"})
    out = eligible.merge(adopted, on=["month", "feature_name"], how="left").merge(direct, on=["month", "feature_name"], how="left").merge(feature_metadata, on="feature_name", how="left")
    out["adopted_customers"] = out["adopted_customers"].fillna(0)
    out["feature_cloud_cost_usd"] = out["feature_cloud_cost_usd"].fillna(0)
    out["feature_adoption_rate"] = out["adopted_customers"] / out["eligible_customers"].replace(0, np.nan)
    out["cost_per_active_user_usd"] = out["feature_cloud_cost_usd"] / out["active_users"].replace(0, np.nan)
    out["cost_per_adopted_customer_usd"] = out["feature_cloud_cost_usd"] / out["adopted_customers"].replace(0, np.nan)
    out["cost_share_pct"] = out["feature_cloud_cost_usd"] / out.groupby("month")["feature_cloud_cost_usd"].transform("sum")
    out = out.sort_values(["feature_name", "month"])
    out["mom_cost_growth_pct"] = out.groupby("feature_name")["feature_cloud_cost_usd"].pct_change()
    out["mom_adoption_growth_pct"] = out.groupby("feature_name")["feature_adoption_rate"].pct_change()
    adoption_median = out.groupby("month")["feature_adoption_rate"].transform("median")
    cpu_median = out.groupby("month")["cost_per_active_user_usd"].transform("median")
    out["economics_quadrant"] = np.select(
        [
            (out["feature_adoption_rate"] >= adoption_median) & (out["cost_per_active_user_usd"] < cpu_median),
            (out["feature_adoption_rate"] >= adoption_median) & (out["cost_per_active_user_usd"] >= cpu_median),
            (out["feature_adoption_rate"] < adoption_median) & (out["cost_per_active_user_usd"] < cpu_median),
        ],
        ["Efficient Winner", "Scale Carefully", "Monitor"],
        default="Optimization Priority",
    )
    return out


def monthly_portfolio(filtered_customer_monthly: pd.DataFrame) -> pd.DataFrame:
    if filtered_customer_monthly.empty:
        return pd.DataFrame()
    return filtered_customer_monthly.groupby("month", as_index=False).agg(
        mrr_usd=("mrr_usd", "sum"),
        allocated_cloud_cost_usd=("allocated_cloud_cost_usd", "sum"),
        active_customers=("customer_id", "nunique"),
        active_users=("active_users", "sum"),
        margin_risk_customers=("margin_risk_tier", lambda s: int((s == "Margin Risk").sum())),
        revenue_at_risk_usd=("revenue_at_risk_usd", "sum"),
        avg_health_score=("customer_health_score", "mean"),
    ).assign(
        cost_to_revenue_ratio=lambda x: x["allocated_cloud_cost_usd"] / x["mrr_usd"],
        estimated_gross_margin_pct=lambda x: 1 - x["allocated_cloud_cost_usd"] / x["mrr_usd"],
    )
