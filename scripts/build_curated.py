"""Build analytics-ready marts and recommendation tables from raw synthetic data."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CURATED = ROOT / "data" / "curated"
CURATED.mkdir(parents=True, exist_ok=True)

DATE_COLS = {
    "customers": ["signup_date", "churn_date", "planned_upgrade_month"],
    "feature_metadata": ["release_date"],
    "subscriptions_monthly": ["month", "renewal_month"],
    "product_usage_monthly": ["month"],
    "cloud_cost_allocations_monthly": ["month"],
    "infrastructure_costs_monthly": ["month"],
    "support_tickets_monthly": ["month"],
    "incidents": ["incident_date", "month"],
    "budgets_monthly": ["month"],
}


def load(name: str) -> pd.DataFrame:
    path = RAW / f"{name}.parquet"
    df = pd.read_parquet(path)
    for col in DATE_COLS.get(name, []):
        if col in df:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def save(df: pd.DataFrame, name: str) -> None:
    df.to_parquet(CURATED / f"{name}.parquet", index=False)
    df.to_csv(CURATED / f"{name}.csv", index=False, date_format="%Y-%m-%d")


def build_customer_monthly(
    customers: pd.DataFrame,
    subscriptions: pd.DataFrame,
    usage: pd.DataFrame,
    costs: pd.DataFrame,
    infrastructure: pd.DataFrame,
    support: pd.DataFrame,
) -> pd.DataFrame:
    usage_agg = usage.groupby(["month", "customer_id"], as_index=False).agg(
        eligible_features=("eligible_flag", "sum"),
        adopted_features=("feature_used_flag", "sum"),
        active_users=("active_users", "max"),
        login_count=("login_count", "sum"),
        workflow_runs=("workflow_runs", "sum"),
        api_calls=("api_calls", "sum"),
        storage_gb=("storage_gb", "sum"),
        compute_minutes=("compute_minutes", "sum"),
        ai_tokens_million=("ai_tokens_million", "sum"),
        athena_scanned_gb=("athena_scanned_gb", "sum"),
    )
    usage_agg["feature_adoption_rate"] = usage_agg["adopted_features"] / usage_agg["eligible_features"].replace(0, np.nan)

    direct = costs.groupby(["month", "customer_id"], as_index=False)["cost_usd"].sum().rename(columns={"cost_usd": "direct_cloud_cost_usd"})
    monthly_infra = infrastructure.groupby("month", as_index=False)["cost_usd"].sum().rename(columns={"cost_usd": "total_cloud_cost_usd"})
    monthly_direct = direct.groupby("month", as_index=False)["direct_cloud_cost_usd"].sum()
    monthly_overhead = monthly_infra.merge(monthly_direct, on="month", how="left")
    monthly_overhead["shared_overhead_usd"] = monthly_overhead["total_cloud_cost_usd"] - monthly_overhead["direct_cloud_cost_usd"]

    df = subscriptions.merge(customers, on="customer_id", how="left").merge(usage_agg, on=["month", "customer_id"], how="left").merge(direct, on=["month", "customer_id"], how="left").merge(support, on=["month", "customer_id"], how="left")
    df = df.merge(monthly_overhead[["month", "shared_overhead_usd"]], on="month", how="left")
    monthly_mrr = df.groupby("month")["mrr_usd"].transform("sum")
    df["shared_cost_allocation_usd"] = df["shared_overhead_usd"] * (df["mrr_usd"] / monthly_mrr)
    df["allocated_cloud_cost_usd"] = df["direct_cloud_cost_usd"].fillna(0) + df["shared_cost_allocation_usd"].fillna(0)
    df["cost_to_revenue_ratio"] = df["allocated_cloud_cost_usd"] / df["mrr_usd"].replace(0, np.nan)
    df["estimated_gross_margin_pct"] = 1 - df["cost_to_revenue_ratio"]
    df["cost_per_active_user_usd"] = df["allocated_cloud_cost_usd"] / df["active_users"].replace(0, np.nan)
    df["margin_risk_tier"] = pd.cut(
        df["cost_to_revenue_ratio"], bins=[-np.inf, 0.10, 0.25, np.inf],
        labels=["Healthy", "Monitor", "Margin Risk"],
    ).astype(str)
    df["customer_health_score"] = (
        60
        - df["cost_to_revenue_ratio"].clip(0, 0.6) * 80
        + df["feature_adoption_rate"].fillna(0) * 25
        + (df["csat_score"].fillna(4.5) - 3) * 8
        - df["high_severity_tickets"].fillna(0) * 5
    ).clip(0, 100)
    df["revenue_at_risk_usd"] = np.where(df["margin_risk_tier"] == "Margin Risk", df["mrr_usd"], 0.0)
    return df


def build_feature_monthly(usage: pd.DataFrame, costs: pd.DataFrame, subscriptions: pd.DataFrame, features: pd.DataFrame) -> pd.DataFrame:
    eligible = usage.groupby(["month", "feature_name"], as_index=False).agg(
        eligible_customers=("customer_id", "nunique"),
        adopted_customers=("feature_used_flag", "sum"),
        active_users=("active_users", "sum"),
        workflow_runs=("workflow_runs", "sum"),
        api_calls=("api_calls", "sum"),
        storage_gb=("storage_gb", "sum"),
        compute_minutes=("compute_minutes", "sum"),
        ai_tokens_million=("ai_tokens_million", "sum"),
        athena_scanned_gb=("athena_scanned_gb", "sum"),
    )
    # adopted_customers needs unique customer count where feature_used=True.
    adopted = usage[usage["feature_used_flag"]].groupby(["month", "feature_name"])["customer_id"].nunique().rename("adopted_customers_unique").reset_index()
    eligible = eligible.drop(columns="adopted_customers").merge(adopted, on=["month", "feature_name"], how="left").rename(columns={"adopted_customers_unique": "adopted_customers"})
    eligible["adopted_customers"] = eligible["adopted_customers"].fillna(0)
    eligible["feature_adoption_rate"] = eligible["adopted_customers"] / eligible["eligible_customers"].replace(0, np.nan)

    feature_cost = costs.groupby(["month", "feature_name"], as_index=False)["cost_usd"].sum().rename(columns={"cost_usd": "feature_cloud_cost_usd"})
    df = eligible.merge(feature_cost, on=["month", "feature_name"], how="left").merge(features, on="feature_name", how="left")
    df["cost_per_active_user_usd"] = df["feature_cloud_cost_usd"] / df["active_users"].replace(0, np.nan)
    df["cost_per_adopted_customer_usd"] = df["feature_cloud_cost_usd"] / df["adopted_customers"].replace(0, np.nan)
    df["cost_share_pct"] = df["feature_cloud_cost_usd"] / df.groupby("month")["feature_cloud_cost_usd"].transform("sum")
    df["mom_cost_growth_pct"] = df.sort_values("month").groupby("feature_name")["feature_cloud_cost_usd"].pct_change()
    df["mom_adoption_growth_pct"] = df.sort_values("month").groupby("feature_name")["feature_adoption_rate"].pct_change()

    adoption_median = df.groupby("month")["feature_adoption_rate"].transform("median")
    cost_user_median = df.groupby("month")["cost_per_active_user_usd"].transform("median")
    df["economics_quadrant"] = np.select(
        [
            (df["feature_adoption_rate"] >= adoption_median) & (df["cost_per_active_user_usd"] < cost_user_median),
            (df["feature_adoption_rate"] >= adoption_median) & (df["cost_per_active_user_usd"] >= cost_user_median),
            (df["feature_adoption_rate"] < adoption_median) & (df["cost_per_active_user_usd"] < cost_user_median),
        ],
        ["Efficient Winner", "Scale Carefully", "Monitor"],
        default="Optimization Priority",
    )
    return df


def build_service_monthly(infra: pd.DataFrame, budgets: pd.DataFrame) -> pd.DataFrame:
    df = infra.groupby(["month", "aws_service", "environment", "cost_category"], as_index=False)["cost_usd"].sum()
    total = df.groupby("month")["cost_usd"].transform("sum")
    df["monthly_cost_share_pct"] = df["cost_usd"] / total
    df = df.merge(budgets[["month", "budget_usd", "variance_usd", "variance_pct"]], on="month", how="left")
    return df


def build_executive(customer_monthly: pd.DataFrame, infra: pd.DataFrame, budgets: pd.DataFrame, incidents: pd.DataFrame) -> pd.DataFrame:
    rev = customer_monthly.groupby("month", as_index=False).agg(
        mrr_usd=("mrr_usd", "sum"),
        active_customers=("customer_id", "nunique"),
        total_active_users=("active_users", "sum"),
        revenue_at_risk_usd=("revenue_at_risk_usd", "sum"),
        avg_customer_health_score=("customer_health_score", "mean"),
        margin_risk_customers=("margin_risk_tier", lambda s: int((s == "Margin Risk").sum())),
    )
    cost = infra.groupby("month", as_index=False)["cost_usd"].sum().rename(columns={"cost_usd": "total_cloud_cost_usd"})
    inc = incidents.groupby("month", as_index=False).agg(
        incident_count=("incident_id", "count"),
        downtime_minutes=("downtime_minutes", "sum"),
        estimated_business_impact_usd=("estimated_business_impact_usd", "sum"),
    )
    df = rev.merge(cost, on="month").merge(budgets, on="month").merge(inc, on="month", how="left")
    df["arr_run_rate_usd"] = df["mrr_usd"] * 12
    df["cloud_cost_to_revenue_ratio"] = df["total_cloud_cost_usd"] / df["mrr_usd"]
    df["estimated_gross_margin_pct"] = 1 - df["cloud_cost_to_revenue_ratio"]
    df["cost_per_active_customer_usd"] = df["total_cloud_cost_usd"] / df["active_customers"]
    df["cost_per_active_user_usd"] = df["total_cloud_cost_usd"] / df["total_active_users"]
    df["mrr_growth_pct"] = df["mrr_usd"].pct_change()
    df["cloud_cost_growth_pct"] = df["total_cloud_cost_usd"].pct_change()
    df["incident_count"] = df["incident_count"].fillna(0).astype(int)
    return df


def build_anomalies(feature_monthly: pd.DataFrame, service_monthly: pd.DataFrame) -> pd.DataFrame:
    rows = []
    service_agg = service_monthly.groupby(["month", "aws_service"], as_index=False)["cost_usd"].sum()
    for entity_type, df, entity_col, value_col in [
        ("feature", feature_monthly, "feature_name", "feature_cloud_cost_usd"),
        ("service", service_agg, "aws_service", "cost_usd"),
    ]:
        for entity, group in df.groupby(entity_col):
            g = group.sort_values("month").copy()
            if len(g) < 6:
                continue
            values = g[[value_col]].to_numpy()
            model = IsolationForest(n_estimators=150, contamination=0.12, random_state=20260721)
            g["anomaly_flag"] = model.fit_predict(values) == -1
            g["rolling_mean"] = g[value_col].rolling(3, min_periods=2).mean()
            g["deviation_pct"] = (g[value_col] - g["rolling_mean"]) / g["rolling_mean"].replace(0, np.nan)
            for _, r in g[g["anomaly_flag"]].iterrows():
                rows.append({
                    "month": r["month"], "entity_type": entity_type, "entity_name": entity,
                    "metric_name": value_col, "metric_value": round(float(r[value_col]), 2),
                    "rolling_mean": round(float(r["rolling_mean"]), 2) if pd.notna(r["rolling_mean"]) else np.nan,
                    "deviation_pct": round(float(r["deviation_pct"]), 4) if pd.notna(r["deviation_pct"]) else np.nan,
                    "severity": "High" if abs(r["deviation_pct"]) > 0.35 else "Medium",
                })
    return pd.DataFrame(rows).sort_values(["month", "severity"], ascending=[False, True])


def build_recommendations(feature_monthly: pd.DataFrame, service_monthly: pd.DataFrame, customer_monthly: pd.DataFrame) -> pd.DataFrame:
    latest_month = feature_monthly["month"].max()
    latest = feature_monthly[feature_monthly["month"] == latest_month].copy()
    latest_service = service_monthly[service_monthly["month"] == latest_month].copy()
    latest_customer = customer_monthly[customer_monthly["month"] == latest_month].copy()
    recs = []

    def add(rec_id: str, category: str, issue: str, evidence: str, action: str, owner: str, effort: str, risk: str, monthly_savings: float, revenue_uplift: float, confidence: str):
        impact = monthly_savings + revenue_uplift
        priority_score = impact / ({"Low": 1.0, "Medium": 1.7, "High": 2.6}[effort])
        recs.append({
            "recommendation_id": rec_id, "as_of_month": latest_month, "category": category,
            "issue": issue, "evidence": evidence, "recommended_action": action, "owner": owner,
            "effort": effort, "implementation_risk": risk,
            "estimated_monthly_savings_usd": round(monthly_savings, 2),
            "estimated_monthly_revenue_uplift_usd": round(revenue_uplift, 2),
            "estimated_total_monthly_impact_usd": round(impact, 2),
            "confidence": confidence, "priority_score": round(priority_score, 2), "status": "Proposed",
        })

    ai = latest.set_index("feature_name").loc["AI Assistant"]
    add("REC-001", "Product Economics", "AI Assistant cost is growing faster than monetization",
        f"AI Assistant cost is ${ai.feature_cloud_cost_usd:,.0f}/month at {ai.feature_adoption_rate:.1%} adoption and ${ai.cost_per_active_user_usd:,.2f} per active user.",
        "Introduce semantic caching, prompt/token limits, usage telemetry, and an AI usage add-on above plan allowances.",
        "Product + Engineering + Finance", "High", "Medium", ai.feature_cloud_cost_usd * 0.14, 14_500, "High")

    fs = latest.set_index("feature_name").loc["File Storage"]
    add("REC-002", "Storage Optimization", "File retention policy creates high cost relative to adoption",
        f"File Storage accounts for {fs.cost_share_pct:.1%} of direct feature cost with {fs.feature_adoption_rate:.1%} adoption.",
        "Apply S3 lifecycle policies, intelligent tiering, retention limits, and customer-facing storage quotas.",
        "Cloud Operations + Product", "Medium", "Low", fs.feature_cloud_cost_usd * 0.23, 2_500, "High")

    athena = latest_service[latest_service["aws_service"] == "Amazon Athena"]["cost_usd"].sum()
    add("REC-003", "Analytics Optimization", "Athena queries scan more data than necessary",
        f"Latest-month Athena cost is ${athena:,.0f}; raw CSV and broad scans are the primary synthetic drivers.",
        "Convert curated datasets to Parquet, partition by month, select only required columns, and enforce query workgroups.",
        "Data Engineering", "Medium", "Low", athena * 0.58, 0, "High")

    dev = latest_service[latest_service["environment"] == "development"]["cost_usd"].sum()
    add("REC-004", "Environment Governance", "Development resources remain active outside working hours",
        f"Development environment cost is ${dev:,.0f} in the latest month after a Q1 2026 spike.",
        "Schedule non-production shutdowns, set per-environment budgets, and require owner/expiration tags.",
        "Cloud Operations", "Low", "Low", dev * 0.32, 0, "High")

    risk = latest_customer[latest_customer["margin_risk_tier"] == "Margin Risk"]
    risk_mrr = risk["mrr_usd"].sum()
    add("REC-005", "Pricing", "High-usage accounts are underpriced",
        f"{len(risk):,} customers are in Margin Risk, representing ${risk_mrr:,.0f} MRR.",
        "Launch a pricing review for accounts above the 25% cost-to-revenue threshold and add usage-based API/AI overages.",
        "Finance + Customer Success", "Medium", "Medium", 0, risk_mrr * 0.055, "Medium")

    cw = latest_service[latest_service["aws_service"] == "Amazon CloudWatch"]["cost_usd"].sum()
    add("REC-006", "Observability", "Log ingestion and retention are not governed tightly",
        f"CloudWatch cost is ${cw:,.0f} in the latest month; a February 2026 logging incident demonstrated exposure.",
        "Reduce verbose logs, apply retention policies, separate audit and debug logs, and alert on ingestion anomalies.",
        "Engineering + Security", "Low", "Low", cw * 0.20, 0, "High")

    ec2 = latest_service[latest_service["aws_service"] == "Amazon EC2"]["cost_usd"].sum()
    add("REC-007", "Compute Optimization", "Shared compute requires rightsizing and commitment review",
        f"Amazon EC2 represents ${ec2:,.0f} in latest-month shared and non-production cost.",
        "Use Compute Optimizer, rightsizing, Auto Scaling, and Savings Plans only after baseline demand is stable.",
        "Cloud Operations + Finance", "Medium", "Low", ec2 * 0.16, 0, "Medium")

    qa = latest.set_index("feature_name").loc["Advanced Analytics"]
    add("REC-008", "Product Portfolio", "Advanced Analytics has low adoption and relatively high unit cost",
        f"Advanced Analytics adoption is {qa.feature_adoption_rate:.1%} with ${qa.cost_per_active_user_usd:,.2f} cost per active user.",
        "Improve onboarding and validate willingness-to-pay before increasing infrastructure investment.",
        "Product + Customer Success", "Medium", "Medium", qa.feature_cloud_cost_usd * 0.08, 4_000, "Medium")

    return pd.DataFrame(recs).sort_values("priority_score", ascending=False)


def build_data_quality_report(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    checks = []
    for name, df in tables.items():
        checks.append({"table_name": name, "check_name": "row_count_positive", "status": "PASS" if len(df) > 0 else "FAIL", "observed_value": len(df), "expected_rule": "> 0 rows"})
        checks.append({"table_name": name, "check_name": "duplicate_rows", "status": "PASS" if df.duplicated().sum() == 0 else "WARN", "observed_value": int(df.duplicated().sum()), "expected_rule": "0 full-row duplicates"})
    key_checks = [
        ("customers", ["customer_id"]),
        ("subscriptions_monthly", ["month", "customer_id"]),
        ("product_usage_monthly", ["month", "customer_id", "feature_name"]),
        ("budgets_monthly", ["month"]),
    ]
    for name, keys in key_checks:
        df = tables[name]
        dups = int(df.duplicated(keys).sum())
        checks.append({"table_name": name, "check_name": f"unique_key_{'_'.join(keys)}", "status": "PASS" if dups == 0 else "FAIL", "observed_value": dups, "expected_rule": "0 duplicate keys"})
    for name, col in [("subscriptions_monthly", "mrr_usd"), ("cloud_cost_allocations_monthly", "cost_usd"), ("infrastructure_costs_monthly", "cost_usd")]:
        neg = int((tables[name][col] < 0).sum())
        checks.append({"table_name": name, "check_name": f"nonnegative_{col}", "status": "PASS" if neg == 0 else "FAIL", "observed_value": neg, "expected_rule": "No negative values"})
    return pd.DataFrame(checks)


def main() -> None:
    customers = load("customers")
    subscriptions = load("subscriptions_monthly")
    usage = load("product_usage_monthly")
    costs = load("cloud_cost_allocations_monthly")
    infrastructure = load("infrastructure_costs_monthly")
    support = load("support_tickets_monthly")
    incidents = load("incidents")
    budgets = load("budgets_monthly")
    features = load("feature_metadata")

    customer_monthly = build_customer_monthly(customers, subscriptions, usage, costs, infrastructure, support)
    feature_monthly = build_feature_monthly(usage, costs, subscriptions, features)
    service_monthly = build_service_monthly(infrastructure, budgets)
    executive_monthly = build_executive(customer_monthly, infrastructure, budgets, incidents)
    anomalies = build_anomalies(feature_monthly, service_monthly)
    recommendations = build_recommendations(feature_monthly, service_monthly, customer_monthly)
    dq = build_data_quality_report({
        "customers": customers, "subscriptions_monthly": subscriptions,
        "product_usage_monthly": usage, "cloud_cost_allocations_monthly": costs,
        "infrastructure_costs_monthly": infrastructure, "budgets_monthly": budgets,
    })

    for name, df in {
        "customer_monthly": customer_monthly,
        "feature_monthly": feature_monthly,
        "service_environment_monthly": service_monthly,
        "executive_monthly": executive_monthly,
        "anomalies": anomalies,
        "recommendations": recommendations,
        "data_quality_report": dq,
    }.items():
        save(df, name)
        print(f"Built {name:34s} {len(df):>8,} rows")


if __name__ == "__main__":
    main()
