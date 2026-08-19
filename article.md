---
title: "I tried to figure out if Boston Marathon's qualifying times are fair"
description: "Three frameworks, 22 brackets, one stubborn outlier. What I found when I actually did the math."
author: "Jeremy Lee"
date: 2026-05-19
tags: [boston-marathon, running, data-analysis, python, side-project]
---

![A pack of marathon runners stretched across a city street at golden hour](./images/hero-marathon-runners.jpg)
*[HERO IMAGE: marathoners at sunrise, see "Image credits" at the end for free-licensed sources]*

## The argument that wouldn't die

If you spend enough time in running forums, you will eventually watch the same fight play out.

Someone posts the Boston Marathon qualifying times. Someone else replies that the women's standards are too easy. A third person says no, actually, the women's standards are too *hard* once you account for age. A fourth links to a 2014 spreadsheet that claims to prove it both ways. Half the thread ends up arguing about whether the 60+ brackets are an act of generosity or condescension, and the other half is arguing about whether non-binary runners should be included at all. Nobody ever lands the plane.

I had the same questions myself, mostly because I knew people who'd narrowly missed BQ and were trying to figure out if they'd been held to a harder standard than someone else. The conversations always trailed off the same way:

> *"I think it's unfair, but I can't prove it. The BAA's never said how they came up with the numbers."*

That's the thing. The Boston Athletic Association has been publishing qualifying times since 1980 and has never disclosed the methodology. Not the spreadsheet, not the formula, not the philosophy. The press releases reference "careful analysis of results data," which tells you nothing.

So I sat down with the data myself.

## What I was actually trying to answer

I had to define "fair" before I could measure it. The version I went with is: **does every age-gender bracket require the same proportional effort to qualify?** Two 32-year-old men running the same time are obviously held to the same standard. But should a 32-year-old man's standard be the *same fraction of his potential* as a 67-year-old woman's standard is of hers?

That's a values question, and reasonable people will land in different places. So I refused to pick one answer and applied three different frameworks instead:

- **Framework 1 (World Record Multiplier):** A bracket's BQ as a multiple of that bracket's world record. The 2:55:00 standard for men 18-34 is 1.46× Sabastian Sawe's 1:59:30. If every bracket landed at the same multiplier, you'd call the system fair.

- **Framework 2 (Top-3 Records):** Same idea, but anchored to the average of the top three known performances instead of the single WR. World records are outliers by definition, one extraordinary athlete can skew a whole bracket, so this is a robustness check.

- **Framework 3 (WMA Age-Graded Scoring):** Uses World Masters Athletics' published age factors, which are derived from population-level performance data instead of individual records. Asks: what fraction of your *age-specific biological potential* does Boston demand?

Each framework would give a different answer. The interesting question wasn't which one was "right". It was whether the three of them agreed about anything.

## What I found

The simplest version is: **the BAA has the averages right and the consistency wrong.**

![A bar chart showing the BQ standard divided by the world record for each of 22 age-gender brackets. Men's bars sit tightly between 1.43 and 1.53 across the dashed median line at 1.50. Women's bars are all over the place, with W35-39 at 1.62 and W80+ way below at 1.27](./images/fig1-wr-multiplier.png)
*Framework 1 in one chart. The dashed line is the median (1.50× WR). The blue men's bars hug it. The red women's bars don't.*

That image is most of the article. Notice the blue bars. Every men's bracket from 18-34 all the way up to 80+ sits within a thin band between 1.43 and 1.53. Now look at the red bars. W35-39 sits at 1.62. W80+ at 1.27. That's a spread of 0.35, more than three times the men's spread of 0.10.

A Welch t-test on the gender means returns p = 0.81, meaning the *averages* for men and women are statistically indistinguishable. The BAA calibrated those correctly. But a Levene test for equal variance returns p = 0.036, meaning the consistency is statistically different. The men's brackets are tightly aligned with each other. The women's brackets are not.

This held up under every framework I threw at it. Coefficient of variation tells the same story three different ways:

![A bar chart with three groups labeled WR, Top-3, and Age-Graded. Inside each group, a short blue bar for men (1.9%, 2.1%, 4.0%) sits next to a tall red bar for women (6.6%, 7.3%, 7.8%)](./images/fig2-cv-comparison.png)
*Coefficient of variation under each framework. Lower bars = more consistent across brackets. Women's brackets are 3-4× more variable than men's no matter how you measure.*

