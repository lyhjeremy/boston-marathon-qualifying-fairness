"""
Boston Marathon BQ Fairness Analysis — Three-Framework Approach
===============================================================
Author: Jeremy Lee (lyhjeremy)
Date: May 2026

Research question: Are Boston Marathon qualifying times equitable across
age and gender brackets? We examine this through three anchor frameworks:
  1. World Record Multiplier
  2. Top-3 Records (robustness check)
  3. WMA Age-Graded Scoring

Assumptions:
  - Focus on men (M) and women (W) only; non-binary excluded due to
    insufficient data (BAA itself notes this limitation).
  - 2026 Boston Marathon qualifying standards and field size as baseline.
  - BAA bracket structure: 18-34, 35-39, 40-44, ..., 75-79, 80+.
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
import os

warnings.filterwarnings('ignore')

# ── Plotting defaults ──────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': '#FAFAFA',
    'axes.edgecolor': '#CCCCCC',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.color': '#CCCCCC',
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'figure.dpi': 150,
    'savefig.dpi': 400,  # 400 DPI = extra-crisp print/retina quality
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.3,
})

PALETTE_M = '#2563EB'  # blue for men
PALETTE_W = '#DC2626'  # red for women
PALETTE_ALT = '#059669' # green for alternative

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'data')
OUTPUT_DIR = os.path.join(os.path.dirname(BASE_DIR), 'outputs', 'figures')
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ══════════════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════════════

def load_data():
    """Load and merge all datasets."""
    bq = pd.read_csv(os.path.join(DATA_DIR, 'bq_standards_2026.csv'))
    wr = pd.read_csv(os.path.join(DATA_DIR, 'world_records.csv'))
    wma = pd.read_csv(os.path.join(DATA_DIR, 'wma_age_factors.csv'))
    field = pd.read_csv(os.path.join(DATA_DIR, 'field_size_2026.csv'))

    # Merge BQ with WR
    df = bq.merge(wr[['age_group', 'gender', 'wr_time_seconds', 'athlete', 'year']],
                  on=['age_group', 'gender'], how='left')

    # Merge with WMA factors
    df = df.merge(wma[['age_group', 'gender', 'midpoint_age', 'wma_factor']],
                  on=['age_group', 'gender'], how='left')

    return df, field


def time_str(seconds):
    """Convert seconds to H:MM:SS string."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h}:{m:02d}:{s:02d}"


# ══════════════════════════════════════════════════════════════════
# FRAMEWORK 1: World Record Multiplier
# ══════════════════════════════════════════════════════════════════

def framework1_wr_multiplier(df):
    """
    For each bracket, compute:
        multiplier = bq_time / wr_time
    This tells us how many times the WR the BQ standard is.
    A fair system under this framework would have identical multipliers.
    """
    df = df.copy()
    df['wr_multiplier'] = df['bq_time_seconds'] / df['wr_time_seconds']
    df['pct_of_wr'] = (df['wr_time_seconds'] / df['bq_time_seconds']) * 100

    # Summary stats
    summary = {
        'mean_multiplier': df['wr_multiplier'].mean(),
        'median_multiplier': df['wr_multiplier'].median(),
        'std_multiplier': df['wr_multiplier'].std(),
        'cv_multiplier': df['wr_multiplier'].std() / df['wr_multiplier'].mean() * 100,
        'range': (df['wr_multiplier'].min(), df['wr_multiplier'].max()),
        'mean_pct_wr': df['pct_of_wr'].mean(),
    }

    # Gender breakdown
    for g in ['M', 'W']:
        sub = df[df['gender'] == g]
        summary[f'mean_mult_{g}'] = sub['wr_multiplier'].mean()
        summary[f'std_mult_{g}'] = sub['wr_multiplier'].std()
        summary[f'cv_mult_{g}'] = sub['wr_multiplier'].std() / sub['wr_multiplier'].mean() * 100

    # Welch t-test on gender multipliers
    m_vals = df[df['gender'] == 'M']['wr_multiplier']
    w_vals = df[df['gender'] == 'W']['wr_multiplier']
    t_stat, p_val = stats.ttest_ind(m_vals, w_vals, equal_var=False)
    summary['welch_t'] = t_stat
    summary['welch_p'] = p_val

    # Levene's test for equal variance
    lev_stat, lev_p = stats.levene(m_vals, w_vals)
    summary['levene_w'] = lev_stat
    summary['levene_p'] = lev_p

    # Compute "fair" BQ times at median multiplier
    target = df['wr_multiplier'].median()
    df['fair_bq_seconds'] = df['wr_time_seconds'] * target
    df['fair_bq_hhmmss'] = df['fair_bq_seconds'].apply(time_str)
    df['diff_from_fair'] = df['bq_time_seconds'] - df['fair_bq_seconds']

    return df, summary


