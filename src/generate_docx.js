// Generate the academic DOCX report mirroring the PDF content.
// Builds an 8-section Word document with embedded figures, styled headings,
// methodology callouts, findings, sensitivity tables, and limitations.

const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, AlignmentType, HeadingLevel, LevelFormat, BorderStyle,
  WidthType, ShadingType, PageBreak, PageOrientation
} = require('docx');

const PROJECT_DIR = path.resolve(__dirname, '..');
const FIG_DIR = path.join(PROJECT_DIR, 'outputs', 'figures');
const RESULTS_PATH = path.join(PROJECT_DIR, 'outputs', 'analysis_results.csv');
const OUT_PATH = path.join(PROJECT_DIR, 'reports', 'Boston_BQ_Three_Frameworks_Report.docx');

// Read results CSV → array of objects (very small file, simple parser is fine)
function loadResults() {
  const text = fs.readFileSync(RESULTS_PATH, 'utf-8').trim();
  const lines = text.split('\n');
  const headers = lines[0].split(',');
  return lines.slice(1).map(line => {
    const cells = line.split(',');
    const obj = {};
    headers.forEach((h, i) => { obj[h] = cells[i]; });
    return obj;
  });
}

// ─── Helpers ──────────────────────────────────────────────────────────
const COLOR = {
  text: '1A1A2E',
  soft: '555555',
  muted: '888888',
  accent: 'C0392B',
  border: 'CCCCCC',
  shadeHead: '1A1A2E',
  shadeAlt: 'F5F2EC',
};

// 12pt = 24 half-points (docx uses half-points for run size)
function p(text, opts = {}) {
  return new Paragraph({
    alignment: opts.align || AlignmentType.JUSTIFIED,
    spacing: { after: opts.after !== undefined ? opts.after : 120, line: 320 },
    children: [new TextRun({
      text,
      font: 'Calibri',
      size: opts.size || 22,  // 11pt body default
      bold: opts.bold || false,
      italics: opts.italics || false,
      color: opts.color || COLOR.text,
    })],
  });
}

// Paragraph with multiple inline runs (supports bold/italic phrases)
function pRich(runs, opts = {}) {
  return new Paragraph({
    alignment: opts.align || AlignmentType.JUSTIFIED,
    spacing: { after: opts.after !== undefined ? opts.after : 120, line: 320 },
    children: runs.map(r => {
      if (typeof r === 'string') {
        return new TextRun({ text: r, font: 'Calibri', size: 22, color: COLOR.text });
      }
      return new TextRun({
        text: r.text,
        font: 'Calibri',
        size: r.size || 22,
        bold: !!r.bold,
        italics: !!r.italics,
        color: r.color || COLOR.text,
      });
    }),
  });
}

function spacer(height = 200) {
  return new Paragraph({ spacing: { after: height }, children: [new TextRun('')] });
}

function imageBlock(filename, widthPx, heightPx, caption) {
  const data = fs.readFileSync(path.join(FIG_DIR, filename));
  const blocks = [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 160, after: 80 },
      children: [new ImageRun({
        type: 'png',
        data,
        transformation: { width: widthPx, height: heightPx },
        altText: { title: filename, description: caption, name: filename },
      })],
    }),
  ];
  if (caption) {
    blocks.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 240, line: 280 },
      children: [new TextRun({
        text: caption,
        font: 'Calibri',
        size: 18,         // 9pt
        italics: true,
        color: COLOR.muted,
      })],
    }));
  }
  return blocks;
}

// ─── Document content ─────────────────────────────────────────────────

const children = [];

