from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd
from rapidfuzz import fuzz
from scipy.stats import chisquare


def _col(df, candidates):
    return next((c for c in df.columns if any(x in c.lower() for x in candidates)), None)


def benford_test(series: pd.Series) -> dict[str, Any]:
    values = pd.to_numeric(series, errors="coerce").abs()
    digits = values[values > 0].astype(str).str.replace(".", "", regex=False).str.lstrip("0").str[0]
    observed = digits.value_counts().reindex(list("123456789"), fill_value=0).astype(float)
    expected = np.log10(1 + 1 / np.arange(1, 10)) * observed.sum()
    statistic, pvalue = chisquare(observed.values, expected) if observed.sum() else (0.0, 1.0)
    return {"observed": observed.to_dict(), "chi_square": float(statistic), "p_value": float(pvalue)}


def fraud_flags(df: pd.DataFrame, threshold: float | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    out = df.copy()
    out["fraud_flags"] = ""
    amount = _col(out, ("amount", "sum", "total", "payment"))
    vendor = _col(out, ("vendor", "supplier", "counterparty"))
    invoice = _col(out, ("invoice", "document"))
    date = _col(out, ("date", "sana", "created"))
    stats = benford_test(out[amount]) if amount else {"p_value": 1.0, "chi_square": 0.0, "observed": {}}
    if amount:
        amounts = pd.to_numeric(out[amount], errors="coerce")
        if threshold:
            mask = amounts.between(threshold * .98, threshold * .999)
            out.loc[mask, "fraud_flags"] = "structuring"
        if invoice and vendor:
            dup = out.duplicated([vendor, invoice, amount], keep=False)
            out.loc[dup, "fraud_flags"] = out.loc[dup, "fraud_flags"].replace("", "duplicate_payment")
            out.loc[dup & out["fraud_flags"].ne("duplicate_payment"), "fraud_flags"] += ";duplicate_payment"
    if date:
        dates = pd.to_datetime(out[date], errors="coerce")
        off_hours = dates.dt.hour.isin([23, 0, 1, 2, 3, 4]) | dates.dt.dayofweek.isin([5, 6])
        out.loc[off_hours, "fraud_flags"] = out.loc[off_hours, "fraud_flags"].replace("", "off_hours")
        out.loc[off_hours & out["fraud_flags"].ne("off_hours"), "fraud_flags"] += ";off_hours"
    if vendor:
        names = out[vendor].fillna("").astype(str).tolist()
        for i, name in enumerate(names):
            if not name:
                continue
            for j in range(i):
                if names[j] and 85 <= fuzz.ratio(name, names[j]) < 100:
                    out.loc[[i, j], "fraud_flags"] = out.loc[[i, j], "fraud_flags"].map(lambda x: f"{x};fuzzy_vendor".strip(";"))
    return out, stats
