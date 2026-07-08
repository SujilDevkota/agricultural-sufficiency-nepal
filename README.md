# District-Level Patterns of Land Fragmentation, Irrigation Access, and Agricultural Production Sufficiency in Nepal

A district-level study of how **land fragmentation** and **irrigation access** relate to **agricultural production sufficiency** across all **77 districts of Nepal**, built from the official tables of the *National Sample Census of Agriculture (NSCA) 2021/22*.

**Author:** Sujil Devkota · M.A. Economics
**Institution:** Patan Multiple Campus, Tribhuvan University
**Supervisor:** Dr. Kumar Bhattarai
**Repository:** https://github.com/SujilDevkota/agricultural-sufficiency-nepal

This repository is the home of the completed thesis. It holds the final thesis PDF, the presentation, and the full, runnable analysis — code and data together, so every table and figure in the thesis can be reproduced from source.

---

## Abstract

This thesis examines how land fragmentation and irrigation access are associated with agricultural production sufficiency across the 77 districts of Nepal. A district-level dataset is constructed from the published tables of the NSCA 2021/22. Because the outcome is a bounded proportion, the analysis combines descriptive and correlation evidence with a weighted OLS benchmark and a **fractional logit model** with province fixed effects, mean-centred interactions, and extensive robustness checks.

The data reveal large spatial variation: average parcels per holding range from **1.5 to 6.3**, the irrigated-area share from about **3 to 91 percent**, and the insufficiency share from **32 to 87 percent**. In the multivariate results, **irrigation coverage is the dominant correlate** — its association with insufficiency is negative and statistically significant in every specification, attenuating but remaining significant when ecological-belt controls replace province effects. Predicted insufficiency differs by roughly **20 percentage points** between low- and high-irrigation profiles (a descriptive contrast, not an intervention effect), with bootstrap intervals that exclude zero. The association with land fragmentation is absorbed by geography once fixed effects and controls are included, and the fragmentation–irrigation interaction is statistically null.

The findings are district-level associations rather than causal effects. The pattern is nonetheless consistent with prioritising irrigation expansion in low-coverage hill and mountain districts, pursuing land consolidation only as a complement bundled with irrigation and mechanisation, and targeting chronic food deprivation toward near-landless peri-urban and Terai holdings.

**Keywords:** land fragmentation, irrigation access, production sufficiency, Nepal

---

## Repository contents

```
agricultural-sufficiency-nepal/
├── paper/
│   └── thesis.pdf             Final thesis (read this)
├── slides/
│   └── presentation.pdf       Defense presentation (20 slides)
├── code/                      Analysis pipeline (Python, standard library + numpy/matplotlib)
├── data/
│   ├── raw/nsonepal/          NSCA 2021/22 source reports (PDF) + digitised tables (CSV)
│   ├── raw/*.geojson          District boundaries
│   └── processed/             Assembled district-level dataset
├── requirements.txt
└── LICENSE
```

## Data

The analysis is built on the **National Sample Census of Agriculture (NSCA) 2021/22**, published by the National Statistics Office, Government of Nepal. The two official source reports are included in [`data/raw/nsonepal/`](data/raw/nsonepal/): the national report and the district-level summary. The tables used here (parcels, irrigation by source, food sufficiency, farm population, mechanisation, credit, market access, and more) are digitised from them into CSVs in the same folder. [`build_research_dataset.py`](code/build_research_dataset.py) assembles those into the analysis-ready panel at [`data/processed/district_research_dataset.csv`](data/processed/district_research_dataset.csv) — one row per district, 77 districts.

## Reproducing the analysis

Requires Python 3.9+.

```bash
git clone https://github.com/SujilDevkota/agricultural-sufficiency-nepal.git
cd agricultural-sufficiency-nepal
pip install -r requirements.txt

# 1. Assemble the district dataset from the NSCA source tables
python3 code/build_research_dataset.py

# 2. Core estimation: fractional logit, weighted correlations, APEs, scenarios
python3 code/run_final_paper_analysis.py

# 3. Robustness and supplementary checks
python3 code/run_thesis_robustness.py
python3 code/run_thesis_review_extras.py
python3 code/run_spatial_diagnostics.py
python3 code/run_diagnostic_tests.py

# 4. Regenerate the result tables and figures
python3 code/generate_thesis_tables.py
python3 code/generate_final_paper_figures.py
python3 code/generate_annex_figures.py
```

Every output — the intermediate CSVs and memos, the result tables, and the figures — is written to `results/` (git-ignored and fully regenerable). These reproduce the exact tables and figures reported in the thesis PDF.

## Method in brief

The outcome — the district share of holdings reporting production insufficiency — is a bounded proportion, so the primary specification is a **fractional logit** (quasi-maximum-likelihood) model with province fixed effects and holding-count weights. It is benchmarked against weighted OLS and checked with ecological-belt controls, mean-centred interactions, variance-inflation diagnostics, a spatial-autocorrelation (Moran's I) test, and holding-weighted bootstrap intervals. Effects are reported as average partial effects and as descriptive low- vs. high-coverage scenario contrasts.

## Citation

> Devkota, S. (2026). *District-Level Patterns of Land Fragmentation, Irrigation Access, and Agricultural Production Sufficiency in Nepal* [Master's thesis, Tribhuvan University].

## License

Code is released under the MIT License. The thesis and presentation are the author's academic work; the underlying NSCA 2021/22 data remain the property of the National Statistics Office, Government of Nepal. See [LICENSE](LICENSE).
