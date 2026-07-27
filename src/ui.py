"""Formatting and UI helpers."""
from __future__ import annotations

import math
import pandas as pd
import streamlit as st

PALETTE = {
    "navy": "#0B1F3A",
    "blue": "#2563EB",
    "cyan": "#06B6D4",
    "teal": "#0F766E",
    "green": "#16A34A",
    "amber": "#D97706",
    "red": "#DC2626",
    "purple": "#7C3AED",
    "slate": "#64748B",
    "light": "#F8FAFC",
}

QUADRANT_COLORS = {
    "Efficient Winner": "#16A34A",
    "Scale Carefully": "#D97706",
    "Monitor": "#2563EB",
    "Optimization Priority": "#DC2626",
}

RISK_COLORS = {
    "Healthy": "#16A34A",
    "Monitor": "#D97706",
    "Margin Risk": "#DC2626",
}


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1500px;}
        [data-testid="stSidebar"] {background: linear-gradient(180deg, #071426 0%, #0B1F3A 100%);}
        [data-testid="stSidebar"] * {color: #F8FAFC;}
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, rgba(37,99,235,.10), rgba(6,182,212,.06));
            border: 1px solid rgba(37,99,235,.20); border-radius: 14px; padding: 14px 16px;
            box-shadow: 0 8px 24px rgba(15,23,42,.05);
        }
        [data-testid="stMetricValue"] {font-weight: 750;}
        .hero {
            background: linear-gradient(135deg, #0B1F3A 0%, #123B66 58%, #0F766E 100%);
            border-radius: 20px; padding: 28px 32px; color: white; margin-bottom: 18px;
            box-shadow: 0 18px 40px rgba(11,31,58,.20);
        }
        .hero h1 {margin:0; font-size: 2.2rem; color:white;}
        .hero p {margin:.5rem 0 0; color:#DCEBFA; font-size:1.02rem;}
        .pill {display:inline-block; border-radius:999px; padding:5px 10px; margin:8px 6px 0 0; background:rgba(255,255,255,.14); font-size:.80rem;}
        .section-note {background:#F8FAFC; border-left:4px solid #2563EB; padding:12px 16px; border-radius:8px; margin:.5rem 0 1rem;}
        .insight-card {background:white; border:1px solid #E2E8F0; border-radius:14px; padding:16px; min-height:130px; box-shadow:0 6px 18px rgba(15,23,42,.04);}
        .insight-card h4 {margin:0 0 8px; color:#0B1F3A;}
        .insight-card p {margin:0; color:#475569; font-size:.92rem;}
        .footer-note {color:#64748B; font-size:.82rem; margin-top:2rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, pills: list[str] | None = None) -> None:
    pill_html = "".join(f'<span class="pill">{p}</span>' for p in (pills or []))
    st.markdown(
        f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p><div>{pill_html}</div></div>',
        unsafe_allow_html=True,
    )


def money(value: float | int | None, decimals: int = 0) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "—"
    return f"${value:,.{decimals}f}"


def percent(value: float | None, decimals: int = 1) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{value:.{decimals}%}"


def compact(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "—"
    abs_value = abs(float(value))
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if abs_value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,.0f}"


def delta_money(current: float, previous: float | None) -> str | None:
    if previous is None or previous == 0 or pd.isna(previous):
        return None
    return f"{(current - previous) / previous:+.1%} MoM"


def insight_card(title: str, body: str) -> None:
    st.markdown(f'<div class="insight-card"><h4>{title}</h4><p>{body}</p></div>', unsafe_allow_html=True)


def footer() -> None:
    st.markdown(
        '<div class="footer-note">Synthetic portfolio data. AWS-style rates are illustrative and must not be used as a billing estimate.</div>',
        unsafe_allow_html=True,
    )
