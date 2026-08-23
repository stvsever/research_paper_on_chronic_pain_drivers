# Stage 12.5 - Formal tests of the two structural assumptions of the flow construct.
#
# The flow construct makes two structural claims that the usual experience-sampling
# operationalization builds in rather than tests:
#
#   (i)  CONFIGURALITY. The challenge-skill condition acts through the *match* between the
#        two appraisals, not only through their levels. Operationally, balance
#        (-|C - S|) should carry variance in the flow experience over and above what
#        challenge and skill contribute additively.
#   (ii) COMPOSITE COHERENCE. The four appraisals form one construct, so a composite is a
#        fair summary of them. Operationally, splitting the composite into its constituents
#        should not improve fit and should not reveal constituents that pull in opposite
#        directions (VanderWeele, 2022).
#
# Both claims are testable by likelihood-ratio comparison of nested fixed-effect structures.
# The nesting is exact: FLOWEXP is (ENGAGE + VALENCE)/2, so a model with the composite is
# the constituent model under the constraint b_ENGAGE = b_VALENCE with the condition items
# excluded; and balance is a nonlinear function of challenge and skill, so it can be added
# to a model that already contains both as main effects.
#
# All nested comparisons use ML (REML = FALSE) and a random intercept only, so the
# comparison is about the fixed-effect structure and nothing else. Random-slope versions of
# the same models are reported elsewhere in stage 12 and give the same coefficients.

this <- normalizePath(sub("--file=", "",
  grep("--file=", commandArgs(FALSE), value = TRUE)[1]), mustWork = FALSE)
lib <- file.path(dirname(this), "..", "..", "..", "..", "lib")
source(file.path(lib, "common.R"))
need(c("lme4", "lmerTest"))

set.seed(20260703)
ctrl <- lme4::lmerControl(calc.derivs = FALSE, optimizer = "bobyqa")

d <- build_flow(read_ema())
f <- d[stats::complete.cases(d[, FLOW_ITEMS]), ]
f$chan <- flow_channel(f$CHALLENGE_w, f$EFFIC_w, 0)

ml <- function(fml, data) lme4::lmer(as.formula(fml), data = data, REML = FALSE, control = ctrl)

#' One row of a nested likelihood-ratio comparison.
lrt_row <- function(question, restricted, full, m0, m1) {
  a <- stats::anova(m0, m1)
  data.frame(
    question = question,
    restricted = restricted, full = full,
    df_restricted = a$npar[1], df_full = a$npar[2],
    AIC_restricted = round(a$AIC[1], 1), AIC_full = round(a$AIC[2], 1),
    delta_AIC = round(a$AIC[1] - a$AIC[2], 1),
    BIC_restricted = round(a$BIC[1], 1), BIC_full = round(a$BIC[2], 1),
    chisq = round(a$Chisq[2], 2), df = a$Df[2],
    p = signif(a$`Pr(>Chisq)`[2], 4), row.names = NULL)
}

tidy_fixed <- function(m, model, outcome) {
  m <- lmerTest::as_lmerModLmerTest(m)
  co <- summary(m)$coefficients
  data.frame(model = model, outcome = outcome, term = rownames(co),
             estimate = round(co[, "Estimate"], 3),
             SE = round(co[, "Std. Error"], 3),
             lo = round(co[, "Estimate"] - 1.96 * co[, "Std. Error"], 3),
             hi = round(co[, "Estimate"] + 1.96 * co[, "Std. Error"], 3),
             df = round(co[, "df"], 1),
             t = round(co[, "t value"], 2),
             p = signif(co[, "Pr(>|t|)"], 4),
             n_obs = nobs(m), row.names = NULL)
}

# =============================================================================
# 1. Configurality: does the match between challenge and skill add anything?
# =============================================================================
# Every test below asks the same question in a different functional form, and each keeps
# challenge and skill in the model in their own metric. That matters: a term built from
# |C - S| is only interpretable if a point on the challenge scale means the same as a point
# on the skill scale, whereas the additive, interaction, and response-surface tests do not
# need that assumption (Edwards & Parry, 1993; Edwards, 1994).
cond <- f[stats::complete.cases(f[, c("FLOWEXP", "CHALLENGE_w", "EFFIC_w",
                                      "balance_w", "elevation_w")]), ]
cond$discrepancy <- cond$CHALLENGE_w - cond$EFFIC_w
cond$overload <- pmax(cond$discrepancy, 0)   # one-sided kink at C = S, overload side

