"""Build the first South/Central Asian language feasibility table.

This first milestone answers a deliberately simple question: which Glottolog
coordinate-bearing South/Central Asian languages also appear in Grambank and/or
PHOIBLE?  The script intentionally stops before modeling; it only harmonizes
Glottocodes, filters the pilot region, and prints overlap counts.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

from utils import (
    field_value,
    first_existing_path,
    in_south_asia_box,
    parse_float,
    optional_column,
    pick_column,
    read_csv_rows,
    truthy_csv,
    write_csv_rows,
)

ROOT = Path(__file__).resolve().parents[1]
GLOTTOLOG_DIR = ROOT / "data_raw" / "glottolog"
GRAMBANK_DIR = ROOT / "data_raw" / "grambank"
PHOIBLE_DIR = ROOT / "data_raw" / "phoible"
OUT_DIR = ROOT / "data_processed"
OUT_PATH = OUT_DIR / "languages_master.csv"

MASTER_COLUMNS = [
    "glottocode",
    "name",
    "level",
    "macroarea",
    "isocodes",
    "family",
    "classification",
    "latitude",
    "longitude",
    "in_grambank",
    "in_phoible",
]


def read_glottolog_geo() -> tuple[list[dict[str, str]], dict[str, str]]:
    """Read Glottolog's coordinate table and return rows plus detected columns."""
    path = GLOTTOLOG_DIR / "languages_and_dialects_geo.csv"
    rows = read_csv_rows(path)
    if not rows:
        raise ValueError(f"No rows found in {path}.")
    columns = rows[0].keys()
    detected = {
        "glottocode": pick_column(columns, ["glottocode", "Glottocode", "id", "ID"], label="Glottocode"),
        "name": pick_column(columns, ["name", "Name", "language", "Language"], label="name"),
        "latitude": pick_column(columns, ["latitude", "Latitude", "lat", "Lat"], label="latitude"),
        "longitude": pick_column(columns, ["longitude", "Longitude", "lon", "Lon", "lng"], label="longitude"),
        "level": optional_column(columns, ["level", "Level", "languoid_level", "Languoid_Level"]),
        "macroarea": optional_column(columns, ["macroarea", "Macroarea", "macro_area", "Macro_Area"]),
        "isocodes": optional_column(columns, ["isocodes", "Isocodes", "iso639P3code", "ISO639P3code", "iso_code"]),
    }
    print("Glottolog geo columns:")
    print(list(columns))
    return rows, detected


def read_glottolog_languoid_metadata() -> dict[str, dict[str, str]]:
    """Read optional Glottolog languoid metadata for family/classification labels."""
    path = GLOTTOLOG_DIR / "glottolog_languoid.csv.zip"
    if not path.exists():
        print("Glottolog languoid metadata not found; family/classification will be blank.")
        return {}

    with zipfile.ZipFile(path) as archive:
        csv_names = [name for name in archive.namelist() if name.endswith(".csv")]
        if not csv_names:
            raise ValueError(f"No CSV file found inside {path}.")
        with archive.open(csv_names[0]) as handle:
            text = handle.read().decode("utf-8-sig").splitlines()

    import csv

    rows = list(csv.DictReader(text))
    if not rows:
        return {}
    columns = rows[0].keys()
    code_col = pick_column(columns, ["id", "glottocode", "Glottocode", "ID"], label="languoid Glottocode")
    family_col = optional_column(columns, ["family", "Family", "top_level", "Top_Level"])
    classification_col = optional_column(columns, ["classification", "Classification", "lineage", "Lineage"])
    name_col = optional_column(columns, ["name", "Name"])
    level_col = optional_column(columns, ["level", "Level", "languoid_level", "Languoid_Level"])
    macroarea_col = optional_column(columns, ["macroarea", "Macroarea", "macro_area", "Macro_Area"])
    isocodes_col = optional_column(columns, ["isocodes", "Isocodes", "iso639P3code", "ISO639P3code", "iso_code"])

    print("Glottolog languoid columns:")
    print(list(columns))

    metadata = {}
    for row in rows:
        code = row.get(code_col, "").strip()
        if not code:
            continue
        metadata[code] = {
            "family": row.get(family_col, "").strip() if family_col else "",
            "classification": row.get(classification_col, "").strip() if classification_col else "",
            "languoid_name": row.get(name_col, "").strip() if name_col else "",
            "level": row.get(level_col, "").strip() if level_col else "",
            "macroarea": row.get(macroarea_col, "").strip() if macroarea_col else "",
            "isocodes": row.get(isocodes_col, "").strip() if isocodes_col else "",
        }
    return metadata


