#!/usr/bin/env python3
"""Generate LaTeX tables for Chapter IV and the Annex from the analysis CSVs.

Reads results/{analysis,robustness}/*.csv; writes results/tables/*.tex.
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / "results" / "analysis"
R = ROOT / "results" / "robustness"
OUT = ROOT / "results" / "tables"
DATA = ROOT / "data" / "processed" / "district_research_dataset.csv"


def rd(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def w(name: str, content: str) -> None:
    (OUT / name).write_text(content, encoding="utf-8")
    print("wrote", name)


def tex_escape(s: str) -> str:
    return s.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")


def f3(x) -> str:
    return f"{float(x):.3f}"


def coef_cell(coef, stars) -> str:
    return f"{float(coef):.4f}{stars}"


def main() -> None:
    OUT.mkdir(exist_ok=True)

    # ----- 4.1 summary statistics --------------------------------------
    rows = rd(A / "summary_statistics.csv")
    body = "\n".join(
        f"{tex_escape(r['label'])} & {f3(r['mean'])} & {f3(r['weighted_mean'])} & "
        f"{f3(r['weighted_std_dev'])} & {f3(r['min'])} & {f3(r['max'])} \\\\"
        for r in rows)
    w("tab_summary_stats.tex", rf"""\begin{{table}}[htbp]
\centering
\caption{{Summary Statistics of the District Variables}}
\label{{tab:summary-stats}}
\footnotesize
\setlength{{\tabcolsep}}{{4pt}}
\begin{{tabular}}{{lccccc}}
\toprule
Variable & Mean & Weighted mean & Weighted SD & Min & Max \\
\midrule
{body}
\bottomrule
\end{{tabular}}

\vspace{{0.3em}}
\begin{{minipage}}{{0.94\textwidth}}
\footnotesize
Note: 77 districts. Weighted statistics use the total number of agricultural
holdings in each district as weights. Source: author's computations from the
NSCA 2021/22 district tables (NSO, 2023).
\end{{minipage}}
\end{{table}}
""")

    # ----- 4.2 province profile -----------------------------------------
    rows = rd(A / "province_profiles.csv")
    body = "\n".join(
        f"{tex_escape(r['province'])} & {r['district_count']} & "
        f"{f3(r['holdings_share'])} & {f3(r['avg_parcels_weighted_mean'])} & "
        f"{f3(r['irrigation_area_weighted_mean'])} & {f3(r['insufficiency_weighted_mean'])} \\\\"
        for r in rows)
    w("tab_province_profile.tex", rf"""\begin{{table}}[htbp]
\centering
\caption{{Province Profile of Fragmentation, Irrigation, and Insufficiency}}
\label{{tab:province-profile}}
\footnotesize
\setlength{{\tabcolsep}}{{4pt}}
\begin{{tabular}}{{lccccc}}
\toprule
Province & Districts & Holdings share & Parcels & Irrig.\ share & Insuff.\ share \\
\midrule
{body}
\bottomrule
\end{{tabular}}

\vspace{{0.3em}}
\begin{{minipage}}{{0.94\textwidth}}
\footnotesize
Note: weighted province means using district holdings as weights.
Source: author's computations from the NSCA 2021/22 district tables.
\end{{minipage}}
\end{{table}}
""")

    # ----- 4.2b ecological-belt profile ----------------------------------
    belts_map = {r["district"]: r["belt"] for r in rd(R / "district_belts.csv")}
    data_all = rd(DATA)
    tot_hold_all = sum(float(r["total_holdings"]) for r in data_all)
    lines = []
    for belt in ("Mountain", "Hill", "Terai"):
        rowsb = [r for r in data_all if belts_map[r["district"]] == belt]
        tw = sum(float(r["total_holdings"]) for r in rowsb)

        def wm(col):
            return sum(float(r[col]) * float(r["total_holdings"]) for r in rowsb) / tw

        lines.append(
            f"{belt} & {len(rowsb)} & {tw / tot_hold_all:.3f} & "
            f"{wm('avg_parcels_per_holding'):.3f} & {wm('irrigation_area_share'):.3f} & "
            f"{wm('ag_insufficiency_share'):.3f} & {wm('severe_insuff_10_12_share'):.3f} \\\\")
    body = "\n".join(lines)
    w("tab_belt_profile.tex", rf"""\begin{{table}}[htbp]
