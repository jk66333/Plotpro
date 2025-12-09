"""
generate_commission_pdf.py
Stable PDF generator for receipts. Safe text sanitization and currency formatting.
"""

import os
import re
import logging
from datetime import datetime
from fpdf import FPDF  # pip install fpdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _sanitize_text(s: str) -> str:
    """Sanitize text for PDF output: remove control characters, collapse whitespace."""
    if s is None:
        return ""
    s = str(s)
    s = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", s)
    s = re.sub(r"\r\n?", "\n", s)
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()


def _format_currency(value) -> str:
    try:
        return f"₹{float(value):,.2f}"
    except Exception:
        return str(value)


class ReceiptPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 8, "Receipt / Commission", ln=True, align="C")
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", 0, 0, "C")


def generate_commission_pdf(receipt: dict, out_dir: str = ".", filename: str = None) -> str:
    """
    Generate a PDF file for `receipt` dict and save to disk.
    Returns absolute path to the saved PDF.
    """
    try:
        os.makedirs(out_dir, exist_ok=True)

        if not filename:
            safe_name = _sanitize_text(receipt.get("client_name", "receipt")).replace(" ", "_")[:40]
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            # include receipt id if available for easier lookup
            rid = receipt.get("id") or receipt.get("receipt_id") or ""
            filename = f"{safe_name}_{rid}_{timestamp}.pdf" if rid else f"{safe_name}_{timestamp}.pdf"

        out_path = os.path.join(out_dir, filename)

        pdf = ReceiptPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=11)

        # Title
        title = _sanitize_text(receipt.get("title", "Commission / Receipt"))
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, title, ln=True)
        pdf.ln(2)

        # Selected fields with formatting
        fields = [
            ("Client Name", "client_name"),
            ("Plot No.", "plot_no"),
            ("Basic Price (per Sq.Yard)", "basic_price"),
            ("Sq.Yards", "sq_yards"),
            ("Sale Amount", "sale_amount"),
            ("Commission %", "commission_percent"),
            ("Fixed Fee", "fixed_fee"),
            ("Computed Commission", "computed_commission"),
            ("Notes", "notes"),
        ]

        pdf.set_font("Arial", size=10)
        for label, key in fields:
            if key not in receipt:
                continue
            val = receipt.get(key)
            if key in ("basic_price", "sale_amount", "computed_commission", "fixed_fee"):
                display = _format_currency(val)
            else:
                display = _sanitize_text(val)
            pdf.cell(55, 7, f"{label}:", 0, 0)
            pdf.multi_cell(0, 7, str(display))

        pdf.ln(4)

        terms = receipt.get("terms")
        if terms:
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 7, "Terms & Notes:", ln=True)
            pdf.set_font("Arial", size=9)
            safe_terms = _sanitize_text(terms)
            pdf.multi_cell(0, 6, safe_terms)

        pdf.output(out_path)
        logger.info("PDF generated: %s", out_path)
        return os.path.abspath(out_path)

    except Exception as exc:
        logger.exception("Error generating PDF: %s", exc)
        raise
