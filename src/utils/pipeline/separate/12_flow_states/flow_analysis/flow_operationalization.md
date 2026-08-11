# Flow operationalization: specification and decision record

Companion reference to [`analyze_flow.ipynb`](analyze_flow.ipynb). The notebook is the full
report with all output; this file is the compact specification, the decision record, and the
results summary, for anyone who wants the substance without opening the notebook.

All models are estimated by the scripts in [`../scripts/`](../scripts/); the notebook is the
reporting layer over their output.

Project 21: Viane et al. (2004, *Pain*) / Crombez et al. (2013). Palmtop experience sampling, 8
random beeps per day plus a morning and an evening diary, 14 days.

**Status.** Analysis complete and implemented as pipeline stage 12.

---

## 1. The construct

Flow is a state of deep absorption and effortless concentration, arising when perceived challenge
and perceived skill are both high and roughly matched, and experienced as intrinsically rewarding
(Csikszentmihalyi, 1990). It has two structurally distinct parts that must not be merged:

- an **antecedent condition**, the challenge-skill configuration, and
- the **experience** itself, absorption plus enjoyment.

## 2. The four items

| Facet, and its role | Item (EN) | Item (NL) | Column (raw) |
| --- | --- | --- | --- |
| Challenge, antecedent condition | This activity is a personal challenge to me | Deze activiteit is een persoonlijke uitdaging voor mij | `CHALLENGE` (`ACT_UITD`) |
| Skill, antecedent condition | I am good at it | Ik kan dit goed | `EFFIC` (`ACT_SUC`) |
| Absorption, core experience | I am absorbed in this activity | Ik ga op in deze activiteit | `ENGAGE` (`ACT_AAND`) |
| Enjoyment, autotelic marker | I like doing this | Ik doe dit graag | `VALENCE` (`ACT_MOT`) |

All 7-point, "not at all" to "very much". Challenge and skill descend from the Delespaul ESM
tradition; absorption and enjoyment were assigned by the original authors to Klinger's framework.

**Coverage.** Three of Csikszentmihalyi's nine dimensions (challenge-skill balance, concentration
through absorption, autotelic experience through enjoyment) plus the antecedent condition. Not
measured: clear goals, unambiguous feedback, sense of control, loss of self-consciousness, time
transformation. The correct label is a **core flow proxy**, never "a measure of flow".

**Provenance.** The original study analysed these items separately and never as a flow index.
Every derived variable here is a secondary, analyst-constructed measure and must be reported as
such. This is an analysis decision, not a re-coding of the source data.

## 3. Formulas

```
flow experience = mean(absorption, enjoyment)

balance         = -|challenge - skill|          higher = better matched
elevation       = (challenge + skill) / 2       higher = both high

gated flow index = (challenge >= cut AND skill >= cut) AND (flow experience >= cut)
```

Balance without elevation would score a low-challenge, low-skill moment (apathy) as perfectly
balanced, so the elevation term is required. The four items are never summed into one score:
that conflates the antecedent with the outcome.

## 4. Decision record

| Decision | Choice | Reason |
| --- | --- | --- |
| Research question | All three: V1 prevalence, V2 model, V3 dynamics, each with its own operationalization | They ask different things and must not be mixed |
| Standardization | **D** person-mean centering primary; **A** raw absolute for all prevalence claims; **B** grand-mean z and **C** within-person z as sensitivity | D separates level from fluctuation and is the multilevel standard. Only A can represent the absence of flow |
| Day and time of day | Tested as level-1 covariates, then omitted from the reported models | Time of day is significant in its own right but changes no focal estimate (elevation 0.7443 to 0.7456; flow-pain -0.0937 to -0.1010) |
| Flow condition | **Continuous** balance and elevation primary; quadrant retained for description; additive form also fitted | Continuous retains information; the additive form turns out to fit best |
| Absolute threshold | Both items **>= 5** conservative, **>= 4** reported alongside | Only under the strict rule can a participant score zero |
| Analysis track | **B** hybrid multilevel with random slopes primary; **C** per person for heterogeneity | Estimates the average effect and the spread at once; partial pooling stabilises short series |
| Compliance minimum | **50 valid moments** for person-level estimates; all participants in the multilevel models | The project's existing idiographic floor, stricter than the 20 to 30 suggested |
| Sensitivity analyses | Standardization A/B/C/D; quadrant versus continuous; day and time of day as covariates; compliance at 20/30/50/70 | Each targets a choice that could have driven a conclusion. None does |
| Flow experience | Mean of absorption and enjoyment | The enjoyment gate separates flow from effortful struggle, essential in a pain context |
| Index versus model | Both: gated index for V1, model test for V2 | They answer different questions |
| Valid response | Project definition (core pain item answered) | The 15-minute protocol window is unrecoverable: the archive holds only entry times, no signal timestamps |
| Lag construction | Within day, on person-standardized scores | Matches the convention used elsewhere in the study |
| Activity control | Physical activation adjusted models alongside unadjusted | Challenge correlates r = .57 within persons with being active, and activity raises pain |
| Missingness | Documented, no imputation | 4.6 percent listwise loss with a mild, characterised deviation |