\centering
\caption{{Ecological-Belt Profile of Fragmentation, Irrigation, and Insufficiency}}
\label{{tab:belt-profile}}
\footnotesize
\setlength{{\tabcolsep}}{{4pt}}
\begin{{tabular}}{{lcccccc}}
\toprule
Belt & Districts & Holdings share & Parcels & Irrig.\ share & Insuff.\ share & Severe share \\
\midrule
{body}
\bottomrule
\end{{tabular}}

\vspace{{0.3em}}
\begin{{minipage}}{{0.94\textwidth}}
\footnotesize
Note: holdings-weighted belt means using district holdings as weights. ``Severe
share'' is the share of holdings reporting 10--12 months of food insufficiency.
Source: author's computations from the NSCA 2021/22 district tables.
\end{{minipage}}
\end{{table}}
""")

    # ----- 4.2c weighted correlation matrix of the model variables -------
    mat_vars = [
        ("avg_parcels_per_holding", "Frag."),
        ("irrigation_area_share", "Irrig."),
        ("avg_holding_size_ha", "Size"),
        ("loan_share", "Loan"),
        ("subsidy_share", "Subsidy"),
        ("power_tiller_share", "Mech."),
        ("market_access_fast_share", "Market"),
        ("climate_impact_share", "Climate"),
        ("ag_insufficiency_share", "Insuff."),
    ]
    wts = [float(r["total_holdings"]) for r in data_all]
    sw = sum(wts)

    def col(name, row):
        if name == "avg_holding_size_ha":  # derived, not stored in the raw CSV
            return float(row["total_area_ha"]) / float(row["total_holdings"])
        return float(row[name])

    def wcorr(ca, cb):
        a = [col(ca, r) for r in data_all]
        b = [col(cb, r) for r in data_all]
        ma = sum(x * w for x, w in zip(a, wts)) / sw
        mb = sum(x * w for x, w in zip(b, wts)) / sw
        cov = sum(w * (x - ma) * (y - mb) for x, y, w in zip(a, b, wts)) / sw
        va = sum(w * (x - ma) ** 2 for x, w in zip(a, wts)) / sw
        vb = sum(w * (y - mb) ** 2 for y, w in zip(b, wts)) / sw
        return cov / (va * vb) ** 0.5

    lines = []
    for i, (ci, li) in enumerate(mat_vars):
        cells = [li]
        for j, (cj, lj) in enumerate(mat_vars):
            if j > i:
                cells.append("")
            elif j == i:
                cells.append("1")
            else:
                cells.append(f"{wcorr(ci, cj):.2f}")
        lines.append(" & ".join(cells) + r" \\")
    body = "\n".join(lines)
    heads = " & ".join(l for _, l in mat_vars)
    w("tab_corr_matrix.tex", rf"""\begin{{table}}[htbp]
\centering
\caption{{Weighted Correlation Matrix of the Model Variables}}
\label{{tab:corr-matrix}}
\footnotesize
\setlength{{\tabcolsep}}{{3.5pt}}
\begin{{tabular}}{{l{'c' * len(mat_vars)}}}
\toprule
 & {heads} \\
\midrule
{body}
\bottomrule
\end{{tabular}}

