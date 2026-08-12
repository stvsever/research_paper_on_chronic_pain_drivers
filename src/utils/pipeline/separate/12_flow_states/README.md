# Stage 12 - Flow states

Operationalizes Csikszentmihalyi's flow construct from the four momentary activity appraisals in
the diary and relates it to the momentary experience of pain.

The four items split into an antecedent challenge-skill **condition** (`CHALLENGE`, `EFFIC`) and
the **flow experience** itself (`ENGAGE`, `VALENCE`). They are never summed into a single score,
because that conflates antecedent with outcome. Every derived flow variable is a secondary,
analyst-constructed measure: Viane et al. (2004) analysed these items separately and never as a
flow index.

## Layout

| Path | What it is |
| --- | --- |
| `scripts/` | The analysis. All estimation happens here, and it runs inside `make run-all`. |
| `flow_analysis/` | The report: a pre-run notebook that reads the scripts' output, plus a written specification and decision record. **Start here for the substance.** |

## `scripts/`

| Script | What it does |
| --- | --- |
| `01_flow_construct.R` | Builds the flow variables, the four-channel classification under five standardization rules, per-person prevalence, the multilevel condition-to-experience model with two alternative parameterizations, the standardization sensitivity table, the day and time-of-day covariate check, and the missingness characterisation. |
| `02_flow_pain_models.R` | Concurrent and lag-1 multilevel models of flow with pain, attention to pain, interference, and threat; the lagged condition-to-experience test; channel contrasts; the per-person distribution of the flow-pain coupling; and the compliance-threshold sensitivity. |
| `03_flow_trait_link.py` | Person-level flow proneness against the stage 08 baseline accounts, incremental variance, and the profile of the persons whose flow-pain coupling is negative. |
| `04_flow_mlvar.R` | Re-estimates the benchmark network with the flow composite in place of the single absorption node, and decomposes the composite into its four constituents entered alone and jointly. |

Outputs land in `src/results/tables/12_flow_*.csv` and `src/results/models/12_flow_analytic_frame.csv`.

## The standardization decision

This is where most ESM flow analyses go wrong. Within-person z-scoring makes every person's mean
zero and therefore mechanically assigns above-average moments to everyone, including a person who
was never in flow in any absolute sense. Person-mean centering is the default here; the raw
absolute scale carries every prevalence claim, and grand-mean z and within-person z run as
sensitivity analyses.

## Reproducing

```bash
make run-stage STAGE=12
```

then re-run `flow_analysis/analyze_flow.ipynb` to refresh its tables and figures.
