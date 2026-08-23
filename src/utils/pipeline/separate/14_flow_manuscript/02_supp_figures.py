"""Stage 14.2 - Supplementary figures for manuscript 02 (the flow construct study)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

LIB = Path(__file__).resolve().parents[3] / "lib"
sys.path.insert(0, str(LIB))
import paths  # noqa: E402
import vizstyle as vs  # noqa: E402

vs.apply_style()
T = paths.RESULTS_TABLES
N = paths.RESULTS_NETWORKS
M = paths.RESULTS_MODELS
FIG = paths.FLOW_FIG_SUPP
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
RULES = ["A_abs4", "A_abs5", "B_grandz", "C_withinz", "D_center"]
RULE_SHORT = {"A_abs4": "A raw $\\geq$ 4", "A_abs5": "A raw $\\geq$ 5",
              "B_grandz": "B grand-mean z", "C_withinz": "C within-person z",
              "D_center": "D person-centred"}


def frame():
    return pd.read_csv(M / "12_flow_analytic_frame.csv")


# ---------------------------------------------------------------------------
# SUP_01 - The analytic frame
# ---------------------------------------------------------------------------
def sup_01():
    f = frame()
    miss = pd.read_csv(T / "12_flow_missingness.csv")
    desc = pd.read_csv(T / "12_flow_item_descriptives.csv")

    fig, ax = plt.subplots(2, 3, figsize=(15.6, 8.8))

    a = ax[0, 0]
    n = f.groupby("pid").size()
    a.hist(n, bins=np.arange(20, 125, 5), color=FLOW, edgecolor="white")
    a.axvline(n.median(), color=vs.NODE_COLORS["PIJN"], lw=1.6)
    a.text(n.median() - 2, a.get_ylim()[1] * 0.94, f"median = {n.median():.0f}",
           ha="right", fontsize=8, color=vs.NODE_COLORS["PIJN"])
    a.set_xlabel("Moments with all four appraisals answered")
    a.set_ylabel("Participants")
    a.set_title("Series length in the flow analytic frame")
    vs.bar_axes(a); vs.panel_label(a, "A")

    a = ax[0, 1]
    dd = desc.set_index("variable")
    x = np.arange(len(ITEMS))
    a.bar(x, [dd.loc[i, "mean"] for i in ITEMS],
          yerr=[dd.loc[i, "sd"] for i in ITEMS], capsize=4,
          color=[vs.NODE_COLORS[i] for i in ITEMS], edgecolor="white",
          error_kw={"lw": 1.1, "ecolor": vs.INK})
    a.axhline(4, color=vs.INK, ls="--", lw=1.0)
    a.set_xticks(x); a.set_xticklabels([ITEM_LAB[i] for i in ITEMS], fontsize=8.5)
    a.set_ylim(0, 7.4); a.set_ylabel("Mean response (SD)")
    a.set_title("Item means against the scale midpoint")
    vs.bar_axes(a); vs.panel_label(a, "B")

    a = ax[0, 2]
    x = np.arange(len(ITEMS))
    a.bar(x, [dd.loc[i, "icc_person"] for i in ITEMS],
          color=[vs.NODE_COLORS[i] for i in ITEMS], edgecolor="white")
    for xi, i in enumerate(ITEMS):
        a.text(xi, dd.loc[i, "icc_person"] + 0.008, f"{dd.loc[i, 'icc_person']:.2f}",
               ha="center", fontsize=8)
    a.set_xticks(x); a.set_xticklabels([ITEM_LAB[i] for i in ITEMS], fontsize=8.5)
    a.set_ylim(0, 0.34); a.set_ylabel("ICC (between-person share)")
    a.set_title("Little of the variance is between persons")
    vs.bar_axes(a); vs.panel_label(a, "C")

    a = ax[1, 0]
    mm = miss.copy()
    lab = {**OUT_LAB, "NEGAFF": "Negative affect", "POSAFF": "Positive affect",
           "ACTIEF": "Physical activation"}
    mm["label"] = mm["variable"].map(lab).fillna(mm["variable"])
    mm = mm.sort_values("cohens_d")
    y = np.arange(len(mm))
    cols = [vs.NODE_COLORS["PIJN"] if p < .05 else GREY for p in mm["p"]]
    a.barh(y, mm["cohens_d"], color=cols, edgecolor="white")
    a.axvline(0, color=vs.INK, lw=1.0)
    a.set_yticks(y); a.set_yticklabels(mm["label"], fontsize=8)
    a.set_xlabel("Cohen's $d$, dropped minus retained moments")
    a.set_title(f"Listwise loss is {mm['pct_dropped'].iloc[0]:.1f}% and mildly selective")
    vs.bar_axes(a, "horizontal"); vs.panel_label(a, "D")

    a = ax[1, 1]
    keep_beep = f["beep"].value_counts()
    keep_beep = sorted(keep_beep[keep_beep >= 150].index)
    by_beep = f[f["beep"].isin(keep_beep)].groupby("beep")[
        ["FLOWEXP", "CHALLENGE", "EFFIC"]].mean()
    for c, col in [("FLOWEXP", FLOW), ("CHALLENGE", vs.NODE_COLORS["CHALLENGE"]),
                   ("EFFIC", vs.NODE_COLORS["EFFIC"])]:
        a.plot(by_beep.index, by_beep[c], "o-", ms=5, lw=1.8, color=col,
               label=ITEM_LAB[c])
    a.set_xlabel("Prompt position within the day")
    a.set_ylabel("Mean response")
    a.set_title("Time of day shifts the level, not the model")
    a.legend(fontsize=8); vs.panel_label(a, "E")

    a = ax[1, 2]
    by_day = f.groupby("day")[["FLOWEXP", "PIJN"]].mean()
    a.plot(by_day.index, by_day["FLOWEXP"], "o-", ms=5, lw=1.8, color=FLOW,
           label="Flow experience")
    a.plot(by_day.index, by_day["PIJN"], "s-", ms=5, lw=1.8,
           color=vs.NODE_COLORS["PIJN"], label="Pain intensity")
    a.set_xlabel("Study day")
    a.set_ylabel("Mean response")
    a.set_title("Day-to-day variation without a trend")
    a.legend(fontsize=8); vs.panel_label(a, "F")

    fig.tight_layout(h_pad=2.8, w_pad=2.8)
    vs.savefig(fig, FIG / "SUP_01_analytic_frame.png")


# ---------------------------------------------------------------------------
# SUP_02 - How the standardization rule decides everything descriptive
# ---------------------------------------------------------------------------
def sup_02():
    f = frame()
    prev = pd.read_csv(T / "12_flow_prevalence_by_rule.csv")
    prof = pd.read_csv(T / "12_flow_channel_profiles.csv")
    sens = pd.read_csv(T / "12_flow_standardization_sensitivity.csv")

    fig, ax = plt.subplots(2, 3, figsize=(15.6, 8.8))

    a = ax[0, 0]
    pv = prev.set_index("rule").loc[RULES]
    x = np.arange(len(RULES))
    a.bar(x, 100 * pv["person_median"], color=FLOW, edgecolor="white")
    for xi, (lo, hi) in enumerate(zip(pv["person_min"], pv["person_max"])):
        a.vlines(xi, 100 * lo, 100 * hi, color=vs.INK, lw=1.4)
    a.set_xticks(x)
    a.set_xticklabels([RULE_SHORT[r].replace(" ", "\n") for r in RULES], fontsize=7.5)
    a.set_ylabel("% of a person's moments in flow")
    a.set_title("Median participant, with the full range")
    vs.bar_axes(a); vs.panel_label(a, "A")

    a = ax[0, 1]
    bottom = np.zeros(len(RULES))
    for name in vs.CHANNEL_ORDER:
        vals = np.array([100 * prof[(prof["rule"] == r) & (prof["channel"] == name)]
                         ["share"].iloc[0] for r in RULES])
        a.bar(np.arange(len(RULES)), vals, bottom=bottom,
              color=vs.CHANNEL_COLORS[name], edgecolor="white", label=name)
        for xi, (v, b) in enumerate(zip(vals, bottom)):
            if v > 6:
                a.text(xi, b + v / 2, f"{v:.0f}", ha="center", va="center", fontsize=7.5,
                       color="white")
        bottom += vals
    a.set_xticks(np.arange(len(RULES)))
    a.set_xticklabels([RULE_SHORT[r].replace(" ", "\n") for r in RULES], fontsize=7.5)
    a.set_ylim(0, 118)
    a.set_ylabel("% of moments")
    a.set_title("Channel composition under each rule")
    a.legend(fontsize=7.5, ncol=2); vs.bar_axes(a); vs.panel_label(a, "B")

    a = ax[0, 2]
    order = ["A_raw", "B_grandz", "C_withinz", "D_center"]
    lab = {"A_raw": "A raw", "B_grandz": "B grand z", "C_withinz": "C within z",
           "D_center": "D centred"}
    x = np.arange(len(order)); w = 0.36
    for k, (term, col) in enumerate([("Elevation", ELEV), ("Balance", BAL)]):
        sub = sens[sens["term"] == term].set_index("metric").loc[order]
        a.bar(x + (k - 0.5) * w, sub["estimate"], w, color=col, edgecolor="white",
              label=term, yerr=1.96 * sub["SE"], capsize=2.5,
              error_kw={"lw": 1.0, "ecolor": vs.INK})
        for xi, (e, se) in enumerate(zip(sub["estimate"], sub["SE"])):
            a.text(xi + (k - 0.5) * w, e + np.sign(e) * (1.96 * se + 0.03),
                   f"{e:+.2f}", ha="center",
                   va="bottom" if e >= 0 else "top", fontsize=7)
    a.axhline(0, color=vs.INK, lw=0.9)
    a.set_xticks(x); a.set_xticklabels([lab[k] for k in order], fontsize=8.5)
    a.set_ylim(-0.25, 1.05)
    a.set_ylabel("Effect on the flow experience")
    a.set_title("Condition terms on every metric")
    a.legend(fontsize=8); vs.bar_axes(a); vs.panel_label(a, "C")

    a = ax[1, 0]
    for r, col in zip(["A_abs5", "A_abs4"], [vs.CHANNEL_COLORS["Flow"], GREY]):
        pp = f.groupby("pid")[f"flow_gated_{r}"].mean().sort_values(ascending=False)
        a.plot(np.arange(len(pp)), 100 * pp.values, lw=2.0, color=col,
               label=RULE_SHORT[r])
    a.set_xlabel("Participants, ordered")
    a.set_ylabel("% of that person's moments in flow")
    a.set_title("Person-level prevalence under the absolute rules")
    a.legend(fontsize=8); vs.panel_label(a, "D")

    a = ax[1, 1]
    agree = np.zeros((len(RULES), len(RULES)))
    for i, r1 in enumerate(RULES):
        for j, r2 in enumerate(RULES):
            agree[i, j] = (f[f"flow_gated_{r1}"] == f[f"flow_gated_{r2}"]).mean()
    im = a.imshow(agree, cmap="YlGnBu", vmin=0.5, vmax=1.0)
    a.set_xticks(range(len(RULES))); a.set_yticks(range(len(RULES)))
    a.set_xticklabels([RULE_SHORT[r] for r in RULES], rotation=35, ha="right", fontsize=7)
    a.set_yticklabels([RULE_SHORT[r] for r in RULES], fontsize=7)
    for i in range(len(RULES)):
        for j in range(len(RULES)):
            a.text(j, i, f"{agree[i, j]:.2f}", ha="center", va="center", fontsize=7.5,
                   color=vs.INK if agree[i, j] < 0.85 else "white")
    a.set_title("Agreement on which moments are flow moments")
    vs.matrix_axes(a); vs.add_cbar(fig, a, im, label="share agreeing")
    vs.panel_label(a, "E")

    a = ax[1, 2]
    x = np.arange(len(RULES))
    a.bar(x, prev.set_index("rule").loc[RULES, "n_persons_zero"], color=vs.MUTED,
          edgecolor="white")
    for xi, v in enumerate(prev.set_index("rule").loc[RULES, "n_persons_zero"]):
        a.text(xi, v + 0.08, str(int(v)), ha="center", fontsize=9)
    a.set_xticks(x)
    a.set_xticklabels([RULE_SHORT[r].replace(" ", "\n") for r in RULES], fontsize=7.5)
    a.set_ylim(0, 5.2)
    a.set_ylabel("Participants who never reach flow")
    a.set_title("Only an absolute rule can represent absence")
    vs.bar_axes(a); vs.panel_label(a, "F")

    fig.tight_layout(h_pad=2.8, w_pad=2.8)
    vs.savefig(fig, FIG / "SUP_02_standardization.png")


# ---------------------------------------------------------------------------
# SUP_03 - Diagnostics of the balance parameterization
# ---------------------------------------------------------------------------
def sup_03():
    f = frame()
    nested = pd.read_csv(T / "12_flow_condition_nested_fixed.csv")
    simple = pd.read_csv(T / "12_flow_balance_simple_slopes.csv")
    diag = pd.read_csv(T / "12_flow_balance_diagnostics.csv")
    tests = pd.read_csv(T / "12_flow_structural_tests.csv")

    fig, ax = plt.subplots(2, 3, figsize=(15.6, 8.8))

    a = ax[0, 0]
    # Residuals of the additive within-person model. If the match between challenge and
    # skill carried variance, the residuals would form a ridge along the diagonal.
    add = nested[nested["model"] == "challenge + skill"].set_index("term")
    bc = add.loc["CHALLENGE_w", "estimate"]; bs = add.loc["EFFIC_w", "estimate"]
    g = f.dropna(subset=["FLOWEXP_w", "CHALLENGE_w", "EFFIC_w"]).copy()
    g["resid"] = g["FLOWEXP_w"] - (bc * g["CHALLENGE_w"] + bs * g["EFFIC_w"])
    grid = np.full((7, 7), np.nan)
    for (ch, sk), gr in g.groupby(["CHALLENGE", "EFFIC"]):
        if len(gr) >= 20:
            grid[int(sk) - 1, int(ch) - 1] = gr["resid"].mean()
    im = a.imshow(grid, origin="lower", cmap="RdBu_r", vmin=-0.6, vmax=0.6,
                  extent=(0.5, 7.5, 0.5, 7.5), aspect="auto")
    for si in range(7):
        for ci in range(7):
            if np.isfinite(grid[si, ci]):
                a.text(ci + 1, si + 1, f"{grid[si, ci]:+.2f}", ha="center", va="center",
                       fontsize=6.5,
                       color=vs.INK if abs(grid[si, ci]) < 0.42 else "white")
    a.plot([0.5, 7.5], [0.5, 7.5], color=vs.INK, lw=1.4, ls="--")
    a.set_xticks(range(1, 8)); a.set_yticks(range(1, 8))
    a.set_xlabel("Challenge (1 to 7)"); a.set_ylabel("Skill (1 to 7)")
    a.set_title("Additive-model residuals: no ridge on the diagonal")
    a.grid(False); vs.add_cbar(fig, a, im, label="mean residual")
    vs.panel_label(a, "A")

    a = ax[0, 1]
    surf = nested[nested["model"] == "quadratic response surface"]
    surf = surf[surf["term"] != "(Intercept)"]
    lab = {"CHALLENGE_w": "Challenge", "EFFIC_w": "Skill",
           "I(CHALLENGE_w^2)": "Challenge$^2$", "I(EFFIC_w^2)": "Skill$^2$",
           "CHALLENGE_w:EFFIC_w": "Challenge $\\times$ skill"}
    y = np.arange(len(surf))[::-1]
    cols = [vs.CHANNEL_COLORS["Flow"] if p < .05 else GREY for p in surf["p"]]
    for yy, (e, lo, hi, c) in zip(y, zip(surf["estimate"], surf["lo"], surf["hi"], cols)):
        a.hlines(yy, lo, hi, color=c, lw=2.4)
        a.plot(e, yy, "o", ms=5.5, color=vs.INK, zorder=3)
    a.axvline(0, color=vs.INK, lw=0.9, ls="--")
    a.set_yticks(y); a.set_yticklabels([lab[t] for t in surf["term"]], fontsize=8.5)
    a.set_xlabel("Effect on the flow experience (95% CI)")
    a.set_title("Only the linear terms carry the surface")
    a.grid(axis="x", visible=True); a.grid(axis="y", visible=False)
    vs.panel_label(a, "B")

    a = ax[0, 2]
    y = np.arange(len(simple))[::-1]
    cols = [BAL if p < .05 else GREY for p in simple["p"]]
    for yy, (e, lo, hi, c) in zip(y, zip(simple["estimate"], simple["lo"], simple["hi"],
                                         cols)):
        a.hlines(yy, lo, hi, color=c, lw=2.6)
        a.plot(e, yy, "o", ms=5.5, color=vs.INK, zorder=3)
    a.axvline(0, color=vs.INK, lw=0.9, ls="--")
    a.set_yticks(y); a.set_yticklabels(simple["elevation"], fontsize=9)
    a.set_xlabel("Balance effect (95% CI)")
    a.set_title("Balance only moves at high elevation, and barely")
    a.grid(axis="x", visible=True); a.grid(axis="y", visible=False)
    vs.panel_label(a, "C")

    a = ax[1, 0]
    f2 = f.dropna(subset=["CHALLENGE_w", "EFFIC_w", "FLOWEXP"]).copy()
    f2["absd"] = (f2["CHALLENGE_w"] - f2["EFFIC_w"]).abs()
    f2["ad_bin"] = pd.cut(f2["absd"], [-0.01, 0.5, 1.5, 2.5, 3.5, 12],
                          labels=["0 to 0.5", "0.5 to 1.5", "1.5 to 2.5", "2.5 to 3.5",
                                  "> 3.5"])
    f2["e_t"] = pd.qcut(f2["elevation_w"], 3, labels=["low", "middle", "high"])
    for name, col in zip(["low", "middle", "high"],
                         ["#9aa5b1", BAL, vs.CHANNEL_COLORS["Flow"]]):
        g = f2[f2["e_t"] == name].groupby("ad_bin", observed=True)["FLOWEXP"].agg(
            ["mean", "sem"])
        a.errorbar(np.arange(len(g)), g["mean"], yerr=1.96 * g["sem"], marker="o", ms=5,
                   lw=1.8, color=col, capsize=3, label=f"{name} elevation")
        a.set_xticks(np.arange(len(g)))
        a.set_xticklabels(g.index, fontsize=7.5, rotation=20)
    a.set_xlabel("Mismatch $|C_w - S_w|$ (person-centred)")
    a.set_ylabel("Mean flow experience")
    a.set_title("Person-centred metric, same picture")
    a.legend(fontsize=8); vs.panel_label(a, "D")

    a = ax[1, 1]
    tt = tests.copy()
    tt["short"] = ["+ balance", "+ one-sided kink", "+ interaction", "+ quadratic surface",
                   "+ four channels", "balance on surface", "balance $\\times$ elevation"]
    y = np.arange(len(tt))[::-1]
    cols = [vs.CHANNEL_COLORS["Flow"] if p < .05 else GREY for p in tt["p"]]
    a.barh(y, -np.log10(tt["p"]), color=cols, edgecolor="white", height=0.62)
    a.axvline(-np.log10(0.05), color=vs.NODE_COLORS["PIJN"], lw=1.2, ls="--")
    a.text(-np.log10(0.05) + 0.08, len(tt) - 0.6, "p = .05", fontsize=7.5,
           color=vs.NODE_COLORS["PIJN"])
    a.axhline(1.5, color=vs.MUTED, lw=0.9, ls=":")
    a.set_xlim(0, max(6.6, -np.log10(tt["p"]).max() * 1.35))
    box = {"facecolor": "white", "alpha": 0.9, "edgecolor": "none", "pad": 1.8}
    a.text(0.985, 0.11, "parameterization\ndiagnostics", transform=a.transAxes,
           ha="right", va="center", fontsize=7.5, color=vs.MUTED, bbox=box, zorder=6)
    a.text(0.985, 0.72, "tests of\nconfigurality", transform=a.transAxes, ha="right",
           va="center", fontsize=7.5, color=vs.MUTED, bbox=box, zorder=6)
    a.set_yticks(y); a.set_yticklabels(tt["short"], fontsize=8)
    a.set_xlabel(r"$-\log_{10} p$ against the stated baseline")
    a.set_title("Every nested test, on one scale")
    vs.bar_axes(a, "horizontal"); vs.panel_label(a, "E")

    a = ax[1, 2]
    grid = np.full((7, 7), np.nan)
    cnt = np.zeros((7, 7))
    for (ch, sk), gr in f.groupby(["CHALLENGE", "EFFIC"]):
        cnt[int(sk) - 1, int(ch) - 1] = len(gr)
    im = a.imshow(np.where(cnt > 0, cnt, np.nan), origin="lower", cmap="Purples",
                  extent=(0.5, 7.5, 0.5, 7.5), aspect="auto")
    for si in range(7):
        for ci in range(7):
            if cnt[si, ci] > 0:
                a.text(ci + 1, si + 1, f"{int(cnt[si, ci])}", ha="center", va="center",
                       fontsize=6.5,
                       color=vs.INK if cnt[si, ci] < cnt.max() * 0.55 else "white")
    a.plot([0.5, 7.5], [0.5, 7.5], color=vs.NODE_COLORS["PIJN"], lw=1.4, ls="--")
    a.set_xticks(range(1, 8)); a.set_yticks(range(1, 8))
    a.set_xlabel("Challenge (1 to 7)"); a.set_ylabel("Skill (1 to 7)")
    a.set_title("Moments per cell; the diagonal is thinly filled")
    a.grid(False); vs.add_cbar(fig, a, im, label="moments")
    vs.panel_label(a, "F")

    fig.tight_layout(h_pad=2.8, w_pad=2.8)
    vs.savefig(fig, FIG / "SUP_03_balance_diagnostics.png")


# ---------------------------------------------------------------------------
# SUP_04 - Temporal architecture of the construct
# ---------------------------------------------------------------------------
def sup_04():
    cl = pd.read_csv(T / "12_flow_condition_lagged.csv")
    lag = pd.read_csv(T / "12_flow_pain_lagged.csv")
    rnd = pd.read_csv(T / "12_flow_lagged_random_slopes.csv")
    nt = pd.read_csv(N / "12_flow_mlvar_temporal_edges.csv")
    nc = pd.read_csv(N / "12_flow_mlvar_contemporaneous_edges.csv")

    NLAB = {"PIJN": "Pain", "THREAT": "Threat", "ATTEND": "Attention",
            "FLOWEXP": "Flow exp."}
    fig, ax = plt.subplots(2, 3, figsize=(15.6, 8.8))

    a = ax[0, 0]
    same = cl[cl["model"] == "condition(t) -> experience(t), same rows"].set_index("term")
    lagm = cl[cl["model"] == "condition(t-1) -> experience(t)"].set_index("term")
    rows = [("elevation_zz", same, "Elevation, same beep", ELEV),
            ("elevation_zz_lag", lagm, "Elevation, lag 1", ELEV),
            ("balance_zz", same, "Balance, same beep", BAL),
            ("balance_zz_lag", lagm, "Balance, lag 1", BAL)]
    y = np.arange(len(rows))[::-1]
    for yy, (t, src, _, c) in zip(y, rows):
        e, se = src.loc[t, "estimate"], src.loc[t, "SE"]
        a.hlines(yy, e - 1.96 * se, e + 1.96 * se, color=c, lw=2.6)
        a.plot(e, yy, "o", ms=5.5, color=vs.INK, zorder=3)
    a.axvline(0, color=vs.INK, lw=0.9, ls="--")
    a.set_yticks(y); a.set_yticklabels([l for _, _, l, _ in rows], fontsize=8.5)
    a.set_xlabel("Effect on the flow experience (95% CI)")
    a.set_title("The condition precedes nothing")
    a.grid(axis="x", visible=True); a.grid(axis="y", visible=False)
    vs.panel_label(a, "A")

    a = ax[0, 1]
    e_same = same.loc["elevation_zz", "estimate"]
    e_lag = lagm.loc["elevation_zz_lag", "estimate"]
    a.bar([0, 1], [e_same, e_lag], color=[ELEV, GREY], edgecolor="white",
          yerr=[1.96 * same.loc["elevation_zz", "SE"],
                1.96 * lagm.loc["elevation_zz_lag", "SE"]], capsize=4,
          error_kw={"lw": 1.1, "ecolor": vs.INK})
    a.set_xticks([0, 1]); a.set_xticklabels(["Same beep", "Lag 1"], fontsize=9)
    a.text(1, e_lag + 0.09, f"{100 * e_lag / e_same:.0f}% of the\nsame-beep effect",
           ha="center", fontsize=8, color=vs.MUTED)
    a.set_ylim(0, 1.05)
    a.set_ylabel("Elevation effect on the flow experience")
    a.set_title("The elevation effect does not survive one prompt")
    vs.bar_axes(a); vs.panel_label(a, "B")

    a = ax[0, 2]
    rr = rnd.copy()
    rr["label"] = np.where(rr["direction"].str.startswith("flow"),
                           "Flow $\\rightarrow$ " + rr["outcome"].map(OUT_LAB),
                           rr["outcome"].map(OUT_LAB) + " $\\rightarrow$ flow")
    rr = rr.sort_values("random_SD")
    y = np.arange(len(rr))
    a.barh(y, rr["random_SD"], color=FLOW, edgecolor="white")
    a.set_yticks(y); a.set_yticklabels(rr["label"], fontsize=7.5)
    a.set_xlabel("Between-person SD of the lag-1 effect")
    a.set_title("Even the person-to-person spread is small")
    vs.bar_axes(a, "horizontal"); vs.panel_label(a, "C")

    a = ax[1, 0]
    ar = lag[(lag["model"] == "flow(t-1) -> outcome(t)") &
             (lag["term"] == lag["outcome"] + "_lag")]
    fl = lag[(lag["model"] == "flow(t-1) -> outcome(t)") &
             (lag["term"] == "FLOWEXP_lag")].set_index("outcome")
    x = np.arange(len(OUT)); w = 0.36
    a.bar(x - w / 2, [ar[ar["outcome"] == o]["estimate"].iloc[0] for o in OUT], w,
          color=vs.INK, edgecolor="white", label="Own autoregression")
    a.bar(x + w / 2, [abs(fl.loc[o, "estimate"]) for o in OUT], w, color=FLOW,
          edgecolor="white", label="|Flow at t-1|")
    a.set_xticks(x); a.set_xticklabels([OUT_LAB[o].replace(" ", "\n") for o in OUT],
                                       fontsize=8)
    a.set_ylabel("Lag-1 effect, standardized")
    a.set_title("The design detects time, just not flow")
    a.legend(fontsize=8); vs.bar_axes(a); vs.panel_label(a, "D")

    a = ax[1, 1]
    nodes = ["PIJN", "THREAT", "ATTEND", "FLOWEXP"]
    Mx = np.zeros((4, 4)); P = np.ones((4, 4))
    for _, r in nt.iterrows():
        Mx[nodes.index(r["to"]), nodes.index(r["from"])] = r["weight"]
        P[nodes.index(r["to"]), nodes.index(r["from"])] = r["P"]
    im = a.imshow(Mx, cmap="RdBu_r", vmin=-0.4, vmax=0.4)
    a.set_xticks(range(4)); a.set_yticks(range(4))
    a.set_xticklabels([NLAB[n] for n in nodes], fontsize=8, rotation=25, ha="right")
    a.set_yticklabels([NLAB[n] for n in nodes], fontsize=8)
    for i in range(4):
        for j in range(4):
            star = "*" if P[i, j] < .05 else ""
            a.text(j, i, f"{Mx[i, j]:.2f}{star}", ha="center", va="center", fontsize=7.5,
                   color=vs.INK if abs(Mx[i, j]) < 0.25 else "white")
    a.set_xlabel("From (t-1)"); a.set_ylabel("To (t)")
    a.set_title("Temporal network with the composite as a node")
    vs.matrix_axes(a, remove_axis_labels=False)
    vs.add_cbar(fig, a, im, label="lag-1 weight"); vs.panel_label(a, "E")

    a = ax[1, 2]
    y = np.arange(len(nc))[::-1]
    cols = [vs.CHANNEL_COLORS["Flow"] if p < .05 else GREY for p in nc["P"]]
    a.barh(y, nc["pcor"], color=cols, edgecolor="white")
    a.axvline(0, color=vs.INK, lw=1.0)
    a.set_yticks(y)
    a.set_yticklabels([f"{NLAB[a_]} - {NLAB[b_]}"
                       for a_, b_ in zip(nc["node1"], nc["node2"])], fontsize=8)
    a.set_xlabel("Partial correlation at the same beep")
    a.set_title("Contemporaneous network")
    vs.bar_axes(a, "horizontal"); vs.panel_label(a, "F")

    fig.tight_layout(h_pad=2.8, w_pad=2.8)
    vs.savefig(fig, FIG / "SUP_04_temporal_architecture.png")


# ---------------------------------------------------------------------------
# SUP_05 - Person level: proneness, coupling, and baseline profiles
# ---------------------------------------------------------------------------
def sup_05():
    link = pd.read_csv(T / "12_flow_trait_link.csv")
    inc = pd.read_csv(T / "12_flow_incremental_r2.csv")
    grp = pd.read_csv(T / "12_flow_coupling_groups.csv")
    per = pd.read_csv(T / "12_flow_perperson_slopes.csv")
    pf = pd.read_csv(T / "12_flow_person_prevalence.csv")

    ACC = ["Threat", "Biomedical", "Personality"]
    fig, ax = plt.subplots(2, 3, figsize=(15.6, 8.8))

    a = ax[0, 0]
    fv = ["Mean flow experience", "Flow proneness (strict)", "Mean challenge",
          "Mean skill", "Flow-pain coupling"]
    mat = np.full((len(fv), len(ACC)), np.nan)
    pmat = np.full((len(fv), len(ACC)), np.nan)
    for i, v in enumerate(fv):
        for j, acc in enumerate(ACC):
            r = link[(link["flow_variable"] == v) & (link["account"] == acc)]
            if len(r):
                mat[i, j] = r["partial_r"].iloc[0]
                pmat[i, j] = r["partial_p"].iloc[0]
    im = a.imshow(mat, cmap="RdBu_r", vmin=-0.5, vmax=0.5, aspect="auto")
    a.set_xticks(range(len(ACC))); a.set_xticklabels(ACC, fontsize=8.5)
    a.set_yticks(range(len(fv)))
    a.set_yticklabels([v.replace(" (strict)", "") for v in fv], fontsize=8)
    for i in range(len(fv)):
        for j in range(len(ACC)):
            if np.isfinite(mat[i, j]):
                star = "*" if pmat[i, j] < .05 else ""
                a.text(j, i, f"{mat[i, j]:.2f}{star}", ha="center", va="center",
                       fontsize=8, color=vs.INK if abs(mat[i, j]) < 0.35 else "white")
    a.set_title("Partial r with baseline profiles (mean pain controlled)")
    vs.matrix_axes(a); vs.add_cbar(fig, a, im, label="partial r"); vs.panel_label(a, "A")

    a = ax[0, 1]
    st = ["Pain intensity", "Pain interference", "Attention to pain", "Threat value"]
    sub = inc[inc["flow_variable"] == "Flow proneness (strict)"].set_index("state").loc[st]
    x = np.arange(len(st)); w = 0.36
    a.bar(x - w / 2, sub["R2_accounts"], w, color=vs.MUTED, edgecolor="white",
          label="Baseline profiles")
    a.bar(x + w / 2, sub["R2_accounts_plus_flow"], w, color=FLOW, edgecolor="white",
          label="+ flow proneness")
    for xi, d in enumerate(sub["delta_R2"]):
        a.text(xi + w / 2, sub["R2_accounts_plus_flow"].iloc[xi] + 0.012,
               f"$\\Delta$ = {d:.3f}", ha="center", fontsize=7.5, color=vs.MUTED)
    a.set_xticks(x); a.set_xticklabels([s.replace(" ", "\n") for s in st], fontsize=8)
    a.set_ylim(0, 0.55); a.set_ylabel(r"Explained variance ($R^2$)")
    a.set_title("Flow proneness adds most to mean pain")
    a.legend(fontsize=8); vs.bar_axes(a); vs.panel_label(a, "B")

    a = ax[0, 2]
    y = np.arange(len(grp))[::-1]
    cols = [FLOW if p < .05 else GREY for p in grp["p"]]
    a.barh(y, grp["cohens_d"], color=cols, edgecolor="white")
    a.axvline(0, color=vs.INK, lw=1.0)
    a.set_yticks(y); a.set_yticklabels(grp["variable"], fontsize=8)
    a.set_xlabel("Cohen's $d$, negative-coupling minus other participants")
    a.set_title("Who has a negative coupling")
    vs.bar_axes(a, "horizontal"); vs.panel_label(a, "C")

    a = ax[1, 0]
    m = per.merge(pf, on="pid", how="inner")
    a.scatter(m["mean_flowexp"], m["b_contemp"], s=34, color=FLOW, alpha=0.8,
              edgecolor="white", linewidth=0.5)
    a.axhline(0, color=vs.INK, lw=0.9, ls="--")
    r = np.corrcoef(m["mean_flowexp"], m["b_contemp"])[0, 1]
    a.set_xlabel("Mean flow experience")
    a.set_ylabel("Person-specific flow-pain slope")
    a.set_title(f"Level barely predicts coupling (r = {r:.2f})")
    vs.panel_label(a, "D")

    a = ax[1, 1]
    a.scatter(m["n"], m["b_contemp"], s=34, color=vs.MUTED, alpha=0.85,
              edgecolor="white", linewidth=0.5)
    a.axhline(0, color=vs.INK, lw=0.9, ls="--")
    r = np.corrcoef(m["n"], m["b_contemp"])[0, 1]
    a.set_xlabel("Moments contributed by that participant")
    a.set_ylabel("Person-specific flow-pain slope")
    a.set_title(f"Series length does not drive it (r = {r:.2f})")
    vs.panel_label(a, "E")

    a = ax[1, 2]
    a.scatter(pf["mean_challenge"], pf["mean_effic"], s=36,
              c=pf["flow_prop_abs5"], cmap="YlGnBu", edgecolor="white", linewidth=0.5)
    lims = [1, 7]
    a.plot(lims, lims, color=vs.MUTED, lw=1.0, ls="--")
    a.set_xlim(1, 7); a.set_ylim(1, 7)
    a.set_xlabel("Mean challenge"); a.set_ylabel("Mean skill")
    a.set_title("Almost every patient sits above the diagonal")
    sc = a.collections[0]
    vs.add_cbar(fig, a, sc, label="share of flow moments")
    vs.panel_label(a, "F")

    fig.tight_layout(h_pad=2.8, w_pad=2.8)
    vs.savefig(fig, FIG / "SUP_05_person_level.png")


# ---------------------------------------------------------------------------
# SUP_06 - Robustness of the flow-pain association
# ---------------------------------------------------------------------------
def sup_06():
    con = pd.read_csv(T / "12_flow_pain_contemporaneous.csv")
    cov = pd.read_csv(T / "12_flow_covariate_check.csv")
    prof = pd.read_csv(T / "12_flow_channel_profiles.csv")
    rs = pd.read_csv(T / "12_flow_pain_random_slopes.csv")
    f = frame()

    fig, ax = plt.subplots(2, 3, figsize=(15.6, 8.8))

    a = ax[0, 0]
    x = np.arange(len(OUT)); w = 0.26
    for k, (term, col, lab) in enumerate([
            ("FLOWEXP_w", FLOW, "Flow experience"),
            ("balance_w", BAL, "Balance"),
            ("elevation_w", ELEV, "Elevation")]):
        sub = con[(con["model"] == "activity-adjusted") &
                  (con["term"] == term)].set_index("outcome")
        a.bar(x + (k - 1) * w, [sub.loc[o, "estimate"] for o in OUT], w, color=col,
              edgecolor="white", label=lab,
              yerr=[1.96 * sub.loc[o, "SE"] for o in OUT], capsize=1.8,
              error_kw={"lw": 0.8, "ecolor": vs.INK})
    a.axhline(0, color=vs.INK, lw=0.9)
    a.set_xticks(x); a.set_xticklabels([OUT_LAB[o].replace(" ", "\n") for o in OUT],
                                       fontsize=8)
    a.set_ylabel("Effect at the same beep")
    a.set_title("All three terms in the same model")
    a.legend(fontsize=7.5); vs.bar_axes(a); vs.panel_label(a, "A")

    a = ax[0, 1]
    sub = con[(con["model"] == "activity-adjusted") &
              (con["term"] == "ACTIEF_w")].set_index("outcome")
    a.bar(np.arange(len(OUT)), [sub.loc[o, "estimate"] for o in OUT],
          color=vs.NODE_COLORS["PIJN"], edgecolor="white",
          yerr=[1.96 * sub.loc[o, "SE"] for o in OUT], capsize=3,
          error_kw={"lw": 1.0, "ecolor": vs.INK})
    a.axhline(0, color=vs.INK, lw=0.9)
    a.set_xticks(np.arange(len(OUT)))
    a.set_xticklabels([OUT_LAB[o].replace(" ", "\n") for o in OUT], fontsize=8)
    a.set_ylabel("Effect of physical activation")
    a.set_title("Being active raises pain in its own right")
    vs.bar_axes(a); vs.panel_label(a, "B")

    a = ax[0, 2]
    lab_c = {"V2: condition -> experience": "Elevation on the\nflow experience",
             "Flow -> pain (activity-adjusted)": "Flow experience on\npain intensity"}
    pct = 100 * (cov["b_with"] - cov["b_without"]) / cov["b_without"].abs()
    y = np.arange(len(cov))[::-1]
    a.barh(y, pct, color=FLOW, edgecolor="white", height=0.5)
    a.axvline(0, color=vs.INK, lw=1.0)
    for yy, (pc, bw, ba) in zip(y, zip(pct, cov["b_without"], cov["b_with"])):
        a.text(pc + np.sign(pc) * 0.4, yy, f"{bw:+.4f} $\\rightarrow$ {ba:+.4f}",
               va="center", ha="left" if pc >= 0 else "right", fontsize=8,
               color=vs.MUTED)
    a.set_yticks(y)
    a.set_yticklabels([lab_c.get(m, m) for m in cov["model"]], fontsize=8)
    a.set_xlim(-14, 14)
    a.set_xlabel("% change in the focal estimate when day and beep are added")
    a.set_title("Time of day changes nothing focal")
    vs.bar_axes(a, "horizontal"); vs.panel_label(a, "C")

    a = ax[1, 0]
    ch = prof[prof["rule"] == "A_abs5"].set_index("channel").loc[vs.CHANNEL_ORDER]
    cols_ = ["mean_pijn", "mean_pijn_aff", "mean_attend", "mean_threat"]
    labs_ = ["Pain\nintensity", "Pain\ninterference", "Attention\nto pain", "Threat\nvalue"]
    x = np.arange(len(cols_)); w = 0.2
    for k, name in enumerate(vs.CHANNEL_ORDER):
        a.bar(x + (k - 1.5) * w, [ch.loc[name, c] for c in cols_], w,
              color=vs.CHANNEL_COLORS[name], edgecolor="white", label=name)
    a.set_xticks(x); a.set_xticklabels(labs_, fontsize=8)
    a.set_ylabel("Raw momentary mean")
    a.set_title("Momentary profile of the four channels")
    a.legend(fontsize=7.5, ncol=2); vs.bar_axes(a); vs.panel_label(a, "D")

    a = ax[1, 1]
    x = np.arange(len(OUT)); w = 0.36
    rsi = rs.set_index("outcome")
    a.bar(x - w / 2, [rsi.loc[o, "random_SD_flow_base"] for o in OUT], w, color=GREY,
          edgecolor="white", label="Unadjusted")
    a.bar(x + w / 2, [rsi.loc[o, "random_SD_flow_adj"] for o in OUT], w, color=FLOW,
          edgecolor="white", label="Activity-adjusted")
    for xi, o in enumerate(OUT):
        fx = con[(con["model"] == "activity-adjusted") & (con["term"] == "FLOWEXP_w") &
                 (con["outcome"] == o)]["estimate"].iloc[0]
        a.plot(xi, abs(fx), "d", ms=7, color=vs.NODE_COLORS["PIJN"], zorder=4)
    a.set_xticks(x); a.set_xticklabels([OUT_LAB[o].replace(" ", "\n") for o in OUT],
                                       fontsize=8)
    a.set_ylabel("Between-person SD of the flow slope")
    a.set_title("The spread is as large as the average effect")
    a.legend(handles=a.get_legend_handles_labels()[0] +
             [plt.Line2D([], [], marker="d", ls="", color=vs.NODE_COLORS["PIJN"],
                         label="|fixed effect|")], fontsize=7.5)
    vs.bar_axes(a); vs.panel_label(a, "E")

    a = ax[1, 2]
    bins = np.linspace(-3.2, 3.2, 33)
    a.hist(f["FLOWEXP_w"].dropna(), bins=bins, color=FLOW, alpha=0.75, edgecolor="white",
           label="Flow experience")
    a.hist(f["PIJN_w"].dropna(), bins=bins, color=vs.NODE_COLORS["PIJN"], alpha=0.55,
           edgecolor="white", label="Pain intensity")
    a.set_xlabel("Person-centred score")
    a.set_ylabel("Moments")
    a.set_title("Both focal variables move within persons")
    a.legend(fontsize=8); vs.bar_axes(a); vs.panel_label(a, "F")

    fig.tight_layout(h_pad=2.8, w_pad=2.8)
    vs.savefig(fig, FIG / "SUP_06_robustness.png")


def main():
    np.random.seed(20260703)
    for fn in [sup_01, sup_02, sup_03, sup_04, sup_05, sup_06]:
        try:
            fn()
        except Exception as e:
            import traceback
            print(f"  WARNING: {fn.__name__} failed: {e}")
            traceback.print_exc()
    print("flow supplementary figures written to", FIG)


if __name__ == "__main__":
    main()
