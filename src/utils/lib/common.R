# Shared helpers for all R analysis scripts.
# Sourced at the top of each stage script via a relative path resolved by the orchestrator.

# ---- paths -----------------------------------------------------------------
# Resolve the project root from this file's location. Works when sourced.
.this_file <- tryCatch(
  normalizePath(sys.frame(1)$ofile, mustWork = FALSE),
  error = function(e) NA_character_
)
if (is.na(.this_file) || .this_file == "") {
  # Fallback: assume common.R lives in src/utils/lib
  .this_file <- file.path(getwd(), "common.R")
}

project_root <- function() {
  # src/utils/lib/common.R -> up three levels to project root
  p <- normalizePath(file.path(dirname(.this_file), "..", "..", ".."),
                     mustWork = FALSE)
  p
}

ROOT <- project_root()
DIR_PROCESSED <- file.path(ROOT, "src", "data", "processed")
DIR_TABLES    <- file.path(ROOT, "src", "results", "tables")
DIR_MODELS    <- file.path(ROOT, "src", "results", "models")
DIR_NETWORKS  <- file.path(ROOT, "src", "results", "networks")
DIR_LOGS      <- file.path(ROOT, "src", "results", "logs")
for (d in c(DIR_TABLES, DIR_MODELS, DIR_NETWORKS, DIR_LOGS)) {
  if (!dir.exists(d)) dir.create(d, recursive = TRUE, showWarnings = FALSE)
}

# ---- package loading -------------------------------------------------------
need <- function(pkgs) {
  for (p in pkgs) {
    suppressPackageStartupMessages(
      ok <- requireNamespace(p, quietly = TRUE)
    )
    if (!ok) stop(sprintf("Required R package not installed: %s", p))
    suppressPackageStartupMessages(library(p, character.only = TRUE))
  }
  invisible(TRUE)
}

# ---- io --------------------------------------------------------------------
read_ema <- function() {
  f <- file.path(DIR_PROCESSED, "ema_long.csv")
  d <- utils::read.csv(f, stringsAsFactors = FALSE)
  # pandas writes the boolean flag as "True"/"False"; coerce to logical for R.
  if (is.character(d$completed)) d$completed <- d$completed %in% c("True", "TRUE", "true")
  d
}
read_person <- function() {
  f <- file.path(DIR_PROCESSED, "person_level.csv")
  utils::read.csv(f, stringsAsFactors = FALSE)
}
write_result <- function(df, name, dir = DIR_TABLES) {
  f <- file.path(dir, name)
  utils::write.csv(df, f, row.names = FALSE)
  cat(sprintf("  wrote %s (%d rows)\n", f, nrow(df)))
  invisible(f)
}

# Core analytic node sets (column names in ema_long.csv).
# Grounded in the cognitive-affective model of the interruptive function of pain
# (Eccleston & Crombez, 1999): momentary pain, the threat value that amplifies its
# attentional capture, attention to pain itself, and the goal-directed activity that pain
# interrupts.
CORE_NODES  <- c("PIJN", "THREAT", "ATTEND", "ENGAGE")
CORE_LABELS <- c("Pain", "Threat", "Attention", "Engagement")
# Extended model adds two further goal-directed activity characteristics from the diary
# (Klinger's goal-directed motivation model): efficacy and valence.
EXTENDED_NODES <- c("PIJN", "THREAT", "ATTEND", "ENGAGE", "EFFIC", "VALENCE")

# ---- flow construct (stage 12) ---------------------------------------------
# Four momentary activity appraisals map onto the two halves of Csikszentmihalyi's flow
# model. CHALLENGE and EFFIC are the antecedent challenge-skill condition; ENGAGE and
# VALENCE are the flow experience itself (absorption plus the autotelic enjoyment marker).
# Viane et al. (2004) analysed these items separately and never as a flow index, so every
# derived flow variable below is a secondary, analyst-constructed measure.
FLOW_CONDITION_ITEMS  <- c("CHALLENGE", "EFFIC")
FLOW_EXPERIENCE_ITEMS <- c("ENGAGE", "VALENCE")
FLOW_ITEMS <- c(FLOW_CONDITION_ITEMS, FLOW_EXPERIENCE_ITEMS)