// Title block
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 0, after: 80 },
  children: [new TextRun({
    text: 'Are Boston Marathon Qualifying Times Fair?',
    font: 'Georgia',
    size: 44,       // 22pt
    bold: true,
    color: COLOR.text,
  })],
}));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 80 },
  children: [new TextRun({
    text: 'A Three-Framework Comparative Analysis of BQ Standards Across Age and Gender',
    font: 'Georgia',
    size: 26,       // 13pt
    italics: true,
    color: COLOR.soft,
  })],
}));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 360 },
  children: [new TextRun({
    text: 'Jeremy Lee  |  May 2026  |  github.com/lyhjeremy/boston-bq-fairness',
    font: 'Georgia',
    size: 22,
    italics: true,
    color: COLOR.soft,
  })],
}));

// Abstract
children.push(new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 240, after: 160 },
  children: [new TextRun({ text: 'Abstract', font: 'Georgia', size: 30, bold: true, color: COLOR.text })],
}));
children.push(p(
  'The Boston Athletic Association sets qualifying times that vary by age and gender, but has never publicly disclosed the methodology behind these standards. This report examines whether current BQ times represent equal difficulty across all 22 age-gender brackets by applying three independent frameworks: (1) a world-record multiplier, (2) a top-three-records robustness check, and (3) WMA age-graded scoring. All three frameworks reveal the same structural pattern: men\u2019s brackets are remarkably consistent (CV 1.9\u20134.0%), while women\u2019s brackets show 3\u20134 times more variation (CV 6.6\u20137.8%), driven primarily by outlier reference records in younger and oldest brackets. A Welch t-test on gender means returns p = 0.81 under the WR framework, indicating no significant mean-level difference. The W80+ bracket stands out as the most miscalibrated under all frameworks. We present alternative BQ tables under each framework and discuss limitations.'
));

// ── 1. Introduction
children.push(new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 360, after: 160 },
  children: [new TextRun({ text: '1. Introduction', font: 'Georgia', size: 30, bold: true, color: COLOR.text })],
}));
children.push(p('The Boston Marathon, first run in 1897, is the world\u2019s oldest annually contested marathon and one of only a handful of major marathons that requires a qualifying time for entry. The Boston Athletic Association (BAA) publishes qualifying standards across 11 age groups and two genders (plus a non-binary category adopted in recent years). For the 2026 race, the BAA tightened standards by five minutes for all athletes under 60, responding to record demand: 33,249 applications for roughly 24,000 qualifier spots.'));
children.push(p('Despite decades of adjustments, the BAA has never publicly explained the quantitative framework behind its qualifying times. Their rationale statements reference \u201Ccareful analysis of results data\u201D without specifying whether they optimize for equal difficulty, equal selectivity, field-size targets, or historical continuity. This creates a natural research question: are the qualifying times equitable across age and gender brackets?'));
children.push(p('We define \u201Cequitable\u201D operationally as: every bracket requires the same proportional effort relative to a shared anchor. The choice of anchor is itself a fairness decision, which is why we apply three different anchors and compare what each reveals.'));

// ── 2. Data
children.push(new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 360, after: 160 },
  children: [new TextRun({ text: '2. Data Sources', font: 'Georgia', size: 30, bold: true, color: COLOR.text })],
}));
children.push(p('2026 BAA qualifying standards were sourced directly from baa.org. Open marathon world records (men: Sabastian Sawe, 1:59:30, London 2026; women mixed: Ruth Chepngetich, 2:09:56, Chicago 2024) were verified against World Athletics. Masters records (M35 through W80+) were compiled from the Wikipedia list of masters world records in road running, cross-referenced with WMA ratified records. WMA 2023 age-grading factors were sourced from the official Appendix B tables. Field-size data (24,362 accepted qualifiers, 4:34 cutoff) from BAA press releases.'));
children.push(p('Scope: 22 brackets (11 age groups \u00D7 2 genders). Non-binary athletes (110 accepted in 2026) are excluded because the BAA itself notes insufficient data to determine appropriate time standards for this category.'));

// ── 3. Methodology
children.push(new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 360, after: 160 },
  children: [new TextRun({ text: '3. Methodology', font: 'Georgia', size: 30, bold: true, color: COLOR.text })],
}));

