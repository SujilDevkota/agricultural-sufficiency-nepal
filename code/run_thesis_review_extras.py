#!/usr/bin/env python3
"""Extra review analyses: VIF, interaction tests, and robustness checks.

Reuses the base estimators and design helper. Output: results/review_extras/*.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_final_paper_analysis as base  # noqa: E402
from run_thesis_robustness import design  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "review_extras"
VALLEY = {"Kathmandu", "Lalitpur", "Bhaktapur"}


def ols_r2(y, X):
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    resid = y - X @ beta
    ss_res = float(np.sum(resid ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    return 1.0 - ss_res / ss_tot


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = base.read_dataset(base.DATASET)
    weights = base.as_array(rows, base.WEIGHT)
    y = base.as_array(rows, base.MAIN_OUTCOME)

    # ---------- 1. VIF for the main province-FE specification ----------
    X, cols = design(rows, province_fe=True, belt_fe=False)
    substantive = ["avg_parcels_per_holding", "irrigation_area_share",
                   "frag_x_irrig_area", "avg_holding_size_ha", "loan_share",
                   "subsidy_share", "power_tiller_share",
                   "market_access_fast_share", "climate_impact_share"]
    label = {
        "avg_parcels_per_holding": "Average parcels per holding",
        "irrigation_area_share": "Irrigation area share",
        "frag_x_irrig_area": "Fragmentation $\\times$ irrigation",
        "avg_holding_size_ha": "Average holding size (ha)",
        "loan_share": "Loan share", "subsidy_share": "Subsidy share",
        "power_tiller_share": "Power tiller share",
        "market_access_fast_share": "Fast market access share",
        "climate_impact_share": "Climate impact share",
    }
    vif_rows = []
    for term in substantive:
        j = cols.index(term)
        others = [k for k in range(X.shape[1]) if k != j]
        r2 = ols_r2(X[:, j], X[:, others])
        vif = 1.0 / (1.0 - r2) if r2 < 1 else float("inf")
        vif_rows.append({"term": term, "label": label[term], "vif": f"{vif:.2f}"})
        print(f"VIF {term:28} = {vif:7.2f}")
    base.write_csv(OUT / "vif.csv", vif_rows)

    # ---------- 2. market-access x holding-size interaction ----------
    # main design plus an explicit market x size term
    mkt = base.as_array(rows, "market_access_fast_share")
    size = base.as_array(rows, "avg_holding_size_ha")
    Xm = np.column_stack([X, mkt * size])
    cols_m = cols + ["market_x_size"]
    beta, se, stat, p, fit = base.fractional_logit_hc1(y, Xm, weights)
    mkt_rows = []
    for term in ["market_access_fast_share", "avg_holding_size_ha", "market_x_size"]:
        k = cols_m.index(term)
        mkt_rows.append({"term": term, "coefficient": f"{beta[k]:.4f}",
                         "robust_se": f"{se[k]:.4f}", "p": f"{p[k]:.4f}",
                         "significance": base.significance_stars(float(p[k]))})
        print(f"market-test {term:26} coef={beta[k]:.4f} p={p[k]:.4f}")
    base.write_csv(OUT / "market_interaction.csv", mkt_rows)

    # ---------- 3. parsimonious WITHOUT interaction ----------
    # parsimonious cols: const, frag, irrig, frag_x_irrig, size + province FE
    Xp, colsp = design(rows, province_fe=True, belt_fe=False, parsimonious=True)
    drop = colsp.index("frag_x_irrig_area")
    keep = [k for k in range(Xp.shape[1]) if k != drop]
    Xpn = Xp[:, keep]
    colspn = [colsp[k] for k in keep]
    bpn, spn, tpn, ppn, fpn = base.fractional_logit_hc1(y, Xpn, weights)
    def grab(cols_, b, s, p, term):
        if term not in cols_:
            return {"coefficient": "", "robust_se": "", "p": "",
                    "significance": ""}
        k = cols_.index(term)
        return {"coefficient": f"{b[k]:.4f}", "robust_se": f"{s[k]:.4f}",
                "p": f"{p[k]:.4f}",
                "significance": base.significance_stars(float(p[k]))}
    extra_specs = []
    extra_specs.append({"model": "flogit_parsimonious_noint",
                        "label": "Fractional logit, parsimonious, no interaction",
                        "fit": f"{fpn['metric_value']:.4f}",
                        "frag": grab(colspn, bpn, spn, ppn, "avg_parcels_per_holding"),
                        "irrig": grab(colspn, bpn, spn, ppn, "irrigation_area_share"),
                        "inter": {"coefficient": "", "robust_se": "", "significance": ""}})
    print(f"parsimonious-no-int irrigation coef={bpn[colspn.index('irrigation_area_share')]:.4f} "
          f"(p={ppn[colspn.index('irrigation_area_share')]:.4f})")

    # ---------- 4. exclude Kathmandu-valley districts ----------
    keep_rows = [i for i, r in enumerate(rows) if str(r["district"]) not in VALLEY]
    rv = [rows[i] for i in keep_rows]
    yv = y[keep_rows]; wv = weights[keep_rows]
    Xv, colsv = design(rv, province_fe=True, belt_fe=False)
    bv, sv, tv, pv, fv = base.fractional_logit_hc1(yv, Xv, wv)
    extra_specs.append({"model": "flogit_valley_excluded",
                        "label": f"Fractional logit, province FE, valley excluded ($n$={len(rv)})",
                        "fit": f"{fv['metric_value']:.4f}",
                        "frag": grab(colsv, bv, sv, pv, "avg_parcels_per_holding"),
                        "irrig": grab(colsv, bv, sv, pv, "irrigation_area_share"),
                        "inter": grab(colsv, bv, sv, pv, "frag_x_irrig_area")})
    print(f"valley-excluded irrigation coef={bv[colsv.index('irrigation_area_share')]:.4f} "
          f"(p={pv[colsv.index('irrigation_area_share')]:.4f}), n={len(rv)}")

    # ---------- 5. household-size control (external examiner, §4.1) ----------
    # Members per holding from NSCA Table 26 (farm population).
    hh = {}
    with (ROOT / "data" / "raw" / "nsonepal" / "table_26_farm_population.csv"
          ).open(newline="", encoding="utf-8") as fh:
        import csv as _csv
        for r in _csv.DictReader(fh):
            hh[r["district"]] = ((float(r["farm_pop_male"])
                                  + float(r["farm_pop_female"]))
                                 / float(r["total_holdings"]))
    hh_col = np.array([hh[str(r["district"])] for r in rows])
    hh_mean = float(np.average(hh_col, weights=weights))
    print(f"household size: weighted mean {hh_mean:.3f} members/holding, "
          f"range {hh_col.min():.2f}-{hh_col.max():.2f}")
    Xh = np.column_stack([X, hh_col])
    cols_h = cols + ["avg_household_size_members"]
    bh, sh, th, ph, fh_fit = base.fractional_logit_hc1(y, Xh, weights)
    extra_specs.append({"model": "flogit_household_size",
                        "label": "Fractional logit, household-size control",
                        "fit": f"{fh_fit['metric_value']:.4f}",
                        "frag": grab(cols_h, bh, sh, ph, "avg_parcels_per_holding"),
                        "irrig": grab(cols_h, bh, sh, ph, "irrigation_area_share"),
                        "inter": grab(cols_h, bh, sh, ph, "frag_x_irrig_area")})
    khh = cols_h.index("avg_household_size_members")
    kirr = cols_h.index("irrigation_area_share")
    base.write_csv(OUT / "household_size_control.csv", [{
        "term": "avg_household_size_members",
        "coefficient": f"{bh[khh]:.4f}", "robust_se": f"{sh[khh]:.4f}",
        "p": f"{ph[khh]:.4f}",
        "weighted_mean_household_size": f"{hh_mean:.4f}",
    }])
    print(f"household-size control: irrigation coef={bh[kirr]:.4f} "
          f"(p={ph[kirr]:.4f}); household size coef={bh[khh]:.4f} "
          f"(p={ph[khh]:.4f})")

    # ---------- 6. parcels-per-hectare fragmentation proxy (examiner, §4.5) --
    # Parcels per hectare; centred like the main vars before interacting.
    ppha = np.array([float(r["total_parcels"]) / float(r["total_area_ha"])
                     for r in rows])
    frag_c_mean = float(np.average(ppha, weights=weights))
    irrig = base.as_array(rows, "irrigation_area_share")
    irrig_c = irrig - base.CENTERING["irrigation_area_share"]
    Xp2, colsp2 = design(rows, province_fe=True, belt_fe=False)
    jf = colsp2.index("avg_parcels_per_holding")
    ji = colsp2.index("frag_x_irrig_area")
    Xp2[:, jf] = ppha
    Xp2[:, ji] = (ppha - frag_c_mean) * irrig_c
    colsp2[jf] = "parcels_per_ha"
    colsp2[ji] = "ppha_x_irrig_area"
    bp2, sp2, tp2, pp2, fp2 = base.fractional_logit_hc1(y, Xp2, weights)
    extra_specs.append({"model": "flogit_parcels_per_ha",
                        "label": "Fractional logit, fragmentation as parcels per hectare",
                        "fit": f"{fp2['metric_value']:.4f}",
                        "frag": grab(colsp2, bp2, sp2, pp2, "parcels_per_ha"),
                        "irrig": grab(colsp2, bp2, sp2, pp2, "irrigation_area_share"),
                        "inter": grab(colsp2, bp2, sp2, pp2, "ppha_x_irrig_area")})
    print(f"parcels-per-ha proxy: frag coef={bp2[colsp2.index('parcels_per_ha')]:.4f} "
          f"(p={pp2[colsp2.index('parcels_per_ha')]:.4f}); irrigation "
          f"coef={bp2[colsp2.index('irrigation_area_share')]:.4f} "
          f"(p={pp2[colsp2.index('irrigation_area_share')]:.4f}); weighted mean "
          f"{frag_c_mean:.2f} parcels/ha")

    # ---------- 7. fitted-vs-actual correlation, main fractional logit ------
    bmain, *_ = base.fractional_logit_hc1(y, X, weights)
    fitted = base.logistic(X @ bmain)
    corr = float(np.corrcoef(fitted, y)[0, 1])
    base.write_csv(OUT / "fit_correlation.csv", [{
        "model": "fractional_logit_main",
        "fitted_actual_correlation": f"{corr:.4f}",
        "fitted_actual_r2": f"{corr ** 2:.4f}",
    }])
    print(f"fitted-vs-actual correlation (main flogit): {corr:.4f} "
          f"(squared {corr ** 2:.4f})")

    # flatten extra_specs to a CSV
    flat = []
    for s in extra_specs:
        flat.append({
            "model": s["model"], "label": s["label"], "fit": s["fit"],
            "frag_coef": s["frag"]["coefficient"], "frag_sig": s["frag"]["significance"],
            "frag_p": s["frag"].get("p", ""),
            "irrig_coef": s["irrig"]["coefficient"], "irrig_sig": s["irrig"]["significance"],
            "irrig_p": s["irrig"].get("p", ""),
            "inter_coef": s["inter"]["coefficient"], "inter_sig": s["inter"]["significance"],
            "inter_p": s["inter"].get("p", ""),
        })
    base.write_csv(OUT / "extra_specs.csv", flat)
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
