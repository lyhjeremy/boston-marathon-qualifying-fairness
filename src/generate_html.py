"""Generate the self-contained HTML report (web/index.html) with embedded figures.

Styled in the Ledger road family: tokens and fonts come from ../assets/family.css."""
import base64
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
FIG_DIR = os.path.join(PROJECT_DIR, 'outputs', 'figures')
WEB_DIR = os.path.join(PROJECT_DIR, 'web')
os.makedirs(WEB_DIR, exist_ok=True)

# ── Encode figures ────────────────────────────────────────────
def encode_fig(name):
    path = os.path.join(FIG_DIR, name)
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

fig1 = encode_fig('fig1_wr_multiplier.png')
fig3 = encode_fig('fig3_cv_comparison.png')
fig4 = encode_fig('fig4_fair_vs_actual.png')
fig5 = encode_fig('fig5_heatmap.png')
fig6 = encode_fig('fig6_alternative_bq.png')
fig7 = encode_fig('fig7_historical.png')
fig8 = encode_fig('fig8_sensitivity.png')

# ── Load results for inline tables ────────────────────────────
results = pd.read_csv(os.path.join(PROJECT_DIR, 'outputs', 'analysis_results.csv'))

# Build comparison table HTML
def build_table_rows():
    rows = []
    for _, r in results.iterrows():
        diff_wr = r['diff_from_fair'] / 60
        diff_ag = r['diff_from_fair_ag'] / 60

        # Color coding by deviation
        def cls(d):
            if abs(d) < 5:
                return 'neutral'
            if d > 0:
                return 'lenient'
            return 'strict'

        wr_cls = cls(diff_wr)
        ag_cls = cls(diff_ag)
        sign_wr = '+' if diff_wr >= 0 else ''
        sign_ag = '+' if diff_ag >= 0 else ''
        gender_label = 'M' if r['gender'] == 'M' else 'W'

        rows.append(f"""
        <tr>
          <td class="bracket">{r['age_group']}</td>
          <td class="gender gender-{gender_label.lower()}">{gender_label}</td>
          <td class="time">{r['bq_time_hhmmss']}</td>
          <td class="mult">{r['wr_multiplier']:.3f}</td>
          <td class="ag">{r['ag_pct']:.1f}%</td>
          <td class="diff diff-{wr_cls}">{sign_wr}{diff_wr:.1f}m</td>
          <td class="diff diff-{ag_cls}">{sign_ag}{diff_ag:.1f}m</td>
        </tr>""")
    return ''.join(rows)

table_rows = build_table_rows()

# ── Stylesheet (Ledger road family; no shadows, gradients, radius or hover motion) ──
CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; border-radius: 0; }
body { background: var(--paper); color: var(--ink); font: 400 18px/1.7 var(--font-head);
       border-top: 6px solid var(--signal-2); -webkit-font-smoothing: antialiased; }
a { color: var(--signal); text-decoration: underline; text-underline-offset: 3px; text-decoration-thickness: 1px; }
a:hover { color: var(--ink); }
:focus-visible { outline: 2px solid var(--signal); outline-offset: 3px; }
strong { color: var(--ink); font-weight: 600; }
code { font: 400 .84em var(--font-mono); background: var(--panel); border: 1px solid var(--rule); padding: .05em .35em; }
.bar { display: block; background: var(--ink); color: var(--paper); text-align: center; padding: 11px 18px;
       font: 600 14.5px/1.45 var(--font-body); text-decoration: none; }
.bar:hover { color: var(--paper); text-decoration: underline; }

.hero { width: min(100% - 2.4rem, 46rem); margin: 0 auto; padding: 44px 0 30px; border-bottom: 3px solid var(--ink); }
.hero-kicker { font: 400 13px/1.4 var(--font-mono); letter-spacing: .12em; text-transform: uppercase; color: var(--signal); margin-bottom: 14px; }
.hero h1 { font: 700 clamp(40px, 6.6vw, 74px)/.95 var(--font-display); text-transform: uppercase; letter-spacing: -.005em; margin-bottom: 20px; }
.hero-deck { font-size: 1.08em; color: var(--ink-2); max-width: 60ch; margin-bottom: 18px; }
.hero-meta { font: 400 13px/1.4 var(--font-mono); color: var(--ink-2); letter-spacing: .06em; text-transform: uppercase; }

