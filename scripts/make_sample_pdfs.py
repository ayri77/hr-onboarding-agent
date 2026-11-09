"""Erzeugt aus docs/*.md die fiktiven Beispiel-PDFs (docs/*.pdf).

Nur für die Demo: die echten Onboarding-PDFs werden einfach in docs/ gelegt,
dieses Skript wird dann nicht mehr gebraucht.

    python scripts/make_sample_pdfs.py
"""
from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer

DOCS = Path(__file__).resolve().parent.parent / "docs"


def md_to_flowables(text: str) -> list:
    styles = getSampleStyleSheet()
    out: list = []
    bullets: list[str] = []

    def flush_bullets() -> None:
        if bullets:
            out.append(ListFlowable([ListItem(Paragraph(b, styles["Normal"])) for b in bullets], bulletType="bullet"))
            out.append(Spacer(1, 0.3 * cm))
            bullets.clear()

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            flush_bullets()
            continue
        if line.startswith("# "):
            out.append(Paragraph(line[2:], styles["Title"]))
        elif line.startswith("## "):
            flush_bullets()
            out.append(Spacer(1, 0.3 * cm))
            out.append(Paragraph(line[3:], styles["Heading2"]))
        elif line.startswith("- "):
            bullets.append(line[2:])
        else:
            # *kursiv* -> <i>kursiv</i>
            line = re.sub(r"\*(.+?)\*", r"<i>\1</i>", line)
            out.append(Paragraph(line, styles["Normal"]))
            out.append(Spacer(1, 0.2 * cm))
    flush_bullets()
    return out


def main() -> None:
    for md in sorted(DOCS.glob("*.md")):
        pdf = md.with_suffix(".pdf")
        doc = SimpleDocTemplate(str(pdf), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                                topMargin=2 * cm, bottomMargin=2 * cm, title=md.stem)
        doc.build(md_to_flowables(md.read_text(encoding="utf-8")))
        print(f"{pdf.name}: {pdf.stat().st_size} Bytes")


if __name__ == "__main__":
    main()
