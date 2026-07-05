# Stage 07.2 - Per-person unregularized VAR (heterogeneity and individual inference).
#
# graphicalVAR gives sparse, regularized person networks. To quantify the SPREAD of the
# pain-driver couplings and whether individual estimates are precise, this stage also fits an
# unregularized within-person lag-1 model of the pain equation for each person:
#   Pain(t) ~ Pain(t-1) + Attention(t-1) + Fear(t-1) + Engagement(t-1)
# on person-standardized data, within day. It reports each person's driver-to-pain
# coefficients with 95% confidence intervals, and a wide table of all core lag-1 coefficients
# used to compute between-person heterogeneity (the random-effect-style SD of each edge).

this <- normalizePath(sub("--file=", "",
  grep("--file=", commandArgs(FALSE), value = TRUE)[1]), mustWork = FALSE)
lib <- file.path(dirname(this), "..", "..", "..", "lib")
source(file.path(lib, "common.R"))

d <- read_ema()
vars <- CORE_NODES

# person-standardize each node
for (v in vars) {
  d[[v]] <- ave(d[[v]], d$pid, FUN = function(x) {
    s <- stats::sd(x, na.rm = TRUE); if (is.na(s) || s == 0) s <- 1
    (x - mean(x, na.rm = TRUE)) / s
  })
}
# within-day lag-1 predictors
d <- d[order(d$pid, d$day, d$beep), ]
for (v in vars) {
  d[[paste0(v, "_lag")]] <- ave(seq_len(nrow(d)), paste(d$pid, d$day), FUN = function(idx) {
    x <- d[[v]][idx]; c(NA, x[-length(x)])
  })
}

lagcols <- paste0(vars, "_lag")
pain_rows <- list()
wide_rows <- list()
for (id in unique(d$pid)) {
  dp <- d[d$pid == id, ]
  ccols <- c(vars, lagcols)
  dp <- dp[stats::complete.cases(dp[, ccols]), ]
  if (nrow(dp) < 25) next

  # pain equation with CIs
  f <- as.formula(paste0("PIJN ~ ", paste(lagcols, collapse = " + ")))
  fit <- tryCatch(lm(f, data = dp), error = function(e) NULL)
  if (is.null(fit)) next
  ci <- tryCatch(stats::confint(fit), error = function(e) NULL)
  co <- summary(fit)$coefficients
  get <- function(term) if (term %in% rownames(co)) co[term, "Estimate"] else NA
  getlo <- function(term) if (!is.null(ci) && term %in% rownames(ci)) ci[term, 1] else NA
  gethi <- function(term) if (!is.null(ci) && term %in% rownames(ci)) ci[term, 2] else NA
  pain_rows[[id]] <- data.frame(
    pid = id, n = nrow(dp),
    threat_to_pain = get("THREAT_lag"), threat_lo = getlo("THREAT_lag"), threat_hi = gethi("THREAT_lag"),
    attend_to_pain = get("ATTEND_lag"), attend_lo = getlo("ATTEND_lag"), attend_hi = gethi("ATTEND_lag"),
    engage_to_pain = get("ENGAGE_lag"), engage_lo = getlo("ENGAGE_lag"), engage_hi = gethi("ENGAGE_lag"),
    pain_autoreg = get("PIJN_lag"))

  # full set of lag-1 coefficients (each outcome ~ all lags) for the heterogeneity network
  wr <- list(pid = id)
  for (out_v in vars) {
    fo <- as.formula(paste0(out_v, " ~ ", paste(lagcols, collapse = " + ")))
    fit2 <- tryCatch(lm(fo, data = dp), error = function(e) NULL)
    if (is.null(fit2)) next
    cf <- coef(fit2)
    for (pr in vars) {
      wr[[paste0(pr, "__to__", out_v)]] <- unname(cf[paste0(pr, "_lag")])
    }
  }
  wide_rows[[id]] <- as.data.frame(wr, stringsAsFactors = FALSE)
}

pain_df <- do.call(rbind, pain_rows)
wide_df <- do.call(rbind, wide_rows)
write_result(pain_df, "07_perperson_pain_equation.csv", DIR_NETWORKS)
write_result(wide_df, "07_perperson_var_ols_wide.csv", DIR_NETWORKS)

# between-person heterogeneity: SD of each directed lag-1 edge across persons
edge_cols <- setdiff(names(wide_df), "pid")
het <- data.frame(edge = edge_cols,
                  mean = sapply(wide_df[edge_cols], mean, na.rm = TRUE),
                  sd = sapply(wide_df[edge_cols], stats::sd, na.rm = TRUE))
het$from <- sub("__to__.*", "", het$edge)
het$to <- sub(".*__to__", "", het$edge)
write_result(het, "07_perperson_edge_heterogeneity.csv", DIR_NETWORKS)

# individual inference on the three pain-driver couplings
sig_frac <- function(lo, hi) mean((lo > 0 & hi > 0) | (lo < 0 & hi < 0), na.rm = TRUE)
cat("\n=== per-person pain-driver couplings ===\n")
for (e in c("threat", "attend", "engage")) {
  v <- pain_df[[paste0(e, "_to_pain")]]
  lo <- pain_df[[paste0(e, "_lo")]]; hi <- pain_df[[paste0(e, "_hi")]]
  cat(sprintf("%-8s to pain: mean %+.3f, range [%+.2f, %+.2f], %d/%d individually significant\n",
              e, mean(v, na.rm = TRUE), min(v, na.rm = TRUE), max(v, na.rm = TRUE),
              sum((lo > 0 & hi > 0) | (lo < 0 & hi < 0), na.rm = TRUE), sum(!is.na(v))))
}