.container { width: min(100% - 2.4rem, 46rem); margin: 0 auto; padding: 40px 0 30px; }
.container-wide { width: min(100% - 2.4rem, 62rem); margin: 0 auto; }
.section-label { display: block; font: 400 12.5px/1.4 var(--font-mono); letter-spacing: .14em; text-transform: uppercase;
                 color: var(--signal-2); margin: 64px 0 6px; padding-top: 14px; border-top: 1px solid var(--rule); }
h2 { font: 600 clamp(30px, 4.2vw, 42px)/1.02 var(--font-display); margin: 0 0 20px; }
h3 { font: 600 24px/1.1 var(--font-display); margin: 32px 0 10px; }
p { margin-bottom: 20px; color: var(--ink-2); }
p.lead { font-size: 1.14em; color: var(--ink); margin-bottom: 28px; }

.toc { border: 1px solid var(--edge); padding: 16px 22px; margin: 0 0 20px; }
.toc-title { font: 600 18px/1.2 var(--font-display); text-transform: uppercase; letter-spacing: .04em; margin-bottom: 8px; }
.toc ol { padding-left: 1.4em; font: 400 15.5px/1.9 var(--font-body); }

.callout { border: 1px solid var(--edge); background: var(--panel); padding: 18px 22px; margin: 28px 0;
           font: 400 16px/1.6 var(--font-body); color: var(--ink-2); }
.pullquote { font: 600 clamp(26px, 3.6vw, 34px)/1.15 var(--font-display); text-transform: uppercase; color: var(--signal);
             border-top: 3px solid var(--ink); border-bottom: 1px solid var(--rule); padding: 18px 0; margin: 40px 0; }

.stat-row { display: grid; grid-template-columns: repeat(2, 1fr); border-top: 2px solid var(--ink); border-bottom: 1px solid var(--rule); margin: 28px 0; }
@media (min-width: 700px) { .stat-row { grid-template-columns: repeat(4, 1fr); } }
.stat { padding: 14px 12px 14px 0; }
.stat .value { font: 700 40px/1 var(--font-display); color: var(--ink); font-variant-numeric: tabular-nums; }
.stat .value.accent { color: var(--signal); }
.stat .label { font: 400 12px/1.4 var(--font-mono); text-transform: uppercase; letter-spacing: .08em; color: var(--ink-2); margin-top: 6px; }

.sources-list { list-style: none; border-top: 1px solid var(--rule); margin: 0 0 24px; font: 400 15.5px/1.5 var(--font-body); }
.sources-list li { display: flex; justify-content: space-between; gap: 16px; flex-wrap: wrap; padding: 9px 0; border-bottom: 1px solid var(--rule); }
.sources-list .source { font: 400 13px/1.5 var(--font-mono); color: var(--ink-2); }

.frameworks { list-style: none; border-top: 2px solid var(--ink); margin: 24px 0; }
.frameworks li { padding: 18px 0; border-bottom: 1px solid var(--rule); }
.frameworks .tag { font: 400 12.5px/1.4 var(--font-mono); text-transform: uppercase; letter-spacing: .1em; color: var(--signal-2); }
.frameworks h3 { margin: 4px 0 8px; }
.frameworks p { margin-bottom: 10px; font-size: .95em; }
.formula { font: 400 14.5px/1.5 var(--font-mono); color: var(--ink); background: var(--panel); border: 1px solid var(--rule);
           padding: 10px 14px; margin: 10px 0; overflow-x: auto; }

