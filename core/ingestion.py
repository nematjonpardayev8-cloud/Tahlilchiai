from __future__ import annotations

from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd
from openpyxl import load_workbook


@dataclass
class IngestionResult:
    frame: pd.DataFrame
    formula_cells: set[str] = field(default_factory=set)
    formula_overwrites: list[dict[str, Any]] = field(default_factory=list)
    source_name: str = "workbook"


def _source_path(source: Any) -> str | BytesIO:
    if isinstance(source, (str, Path)):
        return str(source)
    if hasattr(source, "seek"):
        source.seek(0)
    return source


def load_workbook_data(source: Any, sheet_name: str | None = None) -> IngestionResult:
    """Read the first (or selected) sheet while retaining formula/value evidence."""
    path = _source_path(source)
    raw = load_workbook(path, data_only=False, read_only=False)
    if hasattr(source, "seek"):
        source.seek(0)
    values = load_workbook(_source_path(source), data_only=True, read_only=False)
    selected = sheet_name or raw.sheetnames[0]
    raw_ws, value_ws = raw[selected], values[selected]
    rows = list(value_ws.values)
    if not rows:
        return IngestionResult(pd.DataFrame(), source_name=selected)
    headers = [str(x).strip() if x is not None else f"column_{i}" for i, x in enumerate(rows[0])]
    frame = pd.DataFrame(rows[1:], columns=headers)
    formulas, overwrites = set(), []
    for row in raw_ws.iter_rows():
        for cell in row:
            if isinstance(cell.value, str) and cell.value.startswith("="):
                formulas.add(cell.coordinate)
                value_cell = value_ws[cell.coordinate]
                if isinstance(value_cell.value, (int, float)) and not isinstance(cell.value, str):
                    overwrites.append({"cell": cell.coordinate, "formula": cell.value, "value": value_cell.value})
    # A formula cell with no cached result is still useful evidence, but not an overwrite.
    return IngestionResult(frame, formulas, overwrites, selected)


def load_csv(source: Any) -> IngestionResult:
    return IngestionResult(pd.read_csv(source), source_name=getattr(source, "name", "csv"))