## 5. Analytic frame

5,976 moments in 68 persons, median 92 per person. Every flow item has an ICC of .20 to .24, so
roughly 78 percent of the variance is within person. Listwise loss 4.6 percent; skipped moments
carry slightly more threat (d = 0.15) and negative affect (d = 0.19) but not more pain.

## 6. Results

### V1, prevalence

| Rule | Condition met | Gated flow | Median person | Persons at zero |
| --- | --- | --- | --- | --- |
| A. Absolute, both >= 4 | 39.6% | 36.8% | 35.0% | 0 of 68 |
| A. Absolute, both >= 5 | 22.0% | 19.3% | 16.4% | **4 of 68** |
| B. Grand-mean z | 30.6% | 27.8% | 26.7% | 2 of 68 |
| C. Within-person z | 28.9% | 24.6% | 24.5% | 0 of 68 |
| D. Person-mean centred | 28.9% | 24.6% | 24.5% | 0 of 68 |

Flow-like moments are common. The relative metrics cannot represent absence, which is why every
prevalence claim is made on metric A. Under the strict rule the largest channel is **relaxation**
(37.0 percent), not flow (22.0 percent).

### V2, does the flow model hold

`FLOWEXP ~ balance_w + elevation_w + balance_b + elevation_b + (1 + balance_w + elevation_w | pid)`

| Term | b | SE | p | Random SD |
| --- | --- | --- | --- | --- |
| Elevation (within) | **0.744** | 0.024 | <.001 | 0.164 |
| Balance (within) | 0.006 | 0.020 | .78 | 0.132 |
| Elevation (between) | **0.796** | 0.085 | <.001 | |
| Balance (between) | **-0.111** | 0.049 | **.028** | |

Balance is null within persons and significantly negative between persons and on the raw scale
(b = -0.090, p < .001). Across all four standardization metrics, elevation stays between 0.74 and
0.89 and balance is never positive. Model comparison: additive challenge plus skill AIC 16880,
balance plus elevation 17321, categorical quadrant 18482; the challenge-by-skill interaction is
not significant (p = .15).

**The flow condition acts additively in these data, not configurationally.**

### V3, temporal structure and person specificity

Condition at t-1 predicting the experience at t, controlling the flow-experience autoregression:
elevation b = 0.052, SE = 0.028, p = .062 (marginal, not significant); balance b = -0.007, p = .70.
The lagged elevation effect is 6 percent of the concurrent one (0.052 against 0.856), so the
temporal antecedence the theory implies is not detectable at this sampling interval.

Per-person flow-pain slopes (63 persons, person-standardized):

| | Median | IQR | Range | % negative | Reliably negative | Reliably positive |
| --- | --- | --- | --- | --- | --- | --- |
| Concurrent | -0.137 | -0.203 to 0.010 | -0.465 to 0.445 | 73.0% | 14 | 4 |
| Lag 1 | -0.000 | -0.084 to 0.052 | -0.265 to 0.227 | 49.2% | 2 | 0 |

### Flow and the momentary experience of pain

Concurrent, activity-adjusted, within persons:

| Outcome | b | SE | p | Random SD |
| --- | --- | --- | --- | --- |
| Pain interference | **-0.139** | 0.025 | <.001 | 0.146 |
| Pain intensity | **-0.094** | 0.020 | <.001 | 0.114 |
| Threat value | **-0.079** | 0.014 | <.001 | 0.071 |
| Attention to pain | **-0.074** | 0.019 | <.001 | 0.097 |

Lag 1, both directions: all seven paths null (p between .28 and .94), while every autoregression is
large and significant (pain 0.395, interference 0.352, threat 0.321, attention 0.266). The relation
is strictly concurrent.

Channel contrasts against apathy: flow is better on all four outcomes (-0.070 to -0.179), but
**relaxation is better still** (-0.167 to -0.280), and anxiety is no better than apathy and
significantly worse on interference (+0.131, p = .015).

### Person-level flow proneness and baseline profiles

Mean flow experience correlates -0.27 with the baseline threat profile (p = .028) and -0.26 with
neuroticism (p = .035); both survive partialling out mean pain. No baseline account predicts the
flow-pain slope. Flow proneness adds delta R2 = .081 to the prediction of mean pain over the three
accounts.

### Robustness

Standardization A/B/C/D: elevation 0.74 to 0.89 everywhere, balance never positive. Day and beep
number as level-1 covariates: time of day is itself significant but no focal estimate moves.
Compliance floor at 20, 30, 50, 70 moments: the flow-pain estimate moves from -0.0937 to -0.0883
and stays significant throughout.

