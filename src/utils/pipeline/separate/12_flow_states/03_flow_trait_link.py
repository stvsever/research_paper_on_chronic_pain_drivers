"""Stage 12.3 - Person-level flow proneness and the baseline trait profiles.

Flow is a momentary state, but the *propensity* to reach it is a person-level quantity, and
that is the only level at which flow can legitimately meet the RQ2 trait framework. Three
person-level flow variables are built from the stage 12.1 output:

    flow_proneness   proportion of moments meeting the strict gated criterion (both condition
                     items >= 5 and the flow experience >= 5)
    mean_flowexp     the person's average flow experience (absorption plus enjoyment)
    flow_pain_slope  the person's own within-person flow-to-pain coupling (stage 12.2)

Each is related to the threat, biomedical, and personality accounts from stage 08, with the
same zero-order / partial / incremental-R2 logic used in stage 09 so the numbers are directly
comparable to the RQ2 table. Two further questions are answered here:
    - does flow proneness add explained variance in the mean momentary states over and above
      the three baseline accounts?
    - do the baseline accounts predict who shows a negative flow-pain coupling?

With 68 persons this analysis is exploratory and is powered only for moderate effects.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lib"))
import paths  # noqa: E402

paths.ensure_dirs()
T = paths.RESULTS_TABLES

ACCOUNTS = {"threat_account": "Threat", "biomedical_account": "Biomedical",
            "personality_account": "Personality"}
FLOW_VARS = {"flow_prop_abs5": "Flow proneness (strict)",
             "mean_flowexp": "Mean flow experience",
             "mean_challenge": "Mean challenge",
             "mean_effic": "Mean skill",
             "flow_pain_slope": "Flow-pain coupling"}


def resid(a, c):
    c1 = np.column_stack([np.ones(len(a)), c])
    beta, *_ = np.linalg.lstsq(c1, a, rcond=None)
    return a - c1 @ beta


def partial_corr(x, y, z):
    rx, ry = resid(x, z), resid(y, z)
    r, p = stats.pearsonr(rx, ry)
    return r, p


def r2_of(y, X):
    X = np.column_stack([np.ones(len(y)), X])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return 1 - np.sum((y - X @ beta) ** 2) / np.sum((y - y.mean()) ** 2)


def main():
    prev = pd.read_csv(T / "12_flow_person_prevalence.csv")
    slopes = pd.read_csv(T / "12_flow_perperson_slopes.csv")[["pid", "b_contemp", "b_lagged"]]
    slopes = slopes.rename(columns={"b_contemp": "flow_pain_slope",
                                    "b_lagged": "flow_pain_slope_lagged"})
    traits = pd.read_csv(T / "08_trait_profiles.csv")
    ema = pd.read_csv(paths.EMA_LONG)
    person = pd.read_csv(paths.PERSON_LEVEL)[["subject", "pid"]]

    means = ema.groupby("pid")[["PIJN", "ATTEND", "ENGAGE", "PIJN_AFF",
                                "THREAT"]].mean().reset_index()
    df = (prev.merge(slopes, on="pid", how="left")
              .merge(means, on="pid", how="left")
              .merge(person, on="pid", how="left")
              .merge(traits, on="subject", how="inner"))
    print(f"  person-level flow frame: {len(df)} persons")

    # --- 1. accounts vs each person-level flow variable ----------------------
    rows = []
    for fv, flabel in FLOW_VARS.items():
        y = df[fv].to_numpy(float)
        ok = np.isfinite(y)
        for acc, alabel in ACCOUNTS.items():
            x = df[acc].to_numpy(float)
            m = ok & np.isfinite(x)
            r, p = stats.pearsonr(x[m], y[m])
            pr, pp = partial_corr(x[m], y[m], df["PIJN"].to_numpy(float)[m])
            rows.append({"flow_variable": flabel, "account": alabel, "n": int(m.sum()),
                         "zero_order_r": round(r, 3), "zero_order_p": round(p, 4),
                         "partial_r": round(pr, 3), "partial_p": round(pp, 4)})
    link = pd.DataFrame(rows)
    link.to_csv(T / "12_flow_trait_link.csv", index=False)
    print("  wrote", (T / "12_flow_trait_link.csv").name)

    # --- 2. flow proneness as an incremental predictor of the mean states ----
    inc = []
    accs = df[list(ACCOUNTS)].to_numpy(float)
    acc_ok = np.isfinite(accs).all(axis=1)
    # Goal engagement is deliberately excluded as an outcome here: it is one of the two
    # items inside the flow experience composite, so regressing it on flow proneness would
    # be circular.
    for state, slabel in [("ATTEND", "Attention to pain"), ("PIJN", "Pain intensity"),
                          ("PIJN_AFF", "Pain interference"), ("THREAT", "Threat value")]:
        y = df[state].to_numpy(float)
        for fv, flabel in [("flow_prop_abs5", "Flow proneness (strict)"),
                           ("mean_flowexp", "Mean flow experience")]:
            add = df[fv].to_numpy(float).reshape(-1, 1)
            m = acc_ok & np.isfinite(y) & np.isfinite(add).ravel()
            base = r2_of(y[m], accs[m])
            full = r2_of(y[m], np.column_stack([accs[m], add[m]]))
            inc.append({"state": slabel, "flow_variable": flabel, "n": int(m.sum()),
                        "R2_accounts": round(base, 3),
                        "R2_accounts_plus_flow": round(full, 3),
                        "delta_R2": round(full - base, 3)})
    pd.DataFrame(inc).to_csv(T / "12_flow_incremental_r2.csv", index=False)
    print("  wrote 12_flow_incremental_r2.csv")

    # --- 3. who shows a negative flow-pain coupling? -------------------------
    sub = df[np.isfinite(df["flow_pain_slope"])].copy()
    sub["negative_coupler"] = (sub["flow_pain_slope"] < 0).astype(int)
    grp = []
    for var, label in [("threat_account", "Threat"), ("biomedical_account", "Biomedical"),
                       ("personality_account", "Personality"),
                       ("flow_prop_abs5", "Flow proneness (strict)"),
                       ("PIJN", "Mean pain")]:
        a = sub.loc[sub["negative_coupler"] == 1, var].to_numpy(float)
        b = sub.loc[sub["negative_coupler"] == 0, var].to_numpy(float)
        a, b = a[np.isfinite(a)], b[np.isfinite(b)]
        t, p = stats.ttest_ind(a, b, equal_var=False)
        pooled = np.sqrt((np.var(a, ddof=1) + np.var(b, ddof=1)) / 2)
        grp.append({"variable": label, "n_negative": len(a), "n_nonnegative": len(b),
                    "mean_negative": round(float(np.mean(a)), 3),
                    "mean_nonnegative": round(float(np.mean(b)), 3),
                    "cohens_d": round(float((np.mean(a) - np.mean(b)) / pooled), 3),
                    "p": round(float(p), 4)})
    pd.DataFrame(grp).to_csv(T / "12_flow_coupling_groups.csv", index=False)
    print("  wrote 12_flow_coupling_groups.csv")

    df.to_csv(T / "12_flow_person_frame.csv", index=False)
    print("  wrote 12_flow_person_frame.csv")

    print("\n=== person-level flow variables vs baseline accounts ===")
    print(link.to_string(index=False))
    print("\n=== incremental variance from flow proneness ===")
    print(pd.DataFrame(inc).to_string(index=False))


if __name__ == "__main__":
    main()