.findings { list-style: none; counter-reset: f; border-top: 2px solid var(--ink); margin: 28px 0; }
.findings li { counter-increment: f; display: grid; grid-template-columns: 52px 1fr; gap: 0 14px; padding: 16px 0; border-bottom: 1px solid var(--rule); }
.findings li::before { content: counter(f, decimal-leading-zero); font: 700 34px/1 var(--font-display); color: var(--signal); grid-row: span 2; }
.findings h3 { margin: 0 0 6px; }
.findings p { margin: 0; font-size: .95em; }

figure { margin: 34px 0; }
figure img { display: block; max-width: 100%; height: auto; background: var(--panel); border: 1px solid var(--rule); padding: 10px; }
figcaption { font: 400 14.5px/1.5 var(--font-body); color: var(--ink-2); margin-top: 10px; }

.table-wrap { overflow-x: auto; border-top: 2px solid var(--ink); border-bottom: 2px solid var(--ink); }
table.results { width: 100%; min-width: 620px; border-collapse: collapse; font: 400 15px/1.3 var(--font-mono); }
table.results th { font: 600 15px/1.2 var(--font-display); text-transform: uppercase; letter-spacing: .05em; color: var(--ink-2);
                   text-align: left; padding: 9px 10px; border-bottom: 1px solid var(--ink); }
table.results td { padding: 7px 10px; border-bottom: 1px dotted var(--edge); font-variant-numeric: tabular-nums; }
table.results tr:last-child td { border-bottom: 0; }
table.results td.bracket { font: 700 18px/1 var(--font-display); }
table.results td.diff { text-align: right; }
.diff-lenient { color: var(--signal-2); }
.diff-strict { color: var(--signal); font-weight: 600; }
.diff-neutral { color: var(--ink-2); }
.table-legend { display: flex; flex-wrap: wrap; gap: 6px 22px; margin: 10px 0 0; font: 400 13.5px/1.5 var(--font-body); color: var(--ink-2); }
.table-legend b { font-weight: 600; }
.table-legend .k-lenient { color: var(--signal-2); } .table-legend .k-strict { color: var(--signal); }

footer { width: min(100% - 2.4rem, 46rem); margin: 40px auto 0; padding: 22px 0 56px; border-top: 1px solid var(--rule);
         font: 400 14.5px/1.6 var(--font-body); color: var(--ink-2); }