\vspace{{0.3em}}
\begin{{minipage}}{{0.94\textwidth}}
\footnotesize
Note: holdings-weighted pairwise correlations across the 77 districts, lower
triangle. ``Insuff.'' is the agricultural insufficiency share (the outcome);
the remaining variables are defined in Table~\ref{{tab:opdef}}.
\end{{minipage}}
\end{{table}}
""")

    # ----- 4.3 district extremes ----------------------------------------
    ranks = rd(A / "district_rankings.csv")
    # print from the full-precision dataset so shares match Annex I / Table 4.8
    full = {r["district"]: r["ag_insufficiency_share"] for r in rd(DATA)}
    ins_hi = [r for r in ranks if r["variable"] == "ag_insufficiency_share" and r["direction"] == "highest"][:5]
    ins_lo = [r for r in ranks if r["variable"] == "ag_insufficiency_share" and r["direction"] == "lowest"][:5]
    body = "\n".join(
        f"{hi['rank']} & {tex_escape(hi['district'])} ({tex_escape(hi['province'])}) & {f3(full[hi['district']])} & "
        f"{tex_escape(lo['district'])} ({tex_escape(lo['province'])}) & {f3(full[lo['district']])} \\\\"
        for hi, lo in zip(ins_hi, ins_lo))
    w("tab_district_extremes.tex", rf"""\begin{{table}}[htbp]
\centering
\caption{{Districts With the Highest and Lowest Agricultural Insufficiency Shares}}
\label{{tab:district-extremes}}
\small
\begin{{tabular}}{{clclc}}
\toprule
 & \multicolumn{{2}}{{c}}{{Highest insufficiency}} & \multicolumn{{2}}{{c}}{{Lowest insufficiency}} \\
\cmidrule(lr){{2-3}}\cmidrule(lr){{4-5}}
Rank & District (province) & Share & District (province) & Share \\
\midrule
{body}
\bottomrule
\end{{tabular}}
\end{{table}}
""")

    # ----- 4.4 weighted correlations ------------------------------------
    rows = rd(A / "weighted_correlations.csv")
    body = "\n".join(
        f"{tex_escape(r['label'])} & {f3(r['correlation_with_outcome'])} & "
        f"{f3(r['weighted_correlation_with_outcome'])} \\\\" for r in rows)
    w("tab_weighted_correlations.tex", rf"""\begin{{table}}[htbp]
\centering
\caption{{Correlations With the Agricultural Insufficiency Share}}
\label{{tab:correlations}}
\small
\begin{{tabular}}{{lcc}}
\toprule
Variable & Unweighted correlation & Weighted correlation \\
\midrule
{body}
\bottomrule
\end{{tabular}}

\vspace{{0.3em}}
\begin{{minipage}}{{0.85\textwidth}}
\footnotesize
Note: weighted correlations use district holdings as weights.
\end{{minipage}}
\end{{table}}
""")

    # ----- 4.5 main models ----------------------------------------------
    res = rd(A / "model_results.csv")
    fit = {r["model"]: r for r in rd(A / "model_fit_summary.csv")}

    def model_terms(model):
        return {r["term"]: r for r in res if r["model"] == model}

    ols = model_terms("weighted_ols_province_fe")
    flog = model_terms("fractional_logit_main")
    term_order = [
        ("avg_parcels_per_holding", "Average parcels per holding"),
        ("irrigation_area_share", "Irrigation area share"),
        ("frag_x_irrig_area", "Fragmentation $\\times$ irrigation"),
        ("avg_holding_size_ha", "Average holding size (ha)"),
        ("loan_share", "Loan share"),
        ("subsidy_share", "Subsidy share"),
        ("power_tiller_share", "Power tiller share"),
        ("market_access_fast_share", "Fast market access share"),
        ("climate_impact_share", "Climate impact share"),
        ("const", "Constant"),
    ]
    lines = []
    for term, label in term_order:
        o, f = ols[term], flog[term]
        lines.append(f"{label} & {coef_cell(o['coefficient'], o['significance'])} & "
                     f"{coef_cell(f['coefficient'], f['significance'])} \\\\")
        lines.append(f" & ({float(o['robust_se']):.4f}) & ({float(f['robust_se']):.4f}) \\\\")
    body = "\n".join(lines)
    # [!t]: pin to page top so the section text fills the space below
    w("tab_main_models.tex", rf"""\begin{{table}}[!t]
