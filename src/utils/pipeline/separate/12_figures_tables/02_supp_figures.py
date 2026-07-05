"""Stage 12.2 - Supplementary manuscript figures (SUP_01 to SUP_10).

Each supplementary figure is a rich, multi-panel extension of a methodological theme, so the
supplement documents design, data quality, modelling assumptions, and robustness in depth.
"""
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
from netviz import draw_network  # noqa: E402

vs.apply_style()
T = paths.RESULTS_TABLES
N = paths.RESULTS_NETWORKS
FIG = paths.FIG_SUPP
paths.ensure_dirs()

CORE = ["PIJN", "THREAT", "ATTEND", "ENGAGE"]
EXT = ["PIJN", "THREAT", "ATTEND", "ENGAGE", "EFFIC", "VALENCE"]


def opt(p):
    return pd.read_csv(p) if Path(p).exists() else None


def _blank(ax, msg):
    ax.text(0.5, 0.5, msg, ha="center", va="center", fontsize=9, color=vs.MUTED,
            transform=ax.transAxes)
    ax.axis("off")


def _median_line(ax, value, horizontal=False, label=None, color=None):
    color = color or vs.NODE_COLORS["PIJN"]
    if horizontal:
        ax.axhline(value, color=color, ls="--", lw=1.2)
    else:
        ax.axvline(value, color=color, ls="--", lw=1.2)
    if label:
        ax.text(0.98, 0.95, label, transform=ax.transAxes, ha="right", va="top",
                fontsize=8, color=color)


# --- SUP_01 design & compliance (6 panels) ----------------------------------
def sup_01():
    ema = pd.read_csv(paths.EMA_LONG)
    comp = pd.read_csv(T / "02_compliance_per_person.csv")
    byday = pd.read_csv(T / "02_compliance_by_studyday.csv")
    daily = pd.read_csv(T / "02_timing_daily_counts.csv")
    fig, ax = plt.subplots(2, 3, figsize=(14, 7.8))

    a = ax[0, 0]
    s = comp.sort_values("n_completed")["n_completed"].values
    a.bar(range(len(s)), s, color=vs.NODE_COLORS["ATTEND"])
    _median_line(a, np.median(s), horizontal=True, label=f"median = {np.median(s):.0f}")
    a.set_xlabel("Participants (sorted)"); a.set_ylabel("Completed prompts")
    a.set_title("Completed prompts per participant"); vs.bar_axes(a); vs.panel_label(a, "A")

    a = ax[0, 1]
    a.hist(comp["n_completed"], bins=18, color=vs.MUTED, edgecolor="white")
    _median_line(a, comp["n_completed"].median(), label=f"median = {comp['n_completed'].median():.0f}")
    a.axvline(100, color=vs.INK, ls=":", lw=1.1)
    a.text(100, a.get_ylim()[1] * 0.9, " ~100", fontsize=8, color=vs.INK)
    a.set_xlabel("Completed prompts"); a.set_ylabel("Participants")
    a.set_title("Distribution vs idiographic threshold"); vs.bar_axes(a); vs.panel_label(a, "B")

    a = ax[0, 2]
    a.plot(byday["day"], byday["n_completed"], "-o", color=vs.NODE_COLORS["PIJN"])
    a.set_xlabel("Study day"); a.set_ylabel("Completed prompts (all persons)")
    a.set_title("Compliance across the 14 days"); vs.panel_label(a, "C")

    a = ax[1, 0]
    ppd = ema.groupby(["pid", "day"]).size().reset_index(name="n")
    parts = [ppd[ppd["day"] == dd]["n"].values for dd in sorted(ppd["day"].unique())]
    vpr = a.violinplot(parts, positions=sorted(ppd["day"].unique()), showmedians=True,
                       widths=0.8)
    for b in vpr["bodies"]:
        b.set_facecolor(vs.NODE_COLORS["ENGAGE"]); b.set_alpha(0.5)
    a.axhline(8, color=vs.INK, ls="--", lw=1)
    a.set_xlabel("Study day"); a.set_ylabel("Prompts per person-day")
    a.set_title("Prompts per person-day (target 8)"); vs.panel_label(a, "D")

    a = ax[1, 1]
    bp = ema.groupby("beep").size()
    a.bar(bp.index, bp.values, color=vs.NODE_COLORS["THREAT"])
    a.set_xlabel("Prompt position within day"); a.set_ylabel("Completed prompts")
    a.set_title("Responses by prompt position"); vs.bar_axes(a); vs.panel_label(a, "E")

    a = ax[1, 2]
    a.hist(comp["n_days"], bins=range(1, 17), color=vs.MUTED, edgecolor="white")
    _median_line(a, comp["n_days"].median(), label=f"median = {comp['n_days'].median():.0f}")
    a.set_xlabel("Study days with >=1 prompt"); a.set_ylabel("Participants")
    a.set_title("Days covered per participant"); vs.bar_axes(a); vs.panel_label(a, "F")
    fig.tight_layout(h_pad=2.2, w_pad=2.4)
    vs.savefig(fig, FIG / "SUP_01_design_compliance.png")


