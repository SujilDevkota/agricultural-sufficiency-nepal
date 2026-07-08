#!/usr/bin/env python3
"""Fit the thesis models and write output tables + research memo to results/analysis/."""

from __future__ import annotations

import csv
import math
from pathlib import Path
from statistics import NormalDist
from typing import Iterable

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "processed" / "district_research_dataset.csv"
OUTPUT_DIR = ROOT / "results" / "analysis"
DOCUMENT_MEMO = ROOT / "results" / "analysis" / "research_memo.md"

WEIGHT = "total_holdings"
MAIN_OUTCOME = "ag_insufficiency_share"

PROVINCES = [
    "Koshi",
    "Madhesh",
    "Bagmati",
    "Gandaki",
    "Lumbini",
    "Karnali",
    "Sudurpashchim",
]

PROVINCE_BY_DISTRICT = {
    "Achham": "Sudurpashchim",
    "Arghakhanchi": "Lumbini",
    "Baglung": "Gandaki",
    "Baitadi": "Sudurpashchim",
    "Bajhang": "Sudurpashchim",
    "Bajura": "Sudurpashchim",
    "Banke": "Lumbini",
    "Bara": "Madhesh",
    "Bardiya": "Lumbini",
    "Bhaktapur": "Bagmati",
    "Bhojpur": "Koshi",
    "Chitwan": "Bagmati",
    "Dadeldhura": "Sudurpashchim",
    "Dailekh": "Karnali",
    "Dang": "Lumbini",
    "Darchula": "Sudurpashchim",
    "Dhanusha": "Madhesh",
    "Dhading": "Bagmati",
    "Dhankuta": "Koshi",
    "Dolakha": "Bagmati",
    "Dolpa": "Karnali",
    "Doti": "Sudurpashchim",
    "Gorkha": "Gandaki",
    "Gulmi": "Lumbini",
    "Humla": "Karnali",
    "Ilam": "Koshi",
    "Jajarkot": "Karnali",
    "Jhapa": "Koshi",
    "Jumla": "Karnali",
    "Kailali": "Sudurpashchim",
    "Kalikot": "Karnali",
    "Kanchanpur": "Sudurpashchim",
    "Kapilvastu": "Lumbini",
    "Kaski": "Gandaki",
    "Kathmandu": "Bagmati",
    "Kavrepalanchok": "Bagmati",
    "Khotang": "Koshi",
    "Lalitpur": "Bagmati",
    "Lamjung": "Gandaki",
    "Mahottari": "Madhesh",
    "Makawanpur": "Bagmati",
    "Manang": "Gandaki",
    "Morang": "Koshi",
    "Mugu": "Karnali",
    "Mustang": "Gandaki",
    "Myagdi": "Gandaki",
    "Nawalparasi East": "Gandaki",
    "Nawalparasi West": "Lumbini",
    "Nuwakot": "Bagmati",
    "Okhaldhunga": "Koshi",
    "Palpa": "Lumbini",
    "Panchthar": "Koshi",
    "Parbat": "Gandaki",
    "Parsa": "Madhesh",
    "Pyuthan": "Lumbini",
    "Ramechhap": "Bagmati",
    "Rasuwa": "Bagmati",
    "Rautahat": "Madhesh",
    "Rolpa": "Lumbini",
    "Rukum East": "Lumbini",
    "Rukum West": "Karnali",
    "Rupandehi": "Lumbini",
    "Salyan": "Karnali",
    "Sankhuwasabha": "Koshi",
    "Saptari": "Madhesh",
    "Sarlahi": "Madhesh",
    "Sindhuli": "Bagmati",
    "Sindhupalchok": "Bagmati",
    "Siraha": "Madhesh",
    "Solukhumbu": "Koshi",
    "Sunsari": "Koshi",
    "Surkhet": "Karnali",
    "Syangja": "Gandaki",
    "Tanahu": "Gandaki",
    "Taplejung": "Koshi",
    "Terhathum": "Koshi",
    "Udayapur": "Koshi",
}

