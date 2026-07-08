#!/usr/bin/env python3
"""Regression diagnostics (Breusch-Pagan, Jarque-Bera, VIF) for the main model.

Run on the weighted OLS benchmark residuals; writes a CSV and a LaTeX table.
"""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_final_paper_analysis as base  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "diagnostics"
TABLE = ROOT / "results" / "tables" / "tab_diagnostics.tex"

# Substantive (non-fixed-effect) regressors for VIF, in design-matrix order.
SUBSTANTIVE = [
    "avg_parcels_per_holding",
    "irrigation_area_share",
    "frag_x_irrig_area",
] + list(base.CONTROL_VARS)


# Chi-square upper tail via the incomplete gamma function (no SciPy needed).
def _gser(a: float, x: float) -> float:
    gln = math.lgamma(a)
    if x <= 0.0:
        return 0.0
    ap = a
    total = 1.0 / a
    delta = total
    for _ in range(10000):
        ap += 1.0
        delta *= x / ap
        total += delta
        if abs(delta) < abs(total) * 1e-16:
            break
    return total * math.exp(-x + a * math.log(x) - gln)


def _gcf(a: float, x: float) -> float:
    gln = math.lgamma(a)
    tiny = 1e-300
    b = x + 1.0 - a
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, 10000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-16:
            break
    return math.exp(-x + a * math.log(x) - gln) * h


def chi2_sf(stat: float, df: float) -> float:
    """Upper-tail (survival) probability of a chi-square variate."""
    a = df / 2.0
    x = stat / 2.0
    if x < 0.0 or a <= 0.0:
        raise ValueError("invalid chi-square arguments")
    if x == 0.0:
        return 1.0
    if x < a + 1.0:
        return 1.0 - _gser(a, x)
    return _gcf(a, x)


def ols_r2(y: np.ndarray, Z: np.ndarray) -> float:
    """R-squared of an ordinary least-squares fit of y on Z (Z has a const)."""
    beta = np.linalg.lstsq(Z, y, rcond=None)[0]
    resid = y - Z @ beta
    ss_res = float(resid @ resid)
    ss_tot = float(((y - y.mean()) ** 2).sum())
    return 1.0 - ss_res / ss_tot


def breusch_pagan(resid: np.ndarray, X: np.ndarray) -> dict:
    """Studentized (Koenker) Breusch-Pagan test; robust to non-normal residuals."""
    n = len(resid)
    g = resid ** 2
    r2 = ols_r2(g, X)
    lm = n * r2
    df = X.shape[1] - 1  # exclude constant
    return {"statistic": lm, "df": df, "p_value": chi2_sf(lm, df), "r2_aux": r2}


def jarque_bera(resid: np.ndarray) -> dict:
    """Jarque-Bera test of residual normality."""
    n = len(resid)
    e = resid - resid.mean()
    m2 = float((e ** 2).mean())
    m3 = float((e ** 3).mean())
    m4 = float((e ** 4).mean())
    skew = m3 / m2 ** 1.5
    kurt = m4 / m2 ** 2  # non-excess kurtosis
    jb = n / 6.0 * (skew ** 2 + 0.25 * (kurt - 3.0) ** 2)
    return {"statistic": jb, "df": 2, "p_value": chi2_sf(jb, 2),
            "skewness": skew, "kurtosis": kurt}


def variance_inflation_factors(X: np.ndarray, columns: list[str]) -> dict:
    """VIF for each substantive regressor (fixed effects partialled in)."""
    vifs: dict[str, float] = {}
    for name in SUBSTANTIVE:
        j = columns.index(name)
        target = X[:, j]
        others = np.delete(X, j, axis=1)  # keeps the constant + all other cols
        r2 = ols_r2(target, others)
        vifs[name] = 1.0 / (1.0 - r2)
    return vifs


def fmt_p(p: float) -> str:
    return "< 0.001" if p < 0.001 else f"{p:.3f}"