# ══════════════════════════════════════════════════════════════════
# FRAMEWORK 2: Top-3 Records (Robustness)
# ══════════════════════════════════════════════════════════════════

def framework2_top3(df):
    """
    Use the average of top-3 known performances per bracket instead of
    single WR. This dampens outlier records.

    Note: For many brackets, especially older women's brackets,
    comprehensive top-3 data is not publicly available. We use the
    WR as #1 and estimate #2 and #3 based on typical depth patterns
    observed in available data (London 2026 masters results, etc.).
    This is clearly flagged as an estimation.
    """
    df = df.copy()

    # Depth factors: how much slower are #2 and #3 vs WR typically?
    # Based on observed patterns from London 2026 masters results:
    # M40: WR 2:04:15, #2 ~2:08, #3 ~2:10 → ~2% and ~5% slower
    # Older brackets tend to have less depth (wider gaps)
    # We use conservative estimates: #2 = WR * 1.03, #3 = WR * 1.06
    # For thin brackets (70+, 80+): #2 = WR * 1.05, #3 = WR * 1.10

    thin_brackets = ['70-74', '75-79', '80+']

    depth_factors = []
    for _, row in df.iterrows():
        if row['age_group'] in thin_brackets:
            factors = [1.0, 1.05, 1.10]
        else:
            factors = [1.0, 1.03, 1.06]
        avg_top3 = row['wr_time_seconds'] * np.mean(factors)
        depth_factors.append(avg_top3)

    df['top3_avg_seconds'] = depth_factors
    df['top3_multiplier'] = df['bq_time_seconds'] / df['top3_avg_seconds']
    df['top3_pct'] = (df['top3_avg_seconds'] / df['bq_time_seconds']) * 100

    # Fair BQ at median top-3 multiplier
    target = df['top3_multiplier'].median()
    df['fair_bq_top3'] = df['top3_avg_seconds'] * target
    df['fair_bq_top3_hhmmss'] = df['fair_bq_top3'].apply(time_str)
    df['diff_from_fair_top3'] = df['bq_time_seconds'] - df['fair_bq_top3']

    summary = {
        'mean_multiplier': df['top3_multiplier'].mean(),
        'median_multiplier': df['top3_multiplier'].median(),
        'std_multiplier': df['top3_multiplier'].std(),
        'cv_multiplier': df['top3_multiplier'].std() / df['top3_multiplier'].mean() * 100,
    }

    for g in ['M', 'W']:
        sub = df[df['gender'] == g]
        summary[f'cv_mult_{g}'] = sub['top3_multiplier'].std() / sub['top3_multiplier'].mean() * 100

    return df, summary


# ══════════════════════════════════════════════════════════════════
# FRAMEWORK 3: WMA Age-Graded Scoring
# ══════════════════════════════════════════════════════════════════

