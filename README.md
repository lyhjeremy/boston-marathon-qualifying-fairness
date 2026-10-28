# Are Boston Marathon qualifying times fair?

The Boston Athletic Association has never said how it sets its qualifying times. This repo audits all 22 age-gender standards for 2026 against three yardsticks (world-record multipliers, averaged top-three records and WMA age grading) and asks whether every bracket is equally hard.

[Live site](https://lyhjeremy.github.io/boston-marathon-qualifying-fairness/) · [Write-up](https://lyhjeremy.github.io/boston-marathon-qualifying-fairness/overview/) · [Full report](https://lyhjeremy.github.io/boston-marathon-qualifying-fairness/web/) · [PDF](reports/Are_Boston_Marathon_Qualifying_Times_Fair_Report.pdf) · [Notebook](notebooks/boston_bq_fairness_analysis.ipynb)

Design and copy follow [these standards](https://github.com/lyhjeremy/lyhjeremy/blob/main/DESIGN_STANDARDS.md).

## Results

| Finding | Number |
|---|---|
| Gender gap in mean difficulty (Welch t-test) | p = 0.81 world-record framework, p = 0.68 age-graded |
| Spread across brackets, men vs women (coefficient of variation) | 1.9% vs 6.6% world-record; 2.1% vs 7.3% top-three; 4.0% vs 7.8% age-graded |
| Equal-variance test (Levene, world-record framework) | W = 5.04, p = 0.036 |
| W80+ standard against a uniform standard | 57 min too strict (world-record), 56 min (age-graded) |

The BAA gets the average right, since men and women are asked for the same mean effort. Where it slips is consistency: the women's standards vary much more from bracket to bracket, and W80+ (5:20:00, where a uniform multiplier gives 6:17:20) is the strictest bracket under every framework.

![Bar chart of each bracket's qualifying standard as a multiple of its world record. Men's bars sit between 1.43 and 1.53; women's run from 1.27 at W80+ to 1.62 at W35-39.](outputs/figures/fig1_wr_multiplier.png)

## Method

Each framework asks whether every bracket sits at the same distance from a reference:

1. World-record multiplier: the BQ time divided by the bracket's world record (open records below 40, masters records from 40 up).
2. Top-three records: the same ratio against an averaged top three. The second and third marks are estimated at 3% and 6% slower than the record (5% and 10% for 70+).
3. WMA age grading: the open record divided by the WMA 2023 age factor, as a percentage of the BQ time.

Gender differences in the mean are tested with a Welch t-test and differences in spread with Levene's test and the coefficient of variation. A uniform "fair" standard applies the median multiplier (1.50×) or median age-graded percentage (67.9%) to every bracket. Z-score heatmaps flag outlying brackets. Sensitivity runs drop W80+ and swap in alternative records (Sinead Diver's W45 mark, Tigst Assefa's women-only record); a historical run compares the 2020-2025 standards with 2026.

Stack: Python (pandas, NumPy, SciPy, matplotlib, seaborn), Jupyter. The PDF and Word reports are generated from the same results.

## How to run

```bash
git clone https://github.com/lyhjeremy/boston-marathon-qualifying-fairness.git
cd boston-marathon-qualifying-fairness
pip install -r requirements.txt
python src/analysis.py        # figures to outputs/figures/, results to outputs/analysis_results.csv
python src/generate_html.py   # rebuilds the HTML report at web/index.html
```

Or open `notebooks/boston_bq_fairness_analysis.ipynb` and run all cells.

## Repository layout

| Path | Contents |
|---|---|
| `data/` | Four source CSVs: 2026 standards, world records, WMA age factors, 2026 field size |
| `src/` | `analysis.py` (all statistics and figures), report generators for HTML, PDF and Word |
| `notebooks/` | The analysis as a notebook |
| `outputs/` | Eight figures and the 22-row results table |
| `reports/` | PDF and Word versions of the report |
| `web/` | Self-contained HTML report |
| `overview/` | The write-up page |
| `writeup.md`, `article.md` | The report in Markdown, and a first-person version |

## Data sources

| Dataset | Source |
|---|---|
| 2026 qualifying standards | [baa.org](https://www.baa.org/races/boston-marathon/qualify/) |
| Open marathon records | World Athletics |
| Masters marathon records | [Wikipedia masters list](https://en.wikipedia.org/wiki/List_of_masters_world_records_in_road_running), checked against WMA |
| WMA age factors | [WMA 2023 Appendix B](https://howardgrubb.co.uk/athletics/wmatnf23.html) |
| Field size | BAA press releases |

## Limitations

- Eleven brackets per gender, so the tests have little power. The Levene result is for the world-record framework only.
- The top-three framework uses estimated second and third marks.
- Below 40 there is no separate masters record, so 18-34 and 35-39 share the open record, which makes 35-39 look more lenient.
- Non-binary athletes (110 accepted in 2026) are excluded; the BAA says it lacks the data to set standards for the category.
- "Fair" here means equal proportional difficulty against a reference. The BAA may be optimizing for field size or continuity, which this audit does not measure.

## License

[MIT](LICENSE) © 2026 Jeremy Lee
