from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CURATED = ROOT / "data" / "curated"


def test_customer_cost_reconciles_to_infrastructure_total():
    customer = pd.read_parquet(CURATED / "customer_monthly.parquet")
    infra = pd.read_parquet(RAW / "infrastructure_costs_monthly.parquet")
    allocated = customer.groupby("month")["allocated_cloud_cost_usd"].sum().sort_index()
    actual = infra.groupby("month")["cost_usd"].sum().sort_index()
    assert np.allclose(allocated.values, actual.values, rtol=1e-9, atol=0.02)


def test_executive_margin_formula():
    executive = pd.read_parquet(CURATED / "executive_monthly.parquet")
    expected = 1 - executive["total_cloud_cost_usd"] / executive["mrr_usd"]
    assert np.allclose(executive["estimated_gross_margin_pct"], expected)


def test_feature_adoption_is_bounded():
    feature = pd.read_parquet(CURATED / "feature_monthly.parquet")
    assert feature["feature_adoption_rate"].between(0, 1).all()


def test_recommendations_have_positive_impact_and_owners():
    recs = pd.read_parquet(CURATED / "recommendations.parquet")
    assert (recs["estimated_total_monthly_impact_usd"] > 0).all()
    assert recs["owner"].notna().all()
    assert recs["recommended_action"].str.len().gt(20).all()