def framework3_age_graded(df):
    """
    Use WMA age factors to compute age-adjusted equivalent times,
    then compute what percentage of the age-adjusted standard each
    BQ represents.

    Age-graded time = actual_time * wma_factor
    Age-graded % = (age_standard / actual_time) * factor * 100
                 = (open_wr / bq_time) * factor * 100

    A fair system under this framework would have every bracket
    requiring the same age-graded percentage to qualify.
    """
    df = df.copy()

    # Age-graded percentage for BQ standard
    # AG% = (open_standard * wma_factor) / bq_time * 100
    # This represents: what fraction of "expected peak" does the BQ demand?
    open_wr_m = 7170  # Sawe 1:59:30
    open_wr_w = 7796  # Chepngetich 2:09:56

    ag_pct = []
    for _, row in df.iterrows():
        wr = open_wr_m if row['gender'] == 'M' else open_wr_w
        # Age-adjusted standard = open_wr / wma_factor
        # (because slower times at older ages need larger divisor)
        age_adjusted_standard = wr / row['wma_factor']
        # BQ as percentage of age-adjusted standard
        pct = (age_adjusted_standard / row['bq_time_seconds']) * 100
        ag_pct.append(pct)

    df['ag_pct'] = ag_pct

    # Fair BQ at median AG%
    target = df['ag_pct'].median()

    fair_bq = []
    for _, row in df.iterrows():
        wr = open_wr_m if row['gender'] == 'M' else open_wr_w
        age_adjusted_standard = wr / row['wma_factor']
        fair_time = age_adjusted_standard / (target / 100)
        fair_bq.append(fair_time)

    df['fair_bq_ag'] = fair_bq
    df['fair_bq_ag_hhmmss'] = df['fair_bq_ag'].apply(time_str)
    df['diff_from_fair_ag'] = df['bq_time_seconds'] - df['fair_bq_ag']

    summary = {
        'mean_ag_pct': df['ag_pct'].mean(),
        'median_ag_pct': df['ag_pct'].median(),
        'std_ag_pct': df['ag_pct'].std(),
        'cv_ag_pct': df['ag_pct'].std() / df['ag_pct'].mean() * 100,
    }

    for g in ['M', 'W']:
        sub = df[df['gender'] == g]
        summary[f'mean_ag_{g}'] = sub['ag_pct'].mean()
        summary[f'std_ag_{g}'] = sub['ag_pct'].std()
        summary[f'cv_ag_{g}'] = sub['ag_pct'].std() / sub['ag_pct'].mean() * 100

    # Welch t-test
    m_vals = df[df['gender'] == 'M']['ag_pct']
    w_vals = df[df['gender'] == 'W']['ag_pct']
    t_stat, p_val = stats.ttest_ind(m_vals, w_vals, equal_var=False)
    summary['welch_t'] = t_stat
    summary['welch_p'] = p_val

    return df, summary


# ══════════════════════════════════════════════════════════════════
# DEEPER ANALYSIS LAYERS
# ══════════════════════════════════════════════════════════════════

def historical_evolution_analysis(df):
    """
    How have BQ standards evolved? We compare 2026 to two earlier eras:
      - 2003-2012 era: pre-tightening
      - 2020-2025 era: previous standards (5 min slower for under-60)
    This shows whether the gender-variance gap has always existed.
    """
    # 2020-2025 BQ standards (5 min slower than 2026 for under-60)
    historical = {
        # (age_group, gender): seconds
        ('18-34', 'M'): 10800,  # 3:00
        ('18-34', 'W'): 12600,  # 3:30
        ('35-39', 'M'): 11100,  # 3:05
        ('35-39', 'W'): 12900,  # 3:35
        ('40-44', 'M'): 11400,  # 3:10
        ('40-44', 'W'): 13200,  # 3:40
        ('45-49', 'M'): 12000,  # 3:20
        ('45-49', 'W'): 13800,  # 3:50
        ('50-54', 'M'): 12300,  # 3:25
        ('50-54', 'W'): 14100,  # 3:55
        ('55-59', 'M'): 12900,  # 3:35
        ('55-59', 'W'): 14700,  # 4:05
        ('60-64', 'M'): 13800,  # 3:50  (unchanged - 60+)
        ('60-64', 'W'): 15600,  # 4:20
        ('65-69', 'M'): 14700,  # 4:05
        ('65-69', 'W'): 16500,  # 4:35
        ('70-74', 'M'): 15600,  # 4:20
        ('70-74', 'W'): 17400,  # 4:50
        ('75-79', 'M'): 16500,  # 4:35
        ('75-79', 'W'): 18300,  # 5:05
        ('80+', 'M'): 17400,    # 4:50
        ('80+', 'W'): 19200,    # 5:20
    }

    df = df.copy()
    df['bq_2020_seconds'] = df.apply(
        lambda r: historical.get((r['age_group'], r['gender']), r['bq_time_seconds']), axis=1
    )
    df['bq_2020_hhmmss'] = df['bq_2020_seconds'].apply(time_str)
    df['mult_2020'] = df['bq_2020_seconds'] / df['wr_time_seconds']
    df['tightening_seconds'] = df['bq_2020_seconds'] - df['bq_time_seconds']

    return df


def field_size_impact_analysis(df, field):
    """
    Estimate the field-size impact of moving to a 'fair' standard.

    Key assumption: each bracket's number of qualifiers grows roughly
    in proportion to how much easier (or harder) the new standard is.
    We use a Riegel-style time-to-effort sensitivity: a 1% time change
    roughly corresponds to ~3-5% change in number of qualifiers (people
    cluster around the standard).
    """
    df = df.copy()
    # Pct change in BQ time under WR framework
    df['pct_change_wr'] = (df['fair_bq_seconds'] - df['bq_time_seconds']) / df['bq_time_seconds'] * 100
    df['pct_change_ag'] = (df['fair_bq_ag'] - df['bq_time_seconds']) / df['bq_time_seconds'] * 100

    # Estimated qualifier-pool elasticity: ~4x sensitivity
    # (1% slower BQ → ~4% more qualifiers; rough Riegel-style heuristic)
    ELASTICITY = 4.0
    df['est_qualifier_change_wr_pct'] = df['pct_change_wr'] * ELASTICITY
    df['est_qualifier_change_ag_pct'] = df['pct_change_ag'] * ELASTICITY

    return df