# --- SUP_02 stationarity (6 panels) -----------------------------------------
def sup_02():
    ema = pd.read_csv(paths.EMA_LONG)
    summ = pd.read_csv(T / "04_stationarity_summary.csv")
    pp = pd.read_csv(T / "04_stationarity_perperson.csv")
    dist = pd.read_csv(T / "04_item_distribution.csv")
    fig, ax = plt.subplots(2, 3, figsize=(14, 7.8))

    a = ax[0, 0]
    x = np.arange(len(summ))
    a.bar(x - 0.2, summ["prop_linear_trend"], 0.4, label="Linear trend",
          color=vs.NODE_COLORS["PIJN"])
    a.bar(x + 0.2, summ["prop_kpss_nonstationary"], 0.4, label="KPSS non-stationary",
          color=vs.NODE_COLORS["ATTEND"])
    a.set_xticks(x); a.set_xticklabels([vs.node_label_long(v) for v in summ["variable"]],
                                       rotation=18, fontsize=8)
    a.set_ylabel("Share of individual series"); a.set_title("Per-person stationarity flags")
    a.legend(fontsize=8); vs.bar_axes(a); vs.panel_label(a, "A")

    a = ax[0, 1]
    for v in CORE:
        s = pp[pp["variable"] == v]["trend_p"].dropna()
        a.hist(s, bins=12, histtype="step", lw=1.6, color=vs.node_color(v), label=vs.node_label(v))
    a.axvline(0.05, color=vs.INK, ls="--", lw=1); a.set_xlabel("Linear-trend p-value")
    a.set_ylabel("Persons"); a.set_title("Trend p-values by node")
    a.legend(fontsize=8); vs.panel_label(a, "B")

    a = ax[0, 2]
    for v in CORE:
        s = pp[pp["variable"] == v]["kpss_p"].dropna()
        a.hist(s, bins=12, histtype="step", lw=1.6, color=vs.node_color(v), label=vs.node_label(v))
    a.axvline(0.05, color=vs.INK, ls="--", lw=1); a.set_xlabel("KPSS p-value")
    a.set_ylabel("Persons"); a.set_title("KPSS p-values by node"); vs.panel_label(a, "C")

    a = ax[1, 0]
    a.bar(dist["measure"], dist["skewness"], color=vs.MUTED)
    a.axhline(0, color=vs.INK, lw=0.8)
    a.set_ylabel("Skewness"); a.set_title("Item distribution shape")
    a.tick_params(axis="x", rotation=15); vs.bar_axes(a); vs.panel_label(a, "E" if False else "D")

    a = ax[1, 1]
    ex = ema[ema["pid"].isin(sorted(ema["pid"].unique())[:3])]
    for pid, g in ex.groupby("pid"):
        g = g.reset_index()
        a.plot(range(len(g)), g["PIJN"], lw=0.9, alpha=0.8, label=pid)
    a.set_xlabel("Prompt index"); a.set_ylabel("Pain"); a.set_title("Example pain series")
    a.legend(fontsize=7, ncol=3); vs.panel_label(a, "E")

    a = ax[1, 2]
    lags = [1, 2, 3]
    for v in CORE:
        acf = []
        for lag in lags:
            rs = []
            for pid, g in ema.groupby("pid"):
                x = g[v].values
                if np.sum(~np.isnan(x)) > lag + 5:
                    x0, x1 = x[:-lag], x[lag:]
                    ok = ~np.isnan(x0) & ~np.isnan(x1)
                    if ok.sum() > 5 and np.nanstd(x0[ok]) > 0 and np.nanstd(x1[ok]) > 0:
                        rs.append(np.corrcoef(x0[ok], x1[ok])[0, 1])
            acf.append(np.nanmean(rs))
        a.plot(lags, acf, "-o", color=vs.node_color(v), label=vs.node_label(v))
    a.axhline(0, color=vs.INK, lw=0.8)
    a.set_xticks(lags); a.set_xlabel("Lag (prompts)"); a.set_ylabel("Mean within-person ACF")
    a.set_title("Autocorrelation by node"); a.legend(fontsize=7); vs.panel_label(a, "F")
    fig.tight_layout(h_pad=2.2, w_pad=2.4)
    vs.savefig(fig, FIG / "SUP_02_stationarity.png")


