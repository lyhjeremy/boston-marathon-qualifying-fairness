"""
Generate the academic technical PDF report for the Boston BQ Fairness Analysis.
"""
import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak,
    Table, TableStyle, KeepTogether
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
FIG_DIR = os.path.join(PROJECT_DIR, 'outputs', 'figures')
RESULTS_PATH = os.path.join(PROJECT_DIR, 'outputs', 'analysis_results.csv')
OUTPUT_PATH = os.path.join(PROJECT_DIR, 'reports', 'Boston_BQ_Three_Frameworks_Report.pdf')
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ── Styles ─────────────────────────────────────────────────────
styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    'DocTitle', parent=styles['Title'],
    fontSize=22, spaceAfter=6, textColor=HexColor('#1a1a2e'),
    fontName='Times-Bold',
))
styles.add(ParagraphStyle(
    'DocSubtitle', parent=styles['Normal'],
    fontSize=13, spaceAfter=20, alignment=TA_CENTER,
    textColor=HexColor('#555555'), fontName='Times-Italic',
))
styles.add(ParagraphStyle(
    'SectionHead', parent=styles['Heading1'],
    fontSize=15, spaceBefore=20, spaceAfter=8,
    textColor=HexColor('#1a1a2e'), fontName='Times-Bold',
))
styles.add(ParagraphStyle(
    'SubHead', parent=styles['Heading2'],
    fontSize=12, spaceBefore=14, spaceAfter=6,
    textColor=HexColor('#333333'), fontName='Times-Bold',
))
styles.add(ParagraphStyle(
    'Body', parent=styles['Normal'],
    fontSize=11, leading=15, alignment=TA_JUSTIFY,
    fontName='Times-Roman', spaceAfter=8,
))
styles.add(ParagraphStyle(
    'Caption', parent=styles['Normal'],
    fontSize=9, leading=12, alignment=TA_CENTER,
    textColor=HexColor('#666666'), fontName='Times-Italic',
    spaceBefore=4, spaceAfter=12,
))
styles.add(ParagraphStyle(
    'SmallNote', parent=styles['Normal'],
    fontSize=9, leading=11, fontName='Times-Italic',
    textColor=HexColor('#888888'),
))


