from __future__ import annotations

from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def export_pdf(total: int, high_risk: int, exposure: float, p_value: float) -> bytes:
    stream = BytesIO(); pdf = canvas.Canvas(stream, pagesize=letter)
    pdf.setTitle("Audit Sentinel Executive Summary")
    pdf.setFont("Helvetica-Bold", 18); pdf.drawString(50, 740, "Audit Sentinel - Executive Summary")
    pdf.setFont("Helvetica", 11)
    lines = [f"Records audited: {total}", f"High-risk anomalies: {high_risk}", f"High-risk financial exposure: {exposure:,.2f}", f"Benford chi-square p-value: {p_value:.6f}"]
    for i, line in enumerate(lines): pdf.drawString(60, 690 - i * 28, line)
    pdf.drawString(60, 540, "This report is an analytical screening aid and requires auditor validation.")
    pdf.save(); return stream.getvalue()
