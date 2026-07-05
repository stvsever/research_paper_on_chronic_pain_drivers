"""Stage 02.2 - Everyday context of the momentary reports.

Summarizes pain and its drivers by location and by social context, and describes the
medication and interruption items. Context is descriptive here; it is not part of the
temporal model, but it documents where and with whom the diaries were completed.
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

LOC = {1: "Home", 2: "Outside/underway", 3: "Work", 4: "Hospital", 5: "Other", 6: "Other"}


def main() -> None:
    d = pd.read_csv(paths.EMA_LONG)
    d["location_lab"] = d["location"].map(LOC)

    loc = (d.groupby("location_lab")
             .agg(n_prompts=("PIJN", "size"),
                  mean_pain=("PIJN", "mean"),
                  mean_attend=("ATTEND", "mean"),
                  mean_fear=("FEAR", "mean"),
                  mean_engage=("ENGAGE", "mean"))
             .reset_index())
    loc["pct"] = 100 * loc["n_prompts"] / loc["n_prompts"].sum()
    loc = loc.sort_values("n_prompts", ascending=False).round(2)
    loc.to_csv(T / "02_context_by_location.csv", index=False)

    d["social_lab"] = d["alone"].map({1: "Alone", 0: "Accompanied"})
    soc = (d.dropna(subset=["social_lab"]).groupby("social_lab")
             .agg(n=("PIJN", "size"),
                  mean_pain=("PIJN", "mean"),
                  mean_attend=("ATTEND", "mean"),
                  mean_fear=("FEAR", "mean"),
                  mean_engage=("ENGAGE", "mean"))
             .reset_index().round(2))
    soc.to_csv(T / "02_context_by_social.csv", index=False)

    summ = pd.DataFrame({
        "item": ["Took pain medication since last beep (%)",
                 "Beep felt disturbing (mean 1-7)",
                 "Social situation pleasant (mean 1-7)",
                 "Alone (%)"],
        "value": [round(100 * (d["medication"] == 1).mean(), 1),
                  round(d["disturbed"].mean(), 2),
                  round(d["social_pleasant"].mean(), 2),
                  round(100 * (d["alone"] == 1).mean(), 1)],
    })
    summ.to_csv(T / "02_context_activity_summary.csv", index=False)

    print("stage 02.2 context: locations ->")
    print(loc[["location_lab", "n_prompts", "pct", "mean_pain"]].to_string(index=False))


if __name__ == "__main__":
    main()
