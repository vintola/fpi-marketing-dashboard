"""Render the marketing analysis report to PDF.

Usage:  .venv/bin/python report/render_report.py
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "report.html"
RAW = ROOT / "report_raw.pdf"
OUT = ROOT.parent / "Freedom_Property_Investors_Marketing_Analysis.pdf"

subprocess.run(
    [
        "chromium",
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={RAW}",
        HTML.as_uri(),
    ],
    check=True,
    capture_output=True,
)

doc = pymupdf.open(RAW)
total = doc.page_count

for index, page in enumerate(doc, start=1):
    width = page.rect.width
    height = page.rect.height
    page.insert_textbox(
        pymupdf.Rect(width - 95, height - 28, width - 38, height - 12),
        f"{index:02d} / {total:02d}",
        fontsize=7,
        fontname="helv",
        color=(0.54, 0.60, 0.66),
        align=2,
    )

doc.set_metadata(
    {
        "title": "From attention to membership: Freedom Property Investors marketing analysis",
        "author": "Independent paid media & marketing analytics",
        "subject": "Marketing, conversion and North Star analysis",
        "keywords": "paid media, marketing analytics, conversion, CAC, LTV, North Star, property investment",
        "creator": "Chromium / PyMuPDF",
    }
)
doc.save(OUT, garbage=4, deflate=True)
doc.close()

print(f"Wrote {OUT} ({total} pages)")
