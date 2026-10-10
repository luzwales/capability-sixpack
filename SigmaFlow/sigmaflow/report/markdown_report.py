"""
sigmaflow/report/markdown_report.py
=====================================
Markdown report generator — SigmaFlow.

Generates a professional Markdown report from SigmaFlow pipeline results.
Can be easily converted to PDF using pandoc or other tools.

Usage
-----
    from sigmaflow.report.markdown_report import MarkdownReportGenerator
    gen = MarkdownReportGenerator(results, output_dir="output/reports")
    md_path = gen.generate()
"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _e(text: Any) -> str:
    """Escape text for Markdown (basic escaping)."""
    if not isinstance(text, str):
        text = str(text)
    # Escape special Markdown characters
    text = text.replace("|", "\\|")
    return text


def _fmt(value: Any, decimals: int = 2) -> str:
    """Format numeric values."""
    if value is None:
        return "---"
    if isinstance(value, (int, float)):
        return f"{value:.{decimals}f}"
    return str(value)


class MarkdownReportGenerator:
    """
    Builds a professional Markdown report from SigmaFlow pipeline results.

    Parameters
    ----------
    results : list[dict]   Output from Engine.run()
    output_dir : str|Path  Where .md is saved
    title : str            Report title
    author : str           Author name
    """

    def __init__(
        self,
        results: List[Dict[str, Any]],
        output_dir: str | Path = "output/reports",
        title: str = "SigmaFlow — Automated DMAIC Analysis Report",
        author: str = "SigmaFlow Engine v8",
    ) -> None:
        self.results = results
        self.output_dir = Path(output_dir)
        self.title = title
        self.author = author

    # ── Public API ────────────────────────────────────────────────────────────

    def generate(self) -> str:
        """Generate the Markdown report and return the file path."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        md_path = self.output_dir / "process_analysis_report.md"

        md_path.write_text(self._build_document(), encoding="utf-8")
        logger.info("Markdown report written: %s", md_path)
        print(f"  Markdown report saved to: {md_path}")
        return str(md_path)

    # ── Full document ─────────────────────────────────────────────────────────

    def _build_document(self) -> str:
        ts = datetime.now().strftime("%d %B %Y, %H:%M")

        # Build TOC with DMAIC phases
        toc = self._build_dmaic_toc()

        # Build each dataset's DMAIC sections
        dataset_sections = []
        for r in self.results:
            dataset_sections.append(self._dataset_dmaic_section(r))

        return f"""# {_e(self.title)}

**Automated Lean Six Sigma / DMAIC Analysis**
**Engine:** {_e(self.author)}
**Date:** {_e(ts)}

---

## Table of Contents

{toc}

---

## Abstract

{self._build_abstract()}

---

## Introduction

{self._intro()}

---

## Methodology

{self._methodology()}

---

# DMAIC Analysis Results

{chr(10).join(dataset_sections)}

---

## Recommendations

{self._recommendations()}

---

## Conclusion

{self._conclusion()}

---

*Generated automatically by **SigmaFlow v8**. All outputs — figures, insights.json, and this report — are available in the `output/` directory.*
""".strip()

    # ── DMAIC TOC ─────────────────────────────────────────────────────────────

    def _build_dmaic_toc(self) -> str:
        """Build table of contents organized by DMAIC phases."""
        lines = [
            "1. [Abstract](#abstract)",
            "2. [Introduction](#introduction)",
            "3. [Methodology](#methodology)",
            "4. [DMAIC Analysis Results](#dmaic-analysis-results)",
        ]

        # Add each dataset with its DMAIC phases
        base_idx = 4
        for i, r in enumerate(self.results):
            idx = base_idx + i + 1
            name = _e(r.get("name", r.get("dataset", f"dataset_{idx}")))
            safe_name = name.lower().replace(" ", "-").replace("_", "-")
            lines.append(f"    {idx}. [{name}](#{safe_name})")
            lines.append(f"        - [📋 Define Phase](#{safe_name}-define)")
            lines.append(f"        - [📊 Measure Phase](#{safe_name}-measure)")
            lines.append(f"        - [🔍 Analyze Phase](#{safe_name}-analyze)")
            lines.append(f"        - [💡 Improve Phase](#{safe_name}-improve)")
            lines.append(f"        - [🎯 Control Phase](#{safe_name}-control)")

        lines.extend([
            f"{len(self.results) + 4}. [Recommendations](#recommendations)",
            f"{len(self.results) + 5}. [Conclusion](#conclusion)",
        ])

        return "\n".join(lines)

    # ── Fixed sections ────────────────────────────────────────────────────────

    def _build_abstract(self) -> str:
        abstracts = [r.get("abstract", "") for r in self.results if r.get("abstract")]
        if abstracts:
            return " ".join(_e(a) for a in abstracts)
        n = len(self.results)
        return (
            f"This report presents an automated statistical analysis performed by "
            f"the SigmaFlow v8 engine. A total of {n} dataset(s) were evaluated using "
            f"Statistical Process Control (SPC) and Six Sigma methodologies. "
            f"Results include control chart analysis, process capability indices, "
            f"Western Electric rule evaluation, and root cause correlation analysis. "
            f"Findings are presented with interpretations and recommendations."
        )

    def _intro(self) -> str:
        n = len(self.results)

        # Build summary table
        table_rows = []
        for r in self.results:
            name = _e(r.get("name", r.get("dataset", "?")))
            dtype = _e(r.get("dataset_type", r.get("type", "?")).upper())
            shape = r.get("shape")
            if shape and isinstance(shape, (list, tuple)) and len(shape) >= 2:
                shape_str = f"{shape[0]}×{shape[1]}"
            else:
                shape_str = "—"
            elapsed = _e(r.get("elapsed_s", "?"))
            n_insights = len(r.get("structured_insights", r.get("insights", [])))
            table_rows.append(f"| {name} | {dtype} | {shape_str} | {elapsed}s | {n_insights} |")

        table = "\n".join([
            "| Dataset | Type | Shape | Time | Insights |",
            "|---------|------|-------|------|----------|",
        ] + table_rows)

        return f"""This report was automatically generated by **SigmaFlow v8**, a modular Python framework for industrial process analysis. A total of **{n} dataset(s)** were processed through the complete DMAIC analysis pipeline.

The analysis follows the **DMAIC methodology** — a data-driven quality strategy consisting of five phases:

| Phase | Icon | Purpose |
|-------|------|---------|
| **Define** | 📋 | Define the problem, project goals, and customer deliverables |
| **Measure** | 📊 | Measure the current process and collect data |
| **Analyze** | 🔍 | Analyze data to identify root causes of defects |
| **Improve** | 💡 | Improve the process by eliminating root causes |
| **Control** | 🎯 | Control future process performance |

### Summary

{table}"""

    def _methodology(self) -> str:
        return """The following statistical methods and tools are employed in this analysis:

### Statistical Process Control (SPC)

Control charts are used to distinguish between *common-cause variation* (inherent randomness) and *special-cause variation* (assignable, non-random events). The **XmR chart** (Individuals and Moving Range) is used for individual observations. Control limits are set at μ ± 3σ.

### Western Electric Rules

Four detection rules are applied to identify non-random patterns:

- **Rule 1** — Any single point outside ±3σ limits (probability ≈ 0.27% under normality)
- **Rule 2** — Nine consecutive points on the same side of the center line (probability ≈ 0.4%)
- **Rule 3** — Six consecutive points trending upward or downward (indicates drift)
- **Rule 4** — Fourteen consecutive points alternating direction (indicates over-adjustment or dual-stream process)

### Process Capability Indices

When specification limits are available, the following indices are computed:

| Index | Formula | Interpretation |
|-------|---------|----------------|
| Cp | (USL - LSL) / 6σ | Potential capability (centered) |
| Cpk | min(Cpu, Cpl) | Actual capability (off-centering penalty) |
| Cpu | (USL - μ) / 3σ | Upper one-sided capability |
| Cpl | (μ - LSL) / 3σ | Lower one-sided capability |

**Capability thresholds:**

- Cpk < 1.00 → Process **not capable** (critical)
- 1.00 ≤ Cpk < 1.33 → **Marginal** capability (warning)
- 1.33 ≤ Cpk < 1.67 → **Acceptable** capability
- Cpk ≥ 1.67 → **Excellent** (Six Sigma level)

### Root Cause Analysis

Pearson and Spearman rank correlations are computed between all process variables and the primary quality output. Variables are ranked by absolute correlation to identify the most likely process drivers.

| \|r\| threshold | Strength |
|-----------------|----------|
| \|r\| ≥ 0.70 | Strong association — high priority investigation |
| 0.50 ≤ \|r\| < 0.70 | Moderate association — medium priority |
| 0.30 ≤ \|r\| < 0.50 | Weak association — monitor |
| \|r\| < 0.30 | Negligible |"""

    def _recommendations(self) -> str:
        totals = {"critical": 0, "warning": 0, "info": 0}
        for r in self.results:
            for ins in r.get("structured_insights", []):
                sev = ins.get("severity", "info")
                totals[sev] = totals.get(sev, 0) + 1

        # Gather all strong root cause candidates
        all_strong = []
        for r in self.results:
            rca = r.get("root_cause", {})
            if isinstance(rca, list):
                rca = {}
            for v in rca.get("ranked_variables", []):
                if abs(v.get("pearson_r", 0)) >= 0.70:
                    all_strong.append((r.get("name", r.get("dataset", "?")), v["variable"], v["pearson_r"]))

        rca_section = ""
        if all_strong:
            rows = "\n".join(
                f"| {_e(ds)} | {_e(var)} | {r:+.3f} |"
                for ds, var, r in all_strong[:10]
            )
            rca_section = f"""### Priority Variables for Investigation

The following variables showed strong correlation (|r| ≥ 0.70) with the quality target and should be investigated first:

| Dataset | Variable | Pearson r |
|---------|----------|-----------|
{rows}
"""

        return f"""Based on the automated analysis, the following actions are recommended:

1. **🚨 Address {totals['critical']} critical finding(s) immediately.** Investigate all points flagged by Western Electric rules outside 3σ limits. Document findings and corrective actions.

2. **⚠️ Review {totals['warning']} warning(s)** with the process engineering team. Schedule corrective actions within the next sprint cycle.

3. **Re-run SigmaFlow** after implementing improvements to verify effectiveness of corrective actions.

4. **Expand data collection** on variables identified in root cause analysis to confirm or refute correlation findings.

5. **Set up real-time monitoring** for datasets with out-of-control processes.

{rca_section}

> **Note:** All findings should be reviewed by a qualified process engineer before implementing corrective actions. Correlation does not imply causation."""

    def _conclusion(self) -> str:
        totals = {"critical": 0, "warning": 0, "info": 0}
        for r in self.results:
            for ins in r.get("structured_insights", []):
                sev = ins.get("severity", "info")
                totals[sev] = totals.get(sev, 0) + 1

        return f"""The SigmaFlow v8 automated analysis successfully processed **{len(self.results)} dataset(s)** and produced the following summary:

| Finding Category | Count |
|------------------|-------|
| 🔴 Critical (immediate action) | {totals['critical']} |
| 🟠 Warning (monitor / address) | {totals['warning']} |
| 🟢 Informational (stable) | {totals['info']} |

This report was generated automatically by **SigmaFlow v8**.
All outputs — figures, insights.json, report.md — are available in the `output/` directory.
Statistical findings and recommendations should be reviewed by a qualified Six Sigma practitioner or process engineer."""

    # ── DMAIC Dataset Section ─────────────────────────────────────────────────

    def _dataset_dmaic_section(self, r: Dict[str, Any]) -> str:
        """Build a complete DMAIC section for a single dataset."""
        name = _e(r.get("name", r.get("dataset", "unknown")))
        dtype = _e(r.get("dataset_type", r.get("type", "unknown")).upper())
        shape = r.get("shape")
        elapsed = r.get("elapsed_s", "?")
        safe_name = name.lower().replace(" ", "-").replace("_", "-")

        # Dataset header
        lines = [
            f"## {name}",
            "",
            f"**Type:** {dtype} | **Dimensions:** {shape[0]} rows × {shape[1]} columns | **Processing:** {elapsed}s" if shape else f"**Type:** {dtype} | **Processing:** {elapsed}s",
            "",
            "---",
            "",
        ]

        # Abstract/Summary
        abstract = r.get("abstract", "")
        if abstract:
            lines.extend([
                f"**Summary:** {_e(abstract)}",
                "",
                "---",
                "",
            ])

        # DMAIC Phases
        lines.extend([
            self._build_define_section(r, safe_name),
            self._build_measure_section(r, safe_name),
            self._build_analyze_section(r, safe_name),
            self._build_improve_section(r, safe_name),
            self._build_control_section(r, safe_name),
        ])

        return "\n\n".join(lines)

    def _build_define_section(self, r: Dict[str, Any], safe_name: str) -> str:
        """Build the Define phase section."""
        name = _e(r.get("name", r.get("dataset", "unknown")))
        lines = [
            f"### 📋 Define Phase <a id='{safe_name}-define'></a>",
            "",
            "#### Problem Statement",
            "",
        ]

        # Detection info
        det = r.get("detection") or {}
        problems = det.get("problems", []) if isinstance(det, dict) else []
        primary = det.get("primary_problem", "Unknown") if isinstance(det, dict) else "Unknown"
        response = det.get("response_variable", "—") if isinstance(det, dict) else "—"

        if problems:
            lines.append(f"- **Detected Problems:** {', '.join(p.upper() for p in problems)}")
        lines.append(f"- **Primary Problem:** {primary.upper()}")
        if response != "—":
            lines.append(f"- **Response Variable:** {response}")

        # Dataset overview
        shape = r.get("shape")
        if shape:
            lines.extend([
                "",
                "#### Dataset Overview",
                "",
                f"- **Dataset:** {name}",
                f"- **Dimensions:** {shape[0]} rows × {shape[1]} columns",
            ])

        # Analysis plan
        plan = r.get("analysis_plan", {})
        if plan:
            total_analyses = sum(len(v) for v in plan.values())
            lines.extend([
                "",
                "#### Analysis Plan",
                "",
                f"- **Total Analyses:** {total_analyses} across 5 DMAIC phases",
            ])
            for phase, analyses in plan.items():
                if analyses:
                    phase_name = phase.capitalize()
                    analysis_list = ", ".join(analyses[:5])
                    if len(analyses) > 5:
                        analysis_list += f" (+{len(analyses) - 5} more)"
                    lines.append(f"- **{phase_name}:** {analysis_list}")

        return "\n".join(lines)

    def _build_measure_section(self, r: Dict[str, Any], safe_name: str) -> str:
        """Build the Measure phase section."""
        lines = [
            f"### 📊 Measure Phase <a id='{safe_name}-measure'></a>",
            "",
        ]

        analysis = r.get("analysis", {})

        # Descriptive statistics
        desc = analysis.get("descriptive", {})
        if desc:
            lines.extend([
                "#### Descriptive Statistics",
                "",
                "| Metric | Value |",
                "|--------|-------|",
            ])
            for key, val in list(desc.items())[:10]:
                lines.append(f"| {_e(key)} | {_fmt(val, 4)} |")
            lines.append("")

        # Capability metrics
        cap = analysis.get("capability", {})
        if cap:
            lines.append(self._capability_measure_section(cap))

        # Normality tests
        normality = analysis.get("normality", {})
        if normality:
            lines.extend([
                "#### Normality Tests",
                "",
                "| Test | Statistic | p-value | Result |",
                "|------|-----------|---------|--------|",
            ])
            for test, result in normality.items():
                if isinstance(result, dict):
                    stat = _fmt(result.get("statistic"), 4)
                    pval = _fmt(result.get("pvalue"), 4)
                    is_normal = "Normal" if result.get("is_normal") else "Non-normal"
                    lines.append(f"| {_e(test)} | {stat} | {pval} | {is_normal} |")
            lines.append("")

        # Gauge R&R (MSA)
        grr = analysis.get("gauge_rr", {})
        if grr and not grr.get("error"):
            lines.extend([
                "#### Measurement System Analysis (Gauge R&R)",
                "",
                "| Metric | Value |",
                "|--------|-------|",
                f"| Study Variation | {_fmt(grr.get('study_variation'), 4)} |",
                f"| % Tolerance | {_fmt(grr.get('pct_tolerance'), 2)}% |",
                f"| % Contribution | {_fmt(grr.get('pct_contribution'), 2)}% |",
                f"| NDC | {_fmt(grr.get('ndc'), 1)} |",
                "",
            ])

        return "\n".join(lines)

    def _capability_measure_section(self, cap: Dict[str, Any]) -> str:
        """Build capability section for Measure phase."""
        cpk = cap.get("Cpk")
        cp = cap.get("Cp")
        if cpk is None:
            return ""

        if cpk >= 1.67:
            level, emoji = "Excellent (Six Sigma capable)", "🟢"
        elif cpk >= 1.33:
            level, emoji = "Acceptable", "🟢"
        elif cpk >= 1.00:
            level, emoji = "Marginal", "🟠"
        else:
            level, emoji = "Not Capable", "🔴"

        dpmo = cap.get("dpmo", 0)
        sigma = cap.get("sigma_level", 0)
        usl = cap.get("usl", "—")
        lsl = cap.get("lsl", "—")

        return f"""#### Process Capability Analysis

| Index | Value | Index | Value |
|-------|-------|-------|-------|
| Cp | {_fmt(cp, 3) if cp else '—'} | Cpk | **{emoji} {_fmt(cpk, 3)}** |
| USL | {usl} | LSL | {lsl} |
| DPMO | {f'{dpmo:,.0f}' if dpmo else '—'} | Sigma level | {f'{sigma:.2f}σ' if sigma else '—'} |

**Capability Verdict:** {emoji} **{level}**

"""

    def _build_analyze_section(self, r: Dict[str, Any], safe_name: str) -> str:
        """Build the Analyze phase section."""
        lines = [
            f"### 🔍 Analyze Phase <a id='{safe_name}-analyze'></a>",
            "",
        ]

        # Root cause analysis
        rca = r.get("root_cause", {})
        if isinstance(rca, list):
            rca = {}
        if rca and not rca.get("error"):
            target = _e(rca.get("target_col", "—"))
            ranked = rca.get("ranked_variables", [])
            interp = _e(rca.get("interpretation", ""))
            strong = rca.get("strong_candidates", [])

            lines.extend([
                "#### Root Cause Analysis",
                "",
                f"Correlation analysis performed using **{target}** as the quality target.",
                "",
            ])

            if interp:
                lines.extend([interp, ""])

            if ranked:
                lines.extend([
                    "##### Variable Importance Ranking",
                    "",
                    "| Variable | Pearson r | Spearman r | Strength |",
                    "|----------|-----------|------------|----------|",
                ])
                for v in ranked[:12]:
                    pr = v["pearson_r"]
                    sr = v["spearman_r"]
                    st = v["strength"].capitalize()
                    pr_fmt = f"**{_fmt(pr, 3)}**" if abs(pr) >= 0.70 else _fmt(pr, 3)
                    lines.append(f"| {_e(v['variable'])} | {pr_fmt} | {_fmt(sr, 3)} | {_e(st)} |")
                lines.append("")

            if strong:
                lines.extend([
                    f"**Strong Candidates:** {', '.join(_e(s) for s in strong[:5])}",
                    "",
                ])

            # Correlation heatmap + importance chart
            plots = r.get("plots", [])
            heatmap = next((p for p in plots if "heatmap" in p), None)
            varmap = next((p for p in plots if "importance" in p), None)
            for fig_path in filter(None, [heatmap, varmap]):
                lines.extend(self._figure_block(fig_path))

        # Statistical tests
        tests = r.get("analysis", {}).get("tests", {})
        if tests:
            lines.extend([
                "#### Statistical Tests",
                "",
                "| Test | Statistic | p-value | Result |",
                "|------|-----------|---------|--------|",
            ])
            for test_name, test_result in tests.items():
                if isinstance(test_result, dict):
                    stat = _fmt(test_result.get("statistic"), 4)
                    pval = _fmt(test_result.get("pvalue"), 4)
                    significant = "Significant" if test_result.get("significant") else "Not significant"
                    lines.append(f"| {_e(test_name)} | {stat} | {pval} | {significant} |")
            lines.append("")

        # Western Electric / anomaly insights
        structured = r.get("structured_insights", [])
        if structured:
            lines.append(self._anomaly_section(structured))

        return "\n".join(lines)

    def _build_improve_section(self, r: Dict[str, Any], safe_name: str) -> str:
        """Build the Improve phase section."""
        lines = [
            f"### 💡 Improve Phase <a id='{safe_name}-improve'></a>",
            "",
        ]

        # DOE results
        doe = r.get("analysis", {}).get("doe", {})
        if doe and not doe.get("error"):
            lines.extend([
                "#### Design of Experiments (DOE)",
                "",
            ])

            anova = doe.get("anova", {})
            if anova:
                lines.extend([
                    "##### ANOVA Results",
                    "",
                    "| Factor | F-value | p-value | Significant |",
                    "|--------|---------|---------|-------------|",
                ])
                for factor, result in anova.items():
                    if isinstance(result, dict):
                        fval = _fmt(result.get("f_statistic"), 4)
                        pval = _fmt(result.get("pvalue"), 4)
                        sig = "✓ Yes" if result.get("significant") else "✗ No"
                        lines.append(f"| {_e(factor)} | {fval} | {pval} | {sig} |")
                lines.append("")

            significant_factors = doe.get("significant_factors", [])
            if significant_factors:
                lines.extend([
                    "##### Significant Factors",
                    "",
                    f"**Factors with significant effect:** {', '.join(_e(f) for f in significant_factors)}",
                    "",
                ])

            optimal = doe.get("optimal_settings", {})
            if optimal:
                lines.extend([
                    "##### Optimal Settings",
                    "",
                    "| Factor | Optimal Level |",
                    "|--------|---------------|",
                ])
                for factor, level in optimal.items():
                    lines.append(f"| {_e(factor)} | {_e(level)} |")
                lines.append("")

        # Regression results
        regression = r.get("analysis", {}).get("regression", {})
        if regression and not regression.get("error"):
            lines.extend([
                "#### Regression Analysis",
                "",
                "| Metric | Value |",
                "|--------|-------|",
                f"| R² | {_fmt(regression.get('r_squared'), 4)} |",
                f"| Adjusted R² | {_fmt(regression.get('adjusted_r_squared'), 4)} |",
                f"| F-statistic | {_fmt(regression.get('f_statistic'), 4)} |",
                f"| p-value | {_fmt(regression.get('p_value'), 4)} |",
                "",
            ])

            coefficients = regression.get("coefficients", {})
            if coefficients:
                lines.extend([
                    "##### Coefficients",
                    "",
                    "| Variable | Coefficient | p-value |",
                    "|----------|-------------|---------|",
                ])
                for var, coef in coefficients.items():
                    if isinstance(coef, dict):
                        beta = _fmt(coef.get("coefficient"), 4)
                        pval = _fmt(coef.get("pvalue"), 4)
                        lines.append(f"| {_e(var)} | {beta} | {pval} |")
                lines.append("")

            # Regression plots
            plots = r.get("plots", [])
            reg_plots = [p for p in plots if any(kw in Path(p).name for kw in
                        ("regression", "actual_vs_predicted", "coefficients", "diagnostics"))]
            for p in reg_plots[:2]:
                lines.extend(self._figure_block(p))

        # FMEA results
        fmea = r.get("analysis", {}).get("fmea", {})
        if fmea and not fmea.get("error"):
            high_rpn = fmea.get("high_rpn_items", [])
            if high_rpn:
                lines.extend([
                    "#### FMEA Analysis (High Risk Items)",
                    "",
                    "| Failure Mode | S | O | D | RPN |",
                    "|--------------|---|---|---|-----|",
                ])
                for item in high_rpn[:10]:
                    fm = _e(item.get("failure_mode", "—"))
                    s = item.get("severity", "—")
                    o = item.get("occurrence", "—")
                    d = item.get("detection", "—")
                    rpn = item.get("rpn", "—")
                    lines.append(f"| {fm} | {s} | {o} | {d} | {rpn} |")
                lines.append("")

        return "\n".join(lines)

    def _build_control_section(self, r: Dict[str, Any], safe_name: str) -> str:
        """Build the Control phase section."""
        lines = [
            f"### 🎯 Control Phase <a id='{safe_name}-control'></a>",
            "",
        ]

        analysis = r.get("analysis", {})

        # Control limits
        spc = analysis.get("spc", {})
        if spc:
            lines.extend([
                "#### Control Chart Parameters",
                "",
                "| Parameter | Value |",
                "|-----------|-------|",
            ])
            for key, val in spc.items():
                if isinstance(val, (int, float)):
                    lines.append(f"| {_e(key)} | {_fmt(val, 4)} |")
            lines.append("")

        # Control charts
        plots = r.get("plots", [])
        control_plots = [p for p in plots if any(kw in Path(p).name.lower() for kw in
                        ("control", "xmr", "spc", "trend", "cusum", "ewma", "xbar"))]
        if control_plots:
            lines.extend([
                "#### Control Charts",
                "",
            ])
            for p in control_plots[:3]:
                lines.extend(self._figure_block(p))

        # Updated control plan
        updated_limits = analysis.get("updated_control_limits", {})
        if updated_limits:
            lines.extend([
                "#### Updated Control Plan",
                "",
                "| Limit | Value |",
                "|-------|-------|",
                f"| UCL | {_fmt(updated_limits.get('ucl'), 4)} |",
                f"| CL | {_fmt(updated_limits.get('cl'), 4)} |",
                f"| LCL | {_fmt(updated_limits.get('lcl'), 4)} |",
                "",
            ])

        # Errors
        errors = r.get("errors", {})
        if errors:
            lines.extend([
                "#### ⚠️ Processing Warnings",
                "",
            ])
            for k, v in errors.items():
                lines.append(f"- `{_e(k)}`: {_e(v)}")
            lines.append("")

        return "\n".join(lines)

    # ── Helper methods ────────────────────────────────────────────────────────

    def _anomaly_section(self, structured: List[Dict[str, Any]]) -> str:
        critical = [s for s in structured if s.get("severity") == "critical"]
        warnings = [s for s in structured if s.get("severity") == "warning"]
        info = [s for s in structured if s.get("severity") == "info"]

        lines = ["#### Detected Anomalies & Statistical Insights", ""]

        for group, emoji, label in [
            (critical, "🔴", "Critical Findings"),
            (warnings, "🟠", "Warnings"),
            (info, "🟢", "Informational"),
        ]:
            if not group:
                continue
            lines.append(f"##### {emoji} {label}")
            lines.append("")
            for ins in group:
                rule = _e(ins.get("rule", "")).replace("_", " ").title()
                desc = _e(ins.get("description", ""))
                mean = _e(ins.get("meaning", ""))
                rec = _e(ins.get("recommendation", ""))
                lines += [
                    f"**{rule}**",
                    "",
                    f"- **Finding:** {desc}",
                    f"- **Interpretation:** {mean}",
                    f"- **Recommended Investigation:** {rec}",
                    "",
                ]
        return "\n".join(lines)

    def _figure_block(self, p: str) -> List[str]:
        pp = str(p).replace("\\", "/")
        cap = _e(Path(p).stem.replace("_", " ").title())
        return [
            f"**{cap}**",
            "",
            f"![{cap}]({pp})",
            "",
        ]

    # ── Flatten nested dict ───────────────────────────────────────────────────

    @staticmethod
    def _flatten(d: Any, prefix: str = "", sep: str = ".") -> Dict[str, str]:
        items: Dict[str, str] = {}
        if isinstance(d, dict):
            for k, v in d.items():
                new_key = f"{prefix}{sep}{k}" if prefix else str(k)
                if isinstance(v, (dict, list)):
                    items.update(MarkdownReportGenerator._flatten(v, new_key, sep))
                else:
                    items[new_key] = str(round(v, 4) if isinstance(v, float) else v)
        elif isinstance(d, list):
            for i, v in enumerate(d[:6]):
                items.update(MarkdownReportGenerator._flatten(v, f"{prefix}[{i}]", sep))
        return items
