from __future__ import annotations

import re
from typing import Any

import pandas as pd

ERROR_TOKENS = ("#REF!", "#VALUE!", "#DIV/0!", "#N/A", "#NAME?", "#NUM!")


def hygiene_flags(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["hygiene_flags"] = ""
    for col in out.columns:
        if col == "hygiene_flags":
            continue
        mask = out[col].astype(str).str.contains("|".join(map(re.escape, ERROR_TOKENS)), case=False, na=False)
        out.loc[mask, "hygiene_flags"] = out.loc[mask, "hygiene_flags"].map(lambda x: f"{x};broken_formula".strip(";"))
    date_names = [c for c in out.columns if any(x in c.lower() for x in ("date", "sana"))]
    for col in date_names:
        parsed = pd.to_datetime(out[col], errors="coerce", dayfirst=True)
        invalid = out[col].notna() & parsed.isna()
        out.loc[invalid, "hygiene_flags"] = out.loc[invalid, "hygiene_flags"].map(lambda x: f"{x};invalid_date".strip(";"))
        out[col] = parsed.dt.strftime("%Y-%m-%d").where(parsed.notna(), out[col])
    for col in out.columns:
        if col.endswith("_flags"):
            continue
        if out[col].dtype == "object":
            numeric = out[col].astype(str).str.replace(",", ".", regex=False).str.replace(" ", "", regex=False)
            converted = pd.to_numeric(numeric, errors="coerce")
            text_numbers = converted.notna() & out[col].notna()
            if text_numbers.any():
                out.loc[text_numbers, "hygiene_flags"] = out.loc[text_numbers, "hygiene_flags"].map(lambda x: f"{x};text_number".strip(";"))
    return out