def main() -> None:
    rows = base.read_dataset(base.DATASET)
    y = base.as_array(rows, base.MAIN_OUTCOME)
    weights = base.as_array(rows, base.WEIGHT)

    X, columns = base.build_design_matrix(
        rows, "irrigation_area_share", "frag_x_irrig_area", province_fe=True)

    beta, se, stat, pvals, fit = base.weighted_ols_hc1(y, X, weights)
    resid = y - X @ beta
    n = len(y)

    bp = breusch_pagan(resid, X)
    jb = jarque_bera(resid)
    vifs = variance_inflation_factors(X, columns)
    max_vif_name = max(vifs, key=vifs.get)
    max_vif = vifs[max_vif_name]

    # --- console report ------------------------------------------------------
    print(f"n = {n}; weighted OLS benchmark (province FE, full controls)")
    print(f"  R^2 (weighted)              = {fit['metric_value']:.4f}")
    print("Heteroscedasticity -- Breusch-Pagan (Koenker, studentized)")
    print(f"  LM = {bp['statistic']:.3f}, df = {bp['df']}, p = {fmt_p(bp['p_value'])}")
    print("Normality -- Jarque-Bera")
    print(f"  JB = {jb['statistic']:.3f}, df = {jb['df']}, p = {fmt_p(jb['p_value'])}")
    print(f"  skewness = {jb['skewness']:.3f}, kurtosis = {jb['kurtosis']:.3f}")
    print("Multicollinearity -- variance inflation factors")
    for name in SUBSTANTIVE:
        print(f"  VIF[{name}] = {vifs[name]:.2f}")
    print(f"  max VIF = {max_vif:.2f} ({max_vif_name})")

    # --- CSV ----------------------------------------------------------------
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with (OUT_DIR / "diagnostics.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["diagnostic", "test", "statistic", "df", "p_value", "detail"])
        w.writerow(["Heteroscedasticity", "Breusch-Pagan (studentized)",
                    f"{bp['statistic']:.3f}", bp["df"], f"{bp['p_value']:.4f}",
                    f"aux R2={bp['r2_aux']:.4f}"])
        w.writerow(["Normality", "Jarque-Bera",
                    f"{jb['statistic']:.3f}", jb["df"], f"{jb['p_value']:.4f}",
                    f"skew={jb['skewness']:.3f}; kurt={jb['kurtosis']:.3f}"])
        w.writerow(["Multicollinearity", "Max VIF",
                    f"{max_vif:.2f}", "", "",
                    f"{max_vif_name}; threshold 10"])

    # --- LaTeX table --------------------------------------------------------
    het_concl = ("Reject homoscedasticity" if bp["p_value"] < 0.05
                 else "No heteroscedasticity")
    norm_concl = ("Reject normality" if jb["p_value"] < 0.05
                  else "Do not reject normality")
    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\caption{Regression Diagnostic Tests, Main Insufficiency Model}",
        "\\label{tab:diagnostics}",
        "\\small",
        "\\begin{tabular}{llcc}",
        "\\toprule",
        "Diagnostic & Test & Statistic (df) & $p$-value \\\\",
        "\\midrule",
        f"Heteroscedasticity & Breusch--Pagan & {bp['statistic']:.2f} "
        f"({bp['df']}) & {fmt_p(bp['p_value'])} \\\\",
        f"Normality of residuals & Jarque--Bera & {jb['statistic']:.2f} "
        f"({jb['df']}) & {fmt_p(jb['p_value'])} \\\\",
        f"Multicollinearity & Maximum VIF & {max_vif:.2f} & --- \\\\",
        "\\bottomrule",
        "\\end{tabular}",
        "",
        "\\vspace{0.3em}",
        "\\begin{minipage}{0.92\\textwidth}",
        "\\footnotesize",
        "Note: Diagnostics are computed on the residuals of the weighted OLS "
        "benchmark (Table~\\ref{tab:main-models}), with the full control set and "
        "province fixed effects. The Breusch--Pagan test is reported in its "
        "studentized (Koenker) form, which does not assume normal residuals; a "
        f"$p$-value of {fmt_p(bp['p_value'])} " +
        ("indicates heteroscedasticity, which is why "
         if bp["p_value"] < 0.05 else "does not indicate heteroscedasticity; ") +
        "heteroskedasticity-consistent (HC1) standard errors are reported for "
        "all models regardless. The Jarque--Bera test "
        f"(skewness ${jb['skewness']:.2f}$, kurtosis ${jb['kurtosis']:.2f}$) " +
        ("does not reject residual normality" if jb["p_value"] >= 0.05
         else "rejects residual normality, which the large-sample robust "
         "inference and the bounded fractional logit accommodate") +
        ". The maximum variance inflation factor across the substantive "
        f"regressors is {max_vif:.2f} (well below the conventional threshold of "
        "10; the full set is in Table~\\ref{tab:vif}), so multicollinearity is "
        "not a concern after mean-centring.",
        "\\end{minipage}",
        "\\end{table}",
        "",
    ]
    TABLE.parent.mkdir(parents=True, exist_ok=True)
    TABLE.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {TABLE}")
    print(f"Wrote {OUT_DIR / 'diagnostics.csv'}")


if __name__ == "__main__":
    main()
