"""Sample Streamlit dashboard for Freedom Property Investors marketing analytics.

Run with:  streamlit run app.py
All data is synthetic. See content.ASSUMPTIONS.
"""

from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from content import (
    ACTION_PLAN,
    ASSUMPTIONS,
    HELD_QUALITY_RATE,
    KPI_DICTIONARY,
    RECOMMENDED_SPLIT,
    ROADMAP,
    STRATEGIC_BETS,
)
from data import END, SEGMENTS, START, load_data

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="FPI Marketing Analytics (Sample)",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="auto",
)

ACCENT = "#cff45a"
ACCENT_BRIGHT = "#e0ff8f"
COOL = "#809bff"
VIOLET = "#e879f9"
CORAL = "#ff6b4a"
TEAL = "#5eead4"
SLATE = "#9aa0ad"
GRID = "rgba(238,237,232,0.07)"
LTV_MULT = 2.2

# Legacy names kept so the existing chart calls keep working; the values now
# follow the alvintola.com palette. VIOLET replaces amber so warm series no
# longer sit on top of the lime bars.
NAVY = ACCENT
GOLD = VIOLET
BLUE = COOL
GREEN = TEAL
RED = CORAL
PALETTE = [ACCENT, COOL, VIOLET, CORAL, TEAL, SLATE]

CHANNEL_COLORS = {
    "Meta Prospecting": ACCENT,
    "Meta Retargeting": VIOLET,
    "YouTube In-Stream": CORAL,
    "Google Search": COOL,
    "Google Demand Gen": TEAL,
}
SEGMENT_COLORS = {
    "First-time investor": COOL,
    "Experienced investor": ACCENT,
    "Retiree": VIOLET,
}