VAR_LABELS = {
    "avg_parcels_per_holding": "Average parcels per holding",
    "avg_holding_size_ha": "Average holding size (ha)",
    "irrigation_area_share": "Irrigation area share",
    "irrigated_holdings_share": "Irrigated holdings share",
    "ag_sufficiency_share": "Agricultural sufficiency share",
    "ag_insufficiency_share": "Agricultural insufficiency share",
    "loan_share": "Loan share",
    "subsidy_share": "Subsidy share",
    "power_tiller_share": "Power tiller share",
    "climate_impact_share": "Climate impact share",
    "severe_insuff_10_12_share": "Severe insufficiency share (10-12 months)",
    "market_access_fast_share": "Fast market access share",
    "frag_x_irrig_area": "Fragmentation x irrigation area share",
    "frag_x_irrig_holdings": "Fragmentation x irrigated holdings share",
}

SUMMARY_VARS = [
    "avg_parcels_per_holding",
    "avg_holding_size_ha",
    "irrigation_area_share",
    "irrigated_holdings_share",
    "ag_sufficiency_share",
    "ag_insufficiency_share",
    "loan_share",
    "subsidy_share",
    "power_tiller_share",
    "climate_impact_share",
    "severe_insuff_10_12_share",
    "market_access_fast_share",
]

CORRELATION_VARS = [
    "avg_parcels_per_holding",
    "avg_holding_size_ha",
    "irrigation_area_share",
    "irrigated_holdings_share",
    "loan_share",
    "subsidy_share",
    "power_tiller_share",
    "market_access_fast_share",
    "climate_impact_share",
]

CONTROL_VARS = [
    "avg_holding_size_ha",
    "loan_share",
    "subsidy_share",
    "power_tiller_share",
    "market_access_fast_share",
    "climate_impact_share",
]

# Holdings-weighted means for centring the interaction terms; filled by read_dataset().
CENTERING: dict[str, float] = {}

MODEL_SPECS = [
    {
        "name": "weighted_ols_baseline",
        "estimator": "weighted_ols",
        "outcome": "ag_insufficiency_share",
        "irrigation": "irrigation_area_share",
        "interaction": "frag_x_irrig_area",
        "province_fe": False,
    },
    {
        "name": "weighted_ols_province_fe",
        "estimator": "weighted_ols",
        "outcome": "ag_insufficiency_share",
        "irrigation": "irrigation_area_share",
        "interaction": "frag_x_irrig_area",
        "province_fe": True,
    },
    {
        "name": "fractional_logit_main",
        "estimator": "fractional_logit",
        "outcome": "ag_insufficiency_share",
        "irrigation": "irrigation_area_share",
        "interaction": "frag_x_irrig_area",
        "province_fe": True,
    },
    {
        "name": "fractional_logit_irrig_holdings",
        "estimator": "fractional_logit",
        "outcome": "ag_insufficiency_share",
        "irrigation": "irrigated_holdings_share",
        "interaction": "frag_x_irrig_holdings",
        "province_fe": True,
    },
    {
        "name": "fractional_logit_severe_insufficiency",
        "estimator": "fractional_logit",
        "outcome": "severe_insuff_10_12_share",
        "irrigation": "irrigation_area_share",
        "interaction": "frag_x_irrig_area",
        "province_fe": True,
    },
    {
        "name": "fractional_logit_sufficiency",
        "estimator": "fractional_logit",
        "outcome": "ag_sufficiency_share",
        "irrigation": "irrigation_area_share",
        "interaction": "frag_x_irrig_area",
        "province_fe": True,
    },
]


def read_dataset(path: Path) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            district = row["district"]
            parsed: dict[str, float | str] = {
                "district": district,
                "province": PROVINCE_BY_DISTRICT[district],
            }
            for key, value in row.items():
                if key == "district":
                    continue
                parsed[key] = float(value) if value else math.nan

            total_holdings = float(parsed["total_holdings"])
            total_area = float(parsed["total_area_ha"])
            parsed["avg_holding_size_ha"] = total_area / total_holdings
            rows.append(parsed)

    if len(rows) != 77:
        raise ValueError(f"Expected 77 districts, found {len(rows)}")

    # Mean-centre (holdings-weighted) before forming interactions: main effects
    # read at the average holding, less collinearity; fit/APEs/predictions unchanged.
    hold_w = np.array([float(r["total_holdings"]) for r in rows])
    for var in ("avg_parcels_per_holding", "irrigation_area_share",
                "irrigated_holdings_share"):
        CENTERING[var] = float(np.average(
            np.array([float(r[var]) for r in rows]), weights=hold_w))
    for parsed in rows:
        frag_c = (float(parsed["avg_parcels_per_holding"])
                  - CENTERING["avg_parcels_per_holding"])
        parsed["frag_x_irrig_area"] = frag_c * (
            float(parsed["irrigation_area_share"])
            - CENTERING["irrigation_area_share"])
        parsed["frag_x_irrig_holdings"] = frag_c * (
            float(parsed["irrigated_holdings_share"])
            - CENTERING["irrigated_holdings_share"])
    return rows