children.push(new Paragraph({
  heading: HeadingLevel.HEADING_2,
  spacing: { before: 200, after: 120 },
  children: [new TextRun({ text: '3.1 Framework 1: World Record Multiplier', font: 'Georgia', size: 24, bold: true, color: COLOR.text })],
}));
children.push(p('For each bracket, we compute: multiplier = BQ time / world record time. If the BAA aimed for uniform difficulty under this framework, every bracket would have the same multiplier. Deviations indicate brackets where the standard is relatively easier or harder than average. For brackets below age 40, the open world record is used as the reference since no separate masters record exists. This is an acknowledged limitation: it makes the 35-39 bracket appear artificially easy.'));

children.push(new Paragraph({
  heading: HeadingLevel.HEADING_2,
  spacing: { before: 200, after: 120 },
  children: [new TextRun({ text: '3.2 Framework 2: Top-Three Records', font: 'Georgia', size: 24, bold: true, color: COLOR.text })],
}));
children.push(p('Single world records are inherently outlier-sensitive. To test robustness, we replace the single WR with an estimated average of the top three known performances per bracket. For brackets with rich competition depth (35-69), we estimate the second- and third-best times at 3% and 6% slower than the WR, based on observed patterns from London 2026 masters results. For thin brackets (70+, 80+), we use 5% and 10% gaps. This is clearly an approximation; we flag it throughout.'));

children.push(new Paragraph({
  heading: HeadingLevel.HEADING_2,
  spacing: { before: 200, after: 120 },
  children: [new TextRun({ text: '3.3 Framework 3: WMA Age-Graded Scoring', font: 'Georgia', size: 24, bold: true, color: COLOR.text })],
}));
children.push(p('World Masters Athletics publishes empirically derived age factors that represent the expected performance decline with age. We compute the age-adjusted standard for each bracket and ask: what fraction of their age-specific potential does each BQ standard demand? The formula: age-graded % = (open WR / BQ time) \u00D7 (1 / WMA factor) \u00D7 100. Unlike Frameworks 1 and 2, this approach accounts for the biological expectation at each age rather than anchoring to a single exceptional performance.'));

// Page break before Results
children.push(new Paragraph({ children: [new PageBreak()] }));

// ── 4. Results
children.push(new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 0, after: 160 },
  children: [new TextRun({ text: '4. Results', font: 'Georgia', size: 30, bold: true, color: COLOR.text })],
}));

children.push(new Paragraph({
  heading: HeadingLevel.HEADING_2,
  spacing: { before: 200, after: 120 },
  children: [new TextRun({ text: '4.1 Framework 1: World Record Multiplier', font: 'Georgia', size: 24, bold: true, color: COLOR.text })],
}));
children.push(p('The median multiplier across all 22 brackets is 1.50x, meaning the typical BQ standard is 50% slower than the world record for that bracket. Men\u2019s brackets cluster tightly (CV = 1.9%, range 1.43-1.53x), while women\u2019s brackets spread three times wider (CV = 6.6%, range 1.27-1.62x). A Welch t-test on gender means returns t = -0.25, p = 0.81, indicating no significant mean-level difference between genders. However, Levene\u2019s test for variance equality returns W = 5.04, p = 0.036, confirming the visual impression that women\u2019s brackets are significantly less consistent.'));

// Figure 1
imageBlock('fig1_wr_multiplier.png', 600, 300,
  'Figure 1. BQ time as a multiple of world record, by age-gender bracket. Dashed line = median (1.50x). Women\u2019s bars show much wider spread.'
).forEach(b => children.push(b));

children.push(p('The most striking outlier is W80+ at 1.27x, meaning the BQ standard is only 27% slower than Yoko Nakano\u2019s extraordinary 4:11:45 world record. At the other extreme, W35-39 sits at 1.62x, making it the most lenient bracket relative to its reference. This 0.35x gap (from 1.27 to 1.62) represents the core inconsistency in women\u2019s standards.'));

