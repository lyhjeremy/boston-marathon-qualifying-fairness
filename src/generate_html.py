"""Generate the self-contained HTML web article with embedded figures and SVG art."""
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

# ── SVG illustrations (custom-built, no licensing concerns) ───
SVG_HERO_RUNNERS = """<svg viewBox="0 0 1200 400" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0F1729"/>
      <stop offset="50%" stop-color="#1E2A4A"/>
      <stop offset="100%" stop-color="#2A3F6E"/>
    </linearGradient>
    <linearGradient id="road" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#2A2D3F"/>
      <stop offset="100%" stop-color="#181B2A"/>
    </linearGradient>
    <radialGradient id="sun" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#FFB347" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#FFB347" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1200" height="400" fill="url(#sky)"/>
  <circle cx="900" cy="120" r="200" fill="url(#sun)"/>
  <circle cx="900" cy="120" r="50" fill="#FFB347" opacity="0.4"/>
  <g opacity="0.4" fill="#0A0F1F">
    <rect x="0" y="200" width="60" height="120"/>
    <rect x="70" y="180" width="40" height="140"/>
    <rect x="120" y="190" width="80" height="130"/>
    <rect x="210" y="160" width="50" height="160"/>
    <rect x="270" y="200" width="60" height="120"/>
    <rect x="340" y="170" width="70" height="150"/>
    <rect x="420" y="190" width="40" height="130"/>
    <rect x="470" y="180" width="60" height="140"/>
    <rect x="540" y="200" width="50" height="120"/>
    <rect x="600" y="160" width="80" height="160"/>
    <rect x="690" y="195" width="45" height="125"/>
    <rect x="745" y="175" width="65" height="145"/>
    <rect x="820" y="200" width="55" height="120"/>
    <rect x="885" y="185" width="70" height="135"/>
    <rect x="965" y="170" width="50" height="150"/>
    <rect x="1025" y="195" width="60" height="125"/>
    <rect x="1095" y="180" width="55" height="140"/>
  </g>
  <path d="M 0 320 L 1200 320 L 1200 400 L 0 400 Z" fill="url(#road)"/>
  <g stroke="#D4A537" stroke-width="3" stroke-dasharray="40 30" opacity="0.5">
    <line x1="0" y1="360" x2="1200" y2="360"/>
  </g>
  <g fill="#E5E7EB">
    <g transform="translate(280, 280)">
      <circle cx="0" cy="-30" r="8"/>
      <path d="M -3 -22 L -5 0 L -10 15 L -6 15 L -3 -2 L 3 -2 L 6 15 L 10 15 L 5 0 L 3 -22 Z"/>
      <path d="M -8 -10 L -15 -2" stroke="#E5E7EB" stroke-width="3" fill="none" stroke-linecap="round"/>
      <path d="M 8 -8 L 14 4" stroke="#E5E7EB" stroke-width="3" fill="none" stroke-linecap="round"/>
    </g>
    <g transform="translate(420, 285)" opacity="0.9">
      <circle cx="0" cy="-32" r="9"/>
      <path d="M -3 -23 L -6 2 L -11 18 L -7 18 L -3 0 L 3 0 L 7 18 L 11 18 L 6 2 L 3 -23 Z"/>
      <path d="M -8 -12 L -16 0" stroke="#E5E7EB" stroke-width="3" fill="none" stroke-linecap="round"/>
      <path d="M 8 -10 L 16 4" stroke="#E5E7EB" stroke-width="3" fill="none" stroke-linecap="round"/>
    </g>
    <g transform="translate(580, 282)">
      <circle cx="0" cy="-34" r="10"/>
      <path d="M -3 -24 L -6 4 L -12 20 L -8 20 L -3 2 L 3 2 L 8 20 L 12 20 L 6 4 L 3 -24 Z"/>
      <path d="M -9 -14 L -18 -3" stroke="#E5E7EB" stroke-width="3" fill="none" stroke-linecap="round"/>
      <path d="M 9 -12 L 18 2" stroke="#E5E7EB" stroke-width="3" fill="none" stroke-linecap="round"/>
    </g>
    <g transform="translate(740, 285)" opacity="0.85">
      <circle cx="0" cy="-31" r="8"/>
      <path d="M -3 -22 L -5 1 L -10 17 L -6 17 L -3 -1 L 3 -1 L 6 17 L 10 17 L 5 1 L 3 -22 Z"/>
      <path d="M -8 -10 L -15 -1" stroke="#E5E7EB" stroke-width="3" fill="none" stroke-linecap="round"/>
      <path d="M 8 -8 L 14 4" stroke="#E5E7EB" stroke-width="3" fill="none" stroke-linecap="round"/>
    </g>
    <g transform="translate(880, 280)" opacity="0.7">
      <circle cx="0" cy="-30" r="7"/>
      <path d="M -2 -22 L -4 0 L -9 15 L -5 15 L -2 -2 L 2 -2 L 5 15 L 9 15 L 4 0 L 2 -22 Z"/>
    </g>
  </g>
</svg>"""

