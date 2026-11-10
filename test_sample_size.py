"""Checks against values computed independently from the standard formula."""
from sample_size import sample_size, _ppf

def close(a, b, tol=0.01):
    return abs(a - b) / b < tol

def test_ppf_known_quantiles():
    assert close(-_ppf(0.025), 1.959964, 1e-5)      # two-sided alpha = 0.05
    assert close(-_ppf(0.20),  0.841621, 1e-5)      # power = 80%
    assert close(-_ppf(0.10),  1.281552, 1e-5)      # power = 90%

def test_textbook_case():
    # 3% baseline, +10% relative, alpha .05, power .80  ->  ~53,200 per variant
    assert close(sample_size(0.03, 0.10), 53208, 0.01)

def test_halving_the_effect_quadruples_n():
    small, large = sample_size(0.03, 0.05), sample_size(0.03, 0.10)
    assert 3.5 < small / large < 4.5

def test_higher_baseline_needs_less():
    assert sample_size(0.30, 0.10) < sample_size(0.03, 0.10)

def test_more_power_needs_more():
    assert sample_size(0.03, 0.10, power=0.90) > sample_size(0.03, 0.10, power=0.80)

if __name__ == "__main__":
    import sys
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for f in fns:
        f(); print(f"  ok  {f.__name__}")
    print(f"\n{len(fns)}/{len(fns)} passed")