footer h3 { margin: 0 0 6px; font-size: 20px; text-transform: uppercase; }
footer p { margin-bottom: 8px; font-size: 14.5px; }
.footer-links { display: flex; flex-wrap: wrap; gap: 6px 20px; margin: 8px 0 10px; }
"""

# ── Build the HTML ────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Are Boston Marathon qualifying times fair? The full report</title>
<meta name="description" content="All 22 Boston Marathon age-gender qualifying standards tested against world records, an averaged top three and WMA age grading. No mean gender gap, a large variance gap, and a W80+ standard 57 minutes too strict.">
<meta property="og:title" content="Are Boston Marathon qualifying times fair?">
<meta property="og:description" content="Fair to women on average, uneven bracket to bracket, and W80+ about an hour too strict.">
<meta property="og:type" content="article">
<meta name="theme-color" content="#ECEBE6">
<link rel="stylesheet" href="../assets/family.css">
<style>{CSS}</style>
</head>
<body>
<a class="bar" href="../overview/" data-overview-link>Read the full writeup&nbsp;&rarr;</a>

<header class="hero">
  <div class="hero-kicker">Full report · Boston Marathon · May 2026</div>
  <h1>Are Boston Marathon qualifying times fair?</h1>
  <p class="hero-deck">On the mean, yes: men and women are asked for the same average effort. Bracket to bracket, the women's standards vary far more than the men's, and the W80+ standard is about 57 minutes stricter than the rest of the table. Three frameworks, 22 brackets.</p>
  <div class="hero-meta">Jeremy Lee · <a href="../">Project page</a> · <a href="Boston_BQ_Three_Frameworks_Report.pdf">PDF</a></div>
</header>

<div class="container">

<p class="lead">A 45-year-old woman chasing 3:45 and a 30-year-old man chasing 2:55 both need a Boston qualifier. Are they being asked for the same effort? I scored all 22 brackets against three different references to find out. The answer splits the usual argument in two.</p>

<div class="toc">
<div class="toc-title">Contents</div>
<ol>
  <li><a href="#question">The question nobody answers</a></li>
  <li><a href="#data">The data</a></li>
  <li><a href="#frameworks">Three definitions of fair</a></li>
  <li><a href="#findings">What the numbers say</a></li>
  <li><a href="#tightening">Did the 2026 tightening help?</a></li>
  <li><a href="#sensitivity">How much the result depends on the records chosen</a></li>
  <li><a href="#table">Every bracket</a></li>
  <li><a href="#takeaway">What to take from it</a></li>
</ol>
</div>

<span class="section-label">Section 01</span>
<h2 id="question">The question nobody answers</h2>

<p>To apply for Boston you need a qualifying time; <a href="https://www.baa.org/races/boston-marathon/qualify">the BAA's entry rules</a> leave charity places as the main other way in. You earn the time at another marathon within the qualifying window, and it has to beat the standard for your age and gender. Other World Marathon Majors take time qualifiers too (<a href="https://www.chicagomarathon.com/apply/">Chicago</a> guarantees a place to anyone under its standard), but they also hold a drawing open to everyone.</p>

<p>For the 2026 race the BAA cut five minutes from every standard below age 60. There were <strong>33,249 applications</strong> for about <strong>24,000 qualifier places</strong>, and even after the cut a runner needed to beat their standard by <strong>4 minutes 34 seconds</strong> to get in.</p>

<p>The BAA has never said how it sets each bracket's time. Its announcements refer to "careful analysis of results data" without saying whether the goal is equal difficulty, equal selectivity, a target field size or continuity with past standards.</p>

<div class="callout"><strong>A note on framing.</strong> Fairness depends on what you measure against, so this report uses three references and shows where they agree.</div>

<span class="section-label">Section 02</span>
<h2 id="data">The data</h2>

<p>The analysis covers every bracket in the 2026 standards: 11 age groups for men and for women. Non-binary athletes are excluded because the BAA says it does not yet have enough data to set standards for that category.</p>

<div class="stat-row">
  <div class="stat"><div class="value">22</div><div class="label">Brackets</div></div>
  <div class="stat"><div class="value">24,362</div><div class="label">Qualifiers accepted</div></div>
  <div class="stat"><div class="value accent">4:34</div><div class="label">Cutoff under BQ</div></div>
  <div class="stat"><div class="value accent">8,887</div><div class="label">Qualified, not accepted</div></div>
</div>

<ul class="sources-list">
  <li><span>2026 BAA qualifying standards</span><span class="source">baa.org</span></li>
  <li><span>Open marathon world records</span><span class="source">World Athletics</span></li>
  <li><span>Masters records, M40 to W80+</span><span class="source">Wikipedia masters list, WMA</span></li>
  <li><span>WMA age-grading factors</span><span class="source">WMA 2023 Appendix B</span></li>
  <li><span>2026 field size</span><span class="source">BAA press releases</span></li>
</ul>

<p>The open records are Sabastian Sawe's <strong>1:59:30</strong> (London, April 2026, <a href="https://worldathletics.org/news/press-releases/ratified-world-records-sawe-ehammer-charlton-mcrae-yan-duplantis-assefa">ratified by World Athletics</a> in July 2026) for men and Ruth Chepngetich's <strong>2:09:56</strong> (Chicago 2024) for women. Chepngetich is serving a three-year ban, announced by the <a href="https://www.athleticsintegrity.org/downloads/pdfs/other/Press-Release_Howman-Nobody-Above-the-Rules-%E2%80%93-AIU-Bans-Chepngetich-for-3-Years.pdf">Athletics Integrity Unit</a> on 23 October 2025, after a positive test for the diuretic hydrochlorothiazide on 14 March 2025; the AIU said her records from before that test stand while it looks into other material from her phone, and the <a href="https://worldathletics.org/records/all-time-toplists/road-running/marathon/all/women/senior">World Athletics all-time list</a> still puts 2:09:56 first (checked 28 October 2026). At the other end, the 80+ references are Ed Whitlock's 3:15:54 and Yoko Nakano's 4:11:45.</p>

<span class="section-label">Section 03</span>
<h2 id="frameworks">Three definitions of fair</h2>

<p>Each framework asks the same thing in a different way: does every bracket sit at the same distance from its reference?</p>

<ol class="frameworks">
<li>
  <div class="tag">Framework 1</div>
  <h3>World-record multiplier</h3>
  <p>Divide each bracket's standard by its world record. Under uniform difficulty every bracket would land on the same multiplier.</p>
  <div class="formula">multiplier = BQ_time / world_record</div>
  <p>Transparent, and one exceptional record can move a whole bracket.</p>
</li>
<li>
  <div class="tag">Framework 2</div>
  <h3>Top-three records</h3>
  <p>Replace the single record with an average of the top three. The second and third marks are estimated at 3% and 6% slower than the record for brackets with depth, and 5% and 10% for 70+.</p>
  <div class="formula">multiplier = BQ_time / mean(top3)</div>
  <p>Less sensitive to one record, but partly estimated.</p>
</li>
<li>
  <div class="tag">Framework 3</div>
  <h3>WMA age grading</h3>
  <p>World Masters Athletics publishes age factors for the expected decline in performance with age. This asks what share of age-specific potential each standard demands.</p>
  <div class="formula">AG% = (open_WR / WMA_factor) / BQ &times; 100</div>
  <p>Built on population data, so no single record sets a bracket; the assumptions sit inside the factor tables.</p>
</li>
</ol>

<span class="section-label">Section 04</span>
<h2 id="findings">What the numbers say</h2>

<p>Under Framework 1 the median multiplier across all 22 brackets is <strong>1.50&times;</strong>: the typical standard is half again as slow as the bracket's world record. The interesting part is the spread around it.</p>

<figure>
<img src="data:image/png;base64,{fig1}" alt="World-record multiplier by bracket. Men's bars sit between 1.43 and 1.53; women's run from 1.27 at W80+ to 1.62 at W35-39.">
<figcaption>Figure 1. Each bracket's standard as a multiple of its world record. Men in blue, women in red; the dashed line is the median.</figcaption>
</figure>

<p>The men's bars all fall between 1.43 and 1.53, a range of 0.10. The women's span 0.35. A Welch t-test on the means returns <strong>p = 0.81</strong>, so there is no detectable difference in average difficulty. Levene's test for equal variance returns <strong>p = 0.036</strong>: the spreads differ.</p>

<ol class="findings">
<li>
  <h3>No mean-level gender bias</h3>
  <p>Welch t-test p = 0.81 under the world-record framework and p = 0.68 under age grading. The claim that Boston is harder for women, or for men, does not survive the test.</p>
</li>
<li>
  <h3>Women's standards are less consistent</h3>
  <p>The coefficient of variation is 1.9% for men and 6.6% for women under the world-record framework, 2.1% and 7.3% with top-three records, and 4.0% and 7.8% under age grading. W35&ndash;39 sits at 1.62&times; its record and W80+ at 1.27&times;.</p>
</li>
<li>
  <h3>W80+ is the most miscalibrated bracket</h3>
  <p>The standard is <strong>57 minutes</strong> stricter than a uniform multiplier would set it, and <strong>56 minutes</strong> stricter under age grading. Both frameworks point at the same bracket.</p>
</li>
</ol>

<figure>
<img src="data:image/png;base64,{fig3}" alt="Coefficient of variation by framework. Men: 1.9, 2.1 and 4.0 percent. Women: 6.6, 7.3 and 7.8 percent.">
<figcaption>Figure 2. Coefficient of variation by framework and gender. Lower means more consistent across brackets.</figcaption>
</figure>

<p>What does a 1.50&times; multiplier mean in practice? Sawe's 1:59:30 times the median gives about 2:59 for men 18&ndash;34, close to their 2:55 standard. Apply the same proportion to every bracket and you get a "uniform" standard to compare against.</p>

<figure>
<img src="data:image/png;base64,{fig4}" alt="Minutes between each current standard and the uniform standard under each framework. W80+ falls below minus 50 minutes in each panel.">
<figcaption>Figure 3. Current standard minus uniform standard, in minutes. Above zero is more lenient, below zero stricter.</figcaption>
</figure>

<p>The younger women's brackets (18&ndash;34, 35&ndash;39, 45&ndash;49) sit 10 to 15 minutes on the lenient side. From 70 up the women's brackets turn strict. The men's stay within about 10 minutes of zero.</p>

<div class="pullquote">The averages are right. The consistency is not.</div>

<figure>
<img src="data:image/png;base64,{fig6}" alt="Current standards against the standards each framework would set, by bracket. The W80+ gap is close to an hour.">
<figcaption>Figure 4. Current standards (solid) against what each framework would set if every bracket required the same proportional effort (dashed and dotted).</figcaption>
</figure>

<span class="section-label">Section 05</span>
<h2 id="tightening">Did the 2026 tightening help?</h2>

<p>The 2026 cut was the largest single tightening since 1990: five minutes for every bracket under 60. The BAA gave record demand and faster fields as the reasons. The question here is whether it also changed the spread across brackets.</p>

<figure>
<img src="data:image/png;base64,{fig7}" alt="2020-2025 and 2026 multipliers for each bracket. Every under-60 bar drops by a similar amount; the 60+ bars are unchanged.">
<figcaption>Figure 5. The 2020&ndash;2025 standards (light) against 2026 (dark), as multiples of the current world records.</figcaption>
</figure>

<p>A flat cut within each gender leaves the shape of the table in place, and the 60+ brackets were not touched. Measured against the same records, the women's CV was 7.3% under the 2020&ndash;2025 standards and is 6.6% in 2026; the men's went from 1.8% to 1.9%. The change answered demand and left the spread across brackets close to where it was.</p>

<p>It did make one step steeper. Under the 2020&ndash;2025 standards a 59-year-old man needed 3:35 and a 60-year-old 3:50, a 15-minute step. In 2026 the step is 20 minutes, and the same is true for women.</p>

<span class="section-label">Section 06</span>
<h2 id="sensitivity">How much the result depends on the records chosen</h2>

<p>I re-ran the world-record framework three ways to see whether a single record or reference choice drives the variance gap: dropping W80+, using Sinead Diver's 2:21:34 as an alternative W40&ndash;44 reference, and using Tigst Assefa's women-only record (2:15:41) for W18&ndash;34 in place of the mixed-race mark.</p>

<figure>
<img src="data:image/png;base64,{fig8}" alt="Coefficient of variation under four scenarios. Men stay at 1.9 percent. Women: 6.6 baseline, 4.5 without W80+, 6.6 with Diver, 6.4 with Assefa.">
<figcaption>Figure 6. Coefficient of variation under four scenarios.</figcaption>
</figure>

<p><strong>W80+ carries about a third of the women's spread.</strong> Dropping it takes the women's CV from 6.6% to 4.5%. It is also the bracket most dependent on one athlete's record.</p>

<p><strong>Alternative records barely matter.</strong> Diver's mark leaves the women's CV at 6.6%; Assefa's moves it to 6.4%. The men's CV is 1.9% in every scenario.</p>

<p><strong>The gap survives every scenario.</strong> Even without W80+, the women's CV is more than twice the men's.</p>

<figure>
<img src="data:image/png;base64,{fig5}" alt="Z-score deviation heatmaps for the three frameworks. W80+ is red, meaning harder than average, in all three.">
<figcaption>Figure 7. Z-score deviation heatmaps. Red is harder than average, green easier. W80+ is red under all three frameworks.</figcaption>
</figure>

</div>

<div class="container-wide">
<span class="section-label">Section 07</span>
<h2 id="table">Every bracket</h2>

<p>All 22 brackets: the 2026 standard, the world-record multiplier, the age-graded percentage, and the minutes between the current standard and each framework's uniform standard.</p>

<div class="table-wrap">
<table class="results">
<thead>
<tr>
  <th>Age group</th>
  <th>Gender</th>
  <th>2026 BQ</th>
  <th>WR mult.</th>
  <th>Age-graded</th>
  <th style="text-align:right;">Off fair (WR)</th>
  <th style="text-align:right;">Off fair (AG)</th>
</tr>
</thead>
<tbody>
{table_rows}
</tbody>
</table>
</div>

<div class="table-legend">
  <span><b class="k-lenient">Blue</b>: current standard more than 5 minutes slower than uniform (lenient)</span>
  <span><b>Gray</b>: within 5 minutes</span>
  <span><b class="k-strict">Red</b>: more than 5 minutes faster (strict)</span>
</div>
</div>

<div class="container">

<span class="section-label">Section 08</span>
<h2 id="takeaway">What to take from it</h2>

<p>The data cannot say which framework is correct; that is a choice about what fairness means. Framework 1 fits the view that standards should track current records. Framework 3 fits the view that they should track expected decline with age. If the BAA is aiming at selectivity, field size or continuity, none of the three captures it.</p>

<p>What the data does say: <strong>the averages are balanced.</strong> Mean difficulty is the same for men and women under each framework tested. <strong>The consistency is not.</strong> The women's standards vary much more from bracket to bracket, and W80+ is an outlier under every framework.</p>

<p>If the BAA were to revisit one bracket, the data points at W80+. Easing it by 30 to 50 minutes would bring it in line with the rest of the table under both the world-record and age-graded frameworks. It would affect a few dozen runners a year.</p>

<p>A published method, even one that produced the same times, would let runners and coaches judge the standards on their own terms.</p>

<h3>Limitations</h3>
<p>There are 11 brackets per gender, so the tests are underpowered, and the Levene result (p = 0.036) is from the world-record framework only. The top-three marks are estimated. The 18&ndash;34 and 35&ndash;39 brackets share the open record because there is no separate record below 40, which makes 35&ndash;39 look more lenient. And "fair" here means equal proportional difficulty against a reference; other definitions could reach other verdicts.</p>

<div class="callout">The code, the four datasets, the notebook and the PDF report are in the <a href="https://github.com/lyhjeremy/boston-marathon-qualifying-fairness">GitHub repository</a>. Every number here comes from <code>python src/analysis.py</code>.</div>

</div>

<footer>
<h3>Boston BQ fairness</h3>
<p>Three frameworks applied to the 2026 Boston Marathon qualifying standards.</p>
<div class="footer-links">
  <a href="../">Project page</a>
  <a href="../overview/">Writeup</a>
  <a href="https://github.com/lyhjeremy/boston-marathon-qualifying-fairness">Source on GitHub</a>
  <a href="Boston_BQ_Three_Frameworks_Report.pdf">PDF report</a>
  <a href="https://github.com/lyhjeremy/boston-marathon-qualifying-fairness/blob/main/notebooks/boston_bq_fairness_analysis.ipynb">Notebook</a>
</div>
<p>MIT © 2026 Jeremy Lee · Data current as of May 2026</p>
</footer>

</body>
</html>"""

output_path = os.path.join(WEB_DIR, 'index.html')
with open(output_path, 'w') as f:
    f.write(html)

print(f"HTML saved: {output_path}")
print(f"File size: {os.path.getsize(output_path) / 1024:.0f} KB")