SVG_STOPWATCH = """<svg viewBox="0 0 200 220" xmlns="http://www.w3.org/2000/svg">
  <rect x="92" y="8" width="16" height="14" fill="#374151" rx="2"/>
  <rect x="90" y="20" width="20" height="6" fill="#1a1a2e" rx="1"/>
  <circle cx="100" cy="120" r="85" fill="#FAFAFA" stroke="#1a1a2e" stroke-width="4"/>
  <circle cx="100" cy="120" r="78" fill="none" stroke="#E5E7EB" stroke-width="1"/>
  <g stroke="#374151" stroke-width="2">
    <line x1="100" y1="50" x2="100" y2="58"/>
    <line x1="100" y1="182" x2="100" y2="190"/>
    <line x1="30" y1="120" x2="38" y2="120"/>
    <line x1="162" y1="120" x2="170" y2="120"/>
  </g>
  <line x1="100" y1="120" x2="135" y2="85" stroke="#C0392B" stroke-width="4" stroke-linecap="round"/>
  <line x1="100" y1="120" x2="100" y2="65" stroke="#1a1a2e" stroke-width="2.5" stroke-linecap="round"/>
  <circle cx="100" cy="120" r="5" fill="#C0392B"/>
  <text x="100" y="155" font-family="Source Sans 3, sans-serif" font-size="12" font-weight="700" fill="#6B7280" text-anchor="middle" letter-spacing="2">BQ</text>
</svg>"""

SVG_MEDAL = """<svg viewBox="0 0 200 240" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#FFD700"/>
      <stop offset="50%" stop-color="#FFC700"/>
      <stop offset="100%" stop-color="#D4A537"/>
    </linearGradient>
    <linearGradient id="ribbon" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#C0392B"/>
      <stop offset="100%" stop-color="#8B1A0E"/>
    </linearGradient>
  </defs>
  <path d="M 70 10 L 50 110 L 100 130 L 150 110 L 130 10 Z" fill="url(#ribbon)"/>
  <path d="M 70 10 L 50 110 L 100 130 L 100 10 Z" fill="url(#ribbon)" opacity="0.7"/>
  <circle cx="100" cy="165" r="55" fill="url(#gold)" stroke="#8B6914" stroke-width="2"/>
  <circle cx="100" cy="165" r="45" fill="none" stroke="#8B6914" stroke-width="1" opacity="0.6"/>
  <text x="100" y="160" font-family="Playfair Display, serif" font-size="22" font-weight="700" fill="#8B4513" text-anchor="middle">26.2</text>
  <text x="100" y="180" font-family="Source Sans 3, sans-serif" font-size="9" font-weight="600" fill="#8B4513" text-anchor="middle" letter-spacing="1">MILES</text>
</svg>"""

