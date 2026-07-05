# Stage 10.1 - Within-person detrended sensitivity of the pooled temporal network.
#
# A minority of individual series show a linear trend (stage 04). This refit removes a
# within-person linear time trend from each core node before estimating the pooled mlVAR, so
# that lag-1 effects cannot be inflated by shared drift. The detrended temporal network is
# compared with the primary one.

this <- normalizePath(sub("--file=", "",
  grep("--file=", commandArgs(FALSE), value = TRUE)[1]), mustWork = FALSE)
lib <- file.path(dirname(this), "..", "..", "..", "lib")
source(file.path(lib, "common.R"))
source(file.path(lib, "mlvar_helpers.R"))

d <- read_ema()
d <- d[order(d$pid, d$day, d$beep), ]

# within-person linear detrend
d$tindex <- ave(seq_len(nrow(d)), d$pid, FUN = seq_along)
for (v in CORE_NODES) {
  d[[v]] <- ave(seq_len(nrow(d)), d$pid, FUN = function(idx) {
    y <- d[[v]][idx]; tt <- d$tindex[idx]
    ok <- !is.na(y)
    if (sum(ok) < 5 || stats::sd(y[ok]) == 0) return(y)
    r <- rep(NA_real_, length(y))
    r[ok] <- resid(lm(y[ok] ~ tt[ok]))
    r
  })
}

set.seed(20260703)
m <- fit_mlvar(d)
det <- mlvar_temporal_edges(m)
write_result(det, "robust_detrended_temporal_edges.csv", DIR_NETWORKS)

ref <- utils::read.csv(file.path(DIR_NETWORKS, "05_mlvar_core_temporal_edges.csv"))
ref$edge <- paste0(ref$from, "__to__", ref$to)
cmp <- compare_edges(ref, det, "detrended")
write_result(cmp, "robust_detrended_compare.csv", DIR_NETWORKS)
cat(sprintf("[detrended] r with primary = %.3f, max |diff| = %.3f, sign flips = %d\n",
            attr(cmp, "r"), attr(cmp, "max_abs_diff"), attr(cmp, "n_sign_flip")))
