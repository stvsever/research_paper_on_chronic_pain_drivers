"""Shared visual identity for all figures.

A single, restrained palette and a set of matplotlib rcParams so every figure in the
paper looks like it belongs to the same study. No figure-level suptitles are added here
(panels carry their own titles), in line with the project figure convention.
"""
from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
INK = "#1d2733"          # near-black for text and axes
MUTED = "#5b6b7b"        # secondary text
GRID = "#dfe5ec"         # faint gridlines
PANEL_BG = "#ffffff"

# Node colors. Stable across every figure so a construct is always the same hue.
# The analytic node keys operationalize the interruptive-function model of pain
# (Eccleston & Crombez, 1999): pain, its threat value, attention to pain, and the
# goal-directed activity that pain interrupts.
NODE_COLORS = {
    "PIJN": "#c1483f",       # pain intensity        - warm red
    "THREAT": "#9b59b6",     # threat value          - violet
    "ATTEND": "#2a7f9e",     # attention to pain     - teal/blue
    "ENGAGE": "#3a9e6e",     # goal engagement       - green
    "EFFIC": "#d98a3d",      # goal efficacy         - amber
    "VALENCE": "#8a6d3b",    # activity valence      - brown
}

# Pretty labels for nodes (English, concise). Single-line so they fit inside network nodes;
# figure panels that want longer names expand these where needed.
NODE_LABELS = {
    "PIJN": "Pain",
    "THREAT": "Threat",
    "ATTEND": "Attention",
    "ENGAGE": "Engage",
    "EFFIC": "Efficacy",
    "VALENCE": "Valence",
}

# Longer descriptive labels for bar/axis contexts.
NODE_LABELS_LONG = {
    "PIJN": "Pain intensity",
    "THREAT": "Threat value",
    "ATTEND": "Attention to pain",
    "ENGAGE": "Goal engagement",
    "EFFIC": "Goal efficacy",
    "VALENCE": "Activity valence",
}

# Diverging edge colors (positive = blue, negative = red), colorblind-safe.
EDGE_POS = "#2166ac"
EDGE_NEG = "#b2182b"

# Sequential accent for groups / clusters.
CLUSTER_COLORS = ["#2a7f9e", "#c1483f", "#3a9e6e", "#d98a3d", "#9b59b6"]

# Baseline trait-model colors (RQ2: threat vs biomedical vs personality accounts).
TRAIT_COLORS = {
    "Threat": "#c1483f",
    "Biomedical": "#2a7f9e",
    "Personality": "#8a6d3b",
}


def apply_style() -> None:
    """Apply the project matplotlib style globally."""
    mpl.rcParams.update({
        "figure.dpi": 120,
        "savefig.dpi": 300,
        "figure.facecolor": PANEL_BG,
        "axes.facecolor": PANEL_BG,
        "savefig.facecolor": PANEL_BG,
        "savefig.bbox": "tight",
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.labelsize": 10,
        "axes.edgecolor": MUTED,
        "axes.linewidth": 0.8,
        "axes.labelcolor": INK,
        "axes.titlecolor": INK,
        "text.color": INK,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.7,
        "legend.frameon": False,
        "legend.fontsize": 9,
    })


def panel_label(ax, letter: str, dx: float = -0.08, dy: float = 1.06) -> None:
    """Add a bold panel letter (A, B, C ...) in axis-fraction coordinates."""
    ax.text(dx, dy, letter, transform=ax.transAxes,
            fontsize=13, fontweight="bold", va="top", ha="right", color=INK)


def add_cbar(fig, ax, mappable=None, size: str = "5%", pad: float = 0.12, label=None,
             **kwargs):
    """Append a fixed-width colorbar axis to the right of ``ax``.

    When ``mappable`` is given a colorbar is drawn; otherwise the appended axis is hidden
    and acts only as a spacer. Applying this to every panel in a grid (a real colorbar
    where needed, a hidden spacer elsewhere) keeps all panels exactly the same plotting
    width, so heatmap panels stay centred over the panels above or below them.
    """
    from mpl_toolkits.axes_grid1 import make_axes_locatable

    cax = make_axes_locatable(ax).append_axes("right", size=size, pad=pad)
    if mappable is not None:
        cb = fig.colorbar(mappable, cax=cax, **kwargs)
        if label:
            cb.set_label(label, fontsize=8)
    else:
        cax.axis("off")
    return cax


def strip_axis_frame(ax) -> None:
    """Remove axis spines and tick marks while retaining labels and grid."""
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="both", which="both", length=0)


def bar_axes(ax, orientation: str = "vertical") -> None:
    """Grid on the value axis only; full axis frame and tick labels retained."""
    if orientation == "horizontal":
        ax.grid(axis="x", visible=True)
        ax.grid(axis="y", visible=False)
    elif orientation == "none":
        ax.grid(False)
    else:  # vertical
        ax.grid(axis="y", visible=True)
        ax.grid(axis="x", visible=False)


def matrix_axes(ax, remove_axis_labels: bool = True) -> None:
    """Clean heatmap/matrix panels while keeping row and column tick labels."""
    ax.grid(False)
    strip_axis_frame(ax)
    if remove_axis_labels:
        ax.set_xlabel("")
        ax.set_ylabel("")


def node_color(name: str) -> str:
    return NODE_COLORS.get(name, MUTED)


def node_label(name: str) -> str:
    return NODE_LABELS.get(name, name)


def node_label_long(name: str) -> str:
    return NODE_LABELS_LONG.get(name, name)


def savefig(fig, path, **kwargs):
    """Save a figure at publication resolution and report the path."""
    fig.savefig(path, **kwargs)
    plt.close(fig)
    print(f"  saved figure: {path}")
