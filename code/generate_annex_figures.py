#!/usr/bin/env python3
"""Generate the three Annex III figures (A1-A3) to results/annex_figures/*.pdf."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_final_paper_analysis as base  # noqa: E402
from run_thesis_robustness import design, belt_of  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "annex_figures"

plt.rcParams.update({
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "legend.fontsize": 9,
    "axes.grid": True,
    "grid.alpha": 0.3,
})

BELT_COLORS = {"Mountain": "#7b3294", "Hill": "#1b7837", "Terai": "#d95f02"}


def save(fig, stem: str) -> None:
    fig.tight_layout()
    fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote", stem + ".pdf")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = base.read_dataset(base.DATASET)
    weights = base.as_array(rows, base.WEIGHT)
    y = base.as_array(rows, base.MAIN_OUTCOME)
    severe = base.as_array(rows, "severe_insuff_10_12_share")
    irrig = base.as_array(rows, "irrigation_area_share")
    names = [str(r["district"]) for r in rows]
    belts = [belt_of(n) for n in names]

    # A1: fitted vs actual (fractional logit, province FE)
    X, cols = design(rows, province_fe=True, belt_fe=False)
    beta, *_ = base.fractional_logit_hc1(y, X, weights)
    fitted = base.logistic(X @ beta)
    corr = np.corrcoef(fitted, y)[0, 1]

    fig, ax = plt.subplots(figsize=(7.6, 5.6))
    for b in ("Mountain", "Hill", "Terai"):
        idx = [i for i, bb in enumerate(belts) if bb == b]
        ax.scatter(fitted[idx], y[idx], s=34, alpha=0.85, color=BELT_COLORS[b],
                   edgecolor="white", linewidth=0.5, label=b)
    lims = [0.25, 0.95]
    ax.plot(lims, lims, color="#111111", linewidth=1.6, linestyle="--",
            label="45-degree line")
    ax.set_xlim(lims); ax.set_ylim(lims)
    ax.set_xlabel("Fitted insufficiency share (fractional logit, province FE)")
    ax.set_ylabel("Actual insufficiency share")
    ax.set_title(f"Fitted versus actual district insufficiency "
                 f"(corr = {corr:.3f}, squared corr = {corr**2:.3f})")
    ax.legend(loc="upper left", frameon=True)
    save(fig, "figure_fitted_vs_actual")

    # A2: overall vs severe insufficiency
    fig, ax = plt.subplots(figsize=(7.6, 5.6))
    for b in ("Mountain", "Hill", "Terai"):
        idx = [i for i, bb in enumerate(belts) if bb == b]
        ax.scatter(y[idx], severe[idx], s=34, alpha=0.85, color=BELT_COLORS[b],
                   edgecolor="white", linewidth=0.5, label=b)
    for label in ("Dolpa", "Kathmandu", "Kaski", "Manang", "Rupandehi", "Jhapa"):
        i = names.index(label)
        ax.annotate(label, (y[i], severe[i]), textcoords="offset points",
                    xytext=(6, 4), fontsize=8, color="#222222")
    ax.set_xlabel("Overall insufficiency share (NSCA Table 35)")
    ax.set_ylabel("Severe 10--12-month food-insufficiency share (Table 36.2)")
    ax.set_title("Overall versus severe insufficiency: two different geographies")
    ax.legend(loc="upper right", frameon=True)
    save(fig, "figure_overall_vs_severe")

    # A3: irrigation by ecological belt
    fig, ax = plt.subplots(figsize=(7.6, 5.2))
    order = ["Mountain", "Hill", "Terai"]
    rng = np.random.default_rng(7)
    for k, b in enumerate(order):
        idx = [i for i, bb in enumerate(belts) if bb == b]
        xj = k + rng.uniform(-0.16, 0.16, size=len(idx))
        ax.scatter(xj, irrig[idx], s=30, alpha=0.8, color=BELT_COLORS[b],
                   edgecolor="white", linewidth=0.5)
        wmean = float(np.average(irrig[idx], weights=weights[idx]))
        ax.hlines(wmean, k - 0.28, k + 0.28, color="#111111", linewidth=2.4)
        ax.annotate(f"{wmean:.2f}", (k + 0.30, wmean), fontsize=9, va="center")
    ax.set_xticks(range(3), order)
    ax.set_ylabel("Irrigated-area share")
    ax.set_title("Irrigated-area share by ecological belt "
                 "(points: districts; bars: holdings-weighted belt means)")
    save(fig, "figure_irrigation_by_belt")


if __name__ == "__main__":
    main()