def as_array(rows: list[dict[str, float | str]], column: str) -> np.ndarray:
    return np.array([float(row[column]) for row in rows], dtype=float)


def logistic(values: np.ndarray) -> np.ndarray:
    clipped = np.clip(values, -35.0, 35.0)
    return 1.0 / (1.0 + np.exp(-clipped))


def scaled_weights(weights: np.ndarray) -> np.ndarray:
    return weights / weights.mean()


def weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    return float(np.average(values, weights=weights))


def weighted_std(values: np.ndarray, weights: np.ndarray) -> float:
    mean = np.average(values, weights=weights)
    variance = np.average((values - mean) ** 2, weights=weights)
    return float(math.sqrt(variance))


def weighted_corr(x: np.ndarray, y: np.ndarray, weights: np.ndarray) -> float:
    x_bar = np.average(x, weights=weights)
    y_bar = np.average(y, weights=weights)
    cov = np.average((x - x_bar) * (y - y_bar), weights=weights)
    var_x = np.average((x - x_bar) ** 2, weights=weights)
    var_y = np.average((y - y_bar) ** 2, weights=weights)
    return float(cov / math.sqrt(var_x * var_y))


def approx_p_value(statistic: float) -> float:
    normal = NormalDist()
    return float(2.0 * (1.0 - normal.cdf(abs(statistic))))


def significance_stars(p_value: float) -> str:
    if p_value < 0.01:
        return "***"
    if p_value < 0.05:
        return "**"
    if p_value < 0.10:
        return "*"
    return ""


def summary_rows(rows: list[dict[str, float | str]], weights: np.ndarray) -> list[dict[str, str]]:
    table: list[dict[str, str]] = []
    for variable in SUMMARY_VARS:
        values = as_array(rows, variable)
        table.append(
            {
                "variable": variable,
                "label": VAR_LABELS[variable],
                "mean": f"{values.mean():.4f}",
                "weighted_mean": f"{weighted_mean(values, weights):.4f}",
                "weighted_std_dev": f"{weighted_std(values, weights):.4f}",
                # full precision so downstream tables round once, not twice
                "min": f"{values.min():.6f}",
                "max": f"{values.max():.6f}",
            }
        )
    return table


def province_profile_rows(rows: list[dict[str, float | str]]) -> list[dict[str, str]]:
    all_weights = as_array(rows, WEIGHT)
    national_holdings = all_weights.sum()
    table: list[dict[str, str]] = []
    for province in PROVINCES:
        province_rows = [row for row in rows if row["province"] == province]
        province_weights = as_array(province_rows, WEIGHT)
        table.append(
            {
                "province": province,
                "district_count": str(len(province_rows)),
                "holdings": f"{province_weights.sum():.0f}",
                "holdings_share": f"{province_weights.sum() / national_holdings:.4f}",
                "avg_parcels_weighted_mean": f"{weighted_mean(as_array(province_rows, 'avg_parcels_per_holding'), province_weights):.4f}",
                "irrigation_area_weighted_mean": f"{weighted_mean(as_array(province_rows, 'irrigation_area_share'), province_weights):.4f}",
                "insufficiency_weighted_mean": f"{weighted_mean(as_array(province_rows, 'ag_insufficiency_share'), province_weights):.4f}",
            }
        )
    return table


def correlation_rows(rows: list[dict[str, float | str]], weights: np.ndarray) -> list[dict[str, str]]:
    table: list[dict[str, str]] = []
    outcome = as_array(rows, MAIN_OUTCOME)
    for variable in CORRELATION_VARS:
        values = as_array(rows, variable)
        table.append(
            {
                "variable": variable,
                "label": VAR_LABELS[variable],
                "correlation_with_outcome": f"{np.corrcoef(values, outcome)[0, 1]:.4f}",
                "weighted_correlation_with_outcome": f"{weighted_corr(values, outcome, weights):.4f}",
            }
        )
    return table


