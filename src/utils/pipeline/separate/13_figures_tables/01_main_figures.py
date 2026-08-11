"""Stage 13.1 - Main manuscript figures (MAIN_01 to MAIN_05)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy import stats

LIB = Path(__file__).resolve().parents[3] / "lib"
sys.path.insert(0, str(LIB))
import paths  # noqa: E402
import vizstyle as vs  # noqa: E402
from netviz import draw_network  # noqa: E402

vs.apply_style()
T = paths.RESULTS_TABLES
N = paths.RESULTS_NETWORKS
FIG = paths.FIG_MAIN
paths.ensure_dirs()

CORE = ["PIJN", "THREAT", "ATTEND", "ENGAGE"]
IDIO_THRESHOLD = 100  # recommended series length for stable individual networks


def _ci_band(ax, x, y, color, label=None):
    """Scatter with an OLS fit and a 95% confidence band."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    ax.scatter(x, y, s=24, color=color, alpha=0.7, edgecolor="white", linewidth=0.4,
               zorder=3, label=label)
    if len(x) < 4:
        return
    b, a = np.polyfit(x, y, 1)
    xs = np.linspace(x.min(), x.max(), 100)
    yhat = a + b * xs
    n = len(x)
    resid = y - (a + b * x)
    s_err = np.sqrt(np.sum(resid ** 2) / (n - 2))
    tval = stats.t.ppf(0.975, n - 2)
    se_line = s_err * np.sqrt(1 / n + (xs - x.mean()) ** 2 / np.sum((x - x.mean()) ** 2))
    ax.plot(xs, yhat, color=vs.INK, lw=1.6, zorder=4)
    ax.fill_between(xs, yhat - tval * se_line, yhat + tval * se_line,
                    color=color, alpha=0.18, zorder=2)


# ---------------------------------------------------------------------------
# MAIN_01 - Series length and within-person variance (the methodological pivot)
# ---------------------------------------------------------------------------
def main_01():
    comp = pd.read_csv(T / "02_compliance_per_person.csv")
    vd = pd.read_csv(T / "03_variance_decomposition.csv")
    wc = pd.read_csv(T / "02_within_person_corr.csv").set_index("variable")

    fig, axes = plt.subplots(2, 2, figsize=(11, 8.4))

    ax = axes[0, 0]
    lo = int(np.floor(comp["n_completed"].min() / 5) * 5)
    hi = int(np.ceil(comp["n_completed"].max() / 5) * 5) + 5
    ax.hist(comp["n_completed"], bins=np.arange(lo, hi, 5),
            color=vs.NODE_COLORS["ATTEND"], edgecolor="white")
    ymax = ax.get_ylim()[1]
    med = comp["n_completed"].median()
    ax.axvline(med, color=vs.NODE_COLORS["PIJN"], lw=1.6)
    ax.axvline(IDIO_THRESHOLD, color=vs.INK, ls="--", lw=1.6)
    ax.text(med - 2, ymax * 1.02, f"median = {med:.0f}", ha="right", va="bottom",
            fontsize=8, color=vs.NODE_COLORS["PIJN"])
    ax.text(IDIO_THRESHOLD + 2, ymax * 1.02, "~100 obs (threshold)", ha="left", va="bottom",
            fontsize=8, color=vs.INK)
    ax.set_ylim(0, ymax * 1.16)
    ax.set_xlabel("Completed momentary prompts per person")
    ax.set_ylabel("Participants")
    ax.set_title("Series length supports individual networks")
    vs.bar_axes(ax); vs.panel_label(ax, "A")

    ax = axes[0, 1]
    order = ["PIJN", "THREAT", "ATTEND", "ENGAGE", "EFFIC", "VALENCE"]
    vd = vd.set_index("variable").loc[order].reset_index()
    labels = [vs.node_label_long(v) for v in vd["variable"]]
    bottom = np.zeros(len(vd))
    for comp_col, col, lab in [("var_between_person", vs.MUTED, "Between person"),
                               ("var_between_day", "#b9c4cf", "Between day"),
                               ("var_within_day", vs.NODE_COLORS["ATTEND"], "Within day")]:
        ax.bar(labels, vd[comp_col], bottom=bottom, color=col, label=lab, edgecolor="white")
        bottom += vd[comp_col].values
    ax.set_ylabel("Share of variance"); ax.set_title("Variance decomposition")
    ax.legend(loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.34), fontsize=8)
    ax.tick_params(axis="x", rotation=25); vs.bar_axes(ax); vs.panel_label(ax, "B")

    ax = axes[1, 0]
    ratio = vd["var_within_day"] / vd["var_between_person"]
    ax.barh(labels, ratio, color=[vs.node_color(v) for v in vd["variable"]], edgecolor="white")
    ax.axvline(1.0, color=vs.INK, ls="--", lw=1.0)
    ax.set_xlabel("Within-day / between-person variance ratio")
    ax.set_title("Moment-to-moment vs trait signal")
    vs.bar_axes(ax, "horizontal"); vs.panel_label(ax, "C")

    ax = axes[1, 1]
    drivers = ["THREAT", "ATTEND", "ENGAGE", "EFFIC", "VALENCE"]
    rvals = [wc.loc["PIJN", dv] for dv in drivers]
    dl = [vs.node_label_long(dv) for dv in drivers]
    cols = [vs.EDGE_POS if r >= 0 else vs.EDGE_NEG for r in rvals]
    ax.barh(dl, rvals, color=cols, edgecolor="white")
    ax.axvline(0, color=vs.INK, lw=0.8)
    ax.set_xlabel("Within-person correlation with pain")
    ax.set_title("Momentary drivers co-vary with pain")
    vs.bar_axes(ax, "horizontal"); vs.panel_label(ax, "D")

    fig.tight_layout(h_pad=2.4, w_pad=2.6)
    vs.savefig(fig, FIG / "MAIN_01_variance_feasibility.png")


