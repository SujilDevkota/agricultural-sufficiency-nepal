#!/usr/bin/env python3
"""Spatial diagnostics (§4.2): Moran's I on residuals of the two main models.

Queen contiguity over the 77 districts; permutation p-values -> results/review_extras/moran.csv.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_final_paper_analysis as base  # noqa: E402
from run_thesis_robustness import design  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / "data" / "raw" / "nepal_districts_77.geojson"
OUT = ROOT / "results" / "review_extras"

NAME_MAP = {"Chitawan": "Chitwan", "Kabhrepalanchok": "Kavrepalanchok",
            "Kapilbastu": "Kapilvastu"}

PERMUTATIONS = 9999
SEED = 20260704


def polygon_vertices(geom) -> set[tuple[float, float]]:
    pts: set[tuple[float, float]] = set()
    polys = geom["coordinates"]
    if geom["type"] == "Polygon":
        polys = [polys]
    for poly in polys:
        for ring in poly:
            pts.update((round(x, 9), round(y, 9)) for x, y in ring)
    return pts


def morans_i(e: np.ndarray, W: np.ndarray, rng: np.random.Generator):
    n = len(e)
    z = e - e.mean()
    s0 = W.sum()
    i_obs = (n / s0) * float(z @ W @ z) / float(z @ z)
    draws = np.empty(PERMUTATIONS)
    for k in range(PERMUTATIONS):
        zp = rng.permutation(z)
        draws[k] = (n / s0) * float(zp @ W @ zp) / float(zp @ zp)
    p_two = (1 + np.sum(np.abs(draws) >= abs(i_obs))) / (PERMUTATIONS + 1)
    p_pos = (1 + np.sum(draws >= i_obs)) / (PERMUTATIONS + 1)
    return i_obs, -1.0 / (n - 1), p_two, p_pos


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = base.read_dataset(base.DATASET)
    order = [str(r["district"]) for r in rows]
    weights = base.as_array(rows, base.WEIGHT)
    y = base.as_array(rows, base.MAIN_OUTCOME)

    geo = json.load(GEO.open())
    verts: dict[str, set] = {}
    for f in geo["features"]:
        name = NAME_MAP.get(f["properties"]["DIST_EN"],
                            f["properties"]["DIST_EN"])
        verts[name] = polygon_vertices(f["geometry"])
    missing = [d for d in order if d not in verts]
    if missing:
        sys.exit(f"FAILED: no geometry for {missing}")

    n = len(order)
    W = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            if len(verts[order[i]] & verts[order[j]]) >= 2:
                W[i, j] = W[j, i] = 1.0
    neigh = W.sum(axis=1)
    isolates = [order[i] for i in range(n) if neigh[i] == 0]
    if isolates:
        sys.exit(f"FAILED: isolated districts in contiguity graph: {isolates}")
    print(f"queen contiguity: mean {neigh.mean():.2f} neighbours "
          f"(min {int(neigh.min())}, max {int(neigh.max())}), no isolates")

    # residuals of the two main specifications
    X, cols = design(rows, province_fe=True, belt_fe=False)
    b_ols, *_ = base.weighted_ols_hc1(y, X, weights)
    e_ols = y - X @ b_ols
    b_flog, *_ = base.fractional_logit_hc1(y, X, weights)
    e_flog = y - base.logistic(X @ b_flog)

    rng = np.random.default_rng(SEED)
    out_rows = []
    for label, e in (("weighted_ols_province_fe", e_ols),
                     ("fractional_logit_main", e_flog)):
        i_obs, e_i, p_two, p_pos = morans_i(e, W, rng)
        out_rows.append({
            "model": label, "morans_i": f"{i_obs:.4f}",
            "expected_i": f"{e_i:.4f}", "p_two_sided": f"{p_two:.4f}",
            "p_positive": f"{p_pos:.4f}",
            "permutations": str(PERMUTATIONS),
        })
        print(f"Moran's I ({label}): I={i_obs:.4f}, E[I]={e_i:.4f}, "
              f"two-sided p={p_two:.4f}, positive-autocorr p={p_pos:.4f}")

    base.write_csv(OUT / "moran.csv", out_rows)
    print(f"Wrote {OUT / 'moran.csv'}")


if __name__ == "__main__":
    main()
