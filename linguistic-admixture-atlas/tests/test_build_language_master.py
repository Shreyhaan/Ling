"""Tests for the first language-master build pipeline using tiny fixtures."""

from __future__ import annotations

import csv
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import build_language_master as builder  # noqa: E402


class BuildLanguageMasterTests(unittest.TestCase):
    def test_builds_master_from_toy_datasets(self) -> None:
        fixtures = PROJECT_ROOT / "tests" / "fixtures"
        original_paths = (
            builder.GLOTTOLOG_DIR,
            builder.GRAMBANK_DIR,
            builder.PHOIBLE_DIR,
            builder.OUT_DIR,
            builder.OUT_PATH,
        )
        with TemporaryDirectory() as tmpdir:
            builder.GLOTTOLOG_DIR = fixtures / "glottolog"
            builder.GRAMBANK_DIR = fixtures / "grambank"
            builder.PHOIBLE_DIR = fixtures / "phoible"
            builder.OUT_DIR = Path(tmpdir)
            builder.OUT_PATH = Path(tmpdir) / "languages_master.csv"
            try:
                rows = builder.build_master()
                builder.write_csv_rows(builder.OUT_PATH, rows, builder.MASTER_COLUMNS)
            finally:
                (
                    builder.GLOTTOLOG_DIR,
                    builder.GRAMBANK_DIR,
                    builder.PHOIBLE_DIR,
                    builder.OUT_DIR,
                    builder.OUT_PATH,
                ) = original_paths

            with Path(tmpdir, "languages_master.csv").open(newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                self.assertEqual(reader.fieldnames, builder.MASTER_COLUMNS)

        self.assertEqual([row["glottocode"] for row in rows], ["both1234", "dial1234", "lang1234"])
        self.assertEqual(sum(row["in_grambank"] == "true" for row in rows), 2)
        self.assertEqual(sum(row["in_phoible"] == "true" for row in rows), 2)
        self.assertEqual(sum(row["in_grambank"] == "true" and row["in_phoible"] == "true" for row in rows), 1)
        by_code = {row["glottocode"]: row for row in rows}
        self.assertEqual(by_code["both1234"]["level"], "language")
        self.assertEqual(by_code["both1234"]["macroarea"], "Eurasia")
        self.assertEqual(by_code["both1234"]["isocodes"], "bot")
        self.assertEqual(by_code["dial1234"]["level"], "dialect")
        self.assertIn("level", rows[0])
        self.assertIn("macroarea", rows[0])
        self.assertIn("isocodes", rows[0])


if __name__ == "__main__":
    unittest.main()