\centering
\caption{{Main Model Results for the Agricultural Insufficiency Share}}
\label{{tab:main-models}}
\footnotesize
\begin{{tabular}}{{lcc}}
\toprule
 & Weighted OLS & Fractional logit \\
\midrule
{body}
Province fixed effects & Yes & Yes \\
Observations & 77 & 77 \\
Fit & $R^2 = {float(fit['weighted_ols_province_fe']['fit_value']):.3f}$ & McFadden $R^2 = {float(fit['fractional_logit_main']['fit_value']):.3f}$ \\
\bottomrule
\end{{tabular}}

\vspace{{0.3em}}
\begin{{minipage}}{{0.94\textwidth}}
\footnotesize
Note: robust (HC1) standard errors in parentheses. Both models use normalized
district analytical weights based on total holdings. The fractional logit is
estimated by quasi-maximum likelihood \citep{{papke1996}}. Fragmentation and
irrigation are mean-centred at their holdings-weighted means (2.81 parcels;
0.525 irrigated-area share) before the interaction is formed, so the
main-effect coefficients are evaluated at the average holding's profile.
The McFadden pseudo-$R^2$ is mechanically small for fractional outcomes; the
correlation between the fractional logit's fitted and actual district shares
is 0.886 (Figure~\ref{{fig:annex-fitted}}, Annex III). Significance:
*** $p<0.01$, ** $p<0.05$, * $p<0.10$ (large-sample normal approximation).
\end{{minipage}}
\end{{table}}
""")

    # ----- 4.6 APE + scenarios with bootstrap CI ------------------------
    ape = rd(A / "average_partial_effects.csv")
    scen = rd(A / "counterfactual_scenarios.csv")
    boot = rd(R / "bootstrap_summary.csv")
    ape_lines = "\n".join(
        f"{tex_escape(r['label'])} & {float(r['average_partial_effect']):.4f} \\\\" for r in ape)
    scen_lines = "\n".join(
        f"{tex_escape(r['fragmentation_scenario'])} & {tex_escape(r['irrigation_scenario'])} & "
        f"{f3(r['weighted_average_predicted_insufficiency'])} \\\\" for r in scen)
    gl = next(r for r in boot if "low fragmentation" in r["quantity"])
    gh = next(r for r in boot if "high fragmentation" in r["quantity"])
    bi = next(r for r in boot if "coefficient" in r["quantity"])
    w("tab_ape_scenarios.tex", rf"""\begin{{table}}[htbp]
\centering
\caption{{Average Partial Effects and Scenario Predictions From the Main Fractional Logit}}
\label{{tab:ape-scenarios}}
\small
\begin{{tabular}}{{llc}}
\toprule
\multicolumn{{3}}{{l}}{{\textit{{Panel A: average partial effects}}}} \\
\midrule
\multicolumn{{2}}{{l}}{{Average partial effect of fragmentation}} & {float(ape[0]['average_partial_effect']):.4f} \\
\multicolumn{{2}}{{l}}{{Average partial effect of irrigation area share}} & {float(ape[1]['average_partial_effect']):.4f} \\
\midrule
\multicolumn{{3}}{{l}}{{\textit{{Panel B: weighted average predicted insufficiency}}}} \\
\midrule
Fragmentation scenario & Irrigation scenario & Prediction \\
\midrule
{scen_lines}
\midrule
\multicolumn{{3}}{{l}}{{\textit{{Panel C: bootstrap inference (999 pairs replications)}}}} \\
\midrule
\multicolumn{{2}}{{l}}{{Irrigation coefficient}} & {float(bi['point']):.3f} [{float(bi['ci_low']):.3f}, {float(bi['ci_high']):.3f}] \\
\multicolumn{{2}}{{l}}{{Scenario gap at low fragmentation}} & {float(gl['point']):.3f} [{float(gl['ci_low']):.3f}, {float(gl['ci_high']):.3f}] \\
\multicolumn{{2}}{{l}}{{Scenario gap at high fragmentation}} & {float(gh['point']):.3f} [{float(gh['ci_low']):.3f}, {float(gh['ci_high']):.3f}] \\
\bottomrule
\end{{tabular}}

