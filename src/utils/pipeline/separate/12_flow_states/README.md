# Stage 12 - Flow states

Operationalizes Csikszentmihalyi's flow construct from the four momentary activity appraisals
in the diary and relates it to the momentary experience of pain.

The four items split into an antecedent challenge-skill **condition** (`CHALLENGE`, `EFFIC`)
and the **flow experience** itself (`ENGAGE`, `VALENCE`). They are never summed into a single
score, because that conflates antecedent with outcome. Every derived flow variable is a
secondary, analyst-constructed measure: Viane et al. (2004) analysed these items separately
and never as a flow index.

| Script | What it does |
| --- | --- |
| `01_flow_construct.R` | Builds the flow variables, the four-channel classification under four standardization rules, per-person prevalence, the multilevel condition-to-experience model, and the standardization sensitivity table. |
| `02_flow_pain_models.R` | Contemporaneous and lag-1 multilevel models of flow with pain, attention to pain, interference, and threat, plus the per-person distribution of the flow-pain coupling. |
| `03_flow_trait_link.py` | Person-level flow proneness against the stage 08 baseline accounts, incremental variance, and the profile of the persons whose flow-pain coupling is negative. |
| `flow_analysis/` | Standalone notebook with the complete analysis, its interpretation, the decision record, and a cross-validation of this R implementation against an independent Python one. Start there for the substance. |

Standardization is the decision that drives interpretation. Within-person z-scoring makes every
person's mean zero and therefore mechanically assigns above-average moments to everyone,
including a person who was never in flow in any absolute sense. Person-mean centering is the
default here; absolute and within-z metrics are carried as sensitivity analyses.
