# Codebook: Viane experience-sampling diary

This codebook maps the raw SPSS variables to the analytic node set used in the
idiographic network analysis. Item wording is taken from the final diary protocol
(`diary_items_PEAS.pdf`, the "Aangepaste PEAS-vragen"). All momentary and
morning/evening rating items use a seven-point scale (1 = niet / not at all,
7 = zeer / very much) unless noted. The public identifiable PDFs and Word
documents in this folder are kept locally only and are excluded from version
control; this codebook is the committed reference.

## Design

- Patients with chronic musculoskeletal pain.
- Baseline questionnaire battery, then a two-week diary.
- Momentary (signal-contingent) diary eight times per day (the "day" file).
- A short morning diary and a short evening diary each day.

## Momentary diary ("day" file, raw `diary_day.sav`)

Identifiers and time:

| Raw | Meaning |
| --- | --- |
| `SUBJECT` | participant number |
| `WEEK`, `DAG` | study week block and day within block |
| `UUR` | scheduled clock time of the prompt (string, e.g. "10:31") |

Current thought module (open item plus ratings):

| Raw | Item (translated) | Note |
| --- | --- | --- |
| `GEDACHTE` | "What am I thinking about?" | open text, not modelled |
| `GED_BEL` | "I find this thought important" | thought salience |
| `GED_AFF` | "I find this thought pleasant" | thought valence |
| `GED_PERS` | "This thought will not let go of me" | thought intrusiveness |

Affect module:

| Raw | Item (translated) | Valence |
| --- | --- | --- |
| `OPGEWEKT` | "I feel cheerful" | positive |
| `SOMBER` | "I feel gloomy" | negative |
| `ONTSPANN` | "I feel relaxed" | positive |
| `ANGSTIG` | "I feel anxious" | negative |
| `TEVREDEN` | "I feel satisfied" | positive |
| `MOE` | "I feel tired" | fatigue |
| `GEFRUSTR` | "I feel frustrated" | negative |

Pain-related characteristics:

| Raw | Item (translated) | Construct |
| --- | --- | --- |
| `PIJNINTE` | "I am in pain now" | pain intensity (sensory) |
| `PIJN_AFF` | "My pain hinders me" | pain interference (affective) |
| `CAT_HULP` | "I feel that my pain is becoming too much for me" | catastrophizing / helplessness |
| `VR_ANGST` | "I am afraid of the pain now" | pain-related fear |
| `AANDACH1` | "I pay attention to my pain" | attention to pain |
| `AANDACH2` | "I can ignore the pain now" | attention to pain (reverse keyed) |

Activity characteristics (rated for the concurrent activity):

| Raw | Item (translated) | Construct |
| --- | --- | --- |
| `ACTIV` | "What am I doing?" | open text, not modelled |
| `ACT_MOT` | "I like doing this" | motivation / valence |
| `ACT_SUC` | "I am good at this" | competence |
| `ACTIEF` | "I am physically active" | physical activation |
| `ACT_UITD` | "This activity is a personal challenge for me" | challenge |
| `ACT_AAND` | "I am absorbed in this activity" | activity engagement |
| `ACT_INSP` | "I find it important to complete this activity" | goal importance |

Context and other:

| Raw | Item (translated) | Coding |
| --- | --- | --- |
| `CONTEXT` | "Where am I?" | 1 home, 2 outside/underway, 3 work, 4 hospital, 5/6 other |
| `ALLEEN` | "I am alone" | 0/1 (with a small number of 2 codes treated as missing) |
| `CONT_WIE` | "If not, with whom?" | family, friends, colleagues, carers, other |
| `CONT_AFF` | "This social situation is pleasant" | 1 to 7 |
| `MEDICAT` | "I have taken pain medication since the last beep" | 0/1 |
| `STOORT` | "This beep disturbed me" | 1 to 7 |

## Analytic node set (derived variables in `ema_long.csv`)

