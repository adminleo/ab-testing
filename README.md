# A/B testing — sizing an experiment before you run it

A sample-size calculator and a design checklist, built around the one question
that decides whether a test is worth running at all: **how long until the
result means anything?**

## The calculator

```bash
python3 sample_size.py --baseline 0.03 --traffic 5000 --table
```

```
baseline 3.0%   alpha 0.05   power 80%   traffic 5,000/day

      lift   per variant    both groups       days
  ------------------------------------------------
       +2%     1,281,191      2,562,382        512
       +5%       207,935        415,870         83
      +10%        53,208        106,415         21
      +20%        13,911         27,822          6
      +50%         2,514          5,029          1
```

Pure standard library — no scipy. The inverse normal CDF is Acklam's rational
approximation, checked against known quantiles in `test_sample_size.py`.

```bash
python3 test_sample_size.py     # 5/5 passed
```

**The pattern that matters:** halving the effect you want to detect roughly
**quadruples** the traffic you need. That single relationship is why testing a
button colour is usually a fantasy — a 2% lift on a 3% baseline needs two and a
half million visitors.

## Design checklist

**How many variants?** Two, unless traffic is abundant. Three splits the same
visitors three ways *and* multiplies the comparisons: three variants against
control at α = 0.05 carries roughly a 14% chance of at least one false winner,
not 5%. More variants means correcting the threshold.

**How big a change?** The size of the change decides what you can learn. Change
one element and you know exactly what caused the result, but the effect is
likely too small to detect. Redesign the page and you may get a clear lift
without knowing which of twenty changes produced it. Both are valid — choose
before starting.

**How to split.** Randomly, per visitor, sticky, simultaneous. Random is what
makes the groups comparable on everything you did not think to control for;
splitting by device measures the device, not the design. Hash the visitor ID
with the experiment ID and take the remainder: same person, same bucket, no
state to store.

**Verify the split before reading results.** Configure 50/50 and observe 48/52
and something is broken — bot filtering, a cache, a redirect eating users. That
alone invalidates the test, and it is easy to miss because the numbers still
look plausible.

**Which metric.** One primary metric, fixed before the test. Clicks are
tempting and misleading: a louder button wins on clicks and can still lose
money. Keep guardrails — bounce rate, page speed, returns — and resist
metric-shopping afterwards, which is the multiple-comparison problem again.

**What to log.** Assignment, exposure, and outcome, all raw. The classic bug is
logging only the users who converted, which leaves numerators without
denominators and makes every variant look perfect. Log the assignment for
everyone, including those who do nothing.

**Reading the result.** For clicked/didn't-click, a chi-square test; for a
continuous metric, a two-sample t-test. The confidence interval on the
*difference* says more than the p-value: "+0.4 points, 95% CI [0.1, 0.7]" tells
you how much it moved, not just that it did.

**Peeking is what actually ruins tests.** Checking daily and stopping the
moment it turns green pushes the false-positive rate from 5% to well over 20% —
noise crosses the line eventually, and watching constantly guarantees you are
there when it does. Fix the sample size first, then look once.

## Why this repository exists

Written while working through an experimental-design unit on a retail funnel.
The analysis of the actual experiment will be added here once the data lands;
until then the calculator stands on its own, which is the part that gets reused.
