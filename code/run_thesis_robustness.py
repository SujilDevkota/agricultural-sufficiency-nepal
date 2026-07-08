#!/usr/bin/env python3
"""Chapter IV robustness checks: belt FE, parsimonious/unweighted specs, and a
pairs bootstrap. Reuses run_final_paper_analysis.py and gates on reproduction."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_final_paper_analysis as base  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "robustness"
MEMO = ROOT / "results" / "robustness" / "robustness_memo.md"

MOUNTAIN = {
    "Taplejung", "Sankhuwasabha", "Solukhumbu", "Dolakha", "Sindhupalchok",
    "Rasuwa", "Manang", "Mustang", "Dolpa", "Jumla", "Kalikot", "Mugu",
    "Humla", "Bajura", "Bajhang", "Darchula",
}
TERAI = {
    "Jhapa", "Morang", "Sunsari", "Saptari", "Siraha", "Dhanusha",
    "Mahottari", "Sarlahi", "Rautahat", "Bara", "Parsa", "Chitwan",
    "Nawalparasi East", "Nawalparasi West", "Rupandehi", "Kapilvastu",
    "Dang", "Banke", "Bardiya", "Kailali", "Kanchanpur",
}

# Scenario anchors (sample percentiles), matching the memo.
FRAG_LOW, FRAG_HIGH = 2.300, 3.500
IRRIG_LOW, IRRIG_HIGH = 0.230, 0.668

BOOT_REPS = 999
BOOT_SEED = 20260609


def belt_of(district: str) -> str:
    if district in MOUNTAIN:
        return "Mountain"
    if district in TERAI:
        return "Terai"
    return "Hill"


def design(rows, province_fe: bool, belt_fe: bool, parsimonious: bool = False):
    """Design matrix in the base script's column order."""
    columns = ["const", "avg_parcels_per_holding", "irrigation_area_share",
               "frag_x_irrig_area"]
    if parsimonious:
        columns += ["avg_holding_size_ha"]
    else:
        columns += list(base.CONTROL_VARS)
    vectors = [np.ones(len(rows))]
    vectors.extend(base.as_array(rows, c) for c in columns[1:])
    if province_fe:
        for province in base.PROVINCES[1:]:
            columns.append(f"province_{province}")
            vectors.append(np.array(
                [1.0 if r["province"] == province else 0.0 for r in rows]))
    if belt_fe:
        for belt in ("Mountain", "Hill"):  # Terai is the reference belt
            columns.append(f"belt_{belt}")
            vectors.append(np.array(
                [1.0 if belt_of(str(r["district"])) == belt else 0.0 for r in rows]))
    return np.column_stack(vectors), columns


def scenario_pred(beta, X, weights, frag, irrig):
    Xs = X.copy()
    Xs[:, 1] = frag
    Xs[:, 2] = irrig
    Xs[:, 3] = ((frag - base.CENTERING["avg_parcels_per_holding"])
                * (irrig - base.CENTERING["irrigation_area_share"]))
    return float(np.average(base.logistic(Xs @ beta),
                            weights=base.scaled_weights(weights)))


