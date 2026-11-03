"""Export the KPI dictionary and action plan to Markdown and CSV.

Usage:  .venv/bin/python export_docs.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from content import (
    ACTION_PLAN,
    ASSUMPTIONS,
    KPI_DICTIONARY,
    RECOMMENDED_SPLIT,
    ROADMAP,
    STRATEGIC_BETS,
)

ROOT = Path(__file__).parent
EXPORTS = ROOT / "exports"
EXPORTS.mkdir(exist_ok=True)


def md_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for row in df.itertuples(index=False):
        cells = []
        for value in row:
            text = "" if pd.isna(value) else str(value)
            text = text.replace("|", "\\|").replace("\n", " ")
            cells.append(text)
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def build_kpi_doc() -> str:
    dd = pd.DataFrame(KPI_DICTIONARY)
    dd.to_csv(EXPORTS / "fpi_kpi_dictionary.csv", index=False)
    return f"""# KPI Data Dictionary

This dictionary defines the metrics used in the sample marketing dashboard for
Freedom Property Investors. It exists to make one thing explicit: **every KPI has
a job, a formula, an owner and a guardrail.** A metric without those four things
is trivia.

## Measurement framework

The dashboard is deliberately layered.

1. **Business outcomes** - spend, revenue, CAC, MER, LTV:CAC and payback. These
   decide whether growth is economically viable.
2. **Funnel diagnostics** - CPM, CTR, landing-page rate, CPL, attendance, MQL,
   call and show rates. These explain *why* an outcome moved.
3. **Measurement integrity** - offline match rate, incremental ROAS, lead quality
   score and pacing. These keep the first two layers honest.

## The dictionary

{md_table(dd)}

## How to use it

- Review **business outcomes** monthly with finance and the Head of Growth.
- Review **funnel diagnostics** weekly with channel owners, sales operations and
  lifecycle marketing.
- Treat **measurement integrity** as a release gate: if offline match rate or
  incrementality is not credible, do not move budget on last-click ROAS.
- When a metric has no owner, it will not be maintained. Assign one before
  productionising the dashboard.

## Assumptions

""" + "\n".join(f"- **{title}.** {body}" for title, body in ASSUMPTIONS) + "\n"


def build_action_doc() -> str:
    ap = pd.DataFrame(ACTION_PLAN)
    ap.to_csv(EXPORTS / "fpi_action_plan.csv", index=False)
    rec = RECOMMENDED_SPLIT.copy()
    findings = """## Findings this plan responds to

1. **Measurement gap.** Media is optimised on form fills, not members. There is
   no closed loop between HubSpot outcomes and the ad platforms.
2. **Mid-funnel leak.** Masterclass attendance and speed-to-lead are the largest
   controllable losses. Both are cheaper to fix than buying more traffic.
3. **Misallocated budget.** Search has the lowest CAC and retargeting returns
   roughly 1.8x Meta prospecting's ROAS, yet both are under-funded relative
   to prospecting and YouTube.
4. **Creative fatigue.** Meta CPM is rising while CTR falls. Founder-led and data
   angles outperform testimonial and UGC in the sample.
5. **Trust gaps on site.** Live Lorem Ipsum and inconsistent review counts add
   friction to every paid click.
"""
    roadmap = "\n".join(
        f"### {phase}\n" + "\n".join(f"- {item}" for item in items) + "\n"
        for phase, items in ROADMAP.items()
    )
    bets = "\n".join(f"- **{title}.** {body}" for title, body in STRATEGIC_BETS)
    assumptions = "\n".join(f"- **{title}.** {body}" for title, body in ASSUMPTIONS)
    return f"""# Sample Marketing Action Plan

A prioritised, owner-assigned plan built from the sample dashboard findings for
Freedom Property Investors. P0 items unlock measurement and trust. P1 items move
efficiency. P2 items build durable advantage.

> All data is synthetic. Validate the findings with live CRM and ad-platform data
> before committing budget.

{findings}

## Prioritised actions

{md_table(ap)}

## Recommended budget split

{md_table(rec)}

## 90-day roadmap

{roadmap}

## Success measures

| Measure | Target | Expected movement |
|---|---|---|
| Blended CAC | <= $2,200 | -8% to -12% |
| Masterclass attendance | >= 55% | +8 to +12 points |
| Lead to member | >= 3.0% | +20% |
| Offline conversion match rate | >= 80% | Measurement gate |
| LTV:CAC | >= 4:1 | Unit-economics guardrail |

## Strategic bets

{bets}

## Assumptions and caveats

{assumptions}
"""


if __name__ == "__main__":
    (ROOT / "KPI_DICTIONARY.md").write_text(build_kpi_doc(), encoding="utf-8")
    (ROOT / "ACTION_PLAN.md").write_text(build_action_doc(), encoding="utf-8")
    print("Wrote KPI_DICTIONARY.md, ACTION_PLAN.md and exports/")
