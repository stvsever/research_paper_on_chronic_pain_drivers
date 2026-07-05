# Stage 10.2 - Leave-one-participant-out stability of the pooled cross-lagged edges.
#
# The pooled benchmark network is re-estimated with each participant removed in turn. For
# each cross-lagged (non-autoregressive) edge, the range across refits and the proportion of
# refits that keep the primary sign are reported. Stable signs across all refits indicate that
# no single participant drives a cross-lagged effect.

this <- normalizePath(sub("--file=", "",
  grep("--file=", commandArgs(FALSE), value = TRUE)[1]), mustWork = FALSE)
lib <- file.path(dirname(this), "..", "..", "..", "lib")
source(file.path(lib, "common.R"))
source(file.path(lib, "mlvar_helpers.R"))

d <- read_ema()
ids <- unique(d$pid)

ref <- utils::read.csv(file.path(DIR_NETWORKS, "05_mlvar_core_temporal_edges.csv"))
ref$edge <- paste0(ref$from, "__to__", ref$to)

acc <- NULL
for (i in seq_along(ids)) {
  di <- d[d$pid != ids[i], ]
  m <- tryCatch(fit_mlvar(di), error = function(e) NULL)
  if (is.null(m)) next
  te <- mlvar_temporal_edges(m)[, c("edge", "weight")]
  names(te)[2] <- paste0("w_", i)
  acc <- if (is.null(acc)) te else merge(acc, te, by = "edge")
}

wmat <- as.matrix(acc[, -1])
loo <- data.frame(edge = acc$edge,
                  mean = rowMeans(wmat),
                  min = apply(wmat, 1, min),
                  max = apply(wmat, 1, max))
loo <- merge(ref[, c("edge", "from", "to", "weight")], loo, by = "edge")
loo$prop_sign_consistent <- mapply(function(k) {
  w0 <- loo$weight[k]; wr <- wmat[which(acc$edge == loo$edge[k]), ]
  mean(sign(wr) == sign(w0))
}, seq_len(nrow(loo)))
write_result(loo, "robust_loo_summary.csv", DIR_NETWORKS)

cross <- loo[loo$from != loo$to, ]
cat(sprintf("[LOO] %d refits; cross-lagged edges with 100%% sign consistency: %d / %d\n",
            ncol(wmat), sum(cross$prop_sign_consistent == 1), nrow(cross)))