c_add   <- ml("FLOWEXP ~ CHALLENGE_w + EFFIC_w + (1 | pid)", cond)
c_bal   <- ml("FLOWEXP ~ CHALLENGE_w + EFFIC_w + balance_w + (1 | pid)", cond)
c_kink  <- ml("FLOWEXP ~ CHALLENGE_w + EFFIC_w + overload + (1 | pid)", cond)
c_inter <- ml("FLOWEXP ~ CHALLENGE_w * EFFIC_w + (1 | pid)", cond)
c_chan  <- ml("FLOWEXP ~ CHALLENGE_w + EFFIC_w + chan + (1 | pid)", cond)
c_surf  <- ml(paste("FLOWEXP ~ CHALLENGE_w + EFFIC_w + I(CHALLENGE_w^2) + I(EFFIC_w^2) +",
                    "CHALLENGE_w:EFFIC_w + (1 | pid)"), cond)
c_surf_bal <- ml(paste("FLOWEXP ~ CHALLENGE_w + EFFIC_w + I(CHALLENGE_w^2) + I(EFFIC_w^2) +",
                       "CHALLENGE_w:EFFIC_w + balance_w + (1 | pid)"), cond)
c_be    <- ml("FLOWEXP ~ balance_w + elevation_w + (1 | pid)", cond)
c_be_i  <- ml("FLOWEXP ~ balance_w * elevation_w + (1 | pid)", cond)

tests <- rbind(
  lrt_row("Does balance add to an additive challenge + skill model?",
          "challenge + skill", "challenge + skill + balance", c_add, c_bal),
  lrt_row("Does a one-sided kink at challenge = skill add (overload versus boredom)?",
          "challenge + skill", "challenge + skill + overload", c_add, c_kink),
  lrt_row("Does a multiplicative challenge x skill interaction add?",
          "challenge + skill", "challenge x skill", c_add, c_inter),
  lrt_row("Does a full second-order response surface add?",
          "challenge + skill", "quadratic surface", c_add, c_surf),
  lrt_row("Does the four-channel quadrant structure add?",
          "challenge + skill", "challenge + skill + channel", c_add, c_chan),
  lrt_row("Diagnostic: balance added to the quadratic surface",
          "quadratic surface", "quadratic surface + balance", c_surf, c_surf_bal),
  lrt_row("Diagnostic: balance x elevation inside the balance-elevation form",
          "balance + elevation", "balance x elevation", c_be, c_be_i))
write_result(tests, "12_flow_structural_tests.csv")

write_result(rbind(tidy_fixed(c_add, "challenge + skill", "FLOWEXP"),
                   tidy_fixed(c_bal, "challenge + skill + balance", "FLOWEXP"),
                   tidy_fixed(c_kink, "challenge + skill + overload", "FLOWEXP"),
                   tidy_fixed(c_inter, "challenge x skill", "FLOWEXP"),
                   tidy_fixed(c_surf, "quadratic response surface", "FLOWEXP"),
                   tidy_fixed(c_surf_bal, "quadratic surface + balance", "FLOWEXP"),
                   tidy_fixed(c_be_i, "balance x elevation", "FLOWEXP")),
             "12_flow_condition_nested_fixed.csv")

# Why the two diagnostic rows above are not evidence for configurality: balance is a near
# mirror of the squared discrepancy that the quadratic surface already contains, and the
# balance-elevation form drops the asymmetry between challenge and skill that the additive
# model estimates freely.
diag <- data.frame(
  quantity = c("cor(balance, -(C - S)^2)", "cor(balance, C^2)", "cor(balance, S^2)",
               "cor(balance, elevation)", "b challenge (additive)", "b skill (additive)"),
  value = round(c(
    stats::cor(cond$balance_w, -(cond$discrepancy)^2),
    stats::cor(cond$balance_w, cond$CHALLENGE_w^2),
    stats::cor(cond$balance_w, cond$EFFIC_w^2),
    stats::cor(cond$balance_w, cond$elevation_w),
    lme4::fixef(c_add)[["CHALLENGE_w"]], lme4::fixef(c_add)[["EFFIC_w"]]), 3))
write_result(diag, "12_flow_balance_diagnostics.csv")

# Simple slopes of balance at low, mean, and high elevation, to read the diagnostic
# interaction that the balance-elevation parameterization reports.
sd_elev <- stats::sd(cond$elevation_w, na.rm = TRUE)
m_int <- lmerTest::as_lmerModLmerTest(c_be_i)
V <- as.matrix(stats::vcov(m_int)); b <- lme4::fixef(c_be_i)
simple <- do.call(rbind, lapply(c(-1, 0, 1), function(k) {
  cvec <- c(0, 1, 0, k * sd_elev)   # intercept, balance, elevation, balance:elevation
  est <- sum(cvec * b); se <- sqrt(as.numeric(t(cvec) %*% V %*% cvec))
  data.frame(elevation = c("-1 SD", "person mean", "+1 SD")[k + 2],
             elevation_value = round(k * sd_elev, 3),
             estimate = round(est, 3), SE = round(se, 3),
             lo = round(est - 1.96 * se, 3), hi = round(est + 1.96 * se, 3),
             p = signif(2 * stats::pnorm(-abs(est / se)), 4), row.names = NULL)
}))
write_result(simple, "12_flow_balance_simple_slopes.csv")

