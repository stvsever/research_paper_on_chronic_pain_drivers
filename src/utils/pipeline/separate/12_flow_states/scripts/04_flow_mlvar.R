# Stage 12.4 - Flow-augmented multilevel VAR, and the component decomposition.
#
# Goal engagement, one of the core-four nodes, is the absorption half of the flow experience. This
# stage asks two questions that follow from that.
#
#   1. Does the benchmark circuit change when the single absorption item is replaced by the fuller
#      two-item flow experience (absorption plus enjoyment)? A composite that behaves exactly like
#      one of its parts adds label rather than information.
#   2. Which component carries the association with pain? Composite measures can be driven by a
#      single constituent, in which case the composite obscures rather than summarises
#      (VanderWeele, 2022). Absorption, enjoyment, challenge, and skill are therefore entered
#      separately and compared against the composite.
#
# The mlVAR specification matches stage 05 exactly, so the flow-augmented network is directly
# comparable to the benchmark: within-day lags, orthogonal random effects, person-standardized.

this <- normalizePath(sub("--file=", "",
  grep("--file=", commandArgs(FALSE), value = TRUE)[1]), mustWork = FALSE)
lib <- file.path(dirname(this), "..", "..", "..", "..", "lib")
source(file.path(lib, "common.R"))
need(c("mlVAR", "lme4", "lmerTest"))

set.seed(20260703)
ctrl <- lme4::lmerControl(calc.derivs = FALSE, optimizer = "bobyqa")

d <- build_flow(read_ema())
d$pid <- as.factor(d$pid)

# --- 1. flow-augmented network -----------------------------------------------
vars <- c("PIJN", "THREAT", "ATTEND", "FLOWEXP")
m <- mlVAR(d, vars = vars, idvar = "pid", dayvar = "day", beepvar = "beep",
           lags = 1, temporal = "orthogonal", contemporaneous = "orthogonal",
           estimator = "lmer", scale = TRUE, verbose = FALSE)
saveRDS(m, file.path(DIR_MODELS, "mlvar_flow.rds"))
s <- summary(m)

temp <- s$temporal[, c("from", "to", "fixed", "SE", "P", "ran_SD")]
names(temp) <- c("from", "to", "weight", "SE", "P", "ran_SD")
write_result(temp, "12_flow_mlvar_temporal_edges.csv", DIR_NETWORKS)

con <- s$contemporaneous[, c("v1", "v2", "pcor", "P 1->2", "P 1<-2", "ran_SD_pcor")]
names(con) <- c("node1", "node2", "pcor", "P_a", "P_b", "ran_SD")
con$P <- pmin(con$P_a, con$P_b)
write_result(con[, c("node1", "node2", "pcor", "P", "ran_SD")],
             "12_flow_mlvar_contemporaneous_edges.csv", DIR_NETWORKS)

# --- 2. does the composite behave like the benchmark node? -------------------
# Compare the pain-relevant edges of the flow-augmented network against the benchmark network
# in which the same slot is occupied by absorption alone.
bench_t <- utils::read.csv(file.path(DIR_NETWORKS, "05_mlvar_core_temporal_edges.csv"))
bench_c <- utils::read.csv(file.path(DIR_NETWORKS, "05_mlvar_core_contemporaneous_edges.csv"))

pick_t <- function(df, frm, to) {
  r <- df[df$from == frm & df$to == to, ]
  if (nrow(r)) c(r$weight[1], r$P[1]) else c(NA, NA)
}
pick_c <- function(df, a, b) {
  r <- df[(df$node1 == a & df$node2 == b) | (df$node1 == b & df$node2 == a), ]
  if (nrow(r)) c(r$pcor[1], r$P[1]) else c(NA, NA)
}

cmp_rows <- list()
for (spec in list(
      list(lab = "Pain(t-1) -> activity node(t)", kind = "t", a = "PIJN", b = "ENGAGE",
           bf = "PIJN", bt = "FLOWEXP"),
      list(lab = "Activity node(t-1) -> Pain(t)", kind = "t", a = "ENGAGE", b = "PIJN",
           bf = "FLOWEXP", bt = "PIJN"),
      list(lab = "Pain - activity node (contemporaneous)", kind = "c", a = "PIJN", b = "ENGAGE",
           bf = "PIJN", bt = "FLOWEXP"),
      list(lab = "Attention - activity node (contemporaneous)", kind = "c", a = "ATTEND",
           b = "ENGAGE", bf = "ATTEND", bt = "FLOWEXP"))) {
  if (spec$kind == "t") {
    bench <- pick_t(bench_t, spec$a, spec$b); flow <- pick_t(temp, spec$bf, spec$bt)
  } else {
    bench <- pick_c(bench_c, spec$a, spec$b); flow <- pick_c(con, spec$bf, spec$bt)
  }
  cmp_rows[[length(cmp_rows) + 1]] <- data.frame(
    edge = spec$lab,
    benchmark_absorption = round(bench[1], 3), benchmark_p = signif(bench[2], 3),
    flow_composite = round(flow[1], 3), flow_p = signif(flow[2], 3),
    difference = round(flow[1] - bench[1], 3))
}
write_result(do.call(rbind, cmp_rows), "12_flow_network_comparison.csv")

# --- 3. component decomposition ----------------------------------------------
# Each constituent entered on its own, then all four together, so a component that carries the
# whole association is visible. Person-mean centered, adjusted for physical activation.
f <- d[stats::complete.cases(d[, FLOW_ITEMS]), ]
tidy1 <- function(m, term, model, outcome) {
  co <- summary(m)$coefficients
  data.frame(model = model, outcome = outcome, term = term,
             estimate = round(co[term, "Estimate"], 3),
             SE = round(co[term, "Std. Error"], 3),
             t = round(co[term, "t value"], 2),
             p = signif(co[term, "Pr(>|t|)"], 4), row.names = NULL)
}

dec_rows <- list()
for (o in c("PIJN", "PIJN_AFF", "ATTEND", "THREAT")) {
  # each component alone
  for (v in c("ENGAGE_w", "VALENCE_w", "CHALLENGE_w", "EFFIC_w", "FLOWEXP_w")) {
    fml <- as.formula(sprintf("%s ~ %s + ACTIEF_w + (1 + %s | pid)", o, v, v))
    mm <- lmerTest::lmer(fml, data = f, REML = TRUE, control = ctrl)
    dec_rows[[length(dec_rows) + 1]] <- tidy1(mm, v, "entered alone", o)
  }
  # all four constituents simultaneously
  fml <- as.formula(sprintf(
    "%s ~ ENGAGE_w + VALENCE_w + CHALLENGE_w + EFFIC_w + ACTIEF_w + (1 | pid)", o))
  mm <- lmerTest::lmer(fml, data = f, REML = TRUE, control = ctrl)
  for (v in c("ENGAGE_w", "VALENCE_w", "CHALLENGE_w", "EFFIC_w")) {
    dec_rows[[length(dec_rows) + 1]] <- tidy1(mm, v, "all four together", o)
  }
}
dec <- do.call(rbind, dec_rows)
write_result(dec, "12_flow_component_decomposition.csv")

cat("\n=== flow-augmented network, pain-relevant edges ===\n")
print(do.call(rbind, cmp_rows), row.names = FALSE)
cat("\n=== component decomposition, pain intensity ===\n")
print(dec[dec$outcome == "PIJN", c("model", "term", "estimate", "SE", "p")], row.names = FALSE)