def district_ranking_rows(
    rows: list[dict[str, float | str]],
    column: str,
    top_n: int = 8,
) -> list[dict[str, str]]:
    ascending = sorted(rows, key=lambda row: float(row[column]))
    descending = sorted(rows, key=lambda row: float(row[column]), reverse=True)
    table: list[dict[str, str]] = []
    for direction, ranked in (("lowest", ascending[:top_n]), ("highest", descending[:top_n])):
        for rank, row in enumerate(ranked, start=1):
            table.append(
                {
                    "variable": column,
                    "label": VAR_LABELS[column],
                    "direction": direction,
                    "rank": str(rank),
                    "district": str(row["district"]),
                    "province": str(row["province"]),
                    "value": f"{float(row[column]):.4f}",
                }
            )
    return table


def build_design_matrix(
    rows: list[dict[str, float | str]],
    irrigation_var: str,
    interaction_var: str,
    province_fe: bool,
) -> tuple[np.ndarray, list[str]]:
    columns = ["const", "avg_parcels_per_holding", irrigation_var, interaction_var] + CONTROL_VARS
    vectors = [np.ones(len(rows))]
    vectors.extend(as_array(rows, column) for column in columns[1:])

    if province_fe:
        for province in PROVINCES[1:]:
            columns.append(f"province_{province}")
            vectors.append(
                np.array(
                    [1.0 if row["province"] == province else 0.0 for row in rows],
                    dtype=float,
                )
            )

    X = np.column_stack(vectors)
    return X, columns


def pretty_term(term: str, irrigation_var: str, interaction_var: str) -> str:
    if term == "const":
        return "Constant"
    if term == irrigation_var:
        return VAR_LABELS[irrigation_var]
    if term == interaction_var:
        return VAR_LABELS[interaction_var]
    if term in VAR_LABELS:
        return VAR_LABELS[term]
    if term.startswith("province_"):
        return f"Province FE: {term.split('_', 1)[1]}"
    return term


def weighted_ols_hc1(
    y: np.ndarray,
    X: np.ndarray,
    weights: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict[str, float]]:
    analytic_weights = scaled_weights(weights)
    root_w = np.sqrt(analytic_weights)
    Xw = X * root_w[:, None]
    yw = y * root_w

    beta = np.linalg.lstsq(Xw, yw, rcond=None)[0]
    residuals = y - X @ beta
    xtx_inv = np.linalg.inv(Xw.T @ Xw)

    meat = np.zeros((X.shape[1], X.shape[1]))
    for index in range(len(y)):
        xi = X[index : index + 1].T
        meat += (analytic_weights[index] ** 2) * (residuals[index] ** 2) * (xi @ xi.T)

    n_obs = len(y)
    n_params = X.shape[1]
    vcov = xtx_inv @ meat @ xtx_inv * (n_obs / (n_obs - n_params))
    se = np.sqrt(np.diag(vcov))
    statistic = np.divide(beta, se, out=np.full_like(beta, np.nan), where=se != 0)
    p_values = np.array([approx_p_value(float(value)) for value in statistic], dtype=float)

    ss_res = float(np.sum(analytic_weights * residuals**2))
    y_bar = np.average(y, weights=analytic_weights)
    ss_tot = float(np.sum(analytic_weights * (y - y_bar) ** 2))
    fitted = X @ beta

    fit = {
        "metric_value": 1.0 - ss_res / ss_tot,
        "fitted_min": float(fitted.min()),
        "fitted_max": float(fitted.max()),
        "out_of_bounds": float(np.sum((fitted < 0.0) | (fitted > 1.0))),
        "converged": 1.0,
        "iterations": 1.0,
    }
    return beta, se, statistic, p_values, fit


