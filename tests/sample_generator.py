"""Generate a deliberately dirty sample workbook for manual testing."""
from pathlib import Path
import pandas as pd


def generate(path: str = "sample_dirty.xlsx"):
    df = pd.DataFrame({"Vendor ID": ["V1", "V1", "V2"], "Vendor": ["Apex Logistics LLC", "Apex-Logistics LTD", "Office Co"], "Invoice Number": ["INV-1", "INV-1", "INV-2"], "Amount": [9800, 9800, -25], "Payment Date": ["2026-09-19 23:30", "2026-09-19 23:35", "bad-date"], "Debit": [9800, 9800, 0], "Credit": [0, 0, 25]})
    df.to_excel(Path(path), index=False)

if __name__ == "__main__": generate()
