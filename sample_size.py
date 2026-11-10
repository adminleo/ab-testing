"""Sample size and runtime for a two-proportion A/B test.

    python3 sample_size.py --baseline 0.03 --mde 0.10 --traffic 5000
    python3 sample_size.py --baseline 0.03 --table

Answers the only question that decides whether a test is worth running: how
many visitors, and therefore how many days, before the result means anything.
"""
import argparse
from math import sqrt

# Inverse normal CDF without scipy — Acklam's rational approximation,
# accurate to ~1e-9 over the range that matters here.
def _ppf(p):
    a = (-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00)
    b = (-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01)
    c = (-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00)
    d = (7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00)
    pl, ph = 0.02425, 1 - 0.02425
    if p < pl:
        q = sqrt(-2 * __import__("math").log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > ph:
        q = sqrt(-2 * __import__("math").log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q, r = p - 0.5, (p - 0.5) ** 2
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def sample_size(baseline, mde_relative, alpha=0.05, power=0.80):
    """Visitors needed PER VARIANT to detect a relative lift on `baseline`."""
    if not 0 < baseline < 1:
        raise ValueError("baseline must be a proportion between 0 and 1")
    p2 = baseline * (1 + mde_relative)
    if not 0 < p2 < 1:
        raise ValueError("baseline * (1 + mde) must stay below 1")
    z_a = -_ppf(alpha / 2)          # two-sided
    z_b = -_ppf(1 - power)
    num = (z_a + z_b) ** 2 * (baseline * (1 - baseline) + p2 * (1 - p2))
    return num / (p2 - baseline) ** 2


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--baseline", type=float, required=True, help="current conversion rate, e.g. 0.03")
    ap.add_argument("--mde", type=float, help="relative lift to detect, e.g. 0.10 for +10%%")
    ap.add_argument("--traffic", type=float, help="visitors per day across both variants")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--power", type=float, default=0.80)
    ap.add_argument("--table", action="store_true", help="show a range of detectable lifts")
    a = ap.parse_args()

    def row(mde):
        n = sample_size(a.baseline, mde, a.alpha, a.power)
        days = f"{2 * n / a.traffic:,.0f}" if a.traffic else "—"
        print(f"  {'+' + format(mde * 100, '.0f') + '%':>8}  {n:>12,.0f}  {2 * n:>13,.0f}  {days:>9}")

    print(f"\nbaseline {a.baseline:.1%}   alpha {a.alpha}   power {a.power:.0%}"
          + (f"   traffic {a.traffic:,.0f}/day" if a.traffic else ""))
    print(f"\n  {'lift':>8}  {'per variant':>12}  {'both groups':>13}  {'days':>9}")
    print("  " + "-" * 48)
    for mde in ([0.02, 0.05, 0.10, 0.20, 0.50] if a.table else [a.mde or 0.10]):
        row(mde)
    print("\n  Run at least one full week and stop on a week boundary.")
    print("  If the answer is months, the effect is too small to chase.\n")


if __name__ == "__main__":
    main()