# Absolute (raw 1-7) cut used for the conservative prevalence criterion; the scale midpoint
# (4) is reported alongside it as the liberal criterion.
FLOW_ABS_STRICT <- 5
FLOW_ABS_LIBERAL <- 4

#' Person-mean centre a vector within groups (the within component).
within_center <- function(x, g) ave(x, g, FUN = function(v) v - mean(v, na.rm = TRUE))

#' Person mean of a vector within groups (the between component).
between_mean <- function(x, g) ave(x, g, FUN = function(v) mean(v, na.rm = TRUE))

#' Person-standardise a vector within groups (within-person z).
within_z <- function(x, g) {
  ave(x, g, FUN = function(v) {
    s <- stats::sd(v, na.rm = TRUE)
    if (is.na(s) || s == 0) s <- 1
    (v - mean(v, na.rm = TRUE)) / s
  })
}

#' Build every derived flow variable on an ema_long data frame.
#'
#' Adds, for the chosen metric (`_w` = person-mean centred, `_z` = within-person z,
#' `_raw` = untransformed):
#'   FLOWEXP        mean of absorption and enjoyment (the flow experience)
#'   balance        -|challenge - skill|, higher = better matched
#'   elevation      (challenge + skill)/2, higher = both demanding and masterful
#' Balance alone would score a low-challenge low-skill moment (apathy) as perfectly
#' balanced, which is why the elevation term is not optional (Moneta & Csikszentmihalyi,
#' 1996). The four items are never summed into one score: that would conflate the
#' antecedent condition with the outcome experience.
build_flow <- function(d) {
  d$FLOWEXP <- rowMeans(d[, FLOW_EXPERIENCE_ITEMS], na.rm = FALSE)
  d$balance_raw   <- -abs(d$CHALLENGE - d$EFFIC)
  d$elevation_raw <- (d$CHALLENGE + d$EFFIC) / 2

  for (v in c(FLOW_ITEMS, "FLOWEXP", "PIJN", "ATTEND", "THREAT", "PIJN_AFF", "ACTIEF")) {
    if (!v %in% names(d)) next
    d[[paste0(v, "_w")]] <- within_center(d[[v]], d$pid)
    d[[paste0(v, "_b")]] <- between_mean(d[[v]], d$pid)
    d[[paste0(v, "_z")]] <- within_z(d[[v]], d$pid)
  }
  # condition terms on the two within-person metrics
  d$balance_w   <- -abs(d$CHALLENGE_w - d$EFFIC_w)
  d$elevation_w <- (d$CHALLENGE_w + d$EFFIC_w) / 2
  d$balance_z   <- -abs(d$CHALLENGE_z - d$EFFIC_z)
  d$elevation_z <- (d$CHALLENGE_z + d$EFFIC_z) / 2
  # between-person condition terms (person means of the raw items)
  d$balance_b   <- -abs(d$CHALLENGE_b - d$EFFIC_b)
  d$elevation_b <- (d$CHALLENGE_b + d$EFFIC_b) / 2
  d
}

#' Four-channel classification from a challenge and a skill vector on a common metric.
#' Massimini & Carli (1988): flow = both above cut, anxiety = challenge only,
#' relaxation = skill only, apathy = neither.
flow_channel <- function(challenge, skill, cut_c = 0, cut_s = cut_c) {
  hc <- challenge >= cut_c
  hs <- skill >= cut_s
  out <- ifelse(hc & hs, "Flow",
         ifelse(hc & !hs, "Anxiety",
         ifelse(!hc & hs, "Relaxation", "Apathy")))
  out[is.na(hc) | is.na(hs)] <- NA_character_
  factor(out, levels = c("Flow", "Relaxation", "Anxiety", "Apathy"))
}

# Minimum completed momentary reports required to fit a fully separate individual
# (idiographic) network. About 100 observations per person are recommended for stable
# individual VAR / graphicalVAR estimation (Beltz et al., 2016). Because these diaries
# reach roughly that length, individual estimation is the primary analysis here.
MIN_IDIO_OBS <- 50L

cat(sprintf("[common.R] project root: %s\n", ROOT))
