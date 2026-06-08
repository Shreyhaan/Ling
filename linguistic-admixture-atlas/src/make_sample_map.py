"""Create the first dependency-free SVG map from languages_master.csv."""

from __future__ import annotations

from html import escape
from pathlib import Path

from utils import is_true, parse_float, read_csv_rows

ROOT = Path(__file__).resolve().parents[1]
MASTER_PATH = ROOT / "data_processed" / "languages_master.csv"
FIGURE_PATH = ROOT / "figures" / "fig_01_candidate_sample_map.svg"

WIDTH = 900
HEIGHT = 700
PADDING = 60
MIN_LAT, MAX_LAT = 5.0, 38.0
MIN_LON, MAX_LON = 60.0, 105.0


def project(longitude: float, latitude: float) -> tuple[float, float]:
    """Project lon/lat inside the pilot bounding box to SVG x/y coordinates."""
    x = PADDING + (longitude - MIN_LON) / (MAX_LON - MIN_LON) * (WIDTH - 2 * PADDING)
    y = HEIGHT - PADDING - (latitude - MIN_LAT) / (MAX_LAT - MIN_LAT) * (HEIGHT - 2 * PADDING)
    return x, y


def point_style(row: dict[str, str]) -> str:
    """Style points by Grambank/PHOIBLE availability for the first audit map."""
    in_grambank = is_true(row.get("in_grambank", ""))
    in_phoible = is_true(row.get("in_phoible", ""))
    if in_grambank and in_phoible:
        return "#d73027"
    if in_grambank:
        return "#4575b4"
    if in_phoible:
        return "#1a9850"
    return "#999999"


def main() -> None:
    rows = read_csv_rows(MASTER_PATH)
    circles = []
    for row in rows:
        latitude = parse_float(row.get("latitude", ""))
        longitude = parse_float(row.get("longitude", ""))
        if latitude is None or longitude is None:
            continue
        x, y = project(longitude, latitude)
        name = escape(row.get("name", ""))
        code = escape(row.get("glottocode", ""))
        circles.append(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.2" fill="{point_style(row)}" opacity="0.78">'
            f'<title>{name} ({code})</title></circle>'
        )

    both = sum(is_true(row.get("in_grambank", "")) and is_true(row.get("in_phoible", "")) for row in rows)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Candidate South/Central Asian language sample">
  <rect width="100%" height="100%" fill="white"/>
  <text x="{PADDING}" y="35" font-family="sans-serif" font-size="22" font-weight="700">Candidate South/Central Asian language sample</text>
  <text x="{PADDING}" y="58" font-family="sans-serif" font-size="13" fill="#444">Bounding box: {MIN_LAT:g}–{MAX_LAT:g}°N, {MIN_LON:g}–{MAX_LON:g}°E · total={len(rows)} · Grambank∩PHOIBLE={both}</text>
  <rect x="{PADDING}" y="{PADDING}" width="{WIDTH - 2 * PADDING}" height="{HEIGHT - 2 * PADDING}" fill="#f7f7f7" stroke="#cccccc"/>
  {''.join(circles)}
  <g font-family="sans-serif" font-size="12">
    <circle cx="{PADDING}" cy="{HEIGHT - 31}" r="4" fill="#d73027"/><text x="{PADDING + 10}" y="{HEIGHT - 27}">Grambank + PHOIBLE</text>
    <circle cx="{PADDING + 170}" cy="{HEIGHT - 31}" r="4" fill="#4575b4"/><text x="{PADDING + 180}" y="{HEIGHT - 27}">Grambank only</text>
    <circle cx="{PADDING + 300}" cy="{HEIGHT - 31}" r="4" fill="#1a9850"/><text x="{PADDING + 310}" y="{HEIGHT - 27}">PHOIBLE only</text>
    <circle cx="{PADDING + 420}" cy="{HEIGHT - 31}" r="4" fill="#999999"/><text x="{PADDING + 430}" y="{HEIGHT - 27}">Neither</text>
  </g>
</svg>
'''
    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIGURE_PATH.write_text(svg, encoding="utf-8")
    print("Wrote:", FIGURE_PATH)


if __name__ == "__main__":
    main()
