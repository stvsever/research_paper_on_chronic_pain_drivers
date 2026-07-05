"""Stage 12.3 - Markdown mirrors of the manuscript tables (human-readable audit copies)."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

LIB = Path(__file__).resolve().parents[3] / "lib"
sys.path.insert(0, str(LIB))
import paths  # noqa: E402

T = paths.RESULTS_TABLES
N = paths.RESULTS_NETWORKS
MD_MAIN = paths.TABLES_MAIN
MD_SUPP = paths.TABLES_SUPP
paths.ensure_dirs()


def df_to_md(df: pd.DataFrame) -> str:
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |",
             "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join("" if pd.isna(v) else str(v) for v in row.values) + " |")
    return "\n".join(lines)


def write_md(df: pd.DataFrame, path: Path, title: str):
    path.write_text(f"### {title}\n\n" + df_to_md(df) + "\n")
    print("  wrote", path.relative_to(paths.ROOT))


def main():
    write_md(pd.read_csv(T / "02_person_level_table1.csv"),
             MD_MAIN / "MAIN_01_sample_descriptives.md", "Baseline characteristics")
    ed = pd.read_csv(T / "02_ema_descriptives.csv")
    vd = pd.read_csv(T / "03_variance_decomposition.csv")[["variable", "icc_person",
                                                           "var_within_day"]]
    write_md(ed.merge(vd, on="variable", how="left"),
             MD_MAIN / "MAIN_02_ema_descriptives_variance.md", "Momentary descriptives")
    write_md(pd.read_csv(N / "05_mlvar_core_temporal_edges.csv"),
             MD_MAIN / "MAIN_03_mlvar_temporal_effects.md", "Pooled temporal effects")
    write_md(pd.read_csv(T / "09_between_person_correlations.csv"),
             MD_MAIN / "MAIN_04_trait_between_person.md", "RQ2 between-person associations")
    print("markdown tables written")


if __name__ == "__main__":
    main()
