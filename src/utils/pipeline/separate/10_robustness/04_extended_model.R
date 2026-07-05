# Stage 10.4 - Extended six-node model (adds catastrophizing and negative affect).
#
# The core four-node network isolates pain and the three theory-central drivers. This model
# adds momentary catastrophizing (the second threat-value component) and negative affect, to
# check that the core temporal structure is not distorted once the broader affective-cognitive
# context is included. The six core coefficients are compared with the primary model.

this <- normalizePath(sub("--file=", "",
  grep("--file=", commandArgs(FALSE), value = TRUE)[1]), mustWork = FALSE)
lib <- file.path(dirname(this), "..", "..", "..", "lib")
source(file.path(lib, "common.R"))
source(file.path(lib, "mlvar_helpers.R"))
need(c("mlVAR"))

d <- read_ema()
d$pid <- as.factor(d$pid)

set.seed(20260703)
m <- mlVAR(d, vars = EXTENDED_NODES, idvar = "pid", dayvar = "day", beepvar = "beep",
           lags = 1, temporal = "orthogonal", contemporaneous = "orthogonal",
           estimator = "lmer", scale = TRUE, verbose = FALSE)
saveRDS(m, file.path(DIR_MODELS, "mlvar_extended.rds"))
s <- summary(m)
te <- s$temporal[, c("from", "to", "fixed", "SE", "P", "ran_SD")]
names(te) <- c("from", "to", "weight", "SE", "P", "ran_SD")
te$edge <- paste0(te$from, "__to__", te$to)
write_result(te, "extended_mlvar_temporal_edges.csv", DIR_NETWORKS)

con <- s$contemporaneous[, c("v1", "v2", "pcor", "P 1->2", "P 1<-2")]
names(con) <- c("node1", "node2", "pcor", "P_a", "P_b")
con$P <- pmin(con$P_a, con$P_b)
write_result(con[, c("node1", "node2", "pcor", "P")],
             "extended_mlvar_contemporaneous_edges.csv", DIR_NETWORKS)

# compare the shared core-4 edges
ref <- utils::read.csv(file.path(DIR_NETWORKS, "05_mlvar_core_temporal_edges.csv"))
ref$edge <- paste0(ref$from, "__to__", ref$to)
core_edges <- ref$edge
mrg <- merge(ref[, c("edge", "weight")], te[, c("edge", "weight")], by = "edge",
             suffixes = c("_core4", "_extended"))
cmp <- data.frame(edge = mrg$edge, weight_core4 = mrg$weight_core4,
                  weight_extended = mrg$weight_extended)
write_result(cmp, "extended_core_vs_full_compare.csv", DIR_NETWORKS)
cat(sprintf("[extended-6] r(core-4 edges vs extended) = %.3f\n",
            stats::cor(cmp$weight_core4, cmp$weight_extended)))