That ratio, women 3-4× more variable than men, is the thing that surprised me. I'd expected to find either a clean bias in the means (women's standards harder/easier than men's) or no story at all. What I found instead was structural inconsistency hiding underneath a perfectly balanced average.

## The outlier you can't ignore

When something is statistically weird, the obvious next question is: is it weird everywhere, or is one data point doing all the work?

So I dropped the W80+ bracket and re-ran everything. The men's CV didn't move (1.9% → 1.9%). The women's CV dropped from 6.6% to 4.5%. **One bracket, W80+, accounts for roughly a third of the entire women's variance.**

![A sensitivity analysis bar chart with four scenarios across the x-axis: Baseline, Drop W80+, Stronger W40-44, Women-only WR. Men's blue bars all show 1.9%. Women's red bars show 6.6%, 4.5%, 6.6%, 6.4%](./images/fig3-sensitivity.png)
*Sensitivity analysis. The variance gap is robust to alternative reference records, substituting Sinead Diver's W40 marathon or Tigst Assefa's women-only WR barely moves the needle. But removing W80+ entirely cuts women's CV by a third.*

The W80+ bracket is in a strange position. Its world record (Yoko Nakano, 4:11:45) is an extraordinary performance by an exceptional athlete, the kind of record that gets set once and stands for a decade. The BAA's W80+ standard of 5:20:00 is 1.27× that WR, meaning W80+ women need to come within 27% of a once-in-a-generation performance to qualify. Every other bracket sits between 1.42× and 1.62×. By a mile, this is the strictest bracket in the entire table.

Under the WR framework, the W80+ standard is **57 minutes too strict** compared to where it would land if it were calibrated like every other bracket. Under WMA age-grading, it's **56 minutes too strict**. The two frameworks disagree about almost everything else, but they agree about this. There's no defensible reading of the data where the W80+ standard is in the right place.

## The 2026 tightening didn't fix anything

For the 2026 race, the BAA dropped every standard for runners under 60 by five minutes flat. It was the largest single tightening since 1990, and it was framed as a response to record demand: 33,249 applications for ~24,000 spots. The press release talked about "raising the bar." Nobody at the BAA, as far as I can tell, talked about whether it changed the fairness picture across brackets.

I had the data to check. So I rebuilt the 2020-2025 standards as WR multipliers and put them next to the 2026 standards.

![Two side-by-side bar charts comparing 2020-2025 BQ multipliers to 2026 BQ multipliers, with men on the left and women on the right. Within each chart, light-colored bars (2020-2025) sit just above dark-colored bars (2026), shifted down by roughly the same amount in every bracket](./images/fig4-historical-comparison.png)
*Light bars = 2020-2025. Dark bars = 2026. The tightening shifted every under-60 bracket down by about the same proportion. Relative structure unchanged. The 60+ brackets weren't touched at all.*

The tightening was uniform within each gender. Every under-60 bar dropped by roughly the same proportion. Women's CV in 2020-2025: 6.8%. Women's CV in 2026: 6.6%. The structural inconsistency I found wasn't introduced by 2026, and it wasn't fixed by 2026. It's been there for years.

There was one unintended consequence worth flagging. By tightening only under-60 standards, the BAA made the gap between the 55-59 and 60-64 brackets steeper. A 59-year-old man used to need 3:35. A 60-year-old man needed 3:50. That 15-minute jump on your birthday is now a 20-minute jump. The "birthday cliff" got taller.

## The honest answer

I went in expecting to find either a bias or nothing. What I actually found doesn't reduce cleanly to either side of the argument I described at the top of this article.

- **"Boston is unfair to women on average".** No, it isn't. The means are statistically balanced under every framework I tested.
- **"Boston is unfair to women in distribution".** Yes, it is. The variance is 3-4× higher across women's brackets, robustly, under all three frameworks.
- **"Women's qualifying is broken".** Too strong. Most of the inconsistency comes from one bracket (W80+) and a couple of unusually strong or unusually thin reference records in others.
- **"The BAA should adjust W80+".** This one is unambiguous. Every framework I tried, every sensitivity check I ran, all point at W80+ as the single most miscalibrated bracket in the table.

That last bullet matters more than the rest. If the BAA wants to do exactly one thing in response to this, it's adjusting W80+ by 30-50 minutes. It would affect a tiny number of runners per year. A few dozen women in their 80s, who already have to perform at near-record level to qualify, but it would bring the standard in line with every other bracket under every framework I tested. It's the cheapest fairness intervention available.

## How the analysis works