# ---------------------------------------------------------------------------
# MAIN_02 - Pooled benchmark networks (temporal + contemporaneous; full width)
# ---------------------------------------------------------------------------
def main_02():
    temp = pd.read_csv(N / "05_mlvar_core_temporal_edges.csv")
    con = pd.read_csv(N / "05_mlvar_core_contemporaneous_edges.csv")

    fig, axes = plt.subplots(1, 2, figsize=(13.2, 6.0))
    t_edges = [{"from": r["from"], "to": r["to"], "weight": r["weight"], "P": r["P"]}
               for _, r in temp.iterrows()]
    draw_network(axes[0], CORE, t_edges, directed=True, title="A  Temporal (lag-1)",
                 label_fontsize=11, node_radius=0.42)
    c_edges = [{"node1": r["node1"], "node2": r["node2"], "weight": r["pcor"], "P": r["P"]}
               for _, r in con.iterrows()]
    draw_network(axes[1], CORE, c_edges, directed=False, title="B  Contemporaneous",
                 label_fontsize=11, node_radius=0.42)
    handles = [Line2D([0], [0], color=vs.EDGE_POS, lw=3, label="Positive"),
               Line2D([0], [0], color=vs.EDGE_NEG, lw=3, label="Negative")]
    fig.legend(handles=handles, loc="lower center", ncol=2, fontsize=10,
               bbox_to_anchor=(0.5, 0.01))
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    vs.savefig(fig, FIG / "MAIN_02_mlvar_networks.png")


