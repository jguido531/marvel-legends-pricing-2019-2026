#!/usr/bin/env python3
"""Reproduce the headline Marvel Legends pricing regressions from the public model-ready CSV.

Run from anywhere:
    python code/reproduce_analysis.py

Outputs are written to ./outputs/ relative to the repository root.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "monthly_model_data.csv"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

PREFERRED_VARS = ["resin_yoy", "tooling_yoy", "freight_yoy", "demand_yoy"]


def read_csv(path: Path) -> Dict[str, np.ndarray]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    def num(key: str) -> np.ndarray:
        vals = []
        for r in rows:
            s = (r.get(key) or "").strip()
            vals.append(float(s) if s else np.nan)
        return np.asarray(vals, dtype=float)

    return {
        "month": np.asarray([r["month"] for r in rows], dtype=object),
        "msrp": num("msrp"),
        "resin": num("resin_ppi"),
        "tooling": num("tooling_dies_ppi"),
        "paint": num("paints_ppi"),
        "freight": num("deep_sea_freight_ppi"),
        "demand_yoy": num("toy_hobby_retail_sales_yoy"),
        "packaging": num("packaging_composite_2019_01_100"),
    }


def yoy(x: np.ndarray) -> np.ndarray:
    out = np.full(len(x), np.nan, dtype=float)
    out[12:] = x[12:] / x[:-12] - 1.0
    return out


def normalize100(x: np.ndarray) -> np.ndarray:
    return x / x[0] * 100.0


def standardized_betas(params: np.ndarray, X: np.ndarray, y: np.ndarray) -> np.ndarray:
    return params[1:] * X.std(axis=0, ddof=0) / y.std(ddof=0)


def vif_values(X: np.ndarray) -> np.ndarray:
    out = []
    for j in range(X.shape[1]):
        yj = X[:, j]
        Xj = np.delete(X, j, axis=1)
        fit = sm.OLS(yj, sm.add_constant(Xj)).fit()
        out.append(1.0 / (1.0 - fit.rsquared))
    return np.asarray(out)


def fit_model(y: np.ndarray, X: np.ndarray, names: Sequence[str], hac_lags: int = 12) -> dict:
    mask = ~np.isnan(y)
    for j in range(X.shape[1]):
        mask &= ~np.isnan(X[:, j])
    yy = y[mask]
    XX = X[mask]
    fit = sm.OLS(yy, sm.add_constant(XX)).fit(
        cov_type="HAC",
        cov_kwds={"maxlags": hac_lags, "use_correction": False},
        use_t=False,
    )
    betas = standardized_betas(fit.params, XX, yy)
    vifs = vif_values(XX)
    return {
        "n": len(yy),
        "r2": float(fit.rsquared),
        "adj_r2": float(fit.rsquared_adj),
        "aic": float(fit.aic),
        "params": fit.params,
        "se": fit.bse,
        "p": fit.pvalues,
        "std_beta": betas,
        "vif": vifs,
        "max_vif": float(vifs.max()),
        "names": list(names),
        "mask": mask,
    }


def write_model_csv(path: Path, model_name: str, result: dict) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model", "n", "r2", "adj_r2", "aic", "max_vif"])
        w.writerow([model_name, result["n"], result["r2"], result["adj_r2"], result["aic"], result["max_vif"]])
        w.writerow([])
        w.writerow(["variable", "raw_coefficient", "hac_se", "p_value", "standardized_beta", "vif"])
        w.writerow(["constant", result["params"][0], result["se"][0], result["p"][0], "", ""])
        for i, name in enumerate(result["names"], start=1):
            w.writerow([name, result["params"][i], result["se"][i], result["p"][i], result["std_beta"][i-1], result["vif"][i-1]])


def approx(a: float, b: float, tol: float = 1e-10) -> bool:
    return abs(a - b) <= tol


def main() -> None:
    d = read_csv(DATA)
    msrp_yoy = yoy(d["msrp"])
    resin_yoy = yoy(d["resin"])
    tooling_yoy = yoy(d["tooling"])
    freight_yoy = yoy(d["freight"])
    packaging_yoy = yoy(d["packaging"])

    broad_level = (
        normalize100(d["tooling"])
        + normalize100(d["paint"])
        + d["packaging"]
        + normalize100(d["freight"])
    ) / 4.0
    broad_yoy = yoy(broad_level)

    preferred_X = np.column_stack([resin_yoy, tooling_yoy, freight_yoy, d["demand_yoy"]])
    preferred = fit_model(msrp_yoy, preferred_X, PREFERRED_VARS)
    write_model_csv(OUT / "preferred_regression.csv", "preferred_annual_change", preferred)

    packaging_alt = fit_model(
        msrp_yoy,
        np.column_stack([resin_yoy, packaging_yoy, freight_yoy, d["demand_yoy"]]),
        ["resin_yoy", "packaging_yoy", "freight_yoy", "demand_yoy"],
    )
    broad_alt = fit_model(
        msrp_yoy,
        np.column_stack([resin_yoy, broad_yoy, d["demand_yoy"]]),
        ["resin_yoy", "broad_cost_yoy", "demand_yoy"],
    )

    # Diagnostic raw-level model: not a preferred specification.
    level_y = normalize100(d["msrp"])
    level_X = np.column_stack([
        normalize100(d["resin"]),
        normalize100(d["tooling"]),
        normalize100(d["paint"]),
        d["packaging"],
        normalize100(d["freight"]),
        d["demand_yoy"],
    ])
    level_diag = fit_model(
        level_y,
        level_X,
        ["resin_level", "tooling_level", "paint_level", "packaging_level", "freight_level", "demand_yoy"],
    )

    # Common supply lags. Demand remains contemporaneous.
    lag_rows = []
    for lag in [0, 3, 6, 9, 12]:
        Xlag = np.full((len(msrp_yoy), 4), np.nan)
        if lag == 0:
            Xlag[:, 0] = resin_yoy
            Xlag[:, 1] = tooling_yoy
            Xlag[:, 2] = freight_yoy
        else:
            Xlag[lag:, 0] = resin_yoy[:-lag]
            Xlag[lag:, 1] = tooling_yoy[:-lag]
            Xlag[lag:, 2] = freight_yoy[:-lag]
        Xlag[:, 3] = d["demand_yoy"]
        r = fit_model(msrp_yoy, Xlag, PREFERRED_VARS)
        lag_rows.append([
            lag, r["n"], r["r2"], r["adj_r2"], r["aic"], r["max_vif"],
            *r["std_beta"], *r["p"][1:]
        ])

    with (OUT / "common_lag_robustness.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "supply_lag_months", "n", "r2", "adj_r2", "aic", "max_vif",
            "resin_std_beta", "tooling_std_beta", "freight_std_beta", "demand_std_beta",
            "resin_p", "tooling_p", "freight_p", "demand_p"
        ])
        w.writerows(lag_rows)

    # Supply-only model (adds Aug 2026 because demand is not required).
    supply_only = fit_model(
        msrp_yoy,
        np.column_stack([resin_yoy, tooling_yoy, freight_yoy]),
        ["resin_yoy", "tooling_yoy", "freight_yoy"],
    )

    # Preferred model through Aug 2025 (before the Sep 2025 price regime).
    pre_mask = np.asarray([m < "2025-09-01" for m in d["month"]])
    y_pre = msrp_yoy.copy()
    X_pre = preferred_X.copy()
    y_pre[~pre_mask] = np.nan
    pre_2025 = fit_model(y_pre, X_pre, PREFERRED_VARS)

    # Mixed-timing diagnostic: resin at 12 months, tooling/freight current.
    mixed_X = np.full((len(msrp_yoy), 4), np.nan)
    mixed_X[12:, 0] = resin_yoy[:-12]
    mixed_X[:, 1] = tooling_yoy
    mixed_X[:, 2] = freight_yoy
    mixed_X[:, 3] = d["demand_yoy"]
    mixed = fit_model(msrp_yoy, mixed_X, PREFERRED_VARS)

    with (OUT / "robustness_summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["check", "n", "r2", "adj_r2", "max_vif"])
        for label, r in [
            ("packaging_alternative", packaging_alt),
            ("broad_cost_composite", broad_alt),
            ("raw_level_diagnostic", level_diag),
            ("supply_only", supply_only),
            ("pre_sep_2025", pre_2025),
            ("mixed_timing_resin12", mixed),
        ]:
            w.writerow([label, r["n"], r["r2"], r["adj_r2"], r["max_vif"]])

    # Frozen V20 benchmark checks.
    checks = {
        "preferred_n": preferred["n"] == 79,
        "preferred_r2": approx(preferred["r2"], 0.6298457407399287),
        "preferred_adj_r2": approx(preferred["adj_r2"], 0.6098374024015465),
        "preferred_max_vif": approx(preferred["max_vif"], 2.2865309362513635),
        "packaging_alt_r2": approx(packaging_alt["r2"], 0.593961763608942),
        "broad_alt_r2": approx(broad_alt["r2"], 0.6220654664060943),
        "level_diag_r2": approx(level_diag["r2"], 0.9585451977198512),
        "level_diag_max_vif": approx(level_diag["max_vif"], 185.10469604059523),
        "supply_only_r2": approx(supply_only["r2"], 0.6289632766469362),
        "pre_sep_2025_r2": approx(pre_2025["r2"], 0.7201346862701647),
        "mixed_timing_r2": approx(mixed["r2"], 0.5944166489030349),
    }

    with (OUT / "benchmark_checks.txt").open("w", encoding="utf-8") as f:
        for name, ok in checks.items():
            f.write(f"{name}: {'PASS' if ok else 'FAIL'}\n")

    print("Preferred annual-change model")
    print(f"N={preferred['n']}  R^2={preferred['r2']:.6f}  Adj.R^2={preferred['adj_r2']:.6f}  Max VIF={preferred['max_vif']:.3f}")
    for i, name in enumerate(PREFERRED_VARS, start=1):
        print(f"  {name:12s} beta={preferred['std_beta'][i-1]: .3f}  HAC p={preferred['p'][i]:.6g}")
    print("\nBenchmark checks:", "ALL PASS" if all(checks.values()) else "ONE OR MORE FAILED")
    print(f"Outputs written to: {OUT}")


if __name__ == "__main__":
    main()
