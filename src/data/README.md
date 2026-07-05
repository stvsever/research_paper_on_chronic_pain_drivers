# Data

This directory holds the inputs and processed outputs of the pipeline. Participant-level data
are private and are excluded from version control (see the root `.gitignore`).

## `raw/` (gitignored)

Copies of the required SPSS files, migrated from the legacy Outlook dump in `src/other/`:

| File | Content |
| --- | --- |
| `diary_day.sav` | Momentary diary (eight prompts per day for two weeks). Core EMA source. |
| `diary_morning.sav` | Morning diary (sleep, morning pain, plans). |
| `diary_evening.sav` | Evening diary (goal success, pain control, pain interference). |
| `baseline_between.sav` | Baseline questionnaire battery with integer subject IDs that match the diary, including the pre-scored subscales used for RQ2. |

The baseline source is the "between" file rather than the separately archived questionnaire
file, because the between file carries integer subject IDs that link to the diary, whereas the
questionnaire file uses non-linking string IDs.

## `processed/` (gitignored)

Analysis-ready files written by stage 01:

| File | Content |
| --- | --- |
| `ema_long.csv` | One row per completed momentary prompt, with the recoded analytic nodes, the within-day time structure, and the merged morning and evening day-level covariates. |
| `person_level.csv` | One row per baseline participant, with the scored trait measures and the analytic-sample and idiographic-eligibility flags. |
| `exclusion_log.csv` | Audit trail of any excluded participants. |

## Node definitions

The four core nodes are momentary pain (`PIJN`), attention to pain (`ATTEND`), pain-related
fear (`FEAR`), and activity engagement (`ENGAGE`). The extended model adds catastrophizing
(`CATAS`) and negative affect (`NEGAFF`). Item wording and the full mapping from raw SPSS
variables to analytic nodes are documented in
[`src/utils/study_materials/CODEBOOK.md`](../utils/study_materials/CODEBOOK.md).
