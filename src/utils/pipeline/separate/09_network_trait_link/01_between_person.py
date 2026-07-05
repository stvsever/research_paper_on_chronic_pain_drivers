"""Stage 09.1 - Between-person trait associations (RQ2, part 1).

This stage tests whether the threat-value account (catastrophizing and pain vigilance) is related
to attention to pain and goal engagement in daily life, and compares it against a biomedical
account (pain severity, duration) and a personality account (neuroticism).

Outcomes are each participant's mean momentary attention to pain and mean goal engagement.
For each account we report the zero-order correlation, the partial correlation controlling for
mean momentary pain, and a hierarchical regression in which the account is added after mean pain
to give an incremental R-squared.
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

STATES = {"ATTEND": "Attention to pain", "ENGAGE": "Goal engagement",
          "THREAT": "Threat value", "EFFIC": "Goal efficacy"}
ACCOUNTS = {"threat_account": "Threat", "biomedical_account": "Biomedical",
            "personality_account": "Personality"}


def partial_corr(x, y, z):
    """Partial correlation of x and y controlling z (all 1-D arrays)."""
    def resid(a, c):
        c1 = np.column_stack([np.ones_like(c), c])
        beta, *_ = np.linalg.lstsq(c1, a, rcond=None)
        return a - c1 @ beta
    rx, ry = resid(x, z), resid(y, z)
    r, p = stats.pearsonr(rx, ry)
    return r, p


def incremental_r2(y, base, added):
    def r2(X):
        X = np.column_stack([np.ones(len(y))] + [X])
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        return 1 - np.sum((y - X @ beta) ** 2) / np.sum((y - y.mean()) ** 2)
    r2_base = r2(base)
    r2_full = r2(np.column_stack([base, added]))
    return r2_base, r2_full, r2_full - r2_base


def main() -> None:
    d = pd.read_csv(paths.EMA_LONG)
    means = d.groupby("subject")[["PIJN"] + list(STATES)].mean().reset_index()
    traits = pd.read_csv(T / "08_trait_profiles.csv")
    m = means.merge(traits, on="subject", how="inner")

    corr_rows, hier_rows = [], []
    for state, slab in STATES.items():
        if state == "THREAT":  # threat state is not a between-person "outcome" of interest here
            pass
        for acc, alab in ACCOUNTS.items():
            sub = m.dropna(subset=[state, acc, "PIJN"])
            x = sub[acc].values
            y = sub[state].values
            r0, p0 = stats.pearsonr(x, y)
            rp, pp = partial_corr(y, x, sub["PIJN"].values)
            corr_rows.append({"state": slab, "account": alab, "n": len(sub),
                              "zero_order_r": round(r0, 3), "zero_order_p": round(p0, 3),
                              "partial_r": round(rp, 3), "partial_p": round(pp, 3)})
        # hierarchical: mean pain, then all three accounts (standardized)
        sub = m.dropna(subset=[state, "PIJN"] + list(ACCOUNTS))
        y = sub[state].values
        base = sub["PIJN"].values.reshape(-1, 1)
        acc_mat = np.column_stack([(sub[a] - sub[a].mean()) / sub[a].std() for a in ACCOUNTS])
        r2b, r2f, dr2 = incremental_r2(y, base, acc_mat)
        hier_rows.append({"state": slab, "n": len(sub),
                          "R2_pain": round(r2b, 3), "R2_pain_plus_traits": round(r2f, 3),
                          "incremental_R2_traits": round(dr2, 3)})

    pd.DataFrame(corr_rows).to_csv(T / "09_between_person_correlations.csv", index=False)
    pd.DataFrame(hier_rows).to_csv(T / "09_between_person_hierarchical.csv", index=False)

    print("stage 09.1 between-person trait associations:")
    cc = pd.DataFrame(corr_rows)
    print(cc[cc["state"].isin(["Attention to pain", "Goal engagement"])].to_string(index=False))


if __name__ == "__main__":
    main()
