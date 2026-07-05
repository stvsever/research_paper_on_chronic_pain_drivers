# Stage 04.1 - Per-person stationarity and item distribution checks.
#
# Fully individual VAR / graphicalVAR models assume weak stationarity of each person's
# series. This stage tests, for every person and every core node, a linear-trend regression
# and a KPSS stationarity test, and summarizes the share of series flagged. It also reports
# the skewness and kurtosis of the momentary items. The results justify the primary analysis
# (person-standardized lag-1 models) and motivate the detrended sensitivity model in stage 10.

suppressPackageStartupMessages({
  this <- normalizePath(sub("--file=", "",
    grep("--file=", commandArgs(FALSE), value = TRUE)[1]), mustWork = FALSE)
})
lib <- file.path(dirname(this), "..", "..", "..", "lib")
source(file.path(lib, "common.R"))
need(c("tseries"))

d <- read_ema()
nodes <- CORE_NODES
labels <- setNames(c("Pain", "Attention", "Fear", "Engagement"), nodes)

per_person <- list()
for (p in unique(d$pid)) {
  dp <- d[d$pid == p, ]
  for (v in nodes) {
    y <- dp[[v]]
    y <- y[!is.na(y)]
    if (length(y) < 20 || stats::sd(y) == 0) next
    tt <- seq_along(y)
    lm_p <- tryCatch(summary(lm(y ~ tt))$coefficients[2, 4], error = function(e) NA)
    kpss_p <- tryCatch(suppressWarnings(tseries::kpss.test(y)$p.value),
                       error = function(e) NA)
    per_person[[length(per_person) + 1]] <- data.frame(
      pid = p, variable = v, n = length(y),
      trend_p = lm_p, kpss_p = kpss_p)
  }
}
pp <- do.call(rbind, per_person)
write_result(pp, "04_stationarity_perperson.csv")

# Summary: share of series with a significant linear trend and share flagged non-stationary
# by KPSS (KPSS null is stationarity, so p < .05 flags non-stationarity).
summ <- do.call(rbind, lapply(nodes, function(v) {
  s <- pp[pp$variable == v, ]
  data.frame(variable = v,
             prop_linear_trend = round(mean(s$trend_p < 0.05, na.rm = TRUE), 3),
             prop_kpss_nonstationary = round(mean(s$kpss_p < 0.05, na.rm = TRUE), 3))
}))
write_result(summ, "04_stationarity_summary.csv")

# Item distribution shape (skewness / kurtosis) for the core nodes.
skew <- function(x) { x <- x[!is.na(x)]; m <- mean(x); mean((x - m)^3) / (mean((x - m)^2)^1.5) }
kurt <- function(x) { x <- x[!is.na(x)]; m <- mean(x); mean((x - m)^4) / (mean((x - m)^2)^2) - 3 }
dist <- do.call(rbind, lapply(nodes, function(v) {
  data.frame(measure = labels[[v]],
             skewness = round(skew(d[[v]]), 3),
             kurtosis = round(kurt(d[[v]]), 3))
}))
write_result(dist, "04_item_distribution.csv")

cat("\n=== stationarity summary ===\n"); print(summ, row.names = FALSE)