\vspace{{0.3em}}
\begin{{minipage}}{{0.94\textwidth}}
\footnotesize
Note: scenario gaps are the difference in predicted insufficiency between the
high-irrigation (0.668) and low-irrigation (0.230) profiles, computed from the
unrounded predictions; they may therefore differ in the last digit from
differences of the rounded Panel B values. Brackets contain
95 percent percentile bootstrap confidence intervals from 999 district-level
pairs replications.
\end{{minipage}}
\end{{table}}
""")

    # ----- 4.7 irrigation coefficient across all specifications ----------
    key = rd(A / "key_coefficient_summary.csv")
    rob = rd(R / "robustness_results.csv")
    rfit = {r["model"]: r for r in rd(R / "robustness_fit.csv")}

    def key_row(model):
        d = {r["term"]: r for r in key if r["model"] == model}
        return d

    def rob_row(model):
        return {r["term"]: r for r in rob if r["model"] == model}

    spec_list = [
        ("Weighted OLS, no FE (baseline)", key_row("weighted_ols_baseline"), fit["weighted_ols_baseline"]["fit_value"], "insufficiency"),
        ("Weighted OLS, province FE", key_row("weighted_ols_province_fe"), fit["weighted_ols_province_fe"]["fit_value"], "insufficiency"),
        ("Fractional logit, province FE (main)", key_row("fractional_logit_main"), fit["fractional_logit_main"]["fit_value"], "insufficiency"),
        ("Fractional logit, irrigated-holdings measure", key_row("fractional_logit_irrig_holdings"), fit["fractional_logit_irrig_holdings"]["fit_value"], "insufficiency"),
        ("Weighted OLS, belt FE", rob_row("wols_belt_fe"), rfit["wols_belt_fe"]["fit_value"], "insufficiency"),
        ("Fractional logit, belt FE", rob_row("flogit_belt_fe"), rfit["flogit_belt_fe"]["fit_value"], "insufficiency"),
        ("Fractional logit, province + belt FE", rob_row("flogit_province_belt_fe"), rfit["flogit_province_belt_fe"]["fit_value"], "insufficiency"),
        ("Fractional logit, parsimonious, province FE", rob_row("flogit_parsimonious_province_fe"), rfit["flogit_parsimonious_province_fe"]["fit_value"], "insufficiency"),
        ("OLS, unweighted, province FE", rob_row("ols_unweighted_province_fe"), rfit["ols_unweighted_province_fe"]["fit_value"], "insufficiency"),
        ("Fractional logit, unweighted, province FE", rob_row("flogit_unweighted_province_fe"), rfit["flogit_unweighted_province_fe"]["fit_value"], "insufficiency"),
        ("Fractional logit, sufficiency outcome", key_row("fractional_logit_sufficiency"), fit["fractional_logit_sufficiency"]["fit_value"], "sufficiency"),
        ("Fractional logit, severe 10--12-month outcome", key_row("fractional_logit_severe_insufficiency"), fit["fractional_logit_severe_insufficiency"]["fit_value"], "severe"),
    ]
    lines = []
    for label, d, fv, outcome in spec_list:
        irr_term = "irrigation_area_share" if "irrigation_area_share" in d else "irrigated_holdings_share"
        frag = d["avg_parcels_per_holding"]
        inter_term = "frag_x_irrig_area" if "frag_x_irrig_area" in d else "frag_x_irrig_holdings"
        inter = d[inter_term]
        irrv = d[irr_term]
        lines.append(
            f"{label} & {coef_cell(frag['coefficient'], frag['significance'])} & "
            f"{coef_cell(irrv['coefficient'], irrv['significance'])} & "
            f"{coef_cell(inter['coefficient'], inter['significance'])} & {float(fv):.3f} \\\\")
    # extra review specifications
    E = ROOT / "results" / "review_extras"
    for r in rd(E / "extra_specs.csv"):
        frag_c = f"{float(r['frag_coef']):.4f}{r['frag_sig']}" if r['frag_coef'] else "---"
        irr_c = f"{float(r['irrig_coef']):.4f}{r['irrig_sig']}" if r['irrig_coef'] else "---"
        inter_c = f"{float(r['inter_coef']):.4f}{r['inter_sig']}" if r['inter_coef'] else "---"
        lines.append(f"{tex_escape(r['label'])} & {frag_c} & {irr_c} & {inter_c} & {float(r['fit']):.3f} \\\\")
    body = "\n".join(lines)
    w("tab_irrigation_specs.tex", rf"""\begin{{table}}[htbp]
