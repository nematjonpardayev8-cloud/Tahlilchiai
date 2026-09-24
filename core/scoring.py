from __future__ import annotations

import pandas as pd

WEIGHTS = {"hardcoded_formula_overwrite": 35, "duplicate_payment": 35, "benford_outlier": 35, "negative_balance": 25, "structuring": 25, "off_hours": 15, "fuzzy_vendor": 15, "invalid_date": 5, "text_number": 5}


def score_dataframe(df: pd.DataFrame, benford_p: float = 1.0) -> pd.DataFrame:
    out = df.copy()
    flag_columns = [c for c in ("hygiene_flags", "accounting_flags", "fraud_flags") if c in out]
    def flags(row):
        return ";".join(str(row[c]) for c in flag_columns if str(row[c]) not in ("", "nan"))
    out["audit_flags"] = out.apply(flags, axis=1)
    if benford_p < 0.05 and len(out):
        out["audit_flags"] = out["audit_flags"].map(lambda x: f"{x};benford_outlier".strip(";"))
    out["risk_score"] = out["audit_flags"].map(lambda s: min(100, sum(w for f, w in WEIGHTS.items() if f in s)))
    out["risk_tier"] = pd.cut(out["risk_score"], [-1, 29, 69, 100], labels=["Low", "Medium", "High / Critical"])
    return out