def fractional_logit_hc1(
    y: np.ndarray,
    X: np.ndarray,
    weights: np.ndarray,
    max_iter: int = 200,
    tolerance: float = 1e-10,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict[str, float]]:
    analytic_weights = scaled_weights(weights)
    beta = np.zeros(X.shape[1], dtype=float)

    y_safe = np.clip(y, 1e-8, 1.0 - 1e-8)
    beta = np.linalg.lstsq(X, np.log(y_safe / (1.0 - y_safe)), rcond=None)[0]

    def loglike(params: np.ndarray) -> float:
        mu = logistic(X @ params)
        mu = np.clip(mu, 1e-10, 1.0 - 1e-10)
        return float(np.sum(analytic_weights * (y * np.log(mu) + (1.0 - y) * np.log(1.0 - mu))))

    converged = False
    iterations = 0
    current_ll = loglike(beta)

    for iteration in range(1, max_iter + 1):
        iterations = iteration
        mu = logistic(X @ beta)
        variance = np.clip(mu * (1.0 - mu), 1e-10, None)
        score = X.T @ (analytic_weights * (y - mu))
        information = X.T @ (analytic_weights[:, None] * variance[:, None] * X)

        try:
            step = np.linalg.solve(information, score)
        except np.linalg.LinAlgError:
            step = np.linalg.pinv(information) @ score

        step_factor = 1.0
        improved = False
        while step_factor > 1e-6:
            candidate = beta + step_factor * step
            candidate_ll = loglike(candidate)
            if candidate_ll >= current_ll:
                beta = candidate
                current_ll = candidate_ll
                improved = True
                break
            step_factor *= 0.5

        if not improved:
            break

        if np.max(np.abs(step_factor * step)) < tolerance:
            converged = True
            break

    mu = logistic(X @ beta)
    variance = np.clip(mu * (1.0 - mu), 1e-10, None)
    bread = np.linalg.pinv(X.T @ (analytic_weights[:, None] * variance[:, None] * X))

    meat = np.zeros((X.shape[1], X.shape[1]))
    for index in range(len(y)):
        score_i = analytic_weights[index] * (y[index] - mu[index]) * X[index]
        meat += np.outer(score_i, score_i)

    n_obs = len(y)
    n_params = X.shape[1]
    vcov = bread @ meat @ bread * (n_obs / (n_obs - n_params))
    se = np.sqrt(np.diag(vcov))
    statistic = np.divide(beta, se, out=np.full_like(beta, np.nan), where=se != 0)
    p_values = np.array([approx_p_value(float(value)) for value in statistic], dtype=float)

    ll_null_mean = np.average(y, weights=analytic_weights)
    ll_null = float(
        np.sum(
            analytic_weights
            * (
                y * np.log(np.clip(ll_null_mean, 1e-10, 1.0))
                + (1.0 - y) * np.log(np.clip(1.0 - ll_null_mean, 1e-10, 1.0))
            )
        )
    )

    fit = {
        "metric_value": 1.0 - current_ll / ll_null,
        "fitted_min": float(mu.min()),
        "fitted_max": float(mu.max()),
        "out_of_bounds": 0.0,
        "converged": 1.0 if converged else 0.0,
        "iterations": float(iterations),
    }
    return beta, se, statistic, p_values, fit