# ── Build the HTML ────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Are Boston Marathon Qualifying Times Fair? | A Three-Framework Analysis</title>
<meta name="description" content="A data-driven look at whether Boston Marathon qualifying times treat every age and gender bracket equally, using three independent fairness frameworks.">
<meta property="og:title" content="Are Boston Marathon Qualifying Times Fair?">
<meta property="og:description" content="A three-framework comparative analysis of BQ standards. 22 brackets, three lenses, surprising results.">
<meta property="og:type" content="article">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&family=Source+Sans+3:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {{
  --bg: #FDFCF9;
  --bg-alt: #F5F2EC;
  --text: #1a1a2e;
  --text-soft: #4A4A5E;
  --accent: #C0392B;
  --accent-dark: #8B1A0E;
  --blue: #2563EB;
  --green: #059669;
  --gold: #D4A537;
  --muted: #6B7280;
  --border: #E5E7EB;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
  --shadow-md: 0 4px 16px rgba(0,0,0,0.08);
  --shadow-lg: 0 10px 40px rgba(0,0,0,0.12);
  --serif: "Playfair Display", Georgia, serif;
  --sans: "Source Sans 3", -apple-system, BlinkMacSystemFont, sans-serif;
  --mono: "JetBrains Mono", "SF Mono", Consolas, monospace;
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{
  background: var(--bg);
  color: var(--text);
  font-family: var(--sans);
  font-size: 18px;
  line-height: 1.75;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}}

/* HERO */
.hero {{
  position: relative;
  height: 100vh;
  min-height: 600px;
  max-height: 800px;
  overflow: hidden;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 40px 24px;
}}
.hero-bg {{ position: absolute; top: 0; right: 0; bottom: 0; left: 0; inset: 0; z-index: 0; }}
.hero-bg svg {{ width: 100%; height: 100%; display: block; }}
.hero-overlay {{
  position: absolute; top: 0; right: 0; bottom: 0; left: 0; inset: 0;
  background: linear-gradient(180deg, rgba(15,23,41,0.3) 0%, rgba(15,23,41,0.7) 70%, rgba(15,23,41,0.9) 100%);
  z-index: 1;
}}
.hero-content {{ position: relative; z-index: 2; max-width: 900px; }}
.hero-kicker {{
  font-family: var(--mono);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 3px;
  color: var(--gold);
  margin-bottom: 24px;
  opacity: 0.9;
}}
.hero h1 {{
  font-family: var(--serif);
  font-size: clamp(2.5rem, 7vw, 5rem);
  font-weight: 900;
  line-height: 1.05;
  margin-bottom: 24px;
  letter-spacing: -0.02em;
  text-shadow: 0 2px 20px rgba(0,0,0,0.3);
}}
.hero h1 em {{
  font-style: italic;
  color: #FFB347;
  font-weight: 700;
}}
.hero-deck {{
  font-size: clamp(1.05rem, 2vw, 1.3rem);
  font-weight: 300;
  max-width: 700px;
  margin: 0 auto 32px;
  opacity: 0.92;
  line-height: 1.5;
}}
.hero-meta {{
  font-family: var(--mono);
  font-size: 0.78rem;
  letter-spacing: 1.5px;
  opacity: 0.7;
  text-transform: uppercase;
}}
.hero-scroll {{
  position: absolute;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2;
  font-family: var(--mono);
  font-size: 0.7rem;
  letter-spacing: 2px;
  opacity: 0.6;
  text-transform: uppercase;
  animation: bounce 2s infinite;
}}
@keyframes bounce {{
  0%, 20%, 50%, 80%, 100% {{ transform: translate(-50%, 0); }}
  40% {{ transform: translate(-50%, -10px); }}
  60% {{ transform: translate(-50%, -5px); }}
}}

/* CONTAINER */
.container {{ max-width: 760px; margin: 0 auto; padding: 80px 24px 40px; }}
.container-wide {{ max-width: 1000px; margin: 0 auto; padding: 0 24px; }}

/* TYPOGRAPHY */
.section-label {{
  font-family: var(--mono);
  font-size: 0.75rem;
  letter-spacing: 3px;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 600;
  margin-bottom: 12px;
  display: block;
}}
h2 {{
  font-family: var(--serif);
  font-size: clamp(1.6rem, 3.5vw, 2.4rem);
  font-weight: 700;
  margin: 64px 0 24px;
  color: var(--text);
  line-height: 1.2;
  letter-spacing: -0.01em;
}}
h2:first-of-type {{ margin-top: 0; }}
h3 {{ font-family: var(--serif); font-size: 1.4rem; font-weight: 700; margin: 40px 0 12px; }}
h4 {{ font-family: var(--sans); font-size: 1.05rem; font-weight: 700; margin: 24px 0 8px; }}
p {{ margin-bottom: 22px; color: var(--text-soft); }}
p.lead {{
  font-family: var(--serif);
  font-size: 1.35rem;
  font-weight: 400;
  font-style: italic;
  line-height: 1.55;
  color: var(--text);
  margin-bottom: 32px;
  border-left: 4px solid var(--accent);
  padding-left: 20px;
}}
strong {{ color: var(--text); font-weight: 700; }}
em {{ font-style: italic; }}
a {{ color: var(--accent); text-decoration: none; border-bottom: 1px solid currentColor; }}
a:hover {{ color: var(--accent-dark); }}

/* CALLOUTS */
.callout {{
  background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
  border-left: 4px solid var(--gold);
  padding: 24px 28px;
  margin: 32px 0;
  border-radius: 0 12px 12px 0;
  font-size: 1rem;
  color: var(--text);
}}
.callout strong {{ color: #92400E; }}
.pullquote {{
  font-family: var(--serif);
  font-style: italic;
  font-size: 1.6rem;
  line-height: 1.4;
  color: var(--text);
  text-align: center;
  margin: 48px 0;
  padding: 24px 32px;
  position: relative;
}}
.pullquote::before, .pullquote::after {{
  font-family: var(--serif);
  color: var(--accent);
  font-size: 3rem;
  position: absolute;
  font-style: normal;
  font-weight: 700;
}}
.pullquote::before {{ content: "\\201C"; top: -10px; left: 0; }}
.pullquote::after {{ content: "\\201D"; bottom: -40px; right: 0; }}

/* FINDINGS */
.findings {{ display: grid; gap: 20px; margin: 32px 0; }}
.finding {{
  background: white;
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 28px 32px;
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
  overflow: hidden;
}}
.finding::before {{
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 4px;
  background: var(--accent);
}}
.finding:hover {{ transform: translateY(-2px); box-shadow: var(--shadow-md); }}
.finding .number {{
  font-family: var(--serif);
  font-size: 3rem;
  color: var(--accent);
  font-weight: 900;
  line-height: 1;
  margin-bottom: 8px;
  opacity: 0.4;
}}
.finding h4 {{
  font-family: var(--serif);
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0 0 8px;
  color: var(--text);
}}
.finding p {{ font-size: 0.98rem; margin: 0; color: var(--text-soft); }}

/* FIGURES */
figure {{ margin: 40px 0; text-align: center; }}
figure img {{
  max-width: 100%;
  height: auto;
  border-radius: 12px;
  box-shadow: var(--shadow-md);
}}
figcaption {{
  font-size: 0.88rem;
  color: var(--muted);
  margin-top: 14px;
  font-style: italic;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}}

/* STAT CARDS */
.stat-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 16px;
  margin: 36px 0;
}}
.stat-card {{
  background: white;
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 24px 20px;
  text-align: center;
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s;
}}
.stat-card:hover {{ transform: translateY(-3px); box-shadow: var(--shadow-md); }}
.stat-card .value {{
  font-family: var(--serif);
  font-size: 2.4rem;
  font-weight: 900;
  color: var(--blue);
  line-height: 1;
}}
.stat-card .value.accent {{ color: var(--accent); }}
.stat-card .label {{
  font-family: var(--mono);
  font-size: 0.7rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 1.5px;
  margin-top: 10px;
}}
.stat-card .sub {{
  font-size: 0.78rem;
  color: var(--text-soft);
  margin-top: 4px;
  font-style: italic;
}}

/* METHODOLOGY CARDS */
.method-grid {{ display: grid; gap: 20px; margin: 32px 0; }}
.methodology {{
  background: var(--bg-alt);
  border-radius: 14px;
  padding: 28px;
  border: 1px solid var(--border);
  position: relative;
}}
.methodology .tag {{
  position: absolute;
  top: -10px;
  right: 24px;
  background: var(--accent);
  color: white;
  font-family: var(--mono);
  font-size: 0.7rem;
  padding: 4px 12px;
  border-radius: 12px;
  letter-spacing: 1px;
  text-transform: uppercase;
  font-weight: 600;
}}
.methodology h4 {{
  font-family: var(--serif);
  font-size: 1.25rem;
  margin-bottom: 10px;
  color: var(--text);
}}
.methodology p {{ font-size: 0.98rem; margin-bottom: 12px; color: var(--text-soft); }}
.methodology p:last-child {{ margin-bottom: 0; }}
.methodology .formula {{
  background: white;
  border-radius: 8px;
  padding: 12px 16px;
  font-family: var(--mono);
  font-size: 0.85rem;
  color: var(--text);
  border-left: 3px solid var(--accent);
  margin: 12px 0;
  overflow-x: auto;
}}

/* TABLE */
.table-wrap {{
  overflow-x: auto;
  margin: 32px 0;
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  background: white;
}}
table.results {{ width: 100%; border-collapse: collapse; font-size: 0.92rem; }}
table.results thead {{ background: var(--text); color: white; }}
table.results th {{
  padding: 14px 12px;
  text-align: left;
  font-family: var(--mono);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 1.5px;
  text-transform: uppercase;
}}
table.results td {{ padding: 12px; border-bottom: 1px solid var(--border); }}
table.results tr:last-child td {{ border-bottom: none; }}
table.results tr:nth-child(even) {{ background: #FAFAFA; }}
table.results .bracket {{ font-weight: 600; font-family: var(--mono); font-size: 0.85rem; }}
table.results .gender {{ text-align: center; font-weight: 700; width: 40px; }}
table.results .gender-m {{ color: var(--blue); }}
table.results .gender-w {{ color: var(--accent); }}
table.results .time, table.results .mult, table.results .ag {{
  font-family: var(--mono);
  font-size: 0.88rem;
}}
table.results .diff {{
  font-family: var(--mono);
  font-size: 0.85rem;
  font-weight: 600;
  text-align: right;
}}
table.results .diff-neutral {{ color: var(--muted); }}
table.results .diff-lenient {{ color: var(--green); }}
table.results .diff-strict {{ color: var(--accent); }}

.table-legend {{
  display: flex;
  gap: 24px;
  font-size: 0.85rem;
  color: var(--muted);
  margin-top: 12px;
  flex-wrap: wrap;
}}
.table-legend span {{ display: inline-flex; align-items: center; gap: 6px; }}
.table-legend .dot {{ width: 10px; height: 10px; border-radius: 50%; }}
.dot-green {{ background: var(--green); }}
.dot-red {{ background: var(--accent); }}
.dot-gray {{ background: var(--muted); }}

/* DECORATIVE */
.decorative {{ display: flex; justify-content: center; margin: 40px 0; }}
.decorative svg {{ width: 160px; height: auto; opacity: 0.85; }}
.section-divider {{
  display: block;
  width: 60px;
  height: 4px;
  background: var(--accent);
  margin: 64px auto 32px;
  border-radius: 2px;
}}

/* TOC */
.toc {{
  background: var(--bg-alt);
  border-radius: 12px;
  padding: 24px 28px;
  margin: 0 0 48px;
}}
.toc-title {{
  font-family: var(--mono);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: var(--accent);
  font-weight: 600;
  margin-bottom: 14px;
}}
.toc ol {{ list-style: none; counter-reset: toc; }}
.toc li {{
  counter-increment: toc;
  padding: 8px 0;
  font-size: 0.95rem;
  border-bottom: 1px dashed var(--border);
}}
.toc li:last-child {{ border-bottom: none; }}
.toc li::before {{
  content: counter(toc, decimal-leading-zero);
  font-family: var(--mono);
  font-size: 0.75rem;
  color: var(--accent);
  margin-right: 12px;
  font-weight: 600;
}}
.toc a {{ color: var(--text); border: none; }}
.toc a:hover {{ color: var(--accent); }}

/* SOURCES LIST */
.sources-list {{ list-style: none; padding: 0; margin: 0 0 24px; }}
.sources-list li {{
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  gap: 16px;
}}
.sources-list li:last-child {{ border-bottom: none; }}
.sources-list .source {{ color: var(--muted); font-family: var(--mono); font-size: 0.85rem; }}

/* FOOTER */
footer {{
  background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1e 100%);
  color: rgba(255,255,255,0.7);
  padding: 80px 24px 40px;
  text-align: center;
  margin-top: 80px;
  position: relative;
  overflow: hidden;
}}
footer::before {{
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 4px;
  background: var(--accent);
}}
footer h3 {{
  font-family: var(--serif);
  color: white;
  font-size: 1.5rem;
  margin: 0 0 12px;
}}
footer p {{ color: rgba(255,255,255,0.6); font-size: 0.95rem; margin-bottom: 8px; }}
footer a {{ color: #FFB347; border: none; }}
footer a:hover {{ color: #FFD700; }}
.footer-links {{
  display: flex;
  justify-content: center;
  gap: 32px;
  margin: 24px 0;
  flex-wrap: wrap;
  font-family: var(--mono);
  font-size: 0.8rem;
  letter-spacing: 1.5px;
  text-transform: uppercase;
}}
.footer-meta {{
  font-family: var(--mono);
  font-size: 0.72rem;
  letter-spacing: 1.5px;
  color: rgba(255,255,255,0.4);
  margin-top: 32px;
  text-transform: uppercase;
}}

/* INLINE CODE */
code {{
  background: #fff;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: var(--mono);
  font-size: 0.85em;
  border: 1px solid var(--border);
}}

/* RESPONSIVE */
@media (max-width: 700px) {{
  .container {{ padding: 56px 20px 40px; }}
  .container-wide {{ padding: 0 20px; }}
  .hero {{ min-height: 500px; }}
  h2 {{ font-size: 1.6rem; margin: 48px 0 18px; }}
  h3 {{ font-size: 1.2rem; }}
  p.lead {{ font-size: 1.1rem; }}
  .stat-grid {{ grid-template-columns: repeat(2, 1fr); gap: 12px; }}
  .stat-card .value {{ font-size: 1.8rem; }}
  .finding {{ padding: 20px 22px; }}
  .pullquote {{ font-size: 1.2rem; padding: 16px 24px; }}
  .footer-links {{ gap: 16px; }}
  table.results th, table.results td {{ padding: 10px 8px; font-size: 0.8rem; }}
}}
</style>
</head>
<body>

<div class="hero">
  <div class="hero-bg">{SVG_HERO_RUNNERS}</div>
  <div class="hero-overlay"></div>
  <div class="hero-content">
    <div class="hero-kicker">Data Analysis · Marathon · May 2026</div>
    <h1>Are Boston Marathon<br>Qualifying Times <em>Fair?</em></h1>
    <p class="hero-deck">The BAA has set qualifying standards for 22 age-gender brackets for decades. Their methodology has never been publicly disclosed. We applied three independent fairness frameworks to find out what the data actually says.</p>
    <div class="hero-meta">By Jeremy Lee &middot; 12-minute read</div>
  </div>
  <div class="hero-scroll">↓ Scroll to read</div>
</div>

<div class="container">

<p class="lead">If you're a 45-year-old woman who trained for months to hit a 3:45 marathon, are you being held to the same standard of effort as a 30-year-old man chasing 2:55? Or are some brackets simply getting a better deal? After analyzing 22 brackets through three different lenses, the answer turns out to be more interesting than either side of the usual argument.</p>

<div class="toc">
<div class="toc-title">What's in this analysis</div>
<ol>
  <li><a href="#question">The Question Nobody Answers</a></li>
  <li><a href="#data">The Data Behind 30,000 Hopefuls</a></li>
  <li><a href="#frameworks">Three Lenses on Fairness</a></li>
  <li><a href="#findings">What the Numbers Actually Say</a></li>
  <li><a href="#tightening">Did the 2026 Tightening Help?</a></li>
  <li><a href="#sensitivity">How Robust Are These Conclusions?</a></li>
  <li><a href="#table">The Complete Bracket-by-Bracket Table</a></li>
  <li><a href="#takeaway">The Honest Take</a></li>
</ol>
</div>

<span class="section-label">Section 01</span>
<h2 id="question">The Question Nobody Answers</h2>

<p>On April 20, 2026, roughly 30,000 runners will line up in Hopkinton, Massachusetts to run the world's oldest annual marathon. Most of them earned that starting spot the hard way: by running a qualifying time in another marathon, somewhere in the world, within the previous 18 months. The Boston Marathon is one of only two World Marathon Majors that requires you to qualify by performance rather than by lottery or charity.</p>

<p>The Boston Athletic Association (BAA) publishes qualifying times across 11 age groups and 3 gender categories. For the 2026 race, they tightened standards by a full five minutes across the board for everyone under 60, responding to record demand: <strong>33,249 applications</strong> for roughly <strong>24,000 qualifier spots</strong>. Even after the tightening, runners had to beat their published standard by <strong>4 minutes 34 seconds</strong> to actually get in.</p>

<p>But here's the thing: in the BAA's century-long history of adjusting these standards, they've never publicly explained <em>how</em> they arrive at each bracket's specific time. Their official press releases reference &ldquo;careful analysis of results data&rdquo; without specifying whether they're optimizing for equal difficulty, equal selectivity, field-size targets, historical continuity, or something else entirely.</p>

<div class="callout">
<strong>Important framing:</strong> Fairness isn't a fact. It's a choice of what you measure against. That's why we used three different frameworks. Each one captures a different intuition about what &ldquo;fair&rdquo; should mean. We let you decide which one matters most.
</div>

<div class="decorative">{SVG_STOPWATCH}</div>

<span class="section-label">Section 02</span>
<h2 id="data">The Data Behind 30,000 Hopefuls</h2>

<p>We analyzed every bracket in the 2026 Boston Marathon (11 age groups &times; 2 genders, excluding non-binary because the BAA itself notes insufficient data to set evidence-based standards for that category yet).</p>

<div class="stat-grid">
  <div class="stat-card">
    <div class="value">22</div>
    <div class="label">Brackets</div>
    <div class="sub">11 ages × 2 genders</div>
  </div>
  <div class="stat-card">
    <div class="value">24,362</div>
    <div class="label">Qualifiers In</div>
    <div class="sub">Of 33,249 applied</div>
  </div>
  <div class="stat-card">
    <div class="value accent">4:34</div>
    <div class="label">Under BQ</div>
    <div class="sub">Actual 2026 cutoff</div>
  </div>
  <div class="stat-card">
    <div class="value accent">8,887</div>
    <div class="label">Turned Away</div>
    <div class="sub">Despite hitting BQ</div>
  </div>
</div>

<p>Data sources, all verified against primary sources:</p>

<ul class="sources-list">
  <li><span style="font-weight:600;">2026 BAA Qualifying Standards</span><span class="source">baa.org</span></li>
  <li><span style="font-weight:600;">Open Marathon World Records</span><span class="source">World Athletics</span></li>
  <li><span style="font-weight:600;">Masters Records (M35-M80, W35-W80)</span><span class="source">Wikipedia / WMA / ARRS</span></li>
  <li><span style="font-weight:600;">WMA Age-Grading Factors</span><span class="source">WMA 2023 Appendix B</span></li>
  <li><span style="font-weight:600;">2026 Field Size Metrics</span><span class="source">BAA press releases</span></li>
</ul>

<p>The marathon world records anchoring this analysis are extraordinary. Sabastian Sawe set the open men's record of <strong>1:59:30</strong> at London in April 2026, becoming the first man to break two hours in a record-eligible race. The women's open record stands at <strong>2:09:56</strong> (Ruth Chepngetich, Chicago 2024). For the 80-and-over bracket, Ed Whitlock's 3:15:54 (men) and Yoko Nakano's 4:11:45 (women) are the references; both are landmark performances for athletes in their ninth decade.</p>

<span class="section-label">Section 03</span>
<h2 id="frameworks">Three Lenses on Fairness</h2>

<p>Every fairness analysis depends on what you compare to. We deliberately chose three anchors that capture different intuitions about what &ldquo;equal difficulty&rdquo; should mean.</p>

<div class="method-grid">

<div class="methodology">
  <div class="tag">Framework 1</div>
  <h4>World Record Multiplier</h4>
  <p>For each bracket, divide the BQ time by the bracket's world record. If the BAA aimed for uniform difficulty under this lens, every bracket would land at the same multiplier — say, exactly 1.50× the WR.</p>
  <div class="formula">multiplier = BQ_time / world_record</div>
  <p style="font-size:0.9rem; color:var(--muted); font-style:italic;">Strength: transparent and intuitive. Weakness: a single extraordinary record can skew an entire bracket.</p>
</div>

<div class="methodology">
  <div class="tag">Framework 2</div>
  <h4>Top-3 Records Average</h4>
  <p>World records are outliers by definition. To dampen this, we replace the single WR with the average of the top three known performances per bracket. For deep brackets, we estimate #2 and #3 at 3% and 6% slower than the WR; for thin older brackets, 5% and 10%.</p>
  <div class="formula">multiplier = BQ_time / mean(top3)</div>
  <p style="font-size:0.9rem; color:var(--muted); font-style:italic;">Strength: more robust to outliers. Weakness: top-3 data is estimated for some brackets.</p>
</div>

<div class="methodology">
  <div class="tag">Framework 3</div>
  <h4>WMA Age-Graded Scoring</h4>
  <p>The most sophisticated approach. World Masters Athletics publishes empirically derived age factors that capture the <em>expected</em> performance decline with age across population data — not individual records. We ask: what fraction of your age-specific biological potential does Boston demand?</p>
  <div class="formula">AG% = (open_WR × WMA_factor) / BQ × 100</div>
  <p style="font-size:0.9rem; color:var(--muted); font-style:italic;">Strength: grounded in population biology, not outliers. Weakness: hides assumptions inside the WMA factor tables.</p>
</div>

</div>

<span class="section-label">Section 04</span>
<h2 id="findings">What the Numbers Actually Say</h2>

<p>Here's the first surprise. Under Framework 1, the median multiplier across all 22 brackets is almost exactly <strong>1.50×</strong>. The typical BQ standard requires you to run 50% slower than your bracket's world record. But the spread tells the real story.</p>

<figure>
<img src="data:image/png;base64,{fig1}" alt="WR Multiplier by bracket showing men cluster tightly while women's brackets vary widely">
<figcaption>Figure 1. BQ time as a multiple of the world record, for each age-gender bracket. Men's brackets (blue) cluster tightly around the median; women's brackets (red) vary dramatically, from 1.27× (W80+) to 1.62× (W35-39).</figcaption>
</figure>

<p>Notice how the blue bars all sit between 1.43 and 1.53 — a range of only 0.10. The red bars span 0.35, more than three times that range. For men, the &ldquo;standard&rdquo; difficulty relative to their world record is remarkably consistent. For women, it's all over the map.</p>

<p>A formal statistical test confirms what the eye sees. A Welch t-test comparing the two distributions returns <strong>p = 0.81</strong> — no significant difference in <em>means</em>. But Levene's test for equal variance returns <strong>p = 0.036</strong>: the variances are statistically different. The averages are balanced. The consistency isn't.</p>

<div class="findings">

<div class="finding">
  <div class="number">01</div>
  <h4>No mean-level gender bias</h4>
  <p>Welch t-test: p = 0.81 across all three frameworks. The average difficulty for men and women is statistically indistinguishable. The familiar criticism that &ldquo;Boston is harder for women&rdquo; (or vice versa) does not survive testing. Whatever the BAA optimizes for, they've calibrated the mean correctly across genders.</p>
</div>

<div class="finding">
  <div class="number">02</div>
  <h4>Women's brackets are 3-4× more variable</h4>
  <p>Coefficient of variation (CV) for men: 1.9% under WR framework, 4.0% under age-grading. For women: 6.6% and 7.8%. This holds across every framework we tested. Some women's brackets are clearly lenient (W35-39 sits at 1.62× the WR), while others are brutal (W80+ at 1.27×). The men's brackets simply don't show this pattern.</p>
</div>

<div class="finding">
  <div class="number">03</div>
  <h4>W80+ is the single most miscalibrated bracket</h4>
  <p>Under the WR framework, the current W80+ standard is <strong>57 minutes too strict</strong> relative to a uniform multiplier. Under age-grading: <strong>56 minutes too strict</strong>. This holds regardless of which framework you prefer. If there's one bracket the BAA should revisit on equity grounds alone, the data unambiguously points to this one.</p>
</div>

</div>

<figure>
<img src="data:image/png;base64,{fig3}" alt="Coefficient of variation comparison across three frameworks">
<figcaption>Figure 2. Coefficient of variation by framework and gender. Lower bars mean more consistent standards across brackets. Women's bars are 3-4× taller than men's under every framework, telling us the variability isn't an artifact of how we measure.</figcaption>
</figure>

<p>What does a 1.50× multiplier mean in practice? It means that if Sabastian Sawe's 1:59:30 represents the ceiling of male marathon performance, an 18-34 man hitting his 2:55:00 BQ standard is running at 68% of that pace. Hold that proportion constant and you get the &ldquo;fair&rdquo; BQ for every bracket. The next chart shows the gap between what the BAA sets today and what each framework suggests.</p>

<figure>
<img src="data:image/png;base64,{fig4}" alt="Bar chart showing the gap between current BQ and fair BQ under each framework">
<figcaption>Figure 3. Difference between current and &ldquo;fair&rdquo; BQ times, in minutes. Bars above zero mean the current BQ is more lenient than a uniform standard; bars below mean stricter. Note the deep red bar at W80+ in every panel.</figcaption>
</figure>

<p>The pattern is striking. Younger women's brackets (18-34, 35-39, 45-49) sit well above the zero line — they're relatively lenient relative to their reference records. Then everything flips at 70+, where women's brackets become aggressively strict. Men's bars hover near zero across the board.</p>

<div class="pullquote">
The BAA has the averages right. They haven't yet solved for consistency.
</div>

<figure>
<img src="data:image/png;base64,{fig6}" alt="Line chart of current vs fair BQ times under all three frameworks">
<figcaption>Figure 4. Current BQ times (solid lines) versus what each framework would suggest if every bracket required equal proportional effort (dashed and dotted lines). The W80+ gap balloons to nearly an hour.</figcaption>
</figure>

<span class="section-label">Section 05</span>
<h2 id="tightening">Did the 2026 Tightening Help?</h2>

<p>The 2026 race introduced the largest single tightening of qualifying times since 1990 — five minutes across the board for athletes under 60. The BAA's stated rationale: more applicants than ever, athletes getting faster, and a desire to set a standard that better reflects current performance levels. But did the tightening also improve fairness across brackets, or did it just shift everything uniformly?</p>

<figure>
<img src="data:image/png;base64,{fig7}" alt="Comparison of 2020-2025 BQ multipliers to 2026">
<figcaption>Figure 5. The 2020-2025 standards (light bars) versus the 2026 standards (dark bars), both expressed as multipliers of the current world record. The tightening lowered every under-60 bar by roughly the same proportion — but the gender variability gap persisted.</figcaption>
</figure>

<p>The answer: the tightening was uniform within each gender, which means the relative <em>structure</em> of the standards barely moved. The 60+ brackets weren't touched at all. Women's variance in 2020-2025 (CV ≈ 6.8%) and 2026 (6.6%) are essentially identical. The 2026 changes responded to demand, not to fairness across brackets.</p>

<p>There's an interesting wrinkle here. By tightening only under-60 standards, the BAA implicitly steepened the &ldquo;step&rdquo; between the 55-59 and 60-64 brackets. Under the 2020-2025 standards, a 59-year-old man needed 3:35; his 60-year-old self needed 3:50 — a 15-minute jump. Under 2026, the gap is 20 minutes. That birthday cliff is now larger.</p>

<span class="section-label">Section 06</span>
<h2 id="sensitivity">How Robust Are These Conclusions?</h2>

<p>Before drawing conclusions, we stress-tested the main finding (women's brackets are 3-4× more variable than men's) against three alternative scenarios. If a single outlier or a debatable choice of reference record drives the result, we'd see the gap collapse under any of these perturbations.</p>

<figure>
<img src="data:image/png;base64,{fig8}" alt="Sensitivity analysis bar chart">
<figcaption>Figure 6. Coefficient of variation under four scenarios. Men's CV (blue) stays at 1.9% throughout — the men's data has no critical outlier. Women's CV (red) drops from 6.6% to 4.5% only when we remove W80+ entirely.</figcaption>
</figure>

<p>Three takeaways from this:</p>

<p><strong>The W80+ bracket alone accounts for nearly a third of women's bracket variance.</strong> Dropping it cuts women's CV from 6.6% to 4.5%. That's a single data point doing enormous statistical work. It's both the most miscalibrated bracket and the one most dependent on one extraordinary athlete (Yoko Nakano's 4:11:45) for its reference record.</p>

<p><strong>The result is robust to alternative records.</strong> Substituting Sinead Diver's W40 marathon (2:21:34) as the W40-44 reference barely changes women's CV. Using the women-only WR (Assefa 2:15:41) instead of the mixed-race WR shifts CV from 6.6% to 6.4%. The variance gap is not an artifact of which records we anchor to.</p>

<p><strong>Even with the most outlier-friendly choices, women's CV remains 2-3× higher than men's.</strong> The structural inconsistency in women's brackets is genuine.</p>

<figure>
<img src="data:image/png;base64,{fig5}" alt="Deviation heatmaps across all three frameworks">
<figcaption>Figure 7. Z-score deviation heatmaps. Red cells indicate brackets harder than average; green cells indicate easier. W80+ glows red across all three frameworks, while the lower-right (older women's brackets) shows a consistent pattern of strictness.</figcaption>
</figure>

<span class="section-label">Section 07</span>
</div>

<div class="container-wide">
<h2 id="table" style="text-align:center; max-width:760px; margin-left:auto; margin-right:auto;">The Complete Bracket-by-Bracket Table</h2>

<p style="max-width:760px; margin:0 auto 24px; color:var(--text-soft);">All 22 brackets. Current BAA standard alongside the WR multiplier, age-graded percentage, and how many minutes off each framework's &ldquo;fair&rdquo; standard each bracket sits.</p>

<div class="table-wrap">
<table class="results">
<thead>
<tr>
  <th>Age Group</th>
  <th>Gender</th>
  <th>Current BQ</th>
  <th>WR Mult</th>
  <th>Age-Graded</th>
  <th style="text-align:right;">Diff (WR)</th>
  <th style="text-align:right;">Diff (AG)</th>
</tr>
</thead>
<tbody>
{table_rows}
</tbody>
</table>
</div>

<div class="table-legend" style="max-width:760px; margin:12px auto 0;">
  <span><span class="dot dot-green"></span>Lenient (current BQ slower than fair)</span>
  <span><span class="dot dot-gray"></span>Within 5 minutes of fair</span>
  <span><span class="dot dot-red"></span>Strict (current BQ faster than fair)</span>
</div>
</div>

<div class="container">

<span class="section-divider"></span>
<span class="section-label">Section 08</span>
<h2 id="takeaway">The Honest Take</h2>

<p>This analysis cannot tell you which framework is &ldquo;correct.&rdquo; That's not a data question; it's a values question. If you believe fairness means equal difficulty relative to current world records, Framework 1 is your lens. If you want to account for biological aging, Framework 3 is more defensible. If you think the BAA should optimize for equal selectivity, field-size diversity, or historical continuity, none of these frameworks fully capture that.</p>

<p>What the data <em>can</em> tell you is this: <strong>the BAA has the averages right.</strong> The mean difficulty is balanced across genders under every framework we tested. The criticism that &ldquo;Boston is unfair to women&rdquo; (or men) does not survive statistical testing. <strong>The consistency, though, is not balanced.</strong> Women's brackets are 3-4× more variable than men's, and the W80+ bracket is a genuine outlier regardless of how you measure.</p>

<p>If the BAA wanted to address one bracket on equity grounds alone, the data points clearly at W80+. Adjusting it by 30-50 minutes would bring it in line with every other bracket under either the WR or age-graded framework. The change would affect roughly a few dozen runners per year, but the symbolic message — that the standard for an 80-year-old woman should be calibrated to the same difficulty as a 30-year-old man — would be substantial.</p>

<div class="decorative">{SVG_MEDAL}</div>

<p>The deeper question isn't whether the BAA is right or wrong. It's whether they've publicly committed to a fairness framework at all, or whether the standards have evolved through a combination of historical inertia, demand management, and ad-hoc adjustments. The data is consistent with the latter. A more transparent methodology — even if it leads to the same numbers — would let runners, coaches, and statisticians evaluate the system on its own terms rather than guessing at what it's trying to do.</p>

<div class="callout">
<strong>Want to dig deeper?</strong> The complete code, all four datasets, the Jupyter notebook, and a formal academic PDF report are available in the GitHub repository: <a href="https://github.com/lyhjeremy/boston-bq-fairness">github.com/lyhjeremy/boston-bq-fairness</a>. Everything in this article is reproducible from a single <code>python src/analysis.py</code>.
</div>

</div>

<footer>
<h3>Boston BQ Fairness Analysis</h3>
<p>A three-framework comparative analysis of Boston Marathon qualifying times.</p>
<div class="footer-links">
  <a href="https://github.com/lyhjeremy/boston-bq-fairness">View Source on GitHub</a>
  <a href="Boston_BQ_Three_Frameworks_Report.pdf">Download PDF Report</a>
  <a href="https://github.com/lyhjeremy/boston-bq-fairness/blob/main/notebooks/boston_bq_fairness_analysis.ipynb">Open Notebook</a>
</div>
<p class="footer-meta">© 2026 Jeremy Lee &middot; MIT License &middot; Data current as of May 2026</p>
</footer>

</body>
</html>"""

output_path = os.path.join(WEB_DIR, 'index.html')
with open(output_path, 'w') as f:
    f.write(html)

print(f"HTML saved: {output_path}")
print(f"File size: {os.path.getsize(output_path) / 1024:.0f} KB")