# --- SUP_03 missingness & imputation (6 panels) -----------------------------
def sup_03():
    ema = pd.read_csv(paths.EMA_LONG)
    miss = pd.read_csv(T / "04_missingness_by_measure.csv")
    imp = pd.read_csv(T / "04_imputation_comparison.csv")
    runs = pd.read_csv(T / "04_gap_runlengths.csv")
    fig, ax = plt.subplots(2, 3, figsize=(14, 7.8))

    a = ax[0, 0]
    a.bar(miss["measure"], miss["pct_missing"], color=vs.NODE_COLORS["THREAT"])
    a.set_ylabel("% missing"); a.set_title("Missingness by measure")
    a.tick_params(axis="x", rotation=20); vs.bar_axes(a); vs.panel_label(a, "A")

    a = ax[0, 1]
    cols = [vs.NODE_COLORS["ENGAGE"] if t == "multivariate" else vs.NODE_COLORS["ATTEND"]
            for t in imp["type"]]
    a.barh(imp["method"], imp["std_rmse"], color=cols)
    a.set_xlabel("Standardized RMSE (held-out)"); a.set_title("Imputation reconstruction error")
    vs.bar_axes(a, "horizontal"); vs.panel_label(a, "B")

    a = ax[0, 2]
    a.barh(imp["method"], imp["r_heldout"], color=cols)
    a.axvline(0, color=vs.INK, lw=0.8)
    a.set_xlabel("Held-out correlation r"); a.set_title("Imputation held-out correlation")
    vs.bar_axes(a, "horizontal"); vs.panel_label(a, "C")

    a = ax[1, 0]
    for m in runs["measure"].unique():
        s = runs[runs["measure"] == m]["run_length"]
        a.hist(s, bins=range(1, 9), histtype="step", lw=1.4, label=m)
    a.set_xlabel("Consecutive-missing run length"); a.set_ylabel("Count")
    a.set_title("Missing run lengths"); a.legend(fontsize=7); vs.panel_label(a, "D")

    a = ax[1, 1]
    mb = ema.groupby("beep")["PIJN"].apply(lambda s: 100 * s.isna().mean())
    resp = ema.groupby("beep").size()
    a.bar(resp.index, resp.values, color=vs.MUTED)
    a.set_xlabel("Prompt position within day"); a.set_ylabel("Completed prompts")
    a.set_title("Response count by prompt position"); vs.bar_axes(a); vs.panel_label(a, "E")

    a = ax[1, 2]
    legend = [("univariate", vs.NODE_COLORS["ATTEND"]), ("multivariate", vs.NODE_COLORS["ENGAGE"])]
    for t, c in legend:
        sub = imp[imp["type"] == t]
        a.scatter(sub["std_rmse"], sub["r_heldout"], s=60, color=c, label=t, edgecolor="white")
        for _, rr in sub.iterrows():
            a.annotate(rr["method"], (rr["std_rmse"], rr["r_heldout"]), fontsize=7,
                       xytext=(3, 3), textcoords="offset points")
    a.set_xlabel("Standardized RMSE"); a.set_ylabel("Held-out r")
    a.set_title("Accuracy trade-off"); a.legend(fontsize=8); vs.panel_label(a, "F")
    fig.tight_layout(h_pad=2.2, w_pad=2.4)
    vs.savefig(fig, FIG / "SUP_03_missingness_imputation.png")


