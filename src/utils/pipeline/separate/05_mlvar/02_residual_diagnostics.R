# Stage 05.2 - Residual diagnostics for the temporal model.
#
# For each core node, a within-person lag-1 model (person-standardized outcome regressed on
# the lag-1 person-standardized nodes, within day) is fitted and its residuals are examined:
# residual skewness/kurtosis, the residual-fitted association, and the mean within-person
# lag-1 residual autocorrelation. Near-zero residual autocorrelation indicates that the lag-1
# structure captured the short-range dependence. Residuals feed the diagnostics figure.

suppressPackageStartupMessages({
  this <- normalizePath(sub("--file=", "",
    grep("--file=", commandArgs(FALSE), value = TRUE)[1]), mustWork = FALSE)
})
lib <- file.path(dirname(this), "..", "..", "..", "lib")
source(file.path(lib, "common.R"))

d <- read_ema()
nodes <- CORE_NODES
labels <- setNames(CORE_LABELS, nodes)

# person-standardize
for (v in nodes) {
  d[[v]] <- ave(d[[v]], d$pid, FUN = function(x) {
    s <- stats::sd(x, na.rm = TRUE); if (is.na(s) || s == 0) s <- 1
    (x - mean(x, na.rm = TRUE)) / s
  })
}

# build within-day lag-1 predictors
d <- d[order(d$pid, d$day, d$beep), ]
lagcols <- paste0(nodes, "_lag")
for (v in nodes) {
  d[[paste0(v, "_lag")]] <- ave(seq_len(nrow(d)), paste(d$pid, d$day), FUN = function(idx) {
    x <- d[[v]][idx]; c(NA, x[-length(x)])
  })
}

resid_long <- list()
diag_rows <- list()
skew <- function(x){x<-x[!is.na(x)];m<-mean(x);mean((x-m)^3)/(mean((x-m)^2)^1.5)}
kurt <- function(x){x<-x[!is.na(x)];m<-mean(x);mean((x-m)^4)/(mean((x-m)^2)^2)-3}

for (v in nodes) {
  f <- as.formula(paste0(v, " ~ ", paste(lagcols, collapse = " + ")))
  dd <- d[stats::complete.cases(d[, c(v, lagcols, "pid", "day", "beep")]), ]
  fit <- lm(f, data = dd)
  dd$resid <- resid(fit)
  dd$fitted <- fitted(fit)
  # within-person lag-1 residual autocorrelation
  acs <- tapply(seq_len(nrow(dd)), dd$pid, function(idx) {
    r <- dd$resid[idx]
    if (length(r) < 5) return(NA)
    stats::cor(r[-1], r[-length(r)], use = "complete.obs")
  })
  diag_rows[[v]] <- data.frame(
    node = labels[[v]],
    resid_skewness = round(skew(dd$resid), 3),
    resid_kurtosis = round(kurt(dd$resid), 3),
    mean_resid_acf1 = round(mean(acs, na.rm = TRUE), 3),
    resid_fitted_cor = round(stats::cor(dd$resid, dd$fitted), 3))
  resid_long[[v]] <- data.frame(node = labels[[v]], resid = dd$resid, fitted = dd$fitted)
}

diag <- do.call(rbind, diag_rows); rownames(diag) <- NULL
write_result(diag, "05_mlvar_residual_diagnostics.csv")
write_result(do.call(rbind, resid_long), "05_mlvar_residuals_long.csv", DIR_NETWORKS)

cat("\n=== residual diagnostics ===\n"); print(diag, row.names = FALSE)
