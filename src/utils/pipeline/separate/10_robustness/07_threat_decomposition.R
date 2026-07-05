# Stage 10.7 - Threat-value decomposition sensitivity.
#
# The primary model uses a single threat node (the mean of momentary fear and catastrophizing).
# This refit enters the two appraisals as separate nodes in a five-node mlVAR
# (pain, fear, catastrophizing, attention, engagement) and checks that both threat components
# behave as the composite does, in particular that both predict a stronger subsequent focus on
# pain. Concordant effects justify pooling them into a single threat node.

this <- normalizePath(sub("--file=", "",
  grep("--file=", commandArgs(FALSE), value = TRUE)[1]), mustWork = FALSE)
lib <- file.path(dirname(this), "..", "..", "..", "lib")
source(file.path(lib, "common.R"))
need(c("mlVAR"))

d <- read_ema()
d$pid <- as.factor(d$pid)
vars <- c("PIJN", "FEAR", "CATAS", "ATTEND", "ENGAGE")

set.seed(20260703)
m <- mlVAR(d, vars = vars, idvar = "pid", dayvar = "day", beepvar = "beep",
           lags = 1, temporal = "orthogonal", contemporaneous = "orthogonal",
           estimator = "lmer", scale = TRUE, verbose = FALSE)
s <- summary(m)
te <- s$temporal[, c("from", "to", "fixed", "SE", "P")]
names(te) <- c("from", "to", "weight", "SE", "P")
write_result(te, "robust_threat_decomposition_edges.csv", DIR_NETWORKS)

key <- te[te$to %in% c("ATTEND", "PIJN") & te$from %in% c("FEAR", "CATAS"), ]
cat("\n=== threat-component effects on attention and pain ===\n")
print(key[order(key$to, key$from), ], row.names = FALSE)
cat(sprintf("\nBoth components positive on attention: %s\n",
            all(te$weight[te$from %in% c("FEAR", "CATAS") & te$to == "ATTEND"] > 0)))
