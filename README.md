# Are Boston Marathon Qualifying Times Fair?

A three-framework comparative analysis of Boston Athletic Association qualifying standards across age and gender brackets.

📊 **[Read the full writeup →](writeup.md)** &nbsp;·&nbsp; 📄 [PDF report](reports/Boston_BQ_Three_Frameworks_Report.pdf) &nbsp;·&nbsp; 📝 [Word doc](reports/Boston_BQ_Three_Frameworks_Report.docx) &nbsp;·&nbsp; 📓 [Notebook](notebooks/boston_bq_fairness_analysis.ipynb)

> 📖 **In depth:** https://lyhjeremy.github.io/boston-marathon-qualifying-fairness/overview/

---

## What this is

The BAA publishes qualifying times for 22 age-gender brackets but has never explained how those numbers are set. This project applies three independent fairness frameworks to ask whether the standards demand equal proportional effort across all brackets:

1. **World Record Multiplier** — BQ time as a multiple of the bracket's world record
2. **Top-3 Records** — Robustness check using averaged top performances
3. **WMA Age-Graded Scoring** — Difficulty relative to age-specific biological potential

Plus historical comparison (did the 2026 tightening change the picture?) and sensitivity analysis (are conclusions robust to outliers and alternative reference records?).

## Headline findings

- **No mean-level gender bias** — Welch t-test p = 0.81 across all frameworks
- **Women's brackets are 3-4× more variable than men's** — CV 6.6% vs 1.9% under WR framework
- **W80+ is the most miscalibrated bracket** — 57 minutes too strict under WR, 56 min under age-grading

Full methodology, statistical tests, and bracket-by-bracket results in [`writeup.md`](writeup.md).

## Repository structure

```
boston-marathon-qualifying-fairness/
├── data/                          # Four source CSVs (BQ standards, WRs, WMA factors, field size)
├── notebooks/                     # Jupyter notebook reproducing the analysis end-to-end
├── src/                           # Python/JS source for analysis, PDF, DOCX, HTML
├── outputs/                       # Generated figures (400 DPI) and results CSV
├── reports/                       # PDF and Word versions of the writeup
├── web/                           # Self-contained HTML article (deployable to Vercel)
├── writeup.md                     # Full report in markdown — renders on GitHub
├── README.md                      # This file
├── LICENSE                        # MIT
└── requirements.txt
```

## Reproducing the analysis

```bash
git clone https://github.com/lyhjeremy/boston-marathon-qualifying-fairness.git
cd boston-marathon-qualifying-fairness
pip install -r requirements.txt
python src/analysis.py
```

Or open `notebooks/boston_bq_fairness_analysis.ipynb` in Jupyter / VS Code and run all cells.

## Data sources

| Dataset | Source |
|---------|--------|
| 2026 BQ Standards | [baa.org](https://www.baa.org/races/boston-marathon/qualify/) |
| Open Marathon WRs | World Athletics |
| Masters Marathon WRs | [Wikipedia / WMA](https://en.wikipedia.org/wiki/List_of_masters_world_records_in_road_running) |
| WMA Age Factors | [WMA 2023 Appendix B](https://howardgrubb.co.uk/athletics/wmatnf23.html) |
| Field Size Metrics | BAA press releases |

## License

MIT — see [LICENSE](LICENSE)

## Author

Jeremy Lee — [github.com/lyhjeremy](https://github.com/lyhjeremy)
