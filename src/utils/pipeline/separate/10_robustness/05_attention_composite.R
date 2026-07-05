# Stage 10.5 - Attention measurement sensitivity (single item vs two-item composite).
#
# The primary attention node is the single item "I pay attention to my pain" (ATTEND). The
# diary also asked "I can ignore the pain now", reverse keyed. This refit replaces the
# attention node with the two-item composite (ATTEND2) and compares the temporal network, to
# show that the attention-pain results do not depend on the single-item operationalization.

this <- normalizePath(sub("--file=", "",
  grep("--file=", commandArgs(FALSE), value = TRUE)[1]), mustWork = FALSE)
lib <- file.path(dirname(this), "..", "..", "..", "lib")
source(file.path(lib, "common.R"))
source(file.path(lib, "mlvar_helpers.R"))

d <- read_ema()
d$ATTEND <- d$ATTEND2   # swap in the two-item composite

set.seed(20260703)
m <- fit_mlvar(d)
te <- mlvar_temporal_edges(m)
write_result(te, "robust_attention_composite_temporal_edges.csv", DIR_NETWORKS)

ref <- utils::read.csv(file.path(DIR_NETWORKS, "05_mlvar_core_temporal_edges.csv"))
ref$edge <- paste0(ref$from, "__to__", ref$to)
cmp <- compare_edges(ref, te, "attcomposite")
write_result(cmp, "robust_attention_composite_compare.csv", DIR_NETWORKS)
cat(sprintf("[attention-composite] r with primary = %.3f, max |diff| = %.3f, sign flips = %d\n",
            attr(cmp, "r"), attr(cmp, "max_abs_diff"), attr(cmp, "n_sign_flip")))