children.push(new Paragraph({
  heading: HeadingLevel.HEADING_2,
  spacing: { before: 200, after: 120 },
  children: [new TextRun({ text: '4.2 Framework 2: Top-Three Records', font: 'Georgia', size: 24, bold: true, color: COLOR.text })],
}));
children.push(p('Dampening single-record outliers by averaging the estimated top three performances per bracket shifts the median multiplier to 1.44x but does not substantially reduce women\u2019s CV (7.3% vs 6.6%). This tells us the inconsistency is not solely driven by individual outlier records; structural gaps in older women\u2019s brackets persist even with a more conservative reference.'));

children.push(new Paragraph({
  heading: HeadingLevel.HEADING_2,
  spacing: { before: 200, after: 120 },
  children: [new TextRun({ text: '4.3 Framework 3: Age-Graded Scoring', font: 'Georgia', size: 24, bold: true, color: COLOR.text })],
}));
children.push(p('Under WMA age grading, the median age-graded percentage required to qualify for Boston is 67.9%. Men\u2019s brackets average 68.3% (CV = 4.0%), women\u2019s 69.0% (CV = 7.8%). Welch t-test: t = 0.42, p = 0.68, again showing no significant mean-level gender difference. The age-graded framework reveals something the WR framework obscures: older brackets (75-79, 80+) are substantially harder than they appear, because the WMA factors expect steeper performance decline than the BQ standards allow for.'));

// Figure 2 (fig3 — CV comparison)
imageBlock('fig3_cv_comparison.png', 520, 312,
  'Figure 2. Coefficient of variation across frameworks. Women\u2019s brackets are 3-4x more variable than men\u2019s under all three frameworks.'
).forEach(b => children.push(b));

// Figure 3 (fig4 — Fair vs Actual)
imageBlock('fig4_fair_vs_actual.png', 600, 300,
  'Figure 3. Difference between current BQ and \u201Cfair\u201D BQ (in minutes). Positive = current BQ is lenient; negative = current BQ is strict.'
).forEach(b => children.push(b));

// Page break before Cross-Framework
children.push(new Paragraph({ children: [new PageBreak()] }));

// ── 5. Cross-Framework Findings
children.push(new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 0, after: 160 },
  children: [new TextRun({ text: '5. Cross-Framework Findings', font: 'Georgia', size: 30, bold: true, color: COLOR.text })],
}));
children.push(p('Three findings are robust across all frameworks:'));

children.push(pRich([
  { text: 'Finding 1: No mean-level gender bias. ', bold: true },
  'Under all frameworks, the average difficulty for men and women is statistically indistinguishable (p > 0.68). The BAA appears to have calibrated the average correctly across genders.',
]));
children.push(pRich([
  { text: 'Finding 2: Women\u2019s brackets are 3-4x more variable. ', bold: true },
  'CV for men ranges 1.9-4.0% across frameworks; for women, 6.6-7.8%. This is driven by a combination of outlier reference records and the structural challenge of calibrating standards for brackets with thinner competition depth.',
]));
children.push(pRich([
  { text: 'Finding 3: W80+ is the most miscalibrated bracket. ', bold: true },
  'Under the WR framework, the current BQ is 57 minutes too strict relative to what a uniform multiplier would suggest. Under age-grading, it is 56 minutes too strict. This is the single most defensible critique: regardless of which framework you prefer, the W80+ standard appears too hard.',
]));

// Figure 4 (fig5 — heatmap)
imageBlock('fig5_heatmap.png', 600, 270,
  'Figure 4. Deviation heatmaps. Red cells = bracket is harder than average; green = easier than average. W80+ is consistently red across all frameworks.'
).forEach(b => children.push(b));

// Page break before Historical
children.push(new Paragraph({ children: [new PageBreak()] }));

