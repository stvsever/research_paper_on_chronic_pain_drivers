# Pipeline

The analysis is organized as numbered stages under `separate/`, each a self-contained script
folder with its own short README. The single entry point `full/run_all.py` runs every stage in
order (Python stages in-process, R stages through `Rscript`). Use `--from` to resume and
`--only` to run a single stage prefix.

| Stage | What it does |
| --- | --- |
| 01 | Preprocessing: score baseline traits and build the momentary long file. |
| 02 | Descriptives: sample table, momentary descriptives, context, time-in-study, timing. |
| 03 | Variance decomposition (between-person, between-day, within-day). |
| 04 | Stationarity checks and a missing-data imputation benchmark. |
| 05 | mlVAR pooled benchmark network and residual diagnostics. |
| 06 | S-GIMME confirmatory idiographic estimator. |
| 07 | Primary per-person graphicalVAR networks and per-person pain-equation VAR. |
| 08 | Baseline threat, biomedical, and personality trait profiles (RQ2). |
| 09 | Link between person-specific couplings and baseline accounts (RQ2). |
| 10 | Robustness battery (detrended, attention composite, compliance, extended, LOO, bootstrap). |
| 11 | Daily dysfunction dynamics (evening functioning outcomes). |
| 12 | Figures and tables for the manuscript. |

R does the statistical models; Python does preprocessing, orchestration, and visualization.
The boundary is deliberate and is documented in `src/utils/lib/runr.py`.
