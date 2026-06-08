# Contact-Admixture Atlas of Language Evolution

Working title: **Linguistic Admixture Without Genes: A Residual Atlas of Descent, Contact, and Areal Convergence in South/Central Asia**.

This repository starts the South/Central Asian pilot by building the first feasibility table:

`data_processed/languages_master.csv`

The first sprint intentionally uses only:

- **Glottolog** for language identity, coordinates, and genealogical metadata.
- **Grambank** for grammar-data availability.
- **PHOIBLE** for phonology-data availability.

Jambu, Lexibank, CLICS, D-PLACE, and ancient-DNA context are intentionally deferred until the Glottolog + Grambank + PHOIBLE pipeline works.

## Repository layout

```text
linguistic-admixture-atlas/
  data_raw/
    glottolog/
    grambank/
    phoible/
  data_processed/
  notebooks/
  src/
    build_language_master.py
    utils.py
  figures/
  paper/
```

## Raw data placement

The build script expects these files or cloned repositories:

```text
data_raw/glottolog/languages_and_dialects_geo.csv
data_raw/glottolog/glottolog_languoid.csv.zip        # optional but recommended for family/classification
data_raw/glottolog/tree_glottolog_newick.txt         # optional for this first table
data_raw/grambank/cldf/languages.csv                 # or LanguageTable.csv
data_raw/phoible/cldf/languages.csv                  # or LanguageTable.csv
```

Suggested acquisition commands, where network access allows:

```bash
git clone https://github.com/grambank/grambank.git data_raw/grambank
git clone https://github.com/cldf-datasets/phoible.git data_raw/phoible
```

Glottolog files should be downloaded from the Glottolog downloads page and placed in `data_raw/glottolog/`.

## Build the first feasibility table

```bash
python src/build_language_master.py
```

The script applies the crude first-pass South/Central Asia bounding box:

- latitude: 5 to 38
- longitude: 60 to 105

It writes `data_processed/languages_master.csv` with these initial columns:

- `glottocode`
- `name`
- `level`
- `macroarea`
- `isocodes`
- `family`
- `classification`
- `latitude`
- `longitude`
- `in_grambank`
- `in_phoible`

It also prints the first feasibility counts:

- Total South/Central Asian Glottolog coordinate candidates.
- Number in Grambank.
- Number in PHOIBLE.
- Number in both Grambank and PHOIBLE.

## First feasibility counts

Generated on: 2026-06-08

> Counts are filled in after the raw Glottolog, Grambank, and PHOIBLE data are locally available and `python src/build_language_master.py` completes.

| Quantity | Count |
|---|---:|
| South/Central Asia Glottolog coordinate candidates | TBD |
| In Grambank | TBD |
| In PHOIBLE | TBD |
| In both Grambank and PHOIBLE | TBD |

## First map

After building `languages_master.csv`, create the first SVG map with:

```bash
python src/make_sample_map.py
```

This writes:

```text
figures/fig_01_candidate_sample_map.svg
```

## Notebook audit

`notebooks/01_dataset_audit.ipynb` contains the first interactive audit: load the master table, print overlap counts, inspect the overlapping sample, and draw a simple longitude/latitude scatterplot.
