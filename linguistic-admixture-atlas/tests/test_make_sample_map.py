"""Tests for dependency-free SVG map generation."""

from __future__ import annotations

import csv
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import make_sample_map as mapper  # noqa: E402


class MakeSampleMapTests(unittest.TestCase):
    def test_point_style_uses_case_insensitive_booleans(self) -> None:
        self.assertEqual(
            mapper.point_style({"in_grambank": "TRUE", "in_phoible": "true"}),
            "#d73027",
        )

    def test_escapes_svg_title_labels(self) -> None:
        original_paths = (mapper.MASTER_PATH, mapper.FIGURE_PATH)
        with TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            master_path = tmpdir_path / "languages_master.csv"
            figure_path = tmpdir_path / "sample.svg"
            with master_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["glottocode", "name", "latitude", "longitude", "in_grambank", "in_phoible"],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "glottocode": "amp<1234",
                        "name": "A & <B>",
                        "latitude": "20",
                        "longitude": "80",
                        "in_grambank": "TRUE",
                        "in_phoible": "true",
                    }
                )
            mapper.MASTER_PATH = master_path
            mapper.FIGURE_PATH = figure_path
            try:
                mapper.main()
            finally:
                mapper.MASTER_PATH, mapper.FIGURE_PATH = original_paths
            svg = figure_path.read_text(encoding="utf-8")

        self.assertIn("A &amp; &lt;B&gt; (amp&lt;1234)", svg)
        self.assertIn("Grambank∩PHOIBLE=1", svg)


if __name__ == "__main__":
    unittest.main()