\centering
\caption{{Key Coefficients Across All Estimated Specifications}}
\label{{tab:all-specs}}
\footnotesize
\setlength{{\tabcolsep}}{{4pt}}
\begin{{tabular}}{{@{{}}>{{\raggedright\arraybackslash}}p{{6.6cm}}cccc@{{}}}}
\toprule
Specification & Fragmentation & Irrigation & Interaction & Fit \\
\midrule
{body}
\bottomrule
\end{{tabular}}

\vspace{{0.3em}}
\begin{{minipage}}{{0.97\textwidth}}
\footnotesize
Note: the dependent variable is the agricultural insufficiency share except in
the sufficiency model (complement) and the severe model (10--12-month
food-insufficiency share). The irrigated-holdings specification replaces the
irrigated-area share with the share of holdings reporting irrigation.
Fragmentation and irrigation are mean-centred before the interaction is
formed, so main-effect coefficients are evaluated at the average holding's
profile. Fit is
$R^2$ for OLS and McFadden pseudo-$R^2$ for fractional logits, which are not
comparable across estimators. Significance: *** $p<0.01$, ** $p<0.05$,
* $p<0.10$.
\end{{minipage}}
\end{{table}}
""")

    # ----- 4.8 severe-vs-overall contrast --------------------------------
    data = rd(DATA)
    belts = {r["district"]: r["belt"] for r in rd(R / "district_belts.csv")}
    top_overall = sorted(data, key=lambda r: -float(r["ag_insufficiency_share"]))[:5]
    top_severe = sorted(data, key=lambda r: -float(r["severe_insuff_10_12_share"]))[:5]
    lines = []
    for o, s in zip(top_overall, top_severe):
        lines.append(
            f"{tex_escape(o['district'])} & {f3(o['ag_insufficiency_share'])} & {f3(o['irrigation_area_share'])} & "
            f"{tex_escape(s['district'])} & {f3(s['severe_insuff_10_12_share'])} & {f3(s['irrigation_area_share'])} \\\\")
    body = "\n".join(lines)
    w("tab_severe_contrast.tex", rf"""\begin{{table}}[htbp]
\centering
\caption{{Overall Versus Severe Insufficiency: Two Different Geographies}}
\label{{tab:severe-contrast}}
\footnotesize
\begin{{tabular}}{{lcclcc}}
\toprule
\multicolumn{{3}}{{c}}{{Highest \emph{{overall}} insufficiency}} & \multicolumn{{3}}{{c}}{{Highest \emph{{severe}} (10--12 months)}} \\
\cmidrule(lr){{1-3}}\cmidrule(lr){{4-6}}
District & Share & Irrig. & District & Share & Irrig. \\
\midrule
{body}
\bottomrule
\end{{tabular}}

