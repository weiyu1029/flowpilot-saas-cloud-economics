"""FlowPilot SaaS Product Usage & Cloud Cost Optimization Dashboard."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from src.data import apply_filters, load_datasets, recompute_feature_metrics
from src.pages import (
    copilot_page,
    customer_page,
    data_architecture_page,
    executive_page,
    feature_page,
    finops_page,
    optimization_page,
)
from src.ui import inject_css

st.set_page_config(
    page_title="FlowPilot Cloud Economics",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

data = load_datasets()
customer_monthly = data["customer_monthly"]
months = sorted(customer_monthly["month"].dropna().unique())
month_labels = {pd.Timestamp(m).strftime("%b %Y"): pd.Timestamp(m) for m in months}
labels = list(month_labels)

with st.sidebar:
    st.markdown("## ☁️ FlowPilot")
    st.caption("SaaS cloud economics portfolio")
    page = st.radio(
        "Navigate",
        [
            "Executive Overview",
            "Feature Economics",
            "Customer Profitability",
            "AWS FinOps & Reliability",
            "Optimization Center",
            "Data & Architecture",
            "Insights Copilot",
        ],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown("### Analysis window")
    start_label, end_label = st.select_slider(
        "Month range",
        options=labels,
        value=(labels[0], labels[-1]),
    )
    st.markdown("### Portfolio filters")
    regions = st.multiselect("Region", sorted(customer_monthly["region"].dropna().unique()))
    industries = st.multiselect("Industry", sorted(customer_monthly["industry"].dropna().unique()))
    segments = st.multiselect("Company segment", sorted(customer_monthly["company_size_segment"].dropna().unique()))
    plans = st.multiselect("Plan", ["Starter", "Professional", "Enterprise"])
    st.divider()
    st.caption("Data through June 2026 · deterministic synthetic dataset")

filters = {
    "start_month": month_labels[start_label],
    "end_month": month_labels[end_label],
    "regions": regions,
    "industries": industries,
    "segments": segments,
    "plans": plans,
}
filtered_customer = apply_filters(customer_monthly, filters)
feature_metrics = recompute_feature_metrics(data["usage"], data["cost_allocations"], data["feature_metadata"], filtered_customer)

page_functions = {
    "Executive Overview": executive_page,
    "Feature Economics": feature_page,
    "Customer Profitability": customer_page,
    "AWS FinOps & Reliability": finops_page,
    "Optimization Center": optimization_page,
    "Data & Architecture": data_architecture_page,
    "Insights Copilot": copilot_page,
}
page_functions[page](data, filtered_customer, feature_metrics, filters)
