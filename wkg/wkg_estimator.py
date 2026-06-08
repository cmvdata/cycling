"""
wkg_estimator.py
----------------
Estimate a climber's relative power (W/kg) from climb performance,
with honest uncertainty propagation.

Three estimators, from crude to defensible:
  1. ferrari_wkg()     - the VAM rule of thumb (what cycling Twitter throws around)
  2. physical_wkg()    - full power-balance model (gravity + rolling + aero + drivetrain)
  3. monte_carlo_wkg() - propagates input uncertainty -> distribution + credible interval

The whole point of the project: don't publish a single "mutant" number.
Publish a range, and the probability of exceeding a chosen physiological threshold.
"""

import numpy as np

G = 9.81  # gravity, m/s^2


def ferrari_wkg(elevation_gain_m, time_s, gradient_pct):
    """Dr. Ferrari's VAM rule of thumb. Explicitly an approximation."""
    vam = elevation_gain_m * 3600.0 / time_s            # vertical metres per hour
    gradient_factor = 2.0 + gradient_pct / 10.0
    return vam / (gradient_factor * 100.0)


def physical_power_w(v, gradient, m_total, rho, CdA, Crr, v_wind, eta):
    """
    Steady-state power AT THE RIDER (W) to climb at road speed v (m/s).
    gradient is a fraction (0.08 == 8%). v_wind > 0 is a headwind (m/s).
    """
    theta = np.arctan(gradient)
    p_gravity = m_total * G * np.sin(theta) * v
    p_rolling = Crr * m_total * G * np.cos(theta) * v
    p_aero = 0.5 * rho * CdA * (v + v_wind) ** 2 * v
    return (p_gravity + p_rolling + p_aero) / eta


def physical_wkg(length_m, elevation_gain_m, time_s, m_rider,
                 m_bike=8.0, rho=1.10, CdA=0.32, Crr=0.004, v_wind=0.0, eta=0.976):
    """Single point estimate of W/kg from the physical model (per rider body mass)."""
    gradient = elevation_gain_m / np.sqrt(max(length_m ** 2 - elevation_gain_m ** 2, 1e-9))
    v = length_m / time_s
    p = physical_power_w(v, gradient, m_rider + m_bike, rho, CdA, Crr, v_wind, eta)
    return p / m_rider


def monte_carlo_wkg(length_m, elevation_gain_m, time_s, m_rider_mean,
                    n=200_000, threshold=6.2, seed=0, unc_scale=1.0):
    """
    Propagate uncertainty in the inputs we DON'T really know and return a
    distribution of W/kg estimates. Priors are deliberately wide and editable;
    `unc_scale` multiplies every prior standard deviation (1.0 = default widths).
    """
    rng = np.random.default_rng(seed)
    s = unc_scale
    m_rider = rng.normal(m_rider_mean, 2.0 * s, n)        # published weights are unreliable
    m_bike = rng.normal(8.0, 0.5 * s, n)                  # bike + bottles + kit
    rho = rng.normal(1.10, 0.04 * s, n)                   # air density (altitude/temp)
    CdA = rng.normal(0.32, 0.03 * s, n)                   # seated climbing drag area
    Crr = rng.normal(0.004, 0.0006 * s, n)                # tyres on tarmac
    v_wind = rng.normal(0.0, 1.5 * s, n)                  # unknown wind (head/tail)
    eta = rng.normal(0.976, 0.005 * s, n)                 # drivetrain efficiency
    elev = rng.normal(elevation_gain_m, 0.02 * s * elevation_gain_m, n)  # DEM/GPS noise
    length = rng.normal(length_m, 0.01 * s * length_m, n)

    gradient = elev / np.sqrt(np.maximum(length ** 2 - elev ** 2, 1e-9))
    v = length / time_s
    p = physical_power_w(v, gradient, m_rider + m_bike, rho, CdA, Crr, v_wind, eta)
    wkg = p / m_rider

    return {
        "samples": wkg,
        "median": float(np.median(wkg)),
        "p05": float(np.percentile(wkg, 5)),
        "p95": float(np.percentile(wkg, 95)),
        "p_above_threshold": float(np.mean(wkg > threshold)),
        "threshold": threshold,
    }


if __name__ == "__main__":
    # Demo: Alpe d'Huez, ~13.2 km, 1071 m of gain, climbed in 40:00, rider ~64 kg.
    length_m, gain_m, time_s, mass = 13_200, 1071, 40 * 60, 64.0
    gradient_pct = 100 * gain_m / (length_m ** 2 - gain_m ** 2) ** 0.5

    f = ferrari_wkg(gain_m, time_s, gradient_pct)
    p = physical_wkg(length_m, gain_m, time_s, mass)
    mc = monte_carlo_wkg(length_m, gain_m, time_s, mass)

    print(f"Climb: {length_m/1000:.1f} km @ {gradient_pct:.1f}%, {time_s/60:.0f} min, "
          f"rider {mass:.0f} kg")
    print(f"VAM                   : {gain_m*3600/time_s:.0f} m/h")
    print(f"Ferrari rule-of-thumb : {f:.2f} W/kg")
    print(f"Physical point est.   : {p:.2f} W/kg")
    print(f"Monte Carlo median    : {mc['median']:.2f} W/kg "
          f"(90% CI {mc['p05']:.2f}-{mc['p95']:.2f})")
    print(f"P(W/kg > {mc['threshold']})       : {mc['p_above_threshold']*100:.1f}%")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=130)
    ax.hist(mc["samples"], bins=120, color="#1c7340", alpha=0.85)
    for q, c, lab in [(mc["p05"], "#888", "5%"), (mc["median"], "#d33", "median"),
                      (mc["p95"], "#888", "95%")]:
        ax.axvline(q, color=c, lw=2, ls="--")
        ax.text(q, ax.get_ylim()[1]*0.92, f" {lab}\n {q:.2f}", color=c, fontsize=9)
    ax.set_title("Estimated W/kg is a distribution, not a number  (Alpe d'Huez, 40:00)")
    ax.set_xlabel("W/kg"); ax.set_yticks([])
    for sp in ["top", "right", "left"]:
        ax.spines[sp].set_visible(False)
    fig.tight_layout()
    fig.savefig("wkg_distribution.png")
    print("saved wkg_distribution.png")