def run_spec(name, estimator, rows, y, weights, province_fe, belt_fe,
             parsimonious=False):
    X, columns = design(rows, province_fe, belt_fe, parsimonious)
    fn = base.weighted_ols_hc1 if estimator == "wols" else base.fractional_logit_hc1
    beta, se, stat, pvals, fit = fn(y, X, weights)
    records = []
    for i, term in enumerate(columns):
        records.append({
            "model": name,
            "estimator": estimator,
            "term": term,
            "coefficient": f"{beta[i]:.6f}",
            "robust_se": f"{se[i]:.6f}",
            "statistic": f"{stat[i]:.4f}",
            "approx_p_value": f"{pvals[i]:.4f}",
            "significance": base.significance_stars(float(pvals[i])),
        })
    fitrec = {
        "model": name, "estimator": estimator,
        "n_params": str(X.shape[1]),
        "fit_value": f"{fit['metric_value']:.4f}",
        "converged": "yes" if fit["converged"] else "no",
    }
    return beta, X, columns, records, fitrec


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = base.read_dataset(base.DATASET)
    weights = base.as_array(rows, base.WEIGHT)
    ones = np.ones_like(weights)
    y = base.as_array(rows, base.MAIN_OUTCOME)

    belts = [belt_of(str(r["district"])) for r in rows]
    counts = {b: belts.count(b) for b in ("Mountain", "Hill", "Terai")}
    assert counts == {"Mountain": 16, "Hill": 40, "Terai": 21}, counts

    # ---- reproduction gate: main specs must match the memo ----
    Xp, cols_p = design(rows, province_fe=True, belt_fe=False)
    b_ols, *_ = base.weighted_ols_hc1(y, Xp, weights)
    b_flog, se_flog, *_ = base.fractional_logit_hc1(y, Xp, weights)
    irr = cols_p.index("irrigation_area_share")
    # Main effects are at the weighted-mean profile (mean-centred
    # interactions); scenario predictions are parameterisation-invariant.
    assert abs(b_ols[irr] - (-0.468336)) < 5e-4, b_ols[irr]
    assert abs(b_flog[irr] - (-1.993204)) < 5e-4, b_flog[irr]
    s_ll = scenario_pred(b_flog, Xp, weights, FRAG_LOW, IRRIG_LOW)
    s_lh = scenario_pred(b_flog, Xp, weights, FRAG_LOW, IRRIG_HIGH)
    s_hl = scenario_pred(b_flog, Xp, weights, FRAG_HIGH, IRRIG_LOW)
    s_hh = scenario_pred(b_flog, Xp, weights, FRAG_HIGH, IRRIG_HIGH)
    assert abs(s_ll - 0.6787) < 1e-3 and abs(s_lh - 0.4815) < 1e-3
    assert abs(s_hl - 0.6993) < 1e-3 and abs(s_hh - 0.4804) < 1e-3
    print("Reproduction gate passed: main OLS/flogit and scenarios match the memo.")

    # ---- new specifications ----
    all_records, all_fits = [], []
    specs = [
        ("wols_belt_fe", "wols", weights, False, True, False),
        ("flogit_belt_fe", "flogit", weights, False, True, False),
        ("flogit_province_belt_fe", "flogit", weights, True, True, False),
        ("flogit_parsimonious_province_fe", "flogit", weights, True, False, True),
        ("ols_unweighted_province_fe", "wols", ones, True, False, False),
        ("flogit_unweighted_province_fe", "flogit", ones, True, False, False),
    ]
    headline = {}
    for name, est, w, pfe, bfe, pars in specs:
        beta, X, columns, recs, fitrec = run_spec(name, est, rows, y, w, pfe, bfe, pars)
        all_records.extend(recs)
        all_fits.append(fitrec)
        i = columns.index("irrigation_area_share")
        j = columns.index("frag_x_irrig_area")
        k = columns.index("avg_parcels_per_holding")
        headline[name] = {
            "irrigation": (recs[i]["coefficient"], recs[i]["robust_se"], recs[i]["approx_p_value"], recs[i]["significance"]),
            "fragmentation": (recs[k]["coefficient"], recs[k]["robust_se"], recs[k]["approx_p_value"], recs[k]["significance"]),
            "interaction": (recs[j]["coefficient"], recs[j]["robust_se"], recs[j]["approx_p_value"], recs[j]["significance"]),
            "fit": fitrec["fit_value"], "n_params": fitrec["n_params"],
        }
        print(f"{name:34} irrigation={recs[i]['coefficient']} (p={recs[i]['approx_p_value']}{recs[i]['significance']})  fit={fitrec['fit_value']}")

    # ---- pairs bootstrap of the main fractional logit (province FE) ----
    rng = np.random.default_rng(BOOT_SEED)
    n = len(rows)
    boot_irr, boot_gap_lowfrag, boot_gap_highfrag = [], [], []
    failures = 0
    for _ in range(BOOT_REPS):
        idx = rng.integers(0, n, size=n)
        rs = [rows[i] for i in idx]
        yb = y[idx]
        wb = weights[idx]
        try:
            Xb, colsb = design(rs, province_fe=True, belt_fe=False)
            bb, *_ = base.fractional_logit_hc1(yb, Xb, wb)
            ii = colsb.index("irrigation_area_share")
            boot_irr.append(float(bb[ii]))
            gl = scenario_pred(bb, Xb, wb, FRAG_LOW, IRRIG_HIGH) - \
                 scenario_pred(bb, Xb, wb, FRAG_LOW, IRRIG_LOW)
            gh = scenario_pred(bb, Xb, wb, FRAG_HIGH, IRRIG_HIGH) - \
                 scenario_pred(bb, Xb, wb, FRAG_HIGH, IRRIG_LOW)
            boot_gap_lowfrag.append(gl)
            boot_gap_highfrag.append(gh)
        except Exception:
            failures += 1
    boot_irr = np.array(boot_irr)
    gaps_l = np.array(boot_gap_lowfrag)
    gaps_h = np.array(boot_gap_highfrag)

    def ci(a):
        return float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))

    point_gap_l = s_lh - s_ll
    point_gap_h = s_hh - s_hl
    boot_summary = [
        {"quantity": "flogit irrigation coefficient",
         "point": f"{b_flog[irr]:.4f}", "analytic_se": f"{se_flog[irr]:.4f}",
         "boot_se": f"{boot_irr.std(ddof=1):.4f}",
         "ci_low": f"{ci(boot_irr)[0]:.4f}", "ci_high": f"{ci(boot_irr)[1]:.4f}"},
        {"quantity": "scenario gap, low fragmentation (high - low irrigation)",
         "point": f"{point_gap_l:.4f}", "analytic_se": "",
         "boot_se": f"{gaps_l.std(ddof=1):.4f}",
         "ci_low": f"{ci(gaps_l)[0]:.4f}", "ci_high": f"{ci(gaps_l)[1]:.4f}"},
        {"quantity": "scenario gap, high fragmentation (high - low irrigation)",
         "point": f"{point_gap_h:.4f}", "analytic_se": "",
         "boot_se": f"{gaps_h.std(ddof=1):.4f}",
         "ci_low": f"{ci(gaps_h)[0]:.4f}", "ci_high": f"{ci(gaps_h)[1]:.4f}"},
    ]
    print(f"bootstrap: {len(boot_irr)} successful replications, {failures} failures")
    for r in boot_summary:
        print(f"  {r['quantity']}: {r['point']} [{r['ci_low']}, {r['ci_high']}] boot SE {r['boot_se']}")

    # ---- write outputs ----
    base.write_csv(OUT_DIR / "robustness_results.csv", all_records)
    base.write_csv(OUT_DIR / "robustness_fit.csv", all_fits)
    base.write_csv(OUT_DIR / "bootstrap_summary.csv", boot_summary)
    belt_rows = [{"district": str(r["district"]), "belt": belt_of(str(r["district"])),
                  "province": str(r["province"])} for r in rows]
    base.write_csv(OUT_DIR / "district_belts.csv", belt_rows)

    lines = ["# Thesis Robustness Memo", "",
             "Generated by `code/run_thesis_robustness.py` "
             "(reproduction-gated against the main memo).", "",
             f"- Belt counts: Mountain 16, Hill 40, Terai 21 (reference: Terai)",
             f"- Bootstrap: {len(boot_irr)} pairs replications, seed {BOOT_SEED}.", "",
             "## Irrigation coefficient across specifications", "",
             "| specification | irrigation coef | robust SE | p | fit | params |",
             "| --- | --- | --- | --- | --- | --- |"]
    for name, h in headline.items():
        c, s, p, st = h["irrigation"]
        lines.append(f"| {name} | {c}{st} | {s} | {p} | {h['fit']} | {h['n_params']} |")
    lines += ["", "## Fragmentation and interaction across specifications", "",
              "| specification | fragmentation (p) | interaction (p) |",
              "| --- | --- | --- |"]
    for name, h in headline.items():
        cf, _, pf, stf = h["fragmentation"]
        cx, _, px, stx = h["interaction"]
        lines.append(f"| {name} | {cf}{stf} ({pf}) | {cx}{stx} ({px}) |")
    lines += ["", "## Bootstrap summary", "",
              "| quantity | point | boot SE | 95% CI |", "| --- | --- | --- | --- |"]
    for r in boot_summary:
        lines.append(f"| {r['quantity']} | {r['point']} | {r['boot_se']} | "
                     f"[{r['ci_low']}, {r['ci_high']}] |")
    MEMO.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_DIR} and {MEMO}")


if __name__ == "__main__":
    main()