def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PATH, pagesize=letter,
        topMargin=0.8*inch, bottomMargin=0.8*inch,
        leftMargin=1*inch, rightMargin=1*inch,
    )
    story = []

    # ── Title ──────────────────────────────────────────────────
    story.append(Paragraph(
        "Are Boston Marathon Qualifying Times Fair?", styles['DocTitle']))
    story.append(Paragraph(
        "A Three-Framework Comparative Analysis of BQ Standards Across Age and Gender",
        styles['DocSubtitle']))
    story.append(Paragraph(
        "Jeremy Lee  |  May 2026  |  github.com/lyhjeremy/boston-bq-fairness",
        styles['DocSubtitle']))
    story.append(Spacer(1, 20))

    # ── Abstract ───────────────────────────────────────────────
    story.append(Paragraph("Abstract", styles['SectionHead']))
    story.append(Paragraph(
        "The Boston Athletic Association sets qualifying times that vary by age and gender, "
        "but has never publicly disclosed the methodology behind these standards. This report "
        "examines whether current BQ times represent equal difficulty across all 22 age-gender "
        "brackets by applying three independent frameworks: (1) a world-record multiplier, "
        "(2) a top-three-records robustness check, and (3) WMA age-graded scoring. "
        "All three frameworks reveal the same structural pattern: men's brackets are remarkably "
        "consistent (CV 1.9-4.0%), while women's brackets show 3-4 times more variation "
        "(CV 6.6-7.8%), driven primarily by outlier reference records in younger and oldest "
        "brackets. A Welch t-test on gender means returns p = 0.81 under the WR framework, "
        "indicating no significant mean-level difference. The W80+ bracket stands out as the "
        "most miscalibrated under all frameworks. We present alternative BQ tables under each "
        "framework and discuss limitations.",
        styles['Body']))
    story.append(Spacer(1, 10))

    # ── 1. Introduction ────────────────────────────────────────
    story.append(Paragraph("1. Introduction", styles['SectionHead']))
    story.append(Paragraph(
        "The Boston Marathon, first run in 1897, is the world's oldest annually contested marathon "
        "and one of only a handful of major marathons that requires a qualifying time for entry. "
        "The Boston Athletic Association (BAA) publishes qualifying standards across 11 age groups "
        "and two genders (plus a non-binary category adopted in recent years). For the 2026 race, "
        "the BAA tightened standards by five minutes for all athletes under 60, responding to "
        "record demand: 33,249 applications for roughly 24,000 qualifier spots.",
        styles['Body']))
    story.append(Paragraph(
        "Despite decades of adjustments, the BAA has never publicly explained the quantitative "
        "framework behind its qualifying times. Their rationale statements reference 'careful "
        "analysis of results data' without specifying whether they optimize for equal difficulty, "
        "equal selectivity, field-size targets, or historical continuity. This creates a natural "
        "research question: are the qualifying times equitable across age and gender brackets?",
        styles['Body']))
    story.append(Paragraph(
        "We define 'equitable' operationally as: every bracket requires the same proportional "
        "effort relative to a shared anchor. The choice of anchor is itself a fairness decision, "
        "which is why we apply three different anchors and compare what each reveals.",
        styles['Body']))

    # ── 2. Data ────────────────────────────────────────────────
    story.append(Paragraph("2. Data Sources", styles['SectionHead']))
    story.append(Paragraph(
        "2026 BAA qualifying standards were sourced directly from baa.org. Open marathon world "
        "records (men: Sabastian Sawe, 1:59:30, London 2026; women mixed: Ruth Chepngetich, "
        "2:09:56, Chicago 2024) were verified against World Athletics. Masters records (M35 through "
        "W80+) were compiled from the Wikipedia list of masters world records in road running, "
        "cross-referenced with WMA ratified records. WMA 2023 age-grading factors were sourced "
        "from the official Appendix B tables. Field-size data (24,362 accepted qualifiers, "
        "4:34 cutoff) from BAA press releases.",
        styles['Body']))
    story.append(Paragraph(
        "Scope: 22 brackets (11 age groups x 2 genders). Non-binary athletes (110 accepted in "
        "2026) are excluded because the BAA itself notes insufficient data to determine "
        "appropriate time standards for this category.",
        styles['Body']))

    # ── 3. Methodology ─────────────────────────────────────────
    story.append(Paragraph("3. Methodology", styles['SectionHead']))

    story.append(Paragraph("3.1 Framework 1: World Record Multiplier", styles['SubHead']))
    story.append(Paragraph(
        "For each bracket, we compute: multiplier = BQ time / world record time. If the BAA "
        "aimed for uniform difficulty under this framework, every bracket would have the same "
        "multiplier. Deviations indicate brackets where the standard is relatively easier or harder "
        "than average. For brackets below age 40, the open world record is used as the reference "
        "since no separate masters record exists. This is an acknowledged limitation: it makes "
        "the 35-39 bracket appear artificially easy.",
        styles['Body']))

    story.append(Paragraph("3.2 Framework 2: Top-Three Records", styles['SubHead']))
    story.append(Paragraph(
        "Single world records are inherently outlier-sensitive. To test robustness, we replace "
        "the single WR with an estimated average of the top three known performances per bracket. "
        "For brackets with rich competition depth (35-69), we estimate the second- and third-best "
        "times at 3% and 6% slower than the WR, based on observed patterns from London 2026 "
        "masters results. For thin brackets (70+, 80+), we use 5% and 10% gaps. This is clearly "
        "an approximation; we flag it throughout.",
        styles['Body']))

    story.append(Paragraph("3.3 Framework 3: WMA Age-Graded Scoring", styles['SubHead']))
    story.append(Paragraph(
        "World Masters Athletics publishes empirically derived age factors that represent the "
        "expected performance decline with age. We compute the age-adjusted standard for each "
        "bracket and ask: what fraction of their age-specific potential does each BQ standard "
        "demand? The formula: age-graded % = (open WR / BQ time) x (1 / WMA factor) x 100. "
        "Unlike Frameworks 1 and 2, this approach accounts for the biological expectation at each "
        "age rather than anchoring to a single exceptional performance.",
        styles['Body']))

    # ── 4. Results ─────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("4. Results", styles['SectionHead']))

    story.append(Paragraph("4.1 Framework 1: World Record Multiplier", styles['SubHead']))
    story.append(Paragraph(
        "The median multiplier across all 22 brackets is 1.50x, meaning the typical BQ standard "
        "is 50% slower than the world record for that bracket. Men's brackets cluster tightly "
        "(CV = 1.9%, range 1.43-1.53x), while women's brackets spread three times wider "
        "(CV = 6.6%, range 1.27-1.62x). A Welch t-test on gender means returns t = -0.25, "
        "p = 0.81, indicating no significant mean-level difference between genders. However, "
        "Levene's test for variance equality returns W = 5.04, p = 0.036, confirming the visual "
        "impression that women's brackets are significantly less consistent.",
        styles['Body']))

    # Figure 1
    fig1_path = os.path.join(FIG_DIR, 'fig1_wr_multiplier.png')
    if os.path.exists(fig1_path):
        story.append(Image(fig1_path, width=6.2*inch, height=3.1*inch))
        story.append(Paragraph(
            "Figure 1. BQ time as a multiple of world record, by age-gender bracket. "
            "Dashed line = median (1.50x). Women's bars show much wider spread.",
            styles['Caption']))

    story.append(Paragraph(
        "The most striking outlier is W80+ at 1.27x, meaning the BQ standard is only 27% "
        "slower than Yoko Nakano's extraordinary 4:11:45 world record. At the other extreme, "
        "W35-39 sits at 1.62x, making it the most lenient bracket relative to its reference. "
        "This 0.35x gap (from 1.27 to 1.62) represents the core inconsistency in women's standards.",
        styles['Body']))

    story.append(Paragraph("4.2 Framework 2: Top-Three Records", styles['SubHead']))
    story.append(Paragraph(
        "Dampening single-record outliers by averaging the estimated top three performances per "
        "bracket shifts the median multiplier to 1.44x but does not substantially reduce "
        "women's CV (7.3% vs 6.6%). This tells us the inconsistency is not solely driven by "
        "individual outlier records; structural gaps in older women's brackets persist even with "
        "a more conservative reference.",
        styles['Body']))

    story.append(Paragraph("4.3 Framework 3: Age-Graded Scoring", styles['SubHead']))
    story.append(Paragraph(
        "Under WMA age grading, the median age-graded percentage required to qualify for Boston "
        "is 67.9%. Men's brackets average 68.3% (CV = 4.0%), women's 69.0% (CV = 7.8%). "
        "Welch t-test: t = 0.42, p = 0.68, again showing no significant mean-level gender "
        "difference. The age-graded framework reveals something the WR framework obscures: "
        "older brackets (75-79, 80+) are substantially harder than they appear, because the WMA "
        "factors expect steeper performance decline than the BQ standards allow for.",
        styles['Body']))

    # Figure 3
    fig3_path = os.path.join(FIG_DIR, 'fig3_cv_comparison.png')
    if os.path.exists(fig3_path):
        story.append(Image(fig3_path, width=5.5*inch, height=3.3*inch))
        story.append(Paragraph(
            "Figure 2. Coefficient of variation across frameworks. Women's brackets are "
            "3-4x more variable than men's under all three frameworks.",
            styles['Caption']))

    # Figure 4
    fig4_path = os.path.join(FIG_DIR, 'fig4_fair_vs_actual.png')
    if os.path.exists(fig4_path):
        story.append(Image(fig4_path, width=6.2*inch, height=3.1*inch))
        story.append(Paragraph(
            "Figure 3. Difference between current BQ and 'fair' BQ (in minutes). Positive = "
            "current BQ is lenient; negative = current BQ is strict.",
            styles['Caption']))

    # ── 5. Cross-Framework Findings ────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("5. Cross-Framework Findings", styles['SectionHead']))
    story.append(Paragraph(
        "Three findings are robust across all frameworks:", styles['Body']))
    story.append(Paragraph(
        "<b>Finding 1: No mean-level gender bias.</b> Under all frameworks, the average "
        "difficulty for men and women is statistically indistinguishable (p > 0.68). The BAA "
        "appears to have calibrated the average correctly across genders.",
        styles['Body']))
    story.append(Paragraph(
        "<b>Finding 2: Women's brackets are 3-4x more variable.</b> CV for men ranges 1.9-4.0% "
        "across frameworks; for women, 6.6-7.8%. This is driven by a combination of outlier "
        "reference records and the structural challenge of calibrating standards for brackets "
        "with thinner competition depth.",
        styles['Body']))
    story.append(Paragraph(
        "<b>Finding 3: W80+ is the most miscalibrated bracket.</b> Under the WR framework, the "
        "current BQ is 57 minutes too strict relative to what a uniform multiplier would suggest. "
        "Under age-grading, it is 56 minutes too strict. This is the single most defensible "
        "critique: regardless of which framework you prefer, the W80+ standard appears too hard.",
        styles['Body']))

    # Figure 5
    fig5_path = os.path.join(FIG_DIR, 'fig5_heatmap.png')
    if os.path.exists(fig5_path):
        story.append(Image(fig5_path, width=6.2*inch, height=2.8*inch))
        story.append(Paragraph(
            "Figure 4. Deviation heatmaps. Red cells = bracket is harder than average; "
            "green = easier than average. W80+ is consistently red across all frameworks.",
            styles['Caption']))

    # ── 6. Historical Comparison ───────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("6. Historical Comparison: Did 2026 Tightening Help Fairness?", styles['SectionHead']))
    story.append(Paragraph(
        "The 2026 race introduced the largest single tightening of qualifying times since 1990: "
        "five minutes across the board for athletes under 60. While framed as a response to "
        "record demand, the change also raises the question of whether the tightening improved "
        "fairness across brackets or simply shifted everything uniformly.",
        styles['Body']))

    fig7_path = os.path.join(FIG_DIR, 'fig7_historical.png')
    if os.path.exists(fig7_path):
        story.append(Image(fig7_path, width=6.2*inch, height=2.5*inch))
        story.append(Paragraph(
            "Figure 5. 2020-2025 standards (light bars) vs 2026 standards (dark bars), "
            "expressed as WR multipliers. The tightening was uniform within each gender, "
            "leaving the relative bracket structure unchanged.",
            styles['Caption']))

    story.append(Paragraph(
        "The tightening lowered every under-60 multiplier by roughly the same proportion, leaving "
        "the relative <i>structure</i> of the standards unchanged. The 60+ brackets were untouched. "
        "Women's CV in 2020-2025 (approximately 6.8%) and 2026 (6.6%) are essentially identical. "
        "The 2026 changes responded to demand, not to inter-bracket fairness.",
        styles['Body']))
    story.append(Paragraph(
        "An unintended consequence: by tightening only under-60 standards, the BAA implicitly "
        "steepened the gap between the 55-59 and 60-64 brackets. The men's gap grew from 15 to "
        "20 minutes. This 'birthday cliff' is now larger than it was previously.",
        styles['Body']))

    # ── 7. Sensitivity Analysis ────────────────────────────────
    story.append(Paragraph("7. Sensitivity Analysis", styles['SectionHead']))
    story.append(Paragraph(
        "We stress-tested the main variance-gap finding against three alternative scenarios:",
        styles['Body']))
    story.append(Paragraph(
        "<b>Scenario A:</b> Drop W80+ entirely (remove the largest outlier).<br/>"
        "<b>Scenario B:</b> Use Sinead Diver's W40 2:21:34 as the W40-44 reference.<br/>"
        "<b>Scenario C:</b> Use Tigst Assefa's women-only WR (2:15:41) for W18-34 instead of the "
        "mixed-race record.",
        styles['Body']))

    fig8_path = os.path.join(FIG_DIR, 'fig8_sensitivity.png')
    if os.path.exists(fig8_path):
        story.append(Image(fig8_path, width=6.0*inch, height=3.3*inch))
        story.append(Paragraph(
            "Figure 6. Sensitivity analysis. Men's CV stays at 1.9% across all scenarios; "
            "women's CV drops from 6.6% to 4.5% only when removing W80+, demonstrating that "
            "the variance gap is robust to alternative reference records.",
            styles['Caption']))

    story.append(Paragraph(
        "Results: men's CV stays at 1.9% across every scenario, confirming there is no "
        "comparable outlier in the men's data. Women's CV drops to 4.5% only when W80+ is "
        "removed entirely. Alternative record choices (Diver, Assefa) shift women's CV by less "
        "than 0.3 percentage points. The variance gap is genuine and not an artifact of which "
        "records we anchor to.",
        styles['Body']))

    # ── 8. Complete Bracket Table ──────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("8. Complete Bracket-by-Bracket Table", styles['SectionHead']))
    story.append(Paragraph(
        "All 22 brackets, with each framework's headline metric and the suggested fair BQ under "
        "Frameworks 1 and 3. Negative differences in earlier figures correspond to current BQs "
        "that are stricter than the fair value; positive differences indicate the current BQ "
        "is more lenient.",
        styles['Body']))

    # Load results and build the table
    results = pd.read_csv(RESULTS_PATH)

    header = ['Age', 'Sex', 'Current BQ', 'WR Mult', 'Top-3 Mult', 'AG %', 'Fair BQ (WR)', 'Fair BQ (AG)']
    table_data = [header]
    for _, r in results.iterrows():
        table_data.append([
            r['age_group'],
            r['gender'],
            r['bq_time_hhmmss'],
            f"{r['wr_multiplier']:.3f}",
            f"{r['top3_multiplier']:.3f}",
            f"{r['ag_pct']:.1f}",
            r['fair_bq_hhmmss'],
            r['fair_bq_ag_hhmmss'],
        ])

    bracket_table = Table(
        table_data,
        colWidths=[0.55*inch, 0.4*inch, 0.85*inch, 0.7*inch, 0.75*inch, 0.55*inch, 0.95*inch, 0.95*inch],
        repeatRows=1,
    )

    # Build row backgrounds: alternate light shading, color-code gender column
    row_styles = []
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            row_styles.append(('BACKGROUND', (0, i), (-1, i), HexColor('#F7F5F0')))
        # Gender color
        gender = table_data[i][1]
        gender_color = HexColor('#2563EB') if gender == 'M' else HexColor('#C0392B')
        row_styles.append(('TEXTCOLOR', (1, i), (1, i), gender_color))
        row_styles.append(('FONTNAME', (1, i), (1, i), 'Times-Bold'))

    bracket_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        # Body
        ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 1), (-1, -1), 9.5),
        ('ALIGN', (0, 1), (1, -1), 'CENTER'),         # Age, Gender centered
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),         # Numbers right-aligned
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        # Borders
        ('LINEBELOW', (0, 0), (-1, 0), 1, HexColor('#1a1a2e')),
        ('LINEBELOW', (0, -1), (-1, -1), 0.5, HexColor('#CCCCCC')),
        ('BOX', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
    ] + row_styles))

    story.append(bracket_table)
    story.append(Paragraph(
        "Table 1. Complete bracket-by-bracket results. M brackets shown in blue, W in red. "
        "Current BQ is the official 2026 BAA standard. WR Mult and Top-3 Mult are dimensionless "
        "ratios (BQ time / reference time). AG % is the age-graded percentage. Fair BQ columns "
        "show what each framework would suggest if the median multiplier (1.50) or median "
        "AG % (67.9%) were applied uniformly across all brackets.",
        styles['Caption']))

    # ── 9. Limitations ─────────────────────────────────────────
    story.append(Paragraph("9. Limitations", styles['SectionHead']))
    story.append(Paragraph(
        "<b>Single-record dependence.</b> Frameworks 1 and 2 anchor to individual performances. "
        "Thin brackets (especially older women's) are dominated by one extraordinary athlete. "
        "Framework 3 mitigates this by using population-level age factors, but those factors "
        "are themselves derived from historical data that may underrepresent certain demographics.",
        styles['Body']))
    story.append(Paragraph(
        "<b>Under-35 bracket ambiguity.</b> No separate masters records exist below age 35, so "
        "the 18-34 and 35-39 brackets use the open world record as reference. This artificially "
        "compresses the multiplier for 35-39, making it appear easier than it is.",
        styles['Body']))
    story.append(Paragraph(
        "<b>Top-3 estimation.</b> Framework 2 estimates second and third performances using fixed "
        "depth factors rather than verified data. This is transparent but approximate.",
        styles['Body']))
    story.append(Paragraph(
        "<b>Fairness is multi-dimensional.</b> These frameworks measure difficulty-parity only. "
        "The BAA may legitimately optimize for other objectives: field-size diversity, historical "
        "continuity, participation encouragement, or competitive depth. A standard that looks "
        "'unfair' under one lens may be optimal under another.",
        styles['Body']))
    story.append(Paragraph(
        "<b>Statistical power.</b> With n = 11 per gender, formal tests are underpowered. "
        "The Levene test at p = 0.036 crosses the 0.05 threshold but should be interpreted "
        "cautiously given the small sample.",
        styles['Body']))

    # ── 10. Conclusion ─────────────────────────────────────────
    story.append(Paragraph("10. Conclusion", styles['SectionHead']))
    story.append(Paragraph(
        "The BAA's qualifying standards are, on average, well-calibrated across genders. The "
        "criticism that 'Boston is unfair to women' does not survive statistical testing under "
        "any of the three frameworks examined here. What does emerge is a variance problem: "
        "women's brackets are significantly less consistent than men's, and the W80+ bracket "
        "is a genuine outlier regardless of framework.",
        styles['Body']))
    story.append(Paragraph(
        "The choice of fairness framework matters. World records are transparent but outlier-sensitive. "
        "Top-three averages are more robust but require estimation. Age-graded scoring is the most "
        "empirically grounded but hides its assumptions inside the WMA factor tables. No single "
        "framework is definitively correct. The value of this analysis lies in showing what each "
        "reveals and letting the reader judge which trade-offs matter most.",
        styles['Body']))
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "Full code, data, and reproducibility instructions available at: "
        "github.com/lyhjeremy/boston-bq-fairness",
        styles['SmallNote']))

    # Build
    doc.build(story)
    print(f"  PDF saved: {OUTPUT_PATH}")


if __name__ == '__main__':
    build_pdf()