def run_models(
    rows: list[dict[str, float | str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], dict[str, np.ndarray]]:
    weights = as_array(rows, WEIGHT)
    results_rows: list[dict[str, str]] = []
    fit_rows: list[dict[str, str]] = []
    key_rows: list[dict[str, str]] = []
    coefficient_store: dict[str, np.ndarray] = {}

    for spec in MODEL_SPECS:
        y = as_array(rows, spec["outcome"])
        X, terms = build_design_matrix(
            rows=rows,
            irrigation_var=spec["irrigation"],
            interaction_var=spec["interaction"],
            province_fe=spec["province_fe"],
        )

        if spec["estimator"] == "weighted_ols":
            beta, se, statistic, p_values, fit = weighted_ols_hc1(y=y, X=X, weights=weights)
            fit_label = "R-squared"
        else:
            beta, se, statistic, p_values, fit = fractional_logit_hc1(y=y, X=X, weights=weights)
            fit_label = "McFadden pseudo R-squared"

        coefficient_store[spec["name"]] = beta

        for index, term in enumerate(terms):
            p_value = float(p_values[index])
            row = {
                "model": spec["name"],
                "estimator": spec["estimator"],
                "outcome": spec["outcome"],
                "term": term,
                "label": pretty_term(term, spec["irrigation"], spec["interaction"]),
                "coefficient": f"{beta[index]:.6f}",
                "robust_se": f"{se[index]:.6f}",
                "statistic": f"{statistic[index]:.4f}",
                "approx_p_value": f"{p_value:.4f}",
                "significance": significance_stars(p_value),
            }
            results_rows.append(row)

            if term in {"avg_parcels_per_holding", spec["irrigation"], spec["interaction"]}:
                key_rows.append(
                    {
                        "model": spec["name"],
                        "estimator": spec["estimator"],
                        "outcome": spec["outcome"],
                        "term": term,
                        "label": row["label"],
                        "coefficient": row["coefficient"],
                        "robust_se": row["robust_se"],
                        "statistic": row["statistic"],
                        "approx_p_value": row["approx_p_value"],
                        "significance": row["significance"],
                    }
                )

        fit_rows.append(
            {
                "model": spec["name"],
                "estimator": spec["estimator"],
                "outcome": spec["outcome"],
                "fit_metric": fit_label,
                "fit_value": f"{fit['metric_value']:.4f}",
                "fitted_min": f"{fit['fitted_min']:.4f}",
                "fitted_max": f"{fit['fitted_max']:.4f}",
                "out_of_bounds": str(int(fit["out_of_bounds"])),
                "converged": "yes" if int(fit["converged"]) == 1 else "no",
                "iterations": str(int(fit["iterations"])),
            }
        )

    return results_rows, fit_rows, key_rows, coefficient_store


def average_partial_effect_rows(
    rows: list[dict[str, float | str]],
    beta: np.ndarray,
) -> list[dict[str, str]]:
    weights = as_array(rows, WEIGHT)
    X, _ = build_design_matrix(
        rows=rows,
        irrigation_var="irrigation_area_share",
        interaction_var="frag_x_irrig_area",
        province_fe=True,
    )
    mu = logistic(X @ beta)
    frag = as_array(rows, "avg_parcels_per_holding")
    irrig = as_array(rows, "irrigation_area_share")

    beta_frag = float(beta[1])
    beta_irrig = float(beta[2])
    beta_interaction = float(beta[3])

    irrig_c = irrig - CENTERING["irrigation_area_share"]
    frag_c = frag - CENTERING["avg_parcels_per_holding"]
    dmu_dfrag = mu * (1.0 - mu) * (beta_frag + beta_interaction * irrig_c)
    dmu_dirrig = mu * (1.0 - mu) * (beta_irrig + beta_interaction * frag_c)

    return [
        {
            "term": "avg_parcels_per_holding",
            "label": "Average partial effect of fragmentation",
            "average_partial_effect": f"{weighted_mean(dmu_dfrag, weights):.6f}",
        },
        {
            "term": "irrigation_area_share",
            "label": "Average partial effect of irrigation area share",
            "average_partial_effect": f"{weighted_mean(dmu_dirrig, weights):.6f}",
        },
    ]


def counterfactual_scenario_rows(
    rows: list[dict[str, float | str]],
    beta: np.ndarray,
) -> list[dict[str, str]]:
    weights = as_array(rows, WEIGHT)
    frag = as_array(rows, "avg_parcels_per_holding")
    irrig = as_array(rows, "irrigation_area_share")

    frag_low = float(np.quantile(frag, 0.25))
    frag_high = float(np.quantile(frag, 0.75))
    irrig_low = float(np.quantile(irrig, 0.25))
    irrig_high = float(np.quantile(irrig, 0.75))

    specs = [
        ("Low fragmentation", frag_low, "Low irrigation", irrig_low),
        ("Low fragmentation", frag_low, "High irrigation", irrig_high),
        ("High fragmentation", frag_high, "Low irrigation", irrig_low),
        ("High fragmentation", frag_high, "High irrigation", irrig_high),
    ]

    scenario_rows: list[dict[str, str]] = []
    for frag_label, frag_value, irrig_label, irrig_value in specs:
        simulated_rows: list[dict[str, float | str]] = []
        for row in rows:
            updated = dict(row)
            updated["avg_parcels_per_holding"] = frag_value
            updated["irrigation_area_share"] = irrig_value
            updated["frag_x_irrig_area"] = (
                (frag_value - CENTERING["avg_parcels_per_holding"])
                * (irrig_value - CENTERING["irrigation_area_share"]))
            simulated_rows.append(updated)

        X, _ = build_design_matrix(
            rows=simulated_rows,
            irrigation_var="irrigation_area_share",
            interaction_var="frag_x_irrig_area",
            province_fe=True,
        )
        predicted = logistic(X @ beta)
        scenario_rows.append(
            {
                "fragmentation_scenario": f"{frag_label} ({frag_value:.3f})",
                "irrigation_scenario": f"{irrig_label} ({irrig_value:.3f})",
                "weighted_average_predicted_insufficiency": f"{weighted_mean(predicted, weights):.4f}",
            }
        )
    return scenario_rows


def write_csv(path: Path, rows: Iterable[dict[str, str]]) -> None:
    rows = list(rows)
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"
    lines = [header, separator]
    for row in rows:
        lines.append("| " + " | ".join(row[column] for column in columns) + " |")
    return "\n".join(lines)


def filtered_rows(rows: list[dict[str, str]], model: str) -> list[dict[str, str]]:
    return [row for row in rows if row["model"] == model]


def build_markdown(
    rows: list[dict[str, float | str]],
    summary: list[dict[str, str]],
    province_profiles: list[dict[str, str]],
    correlations: list[dict[str, str]],
    rankings: list[dict[str, str]],
    model_results: list[dict[str, str]],
    fit_rows: list[dict[str, str]],
    average_partial_effects: list[dict[str, str]],
    scenarios: list[dict[str, str]],
) -> str:
    top_insuff = [row for row in rankings if row["variable"] == "ag_insufficiency_share" and row["direction"] == "highest"][:5]
    low_insuff = [row for row in rankings if row["variable"] == "ag_insufficiency_share" and row["direction"] == "lowest"][:5]

    top_text = ", ".join(f"{row['district']} ({float(row['value']):.3f})" for row in top_insuff)
    low_text = ", ".join(f"{row['district']} ({float(row['value']):.3f})" for row in low_insuff)

    main_fractional = filtered_rows(model_results, "fractional_logit_main")
    province_ols = filtered_rows(model_results, "weighted_ols_province_fe")

    fit_lookup = {row["model"]: row for row in fit_rows}
    main_fit = fit_lookup["fractional_logit_main"]
    ols_fit = fit_lookup["weighted_ols_province_fe"]

    return f"""# Final Paper Research Memo

This memo is generated by `code/run_final_paper_analysis.py`.
It is deliberately separate from the proposal draft and should be used as the
empirical working record for the final paper.

## Scope

- Unit of analysis: district
- Number of observations: {len(rows)}
- Core outcome: agricultural insufficiency share
- Weighting approach: district-level analytical weights based on total holdings, normalized to preserve district-level inference
- Main estimators: weighted OLS benchmark and fractional logit with province fixed effects

## Research workflow now in place

1. Start from `data/processed/district_research_dataset.csv`.
2. Add province identifiers and derived variables used in the final paper workflow.
3. Produce descriptive tables, province profiles, district rankings, and weighted correlations.
4. Estimate weighted OLS benchmarks and fractional logit models with robust standard errors.
5. Run robustness checks with an alternative irrigation measure and alternative outcomes.
6. Save a reproducible memo and machine-readable output tables in `results/analysis/`.

## Descriptive picture

- Highest agricultural insufficiency districts in the current run: {top_text}.
- Lowest agricultural insufficiency districts in the current run: {low_text}.

### Summary statistics

{markdown_table(summary, ["label", "mean", "weighted_mean", "weighted_std_dev", "min", "max"])}

### Province profile

{markdown_table(province_profiles, ["province", "district_count", "holdings_share", "avg_parcels_weighted_mean", "irrigation_area_weighted_mean", "insufficiency_weighted_mean"])}

### Weighted correlations with the main outcome

{markdown_table(correlations, ["label", "correlation_with_outcome", "weighted_correlation_with_outcome"])}

## Main model results

### Weighted OLS benchmark with province fixed effects

{markdown_table(province_ols, ["label", "coefficient", "robust_se", "statistic", "approx_p_value", "significance"])}

Model fit: {ols_fit["fit_metric"]} = {ols_fit["fit_value"]}; fitted values range from {ols_fit["fitted_min"]} to {ols_fit["fitted_max"]}; out-of-bounds fitted values = {ols_fit["out_of_bounds"]}.

### Fractional logit main specification

{markdown_table(main_fractional, ["label", "coefficient", "robust_se", "statistic", "approx_p_value", "significance"])}

Model fit: {main_fit["fit_metric"]} = {main_fit["fit_value"]}; fitted values range from {main_fit["fitted_min"]} to {main_fit["fitted_max"]}; converged = {main_fit["converged"]} in {main_fit["iterations"]} iterations.

### Average partial effects from the main fractional logit

{markdown_table(average_partial_effects, ["label", "average_partial_effect"])}

### Scenario predictions from the main fractional logit

{markdown_table(scenarios, ["fragmentation_scenario", "irrigation_scenario", "weighted_average_predicted_insufficiency"])}

## Interpretation discipline

- These are district-level associations, not household-level causal effects.
- Province fixed effects absorb broad regional differences, but they do not solve endogeneity from omitted district characteristics.
- The weighted OLS model remains useful as a benchmark because its fitted values stay within the 0 to 1 range in this run.
- The fractional logit model should be treated as the main bounded-outcome specification for the final paper.

## Robustness direction

- The workflow now tests an alternative irrigation measure using irrigated holdings share.
- The complementary sufficiency outcome mirrors the main result by construction and is useful as a sign-check.
- The severe insufficiency outcome behaves differently in the current district data, so it should be treated as a separate dimension of deprivation rather than as a simple confirmation check for the main model.
- All coefficient tables and fit summaries are saved as CSV files for later table-building in the final paper.

## Next research steps

- Add paper-ready figures based on the generated output tables.
- Review whether additional district controls can be matched from official sources without breaking comparability.
- If NSCA microdata access becomes possible later, treat that as a separate extension rather than mixing it into the current district design.
"""


def enriched_analysis_rows(rows: list[dict[str, float | str]]) -> list[dict[str, str]]:
    fieldnames = [
        "district",
        "province",
        "total_holdings",
        "total_area_ha",
        "avg_holding_size_ha",
        "avg_parcels_per_holding",
        "irrigation_area_share",
        "irrigated_holdings_share",
        "ag_sufficiency_share",
        "ag_insufficiency_share",
        "severe_insuff_10_12_share",
        "loan_share",
        "subsidy_share",
        "power_tiller_share",
        "market_access_fast_share",
        "climate_impact_share",
        "frag_x_irrig_area",
        "frag_x_irrig_holdings",
    ]
    output_rows: list[dict[str, str]] = []
    for row in rows:
        output_rows.append(
            {
                field: str(row[field]) if field in {"district", "province"} else f"{float(row[field]):.6f}"
                for field in fieldnames
            }
        )
    return output_rows


def main() -> None:
    rows = read_dataset(DATASET)
    weights = as_array(rows, WEIGHT)

    summary = summary_rows(rows, weights)
    province_profiles = province_profile_rows(rows)
    correlations = correlation_rows(rows, weights)

    rankings: list[dict[str, str]] = []
    for variable in ("avg_parcels_per_holding", "irrigation_area_share", "ag_insufficiency_share"):
        rankings.extend(district_ranking_rows(rows, variable))

    model_results, fit_rows, key_rows, coefficient_store = run_models(rows)
    average_partial_effects = average_partial_effect_rows(rows, coefficient_store["fractional_logit_main"])
    scenarios = counterfactual_scenario_rows(rows, coefficient_store["fractional_logit_main"])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUT_DIR / "analysis_dataset.csv", enriched_analysis_rows(rows))
    write_csv(OUTPUT_DIR / "summary_statistics.csv", summary)
    write_csv(OUTPUT_DIR / "province_profiles.csv", province_profiles)
    write_csv(OUTPUT_DIR / "weighted_correlations.csv", correlations)
    write_csv(OUTPUT_DIR / "district_rankings.csv", rankings)
    write_csv(OUTPUT_DIR / "model_results.csv", model_results)
    write_csv(OUTPUT_DIR / "model_fit_summary.csv", fit_rows)
    write_csv(OUTPUT_DIR / "key_coefficient_summary.csv", key_rows)
    write_csv(OUTPUT_DIR / "average_partial_effects.csv", average_partial_effects)
    write_csv(OUTPUT_DIR / "counterfactual_scenarios.csv", scenarios)

    memo = build_markdown(
        rows=rows,
        summary=summary,
        province_profiles=province_profiles,
        correlations=correlations,
        rankings=rankings,
        model_results=model_results,
        fit_rows=fit_rows,
        average_partial_effects=average_partial_effects,
        scenarios=scenarios,
    )
    DOCUMENT_MEMO.parent.mkdir(parents=True, exist_ok=True)
    DOCUMENT_MEMO.write_text(memo, encoding="utf-8")

    print(f"Wrote final-paper analysis tables to {OUTPUT_DIR}")
    print(f"Updated research memo at {DOCUMENT_MEMO}")


if __name__ == "__main__":
    main()