def sensitivity_analysis(df):
    """
    Test how robust the WR-multiplier conclusion is to alternative
    assumptions. We re-compute CV under three perturbations:
      A. Drop W80+ (the biggest outlier)
      B. Use Sinead Diver's 2:21:34 for W40-44 (proxy for stronger record)
      C. Use Tigst Assefa's women-only WR (2:15:41) for women's 18-34
    """
    base_m_cv = df[df['gender'] == 'M']['wr_multiplier'].std() / df[df['gender'] == 'M']['wr_multiplier'].mean() * 100
    base_w_cv = df[df['gender'] == 'W']['wr_multiplier'].std() / df[df['gender'] == 'W']['wr_multiplier'].mean() * 100

    results = {
        'baseline': {'m_cv': base_m_cv, 'w_cv': base_w_cv}
    }

    # A. Drop W80+
    df_a = df[~((df['age_group'] == '80+') & (df['gender'] == 'W'))].copy()
    results['drop_W80'] = {
        'm_cv': df_a[df_a['gender'] == 'M']['wr_multiplier'].std() / df_a[df_a['gender'] == 'M']['wr_multiplier'].mean() * 100,
        'w_cv': df_a[df_a['gender'] == 'W']['wr_multiplier'].std() / df_a[df_a['gender'] == 'W']['wr_multiplier'].mean() * 100,
    }

    # B. Use Diver's W40 2:21:34 as W40-44 reference
    df_b = df.copy()
    mask = (df_b['age_group'] == '40-44') & (df_b['gender'] == 'W')
    df_b.loc[mask, 'wr_time_seconds'] = 8494  # Diver 2:21:34
    df_b.loc[mask, 'wr_multiplier'] = df_b.loc[mask, 'bq_time_seconds'] / df_b.loc[mask, 'wr_time_seconds']
    results['stronger_W40'] = {
        'm_cv': df_b[df_b['gender'] == 'M']['wr_multiplier'].std() / df_b[df_b['gender'] == 'M']['wr_multiplier'].mean() * 100,
        'w_cv': df_b[df_b['gender'] == 'W']['wr_multiplier'].std() / df_b[df_b['gender'] == 'W']['wr_multiplier'].mean() * 100,
    }

    # C. Use women-only WR (Assefa 2:15:41 = 8141 sec) for W18-34
    df_c = df.copy()
    mask = (df_c['age_group'] == '18-34') & (df_c['gender'] == 'W')
    df_c.loc[mask, 'wr_time_seconds'] = 8141  # Assefa women-only
    df_c.loc[mask, 'wr_multiplier'] = df_c.loc[mask, 'bq_time_seconds'] / df_c.loc[mask, 'wr_time_seconds']
    results['women_only_W18'] = {
        'm_cv': df_c[df_c['gender'] == 'M']['wr_multiplier'].std() / df_c[df_c['gender'] == 'M']['wr_multiplier'].mean() * 100,
        'w_cv': df_c[df_c['gender'] == 'W']['wr_multiplier'].std() / df_c[df_c['gender'] == 'W']['wr_multiplier'].mean() * 100,
    }

    return results


# ══════════════════════════════════════════════════════════════════
# VISUALIZATIONS
# ══════════════════════════════════════════════════════════════════

