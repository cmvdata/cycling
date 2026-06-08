"""Run the W/kg estimator on two iconic Pyrenean demolitions, 11 years apart."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from wkg_estimator import ferrari_wkg, physical_wkg, monte_carlo_wkg

climbs = {
    "Froome - Ax 3 Domaines (2013)":      dict(length_m=8900,  gain_m=664,  time_s=23*60+14, mass=67, color="#2a6fb0"),
    "Pogacar - Plateau de Beille (2024)": dict(length_m=15800, gain_m=1249, time_s=39*60+43, mass=66, color="#ff8a1e"),
}

fig, ax = plt.subplots(figsize=(8.5, 4.8), dpi=130)
for name, c in climbs.items():
    grad_pct = 100 * c["gain_m"] / (c["length_m"]**2 - c["gain_m"]**2) ** 0.5
    vam = c["gain_m"] * 3600 / c["time_s"]
    f = ferrari_wkg(c["gain_m"], c["time_s"], grad_pct)
    p = physical_wkg(c["length_m"], c["gain_m"], c["time_s"], c["mass"])
    mc = monte_carlo_wkg(c["length_m"], c["gain_m"], c["time_s"], c["mass"], threshold=6.2)
    print(f"\n{name}")
    print(f"  climb {c['length_m']/1000:.1f} km @ {grad_pct:.2f}%  |  "
          f"{c['time_s']//60}:{c['time_s']%60:02d}  |  VAM {vam:.0f} m/h  |  ~{c['mass']} kg")
    print(f"  Ferrari {f:.2f}  |  physical {p:.2f}  |  MC median {mc['median']:.2f} "
          f"(90% CI {mc['p05']:.2f}-{mc['p95']:.2f})  |  P(>6.2)={mc['p_above_threshold']*100:.0f}%")
    ax.hist(mc["samples"], bins=120, color=c["color"], alpha=0.6,
            label=f"{name.split('-')[0].strip()}: {mc['median']:.2f} W/kg")
    ax.axvline(mc["median"], color=c["color"], lw=2, ls="--")

ax.axvline(6.2, color="#c00", lw=1.5, ls=":", label='~6.2 "suspicion" line')
ax.set_title("Two Pyrenean demolitions, 11 years apart  (estimated W/kg, with uncertainty)")
ax.set_xlabel("W/kg"); ax.set_yticks([]); ax.legend(frameon=False, fontsize=9)
for sp in ["top", "right", "left"]:
    ax.spines[sp].set_visible(False)
fig.tight_layout(); fig.savefig("froome_vs_pogacar.png")
print("\nsaved froome_vs_pogacar.png")
