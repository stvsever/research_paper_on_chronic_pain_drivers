# Stage 11 - Daily dysfunction dynamics (pain, its drivers, and evening functioning).
#
# The evening diary provides two daily functioning outcomes: goal success
# ("today I managed to carry out my planned activities") and pain interference ("pain hindered
# me in carrying out my activities"). This stage links the day's momentary experience to that
# evening outcome, within persons, with participant random intercepts (lme4):
#   eve outcome(day) ~ day-mean pain + attention + fear + engagement (person-centered)
# It quantifies whether days with more pain, attention, and fear, and less engagement, end in
# worse functioning, and it does so at the within-person level that the design supports.

this <- normalizePath(sub("--file=", "",
  grep("--file=", commandArgs(FALSE), value = TRUE)[1]), mustWork = FALSE)
lib <- file.path(dirname(this), "..", "..", "..", "lib")
source(file.path(lib, "common.R"))
need(c("lme4", "lmerTest"))

d <- read_ema()

# day-level aggregation of momentary experience and the evening outcomes
agg <- aggregate(cbind(PIJN, THREAT, ATTEND, ENGAGE,
                       eve_pain_interference, eve_goal_success) ~ pid + day,
                 data = d, FUN = function(x) mean(x, na.rm = TRUE), na.action = na.pass)

# person-center the day-level predictors (within-person deviations)
for (v in c("PIJN", "THREAT", "ATTEND", "ENGAGE")) {
  agg[[paste0(v, "_wc")]] <- ave(agg[[v]], agg$pid,
                                 FUN = function(x) x - mean(x, na.rm = TRUE))
}

fit_outcome <- function(outcome) {
  dd <- agg[!is.na(agg[[outcome]]), ]
  f <- as.formula(paste0(outcome,
        " ~ PIJN_wc + ATTEND_wc + THREAT_wc + ENGAGE_wc + (1 | pid)"))
  m <- lmerTest::lmer(f, data = dd, REML = FALSE,
                      control = lme4::lmerControl(calc.derivs = FALSE))
  co <- summary(m)$coefficients
  data.frame(outcome = outcome,
             term = rownames(co),
             estimate = round(co[, "Estimate"], 3),
             SE = round(co[, "Std. Error"], 3),
             p = round(co[, "Pr(>|t|)"], 4),
             n_day = nrow(dd),
             row.names = NULL)
}

res <- rbind(fit_outcome("eve_pain_interference"),
             fit_outcome("eve_goal_success"))
write_result(res, "11_daily_dysfunction_models.csv")

# descriptive within-person correlations of day pain with the evening outcomes
wc_cor <- function(a, b) {
  rs <- c()
  for (p in unique(agg$pid)) {
    g <- agg[agg$pid == p, ]
    if (sum(stats::complete.cases(g[, c(a, b)])) < 5) next
    x <- g[[a]] - mean(g[[a]], na.rm = TRUE); y <- g[[b]] - mean(g[[b]], na.rm = TRUE)
    if (stats::sd(x, na.rm = TRUE) == 0 || stats::sd(y, na.rm = TRUE) == 0) next
    rs <- c(rs, stats::cor(x, y, use = "complete.obs"))
  }
  mean(rs, na.rm = TRUE)
}
desc <- data.frame(
  pair = c("day pain -> interference", "day pain -> goal success",
           "day engagement -> goal success"),
  within_person_r = round(c(wc_cor("PIJN", "eve_pain_interference"),
                            wc_cor("PIJN", "eve_goal_success"),
                            wc_cor("ENGAGE", "eve_goal_success")), 3))
write_result(desc, "11_daily_dysfunction_descriptives.csv")

cat("\n=== daily dysfunction models (within-person, lag-0 day level) ===\n")
print(res[res$term != "(Intercept)", ], row.names = FALSE)
cat("\nwithin-person day-level correlations:\n"); print(desc, row.names = FALSE)
