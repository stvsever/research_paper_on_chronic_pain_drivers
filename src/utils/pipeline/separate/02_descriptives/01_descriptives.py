"""Stage 02.1 - Sample and momentary descriptives.

Produces the baseline Table 1, the momentary-measure descriptives, and the within-person
and between-person correlation matrices among the analytic nodes. The within- versus
between-person split is central to the paper: a construct can relate to pain one way across
people and another way within a person over time.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lib"))
import paths  # noqa: E402

paths.ensure_dirs()
T = paths.RESULTS_TABLES

NODES = ["PIJN", "THREAT", "ATTEND", "ENGAGE", "EFFIC", "VALENCE"]
AUX = ["FEAR", "CATAS", "PIJN_AFF", "CHALLENGE", "IMPORTANCE", "NEGAFF"]


def person_table1(pl: pd.DataFrame) -> pd.DataFrame:
    a = pl[pl["in_analytic_sample"]].copy()
    rows = []

    def add(label, series, pct=False, fmt="{:.1f}"):
        s = pd.to_numeric(series, errors="coerce").dropna()
        if pct:
            rows.append([label, fmt.format(100 * s.mean()), "", int(s.notna().sum())])
        else:
            rng = f"{s.min():.0f} to {s.max():.0f}"
            rows.append([label, f"{s.mean():.1f} ({s.std():.1f})", rng, int(len(s))])

    add("Age (years)", a["age"])
    g = a["gender"].dropna()
    rows.append(["Sex: women / men (%)",
                 f"{100 * (g == 'female').mean():.1f} / {100 * (g == 'male').mean():.1f}",
                 "", int(len(g))])
    add("Pain duration (months)", a["pain_duration_months"])
    add("MPI pain severity", a["MPI_pain_severity"])
    add("MPI interference", a["MPI_interference"])
    add("Pain Disability Index", a["PDI_total"])
    add("PCS catastrophizing (total)", a["PCS_total"])
    add("PVAQ pain vigilance (total)", a["PVAQ_total"])
    add("HADS anxiety", a["HADS_anxiety"])
    add("HADS depression", a["HADS_depression"])
    add("NEO-FFI neuroticism", a["NEO_neuroticism"])
    return pd.DataFrame(rows, columns=["Variable", "Mean (SD)", "Range", "n"])


def ema_descriptives(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for v in NODES + AUX:
        s = d[v]
        # within- and between-person SD
        pm = d.groupby("pid")[v].transform("mean")
        within_sd = (s - pm).std()
        between_sd = d.groupby("pid")[v].mean().std()
        rows.append({
            "variable": v,
            "n_obs": int(s.notna().sum()),
            "mean": s.mean(),
            "sd": s.std(),
            "within_sd": within_sd,
            "between_sd": between_sd,
            "pct_missing": 100 * s.isna().mean(),
        })
    return pd.DataFrame(rows).round(3)


def person_centered(d: pd.DataFrame, cols) -> pd.DataFrame:
    out = d[["pid"]].copy()
    for c in cols:
        out[c] = d[c] - d.groupby("pid")[c].transform("mean")
    return out


def main() -> None:
    d = pd.read_csv(paths.EMA_LONG)
    pl = pd.read_csv(paths.PERSON_LEVEL)

    person_table1(pl).to_csv(T / "02_person_level_table1.csv", index=False)

    ema_descriptives(d).to_csv(T / "02_ema_descriptives.csv", index=False)

    # within-person correlations (person-mean-centred) and between-person (person means)
    wc = person_centered(d, NODES)[NODES].corr().round(3)
    wc.insert(0, "variable", NODES)
    wc.to_csv(T / "02_within_person_corr.csv", index=False)

    bc = d.groupby("pid")[NODES].mean().corr().round(3)
    bc.insert(0, "variable", NODES)
    bc.to_csv(T / "02_between_person_corr.csv", index=False)

    # education distribution for the sample description
    edu_map = {1: "Primary", 2: "Lower secondary", 3: "Higher secondary", 4: "Higher"}
    edu = (pl[pl["in_analytic_sample"]]["education"].map(edu_map)
           .value_counts().rename_axis("education").reset_index(name="n"))
    edu.to_csv(T / "02_education_distribution.csv", index=False)

    print("stage 02.1 descriptives:")
    print(f"  analytic persons        : {int(pl['in_analytic_sample'].sum())}")
    print(f"  completed prompts        : {int(d['completed'].sum())}")
    print("  within-person corr with pain:")
    for v in ["THREAT", "ATTEND", "ENGAGE", "EFFIC", "VALENCE"]:
        print(f"    {v:<7}: {wc.loc[wc['variable'] == 'PIJN', v].iloc[0]:+.3f}")


if __name__ == "__main__":
    main()
