from __future__ import annotations

import pandas as pd


def _find(df, names):
    return next((c for c in df.columns if c.lower() in names or any(n in c.lower() for n in names)), None)


def accounting_flags(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["accounting_flags"] = ""
    amount = _find(out, {"amount", "sum", "debit", "credit", "balance", "amount_usd"})
    if amount:
        values = pd.to_numeric(out[amount], errors="coerce")
        out.loc[values < 0, "accounting_flags"] = "negative_balance"
    debit, credit = _find(out, {"debit", "debits"}), _find(out, {"credit", "credits"})
    if debit and credit:
        mismatch = pd.to_numeric(out[debit], errors="coerce").fillna(0).sub(pd.to_numeric(out[credit], errors="coerce").fillna(0)).abs() > 0.005
        out.loc[mismatch, "accounting_flags"] = out.loc[mismatch, "accounting_flags"].replace("", "trial_balance_mismatch")
        out.loc[mismatch & out["accounting_flags"].ne("trial_balance_mismatch"), "accounting_flags"] += ";trial_balance_mismatch"
    return out
