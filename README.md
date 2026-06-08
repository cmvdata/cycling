# Estimating Climbing W/kg with Honest Uncertainty

A small, reproducible estimator of a cyclist's relative power (watts per kilogram)
on a climb — and a short academic paper built on it. The whole point: a climbing
W/kg figure is **a distribution, not a verdict**. Instead of a single "mutant"
number, the method reports a median, a 90% credible interval, and the probability
of exceeding a chosen threshold.

## Contents

Everything lives in [`wkg/`](wkg/):

- **`wkg_estimator.py`** — three estimators: the VAM/Ferrari rule of thumb, a
  validated physical power-balance model (gravity + rolling + aero + drivetrain),
  and a Monte Carlo layer that propagates input uncertainty into a distribution.
- **`compare_climbs.py`** — applies the method to two iconic Pyrenean efforts
  (Froome, Ax 3 Domaines 2013 vs Pogačar, Plateau de Beille 2024).
- **`test_wkg.py`** — sanity tests (`python -m pytest -q`).
- **`paper.tex` / `paper.pdf`** — the write-up (LaTeX `article`, natbib).
- **`refs.bib`** — the seven peer-reviewed references that anchor each claim.
- **`wkg_distribution.png`, `froome_vs_pogacar.png`** — figures produced by the code.

See [`wkg/README.md`](wkg/README.md) for the full project notes.

## Run

```bash
pip install numpy matplotlib pytest
cd wkg
python -m pytest -q          # sanity tests
python wkg_estimator.py      # demo: Alpe d'Huez -> wkg_distribution.png
python compare_climbs.py     # Froome vs Pogačar -> froome_vs_pogacar.png
```

## Build the paper

```bash
cd wkg
pdflatex paper.tex && bibtex paper && pdflatex paper.tex && pdflatex paper.tex
```

## Stance

This **estimates with uncertainty; it does not accuse.** "Above the old ceiling"
is not "doping." Every number in the paper comes from the code or a cited
reference; the model estimates a mechanical effort and has no fatigue layer.

> Note: the copyrighted reference PDFs are intentionally not redistributed here;
> see `refs.bib` for DOIs.
