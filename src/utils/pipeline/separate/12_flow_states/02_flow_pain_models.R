# Stage 12.2 - Flow and the momentary experience of pain.
#
# Flow is the theoretical mirror image of the interruptive function of pain. The
# interruptive-function model (Eccleston & Crombez, 1999) says pain captures attention away
# from goal pursuit; flow describes the state in which goal pursuit absorbs attention so
# completely that competing signals fail to intrude. The flow-induced-analgesia review of
# Gromakovskis and Gutmanis (2025) notes that this has never been tested in daily life.
#
# Three model families, all within-person:
#   1. contemporaneous : does the flow experience track lower pain, attention to pain,
#                        interference, and threat at the same beep, over and above the
#                        challenge-skill condition and physical activation?
#   2. lagged          : does flow at t-1 predict pain at t, and does pain at t-1 predict
#                        flow at t (the interruption direction)? Both are estimated so the
#                        section reports the bidirectional picture rather than one half.
#   3. idiographic     : the per-person distribution of the flow-pain association, which is
#                        the quantity the paper's idiographic thesis actually cares about.
#
# Lags are built within day, on person-standardized variables, exactly as in stage 07 so the
# coefficients are on the same metric as the per-person VAR estimates. Associations are read
# as within-person predictive relations, not causal effects.

this <- normalizePath(sub("--file=", "",
  grep("--file=", commandArgs(FALSE), value = TRUE)[1]), mustWork = FALSE)
lib <- file.path(dirname(this), "..", "..", "..", "lib")
source(file.path(lib, "common.R"))
need(c("lme4", "lmerTest"))

set.seed(20260703)
ctrl <- lme4::lmerControl(calc.derivs = FALSE, optimizer = "bobyqa")

d <- build_flow(read_ema())
f <- d[stats::complete.cases(d[, FLOW_ITEMS]), ]

tidy_fixed <- function(m, model, outcome) {
  co <- summary(m)$coefficients
  data.frame(model = model, outcome = outcome, term = rownames(co),
             estimate = round(co[, "Estimate"], 3),
             SE = round(co[, "Std. Error"], 3),
             df = round(co[, "df"], 1),
             t = round(co[, "t value"], 2),
             p = signif(co[, "Pr(>|t|)"], 4),
             n_obs = nobs(m), row.names = NULL)
}
random_sd <- function(m, term) {
  vc <- as.data.frame(lme4::VarCorr(m))
  v <- vc$sdcor[!is.na(vc$var1) & is.na(vc$var2) & vc$var1 == term]
  if (length(v)) round(v[1], 3) else NA_real_
}

# --- 1. contemporaneous models ------------------------------------------------
outcomes <- c("PIJN", "ATTEND", "PIJN_AFF", "THREAT")
con_rows <- list()
con_rand <- list()
for (o in outcomes) {
  # base: flow experience plus the challenge-skill condition terms
  f1 <- as.formula(sprintf("%s ~ FLOWEXP_w + balance_w + elevation_w + (1 + FLOWEXP_w | pid)", o))
  m1 <- lmerTest::lmer(f1, data = f, REML = TRUE, control = ctrl)
  con_rows[[length(con_rows) + 1]] <- tidy_fixed(m1, "base", o)
  # adjusted: physical activation added, because challenge co-occurs with being active and
  # activity independently raises pain in this population (within-person r = .57)
  f2 <- as.formula(sprintf(
    "%s ~ FLOWEXP_w + balance_w + elevation_w + ACTIEF_w + (1 + FLOWEXP_w | pid)", o))
  m2 <- lmerTest::lmer(f2, data = f, REML = TRUE, control = ctrl)
  con_rows[[length(con_rows) + 1]] <- tidy_fixed(m2, "activity-adjusted", o)
  con_rand[[length(con_rand) + 1]] <- data.frame(
    outcome = o,
    random_SD_flow_base = random_sd(m1, "FLOWEXP_w"),
    random_SD_flow_adj = random_sd(m2, "FLOWEXP_w"))
}
con <- do.call(rbind, con_rows)
write_result(con, "12_flow_pain_contemporaneous.csv")
write_result(do.call(rbind, con_rand), "12_flow_pain_random_slopes.csv")

