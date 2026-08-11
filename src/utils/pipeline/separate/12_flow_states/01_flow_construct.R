# Stage 12.1 - Flow: construct building, prevalence, and the condition-experience model.
#
# Four momentary activity appraisals in this diary map onto Csikszentmihalyi's flow model:
#   antecedent condition : CHALLENGE ("this activity is a personal challenge for me")
#                          EFFIC     ("I am good at this")
#   flow experience      : ENGAGE    ("I am absorbed in this activity")
#                          VALENCE   ("I like doing this")
# The four items are never summed. A sum conflates the antecedent condition with the
# outcome experience and is theoretically incoherent (Nakamura & Csikszentmihalyi, 2014).
# Instead the condition enters as two terms, balance and elevation, and the experience is
# the outcome. Balance alone would score a low-challenge, low-skill moment (apathy) as
# perfectly balanced, so both terms are required (Moneta & Csikszentmihalyi, 1996).
#
# This stage produces:
#   1. item-level descriptives and the within-person variance share,
#   2. the four-channel classification (Massimini & Carli, 1988) under four standardization
#      rules, with the momentary pain profile of each channel,
#   3. per-person flow prevalence including the persons who never reach the criterion,
#   4. the multilevel condition-to-experience model with random slopes,
#   5. a standardization sensitivity table.
#
# The standardization choice is the decision that drives interpretation. Within-person
# z-scoring makes every person's mean zero and therefore mechanically assigns every person
# above-average moments, including a person who was never in flow in any absolute sense.
# Person-mean centering (the within-between decomposition, Curran & Bauer, 2011) is the
# default here; absolute and within-z metrics are carried as sensitivity analyses.

this <- normalizePath(sub("--file=", "",
  grep("--file=", commandArgs(FALSE), value = TRUE)[1]), mustWork = FALSE)
lib <- file.path(dirname(this), "..", "..", "..", "lib")
source(file.path(lib, "common.R"))
need(c("lme4", "lmerTest"))

set.seed(20260703)

d <- read_ema()
d <- build_flow(d)

# Complete cases on all four flow items: the analytic frame for every flow model.
flow_cc <- stats::complete.cases(d[, FLOW_ITEMS])
f <- d[flow_cc, ]
cat(sprintf("\nflow analytic frame: %d moments, %d persons (median %.0f per person)\n",
            nrow(f), length(unique(f$pid)),
            stats::median(as.numeric(table(f$pid)))))

# --- 1. item descriptives and within-person variance share -------------------
item_desc <- do.call(rbind, lapply(c(FLOW_ITEMS, "FLOWEXP"), function(v) {
  x <- d[[v]]
  pm <- tapply(x, d$pid, mean, na.rm = TRUE)
  var_b <- stats::var(pm, na.rm = TRUE)
  var_t <- stats::var(x, na.rm = TRUE)
  data.frame(variable = v,
             role = if (v %in% FLOW_CONDITION_ITEMS) "Condition" else "Experience",
             n = sum(!is.na(x)),
             mean = round(mean(x, na.rm = TRUE), 2),
             sd = round(stats::sd(x, na.rm = TRUE), 2),
             icc_person = round(var_b / var_t, 3),
             within_share = round(1 - var_b / var_t, 3))
}))
write_result(item_desc, "12_flow_item_descriptives.csv")

# item intercorrelations, within and between person
cor_block <- function(vars, suffix, label) {
  M <- stats::cor(f[, paste0(vars, suffix)], use = "pairwise.complete.obs")
  out <- as.data.frame(round(M, 3))
  names(out) <- vars
  cbind(level = label, variable = vars, out)
}
write_result(rbind(cor_block(c(FLOW_ITEMS, "FLOWEXP"), "_w", "within"),
                   cor_block(c(FLOW_ITEMS, "FLOWEXP"), "_b", "between")),
             "12_flow_item_correlations.csv")

# --- 2. four-channel classification under four standardization rules ---------
# Rule labels follow the operationalization note: A = raw absolute thresholds,
# C = within-person z (median/zero split), D = person-mean centered (zero split).
rules <- list(
  list(id = "A_abs4", label = "Absolute, both items >= 4",
       ch = f$CHALLENGE, sk = f$EFFIC, cut = FLOW_ABS_LIBERAL),
  list(id = "A_abs5", label = "Absolute, both items >= 5",
       ch = f$CHALLENGE, sk = f$EFFIC, cut = FLOW_ABS_STRICT),
  list(id = "D_center", label = "Person-mean centered, above own mean",
       ch = f$CHALLENGE_w, sk = f$EFFIC_w, cut = 0),
  list(id = "C_withinz", label = "Within-person z, above own mean",
       ch = f$CHALLENGE_z, sk = f$EFFIC_z, cut = 0)
)