\vspace{{0.3em}}
\begin{{minipage}}{{0.9\textwidth}}
\footnotesize
Note: ``Irrig.'' is the district irrigated-area share. The two rankings barely
overlap: overall insufficiency peaks in low-irrigation mountain districts,
whereas severe insufficiency concentrates in irrigated, more urbanised
districts with many small, part-time holdings.
\end{{minipage}}
\end{{table}}
""")

    # ----- Annex: full district dataset (two longtables) -----------------
    def annex_table(name, caption, label, cols, fmt_header, size="footnotesize"):
        head = " & ".join(fmt_header) + r" \\"
        chunks = []
        for r in sorted(data, key=lambda x: x["district"]):
            cells = [tex_escape(r["district"])]
            for c in cols:
                if c == "belt":
                    cells.append(belts[r["district"]])
                elif c == "total_holdings":
                    cells.append(f"{int(float(r[c])):,}")
                else:
                    cells.append(f3(r[c]))
            chunks.append(" & ".join(cells) + r" \\")
        body = "\n".join(chunks)
        colspec = "l" + "c" * len(cols)
        w(name, rf"""{{\{size}
\setlength{{\tabcolsep}}{{4pt}}
\begin{{longtable}}{{{colspec}}}
\caption{{{caption}}}
\label{{{label}}}\\
\toprule
{head}
\midrule
\endfirsthead
\caption[]{{{caption} (continued)}}\\
\toprule
{head}
\midrule
\endhead
\bottomrule
\endfoot
{body}
\end{{longtable}}
}}
""")

    annex_table(
        "tab_annex_core.tex",
        "District Dataset: Core Variables",
        "tab:annex-core",
        ["belt", "total_holdings", "avg_parcels_per_holding",
         "irrigation_area_share", "ag_insufficiency_share", "severe_insuff_10_12_share"],
        ["District", "Belt", "Holdings", "Parcels", "Irrig.", "Insuff.", "Severe"],
        size="scriptsize")
    annex_table(
        "tab_annex_controls.tex",
        "District Dataset: Control Variables",
        "tab:annex-controls",
        ["loan_share", "subsidy_share", "power_tiller_share",
         "market_access_fast_share", "climate_impact_share"],
        ["District", "Loan", "Subsidy", "Power tiller", "Fast market", "Climate impact"])

    print("All tables generated.")


if __name__ == "__main__":
    main()


def annex_estimation_tables() -> None:
    """Annex II: full model estimation results (all terms, all specifications)."""
    label_map = dict(
        const="Constant",
        avg_parcels_per_holding="Average parcels per holding",
        irrigation_area_share="Irrigation area share",
        irrigated_holdings_share="Irrigated holdings share",
        frag_x_irrig_area="Fragmentation $\\times$ irrigation (area)",
        frag_x_irrig_holdings="Fragmentation $\\times$ irrigation (holdings)",
        avg_holding_size_ha="Average holding size (ha)",
        loan_share="Loan share",
        subsidy_share="Subsidy share",
        power_tiller_share="Power tiller share",
        market_access_fast_share="Fast market access share",
        climate_impact_share="Climate impact share",
    )

    def pretty(term):
        if term in label_map:
            return label_map[term]
        if term.startswith("province_"):
            return "Province FE: " + term.split("_", 1)[1]
        if term.startswith("belt_"):
            return "Belt FE: " + term.split("_", 1)[1]
        return tex_escape(term)

    model_titles = {
        "weighted_ols_baseline": "Weighted OLS, no fixed effects (baseline)",
        "weighted_ols_province_fe": "Weighted OLS, province fixed effects",
        "fractional_logit_main": "Fractional logit, province fixed effects (main)",
        "fractional_logit_irrig_holdings": "Fractional logit, irrigated-holdings measure",
        "fractional_logit_sufficiency": "Fractional logit, sufficiency outcome",
        "fractional_logit_severe_insufficiency": "Fractional logit, severe 10--12-month outcome",
        "wols_belt_fe": "Weighted OLS, belt fixed effects",
        "flogit_belt_fe": "Fractional logit, belt fixed effects",
        "flogit_province_belt_fe": "Fractional logit, province + belt fixed effects",
        "flogit_parsimonious_province_fe": "Fractional logit, parsimonious, province FE",
        "ols_unweighted_province_fe": "OLS, unweighted, province fixed effects",
        "flogit_unweighted_province_fe": "Fractional logit, unweighted, province FE",
    }

    main_res = rd(A / "model_results.csv")
    rob_res = rd(R / "robustness_results.csv")
    chunks = []
    order = list(model_titles)
    for model in order:
        src = [r for r in main_res if r["model"] == model] or \
              [r for r in rob_res if r["model"] == model]
        if not src:
            continue
        chunks.append(rf"\multicolumn{{4}}{{l}}{{\textbf{{{model_titles[model]}}}}} \\")
        chunks.append(r"\midrule")
        for r in src:
            chunks.append(
                f"{pretty(r['term'])} & {float(r['coefficient']):.4f}{r['significance']} & "
                f"{float(r['robust_se']):.4f} & {float(r['approx_p_value']):.3f} \\\\")
        chunks.append(r"\addlinespace\midrule")
    body = "\n".join(chunks[:-1])  # drop trailing midrule
    w("tab_annex_models.tex", rf"""{{\footnotesize
\setlength{{\tabcolsep}}{{5pt}}
\begin{{longtable}}{{lccc}}
\caption{{Full Estimation Results for All Specifications}}
\label{{tab:annex-models}}\\
\toprule
Term & Coefficient & Robust SE & $p$ \\
\midrule
\endfirsthead
\caption[]{{Full Estimation Results for All Specifications (continued)}}\\
\toprule
Term & Coefficient & Robust SE & $p$ \\
\midrule
\endhead
\bottomrule
\endfoot
{body}
\end{{longtable}}
}}
""")

    fit_main = rd(A / "model_fit_summary.csv")
    fit_rob = rd(R / "robustness_fit.csv")

    def short_metric(name):
        return "$R^2$" if "McFadden" not in name else "McFadden $R^2$"

    # same order as the coefficient panels above
    fit_lines = {}
    for r in fit_main:
        fit_lines[r["model"]] = (f"{model_titles[r['model']]} & {short_metric(r['fit_metric'])} & "
                                 f"{float(r['fit_value']):.4f} & {r['converged']} \\\\")
    for r in fit_rob:
        metric = "$R^2$" if r["estimator"] == "wols" else "McFadden $R^2$"
        fit_lines[r["model"]] = (f"{model_titles[r['model']]} & {metric} & "
                                 f"{float(r['fit_value']):.4f} & {r['converged']} \\\\")
    body = "\n".join(fit_lines[m] for m in model_titles if m in fit_lines)
    w("tab_annex_fit.tex", rf"""\begin{{table}}[htbp]
