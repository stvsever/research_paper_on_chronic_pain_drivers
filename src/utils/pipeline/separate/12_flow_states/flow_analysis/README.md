# Flow analysis

Standalone, fully documented analysis of the flow construct in this dataset. Written to be read
end to end by someone deciding whether the construct earns a place in the manuscript.

| File | What it is |
| --- | --- |
| [`analyze_flow.ipynb`](analyze_flow.ipynb) | The full analysis, with every cell pre-run. Sections 1 to 13 plus a cross-validation appendix. Start here. |
| [`flow_operationalization.md`](flow_operationalization.md) | Compact specification, decision record, and results summary, for reading without running anything. |
| `figures/` | The six figures the notebook generates. |

The notebook re-estimates every model in Python, independently of the R pipeline in the parent
directory (stage 12). Appendix A compares the two implementations coefficient by coefficient; they
agree to within 0.008.

**The manuscript has not been modified.** The manuscript-shaped figures and tables are generated
by stage 13 but nothing inputs them, so adding the section later is a matter of two `\input` lines
and one `\includegraphics`.

To reproduce: run all cells in the notebook, or `make run-stage STAGE=12` for the R side.