# --- SUP_04 graphicalVAR feasibility (4 panels) -----------------------------
def sup_04():
    gv = pd.read_csv(T / "07_graphicalvar_individual_summary.csv")
    f = gv[gv["fitted"]].copy()
    freq = pd.read_csv(N / "07_graphicalvar_edge_selection_freq.csv")
    fig, ax = plt.subplots(2, 2, figsize=(10.5, 7.6))

    a = ax[0, 0]
    a.hist(f["n_temporal_edges"], bins=range(0, 12), color=vs.NODE_COLORS["ATTEND"],
           edgecolor="white")
    _median_line(a, f["n_temporal_edges"].median(),
                 label=f"median = {f['n_temporal_edges'].median():.0f}")
    a.set_xlabel("Selected temporal edges (of 16)"); a.set_ylabel("Persons")
    a.set_title("Temporal edges per person"); vs.bar_axes(a); vs.panel_label(a, "A")

    a = ax[0, 1]
    a.scatter(f["n_complete"], f["n_temporal_edges"], s=22, color=vs.NODE_COLORS["THREAT"],
              alpha=0.7)
    a.axvline(100, color=vs.INK, ls="--", lw=1)
    a.set_xlabel("Completed prompts"); a.set_ylabel("Selected temporal edges")
    a.set_title("Edges vs series length"); vs.panel_label(a, "B")

    a = ax[1, 0]
    fr = freq.sort_values("pct_selected", ascending=True)
    labs = [f"{vs.node_label(r['from'])}->{vs.node_label(r['to'])}" for _, r in fr.iterrows()]
    cols = [vs.NODE_COLORS["PIJN"] if r["from"] == r["to"] else vs.MUTED
            for _, r in fr.iterrows()]
    a.barh(labs, fr["pct_selected"], color=cols)
    a.set_xlabel("% of persons selecting edge"); a.set_title("Temporal edge selection frequency")
    a.tick_params(axis="y", labelsize=6); vs.bar_axes(a, "horizontal"); vs.panel_label(a, "C")

    a = ax[1, 1]
    counts = {"Threat\n-> pain": (f["threat_to_pain"] != 0).sum(),
              "Attention\n-> pain": (f["attend_to_pain"] != 0).sum(),
              "Engage\n-> pain": (f["engage_to_pain"] != 0).sum(),
              "Pain\n-> attention": (f["pain_to_attend"] != 0).sum()}
    a.bar(list(counts.keys()), list(counts.values()), color=vs.NODE_COLORS["PIJN"])
    a.set_ylabel("Persons with nonzero edge"); a.set_title("Selected key edges")
    vs.bar_axes(a); vs.panel_label(a, "D")
    fig.tight_layout(h_pad=2.2, w_pad=2.4)
    vs.savefig(fig, FIG / "SUP_04_graphicalvar_feasibility.png")