# ---------------------------------------------------------------------------
# MAIN_03 - Idiographic heterogeneity in the pain-driver couplings
# ---------------------------------------------------------------------------
def main_03():
    pp = pd.read_csv(N / "07_perperson_pain_equation.csv")
    fix = pd.read_csv(N / "05_mlvar_core_temporal_edges.csv")
    freq = pd.read_csv(N / "07_graphicalvar_edge_selection_freq.csv")
    het = pd.read_csv(N / "07_perperson_edge_heterogeneity.csv")

    def fixed(frm, to):
        m = fix[(fix["from"] == frm) & (fix["to"] == to)]
        return float(m["weight"].iloc[0]) if len(m) else np.nan

    fig, axes = plt.subplots(2, 2, figsize=(11.4, 8.8))
    axA, axB, axC, axD = axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]

    # Panel A: distributions of per-person driver->pain couplings (grey violin + strip)
    cpls = [("threat_to_pain", "THREAT", "Threat"),
            ("attend_to_pain", "ATTEND", "Attention"),
            ("engage_to_pain", "ENGAGE", "Engagement")]
    vdata = [pp[c[0]].dropna().values for c in cpls]
    vp = axA.violinplot(vdata, positions=range(3), widths=0.75, showextrema=False)
    for b in vp["bodies"]:
        b.set_facecolor("#d9dee4"); b.set_edgecolor("none"); b.set_alpha(0.7)
    for i, (col, node, lab) in enumerate(cpls):
        vals = pp[col].dropna().values
        x = np.random.normal(i, 0.055, size=len(vals))
        axA.scatter(x, vals, s=14, color=vs.node_color(node), alpha=0.6, edgecolor="none",
                    zorder=3)
        axA.hlines(vals.mean(), i - 0.28, i + 0.28, color=vs.INK, lw=2, zorder=4)
        axA.plot(i, fixed(node, "PIJN"), marker="D", color=vs.NODE_COLORS["PIJN"], ms=7,
                 zorder=5)
    axA.axhline(0, color=vs.MUTED, lw=0.8, ls="--")
    axA.set_xticks(range(3)); axA.set_xticklabels([c[2] for c in cpls])
    axA.set_ylabel("Per-person lag-1 coefficient to pain")
    axA.set_title("Heterogeneous driver-to-pain couplings")
    axA.legend(handles=[Line2D([0], [0], color=vs.INK, lw=2, label="Per-person mean"),
                        Line2D([0], [0], marker="D", color=vs.NODE_COLORS["PIJN"], lw=0,
                               label="mlVAR fixed effect")], fontsize=8, loc="upper right")
    vs.bar_axes(axA); vs.panel_label(axA, "A")

    # Panel B: sorted per-person threat->pain with 95% CI
    d = pp.dropna(subset=["threat_to_pain"]).sort_values("threat_to_pain").reset_index()
    y = np.arange(len(d))
    sig = ((d["threat_lo"] > 0) & (d["threat_hi"] > 0)) | ((d["threat_lo"] < 0) & (d["threat_hi"] < 0))
    axB.hlines(y, d["threat_lo"], d["threat_hi"],
               color=[vs.NODE_COLORS["THREAT"] if s else "#c9d2db" for s in sig], lw=1.2)
    axB.plot(d["threat_to_pain"], y, "o", ms=3, color=vs.INK)
    axB.axvline(0, color=vs.MUTED, lw=0.8)
    axB.set_xlabel("Threat -> pain (per person, 95% CI)")
    axB.set_ylabel("Participants (sorted)")
    axB.set_title(f"Individual estimates ({int(sig.sum())} of {len(d)} exclude 0)")
    axB.set_yticks([]); vs.panel_label(axB, "B")

    # Panel C: graphicalVAR temporal edge-selection frequency (matrix)
    mat = np.zeros((len(CORE), len(CORE)))
    for _, r in freq.iterrows():
        if r["from"] in CORE and r["to"] in CORE:
            mat[CORE.index(r["from"]), CORE.index(r["to"])] = r["pct_selected"]
    im = axC.imshow(mat, cmap="PuBu", vmin=0, vmax=max(mat.max(), 1))
    axC.set_xticks(range(len(CORE))); axC.set_yticks(range(len(CORE)))
    lbl = [vs.node_label_long(c) for c in CORE]
    axC.set_xticklabels(lbl, rotation=25, ha="right", fontsize=8)
    axC.set_yticklabels(lbl, fontsize=8)
    axC.set_xlabel("To (t)"); axC.set_ylabel("From (t-1)")
    for i in range(len(CORE)):
        for j in range(len(CORE)):
            axC.text(j, i, f"{mat[i, j]:.0f}", ha="center", va="center", fontsize=8,
                     color=vs.INK if mat[i, j] < mat.max() * 0.6 else "white")
    axC.set_title("graphicalVAR: % of persons selecting edge")
    vs.matrix_axes(axC); vs.add_cbar(fig, axC, im, label="% selected"); vs.panel_label(axC, "C")

    # Panel D: between-person heterogeneity network (clean, restored sizing)
    het2 = het[het["from"].isin(CORE) & het["to"].isin(CORE)]
    edges = [{"from": r["from"], "to": r["to"], "weight": r["sd"], "P": 0.0}
             for _, r in het2.iterrows()]
    draw_network(axD, CORE, edges, directed=True, title="D  Between-person heterogeneity (SD)",
                 label_fontsize=9, node_radius=0.36, edge_cmap=plt.cm.Purples)
    vs.panel_label(axD, "D")
    fig.tight_layout(h_pad=2.6, w_pad=2.6)
    vs.savefig(fig, FIG / "MAIN_03_idiographic_heterogeneity.png")