CSS = """
<style>
    @font-face {
        font-family: "Inter";
        src: url("./app/static/fonts/inter.woff2") format("woff2");
        font-weight: 400 700;
        font-style: normal;
        font-display: swap;
    }
    @font-face {
        font-family: "Fraunces";
        src: url("./app/static/fonts/fraunces.woff2") format("woff2");
        font-weight: 300 600;
        font-style: normal;
        font-display: swap;
    }
    @font-face {
        font-family: "Fraunces";
        src: url("./app/static/fonts/fraunces-italic.woff2") format("woff2");
        font-weight: 300 600;
        font-style: italic;
        font-display: swap;
    }
    @font-face {
        font-family: "JetBrains Mono";
        src: url("./app/static/fonts/jetbrains-mono.woff2") format("woff2");
        font-weight: 400 600;
        font-style: normal;
        font-display: swap;
    }

    :root {
        --bg: #0a0b0e;
        --panel: #101218;
        --panel-2: #161a22;
        --line: rgba(238, 237, 232, 0.09);
        --line-strong: rgba(238, 237, 232, 0.17);
        --text: #f2f0e9;
        --muted: #9aa0ad;
        --muted-strong: #bdc2cc;
        --accent: #cff45a;
        --accent-bright: #e0ff8f;
        --accent-soft: rgba(207, 244, 90, 0.12);
        --cool: #809bff;
        --serif: "Fraunces", Georgia, serif;
        --sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        --mono: "JetBrains Mono", "SFMono-Regular", Menlo, monospace;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: var(--bg);
        color: var(--text);
        font-family: var(--sans);
    }
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(ellipse 70% 48% at 78% -10%, rgba(207, 244, 90, 0.075), transparent 62%),
            radial-gradient(ellipse 58% 44% at 4% 38%, rgba(128, 155, 255, 0.055), transparent 66%),
            var(--bg);
    }
    [data-testid="stHeader"] { background: transparent; }
    #MainMenu, footer { visibility: hidden; }
    .block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1500px; }

    h1, h2, h3, h4,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4 {
        font-family: var(--serif) !important;
        font-weight: 400 !important;
        letter-spacing: -0.015em;
        color: var(--text);
    }
    h1 { font-size: clamp(1.7rem, 2.5vw, 2.2rem); }
    h2 { font-size: 1.5rem; }
    h3 { font-size: 1.18rem; }
    h4 { font-size: 1.02rem; }
    p, li { color: var(--muted-strong); }
    .stMarkdown strong { color: var(--text); }
    [data-testid="stCaptionContainer"] p {
        color: var(--muted) !important;
        font-family: var(--mono);
        font-size: 0.68rem;
        letter-spacing: 0.02em;
    }
    code { font-family: var(--mono); color: var(--accent); }
    a { color: var(--accent); }
    hr { border-color: var(--line) !important; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d0f14 0%, #0a0b0e 100%);
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebarContent"] { padding-top: 1.3rem; }
    [data-testid="stSidebarCollapsedControl"] { color: var(--text); }
    .nav-label {
        margin: 2px 0 9px;
        font-family: var(--mono);
        font-size: 0.58rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--muted);
    }
    [data-testid="stRadioGroup"] {
        counter-reset: nav;
        display: flex;
        flex-direction: column;
        align-items: stretch;
        gap: 6px;
    }
    [data-testid="stRadioGroup"] > div {
        counter-increment: nav;
        display: block;
        width: 100%;
    }
    [data-testid="stRadioOption"] {
        display: flex;
        align-items: center;
        gap: 10px;
        width: 100%;
        padding: 9px 11px;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: rgba(238, 237, 232, 0.015);
        cursor: pointer;
        transition: background 0.18s ease, border-color 0.18s ease, transform 0.18s ease;
    }
    [data-testid="stRadioOption"]::before {
        content: "0" counter(nav);
        flex: 0 0 auto;
        padding: 3px 6px;
        border: 1px solid var(--line);
        border-radius: 6px;
        background: rgba(0, 0, 0, 0.22);
        color: var(--muted);
        font-family: var(--mono);
        font-size: 0.56rem;
        letter-spacing: 0.06em;
        transition: color 0.18s ease, border-color 0.18s ease, background 0.18s ease;
    }
    [data-testid="stRadioOption"]::after {
        content: "→";
        margin-left: auto;
        color: var(--muted);
        font-size: 0.8rem;
        opacity: 0;
        transform: translateX(-4px);
        transition: opacity 0.18s ease, transform 0.18s ease, color 0.18s ease;
    }
    [data-testid="stRadioOption"] > div > div:first-child { display: none; }
    [data-testid="stRadioOption"] > div { flex: 1; min-width: 0; }
    [data-testid="stRadioOption"] [data-testid="stMarkdownContainer"] { min-width: 0; }
    [data-testid="stRadioOption"] p {
        font-size: 0.8rem;
        color: var(--muted-strong);
        transition: color 0.18s ease;
    }
    [data-testid="stRadioOption"]:hover {
        border-color: var(--line-strong);
        background: rgba(238, 237, 232, 0.035);
        transform: translateX(2px);
    }
    [data-testid="stRadioOption"]:hover p { color: var(--text); }
    [data-testid="stRadioOption"]:hover::after { opacity: 0.6; transform: none; }
    [data-testid="stRadioOption"][data-selected="true"] {
        border-color: rgba(207, 244, 90, 0.42);
        background: var(--accent-soft);
        box-shadow: inset 3px 0 0 var(--accent), 0 0 0 1px rgba(207, 244, 90, 0.08);
    }
    [data-testid="stRadioOption"][data-selected="true"] p {
        color: var(--accent);
        font-weight: 600;
    }
    [data-testid="stRadioOption"][data-selected="true"]::before {
        color: var(--accent);
        border-color: rgba(207, 244, 90, 0.35);
        background: rgba(207, 244, 90, 0.1);
    }
    [data-testid="stRadioOption"][data-selected="true"]::after {
        opacity: 1;
        transform: none;
        color: var(--accent);
    }

    .brand { display: flex; align-items: center; gap: 12px; margin: 2px 0 18px; }
    .brand-mark {
        width: 38px; height: 38px; flex: 0 0 auto;
        display: grid; place-items: center;
        border-radius: 11px;
        font-family: var(--mono); font-size: 0.66rem; font-weight: 600; letter-spacing: 0.08em;
        color: #0a0b0e;
        background: linear-gradient(135deg, var(--accent-bright), var(--accent));
        box-shadow: 0 8px 22px rgba(207, 244, 90, 0.18);
    }
    .brand-name { font-family: var(--serif); font-size: 1.02rem; line-height: 1.15; color: var(--text); }
    .brand-sub {
        margin-top: 3px;
        font-family: var(--mono); font-size: 0.58rem; letter-spacing: 0.11em;
        text-transform: uppercase; color: var(--muted);
    }
    .filter-summary {
        padding: 9px 11px;
        border: 1px dashed var(--line-strong);
        border-radius: 9px;
        color: var(--muted);
        font-family: var(--mono);
        font-size: 0.66rem;
        letter-spacing: 0.02em;
        line-height: 1.5;
    }

    /* Hero */
    .hero {
        position: relative;
        overflow: hidden;
        margin-bottom: 20px;
        padding: 26px 30px;
        border: 1px solid var(--line);
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(22, 26, 34, 0.96), rgba(10, 11, 14, 0.98));
        box-shadow: 0 22px 55px rgba(0, 0, 0, 0.3);
    }
    .hero::before {
        content: "";
        position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
        background: linear-gradient(180deg, var(--accent), transparent 82%);
    }
    .hero::after {
        content: "";
        position: absolute; top: -60%; right: -8%;
        width: 440px; height: 440px;
        background: radial-gradient(circle, rgba(207, 244, 90, 0.14), transparent 66%);
        pointer-events: none;
    }
    .hero h1 {
        position: relative;
        margin: 0 0 8px;
        font-family: var(--serif);
        font-size: clamp(1.7rem, 2.5vw, 2.2rem);
        color: var(--text);
    }
    .hero p { position: relative; margin: 0; max-width: 940px; color: var(--muted-strong); font-size: 0.96rem; }
    .hero .tag {
        position: relative;
        display: inline-flex; align-items: center; gap: 6px;
        margin-bottom: 12px; padding: 4px 9px;
        border: 1px solid rgba(207, 244, 90, 0.35);
        border-radius: 999px;
        background: var(--accent-soft);
        color: var(--accent);
        font-family: var(--mono); font-size: 0.6rem; letter-spacing: 0.14em; text-transform: uppercase;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        position: relative;
        padding: 16px 18px;
        border: 1px solid var(--line);
        border-radius: 14px;
        background: linear-gradient(180deg, var(--panel), rgba(10, 11, 14, 0.92));
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
        transition: border-color 0.2s ease, transform 0.2s ease;
    }
    div[data-testid="stMetric"]:hover { border-color: rgba(207, 244, 90, 0.3); transform: translateY(-1px); }
    div[data-testid="stMetricLabel"] p {
        font-family: var(--mono) !important;
        font-size: 0.62rem !important;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--muted) !important;
    }
    div[data-testid="stMetricValue"] {
        font-family: var(--serif) !important;
        font-size: 1.6rem !important;
        font-weight: 500 !important;
        color: var(--text) !important;
    }
    div[data-testid="stMetricDelta"] { font-family: var(--mono); font-size: 0.64rem; }
    div[data-testid="stMetricDelta"] svg { display: none; }

    /* Insight + note cards */
    .insight {
        height: 100%;
        padding: 16px 18px;
        border: 1px solid var(--line);
        border-top: 2px solid var(--accent);
        border-radius: 14px;
        background: linear-gradient(180deg, var(--panel), rgba(10, 11, 14, 0.92));
    }
    .insight .kicker {
        margin-bottom: 7px;
        font-family: var(--mono); font-size: 0.59rem; letter-spacing: 0.14em;
        text-transform: uppercase; color: var(--accent); font-weight: 600;
    }
    .insight .title {
        margin-bottom: 6px;
        font-family: var(--serif); font-size: 1.05rem; font-weight: 500;
        line-height: 1.25; color: var(--text);
    }
    .insight .body { font-size: 0.84rem; line-height: 1.5; color: var(--muted-strong); }
    .section-note {
        padding: 12px 14px;
        border: 1px solid var(--line);
        border-left: 2px solid var(--cool);
        border-radius: 10px;
        background: rgba(22, 26, 34, 0.7);
        color: var(--muted-strong);
        font-size: 0.84rem;
    }

    /* Expanders */
    div[data-testid="stExpander"] {
        border: 1px solid var(--line);
        border-radius: 12px;
        background: rgba(16, 18, 24, 0.55);
        overflow: hidden;
    }
    div[data-testid="stExpander"] summary {
        font-family: var(--mono);
        font-size: 0.7rem;
        letter-spacing: 0.04em;
    }
    div[data-testid="stExpander"] summary:hover { color: var(--accent); }
    [data-testid="stSidebar"] div[data-testid="stExpander"] summary {
        padding: 2px 0;
        font-size: 0.66rem;
        letter-spacing: 0.10em;
        text-transform: uppercase;
        color: var(--muted-strong);
    }
    [data-testid="stAppDeployButton"] { display: none !important; }

    /* Buttons */
    .stButton > button, .stDownloadButton > button {
        border: 1px solid var(--line-strong);
        border-radius: 999px;
        background: transparent;
        color: var(--text);
        font-family: var(--mono);
        font-size: 0.66rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 0.55rem 1.1rem;
        transition: color 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        border-color: var(--accent);
        color: var(--accent);
        transform: translateY(-1px);
    }

    /* Inputs */
    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div,
    [data-testid="stDateInput"] [data-baseweb="input"] {
        border-color: var(--line) !important;
        border-radius: 9px !important;
        background: var(--panel-2) !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="input"] > div {
        background: rgba(238, 237, 232, 0.03) !important;
    }
    [data-testid="stMultiSelectTagsContainer"] [data-tag] {
        max-width: 100% !important;
        border: 1px solid rgba(207, 244, 90, 0.35) !important;
        border-radius: 6px !important;
        background: rgba(207, 244, 90, 0.12) !important;
        color: var(--accent) !important;
    }
    [data-testid="stMultiSelectTagsContainer"] [data-tag] > span {
        color: var(--accent) !important;
        font-size: 0.62rem !important;
    }
    [data-testid="stMultiSelectTagsContainer"] [data-tag] button {
        color: var(--accent) !important;
        background: transparent !important;
    }
    [data-testid="stMultiSelectTagsContainer"] [data-tag] svg {
        stroke: var(--accent) !important;
    }
    [data-testid="stMultiSelectTagsContainer"] [data-tag]:hover {
        border-color: rgba(207, 244, 90, 0.6) !important;
        background: rgba(207, 244, 90, 0.18) !important;
    }
    [data-testid="stDateInput"] input { font-size: 0.72rem !important; }
    [data-testid="stWidgetLabel"] p {
        font-family: var(--mono) !important;
        font-size: 0.6rem !important;
        letter-spacing: 0.10em;
        text-transform: uppercase;
        color: var(--muted) !important;
    }
    [data-baseweb="menu"] [role="option"][aria-selected="true"],
    [data-baseweb="menu"] [aria-selected="true"] {
        background: rgba(207, 244, 90, 0.16) !important;
        color: var(--accent) !important;
    }
    [data-baseweb="calendar"] [aria-selected="true"] {
        background: var(--accent) !important;
        color: #0a0b0e !important;
    }

    /* Data + controls */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 12px;
        overflow: hidden;
    }
    [data-testid="stSlider"] [role="slider"] { box-shadow: 0 0 0 3px rgba(207, 244, 90, 0.18); }
    [data-testid="stAlert"] { border: 1px solid var(--line); border-radius: 12px; }

    /* Scrollbars + plotly chrome */
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: #262b36; border: 2px solid var(--bg); border-radius: 8px; }
    ::-webkit-scrollbar-thumb:hover { background: #343b49; }
    .js-plotly-plot .plotly .modebar { opacity: 0.2; transition: opacity 0.2s ease; }
    .js-plotly-plot:hover .plotly .modebar { opacity: 1; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def get_data() -> dict[str, pd.DataFrame]:
    return load_data()


DATA = get_data()
FACT = DATA["fact"]
CREATIVE = DATA["creative"]
RESPONSE = DATA["response"]
LAG = DATA["lag"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _div(a, b):
    try:
        return np.nan if b in (0, None) or pd.isna(b) else a / b
    except (TypeError, ValueError):
        return np.nan


def money(v, decimals: int = 0) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"${v:,.{decimals}f}"


def pct(v, decimals: int = 1) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{v * 100:.{decimals}f}%"


def num(v) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{v:,.0f}"


def mult(v) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{v:.1f}x"


def delta_str(cur, prev) -> str | None:
    if cur is None or prev is None or pd.isna(cur) or pd.isna(prev) or prev == 0:
        return None
    return f"{(cur - prev) / prev * 100:+.1f}% vs prior period"


def metrics(df: pd.DataFrame) -> dict[str, float]:
    spend = float(df["spend"].sum())
    revenue = float(df["revenue"].sum())
    members = float(df["members"].sum())
    regs = float(df["mc_regs"].sum())
    attended = float(df["mc_attended"].sum())
    mqls = float(df["mqls"].sum())
    calls = float(df["calls_booked"].sum())
    held = float(df["calls_held"].sum())
    quality_sessions = (
        float(df["quality_sessions"].sum()) if "quality_sessions" in df.columns else np.nan
    )
    clicks = float(df["clicks"].sum())
    impressions = float(df["impressions"].sum())
    sessions = float(df["sessions"].sum())
    cac = _div(spend, members)
    aov = _div(revenue, members)
    ltv = aov * LTV_MULT if pd.notna(aov) else np.nan
    return {
        "spend": spend,
        "revenue": revenue,
        "members": members,
        "regs": regs,
        "attended": attended,
        "mqls": mqls,
        "calls": calls,
        "held": held,
        "quality_sessions": quality_sessions,
        "cost_per_quality_session": _div(spend, quality_sessions),
        "held_quality_rate": _div(quality_sessions, held),
        "clicks": clicks,
        "impressions": impressions,
        "sessions": sessions,
        "ctr": _div(clicks, impressions),
        "cpm": _div(spend, impressions) * 1000 if impressions else np.nan,
        "cpc": _div(spend, clicks),
        "lpv_rate": _div(sessions, clicks),
        "reg_rate": _div(regs, sessions),
        "cpl": _div(spend, regs),
        "attendance": _div(attended, regs),
        "mql_rate": _div(mqls, attended),
        "cost_per_mql": _div(spend, mqls),
        "call_rate": _div(calls, mqls),
        "cost_per_call": _div(spend, calls),
        "show_rate": _div(held, calls),
        "close_rate": _div(members, held),
        "lead_to_member": _div(members, regs),
        "cac": cac,
        "aov": aov,
        "roas": _div(revenue, spend),
        "mer": _div(revenue, spend),
        "ltv": ltv,
        "ltv_cac": _div(ltv, cac),
        "payback_months": _div(cac, aov / 12),
    }


def apply_filters(df, start, end, channels, segments):
    return df[
        (df["date"] >= pd.Timestamp(start))
        & (df["date"] <= pd.Timestamp(end))
        & (df["channel"].isin(channels))
        & (df["segment"].isin(segments))
    ]


def add_quality(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.assign(quality_rate=np.nan, quality_sessions=np.nan)
    rates = df["segment"].map(HELD_QUALITY_RATE).astype(float).fillna(0.6)
    return df.assign(
        quality_rate=rates,
        quality_sessions=df["calls_held"].astype(float) * rates,
    )


def channel_summary(df: pd.DataFrame) -> pd.DataFrame:
    g = (
        df.groupby("channel", as_index=False)
        .agg(
            spend=("spend", "sum"),
            revenue=("revenue", "sum"),
            members=("members", "sum"),
            mqls=("mqls", "sum"),
            regs=("mc_regs", "sum"),
            attended=("mc_attended", "sum"),
            calls=("calls_booked", "sum"),
            held=("calls_held", "sum"),
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            sessions=("sessions", "sum"),
        )
        .copy()
    )
    g["ctr"] = np.where(g.impressions > 0, g.clicks / g.impressions, np.nan)
    g["cpm"] = np.where(g.impressions > 0, g.spend / g.impressions * 1000, np.nan)
    g["cpl"] = np.where(g.regs > 0, g.spend / g.regs, np.nan)
    g["cost_per_mql"] = np.where(g.mqls > 0, g.spend / g.mqls, np.nan)
    g["cost_per_call"] = np.where(g.calls > 0, g.spend / g.calls, np.nan)
    g["cac"] = np.where(g.members > 0, g.spend / g.members, np.nan)
    g["roas"] = np.where(g.spend > 0, g.revenue / g.spend, np.nan)
    g["share_spend"] = g.spend / g.spend.sum() if g.spend.sum() else np.nan
    g["share_members"] = g.members / g.members.sum() if g.members.sum() else np.nan
    return g.sort_values("spend", ascending=False).reset_index(drop=True)


def style_fig(fig, height: int = 360, title: str | None = None, legend: bool = True):
    fig.update_layout(
        template="plotly_dark",
        height=height,
        margin=dict(l=10, r=10, t=48 if title else 20, b=10),
        font=dict(family="Inter, sans-serif", color="#bdc2cc", size=12),
        title=dict(
            text=title,
            font=dict(size=15, color="#f2f0e9", family="Fraunces, Georgia, serif"),
        )
        if title
        else None,
        colorway=PALETTE,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.28,
            x=0,
            font=dict(size=10, color="#9aa0ad"),
            bgcolor="rgba(0,0,0,0)",
        )
        if legend
        else None,
        hoverlabel=dict(
            font_size=12,
            bgcolor="#161a22",
            bordercolor="rgba(238,237,232,0.17)",
            font=dict(color="#f2f0e9", family="Inter, sans-serif"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor="rgba(238,237,232,0.10)",
        tickfont=dict(color="#9aa0ad"),
        title_font=dict(color="#9aa0ad"),
    )
    fig.update_yaxes(
        gridcolor=GRID,
        zeroline=False,
        tickfont=dict(color="#9aa0ad"),
        title_font=dict(color="#9aa0ad"),
    )
    return fig


def legend_right(fig, width: int = 118):
    """Vertical legend outside the plot, for charts with many series."""
    fig.update_layout(
        legend=dict(
            orientation="v",
            x=1.02,
            xanchor="left",
            y=0.98,
            yanchor="top",
            font=dict(size=9, color="#9aa0ad"),
            bgcolor="rgba(10,11,14,0.68)",
            bordercolor="rgba(238,237,232,0.12)",
            borderwidth=1,
            itemsizing="constant",
        ),
        margin=dict(r=width),
    )
    return fig


def page_header(title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="hero">
            <div class="tag">Sample analytics</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight(col, kicker: str, title: str, body: str):
    col.markdown(
        f"""
        <div class="insight">
            <div class="kicker">{kicker}</div>
            <div class="title">{title}</div>
            <div class="body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def download_csv(df: pd.DataFrame, label: str, filename: str):
    st.download_button(
        label,
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
    )


