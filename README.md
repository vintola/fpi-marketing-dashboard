# Freedom Property Investors - Marketing Analytics Sample

A Streamlit dashboard and consulting pack built from the public positioning of
[freedompropertyinvestors.com.au](https://freedompropertyinvestors.com.au/):
a masterclass-led, high-ticket property investment advisory.

The pack contains:

- **KPI dashboard** covering unit economics, funnel diagnostics, paid media,
  lead quality and creative performance.
- **Data dictionary** that explains every KPI: definition, formula, purpose,
  source/owner and guardrail.
- **Action plan** with findings, prioritised actions, owners, timelines and a
  90-day roadmap.
- **Strategy paper (PDF)** covering the company, conversion system, marketing
  challenges, North Star and measurement plan:
  `Freedom_Property_Investors_Marketing_Analysis.pdf`.

> **All data is synthetic.** It is calibrated to the business model for
> demonstration and is not actual Freedom Property Investors performance data.
> See `content.ASSUMPTIONS` or the Assumptions section below.
>
> **Independent sample.** Not affiliated with, commissioned by, or endorsed by
> Freedom Property Investors. It was built from publicly available positioning
> for portfolio demonstration only.

## Screens

| Page | What it answers |
|---|---|
| Executive summary | Are we acquiring members profitably, and what changed? |
| KPI dashboard | Which funnel stage explains the result, and how do segments differ? |
| Paid media | Where should the next dollar go? Includes a reallocation scenario. |
| Lead quality | Which leads convert, how long do they take, and what is speed-to-lead worth? |
| Creative analytics | Which angles, formats and ads create members efficiently? |
| Data dictionary | Why does each KPI exist and how is it calculated? |
| Action plan | What do we do next, who owns it, and how will we know it worked? |

## Quickstart

Requires Python 3.13 (Streamlit does not yet support 3.14 reliably).

```bash
cd ~/Projects/fpi-marketing-dashboard
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/streamlit run app.py
```

Then open http://localhost:8501.

With pip instead of uv:

```bash
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py
```

## App launcher

This is a local **Streamlit** app (Python, Streamlit 1.66.1), not a deployment on
Streamlit Community Cloud.

A desktop launcher is installed as **FPI Marketing Dashboard** in the application
menu:

`~/.local/share/applications/fpi-marketing-dashboard.desktop`

It starts the server at http://127.0.0.1:8765 (port 8501 is already used by another
local app), waits for it to become healthy, then opens your browser. Logs are written
to `.streamlit.log`.

Use it from a terminal as well:

```bash
./launch-dashboard.sh          # start and open the browser
./launch-dashboard.sh stop     # stop the background server
```

Override the default port with `FPI_DASHBOARD_PORT=9000 ./launch-dashboard.sh`.
If you move the project, update the absolute paths in the `.desktop` file.

## Project structure

```
fpi-marketing-dashboard/
├── app.py                  # Streamlit application
├── data.py                 # Synthetic data generator (replace with live data)
├── content.py              # KPI dictionary, action plan, assumptions
├── export_docs.py          # Regenerates Markdown and CSV exports
├── launch-dashboard.sh     # Launcher used by the app-menu entry
├── assets/                 # Launcher icon
├── requirements.txt
├── KPI_DICTIONARY.md       # Standalone data dictionary
├── ACTION_PLAN.md          # Standalone action plan
├── Freedom_Property_Investors_Marketing_Analysis.pdf
├── report/                 # PDF source (HTML) and renderer
├── exports/                # CSV versions for sharing
└── .streamlit/config.toml  # Theme
```

## Sample data model

The fact table is daily, by channel and investor segment:

`date, channel, segment, spend, impressions, clicks, sessions, mc_regs,
mc_attended, mqls, calls_booked, calls_held, members, revenue`

The creative table adds `creative_id, creative_name, format, angle`. Two small
reference tables cover speed-to-lead conversion and segment conversion lag.

Channels modelled: Meta Prospecting, Meta Retargeting, YouTube In-Stream,
Google Search and Google Demand Gen.

Segments modelled: First-time investor, Experienced investor, Retiree.

## Connecting real data

Replace `load_data()` in `data.py` with a loader that returns the same dictionary:

```python
{
    "fact": <daily fact DataFrame>,
    "creative": <creative-level DataFrame>,
    "response": <speed-to-lead DataFrame>,
    "lag": <segment lag DataFrame>,
}
```

Recommended sources:

- **Meta Marketing API** and **Google Ads API** for spend, impressions, clicks
  and creative metadata.
- **GA4** for sessions and landing-page behaviour.
- **HubSpot** for masterclass registrations, attendance, MQLs, calls, members
  and revenue. Treat HubSpot as the source of truth for outcomes.
- Upload member events back to Meta (CAPI) and Google (enhanced conversions)
  so the platforms optimise on members rather than form fills.

Before trusting the dashboard on live data, confirm:

1. Spend reconciles to finance within 3%.
2. Member counts reconcile to CRM within 3%.
3. Offline conversion match rate is at least 80%.
4. Attribution windows cover the p90 conversion lag.

## Why these KPIs

The dictionary is built in three layers:

1. **Business outcomes** - spend, revenue, blended CAC, MER, LTV:CAC and payback.
   These decide whether the growth engine is viable.
2. **Funnel diagnostics** - CPM, CTR, landing-page rate, CPL, attendance, MQL,
   call and show rates. These explain why an outcome moved and where to act.
3. **Measurement integrity** - offline match rate, incremental ROAS, lead quality
   score and pacing. These stop the first two layers from lying.

Open the **Data dictionary** tab, or `KPI_DICTIONARY.md`, for the full rationale,
formula, data source, owner and target for all 33 KPIs.

## Action plan summary

The sample plan prioritises:

- **P0:** closed-loop measurement (CAPI, enhanced conversions, HubSpot offline
  events), removal of live placeholder copy and inconsistent proof, and a
  masterclass reminder/replay sequence.
- **P1:** rebalance toward Search and Retargeting, a five-minute speed-to-lead
  SLA, a founder/data creative sprint, predictive lead scoring and
  segment-specific nurture.
- **P2:** incrementality testing, defensible YouTube measurement, referral and
  review engine, SEO/content hub, partnerships and dashboard productionisation.

See `ACTION_PLAN.md` or the in-app Action plan tab for owners, timelines,
expected impact and the 90-day roadmap.

## Assumptions

- **Synthetic data:** every number is generated for demonstration.
- **Membership value:** First-time $7,800; Experienced $12,000; Retiree $9,500.
  Blended about $9,600 in year one.
- **LTV:** 2.2x first-year revenue over three years. Replace with observed cohort
  LTV before using LTV:CAC for real budget decisions.
- **Attribution:** members attributed to the paid channel of first touch. Real
  decisions should triangulate last click, first touch and incrementality tests.
- **Currency/period:** AUD, 27 April to 25 October 2026.

## Regenerating the documents

```bash
.venv/bin/python export_docs.py
```

This rewrites `KPI_DICTIONARY.md`, `ACTION_PLAN.md` and the CSV files in
`exports/` from `content.py`.