\centering
\caption{{Model Fit Summary for All Specifications}}
\label{{tab:annex-fit}}
\footnotesize
\begin{{tabular}}{{lccc}}
\toprule
Specification & Fit metric & Value & Converged \\
\midrule
{body}
\bottomrule
\end{{tabular}}
\end{{table}}
""")


def vif_table() -> None:
    """R4: variance inflation factors for the main province-FE specification."""
    E = ROOT / "results" / "review_extras"
    rows = rd(E / "vif.csv")
    body = "\n".join(f"{tex_escape(r['label'])} & {float(r['vif']):.2f} \\\\" for r in rows)
    w("tab_vif.tex", rf"""\begin{{table}}[htbp]
\centering
\caption{{Variance Inflation Factors, Main Province Fixed-Effects Specification}}
\label{{tab:vif}}
\small
\begin{{tabular}}{{lc}}
\toprule
Regressor & VIF \\
\midrule
{body}
\bottomrule
\end{{tabular}}

\vspace{{0.3em}}
\begin{{minipage}}{{0.86\textwidth}}
\footnotesize
Note: VIFs are computed for the substantive regressors in the main
specification, with province fixed effects partialled out, after
fragmentation and irrigation are mean-centred (Section 3.7). All values lie
below the conventional threshold of 10, confirming that centring removes the
mechanical main-effect/interaction collinearity; without centring, the VIFs
of the irrigation share and of the interaction are 17.7 and 13.9.
\end{{minipage}}
\end{{table}}
""")


vif_table()
annex_estimation_tables()