# ---------------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-mark">FPI</div>
            <div>
                <div class="brand-name">Freedom Property Investors</div>
                <div class="brand-sub">Marketing analytics · independent sample</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="nav-label">Pages</div>', unsafe_allow_html=True)
    page = st.radio(
        "View",
        [
            "Executive summary",
            "North star",
            "KPI dashboard",
            "Paid media",
            "Lead quality",
            "Creative analytics",
            "Data dictionary",
            "Action plan",
        ],
        label_visibility="collapsed",
    )
    st.divider()

    all_channels = sorted(FACT["channel"].unique())
    start_date, end_date = START, END
    channels = all_channels
    segments = list(SEGMENTS)

    with st.expander("Filters", expanded=False):
        date_range = st.date_input(
            "Date range",
            value=(START, END),
            min_value=START,
            max_value=END,
        )
        if isinstance(date_range, (tuple, list)):
            if len(date_range) == 2:
                start_date, end_date = date_range
            elif len(date_range) == 1:
                start_date = end_date = date_range[0]
            else:
                start_date, end_date = START, END
        else:
            start_date = end_date = date_range

        channels = st.multiselect("Channels", all_channels, default=all_channels)
        segments = st.multiselect("Segments", list(SEGMENTS), default=list(SEGMENTS))

    if channels == all_channels and segments == list(SEGMENTS):
        filter_summary = "All channels · All segments<br>Full sample period"
    else:
        ch = "All channels" if channels == all_channels else f"{len(channels)} channels"
        sg = "All segments" if segments == list(SEGMENTS) else f"{len(segments)} segments"
        filter_summary = (
            f"{ch} · {sg}<br>"
            f"{pd.Timestamp(start_date):%d %b %Y} – {pd.Timestamp(end_date):%d %b %Y}"
        )
    st.markdown(f'<div class="filter-summary">{filter_summary}</div>', unsafe_allow_html=True)

    st.divider()
    with st.expander("About the sample data"):
        for title, body in ASSUMPTIONS:
            st.markdown(f"**{title}**")
            st.caption(body)
    st.caption("Synthetic data. Independent sample, not affiliated with Freedom Property Investors.")

if not channels or not segments:
    st.warning("Select at least one channel and one segment.")
    st.stop()

filtered = add_quality(apply_filters(FACT, start_date, end_date, channels, segments))
creative_filtered = apply_filters(CREATIVE, start_date, end_date, channels, segments)

if filtered.empty:
    st.warning("No data in the selected range.")
    st.stop()

K = metrics(filtered)
period_days = (pd.Timestamp(end_date) - pd.Timestamp(start_date)).days + 1
prev_filtered = add_quality(
    apply_filters(
        FACT,
        pd.Timestamp(start_date) - timedelta(days=period_days),
        pd.Timestamp(start_date) - timedelta(days=1),
        channels,
        segments,
    )
)
PK = metrics(prev_filtered) if not prev_filtered.empty else {key: np.nan for key in K}
channels_df = channel_summary(filtered)


# ---------------------------------------------------------------------------
# Executive summary
# ---------------------------------------------------------------------------

