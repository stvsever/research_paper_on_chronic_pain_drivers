"""Stage 02.3 - Time-in-study effects (week one versus week two).

The diary has no calendar date, so weekday and weekend cannot be identified. What is known
is the position of each day in the two-week protocol. This stage tests whether the momentary
measures drift between the first and second study week (a reactivity / habituation check) and
whether they trend across the fourteen study days, using participant-clustered linear mixed
models. This is the analog of the day-type stage in the fibromyalgia companion study, adapted
to the information that this design actually carries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lib"))
import paths  # noqa: E402

paths.ensure_dirs()
T = paths.RESULTS_TABLES

NODES = ["PIJN", "THREAT", "ATTEND", "ENGAGE", "EFFIC", "VALENCE"]


def main() -> None:
    d = pd.read_csv(paths.EMA_LONG)
    d["week2"] = (d["study_week"] == 2).astype(int)
    d["day_c"] = d["day"] - d["day"].mean()

    rows = []
    for v in NODES:
        dd = d.dropna(subset=[v]).copy()
        dd["y"] = (dd[v] - dd[v].mean()) / dd[v].std()
        # week-two contrast
        m1 = smf.mixedlm("y ~ week2", dd, groups=dd["pid"]).fit(reml=False, method="lbfgs")
        # linear trend across study days
        m2 = smf.mixedlm("y ~ day_c", dd, groups=dd["pid"]).fit(reml=False, method="lbfgs")
        rows.append({
            "variable": v,
            "week2_beta": round(m1.params["week2"], 3),
            "week2_se": round(m1.bse["week2"], 3),
            "week2_p": round(m1.pvalues["week2"], 3),
            "dayslope_beta": round(m2.params["day_c"], 3),
            "dayslope_p": round(m2.pvalues["day_c"], 3),
        })
    out = pd.DataFrame(rows)
    out.to_csv(T / "02_studyweek_effects.csv", index=False)

    # compliance by day of study
    comp = (d.groupby("day")["completed"].sum().reset_index(name="n_completed"))
    comp["n_persons"] = d.groupby("day")["pid"].nunique().values
    comp.to_csv(T / "02_compliance_by_studyday.csv", index=False)

    print("stage 02.3 study-week effects (standardized):")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