## 7. Conclusions in one paragraph

Absorption in what one is doing accompanies a better momentary pain experience, particularly less
disruption, but it does so at the same moment rather than across time, and the challenge component
that flow theory treats as constitutive brings a physical cost in this population that partly
offsets the benefit. Three boundaries apply: the effect is concurrent only, it is small, and it is
not universal across persons. The flow model itself holds only half: elevation drives the
experience, balance does not, and between persons balance reverses.

## 8. Caveats to report alongside any result

Single-item indicators; core flow proxy covering three of nine dimensions; secondary
analyst-constructed operationalization; the enjoyment gate is essential in a pain context; the
challenge-activity confound (r = .57) drives the channel-level pain ordering; concurrent only;
prevalence claims only on the absolute metric; 4.6 percent listwise loss; the 15-minute response
window could not be applied; 68 participants, so the person-level analyses are exploratory;
several random-slope models sit near a singular boundary where slope variance is genuinely near
zero; no multiplicity correction applied.

## 9. Where everything lives

| Item | Location |
| --- | --- |
| Full analysis notebook | `analyze_flow.ipynb` (this directory) |
| Figures | `figures/` (this directory) |
| Analysis scripts (all estimation) | `../scripts/` (`01_flow_construct.R`, `02_flow_pain_models.R`, `03_flow_trait_link.py`) |
| Numeric results | `src/results/tables/12_flow_*.csv` |
| Derived analytic frame | `src/results/models/12_flow_analytic_frame.csv` |
| Manuscript figures | `paper/assets/figures/main/MAIN_05_flow_states.png`, `paper/assets/figures/supplementary/SUP_11_flow_operationalization.png` |
| Manuscript tables | `paper/assets/tables/main/MAIN_05_flow_pain_models.tex`, `paper/assets/tables/supplementary/SUP_13_flow_operationalization.tex` |

Regenerate the numbers with `make run-stage STAGE=12`, then re-run the notebook to refresh its
tables and figures. Appendix A of the notebook maps every reported result to the script and file
that produced it.

## 10. References

- Csikszentmihalyi, M. (1990). *Flow: The Psychology of Optimal Experience*. Harper & Row.
- Csikszentmihalyi, M., & Larson, R. (1987). *Journal of Nervous and Mental Disease*, 175(9),
  526-536. [doi:10.1097/00005053-198709000-00004](https://doi.org/10.1097/00005053-198709000-00004)
- Massimini, F., & Carli, M. (1988). In *Optimal Experience*. Cambridge University Press.
  [doi:10.1017/CBO9780511621956.014](https://doi.org/10.1017/CBO9780511621956.014)
- Moneta, G. B., & Csikszentmihalyi, M. (1996). *Journal of Personality*, 64(2), 275-310.
  [doi:10.1111/j.1467-6494.1996.tb00512.x](https://doi.org/10.1111/j.1467-6494.1996.tb00512.x)
- Fong, C. J., Zaleski, D. J., & Leach, J. K. (2015). *Journal of Positive Psychology*, 10(5),
  425-446. [doi:10.1080/17439760.2014.967799](https://doi.org/10.1080/17439760.2014.967799)
- Nakamura, J., & Csikszentmihalyi, M. (2014). In *Flow and the Foundations of Positive
  Psychology*. Springer.
  [doi:10.1007/978-94-017-9088-8_16](https://doi.org/10.1007/978-94-017-9088-8_16)
- Jackson, S. A., & Eklund, R. C. (2002). *Journal of Sport and Exercise Psychology*, 24(2),
  133-150. [doi:10.1123/jsep.24.2.133](https://doi.org/10.1123/jsep.24.2.133)
- Curran, P. J., & Bauer, D. J. (2011). *Annual Review of Psychology*, 62, 583-619.
  [doi:10.1146/annurev.psych.093008.100356](https://doi.org/10.1146/annurev.psych.093008.100356)
- Gromakovskis, V., & Gutmanis, M. G. (2025). *Journal of Pain Research*, 18, 6723-6743.
  [doi:10.2147/JPR.S564395](https://doi.org/10.2147/JPR.S564395)
- Eccleston, C., & Crombez, G. (1999). *Psychological Bulletin*, 125(3), 356-366.
  [doi:10.1037/0033-2909.125.3.356](https://doi.org/10.1037/0033-2909.125.3.356)
- Van Damme, S., Legrain, V., Vogt, J., & Crombez, G. (2010). *Neuroscience and Biobehavioral
  Reviews*, 34(2), 204-213. [doi:10.1016/j.neubiorev.2009.01.005](https://doi.org/10.1016/j.neubiorev.2009.01.005)
- Viane, I., Crombez, G., Eccleston, C., Devulder, J., & De Corte, W. (2004). *Pain*, 112(3),
  282-288. [doi:10.1016/j.pain.2004.09.008](https://doi.org/10.1016/j.pain.2004.09.008)
