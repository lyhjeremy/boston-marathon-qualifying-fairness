---
title: "I tried to figure out if Boston Marathon's qualifying times are fair"
description: "Three frameworks, 22 brackets, one stubborn outlier. What I found when I did the math."
author: "Jeremy Lee"
date: 2026-05-19
tags: [boston-marathon, running, data-analysis, python, side-project]
---

## The argument that never ends

Spend long enough in running forums and you will see the same fight more than once.

Someone posts the Boston Marathon qualifying times. Someone replies that the women's standards are too easy. A third person says they are too hard once you account for age. A fourth links an old spreadsheet that seems to prove both. Half the thread then argues about whether the 60+ standards are generous or patronizing, and the other half about whether non-binary runners belong in the comparison. It never gets settled.

I had the same questions. I have run 14 marathons, with a best of 2:48 at Berlin, and I have looked at the qualifying table more often than I would admit. The argument always stalls at the same point: the standards feel unfair to someone, nobody can prove it, and the BAA has never said how it came up with the numbers.

That last part is true. The Boston Athletic Association has published qualifying times since 1980 and has never disclosed how it sets them: no formula, no spreadsheet, no stated goal. The press releases mention "careful analysis of results data" and nothing more.

So I worked through the data myself.

## What I was trying to answer

I had to define "fair" before I could measure it. The definition I used: **does every age-gender bracket require the same proportional effort to qualify?** Two 32-year-old men running the same time are plainly held to the same standard. The harder question is whether a 32-year-old man's standard is the same fraction of his potential as a 67-year-old woman's is of hers.

That is partly a values question, so I did not pick one answer. I used three frameworks:

- **Framework 1, world-record multiplier.** Each bracket's standard as a multiple of that bracket's world record. The 2:55:00 standard for men 18-34 is 1.46 times Sabastian Sawe's 1:59:30. If every bracket landed on the same multiplier, you would call the system fair.
- **Framework 2, top-three records.** The same idea against an average of the top three performances instead of the single record. One exceptional athlete can skew a whole bracket, so this checks whether one record drives the result. The second and third marks are estimated.
- **Framework 3, WMA age grading.** World Masters Athletics publishes age factors built from population-level data, so no single record anchors a bracket. This asks what fraction of your age-specific potential Boston demands.

I expected the three to disagree. What I wanted to know was whether they agreed on anything.

## What I found

The short version: **the BAA has the averages right and the consistency wrong.**

