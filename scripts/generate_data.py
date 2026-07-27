"""Generate deterministic synthetic SaaS product-usage and AWS-style cloud-cost data.

The dataset is intentionally designed for portfolio analytics. Cost rates are illustrative,
not a replacement for the AWS Pricing Calculator or an actual Cost and Usage Report.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from faker import Faker

SEED = 20260721
RNG = np.random.default_rng(SEED)
FAKER = Faker("en_US")
FAKER.seed_instance(SEED)

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
CURATED = ROOT / "data" / "curated"
for path in (RAW, PROCESSED, CURATED):
    path.mkdir(parents=True, exist_ok=True)

MONTHS = pd.period_range("2025-01", "2026-06", freq="M")
MONTH_STARTS = MONTHS.to_timestamp(how="start")
MONTH_ENDS = MONTHS.to_timestamp(how="end").normalize()

INDUSTRIES = [
    "Technology", "Financial Services", "Healthcare", "Retail", "Manufacturing",
    "Professional Services", "Education", "Media", "Logistics", "Hospitality",
]
REGION_COUNTRIES = {
    "North America": ["United States", "Canada"],
    "Europe": ["United Kingdom", "Germany", "France", "Netherlands"],
    "APAC": ["Australia", "Singapore", "Japan", "India"],
    "LATAM": ["Brazil", "Mexico"],
}
REGION_PROBS = [0.52, 0.24, 0.18, 0.06]
ACCOUNT_OWNERS = ["Avery Chen", "Jordan Lee", "Maya Patel", "Noah Williams", "Sofia Garcia", "Ethan Kim"]

PLANS = pd.DataFrame(
    [
        {
            "plan_type": "Starter", "base_mrr": 149.0, "included_seats": 5,
            "seat_price": 14.0, "included_storage_gb": 50, "included_api_calls": 10_000,
            "target_cost_ratio": 0.10,
        },
        {
            "plan_type": "Professional", "base_mrr": 599.0, "included_seats": 25,
            "seat_price": 22.0, "included_storage_gb": 500, "included_api_calls": 250_000,
            "target_cost_ratio": 0.14,
        },
        {
            "plan_type": "Enterprise", "base_mrr": 2_499.0, "included_seats": 100,
            "seat_price": 31.0, "included_storage_gb": 2_000, "included_api_calls": 1_500_000,
            "target_cost_ratio": 0.18,
        },
    ]
)
PLAN_LOOKUP = PLANS.set_index("plan_type").to_dict("index")

FEATURES = pd.DataFrame(
    [
        ["Workflow Automation", "Core Platform", "2024-01-01", "Starter", "AWS Lambda", "workflow_runs", "Automate repeatable business processes"],
        ["Team Collaboration", "Collaboration", "2024-01-01", "Starter", "Amazon DynamoDB", "collaboration_actions", "Share workflows, comments, and approvals"],
        ["Dashboard Reporting", "Analytics", "2024-01-01", "Starter", "Amazon Athena", "dashboard_views", "Monitor operational KPIs"],
        ["Data Export", "Data Management", "2024-01-01", "Starter", "Amazon S3", "exports_count", "Export CSV and scheduled reports"],
        ["File Storage", "Data Management", "2024-01-01", "Starter", "Amazon S3", "storage_gb", "Store files and workflow attachments"],
        ["API Integration", "Integrations", "2024-01-01", "Professional", "Amazon API Gateway", "api_calls", "Connect external systems through APIs"],
        ["AI Assistant", "Artificial Intelligence", "2025-05-01", "Professional", "Amazon Bedrock", "ai_tokens_million", "Generate summaries and workflow recommendations"],
        ["Advanced Analytics", "Analytics", "2025-09-01", "Enterprise", "AWS Glue", "analytics_queries", "Build advanced cross-workspace analysis"],
        ["Admin Controls", "Administration", "2024-01-01", "Enterprise", "AWS Lambda", "admin_actions", "Manage enterprise governance and access"],
    ],
    columns=["feature_name", "product_area", "release_date", "minimum_plan", "primary_aws_service", "primary_usage_metric", "business_value"],
)
FEATURES["release_date"] = pd.to_datetime(FEATURES["release_date"])
PLAN_RANK = {"Starter": 1, "Professional": 2, "Enterprise": 3}

BASE_ADOPTION = {
    "Workflow Automation": 0.86,
    "Team Collaboration": 0.78,
    "Dashboard Reporting": 0.72,
    "Data Export": 0.48,
    "File Storage": 0.42,
    "API Integration": 0.66,
    "AI Assistant": 0.26,
    "Advanced Analytics": 0.08,
    "Admin Controls": 0.74,
}

FEATURE_SERVICE_MAP = {
    "Workflow Automation": [("AWS Lambda", 0.55), ("AWS Step Functions", 0.28), ("Amazon CloudWatch", 0.17)],
    "Team Collaboration": [("Amazon DynamoDB", 0.48), ("Amazon API Gateway", 0.30), ("AWS Lambda", 0.22)],
    "Dashboard Reporting": [("Amazon Athena", 0.48), ("Amazon QuickSight", 0.37), ("Amazon S3", 0.15)],
    "Data Export": [("Amazon S3", 0.42), ("AWS Lambda", 0.28), ("Data Transfer", 0.30)],
    "File Storage": [("Amazon S3", 0.68), ("Amazon CloudFront", 0.18), ("Data Transfer", 0.14)],
    "API Integration": [("Amazon API Gateway", 0.47), ("AWS Lambda", 0.33), ("Amazon CloudWatch", 0.20)],
    "AI Assistant": [("Amazon Bedrock", 0.72), ("AWS Lambda", 0.13), ("Amazon S3", 0.08), ("Amazon CloudWatch", 0.07)],
    "Advanced Analytics": [("AWS Glue", 0.38), ("Amazon Athena", 0.34), ("Amazon QuickSight", 0.28)],
    "Admin Controls": [("AWS Lambda", 0.42), ("Amazon DynamoDB", 0.38), ("Amazon CloudWatch", 0.20)],
}

ROOT_CAUSES = [
    "Unoptimized query", "Unexpected usage spike", "Misconfigured retention policy",
    "Always-on development resources", "Retry storm", "Third-party integration latency",
    "Insufficient capacity planning", "Logging verbosity increase", "Deployment regression",
]


def choose_plan(segment: str) -> str:
    if segment == "SMB":
        return RNG.choice(["Starter", "Professional"], p=[0.82, 0.18])
    if segment == "Mid-Market":
        return RNG.choice(["Starter", "Professional", "Enterprise"], p=[0.10, 0.76, 0.14])
    return RNG.choice(["Professional", "Enterprise"], p=[0.20, 0.80])


def random_date(start: pd.Timestamp, end: pd.Timestamp) -> pd.Timestamp:
    days = (end - start).days
    return start + pd.Timedelta(days=int(RNG.integers(0, max(days, 1))))


def build_customers(n_customers: int = 480) -> pd.DataFrame:
    rows: list[dict] = []
    region_names = list(REGION_COUNTRIES)
    for i in range(1, n_customers + 1):
        segment = RNG.choice(["SMB", "Mid-Market", "Enterprise"], p=[0.55, 0.30, 0.15])
        region = RNG.choice(region_names, p=REGION_PROBS)
        country = RNG.choice(REGION_COUNTRIES[region])
        signup = random_date(pd.Timestamp("2024-03-01"), pd.Timestamp("2026-04-15"))
        plan = choose_plan(segment)
        contract = RNG.choice(["Monthly", "Annual"], p=([0.34, 0.66] if plan != "Starter" else [0.46, 0.54]))
        risk_profile = RNG.choice(["Low", "Medium", "High"], p=[0.57, 0.31, 0.12])
        power_user = bool(RNG.random() < (0.08 if segment == "SMB" else 0.15 if segment == "Mid-Market" else 0.23))
        underpriced = bool(plan in {"Professional", "Enterprise"} and power_user and RNG.random() < 0.42)

        churn_date = pd.NaT
        churn_probability = {"Low": 0.05, "Medium": 0.13, "High": 0.28}[risk_profile]
        if RNG.random() < churn_probability:
            earliest = max(signup + pd.DateOffset(months=5), pd.Timestamp("2025-03-01"))
            if earliest < pd.Timestamp("2026-06-01"):
                churn_date = random_date(earliest, pd.Timestamp("2026-06-25"))

        upgrade_month = pd.NaT
        if plan != "Enterprise" and RNG.random() < (0.24 if power_user else 0.12):
            earliest = max(signup + pd.DateOffset(months=6), pd.Timestamp("2025-07-01"))
            if earliest < pd.Timestamp("2026-05-01"):
                upgrade_month = random_date(earliest, pd.Timestamp("2026-05-01")).to_period("M").to_timestamp()

        company = FAKER.unique.company()
        rows.append(
            {
                "customer_id": f"CUST-{i:04d}",
                "company_name": company,
                "industry": RNG.choice(INDUSTRIES),
                "company_size_segment": segment,
                "region": region,
                "country": country,
                "signup_date": signup.normalize(),
                "churn_date": churn_date,
                "initial_plan": plan,
                "contract_type": contract,
                "account_owner": RNG.choice(ACCOUNT_OWNERS),
                "risk_profile": risk_profile,
                "power_user_flag": power_user,
                "underpriced_flag": underpriced,
                "planned_upgrade_month": upgrade_month,
            }
        )
    return pd.DataFrame(rows)


def get_plan_for_month(customer: pd.Series, month: pd.Timestamp) -> str:
    plan = customer["initial_plan"]
    upgrade = customer["planned_upgrade_month"]
    if pd.notna(upgrade) and month >= upgrade:
        plan = "Professional" if plan == "Starter" else "Enterprise"
    return plan


def eligible_features(plan: str, month: pd.Timestamp) -> Iterable[pd.Series]:
    for _, feature in FEATURES.iterrows():
        if feature["release_date"] <= month and PLAN_RANK[plan] >= PLAN_RANK[feature["minimum_plan"]]:
            yield feature


def build_subscriptions(customers: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for _, c in customers.iterrows():
        base_growth = {"SMB": 0.006, "Mid-Market": 0.012, "Enterprise": 0.017}[c["company_size_segment"]]
        initial_seats = {
            "SMB": int(RNG.integers(3, 18)),
            "Mid-Market": int(RNG.integers(20, 80)),
            "Enterprise": int(RNG.integers(90, 320)),
        }[c["company_size_segment"]]
        for month in MONTH_STARTS:
            if c["signup_date"] > month + pd.offsets.MonthEnd(0):
                continue
            if pd.notna(c["churn_date"]) and c["churn_date"] < month:
                continue
            age_months = max(0, (month.to_period("M") - c["signup_date"].to_period("M")).n)
            plan = get_plan_for_month(c, month)
            plan_cfg = PLAN_LOOKUP[plan]
            seasonal = 1 + 0.03 * np.sin((month.month - 1) / 12 * 2 * np.pi)
            seat_growth = (1 + base_growth) ** age_months
            seats = max(plan_cfg["included_seats"], int(initial_seats * seat_growth * seasonal * RNG.lognormal(0, 0.04)))
            extra_seats = max(0, seats - plan_cfg["included_seats"])
            discount = 0.0
            if c["contract_type"] == "Annual":
                discount = 0.10 if plan != "Enterprise" else 0.13
            if c["underpriced_flag"]:
                discount += 0.12
            mrr = (plan_cfg["base_mrr"] + extra_seats * plan_cfg["seat_price"]) * (1 - discount)
            # Small natural price changes and expansion revenue.
            mrr *= 1 + 0.0025 * age_months
            rows.append(
                {
                    "month": month,
                    "customer_id": c["customer_id"],
                    "plan_type": plan,
                    "seat_count": seats,
                    "base_mrr_usd": round(plan_cfg["base_mrr"], 2),
                    "discount_pct": round(discount, 4),
                    "mrr_usd": round(mrr, 2),
                    "arr_usd": round(mrr * 12, 2),
                    "contract_type": c["contract_type"],
                    "renewal_month": (c["signup_date"] + pd.DateOffset(years=max(1, (month.year - c["signup_date"].year) + 1))).to_period("M").to_timestamp(),
                    "subscription_status": "Active",
                }
            )
    return pd.DataFrame(rows)


def feature_adoption_probability(feature: str, plan: str, age_months: int, month: pd.Timestamp, customer: pd.Series) -> float:
    p = BASE_ADOPTION[feature]
    p += min(age_months, 12) * 0.012
    if plan == "Professional":
        p += 0.05
    elif plan == "Enterprise":
        p += 0.10
    if customer["power_user_flag"]:
        p += 0.10
    if customer["risk_profile"] == "High":
        p -= 0.08
    # Product lifecycle effects.
    if feature == "AI Assistant":
        months_since_release = max(0, (month.to_period("M") - pd.Period("2025-05", freq="M")).n)
        p += min(months_since_release, 12) * 0.025
    if feature == "Advanced Analytics":
        months_since_release = max(0, (month.to_period("M") - pd.Period("2025-09", freq="M")).n)
        p += min(months_since_release, 9) * 0.012
    if feature == "File Storage":
        p -= 0.04
    return float(np.clip(p, 0.04, 0.97))


def build_usage(customers: pd.DataFrame, subscriptions: pd.DataFrame) -> pd.DataFrame:
    customers_idx = customers.set_index("customer_id")
    rows: list[dict] = []
    storage_state: dict[str, float] = {}
    for _, sub in subscriptions.sort_values(["customer_id", "month"]).iterrows():
        c = customers_idx.loc[sub["customer_id"]]
        month = pd.Timestamp(sub["month"])
        age_months = max(0, (month.to_period("M") - c["signup_date"].to_period("M")).n)
        seats = int(sub["seat_count"])
        plan = sub["plan_type"]
        base_util = {"Starter": 0.48, "Professional": 0.58, "Enterprise": 0.66}[plan]
        base_util += 0.08 if c["power_user_flag"] else 0
        base_util -= 0.08 if c["risk_profile"] == "High" else 0
        seat_util = float(np.clip(RNG.normal(base_util, 0.11), 0.12, 0.98))
        active_users_account = max(1, int(seats * seat_util))
        storage_key = c.name
        current_storage = storage_state.get(storage_key, max(5.0, active_users_account * RNG.uniform(1.5, 4.0)))
        current_storage *= RNG.uniform(1.018, 1.075)
        if month >= pd.Timestamp("2025-10-01"):
            current_storage *= 1.015  # retention policy drift
        storage_state[storage_key] = current_storage

        for feature in eligible_features(plan, month):
            fname = feature["feature_name"]
            p = feature_adoption_probability(fname, plan, age_months, month, c)
            used = RNG.random() < p
            active_users = max(0, int(active_users_account * RNG.uniform(0.25, 0.95))) if used else 0
            power = 1.75 if c["power_user_flag"] else 1.0
            enterprise = 1.45 if plan == "Enterprise" else 1.0
            seasonality = 1 + 0.12 * np.sin((month.month - 1) / 12 * 2 * np.pi)

            workflow_runs = int(active_users * RNG.uniform(18, 60) * power * seasonality) if fname == "Workflow Automation" and used else 0
            collaboration_actions = int(active_users * RNG.uniform(45, 150) * seasonality) if fname == "Team Collaboration" and used else 0
            dashboard_views = int(active_users * RNG.uniform(8, 32) * enterprise) if fname == "Dashboard Reporting" and used else 0
            exports_count = int(active_users * RNG.uniform(0.8, 5.5) * power) if fname == "Data Export" and used else 0
            api_calls = int(active_users * RNG.uniform(8_000, 42_000) * power * enterprise) if fname == "API Integration" and used else 0
            ai_tokens_million = float(active_users * RNG.uniform(0.015, 0.11) * power * (1 + 0.04 * max(0, (month.to_period("M") - pd.Period("2025-05", freq="M")).n))) if fname == "AI Assistant" and used else 0.0
            analytics_queries = int(active_users * RNG.uniform(4, 18) * enterprise) if fname == "Advanced Analytics" and used else 0
            admin_actions = int(active_users * RNG.uniform(1.5, 8.0)) if fname == "Admin Controls" and used else 0
            storage_gb = float(current_storage * RNG.uniform(0.75, 1.25)) if fname == "File Storage" and used else 0.0
            # Other metrics support cross-feature economic modeling.
            login_count = int(active_users * RNG.uniform(7, 26) * seasonality) if used else 0
            compute_minutes = (
                workflow_runs * 0.08 + api_calls / 9_000 + dashboard_views * 0.12 +
                ai_tokens_million * 45 + analytics_queries * 1.5 + admin_actions * 0.07
            )
            athena_scanned_gb = dashboard_views * RNG.uniform(0.08, 0.30) if fname == "Dashboard Reporting" and used else 0.0
            if fname == "Advanced Analytics" and used:
                athena_scanned_gb += analytics_queries * RNG.uniform(0.6, 2.2)
            export_gb = exports_count * RNG.uniform(0.02, 0.20) if fname == "Data Export" and used else 0.0

            rows.append(
                {
                    "month": month,
                    "customer_id": c.name,
                    "feature_name": fname,
                    "eligible_flag": True,
                    "feature_used_flag": bool(used),
                    "seat_count": seats,
                    "active_users": active_users,
                    "seat_utilization_pct": round(seat_util, 4),
                    "login_count": login_count,
                    "workflow_runs": workflow_runs,
                    "collaboration_actions": collaboration_actions,
                    "dashboard_views": dashboard_views,
                    "exports_count": exports_count,
                    "export_gb": round(export_gb, 4),
                    "api_calls": api_calls,
                    "storage_gb": round(storage_gb, 4),
                    "compute_minutes": round(compute_minutes, 4),
                    "ai_tokens_million": round(ai_tokens_million, 6),
                    "athena_scanned_gb": round(athena_scanned_gb, 4),
                    "analytics_queries": analytics_queries,
                    "admin_actions": admin_actions,
                }
            )
    return pd.DataFrame(rows)


def base_feature_cost(row: pd.Series) -> float:
    feature = row["feature_name"]
    if not row["feature_used_flag"]:
        # Small feature readiness / shared metadata cost for eligible accounts.
        return {"AI Assistant": 0.15, "Advanced Analytics": 0.10}.get(feature, 0.03)
    if feature == "Workflow Automation":
        return 4.0 + row["workflow_runs"] * 0.0021 + row["compute_minutes"] * 0.018
    if feature == "Team Collaboration":
        return 2.5 + row["collaboration_actions"] * 0.0007 + row["active_users"] * 0.55
    if feature == "Dashboard Reporting":
        return 5.0 + row["athena_scanned_gb"] * 0.024 + row["active_users"] * 2.3
    if feature == "Data Export":
        return 1.5 + row["exports_count"] * 0.18 + row["export_gb"] * 0.10
    if feature == "File Storage":
        # Deliberately high storage cost in the synthetic scenario.
        drift = 1.22 if pd.Timestamp(row["month"]) >= pd.Timestamp("2025-10-01") else 1.0
        return 2.0 + row["storage_gb"] * 0.14 * drift + row["active_users"] * 0.38
    if feature == "API Integration":
        return 6.0 + row["api_calls"] / 1_000_000 * 15.0 + row["compute_minutes"] * 0.035
    if feature == "AI Assistant":
        growth = 1.15 if pd.Timestamp(row["month"]) >= pd.Timestamp("2026-01-01") else 1.0
        return 8.0 + row["ai_tokens_million"] * 36.0 * growth + row["compute_minutes"] * 0.07
    if feature == "Advanced Analytics":
        return 7.0 + row["athena_scanned_gb"] * 0.018 + row["analytics_queries"] * 0.28 + row["active_users"] * 0.62
    if feature == "Admin Controls":
        return 3.0 + row["admin_actions"] * 0.10 + row["active_users"] * 0.45
    raise ValueError(feature)


def build_cost_allocations(usage: pd.DataFrame, customers: pd.DataFrame, subscriptions: pd.DataFrame) -> pd.DataFrame:
    customer_flags = customers.set_index("customer_id")[["power_user_flag", "underpriced_flag"]]
    sub_lookup = subscriptions.set_index(["month", "customer_id"])[["mrr_usd", "plan_type"]]
    rows: list[dict] = []
    for _, u in usage.iterrows():
        base = base_feature_cost(u)
        flags = customer_flags.loc[u["customer_id"]]
        if flags["power_user_flag"]:
            base *= 1.12
        # Inject feature-specific cost pressure for an interview-worthy story.
        month = pd.Timestamp(u["month"])
        if u["feature_name"] == "AI Assistant" and month >= pd.Timestamp("2026-01-01"):
            base *= 1.16
        if u["feature_name"] == "File Storage" and month >= pd.Timestamp("2026-01-01"):
            base *= 1.12
        service_mix = FEATURE_SERVICE_MAP[u["feature_name"]]
        for service, share in service_mix:
            jitter = RNG.normal(1.0, 0.025)
            cost = max(0.01, base * share * jitter)
            usage_quantity = {
                "Amazon Bedrock": u["ai_tokens_million"],
                "Amazon S3": u["storage_gb"] + u["export_gb"],
                "Amazon Athena": u["athena_scanned_gb"],
                "Amazon API Gateway": u["api_calls"] / 1_000_000,
                "AWS Lambda": u["compute_minutes"],
                "AWS Step Functions": u["workflow_runs"],
                "Amazon DynamoDB": u["collaboration_actions"] + u["admin_actions"],
                "Amazon QuickSight": u["active_users"],
                "Amazon CloudWatch": u["compute_minutes"],
                "Amazon CloudFront": u["storage_gb"],
                "Data Transfer": u["export_gb"] + u["storage_gb"] * 0.02,
                "AWS Glue": u["analytics_queries"],
            }.get(service, u["compute_minutes"])
            unit = {
                "Amazon Bedrock": "million_tokens", "Amazon S3": "gb_month",
                "Amazon Athena": "gb_scanned", "Amazon API Gateway": "million_requests",
                "AWS Lambda": "compute_minutes", "AWS Step Functions": "state_transitions_proxy",
                "Amazon DynamoDB": "read_write_actions_proxy", "Amazon QuickSight": "active_users",
                "Amazon CloudWatch": "log_metric_units_proxy", "Amazon CloudFront": "gb_delivery_proxy",
                "Data Transfer": "gb", "AWS Glue": "query_job_units_proxy",
            }.get(service, "usage_units")
            rows.append(
                {
                    "month": month,
                    "customer_id": u["customer_id"],
                    "feature_name": u["feature_name"],
                    "aws_service": service,
                    "environment": "production",
                    "usage_quantity": round(float(usage_quantity), 6),
                    "usage_unit": unit,
                    "cost_usd": round(cost, 4),
                    "allocation_method": "activity_based_costing",
                    "plan_type": sub_lookup.loc[(month, u["customer_id"]), "plan_type"],
                    "mrr_usd": sub_lookup.loc[(month, u["customer_id"]), "mrr_usd"],
                }
            )
    return pd.DataFrame(rows)


def build_infrastructure_costs(cost_allocations: pd.DataFrame) -> pd.DataFrame:
    production = (
        cost_allocations.groupby(["month", "aws_service"], as_index=False)["cost_usd"].sum()
        .assign(environment="production", cost_category="direct_product_cost")
    )
    rows = production.to_dict("records")
    shared_services = ["Amazon EC2", "Amazon RDS", "Amazon CloudFront", "Amazon CloudWatch", "AWS Support"]
    for month in MONTH_STARTS:
        month_growth = 1 + 0.035 * (month.to_period("M") - pd.Period("2025-01", freq="M")).n
        # Production shared platform overhead.
        prod_base = {
            "Amazon EC2": 6200, "Amazon RDS": 5100, "Amazon CloudFront": 2100,
            "Amazon CloudWatch": 1600, "AWS Support": 2900,
        }
        for service in shared_services:
            amount = prod_base[service] * month_growth * RNG.normal(1.0, 0.035)
            rows.append({"month": month, "aws_service": service, "environment": "production", "cost_category": "shared_platform_cost", "cost_usd": round(amount, 2)})

        # Staging and development. Q1 2026 intentionally has always-on resource waste.
        for env, multiplier in [("staging", 0.18), ("development", 0.24)]:
            spike = 1.0
            if env == "development" and pd.Timestamp("2026-01-01") <= month <= pd.Timestamp("2026-03-01"):
                spike = 1.75
            for service in ["Amazon EC2", "Amazon RDS", "Amazon CloudWatch", "Amazon S3"]:
                baseline = {"Amazon EC2": 6200, "Amazon RDS": 5100, "Amazon CloudWatch": 1600, "Amazon S3": 1200}[service]
                amount = baseline * multiplier * month_growth * spike * RNG.normal(1.0, 0.06)
                rows.append({"month": month, "aws_service": service, "environment": env, "cost_category": "non_production_cost", "cost_usd": round(amount, 2)})

        # Logging incident in February 2026.
        if month == pd.Timestamp("2026-02-01"):
            rows.append({"month": month, "aws_service": "Amazon CloudWatch", "environment": "production", "cost_category": "incident_cost", "cost_usd": 6200.0})
    return pd.DataFrame(rows)


def build_support(customers: pd.DataFrame, subscriptions: pd.DataFrame, usage: pd.DataFrame) -> pd.DataFrame:
    usage_summary = usage.groupby(["month", "customer_id"], as_index=False).agg(
        used_features=("feature_used_flag", "sum"),
        compute_minutes=("compute_minutes", "sum"),
        ai_tokens_million=("ai_tokens_million", "sum"),
    )
    data = subscriptions.merge(customers[["customer_id", "risk_profile", "power_user_flag"]], on="customer_id").merge(usage_summary, on=["month", "customer_id"], how="left")
    rows = []
    for _, r in data.iterrows():
        lam = 0.35 + 0.16 * r["used_features"] + 0.55 * (r["risk_profile"] == "High") + 0.25 * r["power_user_flag"]
        if r["month"] == pd.Timestamp("2026-02-01"):
            lam += 0.75
        tickets = int(RNG.poisson(lam))
        high = int(RNG.binomial(tickets, min(0.45, 0.07 + 0.08 * (r["risk_profile"] == "High")))) if tickets else 0
        resolution = float(np.clip(RNG.normal(7.5 + high * 5, 2.8), 0.5, 48)) if tickets else 0.0
        csat = float(np.clip(RNG.normal(4.4 - high * 0.35 - tickets * 0.04, 0.35), 1.0, 5.0)) if tickets else float(np.clip(RNG.normal(4.55, 0.18), 1, 5))
        rows.append({
            "month": r["month"], "customer_id": r["customer_id"], "ticket_count": tickets,
            "high_severity_tickets": high, "avg_resolution_hours": round(resolution, 2),
            "csat_score": round(csat, 2),
        })
    return pd.DataFrame(rows)


def build_incidents() -> pd.DataFrame:
    rows = []
    incident_dates = pd.date_range("2025-01-01", "2026-06-30", freq="4D")
    sampled = RNG.choice(incident_dates, size=112, replace=False)
    for i, dt in enumerate(sorted(sampled), 1):
        service = RNG.choice(["AWS Lambda", "Amazon API Gateway", "Amazon Athena", "Amazon S3", "Amazon RDS", "Amazon CloudWatch", "Amazon Bedrock"])
        feature = RNG.choice(FEATURES["feature_name"].tolist())
        severity = RNG.choice(["SEV-1", "SEV-2", "SEV-3", "SEV-4"], p=[0.04, 0.18, 0.43, 0.35])
        downtime = {"SEV-1": RNG.integers(90, 280), "SEV-2": RNG.integers(30, 120), "SEV-3": RNG.integers(5, 45), "SEV-4": RNG.integers(0, 15)}[severity]
        impact = float(downtime * RNG.uniform(18, 75))
        rows.append({
            "incident_id": f"INC-{i:04d}", "incident_date": pd.Timestamp(dt), "month": pd.Timestamp(dt).to_period("M").to_timestamp(),
            "aws_service": service, "feature_name": feature, "severity": severity,
            "downtime_minutes": int(downtime), "estimated_business_impact_usd": round(impact, 2),
            "root_cause": RNG.choice(ROOT_CAUSES), "status": "Resolved",
        })
    # Ensure the February 2026 logging incident exists.
    rows.append({
        "incident_id": "INC-MAJOR-202602", "incident_date": pd.Timestamp("2026-02-11"), "month": pd.Timestamp("2026-02-01"),
        "aws_service": "Amazon CloudWatch", "feature_name": "Workflow Automation", "severity": "SEV-2",
        "downtime_minutes": 42, "estimated_business_impact_usd": 18_400.0,
        "root_cause": "Logging verbosity increase", "status": "Resolved",
    })
    return pd.DataFrame(rows).sort_values("incident_date")


def build_budgets(infrastructure_costs: pd.DataFrame) -> pd.DataFrame:
    actual = infrastructure_costs.groupby("month", as_index=False)["cost_usd"].sum().rename(columns={"cost_usd": "actual_cost_usd"})
    budgets = []
    prior_actual = actual.iloc[0]["actual_cost_usd"]
    for idx, r in actual.iterrows():
        month = r["month"]
        if idx == 0:
            budget = r["actual_cost_usd"] * 0.98
        else:
            budget = prior_actual * 1.045
        if month == pd.Timestamp("2026-01-01"):
            budget *= 0.92  # aggressive target before the non-production spike
        forecast = r["actual_cost_usd"] * RNG.uniform(1.01, 1.08)
        budgets.append({
            "month": month, "budget_usd": round(budget, 2), "actual_cost_usd": round(r["actual_cost_usd"], 2),
            "forecast_cost_usd": round(forecast, 2), "variance_usd": round(r["actual_cost_usd"] - budget, 2),
            "variance_pct": round((r["actual_cost_usd"] - budget) / budget, 4),
        })
        prior_actual = r["actual_cost_usd"]
    return pd.DataFrame(budgets)


def save(df: pd.DataFrame, name: str, folder: Path = RAW) -> None:
    csv_path = folder / f"{name}.csv"
    parquet_path = folder / f"{name}.parquet"
    df.to_csv(csv_path, index=False, date_format="%Y-%m-%d")
    df.to_parquet(parquet_path, index=False)


def main() -> None:
    customers = build_customers()
    subscriptions = build_subscriptions(customers)
    usage = build_usage(customers, subscriptions)
    cost_allocations = build_cost_allocations(usage, customers, subscriptions)
    infrastructure_costs = build_infrastructure_costs(cost_allocations)
    support = build_support(customers, subscriptions, usage)
    incidents = build_incidents()
    budgets = build_budgets(infrastructure_costs)

    save(customers, "customers")
    save(PLANS, "plans")
    save(FEATURES, "feature_metadata")
    save(subscriptions, "subscriptions_monthly")
    save(usage, "product_usage_monthly")
    save(cost_allocations, "cloud_cost_allocations_monthly")
    save(infrastructure_costs, "infrastructure_costs_monthly")
    save(support, "support_tickets_monthly")
    save(incidents, "incidents")
    save(budgets, "budgets_monthly")

    print("Generated raw datasets:")
    for name, df in {
        "customers": customers, "subscriptions": subscriptions, "usage": usage,
        "cost_allocations": cost_allocations, "infrastructure_costs": infrastructure_costs,
        "support": support, "incidents": incidents, "budgets": budgets,
    }.items():
        print(f"  {name:28s} {len(df):>8,} rows")


if __name__ == "__main__":
    main()