# channel contrast: is the pain profile of a flow moment different from apathy?
f$chan <- stats::relevel(f$chan_apathy_ref <- flow_channel(f$CHALLENGE_w, f$EFFIC_w, 0),
                         ref = "Apathy")
chan_rows <- list()
for (o in outcomes) {
  m <- lmerTest::lmer(as.formula(sprintf("%s ~ chan + (1 | pid)", o)),
                      data = f, REML = TRUE, control = ctrl)
  chan_rows[[length(chan_rows) + 1]] <- tidy_fixed(m, "channel (vs apathy)", o)
}
write_result(do.call(rbind, chan_rows), "12_flow_channel_contrasts.csv")

# --- 2. lagged models ---------------------------------------------------------
# person-standardize, then build within-day lag-1 predictors (stage 07 convention)
lagvars <- c("FLOWEXP", "PIJN", "ATTEND", "PIJN_AFF", "THREAT", "CHALLENGE", "EFFIC")
z <- f
for (v in lagvars) z[[v]] <- within_z(z[[v]], z$pid)
z <- z[order(z$pid, z$day, z$beep), ]
for (v in lagvars) {
  z[[paste0(v, "_lag")]] <- ave(seq_len(nrow(z)), paste(z$pid, z$day), FUN = function(idx) {
    x <- z[[v]][idx]; c(NA, x[-length(x)])
  })
}

lag_rows <- list()
lag_rand <- list()
# forward: flow at t-1 -> outcome at t, controlling the outcome's own lag
for (o in c("PIJN", "ATTEND", "PIJN_AFF", "THREAT")) {
  fml <- as.formula(sprintf("%s ~ FLOWEXP_lag + %s_lag + (1 + FLOWEXP_lag | pid)", o, o))
  m <- lmerTest::lmer(fml, data = z, REML = TRUE, control = ctrl)
  lag_rows[[length(lag_rows) + 1]] <- tidy_fixed(m, "flow(t-1) -> outcome(t)", o)
  lag_rand[[length(lag_rand) + 1]] <- data.frame(
    direction = "flow(t-1) -> outcome(t)", outcome = o,
    random_SD = random_sd(m, "FLOWEXP_lag"))
}
# reverse: pain / attention / threat at t-1 -> flow at t (the interruption direction)
for (p in c("PIJN", "ATTEND", "THREAT")) {
  fml <- as.formula(sprintf("FLOWEXP ~ %s_lag + FLOWEXP_lag + (1 + %s_lag | pid)", p, p))
  m <- lmerTest::lmer(fml, data = z, REML = TRUE, control = ctrl)
  lag_rows[[length(lag_rows) + 1]] <- tidy_fixed(m, "predictor(t-1) -> flow(t)", p)
  lag_rand[[length(lag_rand) + 1]] <- data.frame(
    direction = "predictor(t-1) -> flow(t)", outcome = p,
    random_SD = random_sd(m, paste0(p, "_lag")))
}
write_result(do.call(rbind, lag_rows), "12_flow_pain_lagged.csv")
write_result(do.call(rbind, lag_rand), "12_flow_lagged_random_slopes.csv")