# --- SUP_05 S-GIMME (4 panels) ----------------------------------------------
def sup_05():
    memb = opt(T / "06_sgimme_subgroup_membership.csv")
    spc = opt(N / "06_sgimme_summary_path_counts.csv")
    incl = opt(T / "06_sgimme_inclusion.csv")
    fig, ax = plt.subplots(2, 2, figsize=(10.5, 7.6))

    a = ax[0, 0]
    if memb is not None:
        sizes = memb["subgroup"].value_counts().sort_index()
        a.bar([f"S{int(s)}" for s in sizes.index], sizes.values,
              color=[vs.CLUSTER_COLORS[i % len(vs.CLUSTER_COLORS)] for i in range(len(sizes))])
        a.set_ylabel("Participants"); a.set_title("S-GIMME subgroup sizes"); vs.bar_axes(a)
    else:
        _blank(a, "S-GIMME not available")
    vs.panel_label(a, "A")

    a = ax[0, 1]
    if incl is not None:
        a.hist(incl["n_complete"], bins=16, color=vs.MUTED, edgecolor="white")
        a.axvline(30, color=vs.INK, ls="--", lw=1); a.text(30, a.get_ylim()[1] * 0.9, " min T",
                                                           fontsize=8, color=vs.INK)
        a.set_xlabel("Complete prompts"); a.set_ylabel("Persons")
        a.set_title("Series length for S-GIMME"); vs.bar_axes(a)
    else:
        _blank(a, "n/a")
    vs.panel_label(a, "B")

    a = ax[1, 0]
    if spc is not None:
        grp = spc.sort_values("count.group", ascending=True).tail(8)
        a.barh(grp["path"], grp["count.group"], color=vs.NODE_COLORS["ATTEND"])
        a.set_xlabel("Persons with group-level path"); a.set_title("Group-level paths")
        a.tick_params(axis="y", labelsize=7); vs.bar_axes(a, "horizontal")
    else:
        _blank(a, "n/a")
    vs.panel_label(a, "C")

    a = ax[1, 1]
    if spc is not None:
        cross = spc[spc["count.group"] == 0].sort_values("count.ind", ascending=True).tail(8)
        a.barh(cross["path"], cross["count.ind"], color=vs.NODE_COLORS["THREAT"])
        a.set_xlabel("Persons with individual path"); a.set_title("Individual cross-variable paths")
        a.tick_params(axis="y", labelsize=7); vs.bar_axes(a, "horizontal")
    else:
        _blank(a, "n/a")
    vs.panel_label(a, "D")
    fig.tight_layout(h_pad=2.2, w_pad=2.6)
    vs.savefig(fig, FIG / "SUP_05_sgimme.png")


# --- SUP_06 extended six-node model (3 panels) ------------------------------
def sup_06():
    te = pd.read_csv(N / "extended_mlvar_temporal_edges.csv")
    con = pd.read_csv(N / "extended_mlvar_contemporaneous_edges.csv")
    cmp = opt(N / "extended_core_vs_full_compare.csv")
    fig = plt.figure(figsize=(14, 4.8))
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 0.9])
    a0, a1, a2 = fig.add_subplot(gs[0]), fig.add_subplot(gs[1]), fig.add_subplot(gs[2])

    t_edges = [{"from": r["from"], "to": r["to"], "weight": r["weight"], "P": r["P"]}
               for _, r in te.iterrows()]
    draw_network(a0, EXT, t_edges, directed=True, title="A  Extended temporal (lag-1)",
                 label_fontsize=7, node_radius=0.36)
    c_edges = [{"node1": r["node1"], "node2": r["node2"], "weight": r["pcor"], "P": r["P"]}
               for _, r in con.iterrows()]
    draw_network(a1, EXT, c_edges, directed=False, title="B  Extended contemporaneous",
                 label_fontsize=7, node_radius=0.36)
    if cmp is not None:
        a2.scatter(cmp["weight_core4"], cmp["weight_extended"], s=30,
                   color=vs.NODE_COLORS["PIJN"], alpha=0.75, edgecolor="white")
        lim = [cmp[["weight_core4", "weight_extended"]].min().min() - 0.05,
               cmp[["weight_core4", "weight_extended"]].max().max() + 0.05]
        a2.plot(lim, lim, color=vs.INK, ls="--", lw=1)
        a2.set_xlabel("Core-4 coefficient"); a2.set_ylabel("Extended coefficient")
        a2.set_title("C  Core edges preserved")
        vs.panel_label(a2, "")
    else:
        _blank(a2, "n/a")
    fig.tight_layout(w_pad=2.4)
    vs.savefig(fig, FIG / "SUP_06_extended_network.png")


