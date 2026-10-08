"""Build the interactive sixpack notebook from ``src/sixpack_report.py``.

The generator functions save each report to disk and immediately close the
figure, so nothing would render inside Jupyter. This script emits a
notebook that installs a small ``savefig`` hook: the figure is displayed
inline at the moment it is written, then closed as usual. The result is a
notebook that shows every report *and* keeps writing the PNG files.
"""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf

REPO = Path(__file__).resolve().parent
OUT = REPO / "notebooks" / "capability_reports.ipynb"
FONT_DIR = "src/assets/fonts/plus_jakarta_sans"

nb = nbf.v4.new_notebook()
cells: list = []


def md(text: str) -> None:
    cells.append(nbf.v4.new_markdown_cell(text.strip("\n")))


def code(text: str) -> None:
    cells.append(nbf.v4.new_code_cell(text.strip("\n")))


# --------------------------------------------------------------------------
md(
    """
# Minitab-Style Capability Reports

Interactive companion to `src/sixpack_report.py`.

Everything the CLI can produce, rendered **inline** — no PNG round-trip,
no reopening files:

| Report | What it answers |
|---|---|
| **Capability Sixpack** | Is the process in control *and* capable? |
| **Capability Analysis (Normal)** | Cp / Cpk / Pp / Ppk plus PPM defect rates |
| **Gage R&R (ANOVA)** | Can the measurement system be trusted? |
| **MSA Assistant** | Plain-language pass/fail against AIAG guidelines |

The module is imported, not re-implemented, so these notebooks and the
`python src/sixpack_report.py` CLI always produce identical output.
"""
)

md("## 1. Setup")

code(
    f"""
# Make the report module importable from the notebook.
import sys
from pathlib import Path

REPO = Path.cwd()
if not (REPO / "src" / "sixpack_report.py").exists():
    # Fall back to walking up when the notebook runs from notebooks/
    REPO = next(p for p in [Path.cwd(), *Path.cwd().parents]
                if (p / "src" / "sixpack_report.py").exists())

sys.path.insert(0, str(REPO / "src"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import Image, display

import sixpack_report as sr

print("sixpack_report loaded from:", sr.__file__)
print("Public API:", ", ".join(
    n for n in dir(sr) if n.startswith("generate_")
))
"""
)

md(
    """
### Inline display hook

`generate_*` calls `fig.savefig(...)` then `plt.close(fig)`. We wrap
`savefig` so the figure is displayed **at save time**, while it is still
open, and the PNG is still written to disk exactly as before.
"""
)

code(
    """
import matplotlib

_real_savefig = matplotlib.figure.Figure.savefig


def _savefig_and_display(self, *args, **kwargs):
    \"\"\"Write the PNG (original behaviour), then render it inline.\"\"\"
    result = _real_savefig(self, *args, **kwargs)
    display(self)
    return result


matplotlib.figure.Figure.savefig = _savefig_and_display
print("Inline display hook installed.")
"""
)

md("## 2. Data and specifications")

code(
    """
# Minitab's "Demo data" style process measurement, centred at 104.6.
values = sr._synthetic_data(seed=42)
specs = sr.CapabilitySpecs(lsl=103.0, usl=110.0, target=104.0)

summary = pd.DataFrame({
    "Statistic": ["Observations", "Mean", "Std Dev (overall)",
                  "Min", "Max", "LSL", "USL", "Target"],
    "Value": [
        len(values), f"{values.mean():.3f}", f"{values.std(ddof=1):.3f}",
        f"{values.min():.3f}", f"{values.max():.3f}",
        f"{specs.lsl:.3f}", f"{specs.usl:.3f}", f"{specs.target:.3f}",
    ],
})
summary
"""
)

md(
    """
## 3. Capability Sixpack

The sixpack combines six views into one report:

1. **I-Chart** — are individual measurements in statistical control?
2. **Histogram** — how is the data distributed against the spec limits?
3. **MR-Chart** — is the *short-term* (within) variation stable?
4. **Normal Probability Plot** — is the normality assumption justified?
5. **Last 25 Observations** — what is the process doing right now?
6. **Capability Plot** — how does spread compare to the spec window?

> A capable-but-unstable process and a stable-but-incapable process are
> different problems. The sixpack shows both at once.
"""
)

code(
    """
sixpack_path = REPO / "output" / "sixpack_report.png"

stats = sr.generate_sixpack(
    values,
    specs,
    "Process Capability Sixpack Report",
    sixpack_path,
)
print(f"Saved to {sixpack_path}")
"""
)

code(
    """
capability_table = pd.DataFrame({
    "Index": ["Cp", "Cpk", "Pp", "Ppk", "Cpm"],
    "Value": [stats.cp, stats.cpk, stats.pp, stats.ppk, stats.cpm],
})
capability_table.index = capability_table["Index"]
capability_table.round(3)
"""
)

md(
    """
**How to read it:** the gap between `Cpk` and `Cp` tells you how far the
mean sits from the centre of the spec window. A large gap means the process
is *centred* poorly even if its spread is acceptable — recentre before
investing in variation reduction.
"""
)

md(
    """
## 4. Capability Analysis (Normal)

The focused view: the capability histogram plus overall / within indices and
observed-versus-expected defect rates in parts per million.
"""
)

code(
    """
analysis_path = REPO / "output" / "capability_analysis_report.png"

result = sr.generate_capability_analysis(
    values,
    specs,
    "Process Capability Report for data",
    analysis_path,
)
print(f"Saved to {analysis_path}")
"""
)