profile_vars <- c("PIJN", "PIJN_AFF", "ATTEND", "THREAT", "FLOWEXP",
                  "NEGAFF", "POSAFF", "ACTIEF")

chan_rows <- list()
prev_rows <- list()
for (r in rules) {
  ch <- flow_channel(r$ch, r$sk, r$cut)
  f[[paste0("chan_", r$id)]] <- ch
  # experience gate: a flow moment must also be experienced as absorbing and enjoyable.
  # Under the absolute rules the gate is the same absolute cut; under the relative rules
  # it is the person's own mean. The gate blocks the "balanced but disengaged" false
  # positive that an unguarded quadrant classification produces.
  gate <- switch(substr(r$id, 1, 1),
                 "A" = f$FLOWEXP >= r$cut,
                 "D" = f$FLOWEXP_w >= 0,
                 "C" = f$FLOWEXP_z >= 0)
  f[[paste0("flow_gated_", r$id)]] <- as.integer(ch == "Flow" & gate)

  for (lv in levels(ch)) {
    idx <- which(ch == lv)
    row <- data.frame(rule = r$id, rule_label = r$label, channel = lv,
                      n = length(idx),
                      share = round(length(idx) / sum(!is.na(ch)), 3))
    for (v in profile_vars) row[[paste0("mean_", tolower(v))]] <-
      round(mean(f[[v]][idx], na.rm = TRUE), 2)
    chan_rows[[length(chan_rows) + 1]] <- row
  }

  pp <- tapply(f[[paste0("flow_gated_", r$id)]], f$pid, mean, na.rm = TRUE)
  prev_rows[[length(prev_rows) + 1]] <- data.frame(
    rule = r$id, rule_label = r$label,
    moments_condition = round(mean(ch == "Flow", na.rm = TRUE), 3),
    moments_gated = round(mean(f[[paste0("flow_gated_", r$id)]], na.rm = TRUE), 3),
    person_median = round(stats::median(pp, na.rm = TRUE), 3),
    person_min = round(min(pp, na.rm = TRUE), 3),
    person_max = round(max(pp, na.rm = TRUE), 3),
    n_persons_zero = sum(pp == 0, na.rm = TRUE),
    n_persons = length(pp))
}
write_result(do.call(rbind, chan_rows), "12_flow_channel_profiles.csv")
write_result(do.call(rbind, prev_rows), "12_flow_prevalence_by_rule.csv")

# --- 3. per-person prevalence and mean flow experience -----------------------
per_person <- data.frame(pid = names(tapply(f$FLOWEXP, f$pid, mean, na.rm = TRUE)))
per_person$n_moments <- as.numeric(table(f$pid)[per_person$pid])
per_person$flow_prop_abs5 <- round(as.numeric(
  tapply(f$flow_gated_A_abs5, f$pid, mean, na.rm = TRUE)[per_person$pid]), 3)
per_person$flow_prop_abs4 <- round(as.numeric(
  tapply(f$flow_gated_A_abs4, f$pid, mean, na.rm = TRUE)[per_person$pid]), 3)
for (v in c("FLOWEXP", "CHALLENGE", "EFFIC", "ENGAGE", "VALENCE", "PIJN", "ATTEND")) {
  per_person[[paste0("mean_", tolower(v))]] <- round(as.numeric(
    tapply(f[[v]], f$pid, mean, na.rm = TRUE)[per_person$pid]), 3)
}
write_result(per_person, "12_flow_person_prevalence.csv")

# --- 4. condition -> experience, multilevel with random slopes ---------------
# Hybrid within-between specification: the within terms carry the momentary flow model,
# the between terms absorb stable person differences in challenge and skill so the within
# estimates are not contaminated by them (Curran & Bauer, 2011).
tidy_fixed <- function(m, model) {
  co <- summary(m)$coefficients
  data.frame(model = model, term = rownames(co),
             estimate = round(co[, "Estimate"], 3),
             SE = round(co[, "Std. Error"], 3),
             df = round(co[, "df"], 1),
             t = round(co[, "t value"], 2),
             p = signif(co[, "Pr(>|t|)"], 4),
             row.names = NULL)
}
tidy_random <- function(m, model) {
  vc <- as.data.frame(lme4::VarCorr(m))
  vc <- vc[is.na(vc$var2), ]
  data.frame(model = model, term = ifelse(is.na(vc$var1), "residual", vc$var1),
             random_SD = round(vc$sdcor, 3), row.names = NULL)
}

ctrl <- lme4::lmerControl(calc.derivs = FALSE, optimizer = "bobyqa")

m_cond <- lmerTest::lmer(
  FLOWEXP ~ balance_w + elevation_w + balance_b + elevation_b +
    (1 + balance_w + elevation_w | pid),
  data = f, REML = TRUE, control = ctrl)