# Non-nested comparison of the two parameterizations at equal degrees of freedom.
nonnested <- data.frame(
  model = c("balance + elevation", "challenge + skill (additive)"),
  npar = c(attr(logLik(c_be), "df"), attr(logLik(c_add), "df")),
  AIC = round(c(stats::AIC(c_be), stats::AIC(c_add)), 1),
  BIC = round(c(stats::BIC(c_be), stats::BIC(c_add)), 1),
  logLik = round(c(as.numeric(logLik(c_be)), as.numeric(logLik(c_add))), 1),
  n_obs = c(nobs(c_be), nobs(c_add)))
nonnested$delta_AIC <- round(nonnested$AIC - min(nonnested$AIC), 1)
write_result(nonnested, "12_flow_condition_parameterization.csv")

# =============================================================================
# 2. Composite coherence: does the composite lose information about pain?
# =============================================================================
outcomes <- c("PIJN", "PIJN_AFF", "ATTEND", "THREAT")
comp_rows <- list()
comp_fixed <- list()
for (o in outcomes) {
  keep <- stats::complete.cases(
    f[, c(o, "FLOWEXP_w", "ENGAGE_w", "VALENCE_w", "CHALLENGE_w", "EFFIC_w", "ACTIEF_w")])
  g <- f[keep, ]
  m_comp <- ml(sprintf("%s ~ FLOWEXP_w + ACTIEF_w + (1 | pid)", o), g)
  m_exp  <- ml(sprintf("%s ~ ENGAGE_w + VALENCE_w + ACTIEF_w + (1 | pid)", o), g)
  m_all  <- ml(sprintf("%s ~ ENGAGE_w + VALENCE_w + CHALLENGE_w + EFFIC_w + ACTIEF_w + (1 | pid)", o), g)
  r1 <- lrt_row("Does splitting the composite into absorption and enjoyment improve fit?",
                "flow composite", "absorption + enjoyment", m_comp, m_exp)
  r2 <- lrt_row("Do the condition items add over the experience constituents?",
                "absorption + enjoyment", "all four constituents", m_exp, m_all)
  r3 <- lrt_row("Do the four constituents improve on the composite?",
                "flow composite", "all four constituents", m_comp, m_all)
  comp_rows[[length(comp_rows) + 1]] <- cbind(outcome = o, rbind(r1, r2, r3))
  comp_fixed[[length(comp_fixed) + 1]] <- rbind(
    tidy_fixed(m_comp, "composite", o), tidy_fixed(m_all, "constituents", o))
}
write_result(do.call(rbind, comp_rows), "12_flow_composite_lrt.csv")
write_result(do.call(rbind, comp_fixed), "12_flow_composite_vs_constituents.csv")

write_result(tests, "12_flow_structural_tests.csv")

# =============================================================================
# 3. Channel contrasts with flow as the reference (the head-to-head comparison)
# =============================================================================
f$chan_flowref <- stats::relevel(f$chan, ref = "Flow")
chan_rows <- list()
for (o in outcomes) {
  m <- lmerTest::lmer(as.formula(sprintf("%s ~ chan_flowref + (1 | pid)", o)),
                      data = f, REML = TRUE, control = ctrl)
  co <- summary(m)$coefficients
  chan_rows[[length(chan_rows) + 1]] <- data.frame(
    outcome = o, term = rownames(co),
    estimate = round(co[, "Estimate"], 3), SE = round(co[, "Std. Error"], 3),
    lo = round(co[, "Estimate"] - 1.96 * co[, "Std. Error"], 3),
    hi = round(co[, "Estimate"] + 1.96 * co[, "Std. Error"], 3),
    p = signif(co[, "Pr(>|t|)"], 4), n_obs = nobs(m), row.names = NULL)
}
write_result(do.call(rbind, chan_rows), "12_flow_channel_contrasts_flowref.csv")

# =============================================================================
# 4. Person-specific condition slopes (balance and elevation)
# =============================================================================
# The fixed effect says balance does nothing on average. The random slopes say whether that
# average hides persons for whom matching does matter.
m_rs <- lme4::lmer(FLOWEXP ~ balance_w + elevation_w + balance_b + elevation_b +
                     (1 + balance_w + elevation_w | pid),
                   data = f, REML = TRUE, control = ctrl)
fe <- lme4::fixef(m_rs)
re <- lme4::ranef(m_rs)$pid
per_cond <- data.frame(
  pid = rownames(re),
  balance_slope = round(fe[["balance_w"]] + re[["balance_w"]], 4),
  elevation_slope = round(fe[["elevation_w"]] + re[["elevation_w"]], 4),
  row.names = NULL)
write_result(per_cond, "12_flow_perperson_condition_slopes.csv")

cat("[stage 12.5] structural tests complete\n")
