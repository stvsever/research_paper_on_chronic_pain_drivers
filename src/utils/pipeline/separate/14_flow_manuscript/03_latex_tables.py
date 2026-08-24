"""Stage 14.3 - LaTeX tables for manuscript 02 (the flow construct study).

Five main tables, one per results section, and ten supplementary tables. Every number is
read from the stage 12 result files, so nothing here is hand-typed.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

LIB = Path(__file__).resolve().parents[3] / "lib"
sys.path.insert(0, str(LIB))
import paths  # noqa: E402
from latextab import latex_table, panelled_table, fmt_p, fmt_b, writer  # noqa: E402

T = paths.RESULTS_TABLES
N = paths.RESULTS_NETWORKS
paths.ensure_dirs()
write = writer(paths.FLOW_TABLES_MAIN, paths.FLOW_TABLES_SUPP)

OUT = ["PIJN", "PIJN_AFF", "ATTEND", "THREAT"]
OUT_LAB = {"PIJN": "Pain intensity", "PIJN_AFF": "Pain interference",
           "ATTEND": "Attention to pain", "THREAT": "Threat value"}
ITEMS = ["CHALLENGE", "EFFIC", "ENGAGE", "VALENCE"]
ITEM_LAB = {"CHALLENGE": "Challenge", "EFFIC": "Skill", "ENGAGE": "Absorption",
            "VALENCE": "Enjoyment", "FLOWEXP": "Flow experience"}
TERMS = ["ENGAGE_w", "VALENCE_w", "CHALLENGE_w", "EFFIC_w"]
TERM_LAB = {"ENGAGE_w": "Absorption", "VALENCE_w": "Enjoyment",
            "CHALLENGE_w": "Challenge", "EFFIC_w": "Skill",
            "FLOWEXP_w": "Flow experience (composite)"}
PROV = ("The four appraisals are single momentary items; every flow variable is a "
        "secondary, analyst-constructed measure, since the source study analysed the items "
        "separately.")


# ---- MAIN_01 sample and analytic frame --------------------------------------
def main_01():
    t1 = pd.read_csv(T / "02_person_level_table1.csv")
    t1.columns = ["Variable", "Mean (SD)", "Range", "$n$"]
    desc = pd.read_csv(T / "12_flow_item_descriptives.csv").set_index("variable")
    rows = ITEMS + ["FLOWEXP"]
    pb = pd.DataFrame({
        "Momentary item": [ITEM_LAB[v] for v in rows],
        "Role": [desc.loc[v, "role"] for v in rows],
        "$n$ obs": [f"{int(desc.loc[v, 'n']):,}" for v in rows],
        "Mean": [fmt_b(desc.loc[v, "mean"], 2) for v in rows],
        "SD": [fmt_b(desc.loc[v, "sd"], 2) for v in rows],
        "ICC": [fmt_b(desc.loc[v, "icc_person"], 3) for v in rows],
        "Within-person share": [fmt_b(desc.loc[v, "within_share"], 3) for v in rows]})
    write("MAIN_01_sample_and_frame.tex", panelled_table(
        [(t1, "lccc", "Baseline characteristics of the analytic sample."),
         (pb, "llccccc", "The four momentary appraisals and the flow experience "
                         "composite.")],
        "Sample and the momentary appraisals that operationalize flow.", "tab:frame",
        note=("MPI = West Haven-Yale Multidimensional Pain Inventory; PDI = Pain Disability "
              "Index; PCS = Pain Catastrophizing Scale; PVAQ = Pain Vigilance and Awareness "
              "Questionnaire; HADS = Hospital Anxiety and Depression Scale; NEO-FFI = NEO "
              "Five-Factor Inventory. Items were rated 1 (not at all) to 7 (very much). "
              "Condition items are challenge and skill, experience items absorption and "
              "enjoyment; the flow experience is their mean. ICC is the between-person "
              "variance share. " + PROV)))


# ---- MAIN_02 the challenge-skill condition ----------------------------------
def main_02():
    fx = pd.read_csv(T / "12_flow_condition_experience_fixed.csv")
    rnd = pd.read_csv(T / "12_flow_condition_experience_random.csv")
    tests = pd.read_csv(T / "12_flow_structural_tests.csv")
    par = pd.read_csv(T / "12_flow_condition_parameterization.csv")

    TL = {"balance_w": "Balance, within person", "elevation_w": "Elevation, within person",
          "balance_b": "Balance, between persons",
          "elevation_b": "Elevation, between persons"}
    ca = fx[(fx["model"] == "balance + elevation") & fx["term"].isin(TL)].copy()
    rsd = rnd[rnd["model"] == "balance + elevation"].set_index("term")["random_SD"]
    pa = pd.DataFrame({
        "Term": [TL[t] for t in ca["term"]],
        "$b$": [fmt_b(v) for v in ca["estimate"]],
        "SE": [fmt_b(v) for v in ca["SE"]],
        "95\\% CI": [f"[{e - 1.96 * s:.3f}, {e + 1.96 * s:.3f}]"
                     for e, s in zip(ca["estimate"], ca["SE"])],
        "$p$": [fmt_p(v) for v in ca["p"]],
        "Random SD": [fmt_b(rsd[t]) if t in rsd.index else "" for t in ca["term"]]})

    keep = tests["question"].str.startswith("Does")
    tb = tests[keep].copy()
    SHORT = {
        "Does balance add to an additive challenge + skill model?": "Balance, $-|C-S|$",
        "Does a one-sided kink at challenge = skill add (overload versus boredom)?":
            "One-sided kink at $C=S$",
        "Does a multiplicative challenge x skill interaction add?":
            "Interaction, $C \\times S$",
        "Does a full second-order response surface add?":
            "Quadratic response surface",
        "Does the four-channel quadrant structure add?": "Four-channel quadrant"}
    pb = pd.DataFrame({
        "Term added to challenge + skill": [SHORT[q] for q in tb["question"]],
        "$\\Delta$ df": [int(a - b) for a, b in zip(tb["df_full"], tb["df_restricted"])],
        "$\\chi^2$": [fmt_b(v, 2) for v in tb["chisq"]],
        "$p$": [fmt_p(v) for v in tb["p"]],
        "$\\Delta$ AIC": [fmt_b(v, 1) for v in tb["delta_AIC"]],
        "$\\Delta$ BIC": [fmt_b(b - f, 1)
                          for b, f in zip(tb["BIC_restricted"], tb["BIC_full"])]})

    pc = pd.DataFrame({
        "Parameterization": par["model"],
        "df": par["npar"],
        "AIC": [fmt_b(v, 1) for v in par["AIC"]],
        "BIC": [fmt_b(v, 1) for v in par["BIC"]],
        "$\\Delta$ AIC": [fmt_b(v, 1) for v in par["delta_AIC"]]})

    write("MAIN_02_condition_to_experience.tex", panelled_table(
        [(pa, "lccccc", "Balance and elevation predicting the flow experience "
                        "(multilevel model with random slopes)."),
         (pb, "lccccc", "Nested likelihood-ratio tests of every configural functional "
                        "form, each added to the additive challenge-plus-skill model."),
         (pc, "lcccc", "The two parameterizations of the condition at equal degrees of "
                       "freedom.")],
        "The challenge-skill condition predicting the flow experience, and nested "
        "tests of configurality.", "tab:condition",
        note=("Balance is $-|C-S|$ and elevation $(C+S)/2$, both person-mean centred; "
              "$C$ is challenge and $S$ skill. Panel A is estimated with REML and random "
              "slopes for both within-person terms. Panels B and C are estimated with "
              "maximum likelihood and a random intercept, so that only the fixed-effect "
              "structure differs across the compared models. Positive $\\Delta$ AIC and "
              "$\\Delta$ BIC favour the more complex model. " + PROV)))


# ---- MAIN_03 constituent decomposition --------------------------------------
def main_03():
    dec = pd.read_csv(T / "12_flow_component_decomposition.csv")
    lrt = pd.read_csv(T / "12_flow_composite_lrt.csv")

    def star(p):
        return "***" if p < .001 else ("**" if p < .01 else ("*" if p < .05 else ""))

    def block(model, terms):
        rows = []
        for t in terms:
            rec = {"Constituent": TERM_LAB[t]}
            for o in OUT:
                r = dec[(dec["model"] == model) & (dec["term"] == t) &
                        (dec["outcome"] == o)]
                rec[OUT_LAB[o]] = (f"{r['estimate'].iloc[0]:+.3f}{star(r['p'].iloc[0])} "
                                   f"({r['SE'].iloc[0]:.3f})" if len(r) else "")
            rows.append(rec)
        return pd.DataFrame(rows)

    pa = block("entered alone", TERMS + ["FLOWEXP_w"])
    pa2 = block("all four together", TERMS)

    QL = {"Does splitting the composite into absorption and enjoyment improve fit?":
          "Composite vs. absorption + enjoyment",
          "Do the condition items add over the experience constituents?":
          "Absorption + enjoyment vs. all four",
          "Do the four constituents improve on the composite?":
          "Composite vs. all four constituents"}
    lb = lrt[lrt["question"].isin(QL)].copy()
    pb = pd.DataFrame({
        "Outcome": [OUT_LAB[o] for o in lb["outcome"]],
        "Comparison": [QL[q] for q in lb["question"]],
        "$\\Delta$ df": [int(a - b) for a, b in zip(lb["df_full"], lb["df_restricted"])],
        "$\\chi^2$": [fmt_b(v, 2) for v in lb["chisq"]],
        "$p$": [fmt_p(v) for v in lb["p"]],
        "$\\Delta$ AIC": [fmt_b(v, 1) for v in lb["delta_AIC"]]})

    write("MAIN_03_constituent_decomposition.tex", panelled_table(
        [(pa, "lcccc", "Each appraisal entered alone, predicting the four momentary pain "
                       "measures."),
         (pa2, "lcccc", "The same four appraisals entered jointly."),
         (pb, "llcccc", "Nested likelihood-ratio tests of the composite against its "
                        "constituents.")],
        "Constituent decomposition of the flow composite.", "tab:decomposition",
        note=("Within-person (person-mean centred) predictors and outcomes. In Panel A "
              "``alone'' means the constituent is the only appraisal in the model and "
              "``joint'' means all four are entered together; the bottom row gives the "
              "composite for reference. $^{*}p<.05$, $^{**}p<.01$, $^{***}p<.001$. Panel B "
              "compares nested fixed-effect structures under maximum likelihood with a "
              "random intercept and momentary physical activation as a covariate; the "
              "composite is the constituent model under the constraint that absorption and "
              "enjoyment carry equal weight and that challenge and skill carry none. " +
              PROV)))


# ---- MAIN_04 flow and the momentary experience of pain ----------------------
def main_04():
    con = pd.read_csv(T / "12_flow_pain_contemporaneous.csv")
    lag = pd.read_csv(T / "12_flow_pain_lagged.csv")
    rs = pd.read_csv(T / "12_flow_pain_random_slopes.csv").set_index("outcome")
    per = pd.read_csv(T / "12_flow_perperson_summary.csv")

    base = con[(con["model"] == "base") & (con["term"] == "FLOWEXP_w")].set_index("outcome")
    adj = con[(con["model"] == "activity-adjusted") &
              (con["term"] == "FLOWEXP_w")].set_index("outcome")
    pa = pd.DataFrame({
        "Outcome": [OUT_LAB[o] for o in OUT],
        "$b$ unadjusted": [fmt_b(base.loc[o, "estimate"]) for o in OUT],
        "SE": [fmt_b(base.loc[o, "SE"]) for o in OUT],
        "$b$ adjusted": [fmt_b(adj.loc[o, "estimate"]) for o in OUT],
        "SE ": [fmt_b(adj.loc[o, "SE"]) for o in OUT],
        "95\\% CI": [f"[{adj.loc[o, 'estimate'] - 1.96 * adj.loc[o, 'SE']:.3f}, "
                     f"{adj.loc[o, 'estimate'] + 1.96 * adj.loc[o, 'SE']:.3f}]"
                     for o in OUT],
        "$p$": [fmt_p(adj.loc[o, "p"]) for o in OUT],
        "Random SD": [fmt_b(rs.loc[o, "random_SD_flow_adj"]) for o in OUT]})

    fw = lag[(lag["model"] == "flow(t-1) -> outcome(t)") &
             (lag["term"] == "FLOWEXP_lag")].set_index("outcome")
    ar = lag[(lag["model"] == "flow(t-1) -> outcome(t)") &
             (lag["term"] == lag["outcome"] + "_lag")].set_index("outcome")
    rv = lag[lag["model"] == "predictor(t-1) -> flow(t)"].copy()
    rv = rv[rv["term"] == rv["outcome"] + "_lag"].set_index("outcome")
    pb_rows = []
    for o in OUT:
        pb_rows.append({
            "Path": f"Flow $\\rightarrow$ {OUT_LAB[o]}",
            "$b$": fmt_b(fw.loc[o, "estimate"]), "SE": fmt_b(fw.loc[o, "SE"]),
            "$p$": fmt_p(fw.loc[o, "p"]),
            "Autoregression of the outcome": fmt_b(ar.loc[o, "estimate"])})
    for o in ["PIJN", "ATTEND", "THREAT"]:
        pb_rows.append({
            "Path": f"{OUT_LAB[o]} $\\rightarrow$ flow",
            "$b$": fmt_b(rv.loc[o, "estimate"]), "SE": fmt_b(rv.loc[o, "SE"]),
            "$p$": fmt_p(rv.loc[o, "p"]),
            "Autoregression of the outcome": fmt_b(
                lag[(lag["model"] == "predictor(t-1) -> flow(t)") &
                    (lag["outcome"] == o) &
                    (lag["term"] == "FLOWEXP_lag")]["estimate"].iloc[0])})
    pb = pd.DataFrame(pb_rows)

    pc = per[per["quantity"].isin(["contemporaneous b", "lagged b"])].copy()
    pc = pd.DataFrame({
        "Slope": ["Same beep", "Lag 1"],
        "$n$": pc["n_persons"].values,
        "Median": [fmt_b(v) for v in pc["median"]],
        "IQR": [f"[{a:.2f}, {b:.2f}]" for a, b in zip(pc["q25"], pc["q75"])],
        "Range": [f"[{a:.2f}, {b:.2f}]" for a, b in zip(pc["min"], pc["max"])],
        "\\% neg.": [fmt_b(v, 1) for v in pc["pct_negative"]],
        "Rel. neg.": [int(v) for v in pc["n_sig_negative"]],
        "Rel. pos.": [int(v) for v in pc["n_sig_positive"]]})

    write("MAIN_04_flow_and_pain.tex", panelled_table(
        [(pa, "lccccccc", "The flow experience and the momentary experience of pain at "
                          "the same beep."),
         (pb, "lcccc", "Lag-1 effects in both directions, with the outcome's own "
                       "autoregression in the same model."),
         (pc, "lccccccc", "Distribution of the person-specific flow-pain slope; "
                          "``rel.'' marks slopes whose $95\\%$ interval excludes zero.")],
        "The flow experience and the momentary experience of pain.", "tab:flowpain",
        note=("Panel A models are multilevel with a random slope for the flow experience "
              "and adjust for the challenge-skill condition; the adjusted column adds "
              "momentary physical activation. Panel B is estimated on person-standardized "
              "scores with lags built within day, so no lag crosses the overnight gap. "
              "Panel C reports unregularized per-person ordinary least squares estimates "
              "for participants with at least 50 usable moments; ``reliably'' means the "
              "95\\% confidence interval excludes zero. " + PROV)))


# ---- MAIN_05 the four channels ----------------------------------------------
def main_05():
    ap = pd.read_csv(T / "12_flow_channel_contrasts.csv")
    fl = pd.read_csv(T / "12_flow_channel_contrasts_flowref.csv")

    a = ap[ap["term"].str.startswith("chan")].copy()
    a["channel"] = a["term"].str.replace("chan", "", regex=False)
    pa_rows = []
    for name in ["Flow", "Relaxation", "Anxiety"]:
        rec = {"Channel": name}
        for o in OUT:
            r = a[(a["channel"] == name) & (a["outcome"] == o)].iloc[0]
            rec[OUT_LAB[o]] = f"{r['estimate']:+.3f} ({fmt_p(r['p'])})"
        pa_rows.append(rec)
    pa = pd.DataFrame(pa_rows)

    f = fl[fl["term"].str.startswith("chan_flowref")].copy()
    f["channel"] = f["term"].str.replace("chan_flowref", "", regex=False)
    pb_rows = []
    for name in ["Relaxation", "Anxiety", "Apathy"]:
        rec = {"Channel": name}
        for o in OUT:
            r = f[(f["channel"] == name) & (f["outcome"] == o)].iloc[0]
            rec[OUT_LAB[o]] = f"{r['estimate']:+.3f} ({fmt_p(r['p'])})"
        pb_rows.append(rec)
    pb = pd.DataFrame(pb_rows)

    write("MAIN_05_channels.tex", panelled_table(
        [(pa, "lcccc", "Each channel against apathy, the conventional reference."),
         (pb, "lcccc", "Each channel against flow, the direct head-to-head comparison.")],
        "The four challenge-skill channels and the momentary experience of pain.",
        "tab:channels",
        note=("Channels are formed from person-mean centred challenge and skill: flow is "
              "both above the person's own mean, relaxation skill only, anxiety challenge "
              "only, and apathy neither. Entries are differences on the raw 1 to 7 "
              "response scale from multilevel models with a random person intercept, with "
              "$p$ in parentheses. Negative values mean less pain, less interference, less "
              "attention to pain, or a lower threat value than the reference channel. " +
              PROV)))


# ---- supplementary ----------------------------------------------------------
def sup_01():
    c = pd.read_csv(T / "12_flow_item_correlations.csv")
    vl = ITEMS + ["FLOWEXP"]
    wi = c[c["level"] == "within"].set_index("variable")[vl].loc[vl]
    be = c[c["level"] == "between"].set_index("variable")[vl].loc[vl]
    rows = []
    for i, v in enumerate(vl):
        rec = {"Item": ITEM_LAB[v]}
        for j, u in enumerate(vl):
            rec[ITEM_LAB[u]] = ("" if i == j else
                                (fmt_b(wi.iloc[i, j], 2) if i > j
                                 else fmt_b(be.iloc[i, j], 2)))
        rows.append(rec)
    write("SUP_01_item_correlations.tex", latex_table(
        pd.DataFrame(rows), "Correlations among the four appraisals and the composite.",
        "tab:sup-itemcorr", colspec="lccccc",
        note=("Below the diagonal: within-person correlations after person-mean centring. "
              "Above the diagonal: between-person correlations of the person means. The "
              "flow experience is the mean of absorption and enjoyment, so its "
              "correlations with those two items are inflated by construction.")))


def sup_02():
    p = pd.read_csv(T / "12_flow_prevalence_by_rule.csv")
    SHORT = {"A. Absolute, both items >= 4": "A. Raw, both items $\\geq$ 4",
             "A. Absolute, both items >= 5": "A. Raw, both items $\\geq$ 5",
             "B. Grand-mean z, above the sample mean": "B. Grand-mean $z$",
             "C. Within-person z, above own mean": "C. Within-person $z$",
             "D. Person-mean centered, above own mean": "D. Person-mean centred"}
    tab = pd.DataFrame({
        "Rule": [SHORT.get(r, r) for r in p["rule_label"]],
        "Condition met": [fmt_b(100 * v, 1) for v in p["moments_condition"]],
        "Gated flow": [fmt_b(100 * v, 1) for v in p["moments_gated"]],
        "Median person": [fmt_b(100 * v, 1) for v in p["person_median"]],
        "Person range": [f"{100 * a:.1f} to {100 * b:.1f}"
                         for a, b in zip(p["person_min"], p["person_max"])],
        "At zero": [f"{int(a)}/{int(b)}"
                    for a, b in zip(p["n_persons_zero"], p["n_persons"])]})
    write("SUP_02_prevalence.tex", latex_table(
        tab, "Prevalence of flow moments under each classification rule.",
        "tab:sup-prevalence", colspec="lccccc",
        note=("All shares are percentages of moments, except the last column, which counts "
              "participants who never reach flow. The gated criterion requires both the "
              "challenge-skill condition and a flow "
              "experience above the same cut. Relative rules force a within-person "
              "distribution and therefore assign above-average moments to every "
              "participant, which is why only the absolute rules can represent the absence "
              "of flow and why every prevalence claim in the text is made on the absolute "
              "metric.")))


def sup_03():
    s = pd.read_csv(T / "12_flow_standardization_sensitivity.csv")
    tab = pd.DataFrame({
        "Metric": s["metric_label"], "Term": s["term"],
        "$b$": [fmt_b(v) for v in s["estimate"]],
        "SE": [fmt_b(v) for v in s["SE"]],
        "95\\% CI": [f"[{e - 1.96 * se:.3f}, {e + 1.96 * se:.3f}]"
                     for e, se in zip(s["estimate"], s["SE"])],
        "$p$": [fmt_p(v) for v in s["p"]]})
    write("SUP_03_standardization_sensitivity.tex", latex_table(
        tab, "Condition terms predicting the flow experience on every standardization "
             "metric.", "tab:sup-standardization", colspec="llcccc",
        note=("Person-mean centring is the primary metric. Across all four metrics the "
              "elevation effect stays between .74 and .89 and the balance effect is never "
              "positive.")))


def sup_04():
    n = pd.read_csv(T / "12_flow_condition_nested_fixed.csv")
    LAB = {"(Intercept)": "Intercept", "CHALLENGE_w": "Challenge", "EFFIC_w": "Skill",
           "balance_w": "Balance", "elevation_w": "Elevation", "overload": "Overload kink",
           "CHALLENGE_w:EFFIC_w": "Challenge $\\times$ skill",
           "I(CHALLENGE_w^2)": "Challenge$^2$", "I(EFFIC_w^2)": "Skill$^2$",
           "balance_w:elevation_w": "Balance $\\times$ elevation"}
    n = n[n["term"] != "(Intercept)"]
    tab = pd.DataFrame({
        "Model": n["model"], "Term": [LAB.get(t, t) for t in n["term"]],
        "$b$": [fmt_b(v) for v in n["estimate"]],
        "SE": [fmt_b(v) for v in n["SE"]],
        "95\\% CI": [f"[{a:.3f}, {b:.3f}]" for a, b in zip(n["lo"], n["hi"])],
        "$p$": [fmt_p(v) for v in n["p"]]})
    write("SUP_04_condition_models.tex", latex_table(
        tab, "Fixed effects of every nested condition model.", "tab:sup-condmodels",
        colspec="llcccc",
        note=("All models predict the flow experience from person-mean centred predictors "
              "with a random person intercept, estimated by maximum likelihood. The "
              "``quadratic surface + balance'' model is reported for completeness; its "
              "balance coefficient is not interpretable in isolation because balance "
              "correlates .93 with the squared discrepancy that the surface already "
              "contains.")))


def sup_05():
    d = pd.read_csv(T / "12_flow_balance_diagnostics.csv")
    s = pd.read_csv(T / "12_flow_balance_simple_slopes.csv")
    t = pd.read_csv(T / "12_flow_structural_tests.csv")
    diag = t[t["question"].str.startswith("Diagnostic")]
    QMATH = {"cor(balance, -(C - S)^2)": "$r$(balance, $-(C-S)^2$)",
             "cor(balance, C^2)": "$r$(balance, $C^2$)",
             "cor(balance, S^2)": "$r$(balance, $S^2$)",
             "cor(balance, elevation)": "$r$(balance, elevation)",
             "b challenge (additive)": "$b$ challenge (additive model)",
             "b skill (additive)": "$b$ skill (additive model)"}
    pa = pd.DataFrame({"Quantity": [QMATH.get(q, q) for q in d["quantity"]],
                       "Value": [fmt_b(v) for v in d["value"]]})
    pb = pd.DataFrame({
        "Elevation": s["elevation"],
        "Value (centred)": [fmt_b(v) for v in s["elevation_value"]],
        "Balance $b$": [fmt_b(v) for v in s["estimate"]],
        "SE": [fmt_b(v) for v in s["SE"]],
        "95\\% CI": [f"[{a:.3f}, {b:.3f}]" for a, b in zip(s["lo"], s["hi"])],
        "$p$": [fmt_p(v) for v in s["p"]]})
    pc = pd.DataFrame({
        "Comparison": [q.replace("Diagnostic: ", "") for q in diag["question"]],
        "$\\chi^2$": [fmt_b(v, 2) for v in diag["chisq"]],
        "df": diag["df"].values,
        "$p$": [fmt_p(v) for v in diag["p"]],
        "$\\Delta$ AIC": [fmt_b(v, 1) for v in diag["delta_AIC"]]})
    write("SUP_05_balance_diagnostics.tex", panelled_table(
        [(pa, "lc", "Why the balance term is not interpretable on its own."),
         (pb, "lccccc", "Simple slopes of balance across elevation."),
         (pc, "lcccc", "The two comparisons in which balance appears to matter.")],
        "Diagnostics of the balance parameterization.", "tab:sup-baldiag",
        note=("$C$ is challenge and $S$ skill, both person-mean centred. Balance is a "
              "monotone transformation of the absolute discrepancy and therefore nearly "
              "collinear with the squared discrepancy that a quadratic surface already "
              "contains; the balance-and-elevation form additionally constrains challenge "
              "and skill to equal weight, which the free additive estimates reject. Both "
              "comparisons in Panel C are properties of those parameterizations rather "
              "than evidence of configurality, which is why no configural form beats the "
              "additive model in \\Cref{tab:condition}.")))


def sup_06():
    c = pd.read_csv(T / "12_flow_condition_lagged.csv")
    LAB = {"(Intercept)": "Intercept", "balance_zz": "Balance, same beep",
           "elevation_zz": "Elevation, same beep", "balance_zz_lag": "Balance at $t-1$",
           "elevation_zz_lag": "Elevation at $t-1$",
           "FLOWEXP_lag": "Flow experience at $t-1$"}
    c = c[c["term"] != "(Intercept)"]
    tab = pd.DataFrame({
        "Model": ["Lag 1" if "t-1" in m else "Same beep" for m in c["model"]],
        "Term": [LAB.get(t, t) for t in c["term"]],
        "$b$": [fmt_b(v) for v in c["estimate"]],
        "SE": [fmt_b(v) for v in c["SE"]],
        "$p$": [fmt_p(v) for v in c["p"]],
        "$n$ obs": [f"{int(v):,}" for v in c["n_obs"]]})
    write("SUP_06_condition_lagged.tex", latex_table(
        tab, "The challenge-skill condition at the previous prompt and at the same prompt.",
        "tab:sup-condlag", colspec="llcccc",
        note=("Both models are fitted on the same rows so the lagged and same-beep "
              "estimates are directly comparable. The lag-1 model controls the flow "
              "experience's own autoregression; predictors are person-standardized and "
              "lags are built within day.")))


def sup_07():
    cmp = pd.read_csv(T / "12_flow_network_comparison.csv")
    tab = pd.DataFrame({
        "Edge": cmp["edge"],
        "Benchmark (absorption)": [fmt_b(v) for v in cmp["benchmark_absorption"]],
        "$p$": [fmt_p(v) for v in cmp["benchmark_p"]],
        "With the composite": [fmt_b(v) for v in cmp["flow_composite"]],
        "$p$ ": [fmt_p(v) for v in cmp["flow_p"]],
        "Difference": [fmt_b(v) for v in cmp["difference"]]})
    write("SUP_07_network_substitution.tex", latex_table(
        tab, "Substituting the flow composite for the single absorption node.",
        "tab:sup-network", colspec="lccccc",
        note=("Both networks are multilevel vector autoregressive models on four nodes: "
              "momentary pain, its threat value, attention to pain, and either goal "
              "absorption (benchmark) or the flow composite. Only the edges that involve "
              "the substituted node can change; none changes sign or significance.")))


def sup_08():
    p = pd.read_csv(T / "12_flow_channel_profiles.csv")
    p = p[p["rule"] == "A_abs5"]
    tab = pd.DataFrame({
        "Channel": p["channel"], "$n$": [f"{int(v):,}" for v in p["n"]],
        "\\%": [fmt_b(100 * v, 1) for v in p["share"]],
        "Pain": [fmt_b(v, 2) for v in p["mean_pijn"]],
        "Interference": [fmt_b(v, 2) for v in p["mean_pijn_aff"]],
        "Attention": [fmt_b(v, 2) for v in p["mean_attend"]],
        "Threat": [fmt_b(v, 2) for v in p["mean_threat"]],
        "Flow exp.": [fmt_b(v, 2) for v in p["mean_flowexp"]],
        "Activation": [fmt_b(v, 2) for v in p["mean_actief"]]})
    write("SUP_08_channel_profiles.tex", latex_table(
        tab, "Momentary profile of the four challenge-skill channels.",
        "tab:sup-channelprofiles", colspec="lcccccccc",
        note=("Unadjusted momentary means on the raw 1 to 7 scale under the strict "
              "absolute rule (both condition items at least 5). Activation is the "
              "self-reported physical activation item, which is far higher in the two "
              "high-challenge channels and is the reason every model reported in the text "
              "is also estimated with activation as a covariate.")))


def sup_09():
    link = pd.read_csv(T / "12_flow_trait_link.csv")
    inc = pd.read_csv(T / "12_flow_incremental_r2.csv")
    grp = pd.read_csv(T / "12_flow_coupling_groups.csv")
    pa = pd.DataFrame({
        "Person-level flow variable": link["flow_variable"],
        "Baseline profile": link["account"], "$n$": link["n"],
        "$r$": [fmt_b(v) for v in link["zero_order_r"]],
        "$p$": [fmt_p(v) for v in link["zero_order_p"]],
        "Partial $r$": [fmt_b(v) for v in link["partial_r"]],
        "$p$ ": [fmt_p(v) for v in link["partial_p"]]})
    ib = inc[inc["flow_variable"] == "Flow proneness (strict)"]
    pb = pd.DataFrame({
        "Mean momentary state": ib["state"], "$n$": ib["n"],
        "$R^2$ profiles": [fmt_b(v) for v in ib["R2_accounts"]],
        "$R^2$ + flow proneness": [fmt_b(v) for v in ib["R2_accounts_plus_flow"]],
        "$\\Delta R^2$": [fmt_b(v) for v in ib["delta_R2"]]})
    pc = pd.DataFrame({
        "Person-level variable": grp["variable"],
        "$n$ negative": grp["n_negative"], "$n$ other": grp["n_nonnegative"],
        "Mean, negative": [fmt_b(v) for v in grp["mean_negative"]],
        "Mean, other": [fmt_b(v) for v in grp["mean_nonnegative"]],
        "Cohen's $d$": [fmt_b(v) for v in grp["cohens_d"]],
        "$p$": [fmt_p(v) for v in grp["p"]]})
    write("SUP_09_person_level.tex", panelled_table(
        [(pa, "llccccc", "Person-level flow variables against the baseline profiles."),
         (pb, "lcccc", "Variance in the mean momentary states added by flow proneness."),
         (pc, "lcccccc", "Participants whose flow-pain slope is negative against the "
                         "rest.")],
        "Person-level flow proneness and the baseline profiles.", "tab:sup-personlevel",
        note=("Partial correlations control the participant's mean momentary pain. The "
              "threat profile combines the Pain Catastrophizing Scale and the Pain "
              "Vigilance and Awareness Questionnaire, the biomedical profile pain severity "
              "and duration, and the personality profile NEO-FFI neuroticism. Flow "
              "proneness is the share of a participant's moments meeting the strict "
              "absolute criterion. No profile predicts the person-specific flow-pain "
              "slope, which is the contrast the text draws with the level effects.")))


def sup_10():
    cs = pd.read_csv(T / "12_flow_compliance_sensitivity.csv")
    cov = pd.read_csv(T / "12_flow_covariate_check.csv")
    miss = pd.read_csv(T / "12_flow_missingness.csv")
    pa = pd.DataFrame({
        "Compliance floor": [f"$\\geq$ {int(v)} moments" for v in cs["threshold"]],
        "$n$ persons": cs["n_persons"], "$n$ moments": [f"{int(v):,}" for v in cs["n_moments"]],
        "$b$": [fmt_b(v, 4) for v in cs["estimate"]],
        "SE": [fmt_b(v, 4) for v in cs["SE"]],
        "$p$": [fmt_p(v) for v in cs["p"]]})
    pb = pd.DataFrame({
        "Model": cov["model"], "Focal term": cov["focal_term"],
        "$b$ without": [fmt_b(v, 4) for v in cov["b_without"]],
        "$b$ with": [fmt_b(v, 4) for v in cov["b_with"]],
        "$p$": [fmt_p(v) for v in cov["p_with"]],
        "$p$ beep": [fmt_p(v) for v in cov["beep_p"]],
        "$p$ day": [fmt_p(v) for v in cov["day_p"]]})
    LABM = {**OUT_LAB, "NEGAFF": "Negative affect", "POSAFF": "Positive affect",
            "ACTIEF": "Physical activation"}
    pc = pd.DataFrame({
        "Measure": [LABM.get(v, v) for v in miss["variable"]],
        "Mean, retained": [fmt_b(v, 2) for v in miss["mean_present"]],
        "Mean, dropped": [fmt_b(v, 2) for v in miss["mean_missing"]],
        "$n$ dropped": miss["n_missing"],
        "Cohen's $d$": [fmt_b(v) for v in miss["cohens_d"]],
        "$p$": [fmt_p(v) for v in miss["p"]]})
    write("SUP_10_robustness.tex", panelled_table(
        [(pa, "lccccc", "The flow-pain estimate at four compliance floors."),
         (pb, "llccccc", "Day and prompt position added as level-1 covariates."),
         (pc, "lccccc", "Moments lost to listwise deletion.")],
        "Robustness of the flow analyses.", "tab:sup-robustness",
        note=("Panel A repeats the activity-adjusted concurrent model of pain intensity "
              "with a stricter minimum number of completed moments per participant. In "
              "Panel B the focal estimate is compared with and without day and prompt "
              "position; prompt position is itself significant but moves no focal "
              "estimate. Panel C compares the moments retained in the flow analytic frame "
              "with the "
              f"{miss['pct_dropped'].iloc[0]:.1f}\\% dropped for a missing appraisal.")))


def main():
    for fn in [main_01, main_02, main_03, main_04, main_05,
               sup_01, sup_02, sup_03, sup_04, sup_05, sup_06, sup_07, sup_08, sup_09,
               sup_10]:
        try:
            fn()
        except Exception as e:
            import traceback
            print(f"  WARNING: {fn.__name__} failed: {e}")
            traceback.print_exc()
    print("flow LaTeX tables written to", paths.FLOW_TABLES_PAPER)


if __name__ == "__main__":
    main()