# ---------------------------------------------------------------------------
# MAIN_04 - RQ2: baseline traits and momentary experience (six panels)
# ---------------------------------------------------------------------------
def main_04():
    corr = pd.read_csv(T / "09_between_person_correlations.csv")
    hier = pd.read_csv(T / "09_between_person_hierarchical.csv")
    mod = pd.read_csv(T / "09_moderation.csv")
    d = pd.read_csv(paths.EMA_LONG)
    traits = pd.read_csv(T / "08_trait_profiles.csv")
    means = d.groupby("subject")[["ATTEND", "ENGAGE"]].mean().reset_index()
    m = means.merge(traits, on="subject", how="inner")

    fig, axes = plt.subplots(2, 3, figsize=(15.5, 9.0))

    # Panel A: partial r of each account with mean attention and mean engagement
    ax = axes[0, 0]
    accounts = ["Threat", "Biomedical", "Personality"]
    states = ["Attention to pain", "Goal engagement"]
    x = np.arange(len(states)); w = 0.26
    for k, acc in enumerate(accounts):
        vals = [corr[(corr["state"] == s) & (corr["account"] == acc)]["partial_r"].iloc[0]
                for s in states]
        ax.bar(x + (k - 1) * w, vals, w, color=vs.TRAIT_COLORS[acc], label=acc, edgecolor="white")
    ax.axhline(0, color=vs.INK, lw=0.8)
    ax.set_xticks(x); ax.set_xticklabels(["Attention\nto pain", "Goal\nengagement"], fontsize=9)
    ax.set_ylabel("Partial r (controlling mean pain)")
    ax.set_title("Baseline profiles predict mean states")
    ax.legend(fontsize=8); vs.bar_axes(ax); vs.panel_label(ax, "A")

    # Panel B: threat account vs mean attention to pain (scatter + CI band)
    ax = axes[0, 1]
    _ci_band(ax, m["threat_account"], m["ATTEND"], vs.NODE_COLORS["ATTEND"])
    r = corr[(corr["state"] == "Attention to pain") & (corr["account"] == "Threat")]
    ax.set_xlabel("Baseline threat-value profile (z)")
    ax.set_ylabel("Mean momentary attention to pain")
    ax.set_title(f"Threat and attention (r = {r['zero_order_r'].iloc[0]:.2f})")
    vs.panel_label(ax, "B")

    # Panel C: threat account vs mean goal engagement (scatter + CI band)
    ax = axes[0, 2]
    _ci_band(ax, m["threat_account"], m["ENGAGE"], vs.NODE_COLORS["ENGAGE"])
    r = corr[(corr["state"] == "Goal engagement") & (corr["account"] == "Threat")]
    ax.set_xlabel("Baseline threat-value profile (z)")
    ax.set_ylabel("Mean momentary goal engagement")
    ax.set_title(f"Threat and engagement (r = {r['zero_order_r'].iloc[0]:.2f})")
    vs.panel_label(ax, "C")

    # Panel D: hierarchical variance (mean pain vs pain + profiles)
    ax = axes[1, 0]
    hh = hier[hier["state"].isin(["Attention to pain", "Goal engagement"])].copy()
    x = np.arange(len(hh)); w = 0.36
    ax.bar(x - w / 2, hh["R2_pain"], w, color=vs.MUTED, label="Pain only", edgecolor="white")
    ax.bar(x + w / 2, hh["R2_pain_plus_traits"], w, color=vs.TRAIT_COLORS["Threat"],
           label="Pain + profiles", edgecolor="white")
    ax.set_xticks(x); ax.set_xticklabels(["Attention\nto pain", "Goal\nengagement"], fontsize=9)
    ax.set_ylabel(r"Explained variance ($R^2$)")
    ax.set_title("Baseline profiles add explained variance")
    ax.legend(fontsize=8); vs.bar_axes(ax); vs.panel_label(ax, "D")

    # Panel E: specificity heatmap (accounts x momentary states, zero-order r)
    ax = axes[1, 1]
    st = ["Attention to pain", "Threat value", "Goal engagement", "Goal efficacy"]
    mat = np.full((len(accounts), len(st)), np.nan)
    for i, acc in enumerate(accounts):
        for j, s in enumerate(st):
            row = corr[(corr["account"] == acc) & (corr["state"] == s)]
            if len(row):
                mat[i, j] = row["zero_order_r"].iloc[0]
    im = ax.imshow(mat, cmap="RdBu_r", vmin=-0.6, vmax=0.6, aspect="auto")
    ax.set_xticks(range(len(st)))
    ax.set_xticklabels([s.replace(" ", "\n") for s in st], fontsize=7)
    ax.set_yticks(range(len(accounts))); ax.set_yticklabels(accounts, fontsize=8)
    for i in range(len(accounts)):
        for j in range(len(st)):
            if not np.isnan(mat[i, j]):
                ax.text(j, i, f"{mat[i, j]:.2f}", ha="center", va="center", fontsize=8,
                        color=vs.INK if abs(mat[i, j]) < 0.4 else "white")
    ax.set_title("Profile-state correlations")
    vs.matrix_axes(ax); vs.add_cbar(fig, ax, im, label="r"); vs.panel_label(ax, "E")

    # Panel F: cross-level moderation forest (threat moderator)
    ax = axes[1, 2]
    md = mod[mod["moderator"] == "Threat"].copy().iloc[::-1].reset_index(drop=True)
    y = np.arange(len(md))
    lo = md["interaction_b"] - 1.96 * md["interaction_SE"]
    hi = md["interaction_b"] + 1.96 * md["interaction_SE"]
    sig = md["interaction_p"] < 0.05
    ax.hlines(y, lo, hi, color=[vs.NODE_COLORS["THREAT"] if s else "#c9d2db" for s in sig], lw=2)
    ax.plot(md["interaction_b"], y, "o", ms=5, color=vs.INK)
    ax.axvline(0, color=vs.MUTED, lw=0.9, ls="--")
    ax.set_yticks(y); ax.set_yticklabels(md["coupling"], fontsize=8)
    ax.set_xlabel("Threat x coupling interaction (95% CI)")
    ax.set_title("Profiles do not moderate the couplings")
    vs.panel_label(ax, "F")

    fig.tight_layout(h_pad=2.8, w_pad=2.8)
    vs.savefig(fig, FIG / "MAIN_04_trait_link.png")