code(
    """
performance = result.performance

ppm_table = pd.DataFrame({
    "Defect region": ["Below LSL", "Above USL", "Total"],
    "Observed": [f"{v:,.0f}" for v in performance.observed],
    "Expected Overall": [f"{v:,.0f}" for v in performance.expected_overall],
    "Expected Within": [f"{v:,.0f}" for v in performance.expected_within],
})
ppm_table
"""
)

code(
    """
normality = pd.DataFrame({
    "Statistic": ["Anderson-Darling", "p-value"],
    "Value": [f"{stats.ad_stat:.3f}", f"{stats.ad_p_value:.4f}"],
})
normality
"""
)

md(
    """
**Observed vs expected** is the practical takeaway. When observed defects
substantially exceed the *within* estimate but track the *overall* estimate,
the process has drift or special-cause variation that a capability index
alone would hide.
"""
)

md(
    """
## 5. Gage R&R (ANOVA) Study

Ten parts, three operators, three replicate measurements each. Answers the
only question that matters before trusting any measurement: *how much of the
observed variation is the measurement system rather than the parts?*
"""
)

code(
    """
gage_records = sr._synthetic_gage_rr_data(parts_count=10, operators_count=3, seed=42)
gage_specs = sr.GageRrSpecs(
    tolerance=8.0,
    gage_name="Calipers",
    reported_by="Quality Engineer",
)

gage_path = REPO / "output" / "gage_rr_report.png"
assistant_path = REPO / "output" / "gage_rr_assistant.png"

gage_result = sr.generate_gage_rr_report(
    gage_records,
    "Gage R&R (ANOVA) Report for Measurement",
    gage_path,
    specs=gage_specs,
    assistant_output_path=assistant_path,
)
print(f"Report saved to    {gage_path}")
print(f"Assistant saved to {assistant_path}")
"""
)

code(
    """
print(sr._format_table(gage_result.anova_with_interaction))
print()
if gage_result.anova_without_interaction is not None:
    print(sr._format_table(gage_result.anova_without_interaction))
"""
)

code(
    """
print(sr._format_table(gage_result.variance_components))
print()
print(sr._format_table(gage_result.gage_evaluation))
print()
print(f"Number of Distinct Categories = {gage_result.distinct_categories}")
print(f"Interaction p-value          = {gage_result.interaction_p_value:.4f}")
"""
)

md("### Interpretation")

code(
    """
# The evaluation table carries "%Study Var" for Total Gage R&R; pull it out
# and apply the AIAG thresholds to it.
eval_table = gage_result.gage_evaluation
study_col = eval_table.columns.index("%Study Var")
pct_study = float(
    next(row[study_col] for row in eval_table.rows if row[0] == "Total Gage R&R")
)

# _assessment_for_percent returns (status, verdict).
status, verdict = sr._assessment_for_percent(pct_study)
display(pd.DataFrame({
    "Measure": ["%Study Variation", "Acceptable?", "Assessment"],
    "Value": [f"{pct_study:.1f}%", status, verdict],
}))
"""
)

md(
    """
| %Study Var | Verdict |
|---|---|
| < 10% | Acceptable |
| 10 – 30% | Marginal — application dependent |
| > 30% | Unacceptable — improve the measurement system |

The **MSA Assistant** panel above renders the same verdict as a gauge, which
is easier to read in a design review than a table of percentages.
"""
)

md(
    """
## 6. Bringing your own data

The report functions take plain sequences, so real measurement data drops
straight in. Replace the three values below with your own.
"""
)

code(
    """
my_values = [
    104.0, 104.4, 103.8, 105.1, 104.9,
    105.2, 104.7, 104.1, 104.6, 105.0,
    104.3, 105.5, 103.9, 104.8, 105.1,
]
my_specs = sr.CapabilitySpecs(lsl=103.0, usl=110.0, target=104.0)

my_path = REPO / "output" / "my_process_sixpack.png"

my_stats = sr.generate_sixpack(
    my_values,
    my_specs,
    "Capability Sixpack — My Process",
    my_path,
)
print(f"Saved to {my_path}")
print(f"Mean = {my_stats.mean:.3f}   Cpk = {my_stats.cpk:.3f}")
"""
)

md(
    """
Gage R&R works the same way — pass a list of `GageRrRecord(part, operator,
measurement)`. A `pandas.DataFrame` with those three columns can be converted
with a comprehension:

```python
records = [
    sr.GageRrRecord(row.part, row.operator, row.measurement)
    for row in df.itertuples()
]
```
"""
)

md(
    """
## 7. Command line

The same three reports are available without writing any code:

```bash
python src/sixpack_report.py --download-fonts               # sixpack
python src/sixpack_report.py --capability-analysis          # capability analysis
python src/sixpack_report.py --gage-rr                      # gage R&R + assistant
```

Useful flags: `--gage-parts N`, `--gage-operators N` control the synthetic
study size; `--no-fonts` skips the Plus Jakarta Sans download.

Notebook kernel used to build this report: `src/sixpack_report.py` via
`import sixpack_report as sr`.
"""
)

nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
    "language_info": {"name": "python", "version": "3.11"},
}

OUT.parent.mkdir(parents=True, exist_ok=True)
nbf.write(nb, str(OUT))
print(f"wrote {OUT}  ({len(cells)} cells)")