# --- SUP_07 robustness (4 panels) -------------------------------------------
def sup_07():
    loo = opt(N / "robust_loo_summary.csv")
    boot = opt(N / "robust_bootstrap_summary.csv")
    det = opt(N / "robust_detrended_compare.csv")
    fig, ax = plt.subplots(2, 2, figsize=(10.5, 7.6))

    def elab(frm, to):
        return f"{vs.node_label(frm)}->{vs.node_label(to)}"

    a = ax[0, 0]
    if boot is not None:
        cr = boot[boot["from"] != boot["to"]].sort_values("weight")
        y = np.arange(len(cr))
        a.hlines(y, cr["ci_lo"], cr["ci_hi"], color=vs.NODE_COLORS["ATTEND"], lw=2)
        a.plot(cr["weight"], y, "o", ms=4, color=vs.INK); a.axvline(0, color=vs.MUTED, lw=0.8)
        a.set_yticks(y); a.set_yticklabels([elab(f, t) for f, t in zip(cr["from"], cr["to"])],
                                           fontsize=7)
        a.set_xlabel("Cross-lagged weight (bootstrap 95% CI)"); a.set_title("Person cluster-bootstrap")
    else:
        _blank(a, "bootstrap not available")
    vs.panel_label(a, "A")

    a = ax[0, 1]
    if loo is not None:
        cr = loo[loo["from"] != loo["to"]].sort_values("mean")
        y = np.arange(len(cr))
        a.hlines(y, cr["min"], cr["max"], color=vs.NODE_COLORS["ENGAGE"], lw=2)
        a.plot(cr["weight"], y, "o", ms=4, color=vs.INK); a.axvline(0, color=vs.MUTED, lw=0.8)
        a.set_yticks(y); a.set_yticklabels([elab(f, t) for f, t in zip(cr["from"], cr["to"])],
                                           fontsize=7)
        a.set_xlabel("Cross-lagged weight (LOPO range)"); a.set_title("Leave-one-out refits")
    else:
        _blank(a, "n/a")
    vs.panel_label(a, "B")

    a = ax[1, 0]
    if det is not None:
        a.scatter(det["weight_ref"], det["weight_detrended"], s=26, color=vs.NODE_COLORS["PIJN"],
                  alpha=0.7)
        lim = [det[["weight_ref", "weight_detrended"]].min().min() - 0.05,
               det[["weight_ref", "weight_detrended"]].max().max() + 0.05]
        a.plot(lim, lim, color=vs.INK, lw=1, ls="--")
        a.set_xlabel("Primary weight"); a.set_ylabel("Detrended weight")
        a.set_title("Detrended vs primary")
    else:
        _blank(a, "n/a")
    vs.panel_label(a, "C")

    a = ax[1, 1]
    agree = _agreement_table()
    a.barh(agree["analysis"], agree["r"], color=vs.MUTED)
    a.set_xlim(min(0.9, agree["r"].min() - 0.02), 1.005)
    a.set_xlabel("r with primary temporal network"); a.set_title("Sensitivity agreement")
    a.tick_params(axis="y", labelsize=8); vs.bar_axes(a, "horizontal"); vs.panel_label(a, "D")
    fig.tight_layout(h_pad=2.2, w_pad=2.6)
    vs.savefig(fig, FIG / "SUP_07_robustness.png")


def _agreement_table():
    rows = []
    def rr(name, f, a, b):
        d = opt(N / f)
        if d is not None and a in d and b in d:
            rows.append({"analysis": name, "r": round(np.corrcoef(d[a], d[b])[0, 1], 3)})
    rr("Detrended", "robust_detrended_compare.csv", "weight_ref", "weight_detrended")
    rr("Attention composite", "robust_attention_composite_compare.csv", "weight_ref",
       "weight_attcomposite")
    rr("Compliance >= 70", "robust_threshold70_compare.csv", "weight_ref", "weight_thr70")
    rr("Extended six-node", "extended_core_vs_full_compare.csv", "weight_core4", "weight_extended")
    if not rows:
        rows = [{"analysis": "n/a", "r": np.nan}]
    return pd.DataFrame(rows)