# additive-plus-interaction alternative: does the challenge x skill product add anything
# beyond the balance/elevation parameterization?
m_int <- lmerTest::lmer(
  FLOWEXP ~ CHALLENGE_w * EFFIC_w + CHALLENGE_b + EFFIC_b +
    (1 + CHALLENGE_w + EFFIC_w | pid),
  data = f, REML = TRUE, control = ctrl)

# quadrant alternative: the categorical channel as predictor (flow as reference)
f$chan_D <- stats::relevel(f$chan_D_center, ref = "Apathy")
m_quad <- lmerTest::lmer(FLOWEXP ~ chan_D + (1 | pid), data = f, REML = TRUE, control = ctrl)

cond_fixed <- rbind(tidy_fixed(m_cond, "balance + elevation"),
                    tidy_fixed(m_int, "challenge x skill"),
                    tidy_fixed(m_quad, "quadrant (vs apathy)"))
write_result(cond_fixed, "12_flow_condition_experience_fixed.csv")
write_result(rbind(tidy_random(m_cond, "balance + elevation"),
                   tidy_random(m_int, "challenge x skill"),
                   tidy_random(m_quad, "quadrant (vs apathy)")),
             "12_flow_condition_experience_random.csv")

# model comparison on the same rows (ML refits)
ml <- function(m) stats::update(m, REML = FALSE)
cmp <- data.frame(
  model = c("balance + elevation", "challenge x skill", "quadrant (vs apathy)"),
  AIC = round(c(stats::AIC(ml(m_cond)), stats::AIC(ml(m_int)), stats::AIC(ml(m_quad))), 1),
  BIC = round(c(stats::BIC(ml(m_cond)), stats::BIC(ml(m_int)), stats::BIC(ml(m_quad))), 1),
  n_obs = c(nobs(m_cond), nobs(m_int), nobs(m_quad)))
write_result(cmp, "12_flow_condition_model_comparison.csv")

# --- 5. standardization sensitivity ------------------------------------------
# Refit the primary condition-experience model on each metric and report whether the two
# condition terms keep their sign, size, and significance.
sens_rows <- list()
metrics <- list(
  list(id = "D_center", label = "Person-mean centered (primary)",
       out = "FLOWEXP_w", bal = "balance_w", ele = "elevation_w"),
  list(id = "C_withinz", label = "Within-person z", out = "FLOWEXP_z",
       bal = "balance_z", ele = "elevation_z"),
  list(id = "A_raw", label = "Raw absolute scale", out = "FLOWEXP",
       bal = "balance_raw", ele = "elevation_raw")
)
for (mm in metrics) {
  fml <- as.formula(sprintf("%s ~ %s + %s + (1 + %s + %s | pid)",
                            mm$out, mm$bal, mm$ele, mm$bal, mm$ele))
  fit <- tryCatch(lmerTest::lmer(fml, data = f, REML = TRUE, control = ctrl),
                  error = function(e) NULL)
  if (is.null(fit)) next
  co <- summary(fit)$coefficients
  for (tm in c(mm$bal, mm$ele)) {
    sens_rows[[length(sens_rows) + 1]] <- data.frame(
      metric = mm$id, metric_label = mm$label,
      term = ifelse(grepl("^balance", tm), "Balance", "Elevation"),
      estimate = round(co[tm, "Estimate"], 3),
      SE = round(co[tm, "Std. Error"], 3),
      p = signif(co[tm, "Pr(>|t|)"], 4))
  }
}
write_result(do.call(rbind, sens_rows), "12_flow_standardization_sensitivity.csv")

# persist the analytic frame so the pain-model stage and the figure stage use exactly the
# same derived variables and channel assignments.
keep <- c("pid", "subject", "day", "beep", FLOW_ITEMS, "FLOWEXP",
          paste0(c(FLOW_ITEMS, "FLOWEXP", "PIJN", "ATTEND", "THREAT", "PIJN_AFF", "ACTIEF"), "_w"),
          paste0(c(FLOW_ITEMS, "FLOWEXP"), "_z"),
          "balance_w", "elevation_w", "balance_z", "elevation_z",
          "balance_b", "elevation_b", "balance_raw", "elevation_raw",
          "PIJN", "PIJN_AFF", "ATTEND", "THREAT", "NEGAFF", "POSAFF", "ACTIEF",
          grep("^chan_|^flow_gated_", names(f), value = TRUE))
write_result(f[, intersect(keep, names(f))], "12_flow_analytic_frame.csv", DIR_MODELS)

cat("\n=== flow condition -> experience (primary, person-mean centered) ===\n")
print(cond_fixed[cond_fixed$model == "balance + elevation" &
                   cond_fixed$term != "(Intercept)", ], row.names = FALSE)
cat("\n=== prevalence by standardization rule ===\n")
print(do.call(rbind, prev_rows), row.names = FALSE)
