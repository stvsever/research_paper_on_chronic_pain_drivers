# Stage 10.6 - Stricter compliance threshold sensitivity.
#
# The primary pooled model uses all analytic participants. This refit keeps only participants
# with at least 70 completed prompts (a stricter compliance criterion) and compares the
# temporal network, to show that lower compliers do not drive the pooled results.

this <- normalizePath(sub("--file=", "",
  grep("--file=", commandArgs(FALSE), value = TRUE)[1]), mustWork = FALSE)
lib <- file.path(dirname(this), "..", "..", "..", "lib")
source(file.path(lib, "common.R"))
source(file.path(lib, "mlvar_helpers.R"))

THRESH <- 70L
d <- read_ema()
comp <- tapply(d$completed, d$pid, sum)
keep <- names(comp)[comp >= THRESH]
d <- d[d$pid %in% keep, ]
cat(sprintf("[compliance>=%d] %d of %d participants retained\n",
            THRESH, length(keep), length(comp)))

set.seed(20260703)
m <- fit_mlvar(d)
te <- mlvar_temporal_edges(m)
write_result(te, "robust_threshold70_temporal_edges.csv", DIR_NETWORKS)

ref <- utils::read.csv(file.path(DIR_NETWORKS, "05_mlvar_core_temporal_edges.csv"))
ref$edge <- paste0(ref$from, "__to__", ref$to)
cmp <- compare_edges(ref, te, "thr70")
write_result(cmp, "robust_threshold70_compare.csv", DIR_NETWORKS)
cat(sprintf("[compliance>=%d] r with primary = %.3f, max |diff| = %.3f, sign flips = %d\n",
            THRESH, attr(cmp, "r"), attr(cmp, "max_abs_diff"), attr(cmp, "n_sign_flip")))