// ── 6. Historical Comparison
children.push(new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 0, after: 160 },
  children: [new TextRun({ text: '6. Historical Comparison: Did 2026 Tightening Help Fairness?', font: 'Georgia', size: 30, bold: true, color: COLOR.text })],
}));
children.push(p('The 2026 race introduced the largest single tightening of qualifying times since 1990: five minutes across the board for athletes under 60. While framed as a response to record demand, the change also raises the question of whether the tightening improved fairness across brackets or simply shifted everything uniformly.'));

// Figure 5 (fig7 historical)
imageBlock('fig7_historical.png', 600, 240,
  'Figure 5. 2020-2025 standards (light bars) vs 2026 standards (dark bars), expressed as WR multipliers. The tightening was uniform within each gender, leaving the relative bracket structure unchanged.'
).forEach(b => children.push(b));

children.push(p('The tightening lowered every under-60 multiplier by roughly the same proportion, leaving the relative structure of the standards unchanged. The 60+ brackets were untouched. Women\u2019s CV in 2020-2025 (approximately 6.8%) and 2026 (6.6%) are essentially identical. The 2026 changes responded to demand, not to inter-bracket fairness.'));
children.push(p('An unintended consequence: by tightening only under-60 standards, the BAA implicitly steepened the gap between the 55-59 and 60-64 brackets. The men\u2019s gap grew from 15 to 20 minutes. This \u201Cbirthday cliff\u201D is now larger than it was previously.'));

// ── 7. Sensitivity
children.push(new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 360, after: 160 },
  children: [new TextRun({ text: '7. Sensitivity Analysis', font: 'Georgia', size: 30, bold: true, color: COLOR.text })],
}));
children.push(p('We stress-tested the main variance-gap finding against three alternative scenarios:'));
children.push(pRich([
  { text: 'Scenario A: ', bold: true },
  'Drop W80+ entirely (remove the largest outlier).',
]));
children.push(pRich([
  { text: 'Scenario B: ', bold: true },
  'Use Sinead Diver\u2019s W40 2:21:34 as the W40-44 reference.',
]));
children.push(pRich([
  { text: 'Scenario C: ', bold: true },
  'Use Tigst Assefa\u2019s women-only WR (2:15:41) for W18-34 instead of the mixed-race record.',
]));

// Figure 6 (fig8 sensitivity)
imageBlock('fig8_sensitivity.png', 560, 300,
  'Figure 6. Sensitivity analysis. Men\u2019s CV stays at 1.9% across all scenarios; women\u2019s CV drops from 6.6% to 4.5% only when removing W80+, demonstrating that the variance gap is robust to alternative reference records.'
).forEach(b => children.push(b));

children.push(p('Results: men\u2019s CV stays at 1.9% across every scenario, confirming there is no comparable outlier in the men\u2019s data. Women\u2019s CV drops to 4.5% only when W80+ is removed entirely. Alternative record choices (Diver, Assefa) shift women\u2019s CV by less than 0.3 percentage points. The variance gap is genuine and not an artifact of which records we anchor to.'));

// ── 8. Complete Bracket Table ──────────────────────────────────────
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 0, after: 160 },
  children: [new TextRun({ text: '8. Complete Bracket-by-Bracket Table', font: 'Georgia', size: 30, bold: true, color: COLOR.text })],
}));
children.push(p('All 22 brackets, with each framework\u2019s headline metric and the suggested fair BQ under Frameworks 1 and 3. Negative differences in earlier figures correspond to current BQs that are stricter than the fair value; positive differences indicate the current BQ is more lenient.'));

// Helper to build a styled table cell
function tcell(text, opts = {}) {
  return new TableCell({
    width: { size: opts.width || 1200, type: WidthType.DXA },
    shading: opts.shading ? { type: ShadingType.CLEAR, fill: opts.shading } : undefined,
    margins: { top: 80, bottom: 80, left: 80, right: 80 },
    children: [new Paragraph({
      alignment: opts.align || AlignmentType.LEFT,
      spacing: { before: 0, after: 0 },
      children: [new TextRun({
        text,
        font: 'Calibri',
        size: opts.size || 18,    // 9pt
        bold: !!opts.bold,
        color: opts.color || COLOR.text,
      })],
    })],
  });
}

