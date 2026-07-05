# Stage 05 - Multilevel VAR (pooled benchmark for the idiographic networks).
#
# Role. Because the diaries reach roughly 100 momentary reports per person, the primary
# analysis is the set of fully individual networks in stage 07. mlVAR is the partial-pooling
# benchmark: it borrows strength across persons to estimate a stable group-level network and
# to quantify how much each temporal effect varies between persons (random-effect SD). The
# group-level effects and the random-effect SDs are the reference against which the
# person-specific estimates are read.
#
# Three networks are estimated on the core nodes Pain, Attention to pain, Pain-related fear,
# Activity engagement:
#   - temporal        : directed lag-1 effects, within-day only,
#   - contemporaneous : partial correlations of within-person residuals at the same beep,
#   - between-person  : partial correlations of person means.
# Day boundaries are respected via dayvar (no lag across the overnight gap); beepvar enforces
# adjacency. Variables are within-person standardized (scale = TRUE). Random effects are
# orthogonal.

args <- commandArgs(trailingOnly = TRUE)
this <- normalizePath(sub("--file=", "",
  grep("--file=", commandArgs(FALSE), value = TRUE)[1]), mustWork = FALSE)
lib <- file.path(dirname(this), "..", "..", "..", "lib")
source(file.path(lib, "common.R"))
need(c("mlVAR"))

tag <- "core"
d <- read_ema()
d$pid <- as.factor(d$pid)

vars <- CORE_NODES
labels <- CORE_LABELS

set.seed(20260703)
m <- mlVAR(d, vars = vars, idvar = "pid", dayvar = "day", beepvar = "beep",
           lags = 1, temporal = "orthogonal", contemporaneous = "orthogonal",
           estimator = "lmer", scale = TRUE, verbose = FALSE)

saveRDS(m, file.path(DIR_MODELS, sprintf("mlvar_%s.rds", tag)))
s <- summary(m)

# --- temporal edge list (directed) -------------------------------------------
temp <- s$temporal[, c("from", "to", "fixed", "SE", "P", "ran_SD")]
names(temp) <- c("from", "to", "weight", "SE", "P", "ran_SD")
write_result(temp, sprintf("05_mlvar_%s_temporal_edges.csv", tag), DIR_NETWORKS)

# --- contemporaneous edge list (undirected partial correlations) -------------
con <- s$contemporaneous[, c("v1", "v2", "pcor", "P 1->2", "P 1<-2", "ran_SD_pcor")]
names(con) <- c("node1", "node2", "pcor", "P_a", "P_b", "ran_SD")
con$P <- pmin(con$P_a, con$P_b)
write_result(con[, c("node1", "node2", "pcor", "P", "ran_SD")],
             sprintf("05_mlvar_%s_contemporaneous_edges.csv", tag), DIR_NETWORKS)

# --- between-person edge list ------------------------------------------------
btw <- s$between[, c("v1", "v2", "pcor", "P 1->2", "P 1<-2")]
names(btw) <- c("node1", "node2", "pcor", "P_a", "P_b")
btw$P <- pmin(btw$P_a, btw$P_b)
write_result(btw[, c("node1", "node2", "pcor", "P")],
             sprintf("05_mlvar_%s_between_edges.csv", tag), DIR_NETWORKS)

# --- subject-specific temporal coefficients ----------------------------------
# Beta$subject[[s]] is a [response, predictor, lag] array. Confirm orientation by matching
# a subject-average off-diagonal cell to its fixed temporal effect.
subj <- m$results$Beta$subject
mean_arr <- Reduce(`+`, subj) / length(subj)
fix_att_to_pijn <- temp$weight[temp$from == "ATTEND" & temp$to == "PIJN"]
arr_cell <- mean_arr["PIJN", "ATTEND", 1]
stopifnot(abs(arr_cell - fix_att_to_pijn) < 0.05)
cat("[mlVAR] subject array orientation verified: [response, predictor, lag]\n")

edges <- expand.grid(predictor = vars, response = vars, stringsAsFactors = FALSE)
rows <- lapply(seq_along(subj), function(i) {
  a <- subj[[i]]
  vals <- mapply(function(pr, rs) a[rs, pr, 1], edges$predictor, edges$response)
  data.frame(pid = levels(d$pid)[i],
             from = edges$predictor, to = edges$response,
             coef = as.numeric(vals), stringsAsFactors = FALSE)
})
subj_long <- do.call(rbind, rows)
subj_long$edge <- paste0(subj_long$from, "__to__", subj_long$to)
subj_wide <- reshape(subj_long[, c("pid", "edge", "coef")],
                     idvar = "pid", timevar = "edge", direction = "wide")
names(subj_wide) <- sub("^coef\\.", "", names(subj_wide))
subj_wide$temporal_density <- rowMeans(abs(subj_wide[, setdiff(names(subj_wide), "pid")]))
write_result(subj_wide, sprintf("05_mlvar_%s_subject_temporal_coefs.csv", tag), DIR_NETWORKS)

cat("\n=== mlVAR temporal fixed effects (significant, P<.05) ===\n")
sig <- temp[temp$P < 0.05, ]
print(sig[order(sig$P), ], row.names = FALSE)
cat("\nSaved model + edge lists for tag:", tag, "\n")