def find_language_glottocodes(dataset_dir: Path, dataset_name: str) -> set[str]:
    """Read a CLDF language table and return all populated Glottocodes."""
    path = first_existing_path(
        [
            dataset_dir / "cldf" / "languages.csv",
            dataset_dir / "cldf" / "LanguageTable.csv",
            dataset_dir / "languages.csv",
            dataset_dir / "LanguageTable.csv",
        ]
    )
    rows = read_csv_rows(path)
    if not rows:
        return set()
    columns = rows[0].keys()
    print(f"Using {dataset_name} language table: {path}")
    print(list(columns))
    code_col = pick_column(
        columns,
        ["Glottocode", "glottocode", "Glottolog_ID", "glottolog_id", "GlottologId", "cldf_glottocode"],
        label=f"{dataset_name} Glottocode",
    )
    return {row.get(code_col, "").strip() for row in rows if row.get(code_col, "").strip()}


def build_master() -> list[dict[str, object]]:
    """Construct the filtered master table as dictionaries."""
    geo_rows, geo_columns = read_glottolog_geo()
    languoid_metadata = read_glottolog_languoid_metadata()
    grambank_codes = find_language_glottocodes(GRAMBANK_DIR, "Grambank")
    phoible_codes = find_language_glottocodes(PHOIBLE_DIR, "PHOIBLE")

    master_rows: list[dict[str, object]] = []
    for row in geo_rows:
        code = row.get(geo_columns["glottocode"], "").strip()
        latitude = parse_float(row.get(geo_columns["latitude"], ""))
        longitude = parse_float(row.get(geo_columns["longitude"], ""))
        if not code or not in_south_asia_box(latitude, longitude):
            continue

        metadata = languoid_metadata.get(code, {})
        master_rows.append(
            {
                "glottocode": code,
                "name": row.get(geo_columns["name"], "").strip() or metadata.get("languoid_name", ""),
                "level": field_value(row, geo_columns.get("level"), metadata.get("level", "")),
                "macroarea": field_value(row, geo_columns.get("macroarea"), metadata.get("macroarea", "")),
                "isocodes": field_value(row, geo_columns.get("isocodes"), metadata.get("isocodes", "")),
                "family": metadata.get("family", ""),
                "classification": metadata.get("classification", ""),
                "latitude": latitude,
                "longitude": longitude,
                "in_grambank": truthy_csv(code in grambank_codes),
                "in_phoible": truthy_csv(code in phoible_codes),
            }
        )

    master_rows.sort(key=lambda item: (str(item["name"]).lower(), str(item["glottocode"])))
    return master_rows


def print_counts(master_rows: list[dict[str, object]]) -> None:
    """Print the initial feasibility counts."""
    in_grambank = sum(row["in_grambank"] == "true" for row in master_rows)
    in_phoible = sum(row["in_phoible"] == "true" for row in master_rows)
    in_both = sum(row["in_grambank"] == "true" and row["in_phoible"] == "true" for row in master_rows)

    print()
    print("Wrote:", OUT_PATH)
    print("Total South/Central Asia candidates:", len(master_rows))
    print("In Grambank:", in_grambank)
    print("In PHOIBLE:", in_phoible)
    print("In both:", in_both)


def main() -> None:
    master_rows = build_master()
    write_csv_rows(OUT_PATH, master_rows, MASTER_COLUMNS)
    print_counts(master_rows)


if __name__ == "__main__":
    main()
