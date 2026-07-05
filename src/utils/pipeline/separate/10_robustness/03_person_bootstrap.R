# Stage 10.3 - Person-level cluster bootstrap of the pooled temporal network.
#
# Participants are resampled with replacement (persons are the sampling unit, so each person's
# whole series is kept intact) and the pooled mlVAR is refit on each resample. Percentile 95%
# intervals and sign consistency are reported for every temporal edge. The number of resamples
# is a command-line argument (default 200) to keep the run tractable.

args <- commandArgs(trailingOnly = TRUE)
B <- if (length(args) >= 1) as.integer(args[1]) else 200L

this <- normalizePath(sub("--file=", "",
  grep("--file=", commandArgs(FALSE), value = TRUE)[1]), mustWork = FALSE)
lib <- file.path(dirname(this), "..", "..", "..", "lib")
source(file.path(lib, "common.R"))
source(file.path(lib, "mlvar_helpers.R"))

d <- read_ema()
ids <- unique(d$pid)
ref <- utils::read.csv(file.path(DIR_NETWORKS, "05_mlvar_core_temporal_edges.csv"))
ref$edge <- paste0(ref$from, "__to__", ref$to)

set.seed(20260703)
boot_long <- NULL
for (b in seq_len(B)) {
  samp <- sample(ids, length(ids), replace = TRUE)
  db <- do.call(rbind, lapply(seq_along(samp), function(k) {
    x <- d[d$pid == samp[k], ]
    x$pid <- paste0("b", k)   # unique relabel so resampled copies are distinct clusters
    x
  }))
  m <- tryCatch(fit_mlvar(db), error = function(e) NULL)
  if (is.null(m)) next
  te <- mlvar_temporal_edges(m)[, c("edge", "weight")]
  te$b <- b
  boot_long <- rbind(boot_long, te)
}
write_result(boot_long, "robust_bootstrap_edges_long.csv", DIR_NETWORKS)

summ <- do.call(rbind, lapply(unique(boot_long$edge), function(e) {
  w <- boot_long$weight[boot_long$edge == e]
  w0 <- ref$weight[ref$edge == e]
  data.frame(edge = e,
             ci_lo = stats::quantile(w, 0.025, names = FALSE),
             ci_hi = stats::quantile(w, 0.975, names = FALSE),
             prop_sign_consistent = mean(sign(w) == sign(w0)))
}))
summ <- merge(ref[, c("edge", "from", "to", "weight")], summ, by = "edge")
write_result(summ, "robust_bootstrap_summary.csv", DIR_NETWORKS)

cross <- summ[summ$from != summ$to, ]
excl0 <- cross[(cross$ci_lo > 0 & cross$ci_hi > 0) | (cross$ci_lo < 0 & cross$ci_hi < 0), ]
cat(sprintf("[bootstrap] B=%d; cross-lagged edges whose 95%% CI excludes 0: %d\n",
            B, nrow(excl0)))
print(excl0[, c("from", "to", "weight", "ci_lo", "ci_hi")], row.names = FALSE)
