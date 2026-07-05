"""Stage 01.1 - Build the person-level baseline table.

Reads the baseline "between" questionnaire file (integer subject IDs that match the
diary) and scores the trait measures needed for RQ2. RQ2 asks whether individual
differences in the person-specific pain-driver couplings are best explained by a
threat-value account, a biomedical account, or a personality account.

Composites (each z-scored later, at the link stage):
  - Threat-value account : Pain Catastrophizing Scale total and Pain Vigilance and
                           Awareness Questionnaire total.
  - Biomedical account   : Multidimensional Pain Inventory pain severity and pain duration.
  - Personality account  : NEO-FFI neuroticism.

Output:
  - src/data/processed/person_level.csv (one row per baseline participant)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lib"))
import paths  # noqa: E402

paths.ensure_dirs()

# NEO-FFI-60 Neuroticism key: items and the reverse-scored subset.
NEO_N_ITEMS = [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56]
NEO_N_REVERSE = [1, 16, 31, 46]

# PVAQ is scored as the simple item sum (0 to 5 per item, 16 items).
PVAQ_ITEMS = list(range(1, 17))


def _sum_items(df: pd.DataFrame, prefix: str, items: list[int]) -> pd.Series:
    cols = [f"{prefix}{i}" for i in items if f"{prefix}{i}" in df.columns]
    return df[cols].sum(axis=1, min_count=len(cols))


def _neo_neuroticism(df: pd.DataFrame) -> pd.Series:
    cols = [f"neo{i}" for i in NEO_N_ITEMS if f"neo{i}" in df.columns]
    block = df[cols].copy()
    # Detect the response anchors from the observed data to reverse-score robustly.
    lo = np.nanmin(df[[c for c in df.columns if c.startswith("neo")]].values)
    hi = np.nanmax(df[[c for c in df.columns if c.startswith("neo")]].values)
    for i in NEO_N_REVERSE:
        c = f"neo{i}"
        if c in block.columns:
            block[c] = (lo + hi) - block[c]
    return block.sum(axis=1, min_count=len(cols))


def main() -> None:
    df, meta = pyreadstat.read_sav(str(paths.RAW_BASELINE_SAV))
    df["subject"] = pd.to_numeric(df["subject"], errors="coerce")
    df = df[df["subject"].notna()].copy()
    df["subject"] = df["subject"].astype(int)

    out = pd.DataFrame({"subject": df["subject"]})

    # Demographics.
    out["gender"] = df["geslacht"].map({0: "female", 1: "male"})
    out["age"] = df["leeftijd"]
    out["education"] = df["opleid"]
    out["pain_duration_months"] = df["duur"]

    # Threat-value account.
    pcs_sum = _sum_items(df, "pcs", list(range(1, 14)))
    out["PCS_total"] = df["pcstot"].where(df["pcstot"].notna(), pcs_sum)
    out["PVAQ_total"] = _sum_items(df, "pvaq", PVAQ_ITEMS)

    # Biomedical account.
    out["MPI_pain_severity"] = df["mpips2"]           # pre-scored 3-item MPI pain severity
    out["MPI_interference"] = df["mpipi2"]

    # Personality account.
    out["NEO_neuroticism"] = _neo_neuroticism(df)

    # Additional clinical descriptors used in Table 1.
    out["MPI_life_control"] = df["mpilc2"]
    out["MPI_affective_distress"] = df["mpiad2"]
    out["PDI_total"] = df["pdi"]
    out["HADS_anxiety"] = df["hadsang"]
    out["HADS_depression"] = df["hadsdep"]
    out["HADS_total"] = df["hadstot"]
    out["PCS_rumination"] = df["pcsrum"]
    out["PCS_magnification"] = df["pcsmag"]
    out["PCS_helplessness"] = df["pcshelp"]

    out = out.sort_values("subject").reset_index(drop=True)
    out.to_csv(paths.PERSON_LEVEL, index=False)

    # Convergent validity check for the neuroticism key: trait neuroticism should correlate
    # positively with HADS distress if the reverse-scoring is oriented correctly.
    r = out[["NEO_neuroticism", "HADS_total"]].corr().iloc[0, 1]

    print("=" * 66)
    print("Person-level baseline summary")
    print("=" * 66)
    print(f"baseline participants        : {len(out)}")
    print(f"PCS total (mean, range)      : {out.PCS_total.mean():.1f} "
          f"[{out.PCS_total.min():.0f}, {out.PCS_total.max():.0f}]")
    print(f"PVAQ total (mean, range)     : {out.PVAQ_total.mean():.1f} "
          f"[{out.PVAQ_total.min():.0f}, {out.PVAQ_total.max():.0f}]")
    print(f"MPI pain severity (mean)     : {out.MPI_pain_severity.mean():.2f}")
    print(f"NEO neuroticism (mean)       : {out.NEO_neuroticism.mean():.1f}")
    print(f"pain duration months (median): {out.pain_duration_months.median():.0f}")
    print(f"NEO-N vs HADS-total r        : {r:+.2f} "
          f"({'orientation OK' if r > 0 else 'CHECK KEYING'})")
    print(f"wrote {paths.PERSON_LEVEL}")


if __name__ == "__main__":
    main()
