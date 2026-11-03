"""Synthetic marketing dataset for the Freedom Property Investors sample dashboard.

The numbers are illustrative and calibrated to the public positioning of the
business (masterclass-led, high-ticket property advisory, three investor
segments). They are NOT actual Freedom Property Investors performance data.
All assumptions live in content.ASSUMPTIONS.
"""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

SEED = 20261026
START = date(2026, 4, 27)
DAYS = 182
END = START + timedelta(days=DAYS - 1)

SEGMENTS = ("First-time investor", "Experienced investor", "Retiree")
SEGMENT_CLOSE_MULT = {
    "First-time investor": 0.82,
    "Experienced investor": 1.28,
    "Retiree": 1.02,
}
SEGMENT_AOV = {
    "First-time investor": 7_800,
    "Experienced investor": 12_000,
    "Retiree": 9_500,
}

# spend = average daily spend; cpm/ctr are baseline; downstream rates are
# step conversion rates. seg_mix = share of spend by segment.
CHANNEL_PARAMS = {
    "Meta Prospecting": {
        "spend": 1600,
        "cpm": 26.0,
        "ctr": 0.0135,
        "lpv": 0.90,
        "reg": 0.040,
        "attend": 0.42,
        "mql": 0.60,
        "call": 0.50,
        "show": 0.66,
        "close": 0.38,
        "seg_mix": (0.55, 0.30, 0.15),
        "cpm_trend": 0.22,
        "ctr_trend": -0.15,
    },
    "Meta Retargeting": {
        "spend": 250,
        "cpm": 34.0,
        "ctr": 0.0280,
        "lpv": 0.93,
        "reg": 0.075,
        "attend": 0.50,
        "mql": 0.68,
        "call": 0.55,
        "show": 0.72,
        "close": 0.12,
        "seg_mix": (0.45, 0.35, 0.20),
        "cpm_trend": 0.10,
        "ctr_trend": -0.06,
    },
    "YouTube In-Stream": {
        "spend": 900,
        "cpm": 18.0,
        "ctr": 0.0090,
        "lpv": 0.90,
        "reg": 0.030,
        "attend": 0.40,
        "mql": 0.58,
        "call": 0.45,
        "show": 0.68,
        "close": 0.28,
        "seg_mix": (0.40, 0.40, 0.20),
        "cpm_trend": 0.08,
        "ctr_trend": 0.10,
    },
    "Google Search": {
        "spend": 450,
        "cpm": 55.0,
        "ctr": 0.0450,
        "lpv": 0.95,
        "reg": 0.055,
        "attend": 0.52,
        "mql": 0.72,
        "call": 0.60,
        "show": 0.76,
        "close": 0.13,
        "seg_mix": (0.45, 0.35, 0.20),
        "cpm_trend": 0.05,
        "ctr_trend": 0.02,
    },
    "Google Demand Gen": {
        "spend": 550,
        "cpm": 22.0,
        "ctr": 0.0110,
        "lpv": 0.91,
        "reg": 0.032,
        "attend": 0.42,
        "mql": 0.62,
        "call": 0.48,
        "show": 0.66,
        "close": 0.36,
        "seg_mix": (0.50, 0.32, 0.18),
        "cpm_trend": 0.12,
        "ctr_trend": -0.05,
    },
}

CREATIVES = {
    "Meta Prospecting": [
        ("META-BOOM-FOUNDER", "Boom Locations 2026 - Founder", "Founder video", "2026 Boom Locations", 0.34, 1.18),
        ("META-MORTGAGE-DATA", "Mortgage-Free in 7 Years - Data", "Data explainer", "Pay off mortgage in 7 years", 0.24, 1.05),
        ("META-RESULTS-TESTIMONIAL", "Member Results - Testimonial", "Member testimonial", "Member results", 0.24, 0.92),
        ("META-TAX-UGC", "Reduce Tax Legally - UGC", "UGC", "Reduce tax legally", 0.18, 0.82),
    ],
    "Meta Retargeting": [
        ("META-REPLAY", "Masterclass Replay - Warm Audience", "Webinar replay", "Masterclass replay", 0.60, 1.10),
        ("META-BOOM-FOUNDER", "Boom Locations 2026 - Founder", "Founder video", "2026 Boom Locations", 0.40, 1.00),
    ],
    "YouTube In-Stream": [
        ("YT-BOOM-VSL", "Boom Locations 2026 - VSL", "VSL", "2026 Boom Locations", 0.55, 1.12),
        ("YT-FOUNDER-CUT", "Founder Interview - Media Cut", "Founder interview", "Founder credibility", 0.45, 0.95),
    ],
    "Google Search": [
        ("SR-BRAND", "Freedom Property Investors - Brand", "Search text", "Brand", 0.30, 1.35),
        ("SR-ADVISOR", "Property Investment Advisor", "Search text", "Property investment advisor", 0.40, 1.00),
        ("SR-SUBURB", "High-Growth Suburb Intent", "Search text", "Suburb intent", 0.30, 0.85),
    ],
    "Google Demand Gen": [
        ("DG-BOOM-REPORT", "2026 Boom Locations Report", "Lead magnet", "2026 Boom Locations", 0.55, 1.10),
        ("DG-MASTERCLASS", "Free Masterclass Promo", "Masterclass promo", "Masterclass", 0.45, 0.95),
    ],
}

