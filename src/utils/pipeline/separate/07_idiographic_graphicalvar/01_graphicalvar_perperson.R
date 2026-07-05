# Stage 07 - Per-person graphicalVAR (PRIMARY idiographic networks).
#
# This is the primary analysis. For every eligible participant a fully SEPARATE regularized
# VAR network is fitted (graphicalVAR: LASSO-penalized temporal + contemporaneous networks
# selected by EBIC). Because the diaries reach roughly 100 momentary reports per person, these
# person-specific networks are defensible here, which is the methodological difference from
# the fibromyalgia companion study. The networks answer the individual-level question directly:
# within each individual, which momentary states drive subsequent pain, and how much do those
# person-specific dynamics differ across individuals?
#
# Outputs: per-person edge lists, a per-person summary with the pain-driver couplings, and a
# tally of how often each directed edge is selected across individuals.

this <- normalizePath(sub("--file=", "",
  grep("--file=", commandArgs(FALSE), value = TRUE)[1]), mustWork = FALSE)
lib <- file.path(dirname(this), "..", "..", "..", "lib")
source(file.path(lib, "common.R"))
need(c("graphicalVAR"))

d <- read_ema()
vars <- CORE_NODES
labels <- setNames(CORE_LABELS, vars)
MIN_OBS <- 30  # graphicalVAR requires at least this many complete beeps

d <- d[order(d$pid, d$day, d$beep), ]
ids <- unique(d$pid)

all_edges <- list()
summ <- list()
for (id in ids) {
  sub <- d[d$pid == id, c("day", "beep", vars)]
  n_cc <- sum(stats::complete.cases(sub[, vars]))
  base <- data.frame(pid = id, n_complete = n_cc, fitted = FALSE,
                     n_temporal_edges = NA, n_contemp_edges = NA, temporal_density = NA,
                     threat_to_pain = NA, attend_to_pain = NA, engage_to_pain = NA,
                     pain_autoreg = NA, pain_to_attend = NA, engage_to_attend = NA)
  if (n_cc < MIN_OBS) { summ[[id]] <- base; next }
  fit <- tryCatch(
    graphicalVAR::graphicalVAR(
      sub, vars = vars, beepvar = "beep", dayvar = "day",
      nLambda = 50, gamma = 0.25, scale = TRUE, verbose = FALSE),
    error = function(e) NULL)
  if (is.null(fit)) { summ[[id]] <- base; next }

  PDC <- fit$PDC; PCC <- fit$PCC
  rownames(PDC) <- colnames(PDC) <- vars
  rownames(PCC) <- colnames(PCC) <- vars

  for (i in vars) for (j in vars) {
    all_edges[[length(all_edges) + 1]] <- data.frame(
      pid = id, type = "temporal", from = i, to = j, weight = PDC[i, j])
  }
  for (i in vars) for (j in vars) if (i != j) {
    all_edges[[length(all_edges) + 1]] <- data.frame(
      pid = id, type = "contemporaneous", from = i, to = j, weight = PCC[i, j])
  }
  summ[[id]] <- data.frame(
    pid = id, n_complete = n_cc, fitted = TRUE,
    n_temporal_edges = sum(PDC != 0),
    n_contemp_edges = sum(PCC[upper.tri(PCC)] != 0),
    temporal_density = mean(PDC != 0),
    threat_to_pain = PDC["THREAT", "PIJN"],
    attend_to_pain = PDC["ATTEND", "PIJN"],
    engage_to_pain = PDC["ENGAGE", "PIJN"],
    pain_autoreg = PDC["PIJN", "PIJN"],
    pain_to_attend = PDC["PIJN", "ATTEND"],
    engage_to_attend = PDC["ENGAGE", "ATTEND"])
}

edges_df <- do.call(rbind, all_edges)
summ_df <- do.call(rbind, summ)
write_result(edges_df, "07_graphicalvar_individual_edges.csv", DIR_NETWORKS)
write_result(summ_df, "07_graphicalvar_individual_summary.csv", DIR_TABLES)

fitted <- summ_df[summ_df$fitted, ]
cat(sprintf("\n[graphicalVAR] fitted %d / %d persons (T >= %d complete)\n",
            nrow(fitted), nrow(summ_df), MIN_OBS))
cat(sprintf("[graphicalVAR] temporal edges per person: median %.0f (range %d-%d) of 16 possible\n",
            median(fitted$n_temporal_edges), min(fitted$n_temporal_edges),
            max(fitted$n_temporal_edges)))
for (e in c("threat_to_pain", "attend_to_pain", "engage_to_pain")) {
  v <- fitted[[e]]
  cat(sprintf("[graphicalVAR] nonzero %s: %d persons (%d positive, %d negative)\n",
              e, sum(v != 0), sum(v > 0), sum(v < 0)))
}

tmp <- edges_df[edges_df$type == "temporal", ]
tmp$selected <- tmp$weight != 0
freq <- aggregate(selected ~ from + to, data = tmp, FUN = function(x) mean(x))
freq$pct_selected <- round(100 * freq$selected, 1)
freq$selected <- NULL
write_result(freq[order(-freq$pct_selected), ],
             "07_graphicalvar_edge_selection_freq.csv", DIR_NETWORKS)
