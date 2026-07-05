# Stage 06 - S-GIMME (shared versus individual structure, data-driven subgrouping).
#
# GIMME estimates a unified model per person containing (a) a group-level structure recovered
# across persons, (b) data-driven subgroups (S-GIMME), and (c) individual-specific paths, for
# both contemporaneous and lag-1 (directed) relations. Unlike the fibromyalgia companion
# study, the series here reach roughly the length GIMME recommends (about 100 time points),
# so S-GIMME is used as a confirmatory idiographic estimator alongside the per-person
# graphicalVAR: does a second data-driven method recover the same pain-driver backbone, which
# paths are truly shared, and do interpretable subgroups emerge? Per-person complete-case
# series on the four core nodes are used (a person is included with >= 30 complete beeps).

this <- normalizePath(sub("--file=", "",
  grep("--file=", commandArgs(FALSE), value = TRUE)[1]), mustWork = FALSE)
lib <- file.path(dirname(this), "..", "..", "..", "lib")
source(file.path(lib, "common.R"))
need(c("gimme"))

d <- read_ema()
vars <- CORE_NODES
# gimme drops rows with any missing lag, so its usable T is below the raw complete-case count;
# require a comfortable margin above its hard minimum of 30.
MIN_OBS <- 40

d <- d[order(d$pid, d$day, d$beep), ]
ids <- unique(d$pid)

out_dir <- file.path(DIR_MODELS, "gimme_out")
if (dir.exists(out_dir)) unlink(out_dir, recursive = TRUE)
data_dir <- file.path(out_dir, "data")
dir.create(data_dir, recursive = TRUE, showWarnings = FALSE)

incl <- data.frame(pid = character(), n_complete = integer(), included = logical())
for (id in ids) {
  sub <- d[d$pid == id, vars]
  cc <- stats::complete.cases(sub)
  sub <- sub[cc, , drop = FALSE]
  n <- nrow(sub)
  # gimme cannot handle a constant (zero-variance) column: standardizing it yields all-NA.
  has_variance <- n > 0 && all(apply(sub, 2, function(x) stats::sd(x) > 0))
  ok <- n >= MIN_OBS && has_variance
  incl <- rbind(incl, data.frame(pid = id, n_complete = n, included = ok))
  if (ok) {
    m <- scale(as.matrix(sub))
    colnames(m) <- vars
    utils::write.csv(as.data.frame(m),
                     file.path(data_dir, paste0(id, ".csv")), row.names = FALSE)
  }
}
write_result(incl, "06_sgimme_inclusion.csv", DIR_TABLES)
cat(sprintf("[S-GIMME] %d / %d persons meet T>=%d\n",
            sum(incl$included), length(ids), MIN_OBS))

fit_dir <- file.path(out_dir, "fit")
set.seed(20260703)
# Data are already within-person standardized; do NOT pass standardize = TRUE, and do NOT
# wrap this call in tryCatch (gimme uses non-standard evaluation and both paths trigger a
# "promise already under evaluation" bug in this build). subgroup = TRUE requests the
# S-GIMME data-driven subgrouping (Walktrap community detection on the similarity matrix).
fit <- gimme::gimme(
  data = data_dir, out = fit_dir, sep = ",", header = TRUE,
  ar = TRUE, plot = FALSE, subgroup = TRUE,
  groupcutoff = 0.75, subcutoff = 0.50
)

if (!is.null(fit)) {
  saveRDS(fit, file.path(DIR_MODELS, "sgimme_fit.rds"))

  sf <- utils::read.csv(file.path(fit_dir, "summaryFit.csv"))
  memb <- sf[, intersect(c("file", "sub_membership", "status", "rmsea", "cfi", "srmr"),
                         names(sf))]
  names(memb)[names(memb) == "file"] <- "pid"
  names(memb)[names(memb) == "sub_membership"] <- "subgroup"
  write_result(memb, "06_sgimme_subgroup_membership.csv", DIR_TABLES)

  spc <- utils::read.csv(file.path(fit_dir, "summaryPathCounts.csv"))
  spc$path <- paste(spc$lhs, spc$op, spc$rhs)
  write_result(spc, "06_sgimme_summary_path_counts.csv", DIR_NETWORKS)

  ipe <- utils::read.csv(file.path(fit_dir, "indivPathEstimates.csv"))
  write_result(ipe, "06_sgimme_individual_path_estimates.csv", DIR_NETWORKS)

  n_sub <- length(unique(memb$subgroup))
  sizes <- as.data.frame(table(subgroup = memb$subgroup))
  modularity <- suppressWarnings(stats::na.omit(sf$modularity))
  cat(sprintf("\n[S-GIMME] %d persons fit; %d subgroups (modularity = %.3f)\n",
              nrow(memb), n_sub,
              ifelse(length(modularity) > 0, modularity[1], NA_real_)))
  cat("[S-GIMME] subgroup sizes:\n"); print(sizes)
  cat("\n[S-GIMME] cross-variable paths present in the most individuals:\n")
  cross <- spc[spc$count.group == 0, ]
  print(utils::head(cross[order(-cross$count.ind),
                          intersect(c("path", "count.ind", "count.subgroup1"), names(cross))], 8),
        row.names = FALSE)
} else {
  cat("[S-GIMME] model did not converge / errored; see message above.\n")
}
