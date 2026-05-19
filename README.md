# Are Boston Marathon Qualifying Times Fair?

**A Three-Framework Comparative Analysis of BQ Standards Across Age and Gender**

[![Read the article](https://img.shields.io/badge/Read-Web_Article-C0392B?style=flat-square)](https://boston-bq-fairness.vercel.app)
[![PDF report](https://img.shields.io/badge/Download-PDF_Report-1a1a2e?style=flat-square)](reports/Boston_BQ_Three_Frameworks_Report.pdf)
[![License](https://img.shields.io/badge/License-MIT-D4A537?style=flat-square)](LICENSE)

---

## Overview

The Boston Athletic Association (BAA) sets qualifying times for 22 age-gender brackets but has never publicly disclosed the methodology behind them. This project applies three independent fairness frameworks to ask whether current BQ standards represent equal difficulty across all brackets:

1. **World Record Multiplier** — BQ time as a multiple of the bracket's world record
2. **Top-3 Records** — Robustness check using averaged top performances
3. **WMA Age-Graded Scoring** — Difficulty relative to age-specific biological potential

Plus two deeper analysis layers:

4. **Historical Comparison** — Did the 2026 tightening change the fairness picture?
5. **Sensitivity Analysis** — Are conclusions robust to outliers and alternative reference records?

## Key Findings

| Finding | Details |
|---------|---------|
| **No mean-level gender bias** | Welch t-test p = 0.81. Average difficulty is balanced across genders |
| **Women's brackets 3-4× more variable** | CV: men 1.9%, women 6.6% under WR framework |
| **W80+ is most miscalibrated** | 57 minutes too strict under WR, 56 min under age-grading |
| **2026 tightening did not improve consistency** | Variance gap is unchanged from 2020-2025 |
| **W80+ alone drives ~⅓ of women's variance** | Removing it drops women's CV from 6.6% to 4.5% |

![WR Multiplier Chart](outputs/figures/fig1_wr_multiplier.png)

## Deliverables

- **Web article** (`web/index.html`) — Self-contained magazine-style page with embedded figures and custom SVG illustrations. 1.5 MB. Opens offline.
- **Academic PDF** (`reports/Boston_BQ_Three_Frameworks_Report.pdf`) — 8-page report: abstract, methodology, results, sensitivity, limitations.
- **Jupyter notebook** (`notebooks/boston_bq_fairness_analysis.ipynb`) — Fully executable, cell-by-cell.

## Repository Structure

```
boston-bq-fairness/
├── data/                          # Verified source data (CSV)
│   ├── bq_standards_2026.csv      # BAA qualifying times
│   ├── world_records.csv          # Marathon WRs by bracket
│   ├── wma_age_factors.csv        # WMA 2023 age-grading factors
│   └── field_size_2026.csv        # 2026 field metrics
├── notebooks/
│   └── boston_bq_fairness_analysis.ipynb
├── src/
│   ├── analysis.py                # Core analysis + all 8 figures
│   ├── generate_pdf.py            # PDF report builder
│   ├── generate_html.py           # Web article builder
│   └── build_notebook.py          # Notebook generator
├── outputs/
│   ├── analysis_results.csv       # Full results table (22 rows × 20 cols)
│   └── figures/                   # 8 publication-ready PNGs
├── reports/
│   └── Boston_BQ_Three_Frameworks_Report.pdf
├── web/
│   ├── index.html                 # Self-contained web article
│   └── Boston_BQ_Three_Frameworks_Report.pdf  # Mirrored for download link
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

## Quick Start

```bash
git clone https://github.com/lyhjeremy/boston-bq-fairness.git
cd boston-bq-fairness
pip install -r requirements.txt

# Reproduce everything from scratch
python src/analysis.py
python src/generate_pdf.py
python src/generate_html.py
python src/build_notebook.py
```

## Data Sources

| Dataset | Source | Verification |
|---------|--------|--------------|
| BQ Standards | [baa.org](https://www.baa.org/races/boston-marathon/qualify/) | All 22 brackets verified directly from BAA |
| Open WRs | World Athletics | Sawe 1:59:30, Chepngetich 2:09:56 |
| Masters WRs | [Wikipedia / WMA](https://en.wikipedia.org/wiki/List_of_masters_world_records_in_road_running) | Cross-referenced against WMA ratified records |
| WMA Factors | [WMA 2023 Appendix B](https://howardgrubb.co.uk/athletics/wmatnf23.html) | Official WMA tables |
| Field Size | BAA press releases | 24,362 accepted / 4:34 cutoff |

## Limitations

- Non-binary athletes excluded (BAA itself notes insufficient data)
- Top-3 Framework uses estimated depth factors, not verified 2nd/3rd place times
- Under-35 brackets use open WR as reference (no separate masters record exists)
- n = 11 per gender — formal statistical tests are underpowered

## License

MIT — see [LICENSE](LICENSE)

## Author

Jeremy Lee — [github.com/lyhjeremy](https://github.com/lyhjeremy)