# --- SUP_08 daily dysfunction (4 panels) ------------------------------------
def sup_08():
    ema = pd.read_csv(paths.EMA_LONG)
    mod = pd.read_csv(T / "11_daily_dysfunction_models.csv")
    desc = pd.read_csv(T / "11_daily_dysfunction_descriptives.csv")
    fig, ax = plt.subplots(2, 2, figsize=(10.6, 7.6))

    a = ax[0, 0]
    m = mod[mod["term"] != "(Intercept)"].copy()
    outs = m["outcome"].unique(); terms = m["term"].unique()
    x = np.arange(len(terms)); w = 0.38
    for k, o in enumerate(outs):
        s = m[m["outcome"] == o].set_index("term").reindex(terms)
        a.bar(x + (k - 0.5) * w, s["estimate"], w, yerr=1.96 * s["SE"], capsize=2,
              label=o.replace("eve_", "").replace("_", " "), color=vs.CLUSTER_COLORS[k])
    a.axhline(0, color=vs.INK, lw=0.8); a.set_xticks(x)
    a.set_xticklabels([t.replace("_wc", "") for t in terms], rotation=15, fontsize=8)
    a.set_ylabel("Within-person day-level estimate")
    a.set_title("Day experience -> evening functioning")
    a.legend(fontsize=8); vs.bar_axes(a); vs.panel_label(a, "A")

    a = ax[0, 1]
    a.barh(desc["pair"], desc["within_person_r"], color=vs.NODE_COLORS["ENGAGE"])
    a.axvline(0, color=vs.INK, lw=0.8); a.set_xlabel("Within-person day-level correlation")
    a.set_title("Day-level couplings"); a.tick_params(axis="y", labelsize=8)
    vs.bar_axes(a, "horizontal"); vs.panel_label(a, "B")

    # day-level scatter: day-mean pain vs evening interference (within-person centered)
    agg = ema.groupby(["pid", "day"]).agg(pain=("PIJN", "mean"),
                                          interf=("eve_pain_interference", "mean"),
                                          goal=("eve_goal_success", "mean")).reset_index()
    for col in ["pain", "interf", "goal"]:
        agg[col + "_wc"] = agg[col] - agg.groupby("pid")[col].transform("mean")

    a = ax[1, 0]
    s = agg.dropna(subset=["pain_wc", "interf_wc"])
    a.scatter(s["pain_wc"], s["interf_wc"], s=8, color=vs.NODE_COLORS["PIJN"], alpha=0.3,
              edgecolor="none")
    a.axhline(0, color=vs.MUTED, lw=0.6); a.axvline(0, color=vs.MUTED, lw=0.6)
    a.set_xlabel("Day pain (within-person)"); a.set_ylabel("Evening interference (within-person)")
    a.set_title("Day pain and evening interference"); vs.panel_label(a, "C")

    a = ax[1, 1]
    dist = ema[["eve_pain_interference", "eve_goal_success", "eve_pain_control"]].dropna(how="all")
    parts = [ema[c].dropna().values for c in
             ["eve_goal_success", "eve_pain_control", "eve_pain_interference"]]
    vp = a.violinplot(parts, showmedians=True)
    for b in vp["bodies"]:
        b.set_facecolor(vs.NODE_COLORS["THREAT"]); b.set_alpha(0.5)
    a.set_xticks([1, 2, 3]); a.set_xticklabels(["Goal\nsuccess", "Pain\ncontrol", "Pain\ninterf."],
                                               fontsize=8)
    a.set_ylabel("Evening rating (1-7)"); a.set_title("Evening outcome distributions")
    vs.panel_label(a, "D")
    fig.tight_layout(h_pad=2.4, w_pad=2.6)
    vs.savefig(fig, FIG / "SUP_08_daily_dysfunction.png")


