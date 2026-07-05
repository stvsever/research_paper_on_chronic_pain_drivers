# Shared mlVAR fitting helpers, sourced by the pooled benchmark model (stage 05) and the
# robustness battery (stage 10) so that every refit uses an identical specification.
#
# Role of mlVAR in this project. Unlike the fibromyalgia companion study, the diaries here
# reach roughly 100 momentary reports per person, so fully separate individual networks are
# the primary analysis (stage 07). mlVAR is used as the partial-pooling benchmark: it
# estimates a stable group-level network and quantifies between-person heterogeneity through
# random effects, which anchors the interpretation of the person-specific estimates.
#
# Specification rationale (fixed across the project):
#   - lags = 1 (lag-1 vector autoregression),
#   - dayvar + beepvar: lags are only built between adjacent beeps WITHIN a day (no lag is
#     constructed across the overnight gap),
#   - within-person standardization (scale = TRUE),
#   - orthogonal random effects (the stable choice for this n-persons / n-parameters regime;
#     Epskamp, Waldorp, Mottus, & Borsboom, 2018),
#   - estimator = "lmer".

suppressWarnings(suppressMessages(require(mlVAR)))

CORE_VARS <- c("PIJN", "THREAT", "ATTEND", "ENGAGE")

# Fit the project-standard mlVAR and return the model object.
# NOTE: the lmer estimator is deterministic, so no internal seeding is performed (an
# internal set.seed() would silently break the cluster bootstrap by resetting the RNG to a
# constant after every fit, making every resample identical).
fit_mlvar <- function(d, vars = CORE_VARS) {
  d <- d[, c("pid", "day", "beep", vars)]
  d$pid <- as.factor(d$pid)
  mlVAR::mlVAR(d, vars = vars, idvar = "pid", dayvar = "day", beepvar = "beep",
               lags = 1, temporal = "orthogonal", contemporaneous = "orthogonal",
               estimator = "lmer", scale = TRUE, verbose = FALSE)
}

# Tidy temporal edge list (from = predictor at t-1, to = outcome at t).
mlvar_temporal_edges <- function(m) {
  s <- summary(m)$temporal
  out <- s[, c("from", "to", "fixed", "SE", "P", "ran_SD")]
  names(out) <- c("from", "to", "weight", "SE", "P", "ran_SD")
  out$edge <- paste0(out$from, "__to__", out$to)
  out
}

# Compare two temporal edge lists; returns merged frame + summary stats.
compare_edges <- function(reference, alternative, label = "alt") {
  m <- merge(reference[, c("edge", "from", "to", "weight")],
             alternative[, c("edge", "weight")], by = "edge",
             suffixes = c("_ref", paste0("_", label)))
  wr <- m[["weight_ref"]]
  wa <- m[[paste0("weight_", label)]]
  m$abs_diff <- abs(wr - wa)
  attr(m, "r") <- stats::cor(wr, wa)
  attr(m, "max_abs_diff") <- max(m$abs_diff)
  attr(m, "n_sign_flip") <- sum(sign(wr) != sign(wa) &
                                  pmax(abs(wr), abs(wa)) > 0.05)
  m
}
