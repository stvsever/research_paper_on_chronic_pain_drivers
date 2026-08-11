# Flow analysis

Standalone, fully documented analysis of the flow construct in this dataset. Written to be read
end to end by someone deciding whether the construct earns a place in the manuscript.

| File | What it is |
| --- | --- |
| [`analyze_flow.ipynb`](analyze_flow.ipynb) | The reporting layer, with every cell pre-run. Sections 1 to 13 plus a provenance appendix. Start here. |
| [`flow_operationalization.md`](flow_operationalization.md) | Compact specification, decision record, and results summary, for reading without opening the notebook. |
| `figures/` | The six figures the notebook generates. |

**Division of labour.** All models are estimated by the scripts in `../scripts/`
(`01_flow_construct.R`, `02_flow_pain_models.R`, `03_flow_trait_link.py`), which run inside
`make run-all`. The notebook fits nothing: it reads their result tables, renders them, draws the
figures, and interprets the findings. Appendix A of the notebook maps every result to the script
and the file that produced it.

To regenerate the numbers: `make run-stage STAGE=12`, then re-run the notebook.