# --- SUP_09 context (4 panels) ----------------------------------------------
def sup_09():
    ema = pd.read_csv(paths.EMA_LONG)
    loc = pd.read_csv(T / "02_context_by_location.csv")
    sw = pd.read_csv(T / "02_studyweek_effects.csv")
    fig, ax = plt.subplots(2, 2, figsize=(10.6, 7.6))

    a = ax[0, 0]
    a.bar(loc["location_lab"], loc["pct"], color=vs.MUTED)
    a.set_ylabel("% of prompts"); a.set_title("Where prompts occurred")
    a.tick_params(axis="x", rotation=20); vs.bar_axes(a); vs.panel_label(a, "A")

    a = ax[0, 1]
    lm = loc.set_index("location_lab")[["mean_pain", "mean_attend", "mean_engage"]]
    lm.plot(kind="bar", ax=a, color=[vs.NODE_COLORS["PIJN"], vs.NODE_COLORS["ATTEND"],
                                     vs.NODE_COLORS["ENGAGE"]], width=0.8, legend=True)
    a.set_ylabel("Mean rating"); a.set_title("Momentary states by location")
    a.legend(["Pain", "Attention", "Engagement"], fontsize=7)
    a.tick_params(axis="x", rotation=20); vs.bar_axes(a); vs.panel_label(a, "B")

    a = ax[1, 0]
    for lab, val in [("Alone", 1), ("Accompanied", 0)]:
        sub = ema[ema["alone"] == val]
        a.scatter([lab] * 0, [])  # keep order
    grp = ema.dropna(subset=["alone"]).groupby("alone")[["PIJN", "ATTEND", "ENGAGE"]].mean()
    grp.index = ["Accompanied" if i == 0 else "Alone" for i in grp.index]
    grp.plot(kind="bar", ax=a, color=[vs.NODE_COLORS["PIJN"], vs.NODE_COLORS["ATTEND"],
                                      vs.NODE_COLORS["ENGAGE"]], width=0.8)
    a.set_ylabel("Mean rating"); a.set_title("Momentary states by social context")
    a.legend(["Pain", "Attention", "Engagement"], fontsize=7)
    a.tick_params(axis="x", rotation=0); vs.bar_axes(a); vs.panel_label(a, "C")

    a = ax[1, 1]
    y = np.arange(len(sw))
    cols = [vs.EDGE_POS if b >= 0 else vs.EDGE_NEG for b in sw["week2_beta"]]
    a.barh(y, sw["week2_beta"], xerr=1.96 * sw["week2_se"], color=cols, capsize=2)
    a.set_yticks(y); a.set_yticklabels([vs.node_label_long(v) for v in sw["variable"]], fontsize=8)
    a.axvline(0, color=vs.INK, lw=0.8); a.set_xlabel("Week 2 minus week 1 (SD units)")
    a.set_title("Time-in-study drift"); vs.panel_label(a, "D")
    fig.tight_layout(h_pad=2.4, w_pad=2.6)
    vs.savefig(fig, FIG / "SUP_09_context.png")


# --- SUP_10 within vs between correlations (3 panels) -----------------------
def sup_10():
    wc = pd.read_csv(T / "02_within_person_corr.csv").set_index("variable")[EXT].loc[EXT]
    bc = pd.read_csv(T / "02_between_person_corr.csv").set_index("variable")[EXT].loc[EXT]
    fig, ax = plt.subplots(1, 3, figsize=(13.5, 4.6))
    labs = [vs.node_label(v) for v in EXT]

    def heat(a, M, title):
        im = a.imshow(M, cmap="RdBu_r", vmin=-1, vmax=1)
        a.set_xticks(range(len(EXT))); a.set_yticks(range(len(EXT)))
        a.set_xticklabels(labs, rotation=35, ha="right", fontsize=7)
        a.set_yticklabels(labs, fontsize=7)
        for i in range(len(EXT)):
            for j in range(len(EXT)):
                a.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center", fontsize=6,
                       color=vs.INK if abs(M[i, j]) < 0.6 else "white")
        a.set_title(title); vs.matrix_axes(a)
        return im

    heat(ax[0], wc.values, "A  Within-person"); vs.panel_label(ax[0], "A")
    heat(ax[1], bc.values, "B  Between-person"); vs.panel_label(ax[1], "B")
    im = heat(ax[2], bc.values - wc.values, "C  Between minus within")
    vs.add_cbar(fig, ax[2], im, label="r"); vs.panel_label(ax[2], "C")
    fig.tight_layout(w_pad=2.2)
    vs.savefig(fig, FIG / "SUP_10_within_between_correlations.png")


def main():
    np.random.seed(20260703)
    for fn in [sup_01, sup_02, sup_03, sup_04, sup_05, sup_06, sup_07, sup_08, sup_09, sup_10]:
        try:
            fn()
        except Exception as e:
            print(f"  WARNING: {fn.__name__} failed: {e}")
    print("supplementary figures written to", FIG)


if __name__ == "__main__":
    main()