// Build the table
const results = loadResults();

// Column widths (DXA, 1440 = 1 inch). Total ~9000 = 6.25" fits portrait letter w/ 1" margins
const colW = [800, 600, 1100, 950, 1050, 800, 1200, 1200];

const headerCells = ['Age', 'Sex', 'Current BQ', 'WR Mult', 'Top-3 Mult', 'AG %', 'Fair BQ (WR)', 'Fair BQ (AG)'].map(
  (h, i) => tcell(h, { width: colW[i], shading: '1A1A2E', color: 'FFFFFF', bold: true, align: AlignmentType.CENTER })
);
const tableRows = [new TableRow({ children: headerCells, tableHeader: true })];

results.forEach((r, idx) => {
  const altShade = (idx % 2 === 0) ? undefined : 'F5F2EC';
  const genderColor = (r.gender === 'M') ? '2563EB' : 'C0392B';
  const wrMult = parseFloat(r.wr_multiplier).toFixed(3);
  const top3Mult = parseFloat(r.top3_multiplier).toFixed(3);
  const agPct = parseFloat(r.ag_pct).toFixed(1);
  tableRows.push(new TableRow({
    children: [
      tcell(r.age_group, { width: colW[0], shading: altShade, align: AlignmentType.CENTER }),
      tcell(r.gender, { width: colW[1], shading: altShade, align: AlignmentType.CENTER, bold: true, color: genderColor }),
      tcell(r.bq_time_hhmmss, { width: colW[2], shading: altShade, align: AlignmentType.RIGHT }),
      tcell(wrMult, { width: colW[3], shading: altShade, align: AlignmentType.RIGHT }),
      tcell(top3Mult, { width: colW[4], shading: altShade, align: AlignmentType.RIGHT }),
      tcell(agPct, { width: colW[5], shading: altShade, align: AlignmentType.RIGHT }),
      tcell(r.fair_bq_hhmmss, { width: colW[6], shading: altShade, align: AlignmentType.RIGHT }),
      tcell(r.fair_bq_ag_hhmmss, { width: colW[7], shading: altShade, align: AlignmentType.RIGHT }),
    ],
  }));
});

const bracketTable = new Table({
  rows: tableRows,
  width: { size: 9000, type: WidthType.DXA },
  borders: {
    top:    { style: BorderStyle.SINGLE, size: 4, color: '1A1A2E' },
    bottom: { style: BorderStyle.SINGLE, size: 4, color: '1A1A2E' },
    left:   { style: BorderStyle.SINGLE, size: 2, color: 'CCCCCC' },
    right:  { style: BorderStyle.SINGLE, size: 2, color: 'CCCCCC' },
    insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: 'E5E7EB' },
    insideVertical:   { style: BorderStyle.SINGLE, size: 2, color: 'E5E7EB' },
  },
});

children.push(bracketTable);
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 100, after: 240, line: 280 },
  children: [new TextRun({
    text: 'Table 1. Complete bracket-by-bracket results. M brackets shown in blue, W in red. Current BQ is the official 2026 BAA standard. WR Mult and Top-3 Mult are dimensionless ratios (BQ time / reference time). AG % is the age-graded percentage. Fair BQ columns show what each framework would suggest if the median multiplier (1.50) or median AG % (67.9%) were applied uniformly across all brackets.',
    font: 'Calibri',
    size: 18,
    italics: true,
    color: COLOR.muted,
  })],
}));