The whole thing is a single Python notebook plus four small CSV files. No build step, no infrastructure, no API keys. Open it in Jupyter or VS Code and run all cells.

The four datasets:

- **`bq_standards_2026.csv`.** All 22 BAA qualifying times, sourced directly from baa.org
- **`world_records.csv`.** Open and masters marathon WRs per bracket, verified against World Athletics and the Wikipedia masters records list
- **`wma_age_factors.csv`.** WMA 2023 age-grading factors for marathon, single-year ages averaged to bracket midpoints
- **`field_size_2026.csv`.** 24,362 accepted / 33,249 applied / 4:34 under-BQ cutoff from BAA press releases

The notebook walks through the same nine sections that mirror the report:

1. Loading and merging the four datasets
2. Framework 1: WR multiplier with the Welch t-test and Levene test
3. Framework 2: Top-3 averages with estimated depth factors
4. Framework 3: WMA age-graded percentages
5. Cross-framework comparison (CV charts, fair-vs-actual gap, deviation heatmaps)
6. Historical comparison: rebuilding 2020-2025 standards inline and plotting them against 2026
7. Sensitivity analysis: dropping W80+, substituting Diver's W40, substituting Assefa's women-only WR
8. Key findings (text summary)
9. Limitations and the final summary table

Every figure in the report and on the web article comes from this notebook. Same numbers, same data, same plotting code. I verified it by hashing each embedded image and matching it against the notebook outputs. They're byte-for-byte identical.

## Three things I'd push back on if I were the BAA

When I started this, I assumed I'd end up writing "the BAA should fix X, Y, and Z." What I actually want to flag is more limited. There are good reasons not to over-interpret what I found.

**The frameworks measure difficulty-parity only.** They don't measure field-size diversity, historical continuity, the message you want to send about who belongs at Boston, the depth of competition in each bracket, or any of the other legitimate things a race director might be optimizing for. A standard that looks "unfair" under WR multiplier might be exactly right if your goal is keeping the W80+ field competitive at the front end. I have no idea if that's what the BAA is doing, because nobody's said.

**The sample is small.** Eleven brackets per gender. The Levene test that crosses the 0.05 threshold is real but underpowered. The variance gap is robust to perturbation, so I trust the direction, but I wouldn't bet on the exact effect size.

**The under-35 brackets use the open WR as reference.** No separate masters records exist below age 35, so the 18-34 and 35-39 brackets are anchored to Sawe and Chepngetich. This makes the 35-39 multiplier artificially high (the standard looks "easier" than it is because the reference is harder than it should be). I called this out in the notebook but it's worth flagging again.

## What it doesn't do (yet)

Things I'd build if I cared enough to keep working on it:

- **More than men and women.** I excluded non-binary athletes because the BAA itself notes insufficient data to set evidence-based standards yet. As that dataset grows, the analysis should expand.

- **Brackets the BAA doesn't use.** Maybe the right cut isn't 5-year age groups at all. WMA factors change smoothly with single-year ages; the BAA's bracket structure might itself be a fairness problem.

- **The application-level data.** This whole analysis treats the published BQ standards as the variable of interest. But the *actual* cutoff is 4:34 under BQ. The cutoff exists because the field is capped at ~24,000, and the cap interacts with bracket structure in ways I haven't modeled. A field-size simulation would be a separate project but a natural follow-on.

- **Historical depth.** I compared 2026 to 2020-2025. Going back to the 1980 standards, or to the 2003 tightening, would let me check whether the variance gap has always been this size or whether it's grown.

- **An interactive version.** The static charts are fine for a report, but the natural form of this analysis is a tool where you adjust the framework parameters yourself and watch the numbers move. I built three frameworks; you might want to build a fourth.

---

## Image credits

The hero photo at the top of this article and any decorative imagery should be sourced from a free-licensed library before publishing:

- **Unsplash** ([unsplash.com](https://unsplash.com)), free for commercial use, no attribution required. Search "marathon," "running," "race start" for hero candidates.
- **Pexels** ([pexels.com](https://www.pexels.com)), same license terms. Good selection of finish-line and crowd shots.
- **Wikimedia Commons.** For images of specific runners (Sawe, Chepngetich, Nakano), filter by Creative Commons license and check attribution requirements per image.

The five data figures in this article (fig1, fig2, fig3, fig4, and the implicit heatmap) are generated by the notebook in this repo and saved to `outputs/figures/` at 400 DPI. They're free to reuse with attribution to this project.
