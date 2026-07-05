"""Stage 01.2 - Build the analysis-ready long-format EMA dataset.

Reads the momentary ("day") diary, recodes the reverse-keyed and composite items,
derives the time structure required by the temporal models (beep within day, day within
person), merges the morning and evening diaries as day-level covariates, applies the
documented compliance exclusions, and flags which participants have enough completed
prompts for fully individual (idiographic) network estimation.

Outputs:
  - src/data/processed/ema_long.csv      (one row per completed momentary prompt)
  - src/data/processed/exclusion_log.csv (audit trail of excluded participants)
  - adds analytic flags to person_level.csv.
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

SCALE_MAX = 7          # momentary rating items are on a 1..7 scale
MIN_COMPLETE = 25      # below this a participant is excluded from all analyses
MIN_IDIO = 50          # at/above this a participant is eligible for individual networks


def _to_minutes(s: pd.Series) -> pd.Series:
    """Parse an 'HH:MM' clock string into minutes since midnight for ordering."""
    t = s.astype(str).str.extract(r"(\d{1,2}):(\d{2})")
    return pd.to_numeric(t[0], errors="coerce") * 60 + pd.to_numeric(t[1], errors="coerce")


def main() -> None:
    df, meta = pyreadstat.read_sav(str(paths.RAW_DIARY_DAY))
    df = df.rename(columns={"SUBJECT": "subject"})
    for c in ("subject", "WEEK", "DAG"):
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
    df = df[df["subject"].notna()].copy()

    n_subjects_raw = df["subject"].nunique()
    n_rows_raw = len(df)

    # --- time structure -------------------------------------------------------
    df["minute"] = _to_minutes(df["UUR"])
    df = df.sort_values(["subject", "WEEK", "DAG", "minute"]).reset_index(drop=True)

    # Per-person sequential day index (1..) from the (week, day) blocks actually present,
    # in chronological order. This is the dayvar the temporal models use to avoid building
    # a lag across the overnight gap.
    def _day_index(g: pd.DataFrame) -> pd.Series:
        keys = list(dict.fromkeys(zip(g["WEEK"], g["DAG"])))
        lut = {k: i + 1 for i, k in enumerate(keys)}
        return g.apply(lambda r: lut[(r["WEEK"], r["DAG"])], axis=1)
    df["day"] = df.groupby("subject", group_keys=False).apply(_day_index)
    df["study_week"] = np.where(df["day"] <= 7, 1, 2)
    # beep order within a person-day
    df["beep"] = df.groupby(["subject", "day"]).cumcount() + 1

    # --- node and auxiliary variables (transparent recoding) ------------------
    # Pain-side nodes.
    df["PIJN"] = df["PIJNINTE"]                      # pain intensity (sensory)
    df["PIJN_AFF"] = df["PIJN_AFF"]                  # pain interference ("pain hinders me")
    df["ATTEND"] = df["AANDACH1"]                    # attention to pain ("I focus on my pain")
    df["IGNORE"] = (SCALE_MAX + 1) - df["AANDACH2"]  # "I can ignore the pain" -> reverse
    df["ATTEND2"] = df[["ATTEND", "IGNORE"]].mean(axis=1)  # 2-item attention composite
    df["FEAR"] = df["VR_ANGST"]                      # pain-related fear
    df["CATAS"] = df["CAT_HULP"]                     # catastrophizing / helplessness
    # Threat value of pain = fear + catastrophizing, the appraisal that, in the
    # interruptive-function model, amplifies the attentional capture by pain.
    df["THREAT"] = df[["FEAR", "CATAS"]].mean(axis=1)

    # Goal-directed activity characteristics (Klinger's goal-directed motivation model).
    df["ENGAGE"] = df["ACT_AAND"]                    # engagement / absorption in the activity
    df["EFFIC"] = df["ACT_SUC"]                      # efficacy ("I am good at this")
    df["VALENCE"] = df["ACT_MOT"]                    # valence ("I like doing this")
    df["CHALLENGE"] = df["ACT_UITD"]                 # personal challenge
    df["IMPORTANCE"] = df["ACT_INSP"]               # motivation to complete

    # Affect (retained for descriptives / robustness).
    df["NEGAFF"] = df[["SOMBER", "ANGSTIG", "GEFRUSTR"]].mean(axis=1)
    df["POSAFF"] = df[["OPGEWEKT", "ONTSPANN", "TEVREDEN"]].mean(axis=1)
    df["ACTIEF"] = df["ACTIEF"]                      # self-reported physical activation
    df["location"] = df["CONTEXT"]
    df["alone"] = df["ALLEEN"].where(df["ALLEEN"].isin([0, 1]))
    df["social_pleasant"] = df["CONT_AFF"]
    df["medication"] = df["MEDICAT"].where(df["MEDICAT"].isin([0, 1]))
    df["disturbed"] = df["STOORT"]

    # a prompt is "completed" when the core pain item was answered
    df["completed"] = df["PIJN"].notna()

    # --- merge morning and evening diaries as day-level covariates ------------
    morn, _ = pyreadstat.read_sav(str(paths.RAW_DIARY_MORNING))
    morn = morn.rename(columns={"slaap": "morn_sleep", "pijn": "morn_pain"})
    morn_keyed = _prep_day_level(morn, ["morn_sleep", "morn_pain"])
    df = _merge_day_level(df, morn_keyed)

    eve, _ = pyreadstat.read_sav(str(paths.RAW_DIARY_EVENING))
    eve = eve.rename(columns={
        "plan": "eve_goal_success", "pijncont": "eve_pain_control",
        "pijnhind": "eve_pain_interference", "act_invl": "eve_activity_on_pain",
        "gewoon": "eve_ordinary", "tevred": "eve_satisfied", "stem_inv": "eve_reactivity",
    })
    eve_cols = ["eve_goal_success", "eve_pain_control", "eve_pain_interference",
                "eve_activity_on_pain", "eve_ordinary", "eve_satisfied", "eve_reactivity"]
    eve_keyed = _prep_day_level(eve, eve_cols)
    df = _merge_day_level(df, eve_keyed)

    # --- compliance and exclusions --------------------------------------------
    comp = df.groupby("subject")["completed"].sum()
    excluded = comp[comp < MIN_COMPLETE].index.tolist()
    rows = [{"subject": int(s), "n_completed": int(comp[s]),
             "reason": f"fewer than {MIN_COMPLETE} completed prompts"} for s in excluded]
    pd.DataFrame(rows, columns=["subject", "n_completed", "reason"]).to_csv(
        paths.EXCLUSION_LOG, index=False)

    analytic = df[~df["subject"].isin(excluded) & df["completed"]].copy()
    subj_order = sorted(analytic["subject"].unique())
    id_map = {s: f"P{idx + 1:02d}" for idx, s in enumerate(subj_order)}
    analytic["pid"] = analytic["subject"].map(id_map)

    keep = ["pid", "subject", "day", "beep", "study_week", "completed",
            "PIJN", "PIJN_AFF", "ATTEND", "ATTEND2", "IGNORE", "THREAT", "FEAR", "CATAS",
            "ENGAGE", "EFFIC", "VALENCE", "CHALLENGE", "IMPORTANCE",
            "NEGAFF", "POSAFF", "ACTIEF",
            "location", "alone", "social_pleasant", "medication", "disturbed",
            "morn_sleep", "morn_pain",
            "eve_goal_success", "eve_pain_control", "eve_pain_interference",
            "eve_activity_on_pain", "eve_ordinary", "eve_satisfied", "eve_reactivity"]
    keep = [c for c in keep if c in analytic.columns]
    ema = analytic[keep].sort_values(["pid", "day", "beep"]).reset_index(drop=True)
    ema.to_csv(paths.EMA_LONG, index=False)

    # --- flags on person_level.csv --------------------------------------------
    comp_analytic = ema.groupby("subject")["completed"].sum()
    idio = comp_analytic[comp_analytic >= MIN_IDIO].index.tolist()
    if paths.PERSON_LEVEL.exists():
        pl = pd.read_csv(paths.PERSON_LEVEL)
        pl["pid"] = pl["subject"].map(id_map)
        pl["in_analytic_sample"] = pl["subject"].isin(subj_order)
        pl["idiographic_eligible"] = pl["subject"].isin(idio)
        pl["n_completed"] = pl["subject"].map(comp_analytic).astype("Int64")
        pl.to_csv(paths.PERSON_LEVEL, index=False)

    # --- report ---------------------------------------------------------------
    c = ema.groupby("pid")["completed"].sum()
    print("=" * 66)
    print("EMA preprocessing summary")
    print("=" * 66)
    print(f"raw diary subjects           : {n_subjects_raw}")
    print(f"raw diary rows               : {n_rows_raw}")
    print(f"excluded (< {MIN_COMPLETE} completed)   : {len(excluded)} -> {excluded}")
    print(f"analytic participants        : {len(subj_order)}")
    print(f"analytic completed prompts   : {int(ema['completed'].sum())}")
    print(f"completed per person         : median {c.median():.0f} "
          f"(mean {c.mean():.1f}, range {c.min()}-{c.max()})")
    print(f"idiographic-eligible (>= {MIN_IDIO}) : {len(idio)} participants")
    print(f"wrote {paths.EMA_LONG}")


def _prep_day_level(frame: pd.DataFrame, value_cols: list[str]) -> pd.DataFrame:
    """Reduce a morning/evening diary to one row per (subject, week, day)."""
    f = frame.rename(columns={"subject": "subject", "week": "WEEK", "dag": "DAG"})
    for c in ("subject", "WEEK", "DAG"):
        # morning/evening week is stored as strings such as '1.TXT'; extract the integer.
        digits = f[c].astype(str).str.extract(r"(\d+)")[0]
        f[c] = pd.to_numeric(digits, errors="coerce").astype("Int64")
    cols = ["subject", "WEEK", "DAG"] + [c for c in value_cols if c in f.columns]
    f = f[cols].dropna(subset=["subject"])
    return f.groupby(["subject", "WEEK", "DAG"], as_index=False).mean(numeric_only=True)


def _merge_day_level(df: pd.DataFrame, keyed: pd.DataFrame) -> pd.DataFrame:
    return df.merge(keyed, on=["subject", "WEEK", "DAG"], how="left")


if __name__ == "__main__":
    main()