![Bar chart of each of the 22 brackets' qualifying standard divided by its world record. Men's bars sit between 1.43 and 1.53 around the dashed median at 1.50. Women's bars range from 1.27 at W80+ to 1.62 at W35-39.](outputs/figures/fig1_wr_multiplier.png)
*Framework 1. The dashed line is the median (1.50 times the record). The blue men's bars stay close to it; the red women's bars do not.*

Every men's bracket, from 18-34 to 80+, sits between 1.43 and 1.53. The women's bars run from 1.27 (W80+) to 1.62 (W35-39), a spread of 0.35 against the men's 0.10.

A Welch t-test on the gender means gives p = 0.81: the average difficulty for men and women is statistically indistinguishable, so the BAA calibrated that correctly. Levene's test for equal variance gives p = 0.036. The men's brackets line up with each other, and the women's scatter.

The coefficient of variation tells the same story under each framework:

![Grouped bar chart for the WR, top-three and age-graded frameworks. Men's bars are 1.9, 2.1 and 4.0 percent; women's are 6.6, 7.3 and 7.8 percent.](outputs/figures/fig3_cv_comparison.png)
*Coefficient of variation under each framework. Lower means more consistent across brackets.*

Under the two record-based frameworks the women's CV is about 3.5 times the men's; under age grading it is about twice. That surprised me. I had expected either a clean bias in the means or nothing at all, and instead found an inconsistency sitting under a balanced average.

## The outlier

When a result looks odd, the next question is whether one data point is doing the work.

So I dropped W80+ and re-ran everything. The men's CV stayed at 1.9%. The women's fell from 6.6% to 4.5%. **One bracket accounts for about a third of the women's spread.**

![Bar chart of four scenarios: baseline, drop W80+, stronger W40-44, women-only WR. Men's bars are 1.9 percent in each. Women's are 6.6, 4.5, 6.6 and 6.4 percent.](outputs/figures/fig8_sensitivity.png)
*Sensitivity analysis. Swapping in Sinead Diver's 2:21:34 or Tigst Assefa's women-only record barely changes the result. Removing W80+ cuts the women's CV by a third.*

The W80+ reference is Yoko Nakano's 4:11:45, run in Tokyo at 81. The W80+ standard of 5:20:00 is 1.27 times that record, so women over 80 have to finish within 27% of it to qualify. Every other bracket sits between 1.42 and 1.62 times its record. It is the strictest bracket in the table by a wide margin.

Under the world-record framework the W80+ standard is **57 minutes** too strict compared with where a uniform multiplier would put it. Under WMA age grading it is **56 minutes** too strict. The two frameworks disagree about plenty else and agree on this.

## The 2026 tightening left the spread in place

For 2026 the BAA cut five minutes from every standard under 60. It was the largest single tightening since 1990, framed as a response to record demand: 33,249 applications for about 24,000 places. I found nothing from the BAA on whether it changed the balance between brackets.

I had the data to check, so I rebuilt the 2020-2025 standards as multipliers and put them beside 2026.

![Two bar charts, men and women, comparing 2020-2025 multipliers (light) with 2026 (dark). Every under-60 bracket drops by a similar amount; the 60+ bars are unchanged.](outputs/figures/fig7_historical.png)
*Light bars are 2020-2025, dark bars 2026. The 60+ brackets did not change.*

The cut was the same within each gender, so the shape of the table stayed the same. Against the same records the women's CV was 7.3% under the 2020-2025 standards and 6.6% in 2026; the men's went from 1.8% to 1.9%. The inconsistency was there before 2026 and is still there.

One side effect: by tightening only the under-60 standards, the BAA made the step between 55-59 and 60-64 steeper. A 59-year-old man needed 3:35 and a 60-year-old 3:50, a 15-minute step. It is now 20 minutes.

## Where that leaves the argument

What I found does not line up with either side of the forum fight.

- "Boston is unfair to women on average." No. The means are balanced under every framework I tested.
- "Boston is unfair to women bracket to bracket." Yes. The women's standards vary much more than the men's under all three frameworks.
- "Women's qualifying is broken." Too strong. Much of the inconsistency comes from W80+ and from a few unusual reference records.
- "The BAA should adjust W80+." This one holds up. Every framework and every sensitivity run points at the same bracket.

If the BAA did one thing in response, it would be easing W80+ by 30 to 50 minutes. That would affect a few dozen women a year who already have to run close to record pace to qualify, and it would bring the standard into line with the rest of the table under every framework I tried.

## How the analysis works

It is one Python script (also available as a notebook) and four small CSV files. No build step and no API keys.

The four datasets:

- `bq_standards_2026.csv`: all 22 qualifying times, from baa.org.
- `world_records.csv`: open and masters marathon records per bracket, checked against World Athletics and the Wikipedia masters records list.
- `wma_age_factors.csv`: WMA 2023 marathon age factors, taken at each bracket's midpoint age.
- `field_size_2026.csv`: 24,362 accepted, 33,249 applied and the 4:34 cutoff, from BAA press releases.

The notebook runs in nine sections:

1. Load and merge the four datasets
2. Framework 1: world-record multiplier, Welch t-test and Levene's test
3. Framework 2: top-three averages with estimated depth factors
4. Framework 3: WMA age-graded percentages
5. Cross-framework comparison: CV charts, current-versus-fair gaps, deviation heatmaps
6. Historical comparison: the 2020-2025 standards against 2026
7. Sensitivity analysis: dropping W80+, substituting Diver's mark, substituting Assefa's women-only record
8. Main findings
9. Limitations and the summary table

Every figure in the report and on the web page comes from this code.

## Where I would push back on my own result

There are good reasons not to read too much into this.

**The frameworks only measure equal difficulty.** They say nothing about field-size diversity, continuity, who the race wants to welcome, or depth of competition, all of which a race director might reasonably care about. A standard that looks unfair under a world-record multiplier could be right for some other goal. I don't know what the BAA is aiming for, because it hasn't said.

**The sample is small.** Eleven brackets per gender. The Levene test clears 0.05, but it has little power, and I only ran it on the world-record framework. The variance gap holds up under every perturbation I tried, so I trust its direction more than its exact size.

**The brackets under 40 use the open record.** There is no separate masters record below 40, so 18-34 and 35-39 are both anchored to Sawe and Chepngetich. Chepngetich is serving a three-year ban, announced by the [Athletics Integrity Unit](https://www.athleticsintegrity.org/downloads/pdfs/other/Press-Release_Howman-Nobody-Above-the-Rules-%E2%80%93-AIU-Bans-Chepngetich-for-3-Years.pdf) on 23 October 2025, after a positive test for the diuretic hydrochlorothiazide on 14 March 2025; the AIU said her records from before that test stand while it looks into other material from her phone, and the [World Athletics all-time list](https://worldathletics.org/records/all-time-toplists/road-running/marathon/all/women/senior) still puts 2:09:56 first (checked 28 October 2026). That makes 35-39 look more lenient than it may be.

## What it doesn't cover

- **Non-binary runners.** I excluded them because the BAA says it doesn't yet have the data to set standards for the category. As that data grows, the analysis should include them.
- **Different bracket boundaries.** WMA factors change smoothly with age. Five-year brackets may be part of the problem.
- **The application process.** This treats the published standards as the variable of interest, but the 2026 cutoff that decided entry was 4:34 under BQ, set by the field cap. A simulation of how the cap interacts with the brackets would be its own project.
- **More history.** I compared 2026 with 2020-2025 only. Going back to the 1980 standards or the 2003 tightening would show whether the variance gap has always been this size.
- **An interactive version.** The natural form for this is a tool where you adjust a framework's parameters and watch the standards move.

The eight figures are generated by `src/analysis.py` and saved to `outputs/figures/` at 400 DPI. They are free to reuse with attribution to this project.