def main_05():
    """Flow states and the momentary experience of pain (stage 12).

    Six panels: the flow surface over the challenge-skill plane, the condition-to-experience
    model, the pain profile of the four channels, the contemporaneous flow-to-pain
    associations, the lagged models in both directions, and the per-person distribution of
    the flow-pain coupling.
    """
    f = pd.read_csv(paths.RESULTS_MODELS / "12_flow_analytic_frame.csv")
    chan = pd.read_csv(T / "12_flow_channel_profiles.csv")
    cond = pd.read_csv(T / "12_flow_condition_experience_fixed.csv")
    con = pd.read_csv(T / "12_flow_pain_contemporaneous.csv")
    lag = pd.read_csv(T / "12_flow_pain_lagged.csv")
    per = pd.read_csv(T / "12_flow_perperson_slopes.csv")

    fig, axes = plt.subplots(2, 3, figsize=(15.5, 9.0))

    # Panel A: mean flow experience over the raw challenge-skill plane.
    ax = axes[0, 0]
    grid = np.full((7, 7), np.nan)
    counts = np.zeros((7, 7))
    for (c, s), g in f.groupby(["CHALLENGE", "EFFIC"]):
        ci, si = int(c) - 1, int(s) - 1
        counts[si, ci] = len(g)
        if len(g) >= 10:
            grid[si, ci] = g["FLOWEXP"].mean()
    im = ax.imshow(grid, origin="lower", cmap="YlGnBu", vmin=1, vmax=7,
                   extent=(0.5, 7.5, 0.5, 7.5), aspect="auto")
    for si in range(7):
        for ci in range(7):
            if np.isfinite(grid[si, ci]):
                ax.text(ci + 1, si + 1, f"{grid[si, ci]:.1f}", ha="center", va="center",
                        fontsize=6.5,
                        color=vs.INK if grid[si, ci] < 4.6 else "white")
    ax.axvline(4.5, color=vs.INK, lw=1.0, ls="--")
    ax.axhline(4.5, color=vs.INK, lw=1.0, ls="--")
    box = {"facecolor": "white", "alpha": 0.82, "edgecolor": "none", "pad": 1.6}
    for (fx, fy, ha, va, name, weight) in [
            (0.985, 0.985, "right", "top", "Flow", "bold"),
            (0.985, 0.015, "right", "bottom", "Anxiety", "normal"),
            (0.015, 0.985, "left", "top", "Relaxation", "normal"),
            (0.015, 0.015, "left", "bottom", "Apathy", "normal")]:
        ax.text(fx, fy, name, transform=ax.transAxes, fontsize=8, fontweight=weight,
                ha=ha, va=va, color=vs.CHANNEL_COLORS[name], bbox=box, zorder=5)
    ax.set_xlabel("Challenge (1 to 7)")
    ax.set_ylabel("Skill (1 to 7)")
    ax.set_xticks(range(1, 8)); ax.set_yticks(range(1, 8))
    ax.set_title("The flow surface")
    ax.grid(False)
    vs.add_cbar(fig, ax, im, label="Mean flow experience")
    vs.panel_label(ax, "A")

    # Panel B: condition-to-experience fixed effects with the random-slope spread.
    ax = axes[0, 1]
    cc = cond[(cond["model"] == "balance + elevation") &
              (cond["term"].isin(["balance_w", "elevation_w", "balance_b", "elevation_b"]))]
    order = ["elevation_w", "balance_w", "elevation_b", "balance_b"]
    labels = ["Elevation\n(within)", "Balance\n(within)", "Elevation\n(between)",
              "Balance\n(between)"]
    vals = [cc[cc["term"] == t]["estimate"].iloc[0] for t in order]
    ses = [cc[cc["term"] == t]["SE"].iloc[0] for t in order]
    cols = [vs.FLOW_COLORS["elevation"], vs.FLOW_COLORS["balance"]] * 2
    y = np.arange(len(order))[::-1]
    ax.barh(y, vals, xerr=np.array(ses) * 1.96, color=cols, edgecolor="white",
            error_kw={"ecolor": vs.INK, "elinewidth": 1.0, "capsize": 3})
    ax.axvline(0, color=vs.INK, lw=0.8)
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("Effect on flow experience (95% CI)")
    ax.set_title("Elevation, not balance, drives flow")
    vs.bar_axes(ax, "horizontal"); vs.panel_label(ax, "B")

    # Panel C: momentary pain profile of the four channels (absolute rule, both items >= 5).
    ax = axes[0, 2]
    cp = chan[chan["rule"] == "A_abs5"].set_index("channel")
    states = [("mean_pijn", "Pain"), ("mean_pijn_aff", "Interference"),
              ("mean_attend", "Attention"), ("mean_threat", "Threat")]
    x = np.arange(len(states)); w = 0.2
    for k, ch in enumerate(vs.CHANNEL_ORDER):
        if ch not in cp.index:
            continue
        vals = [cp.loc[ch, c] for c, _ in states]
        ax.bar(x + (k - 1.5) * w, vals, w, color=vs.CHANNEL_COLORS[ch], label=ch,
               edgecolor="white")
    ax.set_xticks(x); ax.set_xticklabels([l for _, l in states], fontsize=8)
    ax.set_ylabel("Momentary rating (1 to 7)")
    ax.set_ylim(1, 5.9)
    ax.set_title("Pain profile of the four channels")
    ax.legend(fontsize=7.5, ncol=4, loc="upper center", columnspacing=1.0,
              handletextpad=0.5)
    vs.bar_axes(ax); vs.panel_label(ax, "C")

    # Panel D: contemporaneous flow-experience associations, unadjusted vs activity-adjusted.
    ax = axes[1, 0]
    outs = ["PIJN", "PIJN_AFF", "ATTEND", "THREAT"]
    labs = [vs.node_label_long(o) if o in vs.NODE_LABELS_LONG else "Pain interference"
            for o in outs]
    y = np.arange(len(outs))[::-1]
    for shift, model, color, lab in [(0.16, "base", vs.MUTED, "Unadjusted"),
                                     (-0.16, "activity-adjusted", vs.FLOW_COLORS["FLOWEXP"],
                                      "Activity-adjusted")]:
        sub = con[(con["model"] == model) & (con["term"] == "FLOWEXP_w")].set_index("outcome")
        est = np.array([sub.loc[o, "estimate"] for o in outs])
        se = np.array([sub.loc[o, "SE"] for o in outs])
        ax.errorbar(est, y + shift, xerr=1.96 * se, fmt="o", ms=5, color=color,
                    ecolor=color, elinewidth=1.6, capsize=2.5, label=lab)
    ax.axvline(0, color=vs.INK, lw=0.9, ls="--")
    ax.set_yticks(y); ax.set_yticklabels(labs, fontsize=8)
    ax.set_xlabel("Effect of flow experience (95% CI)")
    ax.set_title("Flow tracks lower pain at the same moment")
    ax.legend(fontsize=8, loc="upper left"); vs.panel_label(ax, "D")

    # Panel E: lag-1 models in both directions, all null.
    ax = axes[1, 1]
    fw = lag[(lag["model"] == "flow(t-1) -> outcome(t)") &
             (lag["term"] == "FLOWEXP_lag")].set_index("outcome")
    rv = lag[lag["model"] == "predictor(t-1) -> flow(t)"].copy()
    rv = rv[rv["term"] == rv["outcome"] + "_lag"].set_index("outcome")
    rows = [("PIJN", "Flow -> Pain"), ("PIJN_AFF", "Flow -> Interference"),
            ("ATTEND", "Flow -> Attention"), ("THREAT", "Flow -> Threat")]
    rrows = [("PIJN", "Pain -> Flow"), ("ATTEND", "Attention -> Flow"),
             ("THREAT", "Threat -> Flow")]
    ests, ses, labs2, cols2 = [], [], [], []
    for o, lab in rows:
        ests.append(fw.loc[o, "estimate"]); ses.append(fw.loc[o, "SE"])
        labs2.append(lab); cols2.append(vs.FLOW_COLORS["FLOWEXP"])
    for o, lab in rrows:
        ests.append(rv.loc[o, "estimate"]); ses.append(rv.loc[o, "SE"])
        labs2.append(lab); cols2.append(vs.NODE_COLORS["PIJN"])
    y = np.arange(len(ests))[::-1]
    ax.errorbar(ests, y, xerr=1.96 * np.array(ses), fmt="o", ms=5, color=vs.INK,
                ecolor=cols2, elinewidth=0, capsize=0, ls="none")
    for yy, e, s, c in zip(y, ests, ses, cols2):
        ax.hlines(yy, e - 1.96 * s, e + 1.96 * s, color=c, lw=2.2)
        ax.plot(e, yy, "o", ms=5, color=vs.INK, zorder=3)
    ax.axvline(0, color=vs.INK, lw=0.9, ls="--")
    ax.set_yticks(y); ax.set_yticklabels(labs2, fontsize=8)
    ax.set_xlabel("Lag-1 effect, standardized (95% CI)")
    ax.set_title("No lag-1 effect in either direction")
    vs.panel_label(ax, "E")

    # Panel F: per-person flow-pain coupling, sorted, with 95% confidence intervals.
    ax = axes[1, 2]
    pp = per.sort_values("b_contemp").reset_index(drop=True)
    y = np.arange(len(pp))
    sig_neg = pp["hi_contemp"] < 0
    sig_pos = pp["lo_contemp"] > 0
    colors = np.where(sig_neg, vs.FLOW_COLORS["FLOWEXP"],
                      np.where(sig_pos, vs.NODE_COLORS["PIJN"], "#c9d2db"))
    ax.hlines(y, pp["lo_contemp"], pp["hi_contemp"], color=colors, lw=1.4)
    ax.plot(pp["b_contemp"], y, "o", ms=2.6, color=vs.INK)
    ax.axvline(0, color=vs.INK, lw=0.9, ls="--")
    med = pp["b_contemp"].median()
    ax.axvline(med, color=vs.FLOW_COLORS["FLOWEXP"], lw=1.2, ls=":")
    ax.text(0.02, 0.96, f"median $b$ = {med:.2f}\n{int(sig_neg.sum())} of {len(pp)} "
            f"reliably negative\n{int(sig_pos.sum())} reliably positive",
            transform=ax.transAxes, va="top", fontsize=8, color=vs.MUTED)
    ax.set_xlabel("Person-specific flow-pain slope (95% CI)")
    ax.set_ylabel("Participants, ordered")
    ax.set_yticks([])
    ax.set_title("The coupling is person-specific")
    vs.panel_label(ax, "F")

    fig.tight_layout(h_pad=2.8, w_pad=2.8)
    vs.savefig(fig, FIG / "MAIN_05_flow_states.png")


def main():
    np.random.seed(20260703)
    main_01(); main_02(); main_03(); main_04(); main_05()
    print("main figures written to", FIG)


if __name__ == "__main__":
    main()
