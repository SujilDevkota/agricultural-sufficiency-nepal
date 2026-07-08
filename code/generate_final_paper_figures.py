#!/usr/bin/env python3
"""Generate paper-ready figures for the final paper workflow."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "results" / "analysis"
ANALYSIS_DATA = ANALYSIS_DIR / "analysis_dataset.csv"
PROVINCE_PROFILES = ANALYSIS_DIR / "province_profiles.csv"
SCENARIOS = ANALYSIS_DIR / "counterfactual_scenarios.csv"
OUTPUT_DIR = ROOT / "results" / "figures"

PROVINCE_COLORS = {
    "Koshi": "#1b4965",
    "Madhesh": "#ca6702",
    "Bagmati": "#7f5539",
    "Gandaki": "#6a994e",
    "Lumbini": "#8d99ae",
    "Karnali": "#8a1c7c",
    "Sudurpashchim": "#3a86ff",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_analysis_rows() -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for row in read_csv(ANALYSIS_DATA):
        parsed: dict[str, float | str] = {
            "district": row["district"],
            "province": row["province"],
        }
        for key, value in row.items():
            if key in {"district", "province"}:
                continue
            parsed[key] = float(value)
        rows.append(parsed)
    return rows


def weighted_linear_fit(x: np.ndarray, y: np.ndarray, weights: np.ndarray) -> tuple[float, float]:
    slope, intercept = np.polyfit(x, y, deg=1, w=np.sqrt(weights))
    return float(slope), float(intercept)


def point_sizes(weights: np.ndarray) -> np.ndarray:
    scaled = np.sqrt(weights / weights.max())
    return 30.0 + 220.0 * scaled


def save_current_figure(stem: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUTPUT_DIR / f"{stem}.png", dpi=300, bbox_inches="tight")
    plt.savefig(OUTPUT_DIR / f"{stem}.pdf", bbox_inches="tight")
    plt.close()


def base_style() -> None:
    plt.style.use("default")
    plt.rcParams.update(
        {
            "font.family": "serif",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titlesize": 14,
            "axes.labelsize": 12,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 9,
        }
    )


def annotate_selected(ax: plt.Axes, rows: list[dict[str, float | str]], x_key: str, y_key: str, districts: list[str]) -> None:
    for row in rows:
        if row["district"] not in districts:
            continue
        ax.annotate(
            str(row["district"]),
            (float(row[x_key]), float(row[y_key])),
            textcoords="offset points",
            xytext=(5, 4),
            fontsize=8,
            color="#222222",
        )


def make_fragmentation_scatter(rows: list[dict[str, float | str]]) -> None:
    base_style()
    fig, ax = plt.subplots(figsize=(8.6, 6.1))

    x = np.array([float(row["avg_parcels_per_holding"]) for row in rows])
    y = np.array([float(row["ag_insufficiency_share"]) for row in rows])
    weights = np.array([float(row["total_holdings"]) for row in rows])
    sizes = point_sizes(weights)

    for province, color in PROVINCE_COLORS.items():
        province_rows = [row for row in rows if row["province"] == province]
        ax.scatter(
            [float(row["avg_parcels_per_holding"]) for row in province_rows],
            [float(row["ag_insufficiency_share"]) for row in province_rows],
            s=point_sizes(np.array([float(row["total_holdings"]) for row in province_rows])),
            color=color,
            alpha=0.82,
            edgecolor="white",
            linewidth=0.7,
            label=province,
        )

    slope, intercept = weighted_linear_fit(x, y, weights)
    x_line = np.linspace(x.min() - 0.1, x.max() + 0.1, 200)
    ax.plot(x_line, slope * x_line + intercept, color="#111111", linewidth=2.2, label="Weighted fit")

    annotate_selected(
        ax,
        rows,
        "avg_parcels_per_holding",
        "ag_insufficiency_share",
        ["Humla", "Lalitpur", "Dolpa", "Rupandehi"],
    )

    ax.set_title("Fragmentation and Agricultural Insufficiency Across Districts")
    ax.set_xlabel("Average parcels per holding")
    ax.set_ylabel("Agricultural insufficiency share")
    ax.set_xlim(1.3, 6.6)
    ax.set_ylim(0.28, 0.92)
    ax.grid(axis="y", alpha=0.18)

    province_handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=color, markersize=8, label=province)
        for province, color in PROVINCE_COLORS.items()
    ]
    ax.legend(
        province_handles + [Line2D([0], [0], color="#111111", lw=2.2, label="Weighted fit")],
        list(PROVINCE_COLORS) + ["Weighted fit"],
        loc="lower right",
        frameon=False,
        ncol=2,
    )

    save_current_figure("figure_fragmentation_insufficiency")


def make_irrigation_scatter(rows: list[dict[str, float | str]]) -> None:
    base_style()
    fig, ax = plt.subplots(figsize=(8.6, 6.1))

    x = np.array([float(row["irrigation_area_share"]) for row in rows])
    y = np.array([float(row["ag_insufficiency_share"]) for row in rows])
    weights = np.array([float(row["total_holdings"]) for row in rows])

    for province, color in PROVINCE_COLORS.items():
        province_rows = [row for row in rows if row["province"] == province]
        ax.scatter(
            [float(row["irrigation_area_share"]) for row in province_rows],
            [float(row["ag_insufficiency_share"]) for row in province_rows],
            s=point_sizes(np.array([float(row["total_holdings"]) for row in province_rows])),
            color=color,
            alpha=0.82,
            edgecolor="white",
            linewidth=0.7,
            label=province,
        )

    slope, intercept = weighted_linear_fit(x, y, weights)
    x_line = np.linspace(x.min() - 0.01, x.max() + 0.01, 200)
    ax.plot(x_line, slope * x_line + intercept, color="#111111", linewidth=2.2, label="Weighted fit")

    annotate_selected(
        ax,
        rows,
        "irrigation_area_share",
        "ag_insufficiency_share",
        ["Bara", "Rukum East", "Dolpa", "Rupandehi"],
    )

    ax.set_title("Irrigation Coverage and Agricultural Insufficiency Across Districts")
    ax.set_xlabel("Irrigation area share")
    ax.set_ylabel("Agricultural insufficiency share")
    ax.set_xlim(0.0, 0.95)
    ax.set_ylim(0.28, 0.92)
    ax.grid(axis="y", alpha=0.18)

    province_handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=color, markersize=8, label=province)
        for province, color in PROVINCE_COLORS.items()
    ]
    ax.legend(
        province_handles + [Line2D([0], [0], color="#111111", lw=2.2, label="Weighted fit")],
        list(PROVINCE_COLORS) + ["Weighted fit"],
        loc="upper right",
        frameon=False,
        ncol=2,
    )

    save_current_figure("figure_irrigation_insufficiency")


def make_province_profile() -> None:
    base_style()
    rows = read_csv(PROVINCE_PROFILES)
    rows = sorted(rows, key=lambda row: float(row["insufficiency_weighted_mean"]), reverse=True)

    provinces = [row["province"] for row in rows]
    irrigation = np.array([float(row["irrigation_area_weighted_mean"]) for row in rows])
    insuff = np.array([float(row["insufficiency_weighted_mean"]) for row in rows])
    holdings_share = np.array([float(row["holdings_share"]) for row in rows])

    y = np.arange(len(provinces))
    height = 0.34

    fig, ax = plt.subplots(figsize=(8.8, 6.0))
    ax.barh(y + height / 2, insuff, height=height, color="#bc4749", label="Weighted insufficiency share")
    ax.barh(y - height / 2, irrigation, height=height, color="#2a9d8f", label="Weighted irrigation share")

    for idx, share in enumerate(holdings_share):
        ax.text(max(irrigation[idx], insuff[idx]) + 0.015, y[idx], f"holdings {share:.1%}", va="center", fontsize=8, color="#333333")

    ax.set_yticks(y)
    ax.set_yticklabels(provinces)
    ax.invert_yaxis()
    ax.set_xlim(0.0, 0.82)
    ax.set_xlabel("Weighted district average")
    ax.set_title("Province Profile: Irrigation Coverage and Agricultural Insufficiency")
    ax.grid(axis="x", alpha=0.18)
    ax.legend(frameon=False, loc="lower right")

    save_current_figure("figure_province_profile")


def make_scenario_figure() -> None:
    base_style()
    rows = read_csv(SCENARIOS)

    frag_groups = ["Low fragmentation", "High fragmentation"]
    irrig_labels = ["Low irrigation", "High irrigation"]
    scenario_map = {(row["fragmentation_scenario"].split(" (")[0], row["irrigation_scenario"].split(" (")[0]): float(row["weighted_average_predicted_insufficiency"]) for row in rows}

    x = np.arange(len(frag_groups))
    width = 0.34

    low_vals = np.array([scenario_map[(frag, "Low irrigation")] for frag in frag_groups])
    high_vals = np.array([scenario_map[(frag, "High irrigation")] for frag in frag_groups])

    fig, ax = plt.subplots(figsize=(7.8, 5.8))
    bars_low = ax.bar(x - width / 2, low_vals, width=width, color="#d62828", label="Low irrigation")
    bars_high = ax.bar(x + width / 2, high_vals, width=width, color="#2a9d8f", label="High irrigation")

    for bars in (bars_low, bars_high):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height + 0.01, f"{height:.3f}", ha="center", va="bottom", fontsize=9)

    ax.set_xticks(x)
    ax.set_xticklabels(frag_groups)
    ax.set_ylim(0.0, 0.80)
    ax.set_ylabel("Predicted agricultural insufficiency share")
    ax.set_title("Predicted Insufficiency From the Main Fractional Logit")
    ax.grid(axis="y", alpha=0.18)
    ax.legend(frameon=False, loc="upper right")

    save_current_figure("figure_scenario_predictions")


def main() -> None:
    rows = read_analysis_rows()
    make_fragmentation_scatter(rows)
    make_irrigation_scatter(rows)
    make_province_profile()
    make_scenario_figure()
    print(f"Wrote final paper figures to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