// ── 9. Limitations
children.push(new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 360, after: 160 },
  children: [new TextRun({ text: '9. Limitations', font: 'Georgia', size: 30, bold: true, color: COLOR.text })],
}));
children.push(pRich([
  { text: 'Single-record dependence. ', bold: true },
  'Frameworks 1 and 2 anchor to individual performances. Thin brackets (especially older women\u2019s) are dominated by one extraordinary athlete. Framework 3 mitigates this by using population-level age factors, but those factors are themselves derived from historical data that may underrepresent certain demographics.',
]));
children.push(pRich([
  { text: 'Under-35 bracket ambiguity. ', bold: true },
  'No separate masters records exist below age 35, so the 18-34 and 35-39 brackets use the open world record as reference. This artificially compresses the multiplier for 35-39, making it appear easier than it is.',
]));
children.push(pRich([
  { text: 'Top-3 estimation. ', bold: true },
  'Framework 2 estimates second and third performances using fixed depth factors rather than verified data. This is transparent but approximate.',
]));
children.push(pRich([
  { text: 'Fairness is multi-dimensional. ', bold: true },
  'These frameworks measure difficulty-parity only. The BAA may legitimately optimize for other objectives: field-size diversity, historical continuity, participation encouragement, or competitive depth. A standard that looks \u201Cunfair\u201D under one lens may be optimal under another.',
]));
children.push(pRich([
  { text: 'Statistical power. ', bold: true },
  'With n = 11 per gender, formal tests are underpowered. The Levene test at p = 0.036 crosses the 0.05 threshold but should be interpreted cautiously given the small sample.',
]));

// ── 10. Conclusion
children.push(new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 360, after: 160 },
  children: [new TextRun({ text: '10. Conclusion', font: 'Georgia', size: 30, bold: true, color: COLOR.text })],
}));
children.push(p('The BAA\u2019s qualifying standards are, on average, well-calibrated across genders. The criticism that \u201CBoston is unfair to women\u201D does not survive statistical testing under any of the three frameworks examined here. What does emerge is a variance problem: women\u2019s brackets are significantly less consistent than men\u2019s, and the W80+ bracket is a genuine outlier regardless of framework.'));
children.push(p('The choice of fairness framework matters. World records are transparent but outlier-sensitive. Top-three averages are more robust but require estimation. Age-graded scoring is the most empirically grounded but hides its assumptions inside the WMA factor tables. No single framework is definitively correct. The value of this analysis lies in showing what each reveals and letting the reader judge which trade-offs matter most.'));

children.push(spacer(240));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 200 },
  children: [new TextRun({
    text: 'Full code, data, and reproducibility instructions available at: github.com/lyhjeremy/boston-bq-fairness',
    font: 'Calibri',
    size: 18,    // 9pt
    italics: true,
    color: COLOR.muted,
  })],
}));

// ─── Document setup ───────────────────────────────────────────────────
const doc = new Document({
  creator: 'Jeremy Lee',
  title: 'Are Boston Marathon Qualifying Times Fair?',
  description: 'A three-framework comparative analysis of BQ standards across age and gender.',
  styles: {
    default: {
      document: { run: { font: 'Calibri', size: 22 } }, // 11pt default
    },
    paragraphStyles: [
      {
        id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 30, bold: true, font: 'Georgia', color: COLOR.text },
        paragraph: { spacing: { before: 320, after: 160 }, outlineLevel: 0 },
      },
      {
        id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 24, bold: true, font: 'Georgia', color: COLOR.text },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 1 },
      },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 }, // US Letter
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      },
    },
    children,
  }],
});

Packer.toBuffer(doc).then(buffer => {
  fs.mkdirSync(path.dirname(OUT_PATH), { recursive: true });
  fs.writeFileSync(OUT_PATH, buffer);
  console.log(`DOCX saved: ${OUT_PATH}`);
  console.log(`File size: ${(fs.statSync(OUT_PATH).size / 1024).toFixed(0)} KB`);
}).catch(err => {
  console.error('Error generating DOCX:', err);
  process.exit(1);
});
