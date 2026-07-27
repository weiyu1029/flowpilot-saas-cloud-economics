from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CURATED = ROOT / "data" / "curated"


def read(folder: Path, name: str) -> pd.DataFrame:
    return pd.read_parquet(folder / f"{name}.parquet")


def test_primary_keys_are_unique():
    customers = read(RAW, "customers")
    subscriptions = read(RAW, "subscriptions_monthly")
    usage = read(RAW, "product_usage_monthly")
    budgets = read(RAW, "budgets_monthly")
    assert not customers.duplicated(["customer_id"]).any()
    assert not subscriptions.duplicated(["month", "customer_id"]).any()
    assert not usage.duplicated(["month", "customer_id", "feature_name"]).any()
    assert not budgets.duplicated(["month"]).any()


def test_numeric_values_are_nonnegative():
    subscriptions = read(RAW, "subscriptions_monthly")
    costs = read(RAW, "cloud_cost_allocations_monthly")
    infrastructure = read(RAW, "infrastructure_costs_monthly")
    usage = read(RAW, "product_usage_monthly")
    assert (subscriptions["mrr_usd"] >= 0).all()
    assert (costs["cost_usd"] >= 0).all()
    assert (infrastructure["cost_usd"] >= 0).all()
    for col in ["active_users", "api_calls", "storage_gb", "compute_minutes", "ai_tokens_million"]:
        assert (usage[col] >= 0).all()


def test_curated_data_quality_report_has_no_failures():
    report = read(CURATED, "data_quality_report")
    assert "FAIL" not in set(report["status"])
