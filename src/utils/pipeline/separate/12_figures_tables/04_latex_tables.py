"""Stage 12.4 - Generate LaTeX (booktabs) tables for the manuscript.

The manuscript inputs these files directly, so table layout rules live here: titles above the
table, notes below, all tables left-aligned. Main and supplementary tables are regenerated
from the numeric results rather than hand-typed in the manuscript.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

LIB = Path(__file__).resolve().parents[3] / "lib"
sys.path.insert(0, str(LIB))
import paths  # noqa: E402
import vizstyle as vs  # noqa: E402

T = paths.RESULTS_TABLES
N = paths.RESULTS_NETWORKS
paths.ensure_dirs()

NICE = vs.NODE_LABELS_LONG


def esc(value) -> str:
    s = "" if pd.isna(value) else str(value)
    for a, b in [("&", r"\&"), ("%", r"\%"), ("_", r"\_"), ("~", r"\textasciitilde{}"),
                 ("->", r"$\rightarrow$"), (">", r"$>$")]:
        s = s.replace(a, b)
    return s


def fmt_p(p) -> str:
    if pd.isna(p):
        return ""
    return "<.001" if p < .001 else f"{p:.3f}".lstrip("0")


def body(df, colspec):
    lines = [rf"\begin{{tabular*}}{{\textwidth}}{{@{{\extracolsep{{\fill}}}}{colspec}@{{}}}}",
             r"\toprule", " & ".join(esc(c) for c in df.columns) + r" \\", r"\midrule"]
    for _, row in df.iterrows():
        lines.append(" & ".join(esc(v) for v in row.values) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular*}"]
    return lines


def latex_table(df, caption, label, colspec=None, note=None, size=r"\footnotesize"):
    if colspec is None:
        colspec = "l" + "r" * (len(df.columns) - 1)
    lines = [r"\begin{table}[H]", r"\raggedright", rf"\caption{{{caption}}}",
             rf"\label{{{label}}}", size, r"\begingroup",
             r"\setlength{\tabcolsep}{4pt}", r"\renewcommand{\arraystretch}{1.08}",
             r"\noindent"]
    lines += body(df, colspec)
    if note:
        lines.append(rf"\par\vspace{{3pt}}\noindent\parbox{{\textwidth}}{{{size}\textit{{Note.}} {note}}}")
    lines += [r"\endgroup", r"\end{table}"]
    return "\n".join(lines) + "\n"


def two_panel(pa, pb, caption, label, csa, csb, ta, tb, note, size=r"\footnotesize"):
    lines = [r"\begin{table}[H]", r"\raggedright", rf"\caption{{{caption}}}",
             rf"\label{{{label}}}", size, r"\begingroup",
             r"\setlength{\tabcolsep}{4pt}", r"\renewcommand{\arraystretch}{1.08}",
             rf"\noindent\textit{{Panel A.}} {ta}\par\vspace{{2pt}}"]
    lines += body(pa, csa)
    lines.append(rf"\par\vspace{{6pt}}\noindent\textit{{Panel B.}} {tb}\par\vspace{{2pt}}")
    lines += body(pb, csb)
    lines.append(rf"\par\vspace{{3pt}}\noindent\parbox{{\textwidth}}{{{size}\textit{{Note.}} {note}}}")
    lines += [r"\endgroup", r"\end{table}"]
    return "\n".join(lines) + "\n"


def three_panel(pa, pb, pc, caption, label, csa, csb, csc, ta, tb, tc, note,
                size=r"\footnotesize"):
    lines = [r"\begin{table}[H]", r"\raggedright", rf"\caption{{{caption}}}",
             rf"\label{{{label}}}", size, r"\begingroup",
             r"\setlength{\tabcolsep}{4pt}", r"\renewcommand{\arraystretch}{1.08}",
             rf"\noindent\textit{{Panel A.}} {ta}\par\vspace{{2pt}}"]
    lines += body(pa, csa)
    lines.append(rf"\par\vspace{{6pt}}\noindent\textit{{Panel B.}} {tb}\par\vspace{{2pt}}")
    lines += body(pb, csb)
    lines.append(rf"\par\vspace{{6pt}}\noindent\textit{{Panel C.}} {tc}\par\vspace{{2pt}}")
    lines += body(pc, csc)
    lines.append(rf"\par\vspace{{3pt}}\noindent\parbox{{\textwidth}}{{{size}\textit{{Note.}} {note}}}")
    lines += [r"\endgroup", r"\end{table}"]
    return "\n".join(lines) + "\n"


def write(fname, content):
    out_dir = paths.TABLES_MAIN if fname.startswith("MAIN_") else paths.TABLES_SUPP
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / fname).write_text(content)
    print("  wrote", (out_dir / fname).relative_to(paths.ROOT))


def edge_name(frm, to):
    return f"{NICE.get(frm, frm)} -> {NICE.get(to, to)}"


def opt(p):
    return pd.read_csv(p) if Path(p).exists() else None


# ---- MAIN_01 sample ---------------------------------------------------------
def main_01():
    t1 = pd.read_csv(T / "02_person_level_table1.csv")
    t1.columns = ["Variable", "Mean (SD)", "Range", "n"]
    write("MAIN_01_sample_descriptives.tex", latex_table(
        t1, "Baseline characteristics of the analytic sample.", "tab:sample",
        colspec="lccc",
        note=("MPI = West Haven-Yale Multidimensional Pain Inventory; PDI = Pain Disability "
              "Index; PCS = Pain Catastrophizing Scale; PVAQ = Pain Vigilance and Awareness "
              "Questionnaire; HADS = Hospital Anxiety and Depression Scale; NEO-FFI = NEO "
              "Five-Factor Inventory.")))


# ---- MAIN_02 EMA descriptives + variance ------------------------------------
def main_02():
    ed = pd.read_csv(T / "02_ema_descriptives.csv")
    vd = pd.read_csv(T / "03_variance_decomposition.csv")
    core = ["PIJN", "THREAT", "ATTEND", "ENGAGE", "EFFIC", "VALENCE"]
    m = ed[ed["variable"].isin(core)].merge(
        vd[["variable", "icc_person", "var_within_day"]], on="variable", how="left")
    m["Measure"] = m["variable"].map(NICE)
    m = m.set_index("variable").loc[core].reset_index()
    tab = m[["Measure", "n_obs", "mean", "sd", "pct_missing", "icc_person",
             "var_within_day"]].copy()
    tab.columns = ["Measure", "$n$ obs", "Mean", "SD", "% miss.", "ICC", "Within-day var."]
    for c in ["Mean", "SD", "ICC", "Within-day var."]:
        tab[c] = tab[c].round(2)
    tab["% miss."] = tab["% miss."].round(1)
    write("MAIN_02_ema_descriptives_variance.tex", latex_table(
        tab, "Momentary measures: descriptive statistics and variance partition.",
        "tab:emadesc", colspec="lcccccc",
        note=("ICC = intraclass correlation (between-person share). Within-day var. is the "
              "moment-to-moment variance share available to the lag-1 network.")))


# ---- MAIN_03 pooled temporal effects ----------------------------------------
def main_03():
    te = pd.read_csv(N / "05_mlvar_core_temporal_edges.csv")
    te["Effect"] = [edge_name(f, t) for f, t in zip(te["from"], te["to"])]
    te["95% CI"] = [f"[{w - 1.96 * s:.2f}, {w + 1.96 * s:.2f}]"
                    for w, s in zip(te["weight"], te["SE"])]
    te["is_ar"] = te["from"] == te["to"]
    te = te.sort_values(["is_ar", "P"]).reset_index(drop=True)
    tab = te[["Effect", "weight", "SE", "95% CI", "P", "ran_SD"]].copy()
    for c in ["weight", "SE", "ran_SD"]:
        tab[c] = tab[c].round(3)
    tab["P"] = tab["P"].map(fmt_p)
    tab.columns = ["Effect (lag-1)", "Estimate", "SE", "95% CI", "$p$", "Random SD"]
    write("MAIN_03_mlvar_temporal_effects.tex", latex_table(
        tab, "Pooled temporal (lag-1) network: multilevel VAR fixed effects (benchmark).",
        "tab:temporal", colspec="lccccc",
        note=("Standardized within-person coefficients from the mlVAR benchmark. Cross-lagged "
              "effects are listed above autoregressive effects. Random SD is the between-person "
              "standard deviation of the effect, the pooled-model index of heterogeneity.")))


# ---- MAIN_04 RQ2 between-person trait associations --------------------------
def main_04():
    cc = pd.read_csv(T / "09_between_person_correlations.csv")
    cc = cc[cc["state"].isin(["Attention to pain", "Goal engagement"])].copy()
    cc["zero"] = [f"{r:.2f} ({fmt_p(p)})" for r, p in zip(cc["zero_order_r"], cc["zero_order_p"])]
    cc["partial"] = [f"{r:.2f} ({fmt_p(p)})" for r, p in zip(cc["partial_r"], cc["partial_p"])]
    tab = cc[["state", "account", "n", "zero", "partial"]].copy()
    tab.columns = ["Mean momentary state", "Account", "$n$", "$r$ ($p$)",
                   "Partial $r$ ($p$)"]
    write("MAIN_04_trait_between_person.tex", latex_table(
        tab, "RQ2 between-person associations of the baseline accounts with mean momentary "
             "attention to pain and goal engagement.", "tab:link", colspec="llccc",
        note=("Zero-order and partial (controlling mean momentary pain) correlations of each "
              "person's mean momentary state with the threat, biomedical, and personality "
              "accounts.")))


# ---- SUP_01 contemporaneous + between ---------------------------------------
def sup_01():
    con = pd.read_csv(N / "05_mlvar_core_contemporaneous_edges.csv")
    btw = pd.read_csv(N / "05_mlvar_core_between_edges.csv")
    con["Edge"] = [f"{NICE.get(a, a)} - {NICE.get(b, b)}" for a, b in zip(con["node1"], con["node2"])]
    btw["Edge"] = [f"{NICE.get(a, a)} - {NICE.get(b, b)}" for a, b in zip(btw["node1"], btw["node2"])]
    ct = con[["Edge", "pcor", "P"]].copy(); ct["Network"] = "Contemporaneous"
    bt = btw[["Edge", "pcor", "P"]].copy(); bt["Network"] = "Between-person"
    both = pd.concat([ct, bt])[["Network", "Edge", "pcor", "P"]].copy()
    both["pcor"] = both["pcor"].round(3)
    both["P"] = both["P"].map(fmt_p)
    both.columns = ["Network", "Edge", "Partial $r$", "$p$"]
    write("SUP_01_contemporaneous_between_edges.tex", latex_table(
        both, "Contemporaneous and between-person networks (benchmark).",
        "tab:sup-contemporaneous-between", colspec="llcc",
        note="Partial correlations from the pooled mlVAR benchmark."))


# ---- SUP_02 stationarity ----------------------------------------------------
def sup_02():
    sk = pd.read_csv(T / "04_item_distribution.csv").round(3)
    sk.columns = ["Measure", "Skewness", "Kurtosis"]
    st = pd.read_csv(T / "04_stationarity_summary.csv")
    st["variable"] = st["variable"].map(NICE)
    st.columns = ["Variable", "Prop. linear trend", "Prop. KPSS non-stationary"]
    st[["Prop. linear trend", "Prop. KPSS non-stationary"]] = \
        st[["Prop. linear trend", "Prop. KPSS non-stationary"]].round(3)
    write("SUP_02_stationarity.tex", two_panel(
        sk, st, "Item distribution and per-person stationarity.", "tab:sup-stationarity",
        "lcc", "lcc", "Skewness and kurtosis of the core momentary items.",
        "Share of individual series flagged by a linear-trend test and by KPSS.",
        "KPSS = Kwiatkowski-Phillips-Schmidt-Shin test (null is stationarity). A within-person "
        "detrended sensitivity model is reported in the robustness battery."))


# ---- SUP_03 missingness + imputation ----------------------------------------
def sup_03():
    miss = pd.read_csv(T / "04_missingness_by_measure.csv")
    miss.columns = ["Measure", "Observed", "Missing", "% missing"]
    imp = pd.read_csv(T / "04_imputation_comparison.csv")
    imp.columns = ["Method", "Type", "Std. RMSE", "Std. MAE", "$r$ (held-out)"]
    write("SUP_03_imputation_comparison.tex", two_panel(
        miss, imp, "Missing data and imputation benchmark.", "tab:sup-imputation",
        "lccc", "llccc", "Momentary missingness by measure.",
        "Univariate and multivariate imputation compared by held-out reconstruction.",
        "The primary temporal models use available-case (pairwise) handling within each "
        "equation. As a benchmark, 20\\% of observed values were held out at random and "
        "reconstructed. Multivariate methods that borrow strength across concurrent measures "
        "recovered momentary fluctuations best, which supports the available-case decision."))


# ---- SUP_04 sgimme ----------------------------------------------------------
def sup_04():
    spc = opt(N / "06_sgimme_summary_path_counts.csv")
    if spc is None:
        return
    s = spc.copy()
    s["Path"] = s["path"]
    s["Class"] = np.where(s["lhs"] == s["rhs"].str.replace("lag", "", regex=False),
                          "Autoregressive", "Cross-variable")
    s = s.sort_values(["count.group", "count.ind"], ascending=[False, False]).head(14)
    cols = ["Path", "Class", "count.group", "count.ind"]
    extra = [c for c in ["count.subgroup1"] if c in s.columns]
    s = s[cols + extra]
    s.columns = ["Path", "Class", "Group $n$", "Individual $n$"] + \
                (["Subgroup-1 $n$"] if extra else [])
    count_levels = "group, individual, or first subgroup level" if extra else \
        "group or individual level"
    write("SUP_04_sgimme_paths.tex", latex_table(
        s, "S-GIMME path prevalence.", "tab:sup-sgimme",
        colspec="ll" + "c" * (len(s.columns) - 2),
        note=(f"Counts are the number of participants for whom S-GIMME retained each path at the "
              f"{count_levels}. Paths place the outcome on the left of the tilde; 'lag' marks "
              f"lagged (temporal) predictors."),
        size=r"\scriptsize"))


# ---- SUP_05 graphicalVAR edge-selection frequency ---------------------------
def sup_05():
    freq = pd.read_csv(N / "07_graphicalvar_edge_selection_freq.csv")
    freq["Edge"] = [edge_name(f, t) for f, t in zip(freq["from"], freq["to"])]
    freq["Type"] = np.where(freq["from"] == freq["to"], "Autoregressive", "Cross-variable")
    tab = freq.sort_values("pct_selected", ascending=False)[["Edge", "Type", "pct_selected"]]
    tab.columns = ["Directed edge", "Type", "% of persons selecting"]
    write("SUP_05_graphicalvar_selection.tex", latex_table(
        tab, "Per-person graphicalVAR: temporal edge-selection frequency.",
        "tab:sup-graphicalvar", colspec="llc",
        note=("Percentage of fitted participants for whom the regularized (EBIC) individual "
              "network selected each directed lag-1 edge. Autoregressive edges dominate; "
              "cross-variable edges are sparse and heterogeneous."),
        size=r"\scriptsize"))


# ---- SUP_06 extended model --------------------------------------------------
def sup_06():
    ex = pd.read_csv(N / "extended_mlvar_temporal_edges.csv")
    keep = ex[(ex["to"] == "PIJN") | (ex["from"] == ex["to"])].copy()
    keep["Effect"] = [edge_name(f, t) for f, t in zip(keep["from"], keep["to"])]
    keep["is_ar"] = keep["from"] == keep["to"]
    keep = keep.sort_values(["is_ar", "P"])
    tab = keep[["Effect", "weight", "SE", "P", "ran_SD"]].copy()
    for c in ["weight", "SE", "ran_SD"]:
        tab[c] = tab[c].round(3)
    tab["P"] = keep["P"].map(fmt_p).values
    tab.columns = ["Effect (lag-1)", "Estimate", "SE", "$p$", "Random SD"]
    write("SUP_06_extended_model.tex", latex_table(
        tab, "Extended six-node model: autoregressive effects and effects on pain.",
        "tab:sup-extended", colspec="lcccc",
        note=("The model adds two further goal-directed activity characteristics, momentary "
              "efficacy and valence. The core four-node edges were essentially unchanged "
              "relative to the primary benchmark (see the sensitivity-agreement table)."),
        size=r"\scriptsize"))


# ---- SUP_07 per-person coupling summary -------------------------------------
def sup_07():
    pp = pd.read_csv(N / "07_perperson_pain_equation.csv")
    rows = []
    for col, lab in [("threat_to_pain", "Threat value"),
                     ("attend_to_pain", "Attention to pain"),
                     ("engage_to_pain", "Goal engagement")]:
        v = pp[col].dropna()
        lo = pp[col.replace("_to_pain", "_lo")]
        hi = pp[col.replace("_to_pain", "_hi")]
        sig = (((lo > 0) & (hi > 0)) | ((lo < 0) & (hi < 0))).sum()
        rows.append({"Driver -> pain": lab, "$n$": int(v.notna().sum()),
                     "Mean": round(v.mean(), 3), "SD": round(v.std(), 3),
                     "Min": round(v.min(), 2), "Max": round(v.max(), 2),
                     "Indiv. sig.": int(sig)})
    tab = pd.DataFrame(rows)
    write("SUP_07_perperson_couplings.tex", latex_table(
        tab, "Per-person unregularized pain-driver couplings.", "tab:sup-couplings",
        colspec="lcccccc",
        note=("Each participant's lag-1 coefficient predicting pain from the previous prompt's "
              "driver, on person-standardized data. Indiv. sig. counts participants whose 95\\% "
              "confidence interval excludes zero.")))


# ---- SUP_08 robustness stability (LOO + bootstrap) --------------------------
def sup_08():
    loo = opt(N / "robust_loo_summary.csv")
    boot = opt(N / "robust_bootstrap_summary.csv")
    if loo is None or boot is None:
        return
    rob = loo.merge(boot[["edge", "ci_lo", "ci_hi", "prop_sign_consistent"]], on="edge",
                    suffixes=("_loo", "_boot"))
    rob = rob[rob["from"] != rob["to"]].sort_values("mean")
    rob["Effect"] = [edge_name(f, t) for f, t in zip(rob["from"], rob["to"])]
    rob["LOPO range"] = [f"[{lo:.3f}, {hi:.3f}]" for lo, hi in zip(rob["min"], rob["max"])]
    rob["Bootstrap 95% CI"] = [f"[{lo:.3f}, {hi:.3f}]"
                               for lo, hi in zip(rob["ci_lo"], rob["ci_hi"])]
    tab = rob[["Effect", "mean", "LOPO range", "Bootstrap 95% CI",
               "prop_sign_consistent_boot"]].copy()
    tab["mean"] = tab["mean"].round(3)
    tab["prop_sign_consistent_boot"] = tab["prop_sign_consistent_boot"].round(3)
    tab.columns = ["Cross-lagged effect", "Mean", "LOPO range", "Bootstrap 95% CI",
                   "Bootstrap sign-consistency"]
    write("SUP_08_robustness_stability.tex", latex_table(
        tab, "Stability of pooled cross-lagged edges: leave-one-out and person bootstrap.",
        "tab:robust", colspec="lcccc",
        note="LOPO = leave-one-participant-out refits; bootstrap = person cluster resamples."))


# ---- SUP_09 sensitivity agreement -------------------------------------------
def sup_09():
    rows = []
    def rr(name, f, a, b):
        d = opt(N / f)
        if d is not None and a in d and b in d:
            r = np.corrcoef(d[a], d[b])[0, 1]
            flips = int(((np.sign(d[a]) != np.sign(d[b])) &
                         (np.maximum(np.abs(d[a]), np.abs(d[b])) > 0.05)).sum())
            rows.append({"Sensitivity analysis": name, "$r$ with primary": round(r, 3),
                         "Sign flips": flips})
    rr("Within-person detrended", "robust_detrended_compare.csv", "weight_ref",
       "weight_detrended")
    rr("Attention two-item composite", "robust_attention_composite_compare.csv",
       "weight_ref", "weight_attcomposite")
    rr("Stricter compliance ($\\geq 70$)", "robust_threshold70_compare.csv", "weight_ref",
       "weight_thr70")
    rr("Extended six-node model", "extended_core_vs_full_compare.csv", "weight_core4",
       "weight_extended")
    if rows:
        write("SUP_09_sensitivity_agreement.tex", latex_table(
            pd.DataFrame(rows),
            "Agreement of each sensitivity analysis with the primary temporal network.",
            "tab:agreement", colspec="lcc",
            note="$r$ = correlation of the 16 temporal coefficients with the primary benchmark."))


# ---- SUP_10 cross-level moderation ------------------------------------------
def sup_10():
    mod = pd.read_csv(T / "09_moderation.csv")
    tab = mod[["coupling", "moderator", "within_b", "interaction_b", "interaction_SE",
               "interaction_p"]].copy()
    tab["interaction_p"] = tab["interaction_p"].map(fmt_p)
    tab.columns = ["Coupling", "Moderator", "Within-person $b$", "Interaction $b$",
                   "Interaction SE", "Interaction $p$"]
    write("SUP_10_moderation.tex", latex_table(
        tab, "Cross-level moderation of the within-person couplings by baseline accounts.",
        "tab:sup-moderation", colspec="llcccc",
        note=("Each row is a multilevel model in which a baseline account moderates a "
              "within-person lag-1 coupling (random slope). Within-person $b$ is the average "
              "coupling; interaction $b$ is the moderation by the standardized account. "
              "Couplings were not reliably moderated."), size=r"\scriptsize"))


# ---- SUP_11 daily dysfunction -----------------------------------------------
def sup_11():
    mod = pd.read_csv(T / "11_daily_dysfunction_models.csv")
    m = mod[mod["term"] != "(Intercept)"].copy()
    m["Outcome"] = m["outcome"].str.replace("eve_", "").str.replace("_", " ")
    m["Predictor"] = m["term"].str.replace("_wc", "").map(
        lambda x: NICE.get(x, x))
    m["p"] = m["p"].map(fmt_p)
    tab = m[["Outcome", "Predictor", "estimate", "SE", "p"]].copy()
    tab.columns = ["Evening outcome", "Day predictor (within-person)", "Estimate", "SE", "$p$"]
    write("SUP_11_daily_dysfunction.tex", latex_table(
        tab, "Daily dysfunction: within-person day-level models.", "tab:sup-dysfunction",
        colspec="llccc",
        note=("Multilevel models with participant random intercepts. Predictors are "
              "person-centered day means. Day-to-day (between-day) variance in pain was small, "
              "so day-level effects are weak relative to the momentary dynamics.")))


# ---- SUP_12 context ---------------------------------------------------------
def sup_12():
    loc = pd.read_csv(T / "02_context_by_location.csv")
    soc = pd.read_csv(T / "02_context_by_social.csv")
    sw = pd.read_csv(T / "02_studyweek_effects.csv")
    lt = loc[["location_lab", "n_prompts", "pct", "mean_pain", "mean_attend",
              "mean_engage"]].copy()
    for c in ["pct", "mean_pain", "mean_attend", "mean_engage"]:
        lt[c] = lt[c].round(2)
    lt.columns = ["Location", "$n$", "%", "Pain", "Attention", "Engagement"]
    st = soc[["social_lab", "n", "mean_pain", "mean_attend", "mean_engage"]].copy()
    for c in ["mean_pain", "mean_attend", "mean_engage"]:
        st[c] = st[c].round(2)
    st.columns = ["Social context", "$n$", "Pain", "Attention", "Engagement"]
    swt = sw.copy()
    swt["variable"] = swt["variable"].map(NICE)
    swt = swt[["variable", "week2_beta", "week2_se", "week2_p"]]
    swt["week2_p"] = swt["week2_p"].map(fmt_p)
    swt.columns = ["Measure", "Week-2 effect", "SE", "$p$"]
    write("SUP_12_context.tex", three_panel(
        lt, st, swt, "Everyday context and time-in-study.", "tab:sup-context",
        "lccccc", "lcccc", "lccc",
        "Momentary measures by location.", "Momentary measures by social context.",
        "Week-2 versus week-1 drift (standardized, participant-clustered mixed models).",
        "Context summaries are descriptive. Week-2 effects test reactivity and habituation "
        "across the two-week protocol."))


def main():
    for fn in [main_01, main_02, main_03, main_04, sup_01, sup_02, sup_03, sup_04,
               sup_05, sup_06, sup_07, sup_08, sup_09, sup_10, sup_11, sup_12]:
        try:
            fn()
        except Exception as e:
            print(f"  WARNING: {fn.__name__} failed: {e}")
    print("LaTeX tables written to", paths.TABLES_PAPER)


if __name__ == "__main__":
    main()