The core four-node set follows the cognitive-affective model of the interruptive
function of pain (Eccleston and Crombez, 1999): momentary pain, the threat value that
governs its attentional capture, attention to pain, and the goal-directed activity that pain
interrupts.

| Node | Column | Built from |
| --- | --- | --- |
| Pain intensity | `PIJN` | `PIJNINTE` |
| Threat value | `THREAT` | mean of `FEAR` (`VR_ANGST`) and `CATAS` (`CAT_HULP`); the two appraisals the model groups as the threat value of pain (within-person r = .41, between-person r = .68) |
| Attention to pain | `ATTEND` | `AANDACH1` (primary); 2-item composite mean of `AANDACH1` and reverse-scored `AANDACH2` used in a sensitivity analysis (`ATTEND2`) |
| Goal engagement | `ENGAGE` | `ACT_AAND` ("I am absorbed in this activity") |
| Goal efficacy | `EFFIC` | `ACT_SUC` ("I am good at this"; extended-6 node) |
| Activity valence | `VALENCE` | `ACT_MOT` ("I like doing this"; extended-6 node) |

The two threat components (`FEAR`, `CATAS`) are retained separately for the
threat-decomposition sensitivity analysis. Further goal-directed activity
characteristics from the diary are retained for descriptives: `CHALLENGE`
(`ACT_UITD`), `IMPORTANCE` (`ACT_INSP`). Auxiliary momentary variables retained:
`PIJN_AFF` (pain interference), `POSAFF`/`NEGAFF` (mood composites), `ACTIEF`
(self-reported physical activation), and the context items.

## Morning diary (raw `diary_morning.sav`)

| Raw | Meaning |
| --- | --- |
| `uuropst` | time of getting up |
| `slaap` | "I slept well" (1 to 7) |
| `pijn` | "I am in pain now" (morning pain, 1 to 7) |
| `plan`, `wat_plan` | any plans for the day (yes/no) and open description |

Merged into the day file as day-level predictors `morn_sleep` and `morn_pain`.

## Evening diary (raw `diary_evening.sav`)

| Raw | Item (translated) | Analytic name |
| --- | --- | --- |
| `plan` | "Today I managed to carry out my planned activities" | `eve_goal_success` |
| `pijncont` | "Today I managed to keep my pain under control" | `eve_pain_control` |
| `pijnhind` | "Pain hindered me in carrying out my activities" | `eve_pain_interference` |
| `act_invl` | "My activities influenced my pain" | `eve_activity_on_pain` |
| `gewoon` | "I found this an ordinary day" | `eve_ordinary` |
| `tevred` | "Overall I am satisfied with this day" | `eve_satisfied` |
| `stem_inv` | "Filling in the diary influenced my mood" | `eve_reactivity` |

These daily dysfunction outcomes are used in stage 11 (daily dysfunction
dynamics), the analog of the pacing stage in the fibromyalgia companion study.

## Baseline questionnaires (raw `baseline_questionnaires.sav`)

Item blocks (all scored in stage 01): `mpi1..28` (Multidimensional Pain
Inventory), `pdi1..7` (Pain Disability Index), `pcs1..13` (Pain Catastrophizing
Scale), `hads1..14` (Hospital Anxiety and Depression Scale), `wdq1..30` (Worry
Domains Questionnaire), `pvaq1..16` (Pain Vigilance and Awareness
Questionnaire), `neo1..60` (NEO-FFI), `pccl1..42` (Pain Cognition List).
Demographics: `geslacht` (gender), `leeftijd` (age), `opleid` (education),
`duur` (pain duration in months), `diagnose`.

Baseline composites used in RQ2 (individual differences in the person-specific
pain-driver couplings):

- Threat-value account: PCS total (catastrophizing) and PVAQ total (pain
  vigilance).
- Biomedical account: MPI pain severity and pain duration.
- Personality account: NEO-FFI neuroticism (12 items, standard reverse keys).

Scoring conventions and reverse-keyed items are documented inline in
`src/utils/pipeline/separate/01_preprocessing/01_build_person_level.py`.
