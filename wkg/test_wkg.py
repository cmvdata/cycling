"""Sanity tests for the W/kg estimator. Run: python -m pytest -q"""
from wkg_estimator import ferrari_wkg, physical_power_w, physical_wkg, monte_carlo_wkg


def test_power_increases_with_gradient():
    base = dict(v=5.0, m_total=72, rho=1.1, CdA=0.32, Crr=0.004, v_wind=0.0, eta=0.976)
    assert physical_power_w(gradient=0.10, **base) > physical_power_w(gradient=0.04, **base)


def test_faster_time_means_more_wkg():
    slow = physical_wkg(13200, 1071, 45 * 60, 64)
    fast = physical_wkg(13200, 1071, 38 * 60, 64)
    assert fast > slow


def test_ferrari_and_physical_agree_roughly():
    grad = 100 * 1071 / (13200 ** 2 - 1071 ** 2) ** 0.5
    f = ferrari_wkg(1071, 40 * 60, grad)
    p = physical_wkg(13200, 1071, 40 * 60, 64)
    assert abs(f - p) < 0.5            # two methods within half a W/kg


def test_monte_carlo_median_near_point_estimate():
    p = physical_wkg(13200, 1071, 40 * 60, 64)
    mc = monte_carlo_wkg(13200, 1071, 40 * 60, 64, n=50_000, seed=0)
    assert abs(mc["median"] - p) < 0.2
    assert mc["p95"] > mc["p05"]       # the CI has positive width


def test_ci_widens_with_more_uncertainty():
    narrow = monte_carlo_wkg(13200, 1071, 40 * 60, 64, n=80_000, seed=1, unc_scale=1.0)
    wide = monte_carlo_wkg(13200, 1071, 40 * 60, 64, n=80_000, seed=1, unc_scale=2.0)
    assert (wide["p95"] - wide["p05"]) > (narrow["p95"] - narrow["p05"])


def test_pogacar_higher_than_froome():
    froome = monte_carlo_wkg(8900, 664, 23 * 60 + 14, 67, n=50_000, seed=0)
    pogacar = monte_carlo_wkg(15800, 1249, 39 * 60 + 43, 66, n=50_000, seed=0)
    assert pogacar["median"] > froome["median"]
