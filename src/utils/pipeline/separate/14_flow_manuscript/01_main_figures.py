"""Stage 14.1 - Main figures for manuscript 02 (the flow construct study).

Five figures, one per results section:

  MAIN_01  the instrument: what the four appraisals look like and how often the diary
           calls a moment a flow moment
  MAIN_02  configurality: every functional form in which the challenge-skill match could
           matter, and the additive model it has to beat
  MAIN_03  constituent decomposition: what the composite hides (VanderWeele, 2022)
  MAIN_04  flow and momentary pain: concurrent, lagged, and person-specific
  MAIN_05  the challenge-skill plane: where in it the least painful moments actually sit
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

LIB = Path(__file__).resolve().parents[3] / "lib"
sys.path.insert(0, str(LIB))
import paths  # noqa: E402
import vizstyle as vs  # noqa: E402

vs.apply_style()
T = paths.RESULTS_TABLES
N = paths.RESULTS_NETWORKS
M = paths.RESULTS_MODELS
FIG = paths.FLOW_FIG_MAIN
paths.ensure_dirs()

ITEMS = ["CHALLENGE", "EFFIC", "ENGAGE", "VALENCE"]
ITEM_LAB = {"CHALLENGE": "Challenge", "EFFIC": "Skill", "ENGAGE": "Absorption",
            "VALENCE": "Enjoyment", "FLOWEXP": "Flow experience"}
OUT = ["PIJN", "PIJN_AFF", "ATTEND", "THREAT"]
OUT_LAB = {"PIJN": "Pain intensity", "PIJN_AFF": "Pain interference",
           "ATTEND": "Attention to pain", "THREAT": "Threat value"}
FLOW = vs.FLOW_COLORS["FLOWEXP"]
BAL = vs.FLOW_COLORS["balance"]
ELEV = vs.FLOW_COLORS["elevation"]
GREY = "#c9d2db"


def frame():
    return pd.read_csv(M / "12_flow_analytic_frame.csv")


def _forest(ax, labels, est, lo, hi, colors, xlabel, title, zero=0.0, ms=5.5):
    y = np.arange(len(labels))[::-1]
    for yy, e, l, h, c in zip(y, est, lo, hi, colors):
        ax.hlines(yy, l, h, color=c, lw=2.4, zorder=2)
        ax.plot(e, yy, "o", ms=ms, color=vs.INK, zorder=3)
    ax.axvline(zero, color=vs.INK, lw=0.9, ls="--")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8.5)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.grid(axis="x", visible=True)
    ax.grid(axis="y", visible=False)
    return y


# ---------------------------------------------------------------------------
# MAIN_01 - The instrument and what it calls a flow moment
# ---------------------------------------------------------------------------
def main_01():
    f = frame()
    desc = pd.read_csv(T / "12_flow_item_descriptives.csv")
    corr = pd.read_csv(T / "12_flow_item_correlations.csv")
    prev = pd.read_csv(T / "12_flow_prevalence_by_rule.csv")
    prof = pd.read_csv(T / "12_flow_channel_profiles.csv")

    fig, ax = plt.subplots(2, 3, figsize=(15.6, 9.0))

    # A: response distributions of the four appraisals
    a = ax[0, 0]
    w = 0.2
    for k, it in enumerate(ITEMS):
        share = f[it].value_counts(normalize=True).reindex(range(1, 8), fill_value=0)
        role = "condition" if it in ("CHALLENGE", "EFFIC") else "experience"
        a.bar(np.arange(1, 8) + (k - 1.5) * w, share.values, w, color=vs.NODE_COLORS[it],
              edgecolor="white", label=f"{ITEM_LAB[it]} ({role})")
    a.set_xticks(range(1, 8))
    a.set_xlabel("Response (1 = not at all, 7 = very much)")
    a.set_ylabel("Share of moments")
    a.set_ylim(0, 0.375)
    a.set_title("Skill and enjoyment sit high, challenge low")
    a.legend(fontsize=7.5, ncol=2); vs.bar_axes(a); vs.panel_label(a, "A")

    # B: within (lower) and between (upper) correlation structure
    a = ax[0, 1]
    vl = ITEMS + ["FLOWEXP"]
    wi = corr[corr["level"] == "within"].set_index("variable")[vl].loc[vl].values
    be = corr[corr["level"] == "between"].set_index("variable")[vl].loc[vl].values
    Mx = np.tril(wi, -1) + np.triu(be, 1) + np.diag(np.full(len(vl), np.nan))
    im = a.imshow(Mx, cmap="RdBu_r", vmin=-1, vmax=1)
    labs = [ITEM_LAB[v] for v in vl]
    a.set_xticks(range(len(vl))); a.set_yticks(range(len(vl)))
    a.set_xticklabels(labs, rotation=35, ha="right", fontsize=7.5)
    a.set_yticklabels(labs, fontsize=7.5)
    for i in range(len(vl)):
        for j in range(len(vl)):
            if np.isfinite(Mx[i, j]):
                a.text(j, i, f"{Mx[i, j]:.2f}", ha="center", va="center", fontsize=7,
                       color=vs.INK if abs(Mx[i, j]) < 0.6 else "white")
    a.set_title("Lower = within person, upper = between")
    vs.matrix_axes(a); vs.add_cbar(fig, a, im, label="r"); vs.panel_label(a, "B")

    # C: within-person variance share
    a = ax[0, 2]
    dd = desc[desc["variable"] != "FLOWEXP"].set_index("variable").loc[ITEMS].reset_index()
    a.barh([ITEM_LAB[v] for v in dd["variable"]], dd["within_share"],
           color=[vs.NODE_COLORS[v] for v in dd["variable"]], edgecolor="white")
    for yy, v in enumerate(dd["within_share"]):
        a.text(v - 0.02, yy, f"{100 * v:.0f}%", va="center", ha="right", fontsize=8,
               color="white", fontweight="bold")
    a.axvline(0.5, color=vs.INK, ls="--", lw=1.0)
    a.set_xlim(0, 1)
    a.set_xlabel("Share of variance that is within person")
    a.set_title("All four items are momentary, not trait-like")
    vs.bar_axes(a, "horizontal"); vs.add_cbar(fig, a); vs.panel_label(a, "C")

    # D: prevalence under each classification rule
    a = ax[1, 0]
    order = ["A_abs4", "A_abs5", "B_grandz", "C_withinz", "D_center"]
    short = {"A_abs4": "A raw\n$\\geq$ 4", "A_abs5": "A raw\n$\\geq$ 5",
             "B_grandz": "B grand\nmean z", "C_withinz": "C within\nperson z",
             "D_center": "D person\ncentred"}
    pv = prev.set_index("rule").loc[order]
    x = np.arange(len(order)); w = 0.36
    cond_v = 100 * pv["moments_condition"].values
    gate_v = 100 * pv["moments_gated"].values
    a.bar(x - w / 2, cond_v, w, color=vs.MUTED, edgecolor="white", label="Condition met")
    a.bar(x + w / 2, gate_v, w, color=vs.CHANNEL_COLORS["Flow"], edgecolor="white",
          label="Condition + experience gate")
    for xi, nz, top in zip(x, pv["n_persons_zero"].values, np.maximum(cond_v, gate_v)):
        a.text(xi, top + 1.8, f"{int(nz)} of 68\nnever reach it", ha="center", fontsize=7,
               color=vs.MUTED)
    a.set_xticks(x); a.set_xticklabels([short[k] for k in order], fontsize=8)
    a.set_ylim(0, 54); a.set_ylabel("% of moments classified as flow")
    a.set_title("The metric decides how common flow is")
    a.legend(fontsize=7.5); vs.bar_axes(a); vs.panel_label(a, "D")

    # E: per-person flow proneness
    a = ax[1, 1]
    pp = f.groupby("pid")[["flow_gated_A_abs5", "flow_gated_A_abs4"]].mean()
    pp = pp.sort_values("flow_gated_A_abs5")
    y = np.arange(len(pp))
    a.barh(y, 100 * pp["flow_gated_A_abs4"].values, color=GREY, edgecolor="none",
           label="Liberal (both $\\geq$ 4)")
    a.barh(y, 100 * pp["flow_gated_A_abs5"].values, color=vs.CHANNEL_COLORS["Flow"],
           edgecolor="none", label="Strict (both $\\geq$ 5)")
    a.set_yticks([]); a.set_ylabel("Participants, ordered")
    a.set_xlabel("% of that person's moments in flow")
    a.set_title("Flow proneness ranges from never to most moments")
    a.text(0.97, 0.32, f"{int((pp['flow_gated_A_abs5'] == 0).sum())} participants never reach\n"
           "the strict criterion", transform=a.transAxes, ha="right", fontsize=8,
           color=vs.MUTED)
    a.legend(fontsize=7.5, loc="lower right"); vs.bar_axes(a, "horizontal")
    vs.panel_label(a, "E")

    # F: the four channels, share of moments and mean flow experience
    a = ax[1, 2]
    ch = prof[prof["rule"] == "A_abs5"].set_index("channel").loc[vs.CHANNEL_ORDER]
    x = np.arange(len(ch))
    bars = a.bar(x, 100 * ch["share"].values,
                 color=[vs.CHANNEL_COLORS[c] for c in ch.index], edgecolor="white")
    for xi, (sh, fe) in enumerate(zip(ch["share"], ch["mean_flowexp"])):
        a.text(xi, 100 * sh + 1.0, f"{100 * sh:.1f}%", ha="center", fontsize=8.5,
               fontweight="bold")
        a.text(xi, 100 * sh / 2, f"flow exp.\n{fe:.2f}", ha="center", va="center",
               fontsize=7, color="white")
    a.set_xticks(x); a.set_xticklabels(ch.index, fontsize=9)
    a.set_ylim(0, 44); a.set_ylabel("% of moments (strict absolute rule)")
    a.set_title("Relaxation, not flow, is the modal channel")
    vs.bar_axes(a); vs.panel_label(a, "F")

    fig.tight_layout(h_pad=2.8, w_pad=2.8)
    vs.savefig(fig, FIG / "MAIN_01_flow_instrument.png")


# ---------------------------------------------------------------------------
# MAIN_02 - Configural or additive?
# ---------------------------------------------------------------------------
def main_02():
    f = frame()
    fixed = pd.read_csv(T / "12_flow_condition_experience_fixed.csv")
    tests = pd.read_csv(T / "12_flow_structural_tests.csv")
    sens = pd.read_csv(T / "12_flow_standardization_sensitivity.csv")
    nested = pd.read_csv(T / "12_flow_condition_nested_fixed.csv")
    per = pd.read_csv(T / "12_flow_perperson_condition_slopes.csv")

    fig, ax = plt.subplots(2, 3, figsize=(15.6, 9.2))

    # A: balance and elevation, within and between persons
    a = ax[0, 0]
    be = fixed[(fixed["model"] == "balance + elevation")].set_index("term")
    rows = [("elevation_w", "Elevation, within", ELEV),
            ("balance_w", "Balance, within", BAL),
            ("elevation_b", "Elevation, between", ELEV),
            ("balance_b", "Balance, between", BAL)]
    est = [be.loc[t, "estimate"] for t, _, _ in rows]
    se = [be.loc[t, "SE"] for t, _, _ in rows]
    _forest(a, [l for _, l, _ in rows], est,
            [e - 1.96 * s for e, s in zip(est, se)],
            [e + 1.96 * s for e, s in zip(est, se)],
            [c for _, _, c in rows],
            "Effect on the flow experience (95% CI)",
            "Elevation carries the condition, balance does not")
    for yy, e in zip(np.arange(len(rows))[::-1], est):
        a.text(e, yy - 0.30, f"{e:+.3f}", ha="center", va="top", fontsize=7.5,
               color=vs.MUTED)
    a.set_ylim(-0.75, len(rows) - 0.4)
    vs.panel_label(a, "A")

    # B: balance across the four standardization metrics
    a = ax[0, 1]
    order = ["A_raw", "B_grandz", "C_withinz", "D_center"]
    lab = {"A_raw": "A raw", "B_grandz": "B grand z", "C_withinz": "C within z",
           "D_center": "D centred"}
    x = np.arange(len(order)); w = 0.36
    for k, (term, col) in enumerate([("Elevation", ELEV), ("Balance", BAL)]):
        sub = sens[sens["term"] == term].set_index("metric").loc[order]
        a.bar(x + (k - 0.5) * w, sub["estimate"].values, w, color=col, edgecolor="white",
              label=term, yerr=1.96 * sub["SE"].values, capsize=2.5,
              error_kw={"lw": 1.0, "ecolor": vs.INK})
    a.axhline(0, color=vs.INK, lw=0.9)
    a.set_xticks(x); a.set_xticklabels([lab[k] for k in order], fontsize=8.5)
    a.set_ylabel("Effect on the flow experience")
    a.set_title("Balance is never positive, on any metric")
    a.legend(fontsize=8); vs.bar_axes(a); vs.panel_label(a, "B")

    # C: nested tests of every configural functional form
    a = ax[0, 2]
    keep = ["Does balance add to an additive challenge + skill model?",
            "Does a one-sided kink at challenge = skill add (overload versus boredom)?",
            "Does a multiplicative challenge x skill interaction add?",
            "Does a full second-order response surface add?",
            "Does the four-channel quadrant structure add?"]
    short = ["+ balance\n$-|C-S|$", "+ one-sided kink\nat $C=S$", "+ interaction\n$C \\times S$",
             "+ quadratic\nsurface", "+ four-channel\nquadrant"]
    tt = tests.set_index("question").loc[keep]
    y = np.arange(len(keep))[::-1]
    cols = [vs.CHANNEL_COLORS["Flow"] if p < .05 else GREY for p in tt["p"]]
    a.barh(y, tt["delta_AIC"].values, color=cols, edgecolor="white", height=0.62)
    a.axvline(0, color=vs.INK, lw=1.0)
    for yy, (d, p, c2, df) in zip(y, zip(tt["delta_AIC"], tt["p"], tt["chisq"], tt["df"])):
        pt = "$p$ < .001" if p < .001 else f"$p$ = {p:.3f}".replace("0.", ".")
        a.text(3.4, yy, f"$\\chi^2$({int(df)}) = {c2:.2f}, {pt}",
               va="center", ha="left", fontsize=7.5, color=vs.MUTED)
    a.set_yticks(y); a.set_yticklabels(short, fontsize=8)
    a.set_xlim(-4.0, 13.0)
    a.set_xlabel("AIC gained over the additive model")
    a.set_title("No configural form improves on additivity")
    vs.bar_axes(a, "horizontal"); vs.panel_label(a, "C")

    # D: the observed surface, mean flow experience by mismatch within elevation strata
    a = ax[1, 0]
    f = f.dropna(subset=["CHALLENGE", "EFFIC", "FLOWEXP"]).copy()
    f["absd"] = (f["CHALLENGE"] - f["EFFIC"]).abs()
    f["elev"] = (f["CHALLENGE"] + f["EFFIC"]) / 2
    strata = [("Low (mean $\\leq$ 3)", f["elev"] <= 3, "#9aa5b1"),
              ("Middle (3 to 4.5)", (f["elev"] > 3) & (f["elev"] <= 4.5), BAL),
              ("High (mean > 4.5)", f["elev"] > 4.5, vs.CHANNEL_COLORS["Flow"])]
    for name, mask, col in strata:
        g = f[mask].groupby("absd")["FLOWEXP"].agg(["mean", "sem", "size"])
        g = g[g["size"] >= 40]
        a.errorbar(g.index, g["mean"], yerr=1.96 * g["sem"], marker="o", ms=5, lw=1.8,
                   color=col, capsize=2.5, label=name)
    a.set_xlabel("Mismatch $|$challenge $-$ skill$|$ (raw scale)")
    a.set_ylabel("Mean flow experience")
    a.set_title("Within an elevation band, mismatch does little")
    a.legend(fontsize=7.5, title="Elevation band", title_fontsize=7.5)
    vs.panel_label(a, "D")

    # E: what the additive model estimates instead
    a = ax[1, 1]
    add = nested[nested["model"] == "challenge + skill"].set_index("term")
    inter = nested[nested["model"] == "challenge x skill"].set_index("term")
    rows = [("CHALLENGE_w", add, "Challenge", vs.NODE_COLORS["CHALLENGE"]),
            ("EFFIC_w", add, "Skill", vs.NODE_COLORS["EFFIC"]),
            ("CHALLENGE_w:EFFIC_w", inter, "Challenge $\\times$ skill", GREY)]
    _forest(a, [l for _, _, l, _ in rows],
            [src.loc[t, "estimate"] for t, src, _, _ in rows],
            [src.loc[t, "lo"] for t, src, _, _ in rows],
            [src.loc[t, "hi"] for t, src, _, _ in rows],
            [c for _, _, _, c in rows],
            "Effect on the flow experience (95% CI)",
            "Skill weighs about twice challenge")
    for yy, (t, src, _, _) in zip(np.arange(len(rows))[::-1], rows):
        a.text(src.loc[t, "estimate"], yy - 0.24, f"{src.loc[t, 'estimate']:+.3f}",
               ha="center", va="top", fontsize=7.5, color=vs.MUTED)
    a.set_ylim(-0.7, len(rows) - 0.45)
    vs.panel_label(a, "E")

    # F: person-specific condition slopes
    a = ax[1, 2]
    bins = np.linspace(-0.35, 1.15, 31)
    a.hist(per["elevation_slope"], bins=bins, color=ELEV, alpha=0.75, edgecolor="white",
           label="Elevation")
    a.hist(per["balance_slope"], bins=bins, color=BAL, alpha=0.75, edgecolor="white",
           label="Balance")
    a.axvline(0, color=vs.INK, lw=1.1, ls="--")
    a.set_xlabel("Person-specific slope on the flow experience")
    a.set_ylabel("Participants")
    a.set_title("Balance slopes sit at zero for everyone")
    a.text(0.02, 0.97,
           f"balance: median {per['balance_slope'].median():+.3f}, "
           f"range {per['balance_slope'].min():+.2f} to {per['balance_slope'].max():+.2f}\n"
           f"elevation: median {per['elevation_slope'].median():+.3f}, "
           f"positive in {int((per['elevation_slope'] > 0).sum())} of {len(per)}",
           transform=a.transAxes, va="top", fontsize=7.5, color=vs.MUTED)
    a.legend(fontsize=8); vs.bar_axes(a); vs.panel_label(a, "F")

    fig.tight_layout(h_pad=2.8, w_pad=2.8)
    vs.savefig(fig, FIG / "MAIN_02_configural_versus_additive.png")


# ---------------------------------------------------------------------------
# MAIN_03 - Constituent decomposition
# ---------------------------------------------------------------------------
def main_03():
    dec = pd.read_csv(T / "12_flow_component_decomposition.csv")
    lrt = pd.read_csv(T / "12_flow_composite_lrt.csv")
    corr = pd.read_csv(T / "12_flow_item_correlations.csv")
    net_t = pd.read_csv(N / "05_mlvar_core_temporal_edges.csv")
    net_c = pd.read_csv(N / "05_mlvar_core_contemporaneous_edges.csv")
    flw_t = pd.read_csv(N / "12_flow_mlvar_temporal_edges.csv")
    flw_c = pd.read_csv(N / "12_flow_mlvar_contemporaneous_edges.csv")
    cmp = pd.read_csv(T / "12_flow_network_comparison.csv")

    TERMS = ["ENGAGE_w", "VALENCE_w", "CHALLENGE_w", "EFFIC_w"]
    TLAB = {"ENGAGE_w": "Absorption", "VALENCE_w": "Enjoyment",
            "CHALLENGE_w": "Challenge", "EFFIC_w": "Skill"}
    TCOL = {"ENGAGE_w": vs.NODE_COLORS["ENGAGE"], "VALENCE_w": vs.NODE_COLORS["VALENCE"],
            "CHALLENGE_w": vs.NODE_COLORS["CHALLENGE"], "EFFIC_w": vs.NODE_COLORS["EFFIC"]}

    fig, ax = plt.subplots(2, 3, figsize=(15.6, 9.2))

    # A: alone versus jointly, for pain intensity
    a = ax[0, 0]
    alone = dec[(dec["model"] == "entered alone") & (dec["outcome"] == "PIJN")].set_index("term")
    joint = dec[(dec["model"] == "all four together") & (dec["outcome"] == "PIJN")].set_index("term")
    y = np.arange(len(TERMS))[::-1]
    for yy, t in zip(y, TERMS):
        e0, e1 = alone.loc[t, "estimate"], joint.loc[t, "estimate"]
        a.annotate("", xy=(e1, yy), xytext=(e0, yy),
                   arrowprops={"arrowstyle": "-|>", "color": TCOL[t], "lw": 2.0,
                               "shrinkA": 0, "shrinkB": 0})
        a.plot(e0, yy, "o", ms=6, mfc="white", mec=TCOL[t], mew=1.8, zorder=3)
        a.plot(e1, yy, "o", ms=6, color=TCOL[t], zorder=3)
    a.axvline(0, color=vs.INK, lw=0.9, ls="--")
    fe = alone.loc["FLOWEXP_w", "estimate"]
    a.axvline(fe, color=FLOW, lw=1.4, ls=":")
    a.text(fe + 0.002, -0.55, f"composite\nalone {fe:.3f}", ha="left", va="center",
           fontsize=7.5, color=FLOW)
    a.set_yticks(y); a.set_yticklabels([TLAB[t] for t in TERMS], fontsize=9)
    a.set_ylim(-0.7, len(TERMS) - 0.25)
    a.set_xlabel("Effect on momentary pain intensity")
    a.set_title("Alone (hollow) versus jointly (filled)")
    a.grid(axis="x", visible=True); a.grid(axis="y", visible=False)
    a.legend(handles=[Line2D([], [], marker="o", ls="", mfc="white", mec=vs.MUTED, mew=1.6,
                             label="entered alone"),
                      Line2D([], [], marker="o", ls="", color=vs.MUTED,
                             label="entered jointly")], fontsize=7.5, loc="lower right")
    vs.panel_label(a, "A")

    # B: joint coefficients across all four pain outcomes
    a = ax[0, 1]
    x = np.arange(len(OUT)); w = 0.2
    for k, t in enumerate(TERMS):
        sub = dec[(dec["model"] == "all four together") & (dec["term"] == t)].set_index("outcome")
        vals = [sub.loc[o, "estimate"] for o in OUT]
        errs = [1.96 * sub.loc[o, "SE"] for o in OUT]
        a.bar(x + (k - 1.5) * w, vals, w, color=TCOL[t], edgecolor="white", label=TLAB[t],
              yerr=errs, capsize=1.8, error_kw={"lw": 0.8, "ecolor": vs.INK})
    a.axhline(0, color=vs.INK, lw=0.9)
    a.set_xticks(x); a.set_xticklabels([OUT_LAB[o].replace(" ", "\n") for o in OUT],
                                       fontsize=8)
    a.set_ylabel("Effect entered jointly")
    a.set_title("Challenge opposes the other three, everywhere")
    a.legend(fontsize=7.5, ncol=2); vs.bar_axes(a); vs.panel_label(a, "B")

    # C: how much each constituent moves when the others enter
    a = ax[0, 2]
    delta = np.zeros((len(TERMS), len(OUT)))
    for i, t in enumerate(TERMS):
        for j, o in enumerate(OUT):
            e0 = dec[(dec["model"] == "entered alone") & (dec["term"] == t) &
                     (dec["outcome"] == o)]["estimate"].iloc[0]
            e1 = dec[(dec["model"] == "all four together") & (dec["term"] == t) &
                     (dec["outcome"] == o)]["estimate"].iloc[0]
            delta[i, j] = e1 - e0
    im = a.imshow(delta, cmap="RdBu_r", vmin=-0.06, vmax=0.06, aspect="auto")
    a.set_xticks(range(len(OUT)))
    a.set_xticklabels([OUT_LAB[o].replace(" ", "\n") for o in OUT], fontsize=7.5)
    a.set_yticks(range(len(TERMS))); a.set_yticklabels([TLAB[t] for t in TERMS], fontsize=8.5)
    for i in range(len(TERMS)):
        for j in range(len(OUT)):
            a.text(j, i, f"{delta[i, j]:+.3f}", ha="center", va="center", fontsize=7.5,
                   color=vs.INK if abs(delta[i, j]) < 0.045 else "white")
    a.set_title("Change from alone to jointly (suppression)")
    vs.matrix_axes(a); vs.add_cbar(fig, a, im, label=r"$\Delta b$"); vs.panel_label(a, "C")

    # D: nested likelihood-ratio tests of the composite
    a = ax[1, 0]
    q = "Do the four constituents improve on the composite?"
    q2 = "Does splitting the composite into absorption and enjoyment improve fit?"
    sub1 = lrt[lrt["question"] == q].set_index("outcome").loc[OUT]
    sub2 = lrt[lrt["question"] == q2].set_index("outcome").loc[OUT]
    x = np.arange(len(OUT)); w = 0.36
    a.bar(x - w / 2, sub2["delta_AIC"].values, w, color=GREY, edgecolor="white",
          label="Split the composite in two")
    a.bar(x + w / 2, sub1["delta_AIC"].values, w, color=FLOW, edgecolor="white",
          label="Use all four constituents")
    a.axhline(0, color=vs.INK, lw=0.9)
    for xi, (v, p) in enumerate(zip(sub1["delta_AIC"], sub1["p"])):
        pt = "$p$ < .001" if p < .001 else f"$p$ = {p:.3f}".replace("0.", ".")
        a.text(xi + w / 2, v + 0.9, pt, ha="center", fontsize=7, color=vs.MUTED)
    a.set_xticks(x); a.set_xticklabels([OUT_LAB[o].replace(" ", "\n") for o in OUT],
                                       fontsize=8)
    a.set_ylim(min(-3.5, sub2["delta_AIC"].min() - 1.5), sub1["delta_AIC"].max() * 1.22)
    a.set_ylabel("AIC gained over the composite")
    a.set_title("The composite loses information about pain")
    a.legend(fontsize=7.5); vs.bar_axes(a); vs.panel_label(a, "D")

    # E: why suppression happens, the within-person correlations among constituents
    a = ax[1, 1]
    vl = ITEMS
    wi = corr[corr["level"] == "within"].set_index("variable")[vl].loc[vl].values.copy()
    np.fill_diagonal(wi, np.nan)
    im = a.imshow(wi, cmap="RdBu_r", vmin=-1, vmax=1)
    a.set_xticks(range(len(vl))); a.set_yticks(range(len(vl)))
    a.set_xticklabels([ITEM_LAB[v] for v in vl], rotation=30, ha="right", fontsize=8)
    a.set_yticklabels([ITEM_LAB[v] for v in vl], fontsize=8)
    for i in range(len(vl)):
        for j in range(len(vl)):
            if np.isfinite(wi[i, j]):
                a.text(j, i, f"{wi[i, j]:.2f}", ha="center", va="center", fontsize=8,
                       color=vs.INK if abs(wi[i, j]) < 0.6 else "white")
    a.set_title("Constituents co-vary within persons")
    vs.matrix_axes(a); vs.add_cbar(fig, a, im, label="within-person r")
    vs.panel_label(a, "E")

    # F: network substitution, every parameter of the benchmark against the composite
    a = ax[1, 2]
    bt = net_t.set_index(["from", "to"])
    ft = flw_t.copy()
    ft["from"] = ft["from"].replace({"FLOWEXP": "ENGAGE"})
    ft["to"] = ft["to"].replace({"FLOWEXP": "ENGAGE"})
    ft = ft.set_index(["from", "to"])
    common = [i for i in bt.index if i in ft.index]
    xb = np.array([bt.loc[i, "weight"] for i in common])
    yb = np.array([ft.loc[i, "weight"] for i in common])
    touched = np.array([("ENGAGE" in i) for i in common])
    bc = net_c.set_index(["node1", "node2"])
    fc = flw_c.copy()
    fc["node1"] = fc["node1"].replace({"FLOWEXP": "ENGAGE"})
    fc["node2"] = fc["node2"].replace({"FLOWEXP": "ENGAGE"})
    fc = fc.set_index(["node1", "node2"])
    cc = [i for i in bc.index if i in fc.index]
    xc = np.array([bc.loc[i, "pcor"] for i in cc])
    yc = np.array([fc.loc[i, "pcor"] for i in cc])
    tc = np.array([("ENGAGE" in i) for i in cc])
    lim = (-0.12, 0.42)
    a.plot(lim, lim, color=vs.MUTED, lw=1.0, ls="--", zorder=1)
    a.scatter(xb[~touched], yb[~touched], s=42, color=GREY, edgecolor="white", zorder=3,
              label="Temporal, node untouched")
    a.scatter(xb[touched], yb[touched], s=52, color=FLOW, edgecolor="white", zorder=4,
              label="Temporal, substituted node")
    a.scatter(xc[~tc], yc[~tc], s=42, marker="s", color=GREY, edgecolor="white", zorder=3,
              label="Contemporaneous, untouched")
    a.scatter(xc[tc], yc[tc], s=52, marker="s", color=FLOW, edgecolor="white", zorder=4,
              label="Contemporaneous, substituted")
    r = np.corrcoef(np.r_[xb, xc], np.r_[yb, yc])[0, 1]
    mx = np.abs(cmp["difference"]).max()
    a.text(0.03, 0.97, f"r = {r:.3f} over {len(xb) + len(xc)} parameters\n"
           f"largest edge change = {mx:.3f}\nno sign or significance change",
           transform=a.transAxes, va="top", fontsize=8, color=vs.MUTED)
    a.set_xlim(lim); a.set_ylim(lim)
    a.set_xlabel("Benchmark network (absorption node)")
    a.set_ylabel("Network with the flow composite")
    a.set_title("Substituting the composite changes nothing")
    a.legend(fontsize=6.8, loc="lower right"); vs.panel_label(a, "F")

    fig.tight_layout(h_pad=2.8, w_pad=2.8)
    vs.savefig(fig, FIG / "MAIN_03_constituent_decomposition.png")


# ---------------------------------------------------------------------------
# MAIN_04 - Flow and the momentary experience of pain
# ---------------------------------------------------------------------------
def main_04():
    con = pd.read_csv(T / "12_flow_pain_contemporaneous.csv")
    lag = pd.read_csv(T / "12_flow_pain_lagged.csv")
    per = pd.read_csv(T / "12_flow_perperson_slopes.csv")
    sens = pd.read_csv(T / "12_flow_compliance_sensitivity.csv")

    fig, ax = plt.subplots(2, 3, figsize=(15.6, 9.2))

    # A: concurrent associations, unadjusted and activity-adjusted
    a = ax[0, 0]
    y = np.arange(len(OUT))[::-1]
    for shift, mdl, colr, lab in [(0.17, "base", GREY, "Unadjusted"),
                                  (-0.17, "activity-adjusted", FLOW, "Activity-adjusted")]:
        sub = con[(con["model"] == mdl) & (con["term"] == "FLOWEXP_w")].set_index("outcome")
        est = np.array([sub.loc[o, "estimate"] for o in OUT])
        se = np.array([sub.loc[o, "SE"] for o in OUT])
        a.errorbar(est, y + shift, xerr=1.96 * se, fmt="o", ms=5.5, color=colr, ecolor=colr,
                   elinewidth=2.2, capsize=2.5, label=lab)
    a.axvline(0, color=vs.INK, lw=0.9, ls="--")
    a.set_yticks(y); a.set_yticklabels([OUT_LAB[o] for o in OUT], fontsize=8.5)
    a.set_xlabel("Effect of the flow experience (95% CI)")
    a.set_title("Same beep: interference moves most")
    a.legend(fontsize=8, loc="upper left")
    a.grid(axis="x", visible=True); a.grid(axis="y", visible=False)
    vs.panel_label(a, "A")

    # B: every lag-1 path, with the autoregressions as the power check
    a = ax[0, 1]
    fw = lag[(lag["model"] == "flow(t-1) -> outcome(t)") &
             (lag["term"] == "FLOWEXP_lag")].copy()
    fw["label"] = "Flow $\\rightarrow$ " + fw["outcome"].map(OUT_LAB)
    rv = lag[lag["model"] == "predictor(t-1) -> flow(t)"].copy()
    rv = rv[rv["term"] == rv["outcome"] + "_lag"]
    rv["label"] = rv["outcome"].map(OUT_LAB) + " $\\rightarrow$ flow"
    ar = lag[(lag["model"] == "flow(t-1) -> outcome(t)") &
             (lag["term"] == lag["outcome"] + "_lag")].copy()
    ar["label"] = ar["outcome"].map(OUT_LAB) + " autoregression"
    lg = pd.concat([fw, rv, ar], ignore_index=True)
    cols = ([FLOW] * len(fw) + [vs.NODE_COLORS["PIJN"]] * len(rv) + [vs.INK] * len(ar))
    y = np.arange(len(lg))[::-1]
    for yy, e, se, c in zip(y, lg["estimate"], lg["SE"], cols):
        a.hlines(yy, e - 1.96 * se, e + 1.96 * se, color=c, lw=2.2)
        a.plot(e, yy, "o", ms=4.6, color=vs.INK, zorder=3)
    a.axvline(0, color=vs.INK, lw=0.9, ls="--")
    a.axhline(len(ar) - 0.5, color=vs.MUTED, lw=0.8, ls=":")
    a.set_yticks(y); a.set_yticklabels(lg["label"], fontsize=7.5)
    a.set_xlabel("Lag-1 effect, standardized (95% CI)")
    a.set_title("Nothing carries over, yet the model sees time")
    vs.panel_label(a, "B")

    # C: person-specific concurrent slopes
    a = ax[0, 2]
    pp = per.dropna(subset=["b_contemp"]).sort_values("b_contemp").reset_index(drop=True)
    y = np.arange(len(pp))
    sneg, spos = pp["hi_contemp"] < 0, pp["lo_contemp"] > 0
    cols = np.where(sneg, FLOW, np.where(spos, vs.NODE_COLORS["PIJN"], GREY))
    a.hlines(y, pp["lo_contemp"], pp["hi_contemp"], color=cols, lw=1.5)
    a.plot(pp["b_contemp"], y, "o", ms=2.8, color=vs.INK)
    a.axvline(0, color=vs.INK, lw=0.9, ls="--")
    a.axvline(pp["b_contemp"].median(), color=FLOW, lw=1.3, ls=":")
    a.text(0.02, 0.97, f"median $b$ = {pp['b_contemp'].median():.2f}\n"
           f"{int(sneg.sum())} of {len(pp)} reliably negative\n"
           f"{int(spos.sum())} reliably positive",
           transform=a.transAxes, va="top", fontsize=8, color=vs.MUTED)
    a.set_yticks([]); a.set_ylabel("Participants, ordered")
    a.set_xlabel("Person-specific concurrent slope (95% CI)")
    a.set_title("Same beep, person by person")
    vs.panel_label(a, "C")

    # D: person-specific lag-1 slopes
    a = ax[1, 0]
    pl = per.dropna(subset=["b_lagged"]).sort_values("b_lagged").reset_index(drop=True)
    y = np.arange(len(pl))
    sn, sp = pl["hi_lagged"] < 0, pl["lo_lagged"] > 0
    cols = np.where(sn, FLOW, np.where(sp, vs.NODE_COLORS["PIJN"], GREY))
    a.hlines(y, pl["lo_lagged"], pl["hi_lagged"], color=cols, lw=1.5)
    a.plot(pl["b_lagged"], y, "o", ms=2.8, color=vs.INK)
    a.axvline(0, color=vs.INK, lw=0.9, ls="--")
    a.text(0.02, 0.97, f"median $b$ = {pl['b_lagged'].median():.2f}\n"
           f"{int(sn.sum())} reliably negative\n{int(sp.sum())} reliably positive",
           transform=a.transAxes, va="top", fontsize=8, color=vs.MUTED)
    a.set_yticks([]); a.set_ylabel("Participants, ordered")
    a.set_xlabel("Person-specific lag-1 slope (95% CI)")
    a.set_title("Lag 1, person by person")
    vs.panel_label(a, "D")

    # E: the two person-level distributions overlaid
    a = ax[1, 1]
    bins = np.linspace(-0.5, 0.5, 21)
    a.hist(pp["b_contemp"], bins=bins, color=FLOW, alpha=0.6, edgecolor="white",
           label="Same beep")
    a.hist(pl["b_lagged"], bins=bins, color=vs.MUTED, alpha=0.6, edgecolor="white",
           label="Lag 1")
    a.axvline(0, color=vs.INK, lw=1.1, ls="--")
    a.set_xlabel("Person-specific slope"); a.set_ylabel("Participants")
    a.set_title("Concurrent is shifted, lagged is centred")
    a.legend(fontsize=8); vs.bar_axes(a); vs.panel_label(a, "E")

    # F: compliance-threshold sensitivity
    a = ax[1, 2]
    x = np.arange(len(sens))
    a.errorbar(x, sens["estimate"], yerr=1.96 * sens["SE"], fmt="o-", ms=6, lw=1.8,
               color=FLOW, ecolor=FLOW, capsize=3.5)
    a.axhline(0, color=vs.INK, lw=0.9, ls="--")
    a.set_xticks(x)
    a.set_xticklabels([f"$\\geq${int(t)}\n{int(n)} persons\n{int(m):,} moments"
                       for t, n, m in zip(sens["threshold"], sens["n_persons"],
                                          sens["n_moments"])], fontsize=7.5)
    a.set_xlabel("Compliance floor (completed moments per person)")
    a.set_ylabel("Flow effect on pain intensity")
    a.set_title("Stable across every compliance floor")
    vs.bar_axes(a); vs.panel_label(a, "F")

    fig.tight_layout(h_pad=2.8, w_pad=2.8)
    vs.savefig(fig, FIG / "MAIN_04_flow_and_pain.png")


# ---------------------------------------------------------------------------
# MAIN_05 - The challenge-skill plane and where pain is lowest
# ---------------------------------------------------------------------------
def main_05():
    f = frame()
    chan_ap = pd.read_csv(T / "12_flow_channel_contrasts.csv")
    chan_fl = pd.read_csv(T / "12_flow_channel_contrasts_flowref.csv")
    prof = pd.read_csv(T / "12_flow_channel_profiles.csv")
    dec = pd.read_csv(T / "12_flow_component_decomposition.csv")

    fig, ax = plt.subplots(2, 3, figsize=(15.6, 9.2))

    def surface(a, value, cmap, label, title):
        grid = np.full((7, 7), np.nan)
        for (ch, sk), gr in f.groupby(["CHALLENGE", "EFFIC"]):
            if len(gr) >= 15 and np.isfinite(gr[value]).sum() >= 10:
                grid[int(sk) - 1, int(ch) - 1] = gr[value].mean()
        im = a.imshow(grid, origin="lower", cmap=cmap, extent=(0.5, 7.5, 0.5, 7.5),
                      aspect="auto")
        mid = np.nanmean(grid)
        for si in range(7):
            for ci in range(7):
                if np.isfinite(grid[si, ci]):
                    a.text(ci + 1, si + 1, f"{grid[si, ci]:.1f}", ha="center", va="center",
                           fontsize=6.5,
                           color=vs.INK if grid[si, ci] < mid else "white")
        a.axvline(4.5, color=vs.INK, lw=1.0, ls="--")
        a.axhline(4.5, color=vs.INK, lw=1.0, ls="--")
        box = {"facecolor": "white", "alpha": 0.85, "edgecolor": "none", "pad": 1.6}
        for fx, fy, ha_, va_, name in [(0.985, 0.985, "right", "top", "Flow"),
                                       (0.985, 0.015, "right", "bottom", "Anxiety"),
                                       (0.015, 0.985, "left", "top", "Relaxation"),
                                       (0.015, 0.015, "left", "bottom", "Apathy")]:
            a.text(fx, fy, name, transform=a.transAxes, fontsize=8, ha=ha_, va=va_,
                   color=vs.CHANNEL_COLORS[name], bbox=box, zorder=5,
                   fontweight="bold" if name in ("Flow", "Relaxation") else "normal")
        a.set_xticks(range(1, 8)); a.set_yticks(range(1, 8))
        a.set_xlabel("Challenge (1 to 7)"); a.set_ylabel("Skill (1 to 7)")
        a.set_title(title); a.grid(False)
        vs.add_cbar(fig, a, im, label=label)

    surface(ax[0, 0], "FLOWEXP", "YlGnBu", "Mean flow experience",
            "The flow experience rises with both")
    vs.panel_label(ax[0, 0], "A")
    surface(ax[0, 1], "PIJN", "OrRd", "Mean pain intensity",
            "Pain is lowest at low challenge, high skill")
    vs.panel_label(ax[0, 1], "B")
    surface(ax[0, 2], "PIJN_AFF", "OrRd", "Mean pain interference",
            "Interference follows the same gradient")
    vs.panel_label(ax[0, 2], "C")

    # D: channel contrasts against apathy
    a = ax[1, 0]
    ch = chan_ap[chan_ap["term"].str.startswith("chan")].copy()
    ch["channel"] = ch["term"].str.replace("chan", "", regex=False)
    x = np.arange(len(OUT)); w = 0.26
    for k, name in enumerate(["Flow", "Relaxation", "Anxiety"]):
        sub = ch[ch["channel"] == name].set_index("outcome")
        a.bar(x + (k - 1) * w, [sub.loc[o, "estimate"] for o in OUT], w,
              color=vs.CHANNEL_COLORS[name], edgecolor="white", label=name,
              yerr=[1.96 * sub.loc[o, "SE"] for o in OUT], capsize=1.8,
              error_kw={"lw": 0.8, "ecolor": vs.INK})
    a.axhline(0, color=vs.INK, lw=0.9)
    a.set_xticks(x); a.set_xticklabels([OUT_LAB[o].replace(" ", "\n") for o in OUT],
                                       fontsize=8)
    a.set_ylabel("Difference from apathy")
    a.set_title("Every channel against apathy")
    a.legend(fontsize=8); vs.bar_axes(a); vs.panel_label(a, "D")

    # E: the head-to-head test, every channel against flow
    a = ax[1, 1]
    cf = chan_fl[chan_fl["term"].str.startswith("chan_flowref")].copy()
    cf["channel"] = cf["term"].str.replace("chan_flowref", "", regex=False)
    labels, est, lo, hi, cols = [], [], [], [], []
    for o in OUT:
        for name in ["Relaxation", "Anxiety", "Apathy"]:
            r = cf[(cf["outcome"] == o) & (cf["channel"] == name)].iloc[0]
            labels.append(f"{OUT_LAB[o]}: {name}")
            est.append(r["estimate"]); lo.append(r["lo"]); hi.append(r["hi"])
            cols.append(vs.CHANNEL_COLORS[name] if r["p"] < .05 else GREY)
    _forest(a, labels, est, lo, hi, cols, "Difference from the flow channel (95% CI)",
            "Relaxation is the only channel that beats flow", ms=4.4)
    a.tick_params(axis="y", labelsize=6.8)
    vs.panel_label(a, "F" if False else "E")

    # F: the monotone marginals that explain the surface
    a = ax[1, 2]
    for item, col, lab in [("CHALLENGE", vs.NODE_COLORS["CHALLENGE"], "Challenge"),
                           ("EFFIC", vs.NODE_COLORS["EFFIC"], "Skill")]:
        g = f.groupby(item)["PIJN_w"].agg(["mean", "sem", "size"])
        g = g[g["size"] >= 40]
        a.errorbar(g.index, g["mean"], yerr=1.96 * g["sem"], marker="o", ms=6, lw=2.0,
                   color=col, capsize=3, label=lab)
    a.axhline(0, color=vs.INK, lw=0.9, ls="--")
    alone = dec[(dec["model"] == "entered alone") & (dec["outcome"] == "PIJN")].set_index("term")
    joint = dec[(dec["model"] == "all four together") & (dec["outcome"] == "PIJN")].set_index("term")
    a.text(0.03, 0.04,
           "within persons, challenge $b$ = "
           f"{alone.loc['CHALLENGE_w', 'estimate']:+.3f} alone, "
           f"{joint.loc['CHALLENGE_w', 'estimate']:+.3f} jointly\n"
           "within persons, skill $b$ = "
           f"{alone.loc['EFFIC_w', 'estimate']:+.3f} alone, "
           f"{joint.loc['EFFIC_w', 'estimate']:+.3f} jointly",
           transform=a.transAxes, fontsize=7.5, color=vs.MUTED)
    a.set_xticks(range(1, 8))
    a.set_xlabel("Item response (1 to 7)")
    a.set_ylabel("Person-centred momentary pain intensity")
    a.set_title("Skill tracks less pain, challenge does not")
    a.legend(fontsize=8); vs.panel_label(a, "F")

    fig.tight_layout(h_pad=2.8, w_pad=2.8)
    vs.savefig(fig, FIG / "MAIN_05_challenge_skill_plane.png")


def main():
    np.random.seed(20260703)
    main_01(); main_02(); main_03(); main_04(); main_05()
    print("flow main figures written to", FIG)


if __name__ == "__main__":
    main()