if page == "Executive summary":
    page_header(
        "Marketing performance at a glance",
        "A closed-loop view of paid acquisition for a masterclass-led, high-ticket property "
        "advisory: spend, funnel conversion, member acquisition cost and the evidence behind "
        "the recommended action plan.",
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Media spend", money(K["spend"]), delta_str(K["spend"], PK.get("spend")))
    c2.metric("New members", num(K["members"]), delta_str(K["members"], PK.get("members")))
    c3.metric(
        "Blended CAC",
        money(K["cac"]),
        delta_str(K["cac"], PK.get("cac")),
        delta_color="inverse",
        help="Total media spend divided by new members. Lower is better.",
    )
    c4.metric("Attributed revenue", money(K["revenue"]), delta_str(K["revenue"], PK.get("revenue")))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric(
        "MER / ROAS",
        mult(K["mer"]),
        delta_str(K["mer"], PK.get("mer")),
        help="Attributed revenue per dollar of media spend.",
    )
    c6.metric(
        "LTV:CAC",
        mult(K["ltv_cac"]),
        help=f"LTV assumes {LTV_MULT}x first-year revenue over three years.",
    )
    c7.metric(
        "Lead to member",
        pct(K["lead_to_member"], 2),
        delta_str(K["lead_to_member"], PK.get("lead_to_member")),
    )
    c8.metric(
        "Masterclass attendance",
        pct(K["attendance"]),
        delta_str(K["attendance"], PK.get("attendance")),
    )

    st.markdown("#### What the data says")
    ch_valid = channels_df[channels_df["members"] > 0].copy()
    if ch_valid.empty:
        search = retarget = None
    else:
        search = ch_valid[ch_valid.channel == "Google Search"]
        retarget = ch_valid[ch_valid.channel == "Meta Retargeting"]
        search = search.iloc[0] if not search.empty else None
        retarget = retarget.iloc[0] if not retarget.empty else None

    meta = filtered[filtered.channel == "Meta Prospecting"]
    mw = (
        meta.groupby("week_start", as_index=False)
        .agg(
            spend=("spend", "sum"),
            members=("members", "sum"),
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
        )
        .sort_values("week_start")
    )
    meta_cac_change = meta_cpm_change = meta_ctr_change = np.nan
    if len(mw) >= 8:
        first4, last4 = mw.head(4), mw.tail(4)
        first_cac = _div(first4.spend.sum(), first4.members.sum())
        last_cac = _div(last4.spend.sum(), last4.members.sum())
        meta_cac_change = _div(last_cac, first_cac) - 1
        first_cpm = _div(first4.spend.sum(), first4.impressions.sum()) * 1000
        last_cpm = _div(last4.spend.sum(), last4.impressions.sum()) * 1000
        meta_cpm_change = _div(last_cpm, first_cpm) - 1
        first_ctr = _div(first4.clicks.sum(), first4.impressions.sum())
        last_ctr = _div(last4.clicks.sum(), last4.impressions.sum())
        meta_ctr_change = _div(last_ctr, first_ctr) - 1

    i1, i2, i3, i4 = st.columns(4)
    if search is not None:
        insight(
            i1,
            "Efficiency anchor",
            "Search converts at the lowest CAC",
            f"Google Search acquires members at {money(search['cac'])} versus a blended "
            f"{money(K['cac'])}. It delivers {pct(search['share_members'])} of members on "
            f"{pct(search['share_spend'])} of spend.",
        )
    else:
        insight(i1, "Efficiency anchor", "Search data unavailable", "Adjust the filters to include Google Search.")

    if pd.notna(meta_cac_change):
        insight(
            i2,
            "Fatigue signal",
            "Meta prospecting is getting more expensive",
            f"Meta CAC has moved {pct(meta_cac_change)} between the first and last four weeks, "
            f"with CPM {pct(meta_cpm_change)} and CTR {pct(meta_ctr_change)}. This is the "
            f"classic creative and audience fatigue pattern.",
        )
    else:
        insight(i2, "Fatigue signal", "Not enough history", "Select a longer date range to compare four-week blocks.")

    if retarget is not None:
        insight(
            i3,
            "Under-funded",
            "Retargeting earns its budget many times over",
            f"Meta Retargeting returns {mult(retarget['roas'])} on {pct(retarget['share_spend'])} "
            f"of spend, while its CAC of {money(retarget['cac'])} is well below the blended "
            f"{money(K['cac'])}. Demand is capped by audience size, not budget.",
        )
    else:
        insight(i3, "Under-funded", "Retargeting data unavailable", "Adjust the filters to include Meta Retargeting.")

    insight(
        i4,
        "Biggest leak",
        "The middle of the funnel is leaking",
        f"{pct(K['attendance'])} of masterclass registrants attend, and only "
        f"{pct(K['lead_to_member'], 2)} of registrants become members. Fixing attendance and "
        f"speed-to-lead is cheaper than buying more traffic.",
    )

    left, right = st.columns([1.55, 1])
    with left:
        wk = (
            filtered.groupby("week_start", as_index=False)
            .agg(spend=("spend", "sum"), revenue=("revenue", "sum"))
            .sort_values("week_start")
        )
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_bar(
            x=wk.week_start,
            y=wk.spend,
            name="Media spend",
            marker_color=NAVY,
            opacity=0.85,
            hovertemplate="Week of %{x|%d %b}<br>Spend: $%{y:,.0f}<extra></extra>",
        )
        fig.add_scatter(
            x=wk.week_start,
            y=wk.revenue,
            name="Attributed revenue",
            mode="lines+markers",
            line=dict(color=GOLD, width=3),
            marker=dict(size=6),
            secondary_y=True,
            hovertemplate="Week of %{x|%d %b}<br>Revenue: $%{y:,.0f}<extra></extra>",
        )
        fig.update_yaxes(title_text="Spend (A$)", secondary_y=False, tickprefix="$", tickformat="~s")
        fig.update_yaxes(title_text="Revenue (A$)", secondary_y=True, tickprefix="$", tickformat="~s", showgrid=False)
        st.plotly_chart(style_fig(fig, 380, "Weekly spend versus attributed revenue"), width="stretch")

    with right:
        cont = channels_df.sort_values("share_members", ascending=False)
        fig = go.Figure()
        fig.add_bar(
            y=cont.channel,
            x=cont.share_spend,
            name="Share of spend",
            orientation="h",
            marker_color=NAVY,
            hovertemplate="%{y}<br>%{x:.1%} of spend<extra></extra>",
        )
        fig.add_bar(
            y=cont.channel,
            x=cont.share_members,
            name="Share of members",
            orientation="h",
            marker_color=GOLD,
            hovertemplate="%{y}<br>%{x:.1%} of members<extra></extra>",
        )
        fig.update_layout(barmode="group")
        fig.update_xaxes(tickformat=".0%")
        st.plotly_chart(style_fig(fig, 380, "Spend share versus member share"), width="stretch")

    left2, right2 = st.columns(2)
    with left2:
        steps = [
            ("Click to session", _div(K["sessions"], K["clicks"])),
            ("Session to registration", _div(K["regs"], K["sessions"])),
            ("Registration to attendance", _div(K["attended"], K["regs"])),
            ("Attendance to MQL", _div(K["mqls"], K["attended"])),
            ("MQL to call booked", _div(K["calls"], K["mqls"])),
            ("Call booked to show", _div(K["held"], K["calls"])),
            ("Call held to member", _div(K["members"], K["held"])),
        ]
        steps_df = pd.DataFrame(steps, columns=["Stage", "Rate"]).iloc[::-1]
        fig = px.bar(
            steps_df,
            x="Rate",
            y="Stage",
            orientation="h",
            text=steps_df["Rate"].map(lambda v: f"{v * 100:.1f}%"),
            color="Rate",
            color_continuous_scale=[[0, "#2a3442"], [1, ACCENT]],
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_layout(coloraxis_showscale=False)
        fig.update_xaxes(tickformat=".0%", range=[0, max(steps_df["Rate"].max() * 1.22, 0.2)])
        st.plotly_chart(style_fig(fig, 380, "Step conversion through the funnel", legend=False), width="stretch")

    with right2:
        cw = (
            filtered.groupby(["week_start", "channel"], as_index=False)
            .agg(spend=("spend", "sum"), members=("members", "sum"))
            .sort_values("week_start")
        )
        cw["cac"] = np.where(cw.members > 0, cw.spend / cw.members, np.nan)
        cw = cw.dropna(subset=["cac"])
        if not cw.empty:
            fig = px.line(
                cw,
                x="week_start",
                y="cac",
                color="channel",
                color_discrete_map=CHANNEL_COLORS,
                markers=True,
            )
            fig.update_yaxes(tickprefix="$", tickformat=",.0f")
            fig.update_traces(line=dict(width=2), marker=dict(size=4))
            st.plotly_chart(legend_right(style_fig(fig, 380, "Weekly CAC by channel")), width="stretch")
        else:
            st.info("Not enough member events to plot CAC by week.")

    with st.expander("How to read this dashboard"):
        st.markdown(
            "- Every metric is computed from the same filtered fact table, so the cards, charts and "
            "tables reconcile.\n"
            "- Deltas compare the selected period with the immediately preceding period of equal length.\n"
            "- CAC and CPL are media-only. They exclude agency fees, production and sales cost.\n"
            "- The Data Dictionary tab explains why each KPI exists; the Action Plan tab turns the "
            "findings into owners and dates.\n"
            "- All data is synthetic. Replace the loader in `data.py` with live ad-platform and HubSpot "
            "exports before making decisions."
        )


# ---------------------------------------------------------------------------
# North star
# ---------------------------------------------------------------------------

elif page == "North star":
    page_header(
        "Held quality sessions",
        "The North Star is the number of sales calls that were held and pass the quality "
        "checklist: budget confirmed, decision-maker present, a purchase window inside 12 "
        "months and clear intent. It joins volume and quality at the point where revenue is "
        "created — harder to game than registrations or MQLs.",
    )

    hqs = K["quality_sessions"]
    prior_hqs = PK.get("quality_sessions", np.nan)
    held = K["held"]
    q_rate = K["held_quality_rate"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "Held quality sessions",
        num(hqs),
        delta_str(hqs, prior_hqs),
        help="Held calls x segment quality rate. The North Star.",
    )
    c2.metric(
        "Cost per HQS",
        money(K["cost_per_quality_session"]),
        delta_str(K["cost_per_quality_session"], PK.get("cost_per_quality_session")),
        delta_color="inverse",
        help="Media spend / held quality sessions. Excludes sales cost.",
    )
    c3.metric(
        "Held → quality",
        pct(q_rate),
        delta_str(q_rate, PK.get("held_quality_rate")),
        help="Share of held calls that pass the quality checklist.",
    )
    c4.metric(
        "Held sessions",
        num(held),
        delta_str(held, PK.get("held")),
        help="Calls that were booked and attended.",
    )

    weekly = (
        filtered.groupby("week_start", as_index=False)
        .agg(
            hqs=("quality_sessions", "sum"),
            held=("calls_held", "sum"),
            spend=("spend", "sum"),
        )
        .sort_values("week_start")
    )
    weekly["cost_per_hqs"] = np.where(weekly.hqs > 0, weekly.spend / weekly.hqs, np.nan)

    fig = go.Figure()
    fig.add_bar(
        x=weekly.week_start,
        y=weekly.hqs,
        name="Held quality sessions",
        marker_color=ACCENT,
        hovertemplate="Week of %{x|%d %b}<br>HQS: %{y:,.0f}<extra></extra>",
    )
    fig.add_trace(
        go.Scatter(
            x=weekly.week_start,
            y=weekly.cost_per_hqs,
            name="Cost per HQS",
            yaxis="y2",
            mode="lines+markers",
            line=dict(color=VIOLET, width=2),
            marker=dict(size=4, color=VIOLET),
            hovertemplate="Week of %{x|%d %b}<br>Cost per HQS: $%{y:,.0f}<extra></extra>",
        )
    )
    fig = style_fig(fig, 370, "Weekly held quality sessions and cost per HQS")
    fig.update_layout(
        yaxis=dict(title="Held quality sessions"),
        yaxis2=dict(
            title="Cost per HQS (A$)",
            overlaying="y",
            side="right",
            showgrid=False,
            tickprefix="$",
            tickfont=dict(color="#9aa0ad"),
            title_font=dict(color="#9aa0ad"),
        ),
    )
    st.plotly_chart(fig, width="stretch")

    st.markdown("#### Where the North Star comes from")
    stages = pd.DataFrame(
        [
            ("Impressions", K["impressions"], np.nan, "—"),
            ("Clicks", K["clicks"], K["ctr"], "CTR"),
            ("Sessions", K["sessions"], K["lpv_rate"], "Session rate"),
            ("Registrations", K["regs"], K["reg_rate"], "Registration rate"),
            ("Attended", K["attended"], K["attendance"], "Attendance rate"),
            ("MQLs", K["mqls"], K["mql_rate"], "MQL rate"),
            ("Calls booked", K["calls"], K["call_rate"], "Booking rate"),
            ("Calls held", K["held"], K["show_rate"], "Show rate"),
            (
                "Held quality sessions",
                K["quality_sessions"],
                K["held_quality_rate"],
                "Quality rate",
            ),
        ],
        columns=["Stage", "Count", "Step rate", "Rate label"],
    )
    stages["Step rate"] = stages["Step rate"].map(lambda v: pct(v) if pd.notna(v) else "—")
    stages["Cost per unit"] = np.where(stages.Count > 0, K["spend"] / stages.Count, np.nan)
    stages["Cost per unit"] = stages["Cost per unit"].map(money)
    stages["Count"] = stages["Count"].map(num)
    st.dataframe(
        stages[["Stage", "Count", "Rate label", "Step rate", "Cost per unit"]],
        hide_index=True,
        width="stretch",
    )

    st.markdown("#### What moves the North Star")
    st.caption(
        "Illustrative operating lifts, applied one at a time with everything else held constant. "
        "Because HQS is multiplicative, a 1% relative improvement in any driver adds about 1% "
        "HQS; the bars reflect the size of each assumed lift, not an equal-effort comparison."
    )
    base_chain = {
        "CTR": (K["ctr"], 0.0005),
        "Session rate": (K["lpv_rate"], 0.002),
        "Registration rate": (K["reg_rate"], 0.0015),
        "Attendance rate": (K["attendance"], 0.02),
        "MQL rate": (K["mql_rate"], 0.015),
        "Booking rate": (K["call_rate"], 0.015),
        "Show rate": (K["show_rate"], 0.02),
        "Quality rate": (K["held_quality_rate"], 0.02),
    }
    base_hqs = K["quality_sessions"]
    sens_rows = []
    for name, (rate, lift) in base_chain.items():
        factors = {
            "CTR": K["ctr"],
            "Session rate": K["lpv_rate"],
            "Registration rate": K["reg_rate"],
            "Attendance rate": K["attendance"],
            "MQL rate": K["mql_rate"],
            "Booking rate": K["call_rate"],
            "Show rate": K["show_rate"],
            "Quality rate": K["held_quality_rate"],
        }
        factors[name] = min(rate + lift, 0.98)
        new_hqs = (
            K["spend"]
            * (1000 / K["cpm"])
            * factors["CTR"]
            * factors["Session rate"]
            * factors["Registration rate"]
            * factors["Attendance rate"]
            * factors["MQL rate"]
            * factors["Booking rate"]
            * factors["Show rate"]
            * factors["Quality rate"]
        )
        sens_rows.append(
            {
                "Driver": name,
                "Assumed lift": f"+{lift * 100:.1f} pts",
                "New HQS": new_hqs,
                "HQS lift": new_hqs - base_hqs,
                "Cost per HQS after": _div(K["spend"], new_hqs),
            }
        )
    sens = pd.DataFrame(sens_rows).sort_values("HQS lift", ascending=False)

    fig = px.bar(
        sens.sort_values("HQS lift"),
        x="HQS lift",
        y="Driver",
        orientation="h",
        text="HQS lift",
        color="HQS lift",
        color_continuous_scale=[[0, "#2a3442"], [1, ACCENT]],
    )
    fig.update_traces(
        texttemplate="%{text:,.0f} HQS",
        textposition="outside",
        cliponaxis=False,
    )
    fig.update_layout(coloraxis_showscale=False, xaxis_title="Additional held quality sessions")
    st.plotly_chart(
        style_fig(fig, 360, "HQS impact of an illustrative lift in each driver", legend=False),
        width="stretch",
    )
    st.dataframe(
        sens,
        hide_index=True,
        width="stretch",
        column_config={
            "New HQS": st.column_config.NumberColumn(format="%.0f"),
            "HQS lift": st.column_config.NumberColumn(format="+%.0f"),
            "Cost per HQS after": st.column_config.NumberColumn(format="$%.0f"),
        },
    )

    st.markdown("#### What it costs by channel")
    by_ch = (
        filtered.groupby("channel", as_index=False)
        .agg(
            spend=("spend", "sum"),
            held=("calls_held", "sum"),
            hqs=("quality_sessions", "sum"),
            members=("members", "sum"),
            revenue=("revenue", "sum"),
        )
    )
    by_ch["cost_per_hqs"] = np.where(by_ch.hqs > 0, by_ch.spend / by_ch.hqs, np.nan)
    by_ch["quality_rate"] = np.where(by_ch.held > 0, by_ch.hqs / by_ch.held, np.nan)
    by_ch["cac"] = np.where(by_ch.members > 0, by_ch.spend / by_ch.members, np.nan)
    by_ch = by_ch.sort_values("cost_per_hqs")

    fig = px.bar(
        by_ch,
        x="cost_per_hqs",
        y="channel",
        orientation="h",
        text=by_ch["cost_per_hqs"].map(money),
        color="cost_per_hqs",
        color_continuous_scale=[[0, ACCENT], [1, CORAL]],
        category_orders={"channel": by_ch.channel.tolist()},
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_title="Cost per held quality session (A$)",
    )
    fig.update_xaxes(tickprefix="$", tickformat=",.0f")
    st.plotly_chart(
        style_fig(fig, 340, "Cost per held quality session by channel", legend=False),
        width="stretch",
    )
    st.dataframe(
        pd.DataFrame(
            {
                "Channel": by_ch.channel,
                "Spend": by_ch.spend.map(money),
                "Held": by_ch.held.map(num),
                "Quality rate": by_ch.quality_rate.map(pct),
                "HQS": by_ch.hqs.map(num),
                "Cost per HQS": by_ch.cost_per_hqs.map(money),
                "CAC": by_ch.cac.map(money),
            }
        ),
        hide_index=True,
        width="stretch",
    )

    cheapest = by_ch.iloc[0]
    top_driver = sens.iloc[0]
    i1, i2, i3 = st.columns(3)
    insight(
        i1,
        "Cheapest quality",
        cheapest.channel,
        f"{money(cheapest.cost_per_hqs)} per held quality session, versus "
        f"{money(K['cost_per_quality_session'])} blended.",
    )
    insight(
        i2,
        "Biggest lever",
        f"{top_driver['Driver']} {top_driver['Assumed lift']}",
        f"Adds about {num(top_driver['HQS lift'])} held quality sessions at the same spend.",
    )
    insight(
        i3,
        "Quality rate",
        pct(q_rate),
        f"{num(hqs)} of {num(held)} held calls pass the checklist.",
    )

    st.markdown("#### Scenario: lift show rate and quality")
    s1, s2 = st.columns(2)
    show_lift = s1.slider("Show-rate improvement (pts)", 0, 10, 3, 1)
    qual_lift = s2.slider("Quality-rate improvement (pts)", 0, 10, 3, 1)
    new_show = min(K["show_rate"] + show_lift / 100, 0.95)
    new_qual = min(K["held_quality_rate"] + qual_lift / 100, 0.95)
    new_held = K["calls"] * new_show
    new_hqs = new_held * new_qual
    new_cost = _div(K["spend"], new_hqs)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Projected HQS", num(new_hqs), delta_str(new_hqs, hqs))
    m2.metric("Incremental HQS", num(new_hqs - hqs))
    m3.metric(
        "Cost per HQS",
        money(new_cost),
        delta_str(new_cost, K["cost_per_quality_session"]),
        delta_color="inverse",
    )
    m4.metric("Held sessions", num(new_held), delta_str(new_held, held))
    st.caption(
        "Assumes spend and upstream volume hold. Quality improvements usually require sales "
        "training, tighter qualification or better lead scoring; that cost is not modeled."
    )

    with st.expander("How held quality sessions are defined"):
        st.markdown(
            "- A **held quality session** is a sales call that was held and passes the QA "
            "checklist: budget confirmed, decision-maker present, purchase window inside 12 "
            "months and clear intent.\n"
            "- The sample applies segment quality rates: first-time 55%, experienced 72%, "
            "retiree 63%. Replace these with observed CRM and QA outcomes.\n"
            "- **Cost per HQS** is media spend / held quality sessions. It excludes sales cost, "
            "training and tooling.\n"
            "- The driver lifts are illustrative, not forecasts; each is applied one at a time "
            "with the rest of the funnel held constant."
        )


# ---------------------------------------------------------------------------
# KPI dashboard
# ---------------------------------------------------------------------------

elif page == "KPI dashboard":
    page_header(
        "KPI dashboard",
        "Funnel health, unit economics and segment performance. Use this page for the weekly "
        "growth review: start with the guardrail cards, then find the stage that explains any move.",
    )

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Cost per lead", money(K["cpl"]), delta_str(K["cpl"], PK.get("cpl")), delta_color="inverse")
    c2.metric("Cost per MQL", money(K["cost_per_mql"]), delta_str(K["cost_per_mql"], PK.get("cost_per_mql")), delta_color="inverse")
    c3.metric("Cost per call", money(K["cost_per_call"]), delta_str(K["cost_per_call"], PK.get("cost_per_call")), delta_color="inverse")
    c4.metric("Call show rate", pct(K["show_rate"]), delta_str(K["show_rate"], PK.get("show_rate")))
    c5.metric("Call to member", pct(K["close_rate"]), delta_str(K["close_rate"], PK.get("close_rate")))
    c6.metric("CAC payback", f"{K['payback_months']:.1f} mo" if pd.notna(K["payback_months"]) else "-", help="CAC divided by one month of first-year revenue. Lower is better.")

    st.markdown("#### Funnel diagnostics")
    benchmark = {
        "Click to session": 0.90,
        "Session to registration": 0.04,
        "Registration to attendance": 0.55,
        "Attendance to MQL": 0.65,
        "MQL to call booked": 0.40,
        "Call booked to show": 0.70,
        "Call held to member": 0.15,
    }
    stages = [
        ("Click to session", K["clicks"], K["sessions"]),
        ("Session to registration", K["sessions"], K["regs"]),
        ("Registration to attendance", K["regs"], K["attended"]),
        ("Attendance to MQL", K["attended"], K["mqls"]),
        ("MQL to call booked", K["mqls"], K["calls"]),
        ("Call booked to show", K["calls"], K["held"]),
        ("Call held to member", K["held"], K["members"]),
    ]
    rows = []
    for name, before, after in stages:
        rate = _div(after, before)
        bm = benchmark[name]
        rows.append(
            {
                "Stage": name,
                "Volume in": before,
                "Volume out": after,
                "Step conversion": rate * 100,
                "Benchmark": bm * 100,
                "Gap (pts)": (rate - bm) * 100,
                "Status": "On track" if rate >= bm else "Watch",
            }
        )
    fun = pd.DataFrame(rows)
    st.dataframe(
        fun,
        hide_index=True,
        width="stretch",
        column_config={
            "Volume in": st.column_config.NumberColumn(format="%,.0f"),
            "Volume out": st.column_config.NumberColumn(format="%,.0f"),
            "Step conversion": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100),
            "Benchmark": st.column_config.NumberColumn(format="%.1f%%"),
            "Gap (pts)": st.column_config.NumberColumn(format="%+.1f"),
            "Status": st.column_config.TextColumn(),
        },
    )

    left, right = st.columns([1.3, 1])
    with left:
        wk = (
            filtered.groupby("week_start", as_index=False)
            .agg(
                regs=("mc_regs", "sum"),
                attended=("mc_attended", "sum"),
                mqls=("mqls", "sum"),
                calls=("calls_booked", "sum"),
                held=("calls_held", "sum"),
                members=("members", "sum"),
            )
            .sort_values("week_start")
        )
        trend = pd.DataFrame(
            {
                "week_start": wk.week_start,
                "Attendance": np.where(wk.regs > 0, wk.attended / wk.regs, np.nan) * 100,
                "MQL rate": np.where(wk.attended > 0, wk.mqls / wk.attended, np.nan) * 100,
                "Show rate": np.where(wk.calls > 0, wk.held / wk.calls, np.nan) * 100,
                "Lead to member": np.where(wk.regs > 0, wk.members / wk.regs, np.nan) * 100,
            }
        )
        trend_m = trend.melt("week_start", var_name="Measure", value_name="Rate")
        fig = px.line(
            trend_m,
            x="week_start",
            y="Rate",
            color="Measure",
            markers=True,
            color_discrete_sequence=[NAVY, GOLD, BLUE, GREEN],
        )
        fig.update_yaxes(title_text="Rate", ticksuffix="%")
        fig.update_traces(line=dict(width=2), marker=dict(size=4))
        st.plotly_chart(legend_right(style_fig(fig, 380, "Weekly conversion rates")), width="stretch")

    with right:
        st.markdown("**Segment performance**")
        seg = (
            filtered.groupby("segment", as_index=False)
            .agg(
                spend=("spend", "sum"),
                revenue=("revenue", "sum"),
                regs=("mc_regs", "sum"),
                mqls=("mqls", "sum"),
                held=("calls_held", "sum"),
                members=("members", "sum"),
            )
            .merge(LAG[["segment", "avg_days_to_member"]], on="segment", how="left")
        )
        seg["cac"] = np.where(seg.members > 0, seg.spend / seg.members, np.nan)
        seg["aov"] = np.where(seg.members > 0, seg.revenue / seg.members, np.nan)
        seg["ltv_cac"] = np.where(seg.cac > 0, seg.aov * LTV_MULT / seg.cac, np.nan)
        seg["lead_to_member"] = np.where(seg.regs > 0, seg.members / seg.regs, np.nan) * 100
        seg = seg.sort_values("members", ascending=False)
        seg_disp = pd.DataFrame(
            {
                "Segment": seg.segment,
                "Members": seg.members,
                "CAC": seg.cac,
                "AOV": seg.aov,
                "LTV:CAC": seg.ltv_cac,
                "Lead to member (%)": seg.lead_to_member,
                "Avg days": seg.avg_days_to_member,
            }
        )
        st.dataframe(
            seg_disp,
            hide_index=True,
            width="stretch",
            column_config={
                "Members": st.column_config.NumberColumn(format="%.0f"),
                "CAC": st.column_config.NumberColumn(format="$%.0f"),
                "AOV": st.column_config.NumberColumn(format="$%.0f"),
                "LTV:CAC": st.column_config.NumberColumn(format="%.1fx"),
                "Lead to member (%)": st.column_config.NumberColumn(format="%.2f%%"),
                "Avg days": st.column_config.NumberColumn(format="%.0f"),
            },
        )
        st.caption("Avg days is a modelled lag, not a same-period calculation.")

    st.markdown("#### Guardrails")
    g1, g2, g3, g4 = st.columns(4)
    g1.metric("LTV:CAC", mult(K["ltv_cac"]), help="Target at least 4:1.")
    g2.metric("CAC as % of AOV", pct(_div(K["cac"], K["aov"])), help="Target below 30%.")
    g3.metric("MQL rate", pct(K["mql_rate"]), delta_str(K["mql_rate"], PK.get("mql_rate")))
    g4.metric("Cost per booked call", money(K["cost_per_call"]), delta_str(K["cost_per_call"], PK.get("cost_per_call")), delta_color="inverse")

    with st.expander("View the underlying step table as CSV"):
        download_csv(fun, "Download funnel diagnostics (CSV)", "fpi_funnel_diagnostics.csv")


# ---------------------------------------------------------------------------
# Paid media
# ---------------------------------------------------------------------------

elif page == "Paid media":
    page_header(
        "Paid media performance",
        "Where the money goes, what it returns, and how a reallocation would change the blended "
        "result. Efficiency is judged on members and revenue, not clicks.",
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Media spend", money(K["spend"]), delta_str(K["spend"], PK.get("spend")))
    c2.metric("Members", num(K["members"]), delta_str(K["members"], PK.get("members")))
    c3.metric("Blended CAC", money(K["cac"]), delta_str(K["cac"], PK.get("cac")), delta_color="inverse")
    c4.metric("ROAS", mult(K["roas"]), delta_str(K["roas"], PK.get("roas")))

    st.markdown("#### Channel efficiency")
    ch_disp = pd.DataFrame(
        {
            "Channel": channels_df.channel,
            "Spend": channels_df.spend,
            "Spend share": channels_df.share_spend * 100,
            "Impressions": channels_df.impressions,
            "CTR": channels_df.ctr * 100,
            "CPM": channels_df.cpm,
            "CPL": channels_df.cpl,
            "MQLs": channels_df.mqls,
            "Cost / MQL": channels_df.cost_per_mql,
            "Calls held": channels_df.held,
            "Cost / call": channels_df.cost_per_call,
            "Members": channels_df.members,
            "CAC": channels_df.cac,
            "Revenue": channels_df.revenue,
            "ROAS": channels_df.roas,
        }
    )
    st.dataframe(
        ch_disp,
        hide_index=True,
        width="stretch",
        column_config={
            "Spend": st.column_config.NumberColumn(format="$%.0f"),
            "Spend share": st.column_config.NumberColumn(format="%.1f%%"),
            "Impressions": st.column_config.NumberColumn(format="%,.0f"),
            "CTR": st.column_config.NumberColumn(format="%.2f%%"),
            "CPM": st.column_config.NumberColumn(format="$%.2f"),
            "CPL": st.column_config.NumberColumn(format="$%.0f"),
            "MQLs": st.column_config.NumberColumn(format="%.0f"),
            "Cost / MQL": st.column_config.NumberColumn(format="$%.0f"),
            "Calls held": st.column_config.NumberColumn(format="%.0f"),
            "Cost / call": st.column_config.NumberColumn(format="$%.0f"),
            "Members": st.column_config.NumberColumn(format="%.0f"),
            "CAC": st.column_config.NumberColumn(format="$%.0f"),
            "Revenue": st.column_config.NumberColumn(format="$%.0f"),
            "ROAS": st.column_config.NumberColumn(format="%.1fx"),
        },
    )

    left, right = st.columns(2)
    with left:
        plot_df = channels_df.dropna(subset=["cac", "roas"])
        if not plot_df.empty:
            plot_df = plot_df.copy()
            plot_df["member_share_pct"] = plot_df.share_members * 100
            fig = px.scatter(
                plot_df,
                x="cac",
                y="roas",
                size="share_spend",
                color="channel",
                color_discrete_map=CHANNEL_COLORS,
                hover_name="channel",
                hover_data={"members": ":.0f", "spend": ":$,.0f", "member_share_pct": ":.1f"},
                size_max=55,
            )
            fig.update_xaxes(title_text="CAC (A$)", tickprefix="$", tickformat=",.0f")
            fig.update_yaxes(title_text="ROAS", ticksuffix="x", tickformat=".1f")
            st.plotly_chart(legend_right(style_fig(fig, 380, "CAC versus ROAS (bubble = share of spend)")), width="stretch")
        else:
            st.info("Not enough member events to plot channel efficiency.")

    with right:
        wk = (
            filtered.groupby(["week_start", "channel"], as_index=False)
            .agg(spend=("spend", "sum"))
            .sort_values("week_start")
        )
        fig = px.area(
            wk,
            x="week_start",
            y="spend",
            color="channel",
            color_discrete_map=CHANNEL_COLORS,
        )
        fig.update_yaxes(title_text="Spend (A$)", tickprefix="$", tickformat="~s")
        st.plotly_chart(legend_right(style_fig(fig, 380, "Weekly spend mix")), width="stretch")

    st.markdown("#### Reallocation scenario")
    st.markdown(
        '<div class="section-note">Illustrative model. It moves spend between channels at their '
        "current average CAC and assumes constant marginal efficiency, which is optimistic. Use it "
        "to frame the decision, then validate with a geo holdout.</div>",
        unsafe_allow_html=True,
    )
    pool_pct = st.slider(
        "Reallocate this share of combined YouTube and Meta Prospecting spend",
        min_value=0,
        max_value=25,
        value=12,
        step=1,
        format="%d%%",
    )

    def chan_row(name):
        row = channels_df[channels_df.channel == name]
        return row.iloc[0] if not row.empty else None

    meta_row = chan_row("Meta Prospecting")
    yt_row = chan_row("YouTube In-Stream")
    search_row = chan_row("Google Search")
    ret_row = chan_row("Meta Retargeting")

    if all(r is not None for r in (meta_row, yt_row, search_row, ret_row)) and K["members"] > 0:
        pool = (pool_pct / 100) * (meta_row.spend + yt_row.spend)
        alloc_search = pool * 0.60
        alloc_ret = pool * 0.40
        remove_meta = alloc_search * (meta_row.spend / (meta_row.spend + yt_row.spend)) + alloc_ret * (
            meta_row.spend / (meta_row.spend + yt_row.spend)
        )
        remove_yt = pool - remove_meta
        new_members = (
            K["members"]
            + _div(alloc_search, search_row.cac)
            + _div(alloc_ret, ret_row.cac)
            - _div(remove_meta, meta_row.cac)
            - _div(remove_yt, yt_row.cac)
        )
        new_revenue = new_members * K["aov"]
        new_cac = _div(K["spend"], new_members)
        new_roas = _div(new_revenue, K["spend"])

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Projected members", num(new_members), delta_str(new_members, K["members"]))
        s2.metric("Projected CAC", money(new_cac), delta_str(new_cac, K["cac"]), delta_color="inverse")
        s3.metric("Projected ROAS", mult(new_roas), delta_str(new_roas, K["roas"]))
        s4.metric("Projected revenue", money(new_revenue), delta_str(new_revenue, K["revenue"]))
    else:
        st.info("Scenario needs data for all five channels and at least one member.")

    st.markdown("#### Recommended allocation")
    rec = RECOMMENDED_SPLIT.copy()
    fig = go.Figure()
    fig.add_bar(name="Current", x=rec.Channel, y=rec["Current share"] * 100, marker_color=SLATE)
    fig.add_bar(name="Recommended", x=rec.Channel, y=rec["Recommended share"] * 100, marker_color=GOLD)
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Share of budget", ticksuffix="%")
    st.plotly_chart(style_fig(fig, 340, "Current versus recommended budget split"), width="stretch")
    st.dataframe(
        rec.assign(
            **{
                "Current share": (rec["Current share"] * 100).round(1),
                "Recommended share": (rec["Recommended share"] * 100).round(1),
            }
        ),
        hide_index=True,
        width="stretch",
        column_config={
            "Current share": st.column_config.NumberColumn(format="%.1f%%"),
            "Recommended share": st.column_config.NumberColumn(format="%.1f%%"),
        },
    )
    download_csv(ch_disp, "Download channel efficiency (CSV)", "fpi_channel_efficiency.csv")


# ---------------------------------------------------------------------------
# Lead quality
# ---------------------------------------------------------------------------

elif page == "Lead quality":
    page_header(
        "Lead quality and sales handoff",
        "Volume is not the goal. This page shows which segments convert, how long they take, "
        "and how much revenue is lost in the handoff between marketing and sales.",
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Masterclass leads", num(K["regs"]), delta_str(K["regs"], PK.get("regs")))
    c2.metric("MQL rate", pct(K["mql_rate"]), delta_str(K["mql_rate"], PK.get("mql_rate")))
    c3.metric("Call show rate", pct(K["show_rate"]), delta_str(K["show_rate"], PK.get("show_rate")))
    c4.metric("Lead to member", pct(K["lead_to_member"], 2), delta_str(K["lead_to_member"], PK.get("lead_to_member")))

    left, right = st.columns([1.05, 1])
    with left:
        resp = RESPONSE.copy()
        resp["conversion_pct"] = resp.conversion_rate * 100
        fig = px.bar(
            resp,
            x="response_bucket",
            y="conversion_pct",
            text=resp["conversion_pct"].map(lambda v: f"{v:.1f}%"),
            color="conversion_pct",
            color_continuous_scale=[[0, "#2a3442"], [1, ACCENT]],
            hover_data={"leads": ":,.0f", "members": ":,.0f"},
        )
        fig.update_layout(coloraxis_showscale=False)
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_xaxes(title_text="First human contact after lead arrives")
        fig.update_yaxes(title_text="Lead to member", ticksuffix="%")
        st.plotly_chart(style_fig(fig, 380, "Speed to lead versus conversion (sample benchmark)"), width="stretch")
        st.caption(
            "Illustrative benchmark, not a same-period CRM extract. Replace with your own "
            "response-time buckets before setting the SLA."
        )

    with right:
        seg = (
            filtered.groupby("segment", as_index=False)
            .agg(
                spend=("spend", "sum"),
                revenue=("revenue", "sum"),
                regs=("mc_regs", "sum"),
                attended=("mc_attended", "sum"),
                mqls=("mqls", "sum"),
                held=("calls_held", "sum"),
                members=("members", "sum"),
            )
            .merge(LAG[["segment", "avg_days_to_member", "median_days_to_member", "p90_days_to_member"]], on="segment", how="left")
        )
        seg["cac"] = np.where(seg.members > 0, seg.spend / seg.members, np.nan)
        seg["aov"] = np.where(seg.members > 0, seg.revenue / seg.members, np.nan)
        seg["ltv_cac"] = np.where(seg.cac > 0, seg.aov * LTV_MULT / seg.cac, np.nan)
        seg["lead_to_member"] = np.where(seg.regs > 0, seg.members / seg.regs, np.nan) * 100
        seg = seg.sort_values("members", ascending=False)
        seg_disp = pd.DataFrame(
            {
                "Segment": seg.segment,
                "Leads": seg.regs,
                "MQLs": seg.mqls,
                "Calls held": seg.held,
                "Members": seg.members,
                "CAC": seg.cac,
                "AOV": seg.aov,
                "LTV:CAC": seg.ltv_cac,
                "Lead to member (%)": seg.lead_to_member,
                "Avg days": seg.avg_days_to_member,
                "P90 days": seg.p90_days_to_member,
            }
        )
        st.dataframe(
            seg_disp,
            hide_index=True,
            width="stretch",
            column_config={
                "Leads": st.column_config.NumberColumn(format="%.0f"),
                "MQLs": st.column_config.NumberColumn(format="%.0f"),
                "Calls held": st.column_config.NumberColumn(format="%.0f"),
                "Members": st.column_config.NumberColumn(format="%.0f"),
                "CAC": st.column_config.NumberColumn(format="$%.0f"),
                "AOV": st.column_config.NumberColumn(format="$%.0f"),
                "LTV:CAC": st.column_config.NumberColumn(format="%.1fx"),
                "Lead to member (%)": st.column_config.NumberColumn(format="%.2f%%"),
                "Avg days": st.column_config.NumberColumn(format="%.0f"),
                "P90 days": st.column_config.NumberColumn(format="%.0f"),
            },
        )
        st.caption("Lag figures are modelled. Replace with cohort-observed values from CRM.")

    st.markdown("#### Revenue by month and segment")
    mon = (
        filtered.groupby(["month", "segment"], as_index=False)
        .agg(revenue=("revenue", "sum"), members=("members", "sum"))
        .sort_values("month")
    )
    fig = px.bar(
        mon,
        x="month",
        y="revenue",
        color="segment",
        color_discrete_map=SEGMENT_COLORS,
        barmode="stack",
        text="members",
    )
    fig.update_traces(texttemplate="%{text:.0f} members", textposition="inside", insidetextanchor="middle")
    fig.update_yaxes(title_text="Attributed revenue (A$)", tickprefix="$", tickformat="~s")
    st.plotly_chart(style_fig(fig, 360, "Attributed revenue by conversion month"), width="stretch")

    st.markdown("#### Segment funnel conversion")
    seg_full = (
        filtered.groupby("segment", as_index=False)
        .agg(
            regs=("mc_regs", "sum"),
            attended=("mc_attended", "sum"),
            mqls=("mqls", "sum"),
            held=("calls_held", "sum"),
            members=("members", "sum"),
        )
    )
    funnel_rows = []
    for _, row in seg_full.iterrows():
        funnel_rows.append(
            {
                "Segment": row.segment,
                "Lead to attendance": _div(row.attended, row.regs) * 100,
                "Attendance to MQL": _div(row.mqls, row.attended) * 100,
                "MQL to call held": _div(row.held, row.mqls) * 100,
                "Call held to member": _div(row.members, row.held) * 100,
            }
        )
    fun_seg = pd.DataFrame(funnel_rows)
    fun_m = fun_seg.melt("Segment", var_name="Stage", value_name="Rate")
    fig = px.bar(
        fun_m,
        x="Stage",
        y="Rate",
        color="Segment",
        barmode="group",
        color_discrete_map=SEGMENT_COLORS,
    )
    fig.update_yaxes(title_text="Conversion", ticksuffix="%")
    st.plotly_chart(style_fig(fig, 360, "Where each segment drops out"), width="stretch")

    download_csv(seg_disp, "Download segment performance (CSV)", "fpi_segment_performance.csv")


# ---------------------------------------------------------------------------
# Creative analytics
# ---------------------------------------------------------------------------

elif page == "Creative analytics":
    page_header(
        "Creative analytics",
        "Which angles, formats and individual ads create members efficiently - and which are "
        "quietly burning budget. Creative is the main lever available without changing the offer.",
    )

    cre = (
        creative_filtered.groupby(["creative_id", "creative_name", "channel", "format", "angle"], as_index=False)
        .agg(
            spend=("spend", "sum"),
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            regs=("mc_regs", "sum"),
            mqls=("mqls", "sum"),
            members=("members", "sum"),
            revenue=("revenue", "sum"),
        )
        .copy()
    )
    cre["ctr"] = np.where(cre.impressions > 0, cre.clicks / cre.impressions, np.nan)
    cre["cpl"] = np.where(cre.regs > 0, cre.spend / cre.regs, np.nan)
    cre["cac"] = np.where(cre.members > 0, cre.spend / cre.members, np.nan)
    cre["roas"] = np.where(cre.spend > 0, cre.revenue / cre.spend, np.nan)
    cre = cre.sort_values("spend", ascending=False)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active creatives", num(len(cre)))
    top = cre.dropna(subset=["cac"]).sort_values("cac").head(1)
    bottom = cre.dropna(subset=["cac"]).sort_values("cac").tail(1)
    c2.metric("Best CAC", money(top.cac.iloc[0]) if not top.empty else "-", help=top.creative_name.iloc[0] if not top.empty else None)
    c3.metric("Worst CAC", money(bottom.cac.iloc[0]) if not bottom.empty else "-", help=bottom.creative_name.iloc[0] if not bottom.empty else None)
    c4.metric("Best ROAS", mult(cre.roas.max()) if cre.roas.notna().any() else "-")

    st.markdown("#### Creative scorecard")
    cre_disp = pd.DataFrame(
        {
            "Creative": cre.creative_name,
            "Channel": cre.channel,
            "Format": cre.format,
            "Angle": cre.angle,
            "Spend": cre.spend,
            "CTR (%)": cre.ctr * 100,
            "Leads": cre.regs,
            "CPL": cre.cpl,
            "Members": cre.members,
            "CAC": cre.cac,
            "ROAS": cre.roas,
        }
    )
    st.dataframe(
        cre_disp,
        hide_index=True,
        width="stretch",
        column_config={
            "Spend": st.column_config.NumberColumn(format="$%.0f"),
            "CTR (%)": st.column_config.NumberColumn(format="%.2f%%"),
            "Leads": st.column_config.NumberColumn(format="%.0f"),
            "CPL": st.column_config.NumberColumn(format="$%.0f"),
            "Members": st.column_config.NumberColumn(format="%.0f"),
            "CAC": st.column_config.NumberColumn(format="$%.0f"),
            "ROAS": st.column_config.NumberColumn(format="%.1fx"),
        },
    )

    left, right = st.columns(2)
    with left:
        plot_cre = cre.dropna(subset=["ctr", "cac"]).copy()
        if not plot_cre.empty:
            fig = px.scatter(
                plot_cre,
                x="ctr",
                y="cac",
                size="spend",
                color="format",
                hover_name="creative_name",
                hover_data={"channel": True, "members": ":.0f", "roas": ":.1f"},
                size_max=45,
            )
            fig.update_xaxes(title_text="CTR", tickformat=".2%")
            fig.update_yaxes(title_text="CAC (A$)", tickprefix="$", tickformat=",.0f")
            st.plotly_chart(style_fig(fig, 380, "CTR versus CAC by creative"), width="stretch")
        else:
            st.info("Not enough creative data to plot.")

    with right:
        mp = creative_filtered[creative_filtered.channel == "Meta Prospecting"]
        wk = (
            mp.groupby(["week_start", "angle"], as_index=False)
            .agg(clicks=("clicks", "sum"), impressions=("impressions", "sum"))
            .sort_values("week_start")
        )
        wk["ctr"] = np.where(wk.impressions > 0, wk.clicks / wk.impressions, np.nan) * 100
        if not wk.empty:
            fig = px.line(wk, x="week_start", y="ctr", color="angle", markers=True)
            fig.update_yaxes(title_text="CTR", ticksuffix="%")
            st.plotly_chart(style_fig(fig, 380, "Meta prospecting: weekly CTR by angle"), width="stretch")
        else:
            st.info("Select Meta Prospecting to view creative fatigue.")

    st.markdown("#### Format performance")
    fmt = (
        creative_filtered.groupby("format", as_index=False)
        .agg(
            spend=("spend", "sum"),
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            regs=("mc_regs", "sum"),
            members=("members", "sum"),
            revenue=("revenue", "sum"),
        )
        .copy()
    )
    fmt["ctr"] = np.where(fmt.impressions > 0, fmt.clicks / fmt.impressions, np.nan) * 100
    fmt["cpl"] = np.where(fmt.regs > 0, fmt.spend / fmt.regs, np.nan)
    fmt["cac"] = np.where(fmt.members > 0, fmt.spend / fmt.members, np.nan)
    fmt["roas"] = np.where(fmt.spend > 0, fmt.revenue / fmt.spend, np.nan)
    fig = px.bar(
        fmt.sort_values("cac"),
        x="format",
        y="cac",
        color="cac",
        color_continuous_scale=[[0, "#2a3442"], [1, ACCENT]],
        text=fmt.sort_values("cac")["cac"].map(lambda v: f"${v:,.0f}" if pd.notna(v) else "-"),
    )
    fig.update_layout(coloraxis_showscale=False)
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_yaxes(title_text="CAC (A$)", tickprefix="$", tickformat=",.0f")
    st.plotly_chart(style_fig(fig, 320, "CAC by creative format", legend=False), width="stretch")

    download_csv(cre_disp, "Download creative scorecard (CSV)", "fpi_creative_scorecard.csv")


# ---------------------------------------------------------------------------
# Data dictionary
# ---------------------------------------------------------------------------

elif page == "Data dictionary":
    page_header(
        "KPI data dictionary",
        "Why each metric exists, exactly how it is calculated, where it comes from and the "
        "guardrail that keeps it healthy. This is the contract between marketing, sales, data and finance.",
    )

    st.markdown("#### Measurement framework")
    f1, f2, f3 = st.columns(3)
    f1.markdown(
        "**1. Business outcomes**\n\nSpend, revenue, CAC, MER, LTV:CAC and payback. These decide "
        "whether the growth engine is viable and how much can be invested."
    )
    f2.markdown(
        "**2. Funnel diagnostics**\n\nCPM, CTR, landing-page rate, CPL, attendance, MQL, call and "
        "show rates. These explain *why* an outcome moved and where to intervene."
    )
    f3.markdown(
        "**3. Measurement integrity**\n\nOffline match rate, incremental ROAS, lead quality score "
        "and pacing. These keep the first two layers honest."
    )

    dd = pd.DataFrame(KPI_DICTIONARY)
    filter_col1, filter_col2 = st.columns([1, 2])
    with filter_col1:
        stage_options = ["All stages"] + sorted(dd.Stage.unique().tolist())
        stage_choice = st.selectbox("Filter by stage", stage_options)
    with filter_col2:
        query = st.text_input("Search KPI, definition or purpose", placeholder="e.g. CAC, attendance, attribution")

    view = dd.copy()
    if stage_choice != "All stages":
        view = view[view.Stage == stage_choice]
    if query.strip():
        q = query.strip().lower()
        mask = (
            view.KPI.str.lower().str.contains(q, na=False)
            | view.Definition.str.lower().str.contains(q, na=False)
            | view["Why it matters"].str.lower().str.contains(q, na=False)
        )
        view = view[mask]

    st.dataframe(
        view,
        hide_index=True,
        width="stretch",
        column_config={
            "Stage": st.column_config.TextColumn(width="small"),
            "KPI": st.column_config.TextColumn(width="medium"),
            "Definition": st.column_config.TextColumn(width="large"),
            "Formula": st.column_config.TextColumn(width="medium"),
            "Why it matters": st.column_config.TextColumn(width="large"),
            "Source / owner": st.column_config.TextColumn(width="medium"),
            "Target / guardrail": st.column_config.TextColumn(width="medium"),
        },
    )
    download_csv(view, "Download filtered data dictionary (CSV)", "fpi_kpi_dictionary.csv")

    st.markdown("#### KPI details by stage")
    for stage in sorted(dd.Stage.unique()):
        stage_rows = dd[dd.Stage == stage]
        with st.expander(f"{stage} ({len(stage_rows)} KPIs)"):
            for row in stage_rows.to_dict("records"):
                st.markdown(f"**{row['KPI']}**")
                st.markdown(row["Definition"])
                st.markdown(f"*Formula:* `{row['Formula']}`")
                st.markdown(f"*Why it matters:* {row['Why it matters']}")
                st.caption(f"Source / owner: {row['Source / owner']}  |  Target: {row['Target / guardrail']}")
                st.divider()

    st.markdown("#### Assumptions behind the sample")
    for title, body in ASSUMPTIONS:
        st.markdown(f"**{title}.** {body}")


# ---------------------------------------------------------------------------
# Action plan
# ---------------------------------------------------------------------------

elif page == "Action plan":
    page_header(
        "Sample action plan",
        "A prioritised, owner-assigned plan built from the sample findings. P0 items unlock "
        "measurement and trust; P1 items move efficiency; P2 items build durable advantage.",
    )

    st.markdown("#### Findings this plan responds to")
    f1, f2, f3, f4 = st.columns(4)
    f1.markdown(
        "**Measurement gap**\n\nMedia is optimised on form fills, not members. There is no closed "
        "loop between HubSpot outcomes and the ad platforms."
    )
    f2.markdown(
        "**Mid-funnel leak**\n\nMasterclass attendance and speed-to-lead are the largest "
        "controllable losses, and both are cheaper to fix than buying more traffic."
    )
    f3.markdown(
        "**Misallocated budget**\n\nSearch and retargeting are the most efficient channels but are "
        "under-funded relative to Meta prospecting and YouTube."
    )
    f4.markdown(
        "**Creative fatigue**\n\nMeta CPM is rising and CTR is falling. Founder-led and data angles "
        "outperform testimonial and UGC in the sample."
    )

    st.markdown("#### Prioritised actions")
    ap = pd.DataFrame(ACTION_PLAN)
    prio = st.multiselect("Priority", ["P0", "P1", "P2"], default=["P0", "P1", "P2"])
    ap_view = ap[ap.Priority.isin(prio)].copy()

    compact = ap_view[
        ["Priority", "Workstream", "Action", "Owner", "Timeline", "Expected impact"]
    ]
    st.dataframe(
        compact,
        hide_index=True,
        width="stretch",
        column_config={
            "Priority": st.column_config.TextColumn(width="small"),
            "Workstream": st.column_config.TextColumn(width="small"),
            "Action": st.column_config.TextColumn(width="large"),
            "Owner": st.column_config.TextColumn(width="small"),
            "Timeline": st.column_config.TextColumn(width="small"),
            "Expected impact": st.column_config.TextColumn(width="medium"),
        },
    )
    download_csv(ap_view, "Download action plan (CSV)", "fpi_action_plan.csv")

    st.markdown("#### Action detail")
    for p in ["P0", "P1", "P2"]:
        group = ap_view[ap_view.Priority == p]
        if group.empty:
            continue
        with st.expander(f"{p} actions ({len(group)})", expanded=(p == "P0")):
            for row in group.to_dict("records"):
                st.markdown(f"**{row['Action']}**")
                st.markdown(f"*Why / evidence:* {row['Why / evidence']}")
                st.markdown(
                    f"*KPI moved:* {row['KPI moved']}  |  *Owner:* {row['Owner']}  |  "
                    f"*Timeline:* {row['Timeline']}  |  *Effort:* {row['Effort']}"
                )
                st.caption(f"Expected impact: {row['Expected impact']}")
                st.divider()

    st.markdown("#### 90-day roadmap")
    r1, r2, r3 = st.columns(3)
    for col, (phase, items) in zip((r1, r2, r3), ROADMAP.items()):
        with col:
            st.markdown(f"**{phase}**")
            for item in items:
                st.markdown(f"- {item}")

    st.markdown("#### Success measures")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Blended CAC", "<= $2,200", "-8 to -12% target", delta_color="off")
    m2.metric("Masterclass attendance", ">= 55%", "+8 to 12 pts", delta_color="off")
    m3.metric("Lead to member", ">= 3.0%", "+20% target", delta_color="off")
    m4.metric("Offline match rate", ">= 80%", "measurement gate", delta_color="off")

    st.markdown("#### Strategic bets")
    for title, body in STRATEGIC_BETS:
        st.markdown(f"**{title}.** {body}")

    with st.expander("Caveats before executing"):
        for title, body in ASSUMPTIONS:
            st.markdown(f"**{title}.** {body}")
