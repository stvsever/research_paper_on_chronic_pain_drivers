"""Shared LaTeX (booktabs) table builders for the manuscripts.

Layout rules live here so that every table in both papers looks the same: caption above the
table, note below, left-aligned, ``tabular*`` stretched to the text width. Stage 13 builds
the tables of manuscript 01 and stage 14 those of manuscript 02; both import this module.
"""
from __future__ import annotations

import re

import pandas as pd


def esc(value) -> str:
    """Escape a cell value for LaTeX, leaving intentional markup intact.

    Escaping is idempotent: a character that the caller already escaped is left alone, so a
    header written as ``95\\% CI`` does not become ``95\\\\% CI``. Cells containing ``$`` are
    treated as deliberate math and passed through untouched.
    """
    s = "" if pd.isna(value) else str(value)
    if "$" in s:            # already math or deliberately marked up by the caller
        return s
    for pat, rep in [(r"(?<!\\)&", r"\\&"), (r"(?<!\\)%", r"\\%"),
                     (r"(?<!\\)_", r"\\_"), (r"(?<!\\)~", r"\\textasciitilde{}")]:
        s = re.sub(pat, rep, s)
    for a, b in [("->", r"$\rightarrow$"), (">=", r"$\geq$"), (">", r"$>$")]:
        s = s.replace(a, b)
    return s


def fmt_p(p) -> str:
    if pd.isna(p):
        return ""
    return "<.001" if p < .001 else f"{p:.3f}".lstrip("0")


def fmt_b(x, digits: int = 3) -> str:
    return "" if pd.isna(x) else f"{x:.{digits}f}"


def body(df, colspec):
    lines = [rf"\begin{{tabular*}}{{\textwidth}}{{@{{\extracolsep{{\fill}}}}{colspec}@{{}}}}",
             r"\toprule", " & ".join(esc(c) for c in df.columns) + r" \\", r"\midrule"]
    for _, row in df.iterrows():
        lines.append(" & ".join(esc(v) for v in row.values) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular*}"]
    return lines


def _open(caption, label, size, placement):
    return [rf"\begin{{table}}[{placement}]", r"\raggedright", rf"\caption{{{caption}}}",
            rf"\label{{{label}}}", size, r"\begingroup",
            r"\setlength{\tabcolsep}{4pt}", r"\renewcommand{\arraystretch}{1.08}"]


def latex_table(df, caption, label, colspec=None, note=None, size=r"\footnotesize",
                placement="!htbp"):
    if colspec is None:
        colspec = "l" + "r" * (len(df.columns) - 1)
    lines = _open(caption, label, size, placement) + [r"\noindent"]
    lines += body(df, colspec)
    if note:
        lines.append(rf"\par\vspace{{3pt}}\noindent\parbox{{\textwidth}}{{{size}\textit{{Note.}} {note}}}")
    lines += [r"\endgroup", r"\end{table}"]
    return "\n".join(lines) + "\n"


def panelled_table(panels, caption, label, note, size=r"\footnotesize",
                   placement="!htbp"):
    """Build a table of several labelled panels.

    ``panels`` is a sequence of ``(dataframe, colspec, panel_title)`` triples; panels are
    lettered A, B, C ... in order.
    """
    lines = _open(caption, label, size, placement)
    for k, (df, colspec, title) in enumerate(panels):
        letter = chr(ord("A") + k)
        gap = r"\noindent" if k == 0 else r"\par\vspace{6pt}\noindent"
        lines.append(rf"{gap}\textit{{Panel {letter}.}} {title}\par\vspace{{2pt}}")
        lines += body(df, colspec)
    lines.append(rf"\par\vspace{{3pt}}\noindent\parbox{{\textwidth}}{{{size}\textit{{Note.}} {note}}}")
    lines += [r"\endgroup", r"\end{table}"]
    return "\n".join(lines) + "\n"


def writer(out_main, out_supp):
    """Return a ``write(filename, content)`` bound to a manuscript's table directories."""
    def write(fname: str, content: str) -> None:
        out_dir = out_main if fname.startswith("MAIN_") else out_supp
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / fname).write_text(content)
        print("  wrote", out_dir / fname)
    return write