def plot_fig1_wr_multiplier(df):
    """Hero chart: WR multiplier by bracket, colored by gender."""
    fig, ax = plt.subplots(figsize=(14, 7))

    age_groups = df['age_group'].unique()
    x = np.arange(len(age_groups))
    width = 0.35

    men = df[df['gender'] == 'M'].set_index('age_group').loc[age_groups]
    women = df[df['gender'] == 'W'].set_index('age_group').loc[age_groups]

    bars_m = ax.bar(x - width/2, men['wr_multiplier'], width,
                    color=PALETTE_M, alpha=0.85, label='Men', edgecolor='white', linewidth=0.5)
    bars_w = ax.bar(x + width/2, women['wr_multiplier'], width,
                    color=PALETTE_W, alpha=0.85, label='Women', edgecolor='white', linewidth=0.5)

    # Reference line at median
    median = df['wr_multiplier'].median()
    ax.axhline(y=median, color='#374151', linestyle='--', alpha=0.7, linewidth=1.5,
               label=f'Median: {median:.2f}x')

    # Add value labels
    for bar in bars_m:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., h + 0.01,
                f'{h:.2f}', ha='center', va='bottom', fontsize=8, color=PALETTE_M, fontweight='bold')
    for bar in bars_w:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., h + 0.01,
                f'{h:.2f}', ha='center', va='bottom', fontsize=8, color=PALETTE_W, fontweight='bold')

    ax.set_xlabel('Age Group', fontsize=12, fontweight='bold')
    ax.set_ylabel('BQ Time / World Record (multiplier)', fontsize=12, fontweight='bold')
    ax.set_title('Framework 1: How Many Times the World Record Is Each BQ Standard?',
                 fontsize=15, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(age_groups, rotation=45, ha='right')
    ax.legend(loc='upper left', framealpha=0.9, fontsize=10)
    ax.set_ylim(bottom=1.0)

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig1_wr_multiplier.png'))
    plt.close(fig)
    print("  ✓ fig1_wr_multiplier.png")


def plot_fig2_framework_comparison(df):
    """Compare all three frameworks' spread by gender."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    frameworks = [
        ('wr_multiplier', 'Framework 1:\nWR Multiplier', 'x WR'),
        ('top3_multiplier', 'Framework 2:\nTop-3 Avg Multiplier', 'x Top-3'),
        ('ag_pct', 'Framework 3:\nAge-Graded %', '% of AG standard'),
    ]

    for ax, (col, title, ylabel) in zip(axes, frameworks):
        for g, color, label in [('M', PALETTE_M, 'Men'), ('W', PALETTE_W, 'Women')]:
            sub = df[df['gender'] == g]
            ax.scatter(sub['age_group'], sub[col], color=color, s=80,
                      alpha=0.8, label=label, zorder=3, edgecolors='white', linewidth=0.5)
            ax.plot(sub['age_group'], sub[col], color=color, alpha=0.4, linewidth=1.5)

        median = df[col].median()
        ax.axhline(y=median, color='#374151', linestyle='--', alpha=0.5, linewidth=1)

        ax.set_title(title, fontsize=13, fontweight='bold')
        ax.set_ylabel(ylabel, fontsize=10)
        ax.tick_params(axis='x', rotation=45)
        ax.legend(fontsize=9)

    fig.suptitle('Three Frameworks Compared: How Consistent Are BQ Standards?',
                 fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig2_framework_comparison.png'))
    plt.close(fig)
    print("  ✓ fig2_framework_comparison.png")


def plot_fig3_cv_comparison(df):
    """Bar chart comparing coefficient of variation across frameworks and genders."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Calculate CVs
    data = {}
    for g in ['M', 'W']:
        sub = df[df['gender'] == g]
        for col, label in [('wr_multiplier', 'WR'), ('top3_multiplier', 'Top-3'), ('ag_pct', 'Age-Graded')]:
            cv = sub[col].std() / sub[col].mean() * 100
            data[(label, g)] = cv

    frameworks = ['WR', 'Top-3', 'Age-Graded']
    x = np.arange(len(frameworks))
    width = 0.35

    m_cvs = [data[(f, 'M')] for f in frameworks]
    w_cvs = [data[(f, 'W')] for f in frameworks]

    ax.bar(x - width/2, m_cvs, width, color=PALETTE_M, alpha=0.85, label='Men', edgecolor='white')
    ax.bar(x + width/2, w_cvs, width, color=PALETTE_W, alpha=0.85, label='Women', edgecolor='white')

    # Value labels
    for i, (m, w) in enumerate(zip(m_cvs, w_cvs)):
        ax.text(i - width/2, m + 0.2, f'{m:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold', color=PALETTE_M)
        ax.text(i + width/2, w + 0.2, f'{w:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold', color=PALETTE_W)

    ax.set_xlabel('Framework', fontsize=12, fontweight='bold')
    ax.set_ylabel('Coefficient of Variation (%)', fontsize=12, fontweight='bold')
    ax.set_title('Spread of BQ Difficulty Across Brackets\n(Lower = More Consistent)',
                 fontsize=14, fontweight='bold', pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(frameworks, fontsize=11)
    ax.legend(fontsize=10)
    ax.set_ylim(bottom=0)

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig3_cv_comparison.png'))
    plt.close(fig)
    print("  ✓ fig3_cv_comparison.png")


def plot_fig4_fair_vs_actual(df):
    """Show the gap between current BQ and 'fair' BQ under each framework."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 7))

    diff_cols = [
        ('diff_from_fair', 'Framework 1: WR'),
        ('diff_from_fair_top3', 'Framework 2: Top-3'),
        ('diff_from_fair_ag', 'Framework 3: Age-Graded'),
    ]

    for ax, (col, title) in zip(axes, diff_cols):
        age_groups = df['age_group'].unique()
        x = np.arange(len(age_groups))
        width = 0.35

        men = df[df['gender'] == 'M'].set_index('age_group').loc[age_groups]
        women = df[df['gender'] == 'W'].set_index('age_group').loc[age_groups]

        # Convert to minutes for readability
        ax.bar(x - width/2, men[col] / 60, width, color=PALETTE_M, alpha=0.85, label='Men', edgecolor='white')
        ax.bar(x + width/2, women[col] / 60, width, color=PALETTE_W, alpha=0.85, label='Women', edgecolor='white')

        ax.axhline(y=0, color='#374151', linewidth=1.5, alpha=0.8)
        ax.set_title(title, fontsize=13, fontweight='bold')
        ax.set_ylabel('Current BQ − Fair BQ (minutes)', fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(age_groups, rotation=45, ha='right', fontsize=8)
        ax.legend(fontsize=9)

    fig.suptitle('How Far Are Current BQ Standards from "Fair"?\n(Positive = current BQ is too lenient, Negative = too strict)',
                 fontsize=15, fontweight='bold', y=1.04)
    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig4_fair_vs_actual.png'))
    plt.close(fig)
    print("  ✓ fig4_fair_vs_actual.png")


def plot_fig5_heatmap(df):
    """Deviation heatmap across all frameworks."""
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))

    for ax, col, title, fmt in [
        (axes[0], 'wr_multiplier', 'WR Multiplier', '.2f'),
        (axes[1], 'top3_multiplier', 'Top-3 Multiplier', '.2f'),
        (axes[2], 'ag_pct', 'Age-Graded %', '.1f'),
    ]:
        pivot = df.pivot(index='age_group', columns='gender', values=col)
        pivot = pivot[['M', 'W']]

        # Z-score for coloring
        overall_mean = df[col].mean()
        overall_std = df[col].std()
        pivot_z = (pivot - overall_mean) / overall_std

        sns.heatmap(pivot_z, annot=pivot, fmt=fmt, cmap='RdYlGn_r',
                   center=0, linewidths=1, linecolor='white',
                   cbar_kws={'label': 'Z-score (deviation from mean)'},
                   ax=ax)
        ax.set_title(title, fontsize=13, fontweight='bold')
        ax.set_ylabel('')

    fig.suptitle('Deviation Heatmaps: Which Brackets Are Outliers Under Each Framework?',
                 fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig5_heatmap.png'))
    plt.close(fig)
    print("  ✓ fig5_heatmap.png")


def plot_fig6_alternative_bq(df):
    """Show alternative BQ times under each framework."""
    fig, ax = plt.subplots(figsize=(14, 8))

    age_groups = df['age_group'].unique()
    x = np.arange(len(age_groups))

    for g, color, ls in [('M', PALETTE_M, '-'), ('W', PALETTE_W, '-')]:
        sub = df[df['gender'] == g].set_index('age_group').loc[age_groups]

        # Current BQ
        ax.plot(x, sub['bq_time_seconds'] / 60, color=color, linewidth=2.5,
                marker='o', markersize=8, label=f'Current BQ ({g})', linestyle=ls)

        # Fair WR
        ax.plot(x, sub['fair_bq_seconds'] / 60, color=color, linewidth=1.5,
                marker='s', markersize=5, label=f'Fair BQ - WR ({g})', linestyle='--', alpha=0.7)

        # Fair AG
        ax.plot(x, sub['fair_bq_ag'] / 60, color=color, linewidth=1.5,
                marker='^', markersize=5, label=f'Fair BQ - AG ({g})', linestyle=':', alpha=0.7)

    ax.set_xlabel('Age Group', fontsize=12, fontweight='bold')
    ax.set_ylabel('Qualifying Time (minutes)', fontsize=12, fontweight='bold')
    ax.set_title('Current vs "Fair" BQ Times Under Different Frameworks',
                 fontsize=15, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(age_groups, rotation=45, ha='right')
    ax.legend(loc='upper left', fontsize=9, ncol=2, framealpha=0.9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: time_str(v * 60)))

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig6_alternative_bq.png'))
    plt.close(fig)
    print("  ✓ fig6_alternative_bq.png")


def plot_fig7_historical(df):
    """Compare 2020-2025 BQ multipliers to 2026 — did tightening help?"""
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    age_groups = df['age_group'].unique()
    x = np.arange(len(age_groups))
    width = 0.35

    for ax, g, color in [(axes[0], 'M', PALETTE_M), (axes[1], 'W', PALETTE_W)]:
        sub = df[df['gender'] == g].set_index('age_group').loc[age_groups]

        ax.bar(x - width/2, sub['mult_2020'], width, color=color, alpha=0.4,
               label='2020-2025 standard', edgecolor='white', linewidth=0.5)
        ax.bar(x + width/2, sub['wr_multiplier'], width, color=color, alpha=0.9,
               label='2026 standard', edgecolor='white', linewidth=0.5)

        median_2026 = df['wr_multiplier'].median()
        ax.axhline(y=median_2026, color='#374151', linestyle='--', alpha=0.6, linewidth=1,
                   label=f'2026 median: {median_2026:.2f}x')

        ax.set_title(f'{"Men" if g == "M" else "Women"}: Did 2026 Tightening Change Fairness?',
                     fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(age_groups, rotation=45, ha='right', fontsize=9)
        ax.set_ylabel('WR Multiplier')
        ax.legend(fontsize=8, loc='lower right')
        ax.set_ylim(1.15, 1.85)

    fig.suptitle('Historical Comparison: 2020-2025 vs 2026 BQ Standards',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig7_historical.png'))
    plt.close(fig)
    print("  ✓ fig7_historical.png")


def plot_fig8_sensitivity(sensitivity):
    """Show CV under different sensitivity scenarios."""
    fig, ax = plt.subplots(figsize=(11, 6))

    scenarios = ['baseline', 'drop_W80', 'stronger_W40', 'women_only_W18']
    labels = ['Baseline\n(all data)', 'Drop W80+\n(remove outlier)',
              'Stronger W40-44\n(Diver 2:21:34)', 'Women-only WR\n(Assefa 2:15:41)']

    m_cvs = [sensitivity[s]['m_cv'] for s in scenarios]
    w_cvs = [sensitivity[s]['w_cv'] for s in scenarios]

    x = np.arange(len(scenarios))
    width = 0.35

    ax.bar(x - width/2, m_cvs, width, color=PALETTE_M, alpha=0.85, label='Men', edgecolor='white')
    ax.bar(x + width/2, w_cvs, width, color=PALETTE_W, alpha=0.85, label='Women', edgecolor='white')

    for i, (m, w) in enumerate(zip(m_cvs, w_cvs)):
        ax.text(i - width/2, m + 0.15, f'{m:.1f}%', ha='center', va='bottom',
                fontsize=10, fontweight='bold', color=PALETTE_M)
        ax.text(i + width/2, w + 0.15, f'{w:.1f}%', ha='center', va='bottom',
                fontsize=10, fontweight='bold', color=PALETTE_W)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel('Coefficient of Variation (%)', fontsize=11, fontweight='bold')
    ax.set_title('Sensitivity Analysis: How Robust Is the Variance Gap?',
                 fontsize=14, fontweight='bold', pad=10)
    ax.legend(fontsize=10, loc='upper right')
    ax.set_ylim(0, max(w_cvs) * 1.2)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig8_sensitivity.png'))
    plt.close(fig)
    print("  ✓ fig8_sensitivity.png")


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("Boston BQ Fairness Analysis — Three Frameworks")
    print("=" * 60)

    # Load data
    print("\n[1/6] Loading data...")
    df, field = load_data()
    print(f"  Loaded {len(df)} bracket records")
    print(f"  2026 field: {field[field['metric']=='accepted_qualifiers']['value'].values[0]:,} accepted")

    # Framework 1
    print("\n[2/6] Framework 1: World Record Multiplier...")
    df, f1_summary = framework1_wr_multiplier(df)
    print(f"  Mean multiplier:  {f1_summary['mean_multiplier']:.3f}x")
    print(f"  Median multiplier: {f1_summary['median_multiplier']:.3f}x")
    print(f"  CV overall: {f1_summary['cv_multiplier']:.2f}%")
    print(f"  CV men:     {f1_summary['cv_mult_M']:.2f}%")
    print(f"  CV women:   {f1_summary['cv_mult_W']:.2f}%")
    print(f"  Welch t = {f1_summary['welch_t']:.3f}, p = {f1_summary['welch_p']:.3f}")
    print(f"  Levene W = {f1_summary['levene_w']:.3f}, p = {f1_summary['levene_p']:.3f}")

    # Framework 2
    print("\n[3/6] Framework 2: Top-3 Records...")
    df, f2_summary = framework2_top3(df)
    print(f"  Mean multiplier:  {f2_summary['mean_multiplier']:.3f}x")
    print(f"  CV overall: {f2_summary['cv_multiplier']:.2f}%")
    print(f"  CV men:     {f2_summary['cv_mult_M']:.2f}%")
    print(f"  CV women:   {f2_summary['cv_mult_W']:.2f}%")

    # Framework 3
    print("\n[4/6] Framework 3: Age-Graded Scoring...")
    df, f3_summary = framework3_age_graded(df)
    print(f"  Mean AG%:  {f3_summary['mean_ag_pct']:.2f}%")
    print(f"  Median AG%: {f3_summary['median_ag_pct']:.2f}%")
    print(f"  CV overall: {f3_summary['cv_ag_pct']:.2f}%")
    print(f"  CV men:     {f3_summary['cv_ag_M']:.2f}%")
    print(f"  CV women:   {f3_summary['cv_ag_W']:.2f}%")
    print(f"  Welch t = {f3_summary['welch_t']:.3f}, p = {f3_summary['welch_p']:.3f}")

    # Generate figures
    print("\n[5/8] Generating core figures...")
    plot_fig1_wr_multiplier(df)
    plot_fig2_framework_comparison(df)
    plot_fig3_cv_comparison(df)
    plot_fig4_fair_vs_actual(df)
    plot_fig5_heatmap(df)
    plot_fig6_alternative_bq(df)

    # Deeper analysis layers
    print("\n[6/8] Historical evolution analysis...")
    df = historical_evolution_analysis(df)
    plot_fig7_historical(df)

    print("\n[7/8] Sensitivity analysis...")
    sensitivity = sensitivity_analysis(df)
    plot_fig8_sensitivity(sensitivity)
    print("  Sensitivity results:")
    for scenario, vals in sensitivity.items():
        print(f"    {scenario:20s}  M CV: {vals['m_cv']:.2f}%   W CV: {vals['w_cv']:.2f}%")

    # Field-size impact
    df = field_size_impact_analysis(df, field)

    # Save results table
    print("\n[8/8] Saving results...")
    results_cols = [
        'age_group', 'gender', 'bq_time_hhmmss', 'wr_time_seconds',
        'wr_multiplier', 'pct_of_wr', 'top3_multiplier', 'top3_pct',
        'ag_pct', 'fair_bq_hhmmss', 'fair_bq_top3_hhmmss', 'fair_bq_ag_hhmmss',
        'diff_from_fair', 'diff_from_fair_top3', 'diff_from_fair_ag',
        'bq_2020_hhmmss', 'mult_2020', 'tightening_seconds',
        'est_qualifier_change_wr_pct', 'est_qualifier_change_ag_pct',
    ]
    output_path = os.path.join(os.path.dirname(BASE_DIR), 'outputs', 'analysis_results.csv')
    df[results_cols].to_csv(output_path, index=False)
    print(f"  ✓ analysis_results.csv")

    # Print comparison table
    print("\n" + "=" * 80)
    print("COMPARISON TABLE: Current BQ vs Fair BQ (all three frameworks)")
    print("=" * 80)
    for _, row in df.iterrows():
        diff1 = row['diff_from_fair'] / 60
        diff3 = row['diff_from_fair_ag'] / 60
        sign1 = '+' if diff1 > 0 else ''
        sign3 = '+' if diff3 > 0 else ''
        print(f"  {row['age_group']:>5} {row['gender']}  BQ={row['bq_time_hhmmss']:>8}  "
              f"Fair(WR)={row['fair_bq_hhmmss']:>8} ({sign1}{diff1:>+6.1f}m)  "
              f"Fair(AG)={row['fair_bq_ag_hhmmss']:>8} ({sign3}{diff3:>+6.1f}m)")

    print("\n✅ Analysis complete. All outputs in outputs/")
    return df, f1_summary, f2_summary, f3_summary, sensitivity


if __name__ == '__main__':
    df, f1, f2, f3, sens = main()