# --- 3. idiographic per-person associations -----------------------------------
per <- list()
for (id in unique(z$pid)) {
  g <- z[z$pid == id, ]
  gc <- g[stats::complete.cases(g[, c("FLOWEXP", "PIJN")]), ]
  if (nrow(gc) < MIN_IDIO_OBS) next
  r_con <- suppressWarnings(stats::cor(gc$FLOWEXP, gc$PIJN))

  # contemporaneous per-person OLS with a confidence interval
  fit <- stats::lm(PIJN ~ FLOWEXP, data = gc)
  ci <- stats::confint(fit)
  # lagged per-person OLS, controlling the pain autoregression
  gl <- g[stats::complete.cases(g[, c("PIJN", "FLOWEXP_lag", "PIJN_lag")]), ]
  b_lag <- NA_real_; lo_lag <- NA_real_; hi_lag <- NA_real_; p_lag <- NA_real_
  if (nrow(gl) >= 25) {
    fl <- stats::lm(PIJN ~ FLOWEXP_lag + PIJN_lag, data = gl)
    cl <- stats::confint(fl)
    b_lag <- stats::coef(fl)[["FLOWEXP_lag"]]
    lo_lag <- cl["FLOWEXP_lag", 1]; hi_lag <- cl["FLOWEXP_lag", 2]
    p_lag <- summary(fl)$coefficients["FLOWEXP_lag", 4]
  }
  per[[id]] <- data.frame(
    pid = id, n = nrow(gc),
    r_flow_pain = round(r_con, 3),
    b_contemp = round(stats::coef(fit)[["FLOWEXP"]], 3),
    lo_contemp = round(ci["FLOWEXP", 1], 3),
    hi_contemp = round(ci["FLOWEXP", 2], 3),
    p_contemp = signif(summary(fit)$coefficients["FLOWEXP", 4], 4),
    b_lagged = round(b_lag, 3), lo_lagged = round(lo_lag, 3),
    hi_lagged = round(hi_lag, 3), p_lagged = signif(p_lag, 4))
}
per <- do.call(rbind, per)
per <- per[order(per$b_contemp), ]
write_result(per, "12_flow_perperson_slopes.csv")

summ <- data.frame(
  quantity = c("contemporaneous r", "contemporaneous b", "lagged b"),
  n_persons = c(sum(!is.na(per$r_flow_pain)), sum(!is.na(per$b_contemp)),
                sum(!is.na(per$b_lagged))),
  median = round(c(stats::median(per$r_flow_pain, na.rm = TRUE),
                   stats::median(per$b_contemp, na.rm = TRUE),
                   stats::median(per$b_lagged, na.rm = TRUE)), 3),
  q25 = round(c(stats::quantile(per$r_flow_pain, .25, na.rm = TRUE),
                stats::quantile(per$b_contemp, .25, na.rm = TRUE),
                stats::quantile(per$b_lagged, .25, na.rm = TRUE)), 3),
  q75 = round(c(stats::quantile(per$r_flow_pain, .75, na.rm = TRUE),
                stats::quantile(per$b_contemp, .75, na.rm = TRUE),
                stats::quantile(per$b_lagged, .75, na.rm = TRUE)), 3),
  min = round(c(min(per$r_flow_pain, na.rm = TRUE), min(per$b_contemp, na.rm = TRUE),
                min(per$b_lagged, na.rm = TRUE)), 3),
  max = round(c(max(per$r_flow_pain, na.rm = TRUE), max(per$b_contemp, na.rm = TRUE),
                max(per$b_lagged, na.rm = TRUE)), 3),
  pct_negative = round(100 * c(mean(per$r_flow_pain < 0, na.rm = TRUE),
                               mean(per$b_contemp < 0, na.rm = TRUE),
                               mean(per$b_lagged < 0, na.rm = TRUE)), 1),
  n_sig_negative = c(NA,
                     sum(per$hi_contemp < 0, na.rm = TRUE),
                     sum(per$hi_lagged < 0, na.rm = TRUE)),
  n_sig_positive = c(NA,
                     sum(per$lo_contemp > 0, na.rm = TRUE),
                     sum(per$lo_lagged > 0, na.rm = TRUE)))
write_result(summ, "12_flow_perperson_summary.csv")

cat("\n=== contemporaneous flow -> momentary experience (activity-adjusted) ===\n")
print(con[con$model == "activity-adjusted" & con$term == "FLOWEXP_w",
          c("outcome", "estimate", "SE", "p")], row.names = FALSE)
cat("\n=== lagged models (focal predictor only) ===\n")
lg <- do.call(rbind, lag_rows)
focal <- ifelse(lg$model == "flow(t-1) -> outcome(t)", "FLOWEXP_lag",
                paste0(lg$outcome, "_lag"))
print(lg[lg$term == focal, c("model", "outcome", "term", "estimate", "SE", "p")],
      row.names = FALSE)
cat("\n=== per-person heterogeneity ===\n")
print(summ, row.names = FALSE)
