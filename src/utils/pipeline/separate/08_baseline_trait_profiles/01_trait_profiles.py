"""Stage 08 - Baseline trait accounts for RQ2.

RQ2 asks whether individual differences in the person-specific pain-driver couplings are best
explained by a threat-value account, a biomedical account, or a personality account. This stage
builds the three z-scored composites from the baseline table and defines a dominant-account
grouping (the account on which a participant scores highest in standardized units), which is used
as an interpretable subgrouping in the link stage.

Composites:
  - Threat     : mean z(PCS catastrophizing total), z(PVAQ vigilance total).
  - Biomedical : mean z(MPI pain severity), z(pain duration, log).
  - Personality: z(NEO neuroticism).
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


def z(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    return (s - s.mean()) / s.std()


def main() -> None:
    pl = pd.read_csv(paths.PERSON_LEVEL)
    a = pl[pl["in_analytic_sample"]].copy()

    a["z_PCS"] = z(a["PCS_total"])
    a["z_PVAQ"] = z(a["PVAQ_total"])
    a["z_MPIsev"] = z(a["MPI_pain_severity"])
    a["z_duration"] = z(np.log1p(a["pain_duration_months"]))
    a["z_NEO"] = z(a["NEO_neuroticism"])

    a["threat_account"] = a[["z_PCS", "z_PVAQ"]].mean(axis=1)
    a["biomedical_account"] = a[["z_MPIsev", "z_duration"]].mean(axis=1)
    a["personality_account"] = a["z_NEO"]

    accounts = ["threat_account", "biomedical_account", "personality_account"]
    # re-standardize the three composites so the dominant account is comparable
    for c in accounts:
        a[c + "_z"] = z(a[c])
    dom = a[[c + "_z" for c in accounts]].idxmax(axis=1)
    a["dominant_account"] = dom.str.replace("_account_z", "", regex=False).str.capitalize()

    keep = ["subject", "pid", "idiographic_eligible",
            "PCS_total", "PVAQ_total", "MPI_pain_severity", "pain_duration_months",
            "NEO_neuroticism", "HADS_total",
            "threat_account", "biomedical_account", "personality_account",
            "dominant_account"]
    out = a[keep].copy()
    out.to_csv(T / "08_trait_profiles.csv", index=False)

    counts = out["dominant_account"].value_counts().rename_axis("account").reset_index(name="n")
    counts.to_csv(T / "08_dominant_account_counts.csv", index=False)

    # correlations among the three accounts (are they distinguishable?)
    corr = a[accounts].corr().round(3)
    corr.insert(0, "account", accounts)
    corr.to_csv(T / "08_account_intercorrelations.csv", index=False)

    print("stage 08 baseline trait profiles:")
    print(f"  participants with baseline : {len(out)}")
    print("  dominant-account counts:")
    print(counts.to_string(index=False))
    print("  account intercorrelations:")
    print(corr.to_string(index=False))


if __name__ == "__main__":
    main()
