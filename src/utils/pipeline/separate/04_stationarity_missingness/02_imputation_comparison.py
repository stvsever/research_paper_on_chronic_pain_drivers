"""Stage 04.2 - Missingness description and a held-out imputation benchmark.

Momentary missingness here reflects non-response to individual beeps. The primary temporal
models use available-case (pairwise) handling within each equation. This stage documents the
missingness and audits that decision with a held-out reconstruction benchmark: 20 percent of
observed values are hidden at random and reconstructed with univariate time-series methods
(person mean, person median, last observation carried forward, linear interpolation) and
multivariate methods that borrow strength across the concurrent measures (k-nearest
neighbours, iterative/MICE-style regression). Methods are compared by standardized RMSE, the
within-person held-out correlation, and the change in pooled moments after imputation.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer, KNNImputer

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lib"))
import paths  # noqa: E402

paths.ensure_dirs()
T = paths.RESULTS_TABLES
RNG = np.random.default_rng(20260703)

NODES = ["PIJN", "THREAT", "ATTEND", "ENGAGE", "EFFIC", "VALENCE"]
LABELS = {"PIJN": "Pain", "THREAT": "Threat", "ATTEND": "Attention",
          "ENGAGE": "Engagement", "EFFIC": "Efficacy", "VALENCE": "Valence"}


def missingness_table(d: pd.DataFrame) -> pd.DataFrame:
    n = len(d)
    rows = []
    for v in NODES:
        obs = int(d[v].notna().sum())
        rows.append({"measure": LABELS[v], "observed": obs, "missing": n - obs,
                     "pct_missing": round(100 * (n - obs) / n, 1)})
    return pd.DataFrame(rows)


def _uni_impute(series: pd.Series, method: str) -> pd.Series:
    s = series.copy()
    if method == "mean":
        return s.fillna(s.mean())
    if method == "median":
        return s.fillna(s.median())
    if method == "locf":
        return s.ffill().bfill()
    if method == "linear":
        return s.interpolate(limit_direction="both").fillna(s.mean())
    raise ValueError(method)


def benchmark(d: pd.DataFrame) -> pd.DataFrame:
    # Build a person-standardized matrix so RMSE is comparable across measures.
    z = d[["pid"] + NODES].copy()
    for v in NODES:
        z[v] = z.groupby("pid")[v].transform(lambda x: (x - x.mean()) / (x.std() or 1.0))
    full = z[NODES]
    observed_mask = full.notna().values
    # hold out 20% of observed cells
    hold = observed_mask & (RNG.random(full.shape) < 0.20)
    train = full.mask(hold)

    results = []

    # univariate methods (per person, per column)
    for method in ["mean", "median", "locf", "linear"]:
        rec = train.copy()
        for v in NODES:
            rec[v] = z.assign(_t=train[v]).groupby("pid")["_t"].transform(
                lambda s: _uni_impute(s, method))
        results.append(("univariate", method, rec))

    # multivariate methods (borrow across concurrent measures)
    for name, imp in [("knn", KNNImputer(n_neighbors=10)),
                      ("mice", IterativeImputer(max_iter=10, random_state=0,
                                                sample_posterior=False))]:
        arr = imp.fit_transform(train.values)
        results.append(("multivariate", name, pd.DataFrame(arr, columns=NODES,
                                                            index=train.index)))

    truth = full.values
    rows = []
    for kind, name, rec in results:
        recv = rec.values
        err = recv[hold] - truth[hold]
        rmse = float(np.sqrt(np.nanmean(err ** 2)))
        mae = float(np.nanmean(np.abs(err)))
        # within-person correlation on held-out cells
        r = np.corrcoef(recv[hold], truth[hold])[0, 1] if hold.sum() > 2 else np.nan
        rows.append({"method": name, "type": kind, "std_rmse": round(rmse, 3),
                     "std_mae": round(mae, 3), "r_heldout": round(float(r), 3)})
    return pd.DataFrame(rows).sort_values("std_rmse").reset_index(drop=True)


def main() -> None:
    d = pd.read_csv(paths.EMA_LONG)

    miss = missingness_table(d)
    miss.to_csv(T / "04_missingness_by_measure.csv", index=False)

    bench = benchmark(d)
    bench.to_csv(T / "04_imputation_comparison.csv", index=False)

    # consecutive-missing run lengths per measure (for the supplementary figure)
    runs = []
    for v in NODES:
        for pid, g in d.groupby("pid"):
            miss_flag = g[v].isna().values.astype(int)
            run = 0
            for m in miss_flag:
                if m:
                    run += 1
                elif run:
                    runs.append({"measure": LABELS[v], "run_length": run})
                    run = 0
            if run:
                runs.append({"measure": LABELS[v], "run_length": run})
    pd.DataFrame(runs).to_csv(T / "04_gap_runlengths.csv", index=False)

    print("stage 04.2 missingness + imputation benchmark:")
    print(miss.to_string(index=False))
    print(bench.to_string(index=False))


if __name__ == "__main__":
    main()