DOW_FACTOR = np.array([0.80, 1.05, 1.12, 1.10, 1.08, 0.95, 0.78])  # Mon..Sun


def _noise(rng: np.random.Generator, n: int, sigma: float = 0.10) -> np.ndarray:
    return np.clip(rng.lognormal(0.0, sigma, n), 0.65, 1.45)


def _segment_shares(rng: np.random.Generator, mix: tuple[float, float, float], n: int) -> np.ndarray:
    raw = np.array(mix)[None, :] * _noise(rng, n * 3, 0.08).reshape(n, 3)
    return raw / raw.sum(axis=1, keepdims=True)


def _build_fact(rng: np.random.Generator) -> pd.DataFrame:
    dates = [START + timedelta(days=i) for i in range(DAYS)]
    t = np.arange(DAYS) / DAYS
    dow = np.array([d.weekday() for d in dates])
    season = DOW_FACTOR[dow]
    growth = 1 + 0.18 * t

    rows = []
    for channel, p in CHANNEL_PARAMS.items():
        spend = p["spend"] * growth * season * _noise(rng, DAYS, 0.12)
        cpm = p["cpm"] * (1 + p["cpm_trend"] * t)
        ctr = p["ctr"] * (1 + p["ctr_trend"] * t)
        impressions = spend / cpm * 1000
        clicks = impressions * ctr * _noise(rng, DAYS, 0.08)
        sessions = clicks * p["lpv"] * _noise(rng, DAYS, 0.05)
        regs = sessions * p["reg"] * _noise(rng, DAYS, 0.10)
        attended = regs * p["attend"] * _noise(rng, DAYS, 0.09)
        mqls = attended * p["mql"] * _noise(rng, DAYS, 0.08)
        calls = mqls * p["call"] * _noise(rng, DAYS, 0.09)
        held = calls * p["show"] * _noise(rng, DAYS, 0.07)

        shares = _segment_shares(rng, p["seg_mix"], DAYS)
        for si, segment in enumerate(SEGMENTS):
            s = shares[:, si]
            rows.append(
                pd.DataFrame(
                    {
                        "date": dates,
                        "channel": channel,
                        "segment": segment,
                        "spend": spend * s,
                        "impressions": impressions * s,
                        "clicks": clicks * s,
                        "sessions": sessions * s,
                        "mc_regs": regs * s,
                        "mc_attended": attended * s,
                        "mqls": mqls * s,
                        "calls_booked": calls * s,
                        "calls_held": held * s,
                        "members": held * s * p["close"] * SEGMENT_CLOSE_MULT[segment],
                        "revenue": held
                        * s
                        * p["close"]
                        * SEGMENT_CLOSE_MULT[segment]
                        * SEGMENT_AOV[segment],
                    }
                )
            )

    fact = pd.concat(rows, ignore_index=True)
    return _finalise(fact)


def _finalise(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["week_start"] = df["date"] - pd.to_timedelta(df["date"].dt.weekday, unit="D")
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df


def _build_creative(fact: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for (channel, dt, segment), grp in fact.groupby(["channel", "date", "segment"]):
        specs = CREATIVES[channel]
        r = grp.iloc[0]
        n = len(specs)
        weights = np.array([s[4] for s in specs])
        spend_share = weights * _noise(rng, n, 0.06)
        spend_share /= spend_share.sum()
        eff = np.array([s[5] for s in specs])
        click_share = weights * eff * _noise(rng, n, 0.05)
        click_share /= click_share.sum()

        for i, (cid, name, fmt, angle, _w, _e) in enumerate(specs):
            rows.append(
                {
                    "date": dt,
                    "channel": channel,
                    "segment": segment,
                    "creative_id": cid,
                    "creative_name": name,
                    "format": fmt,
                    "angle": angle,
                    "spend": r["spend"] * spend_share[i],
                    "impressions": r["impressions"] * spend_share[i],
                    "clicks": r["clicks"] * click_share[i],
                    "sessions": r["sessions"] * click_share[i],
                    "mc_regs": r["mc_regs"] * click_share[i],
                    "mc_attended": r["mc_attended"] * click_share[i],
                    "mqls": r["mqls"] * click_share[i],
                    "calls_booked": r["calls_booked"] * click_share[i],
                    "calls_held": r["calls_held"] * click_share[i],
                    "members": r["members"] * click_share[i],
                    "revenue": r["revenue"] * click_share[i],
                }
            )
    return _finalise(pd.DataFrame(rows))


def _response_benchmark() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "response_bucket": ["Under 5 min", "5-30 min", "30-120 min", "2-24 hrs", "24+ hrs"],
            "leads": [1200, 2400, 2800, 4100, 3500],
            "members": [216, 288, 224, 164, 53],
        }
    ).assign(conversion_rate=lambda d: d.members / d.leads)


def _lag_by_segment() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "segment": list(SEGMENTS),
            "avg_days_to_member": [58, 36, 64],
            "median_days_to_member": [42, 28, 48],
            "p90_days_to_member": [120, 85, 130],
        }
    )


def load_data() -> dict[str, pd.DataFrame]:
    """Return the synthetic fact, creative, response and lag tables."""
    rng = np.random.default_rng(SEED)
    fact = _build_fact(rng)
    creative = _build_creative(fact, rng)
    return {
        "fact": fact,
        "creative": creative,
        "response": _response_benchmark(),
        "lag": _lag_by_segment(),
    }
