# `src/` overview

Everything that turns the raw diary files into the numbers, figures, and tables in the manuscript.

| Path | What lives there |
| --- | --- |
| [`data/`](data) | `raw/` holds the four archived SPSS files (baseline questionnaires, and the morning, day, and evening diaries). `processed/` holds the analysis-ready files built by pipeline stage 01: `ema_long.csv` (one row per completed momentary prompt), `person_level.csv` (one row per participant), and the exclusion log. |
| [`results/`](results) | Everything the pipeline computes. `tables/` holds the numeric results as CSV, one prefix per stage. `networks/` holds the estimated network edge lists. `models/` holds fitted model objects and derived analytic frames. `logs/` holds run logs. |
| [`utils/`](utils) | The code. `pipeline/` is the analysis itself, `lib/` holds shared helpers, and `study_materials/` holds the codebook and the original study documentation. |

## The pipeline

`utils/pipeline/full/run_all.py` is the single entry point and runs every stage in order. Each
stage is a self-contained folder under `utils/pipeline/separate/` with its own README.

```bash
make run-all              # everything, from raw data to manuscript assets
make run-stage STAGE=12   # one stage
make run-from  STAGE=07   # resume from a stage
```

| Stage | What it does |
| --- | --- |
| 01 | Preprocessing: score baseline traits, build the momentary long file |
| 02 | Descriptives: sample, momentary measures, context, timing |
| 03 | Variance decomposition (between person, between day, within day) |
| 04 | Stationarity checks and a missing-data imputation benchmark |
| 05 | mlVAR pooled benchmark network and residual diagnostics |
| 06 | S-GIMME confirmatory idiographic estimator |
| 07 | Per-person graphicalVAR networks and per-person pain-equation VAR |
| 08 | Baseline threat, biomedical, and personality trait profiles |
| 09 | Link between person-specific couplings and the baseline profiles |
| 10 | Robustness battery (detrending, composites, compliance, bootstrap, leave-one-out) |
| 11 | Daily dysfunction dynamics from the evening diary |
| 12 | Flow states: the challenge-skill condition, the flow experience, and their relation to pain |
| 13 | Figures and tables for the manuscript |

R does the statistical models, Python does preprocessing, orchestration, and visualization. The
boundary is documented in `utils/lib/runr.py`. Shared constants and derived-variable builders live
in `utils/lib/common.R`; the figure palette lives in `utils/lib/vizstyle.py`.

## Where the manuscript assets come from

Stage 13 writes directly into `../paper/assets/`: main and supplementary figures as PNG, and the
tables as both LaTeX (which the manuscript inputs) and Markdown (readable audit copies). Nothing in
`paper/` is hand-edited except `report/main.tex`.
