# Stage 09.2 - Cross-level moderation of the within-person couplings (RQ2, part 2).
#
# The earlier plan correlated noisy two-step per-person coefficients with baseline traits, an
# underpowered approach. This stage instead tests the individual-difference question directly
# and with full power: a single multilevel model per coupling in which a baseline trait account
# (between persons) moderates a within-person lag-1 coupling (a random slope). This is the
# direct test of whether the threat value of pain shapes how strongly pain-related states relate
# to pain within a person.
#
# Pre-specified couplings (theory-driven, not a scan), grounded in the interruptive-function
# model of pain (Eccleston & Crombez, 1999):
#   Pain(t)       ~ Attention(t-1)   x trait   (threat-amplified attentional capture)
#   Pain(t)       ~ Threat(t-1)      x trait
#   Attention(t)  ~ Pain(t-1)        x trait   (interruptive function of pain)
#   Attention(t)  ~ Engagement(t-1)  x trait   (goal engagement as distraction)
#   Engagement(t) ~ Pain(t-1)        x trait   (interruption of goal pursuit)
# Each coupling is moderated in turn by the threat, biomedical, and personality accounts.

this <- normalizePath(sub("--file=", "",
  grep("--file=", commandArgs(FALSE), value = TRUE)[1]), mustWork = FALSE)
lib <- file.path(dirname(this), "..", "..", "..", "lib")
source(file.path(lib, "common.R"))
need(c("lme4", "lmerTest"))

d <- read_ema()
vars <- CORE_NODES

# person-standardize each node, then build within-day lag-1 predictors
for (v in vars) {
  d[[v]] <- ave(d[[v]], d$pid, FUN = function(x) {
    s <- stats::sd(x, na.rm = TRUE); if (is.na(s) || s == 0) s <- 1
    (x - mean(x, na.rm = TRUE)) / s
  })
}
d <- d[order(d$pid, d$day, d$beep), ]
for (v in vars) {
  d[[paste0(v, "_lag")]] <- ave(seq_len(nrow(d)), paste(d$pid, d$day), FUN = function(idx) {
    x <- d[[v]][idx]; c(NA, x[-length(x)])
  })
}

# merge z-scored baseline accounts (between persons)
prof <- utils::read.csv(file.path(DIR_TABLES, "08_trait_profiles.csv"))
zc <- function(x) (x - mean(x, na.rm = TRUE)) / stats::sd(x, na.rm = TRUE)
prof$Threat <- zc(prof$threat_account)
prof$Biomedical <- zc(prof$biomedical_account)
prof$Personality <- zc(prof$personality_account)
d <- merge(d, prof[, c("pid", "Threat", "Biomedical", "Personality")], by = "pid",
           all.x = TRUE)

lagcols <- paste0(vars, "_lag")
couplings <- list(
  c(out = "PIJN", pred = "ATTEND", label = "Attention -> Pain"),
  c(out = "PIJN", pred = "THREAT", label = "Threat -> Pain"),
  c(out = "ATTEND", pred = "PIJN", label = "Pain -> Attention"),
  c(out = "ATTEND", pred = "ENGAGE", label = "Engagement -> Attention"),
  c(out = "ENGAGE", pred = "PIJN", label = "Pain -> Engagement")
)
accounts <- c("Threat", "Biomedical", "Personality")

rows <- list()
for (cp in couplings) {
  out <- cp[["out"]]; pred <- cp[["pred"]]; lab <- cp[["label"]]
  focal <- paste0(pred, "_lag")
  others <- setdiff(lagcols, focal)
  for (acc in accounts) {
    # y ~ focal*acc + other lags + random intercept and random focal slope
    fml <- as.formula(sprintf(
      "%s ~ %s * %s + %s + (1 + %s | pid)",
      out, focal, acc, paste(others, collapse = " + "), focal))
    dd <- d[stats::complete.cases(d[, c(out, lagcols, acc)]), ]
    m <- tryCatch(
      lmerTest::lmer(fml, data = dd, REML = FALSE,
                     control = lme4::lmerControl(optimizer = "bobyqa",
                                                 calc.derivs = FALSE)),
      error = function(e) NULL)
    if (is.null(m)) next
    co <- summary(m)$coefficients
    ix <- paste0(focal, ":", acc)
    main_row <- if (focal %in% rownames(co)) co[focal, ] else rep(NA, 5)
    ix_row <- if (ix %in% rownames(co)) co[ix, ] else rep(NA, 5)
    rows[[length(rows) + 1]] <- data.frame(
      coupling = lab, moderator = acc,
      within_b = round(main_row[["Estimate"]], 3),
      within_p = round(main_row[["Pr(>|t|)"]], 4),
      interaction_b = round(ix_row[["Estimate"]], 3),
      interaction_SE = round(ix_row[["Std. Error"]], 3),
      interaction_p = round(ix_row[["Pr(>|t|)"]], 4),
      n_obs = nrow(dd), n_pers = length(unique(dd$pid)))
  }
}
res <- do.call(rbind, rows)
write_result(res, "09_moderation.csv")

cat("\n=== cross-level moderation of within-person couplings ===\n")
print(res[, c("coupling", "moderator", "within_b", "interaction_b", "interaction_p")],
      row.names = FALSE)
sig <- res[!is.na(res$interaction_p) & res$interaction_p < 0.05, ]
cat(sprintf("\nSignificant moderations (p<.05): %d of %d\n", nrow(sig), nrow(res)))
if (nrow(sig) > 0) print(sig[, c("coupling", "moderator", "interaction_b", "interaction_p")],
                         row.names = FALSE)
