from __future__ import annotations

import pandas as pd
import streamlit as st

from core.ingestion import load_csv, load_workbook_data
from core.rules_hygiene import hygiene_flags
from core.rules_accounting import accounting_flags
from core.rules_fraud import fraud_flags
from core.scoring import score_dataframe
from reports.excel_exporter import export_excel
from reports.pdf_exporter import export_pdf

st.set_page_config(page_title="Audit Sentinel", layout="wide")
st.title("Audit Sentinel")
st.caption("CAATs financial anomaly screening for internal audit teams")
upload = st.file_uploader("Upload Excel or CSV", type=["xlsx", "xlsm", "csv"])
threshold = st.number_input("Authorization threshold (optional)", min_value=0.0, value=0.0)
if upload:
    try:
        ingested = load_csv(upload) if upload.name.lower().endswith(".csv") else load_workbook_data(upload)
        data = hygiene_flags(ingested.frame)
        data = accounting_flags(data)
        data, benford = fraud_flags(data, threshold or None)
        result = score_dataframe(data, benford["p_value"])
        high = result[result["risk_score"] >= 70]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Records audited", len(result)); c2.metric("High-risk anomalies", len(high))
        amount_col = next((c for c in result.columns if "amount" in c.lower() or "payment" in c.lower()), None)
        c3.metric("High-risk exposure", f"{pd.to_numeric(high[amount_col], errors='coerce').sum():,.2f}" if amount_col else "N/A")
        c4.metric("Benford p-value", f"{benford['p_value']:.6f}")
        st.dataframe(result, use_container_width=True)
        st.download_button("Download Excel audit report", export_excel(result), "audit_results.xlsx")
        exposure = pd.to_numeric(high[amount_col], errors="coerce").sum() if amount_col else 0
        st.download_button("Download executive PDF", export_pdf(len(result), len(high), exposure, benford["p_value"]), "executive_summary.pdf")
    except Exception as exc:
        st.error(f"Unable to process file safely: {exc}")
else:
    st.info("Upload a financial workbook to begin screening.")
