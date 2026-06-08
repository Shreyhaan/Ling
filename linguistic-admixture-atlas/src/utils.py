"""Shared utilities for the Contact-Admixture Atlas first data audit.

The first sprint keeps dependencies minimal so the raw-data audit can run in a
fresh environment before the analysis stack is installed.  Notebook work can use
pandas/matplotlib, but the command-line builders use only the Python standard
library.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Iterable

SOUTH_ASIA_BOUNDS = {
    "min_lat": 5.0,
    "max_lat": 38.0,
    "min_lon": 60.0,
    "max_lon": 105.0,
}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read a CSV file as a list of dictionaries."""
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv_rows(path: Path, rows: Iterable[dict[str, object]], fieldnames: list[str]) -> None:
    """Write dictionaries to CSV, creating the parent directory if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def first_existing_path(paths: Iterable[Path]) -> Path:
    """Return the first existing path from a list of candidates."""
    for path in paths:
        if path.exists():
            return path
    formatted = "\n".join(f"  - {path}" for path in paths)
    raise FileNotFoundError(f"None of the expected paths exists:\n{formatted}")


def optional_column(columns: Iterable[str], candidates: Iterable[str]) -> str | None:
    """Return the first matching column name if present, otherwise None."""
    columns_list = list(columns)
    lower_to_original = {column.lower(): column for column in columns_list}
    for candidate in candidates:
        match = lower_to_original.get(candidate.lower())
        if match is not None:
            return match
    return None


def field_value(row: dict[str, str], column: str | None, fallback: str = "") -> str:
    """Read and strip an optional CSV field, falling back for missing/blank values."""
    if column is None:
        return fallback
    value = row.get(column, "").strip()
    return value if value else fallback


def pick_column(columns: Iterable[str], candidates: Iterable[str], *, label: str) -> str:
    """Pick the first matching column name, case-insensitively."""
    columns_list = list(columns)
    lower_to_original = {column.lower(): column for column in columns_list}
    for candidate in candidates:
        match = lower_to_original.get(candidate.lower())
        if match is not None:
            return match
    raise KeyError(
        f"Could not find a {label} column. Tried {list(candidates)}; "
        f"available columns are {columns_list}."
    )


def parse_float(value: str) -> float | None:
    """Parse a floating-point value, returning None for blanks and invalid data."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        parsed = float(text)
    except ValueError:
        return None
    if math.isnan(parsed):
        return None
    return parsed


def in_south_asia_box(latitude: float | None, longitude: float | None) -> bool:
    """Return True if a coordinate falls in the first-pass South/Central Asia box."""
    if latitude is None or longitude is None:
        return False
    return (
        SOUTH_ASIA_BOUNDS["min_lat"] <= latitude <= SOUTH_ASIA_BOUNDS["max_lat"]
        and SOUTH_ASIA_BOUNDS["min_lon"] <= longitude <= SOUTH_ASIA_BOUNDS["max_lon"]
    )


def truthy_csv(value: object) -> str:
    """Normalize booleans for stable CSV output."""
    return "true" if bool(value) else "false"
