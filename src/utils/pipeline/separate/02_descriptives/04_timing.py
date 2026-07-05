"""Stage 02.4 - Diary timing and compliance audit.

Documents the intended eight-per-day, two-week signal-contingent protocol: prompts per
person-day, completed prompts per person, and compliance across the fourteen study days.
These summaries feed the design/compliance supplementary figure.
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


def main() -> None:
    d = pd.read_csv(paths.EMA_LONG)

    per_person = (d.groupby("pid")
                    .agg(n_completed=("completed", "sum"),
                         n_days=("day", "nunique"),
                         max_beep=("beep", "max"))
                    .reset_index())
    per_person.to_csv(T / "02_compliance_per_person.csv", index=False)

    prompts_per_day = (d.groupby(["pid", "day"]).size().reset_index(name="n_prompts"))
    daily = (prompts_per_day.groupby("day")["n_prompts"]
             .agg(["mean", "std", "min", "max"]).round(2).reset_index())
    daily.to_csv(T / "02_timing_daily_counts.csv", index=False)

    summary = pd.DataFrame({
        "metric": ["participants", "completed prompts", "prompts per person (median)",
                   "prompts per person-day (mean)", "study days per person (median)",
                   "max prompts per day"],
        "value": [d["pid"].nunique(),
                  int(d["completed"].sum()),
                  float(per_person["n_completed"].median()),
                  round(prompts_per_day["n_prompts"].mean(), 2),
                  float(per_person["n_days"].median()),
                  int(prompts_per_day["n_prompts"].max())],
    })
    summary.to_csv(T / "02_timing_summary.csv", index=False)

    print("stage 02.4 timing:")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
