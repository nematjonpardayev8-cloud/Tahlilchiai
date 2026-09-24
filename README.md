# Audit Sentinel

Audit Sentinel is a Python 3.11+ Streamlit CAATs screening application for Excel and CSV financial records. It is designed to identify indicators requiring auditor investigation, not to make final fraud determinations.

## Run

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Upload `.xlsx`, `.xlsm`, or `.csv` files. The dashboard runs hygiene checks, accounting checks, Benford analysis, duplicate and threshold screening, fuzzy vendor comparison, off-hours screening, risk scoring, and Excel/PDF exports.

## Expected columns

Column names are detected heuristically. Useful names include `Vendor`, `Vendor ID`, `Invoice Number`, `Amount`, `Debit`, `Credit`, and date fields containing `date`, `created`, or `sana`.

## Important limitations

Excel formula cached values depend on the workbook application that last saved the file. The application treats screening results as audit leads. Thresholds, holidays, chart-of-accounts rules, authorization limits, and operating hours should be configured to the institution's policy before production deployment.
