"""Generate a Minitab-style capability sixpack report."""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import statsmodels.api as sm
import statsmodels.formula.api as smf
import urllib3
from scipy import stats as scipy_stats
from statsmodels.stats.diagnostic import normal_ad
from matplotlib import font_manager
from matplotlib.patches import Rectangle


@dataclass(frozen=True)
class CapabilitySpecs:
    lsl: float
    usl: float
    target: Optional[float] = None


@dataclass(frozen=True)
class CapabilityStats:
    mean: float
    within_sigma: float
    overall_sigma: float
    cp: float
    cpk: float
    pp: float
    ppk: float
    cpm: float
    ad_stat: float
    ad_p_value: float

@dataclass(frozen=True)
class CapabilityIndices:
    cpu: float
    cpl: float
    ppu: float
    ppl: float

@dataclass(frozen=True)
class CapabilityPerformance:
    observed: tuple[float, float, float]
    expected_overall: tuple[float, float, float]
    expected_within: tuple[float, float, float]

@dataclass(frozen=True)
class CapabilityAnalysisResult:
    stats: CapabilityStats
    indices: CapabilityIndices
    performance: CapabilityPerformance

@dataclass(frozen=True)
class GageRrRecord:
    part: str
    operator: str
    measurement: float

@dataclass(frozen=True)
class GageRrSpecs:
    tolerance: Optional[float] = None
    alpha: float = 0.05
    study_multiplier: float = 6.0
    gage_name: Optional[str] = None
    date_of_study: Optional[str] = None
    reported_by: Optional[str] = None
    misc: Optional[str] = None

@dataclass(frozen=True)
class GageRrTable:
    title: str
    columns: list[str]
    rows: list[list[str]]

@dataclass(frozen=True)
class GageRrResult:
    anova_with_interaction: GageRrTable
    anova_without_interaction: Optional[GageRrTable]
    variance_components: GageRrTable
    gage_evaluation: GageRrTable
    distinct_categories: int
    interaction_p_value: float

@dataclass(frozen=True)
class GageRrAssistantSummary:
    process_percent: float
    process_assessment: str
    process_status: str
    tolerance_percent: Optional[float]
    tolerance_assessment: Optional[str]
    tolerance_status: Optional[str]
    comments: list[str]


FONT_FAMILY = "Plus Jakarta Sans"
FONT_URLS = (
    "https://raw.githubusercontent.com/tokotype/PlusJakartaSans/master/fonts/ttf/PlusJakartaSans-Regular.ttf",
    "https://raw.githubusercontent.com/tokotype/PlusJakartaSans/master/fonts/ttf/PlusJakartaSans-Bold.ttf",
)
DEFAULT_FONT_DIR = Path(__file__).resolve().parent / "assets" / "fonts" / "plus_jakarta_sans"
_FONT_PROP: Optional[font_manager.FontProperties] = None
_FONT_BOLD_PROP: Optional[font_manager.FontProperties] = None


def _download_font_file(font_url: str, destination: Path) -> bool:
    try:
        response = requests.get(font_url, timeout=20, verify=False)
        response.raise_for_status()
    except requests.RequestException:
        return False

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(response.content)
    return True

def download_fonts(font_dir: Path = DEFAULT_FONT_DIR) -> bool:
    """Download Plus Jakarta Sans fonts into the provided directory."""
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    regular_path = font_dir / "PlusJakartaSans-Regular.ttf"
    bold_path = font_dir / "PlusJakartaSans-Bold.ttf"

    regular_ok = _download_font_file(FONT_URLS[0], regular_path)
    bold_ok = _download_font_file(FONT_URLS[1], bold_path)
    return regular_ok and bold_ok

def _configure_fonts(font_dir: Path = DEFAULT_FONT_DIR) -> Optional[font_manager.FontProperties]:
    global _FONT_PROP, _FONT_BOLD_PROP
    if _FONT_PROP is not None:
        return _FONT_PROP

    regular_path = font_dir / "PlusJakartaSans-Regular.ttf"
    bold_path = font_dir / "PlusJakartaSans-Bold.ttf"

    if not regular_path.exists():
        return None

    font_manager.fontManager.addfont(str(regular_path))
    if bold_path.exists():
        font_manager.fontManager.addfont(str(bold_path))

    _FONT_PROP = font_manager.FontProperties(fname=str(regular_path))
    bold_source = bold_path if bold_path.exists() else regular_path
    _FONT_BOLD_PROP = font_manager.FontProperties(fname=str(bold_source), weight="bold")

    plt.rcParams["font.family"] = _FONT_PROP.get_name()
    plt.rcParams["font.sans-serif"] = [_FONT_PROP.get_name()]
    plt.rcParams["font.weight"] = "regular"
    plt.rcParams["axes.titleweight"] = "bold"
    return _FONT_PROP

def _ensure_fonts() -> None:
    _configure_fonts()


def _title(ax: plt.Axes, text: str, pad: float) -> None:
    if _FONT_BOLD_PROP is not None:
        title = ax.set_title(text, fontsize=10, pad=pad, fontproperties=_FONT_BOLD_PROP)
        title.set_fontweight("bold")
    elif _FONT_PROP is not None:
        title = ax.set_title(text, fontsize=10, pad=pad, fontproperties=_FONT_PROP)
        title.set_fontweight("bold")
    else:
        ax.set_title(text, fontsize=10, pad=pad, fontweight="bold")

def _set_y_limits(ax: plt.Axes, values: Iterable[float], pad: float = 0.12) -> None:
    data = np.asarray(list(values), dtype=float)
    if data.size == 0:
        return
    min_value = float(np.min(data))
    max_value = float(np.max(data))
    if math.isclose(min_value, max_value):
        delta = max(0.01, abs(min_value) * pad)
    else:
        delta = (max_value - min_value) * pad
    ax.set_ylim(min_value - delta, max_value + delta)

def _shrink_y_axis(ax: plt.Axes, shrink: float = 0.88) -> None:
    if shrink <= 0 or shrink >= 1:
        return
    position = ax.get_position()
    new_height = position.height * shrink
    offset = (position.height - new_height) / 2
    ax.set_position([position.x0, position.y0 + offset, position.width, new_height])

def _shrink_x_axis(ax: plt.Axes, shrink: float = 0.92) -> None:
    if shrink <= 0 or shrink >= 1:
        return
    position = ax.get_position()
    new_width = position.width * shrink
    offset = (position.width - new_width) / 2
    ax.set_position([position.x0 + offset, position.y0, new_width, position.height])

def _operator_colors(count: int) -> list[tuple[float, float, float, float]]:
    if count <= 10:
        cmap = plt.get_cmap("tab10")
    else:
        cmap = plt.get_cmap("tab20")
    return [cmap(idx % cmap.N) for idx in range(count)]


def _moving_ranges(values: np.ndarray) -> np.ndarray:
    return np.abs(np.diff(values))


def _within_sigma(moving_ranges: np.ndarray) -> float:
    # Moving range of 2 uses d2 = 1.128 for the unbiasing constant.
    d2 = 1.128
    mr_bar = np.mean(moving_ranges)
    return mr_bar / d2


def _capability_stats(values: np.ndarray, specs: CapabilitySpecs) -> CapabilityStats:
    mean = float(np.mean(values))
    overall_sigma = float(np.std(values, ddof=1))
    mr = _moving_ranges(values)
    within_sigma = float(_within_sigma(mr))

    if overall_sigma <= 0 or within_sigma <= 0:
        raise ValueError("Data must include variation to compute capability statistics.")

    lsl = specs.lsl
    usl = specs.usl
    target = specs.target if specs.target is not None else (lsl + usl) / 2

    cp = (usl - lsl) / (6 * within_sigma)
    cpk = min((usl - mean) / (3 * within_sigma), (mean - lsl) / (3 * within_sigma))
    pp = (usl - lsl) / (6 * overall_sigma)
    ppk = min((usl - mean) / (3 * overall_sigma), (mean - lsl) / (3 * overall_sigma))
    cpm = (usl - lsl) / (6 * math.sqrt(overall_sigma**2 + (mean - target) ** 2))

    ad_stat, ad_p_value = normal_ad(values)

    return CapabilityStats(
        mean=mean,
        within_sigma=within_sigma,
        overall_sigma=overall_sigma,
        cp=cp,
        cpk=cpk,
        pp=pp,
        ppk=ppk,
        cpm=cpm,
        ad_stat=float(ad_stat),
        ad_p_value=float(ad_p_value),
    )


def _format_sigma(value: float) -> str:
    return f"{value:.3f}"


def _format_capability(value: float) -> str:
    return f"{value:.2f}"

def _format_ppm(value: float) -> str:
    return f"{value:.2f}"

def _validate_capability_inputs(
    values: np.ndarray,
    specs: CapabilitySpecs,
    *,
    min_count: int,
    context: str,
) -> None:
    if values.size < min_count:
        raise ValueError(f"Need at least {min_count} observations for {context}.")
    if specs.usl <= specs.lsl:
        raise ValueError("USL must be greater than LSL.")
    if np.isclose(np.std(values, ddof=1), 0.0):
        raise ValueError("Data must include variation to compute capability statistics.")

def _capability_indices(
    cap_stats: CapabilityStats,
    specs: CapabilitySpecs,
) -> CapabilityIndices:
    mean = cap_stats.mean
    within = cap_stats.within_sigma
    overall = cap_stats.overall_sigma

    cpu = (specs.usl - mean) / (3 * within)
    cpl = (mean - specs.lsl) / (3 * within)
    ppu = (specs.usl - mean) / (3 * overall)
    ppl = (mean - specs.lsl) / (3 * overall)

    return CapabilityIndices(cpu=cpu, cpl=cpl, ppu=ppu, ppl=ppl)

def _performance_ppm(values: np.ndarray, cap_stats: CapabilityStats, specs: CapabilitySpecs) -> CapabilityPerformance:
    total = float(values.size)
    observed_low = float(np.sum(values < specs.lsl)) / total * 1_000_000
    observed_high = float(np.sum(values > specs.usl)) / total * 1_000_000

    within_dist = scipy_stats.norm(loc=cap_stats.mean, scale=cap_stats.within_sigma)
    overall_dist = scipy_stats.norm(loc=cap_stats.mean, scale=cap_stats.overall_sigma)

    expected_within_low = within_dist.cdf(specs.lsl) * 1_000_000
    expected_within_high = (1 - within_dist.cdf(specs.usl)) * 1_000_000
    expected_overall_low = overall_dist.cdf(specs.lsl) * 1_000_000
    expected_overall_high = (1 - overall_dist.cdf(specs.usl)) * 1_000_000

    return CapabilityPerformance(
        observed=(observed_low, observed_high, observed_low + observed_high),
        expected_overall=(
            expected_overall_low,
            expected_overall_high,
            expected_overall_low + expected_overall_high,
        ),
        expected_within=(
            expected_within_low,
            expected_within_high,
            expected_within_low + expected_within_high,
        ),
    )


def _plot_i_chart(ax: plt.Axes, values: np.ndarray, cap_stats: CapabilityStats) -> None:
    x = np.arange(1, len(values) + 1)
    ucl = cap_stats.mean + 3 * cap_stats.within_sigma
    lcl = cap_stats.mean - 3 * cap_stats.within_sigma

    ax.plot(x, values, color="#1f77b4", marker="o", markersize=3, linewidth=0.8)
    ax.axhline(cap_stats.mean, color="#2ca02c", linewidth=1)
    ax.axhline(ucl, color="#d62728", linewidth=1)
    ax.axhline(lcl, color="#d62728", linewidth=1)

    _title(ax, "I Chart", pad=10)
    ax.set_ylabel("Individual Value", fontsize=9)
    ax.set_xlim(1, len(values))
    ax.grid(True, axis="y", linestyle=":", alpha=0.6)
    ax.set_facecolor("white")

    x_min, x_max = ax.get_xlim()
    label_x = x_max + (x_max - x_min) * 0.03

    ax.text(
        label_x,
        ucl,
        f"UCL={ucl:.3f}",
        fontsize=8,
        va="center",
        ha="left",
        clip_on=False,
    )
    ax.text(
        label_x,
        cap_stats.mean,
        f"$\\bar{{X}}$={cap_stats.mean:.3f}",
        fontsize=8,
        va="center",
        ha="left",
        clip_on=False,
    )
    ax.text(
        label_x,
        lcl,
        f"LCL={lcl:.3f}",
        fontsize=8,
        va="center",
        ha="left",
        clip_on=False,
    )


def _plot_mr_chart(ax: plt.Axes, values: np.ndarray) -> None:
    mr = _moving_ranges(values)
    mr_bar = np.mean(mr)
    d3, d4 = 0.0, 3.267
    ucl = d4 * mr_bar
    lcl = d3 * mr_bar

    x = np.arange(2, len(values) + 1)
    ax.plot(x, mr, color="#1f77b4", marker="o", markersize=3, linewidth=0.8)
    ax.axhline(mr_bar, color="#2ca02c", linewidth=1)
    ax.axhline(ucl, color="#d62728", linewidth=1)
    ax.axhline(lcl, color="#d62728", linewidth=1)

    _title(ax, "Moving Range Chart", pad=10)
    ax.set_ylabel("Moving Range", fontsize=9)
    ax.set_xlim(1, len(values))
    ax.grid(True, axis="y", linestyle=":", alpha=0.6)
    ax.set_facecolor("white")

    x_min, x_max = ax.get_xlim()
    label_x = x_max + (x_max - x_min) * 0.03

    ax.text(
        label_x,
        ucl,
        f"UCL={ucl:.3f}",
        fontsize=8,
        va="center",
        ha="left",
        clip_on=False,
    )
    ax.text(
        label_x,
        mr_bar,
        f"$\\bar{{M}}$R={mr_bar:.3f}",
        fontsize=8,
        va="center",
        ha="left",
        clip_on=False,
    )
    ax.text(
        label_x,
        lcl,
        "LCL=0",
        fontsize=8,
        va="center",
        ha="left",
        clip_on=False,
    )


def _plot_last_observations(ax: plt.Axes, values: np.ndarray, cap_stats: CapabilityStats) -> None:
    last_values = values[-25:]
    x = np.arange(len(values) - len(last_values) + 1, len(values) + 1)
    ax.scatter(x, last_values, color="#1f77b4", s=16)
    ax.axhline(cap_stats.mean, color="#2ca02c", linewidth=1, linestyle="--")
    _title(ax, "Last 25 Observations", pad=10)
    ax.set_xlabel("Observation", fontsize=9)
    ax.set_ylabel("Values", fontsize=9)
    ax.grid(True, axis="y", linestyle=":", alpha=0.6)
    ax.set_facecolor("white")


def _plot_capability_histogram(
    ax: plt.Axes,
    values: np.ndarray,
    cap_stats: CapabilityStats,
    specs: CapabilitySpecs,
    *,
    title: Optional[str],
    show_legend: bool,
    show_spec_box: bool,
    legend_loc: str = "upper left",
    legend_bbox: Optional[tuple[float, float]] = None,
) -> None:
    _counts, _bins, _ = ax.hist(
        values,
        bins=12,
        color="#8cb4e2",
        edgecolor="#4c72b0",
        alpha=0.7,
        density=True,
    )

    x = np.linspace(min(values) - 1, max(values) + 1, 200)
    ax.plot(
        x,
        scipy_stats.norm.pdf(x, cap_stats.mean, cap_stats.overall_sigma),
        color="#d62728",
        linewidth=1.2,
        label="Overall",
    )

    ax.plot(
        x,
        scipy_stats.norm.pdf(x, cap_stats.mean, cap_stats.within_sigma),
        color="#1f77b4",
        linewidth=1.2,
        label="Within",
        linestyle="--"
    )

    ax.axvline(specs.lsl, color="#d62728", linestyle="--", linewidth=1)
    ax.axvline(specs.usl, color="#d62728", linestyle="--", linewidth=1)
    if specs.target is not None:
        ax.axvline(specs.target, color="#2ca02c", linestyle=":", linewidth=1)

    if title:
        _title(ax, title, pad=12)
    ax.set_ylabel("")
    ax.set_yticks([])
    ax.grid(True, axis="y", linestyle=":", alpha=0.6)
    ax.set_facecolor("white")

    y_min, y_max = ax.get_ylim()
    label_y = y_max * 1.02
    ax.text(
        specs.lsl,
        label_y,
        "LSL",
        color="#d62728",
        fontsize=8,
        ha="center",
        va="bottom",
        clip_on=False,
    )
    if specs.target is not None:
        ax.text(
            specs.target,
            label_y,
            "Target",
            color="#2ca02c",
            fontsize=8,
            ha="center",
            va="bottom",
            clip_on=False,
        )
    ax.text(
        specs.usl,
        label_y,
        "USL",
        color="#d62728",
        fontsize=8,
        ha="center",
        va="bottom",
        clip_on=False,
    )

    if show_legend:
        if legend_bbox is None:
            legend_bbox = (1.05, 1.08)
        legend = ax.legend(
            fontsize=8,
            loc=legend_loc,
            bbox_to_anchor=legend_bbox,
            borderaxespad=0.0,
            frameon=True,
        )
        legend.get_frame().set_facecolor("white")
        legend.get_frame().set_edgecolor("#cccccc")
        legend.get_frame().set_linewidth(1)

    if show_spec_box:
        spec_text = "\n".join(
            [
                "Specifications",
                f"LSL  {specs.lsl:.0f}",
                f"Target  {specs.target:.0f}" if specs.target is not None else "",
                f"USL  {specs.usl:.0f}",
            ]
        ).strip()
        info_x = 1.05
        ax.text(
            info_x,
            0.7,
            spec_text,
            transform=ax.transAxes,
            fontsize=8,
            va="top",
            ha="left",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#cccccc"),
            clip_on=False,
        )

def _plot_histogram(
    ax: plt.Axes,
    values: np.ndarray,
    cap_stats: CapabilityStats,
    specs: CapabilitySpecs,
) -> None:
    _plot_capability_histogram(
        ax,
        values,
        cap_stats,
        specs,
        title="Capability Histogram",
        show_legend=True,
        show_spec_box=True,
    )


def _plot_probability(ax: plt.Axes, values: np.ndarray, cap_stats: CapabilityStats) -> None:
    (osm, osr), (slope, intercept, _r) = scipy_stats.probplot(values, dist="norm")
    ax.scatter(osr, osm, color="#1f77b4", s=12)
    fit = slope * np.array(osm) + intercept
    ax.plot(fit, osm, color="#d62728", linewidth=1)

    # 95% confidence interval for the fitted line
    n = len(values)
    sorted_vals = np.sort(values)
    # Plotting positions (median rank approximation)
    p = (np.arange(1, n + 1) - 0.5) / n
    # Z-scores for the plotting positions
    z = scipy_stats.norm.ppf(p)
    # Standard normal PDF at z
    phi_z = scipy_stats.norm.pdf(z)
    # Standard error for order statistics
    se = cap_stats.overall_sigma * np.sqrt(p * (1 - p) / n) / phi_z
    # 95% CI using z=1.96
    z_alpha = 1.96
    ci_lower = slope * osm + intercept - z_alpha * se
    ci_upper = slope * osm + intercept + z_alpha * se
    ax.plot(ci_lower, osm, color="#d62728", linewidth=0.8, linestyle="--", alpha=0.7)
    ax.plot(ci_upper, osm, color="#d62728", linewidth=0.8, linestyle="--", alpha=0.7)

    _title(ax, "Normal Prob Plot", pad=10)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_yticks([])
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.set_facecolor("white")

    ax.text(
        0.98,
        0.1,
        f"AD: {cap_stats.ad_stat:.3f}, P: {cap_stats.ad_p_value:.3f}",
        transform=ax.transAxes,
        fontsize=8,
        ha="right",
    )


def _plot_capability(ax: plt.Axes, cap_stats: CapabilityStats, specs: CapabilitySpecs) -> None:
    _title(ax, "Capability Plot", pad=10)
    ax.set_xlim(specs.lsl - 1, specs.usl + 1)
    ax.set_ylim(0, 3)
    _shrink_x_axis(ax, shrink=0.5)
    ax.set_yticks([0.5, 1.5, 2.5])
    ax.set_yticklabels(["Specs", "Within", "Overall"], fontsize=8)
    ax.grid(True, axis="x", linestyle=":", alpha=0.6)
    ax.set_facecolor("white")

    def _interval(y: float, center: float, sigma: float, color: str) -> None:
        width = 3 * sigma
        start = center - width
        end = center + width
        ax.hlines(y, start, end, color=color, linewidth=2)
        ax.plot(
            [start, center, end],
            [y, y, y],
            linestyle="None",
            marker="+",
            color=color,
            markersize=9,
            markeredgewidth=1.6,
        )

    _interval(2.5, cap_stats.mean, cap_stats.overall_sigma, "#1f77b4")
    _interval(1.5, cap_stats.mean, cap_stats.within_sigma, "#d62728")

    ax.hlines(0.5, specs.lsl, specs.usl, color="#2ca02c", linewidth=2)
    ax.plot(
        [specs.lsl, (specs.lsl + specs.usl) / 2, specs.usl],
        [0.5, 0.5, 0.5],
        linestyle="None",
        marker="+",
        color="#2ca02c",
        markersize=9,
        markeredgewidth=1.6,
    )

    ax.set_xlabel("Values", fontsize=9)

    # Left table: Within stats
    within_stats = [
        ["StDev", _format_sigma(cap_stats.within_sigma)],
        ["Cp", _format_capability(cap_stats.cp)],
        ["Cpk", _format_capability(cap_stats.cpk)],
    ]
    left_table = ax.table(
        cellText=within_stats,
        colLabels=["Within", ""],
        loc="center left",
        cellLoc="center",
        colLoc="center",
        bbox=[-0.75, 0.25, 0.4, 0.55],
    )
    left_table.auto_set_font_size(False)
    left_table.set_fontsize(7)
    left_table.scale(1, 1.3)
    for (row, col), cell in left_table.get_celld().items():
        cell.set_facecolor("white")
        cell.set_edgecolor("white")
        cell.set_linewidth(0)
        if row == 0:
            cell.set_text_props(weight="bold", fontsize=7)

    # Right table: Overall stats
    overall_stats = [
        ["StDev", _format_sigma(cap_stats.overall_sigma)],
        ["Pp", _format_capability(cap_stats.pp)],
        ["Ppk", _format_capability(cap_stats.ppk)],
        ["Cpm", _format_capability(cap_stats.cpm)],
    ]
    right_table = ax.table(
        cellText=overall_stats,
        colLabels=["Overall", ""],
        loc="center right",
        cellLoc="center",
        colLoc="center",
        bbox=[1.10, 0.15, 0.4, 0.65],
    )
    right_table.auto_set_font_size(False)
    right_table.set_fontsize(7)
    right_table.scale(1, 1.3)
    for (row, col), cell in right_table.get_celld().items():
        cell.set_facecolor("white")
        cell.set_edgecolor("white")
        cell.set_linewidth(0)
        if row == 0:
            cell.set_text_props(weight="bold", fontsize=7)

def _prepare_box(ax: plt.Axes) -> None:
    ax.set_facecolor("none")
    ax.axis("off")

def _draw_box(
    ax: plt.Axes,
    *,
    left: float,
    bottom: float,
    width: float,
    height: float,
) -> None:
    ax.add_patch(
        Rectangle(
            (left, bottom),
            width,
            height,
            transform=ax.transAxes,
            fill=True,
            facecolor="white",
            edgecolor="#666666",
            linewidth=1,
        )
    )

def _draw_two_column_rows(
    ax: plt.Axes,
    rows: list[tuple[str, str]],
    *,
    start_y: float,
    line_height: float,
    label_x: float = 0.06,
    value_x: float = 0.58,
    fontsize: float = 8,
) -> float:
    y = start_y
    for label, value in rows:
        ax.text(label_x, y, label, fontsize=fontsize, ha="left", va="top", transform=ax.transAxes)
        ax.text(value_x, y, value, fontsize=fontsize, ha="left", va="top", transform=ax.transAxes)
        y -= line_height
    return y

def _draw_section_title(
    ax: plt.Axes,
    title: str,
    *,
    y: float,
    fontsize: float = 8.5,
    label_x: float = 0.06,
) -> float:
    ax.text(label_x, y, title, fontsize=fontsize, fontweight="bold", ha="left", va="top", transform=ax.transAxes)
    return y

def _draw_boxed_section(
    ax: plt.Axes,
    title: str,
    rows: list[tuple[str, str]],
    *,
    top_y: float,
    line_height: float,
    left: float = 0.05,
    right: float = 0.95,
    padding: float = 0.03,
    label_x: float = 0.08,
    value_x: float = 0.6,
) -> float:
    lines_count = 1 + len(rows)
    height = lines_count * line_height + padding * 2
    bottom = top_y - height
    _draw_box(ax, left=left, bottom=bottom, width=right - left, height=height)
    title_y = top_y - padding
    _draw_section_title(ax, title, y=title_y, label_x=label_x)
    _draw_two_column_rows(
        ax,
        rows,
        start_y=title_y - line_height,
        line_height=line_height,
        label_x=label_x,
        value_x=value_x,
    )
    return bottom

def _draw_stacked_sections(
    ax: plt.Axes,
    sections: list[tuple[str, list[tuple[str, str]]]],
    *,
    top_y: float,
    line_height: float,
    left: float = 0.05,
    right: float = 0.95,
    padding: float = 0.025,
    label_x: float = 0.08,
    value_x: float = 0.58,
    divider_gap: float = 0.03,
) -> None:
    heights = [((1 + len(rows)) * line_height + padding * 2) for _title, rows in sections]
    total_height = sum(heights) + divider_gap * (len(sections) - 1)
    bottom = top_y - total_height
    _draw_box(ax, left=left, bottom=bottom, width=right - left, height=total_height)

    current_top = top_y
    for idx, (title, rows) in enumerate(sections):
        section_height = heights[idx]
        title_y = current_top - (padding if idx == 0 else 0)
        _draw_section_title(ax, title, y=title_y, label_x=label_x)
        _draw_two_column_rows(
            ax,
            rows,
            start_y=title_y - 1.5*line_height,
            line_height=line_height,
            label_x=label_x,
            value_x=value_x,
        )
        current_top -= section_height
        if idx < len(sections) - 1:
            divider_y = current_top - divider_gap / 2
            ax.plot(
                [left, right],
                [divider_y, divider_y],
                transform=ax.transAxes,
                color="#666666",
                linewidth=1,
            )
            current_top -= divider_gap

def _process_data_rows(values: np.ndarray, cap_stats: CapabilityStats, specs: CapabilitySpecs) -> list[tuple[str, str]]:
    target = specs.target if specs.target is not None else (specs.lsl + specs.usl) / 2
    return [
        ("LSL", f"{specs.lsl:.3f}"),
        ("Target", f"{target:.3f}"),
        ("USL", f"{specs.usl:.3f}"),
        ("Sample N", f"{values.size:d}"),
        ("Mean", f"{cap_stats.mean:.4f}"),
        ("StDev(Within)", f"{cap_stats.within_sigma:.6f}"),
        ("StDev(Overall)", f"{cap_stats.overall_sigma:.6f}"),
    ]

def _overall_capability_rows(
    cap_stats: CapabilityStats,
    indices: CapabilityIndices,
    *,
    include_cpm: bool,
) -> list[tuple[str, str]]:
    rows = [
        ("Pp", _format_capability(cap_stats.pp)),
        ("PPL", _format_capability(indices.ppl)),
        ("PPU", _format_capability(indices.ppu)),
        ("Ppk", _format_capability(cap_stats.ppk)),
    ]
    if include_cpm:
        rows.append(("Cpm", _format_capability(cap_stats.cpm)))
    return rows

def _within_capability_rows(cap_stats: CapabilityStats, indices: CapabilityIndices) -> list[tuple[str, str]]:
    return [
        ("Cp", _format_capability(cap_stats.cp)),
        ("CPL", _format_capability(indices.cpl)),
        ("CPU", _format_capability(indices.cpu)),
        ("Cpk", _format_capability(cap_stats.cpk)),
    ]

def _draw_performance_table(ax: plt.Axes, performance: CapabilityPerformance) -> None:
    labels = ["PPM < LSL", "PPM > USL", "PPM Total"]
    columns = [
        ("Observed", performance.observed),
        ("Expected Overall", performance.expected_overall),
        ("Expected Within", performance.expected_within),
    ]
    left = 0.15
    right = 0.85
    label_x = 0.17
    column_x = [0.35, 0.52, 0.69]
    line_height = 0.145
    padding = 0.025
    lines_count = 1 + len(labels)
    top_y = 0.9
    height = lines_count * line_height + padding * 4
    bottom = top_y - height
    _draw_box(ax, left=left, bottom=bottom, width=right - left, height=height)

    header_y = top_y - padding
    ax.text(label_x, header_y, "Performance", fontsize=8.5, fontweight="bold", ha="left", va="top", transform=ax.transAxes)
    for idx, (header, _values) in enumerate(columns):
        ax.text(column_x[idx], header_y, header, fontsize=8, ha="left", va="top", transform=ax.transAxes)

    y = header_y - 1.5*line_height
    for row_idx, label in enumerate(labels):
        ax.text(label_x, y, label, fontsize=8, ha="left", va="top", transform=ax.transAxes)
        for col_idx, (_header, values) in enumerate(columns):
            ax.text(column_x[col_idx], y, _format_ppm(values[row_idx]), fontsize=8, ha="left", va="top", transform=ax.transAxes)
        y -= line_height

def _plot_capability_analysis_report(
    values: np.ndarray,
    cap_stats: CapabilityStats,
    indices: CapabilityIndices,
    performance: CapabilityPerformance,
    specs: CapabilitySpecs,
    title: str,
    output_path: Path,
) -> None:
    fig = plt.figure(figsize=(7, 3.8), dpi=150)
    fig.patch.set_facecolor("#e0e0e0")
    if _FONT_BOLD_PROP is not None:
        fig_title = fig.suptitle(title, fontsize=12, y=0.98, fontproperties=_FONT_BOLD_PROP)
        fig_title.set_fontweight("bold")
    elif _FONT_PROP is not None:
        fig_title = fig.suptitle(title, fontsize=12, y=0.98, fontproperties=_FONT_PROP)
        fig_title.set_fontweight("bold")
    else:
        fig.suptitle(title, fontsize=12, y=0.98, fontweight="bold")

    grid = fig.add_gridspec(
        3,
        3,
        width_ratios=[1.3, 2.0, 1.3],
        height_ratios=[2.2, 0.01, 0.8],
        hspace=0.1,
        wspace=0.08,
    )

    hist_ax = fig.add_subplot(grid[0, 1])
    _plot_capability_histogram(
        hist_ax,
        values,
        cap_stats,
        specs,
        title=None,
        show_legend=True,
        show_spec_box=False,
        legend_loc="upper left",
        legend_bbox=(1.06, 1.0),
    )
    hist_ax.set_ylabel("")

    left_ax = fig.add_subplot(grid[0, 0])
    _prepare_box(left_ax)
    _draw_boxed_section(
        left_ax,
        "Process Data",
        _process_data_rows(values, cap_stats, specs),
        top_y=0.93,
        line_height=0.075,
        label_x=0.08,
        value_x=0.56,
    )

    right_ax = fig.add_subplot(grid[0, 2])
    _prepare_box(right_ax)
    _draw_stacked_sections(
        right_ax,
        [
            (
                "Overall Capability",
                _overall_capability_rows(cap_stats, indices, include_cpm=specs.target is not None),
            ),
            ("Potential (Within) Capability", _within_capability_rows(cap_stats, indices)),
        ],
        top_y=0.80,
        line_height=0.053,
        left=0.01,
        right=0.99,
        padding=0.04,
        label_x=0.03,
        value_x=0.50,
        divider_gap=0.04,
    )

    performance_ax = fig.add_subplot(grid[2, :])
    _prepare_box(performance_ax)
    _draw_performance_table(performance_ax, performance)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.subplots_adjust(top=0.9, bottom=0.08, left=0.05, right=0.97, hspace=0.1, wspace=0.05)
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)

def _format_anova_table(table: pd.DataFrame, total_ss: float, total_df: int) -> GageRrTable:
    rows: list[list[str]] = []
    for source, data in table.iterrows():
        df = int(data["df"])
        ss = float(data["sum_sq"])
        ms = ss / df if df > 0 else 0.0
        f_value = data.get("F", np.nan)
        p_value = data.get("PR(>F)", np.nan)

        def _fmt(value: float) -> str:
            if np.isnan(value):
                return ""
            return f"{value:.3f}"

        rows.append(
            [
                source,
                f"{df:d}",
                f"{ss:.5f}",
                f"{ms:.5f}",
                _fmt(float(f_value)),
                _fmt(float(p_value)),
            ]
        )

    rows.append(["Total", f"{total_df:d}", f"{total_ss:.5f}", "", "", ""])
    return GageRrTable(
        title="Two-Way ANOVA",
        columns=["Source", "DF", "SS", "MS", "F", "P"],
        rows=rows,
    )

def _validate_gage_rr_data(df: pd.DataFrame) -> tuple[int, int, int]:
    if df.empty:
        raise ValueError("Gage R&R data cannot be empty.")
    if df["part"].nunique() < 2:
        raise ValueError("Gage R&R requires at least two parts.")
    if df["operator"].nunique() < 2:
        raise ValueError("Gage R&R requires at least two operators.")

    counts = df.groupby(["part", "operator"]).size()
    if counts.nunique() != 1:
        raise ValueError("Gage R&R requires a balanced design for all part/operator combinations.")
    replicates = int(counts.iloc[0])
    if replicates < 2:
        raise ValueError("Gage R&R requires at least two trials per part/operator combination.")

    parts = df["part"].nunique()
    operators = df["operator"].nunique()
    return parts, operators, replicates

def _anova_tables(df: pd.DataFrame, specs: GageRrSpecs) -> tuple[GageRrTable, Optional[GageRrTable], bool, float]:
    total_ss = float(((df["measurement"] - df["measurement"].mean()) ** 2).sum())
    total_df = df.shape[0] - 1

    full_model = smf.ols("measurement ~ C(part) * C(operator)", data=df).fit()
    full_anova = sm.stats.anova_lm(full_model, typ=2)
    full_anova = full_anova.rename(
        index={
            "C(part)": "Part",
            "C(operator)": "Operator",
            "C(part):C(operator)": "Part * Operator",
            "Residual": "Repeatability",
        }
    )
    interaction_p = float(full_anova.loc["Part * Operator", "PR(>F)"])
    full_table = _format_anova_table(full_anova, total_ss, total_df)

    if interaction_p < specs.alpha:
        return full_table, None, True, interaction_p

    reduced_model = smf.ols("measurement ~ C(part) + C(operator)", data=df).fit()
    reduced_anova = sm.stats.anova_lm(reduced_model, typ=2)
    reduced_anova = reduced_anova.rename(
        index={
            "C(part)": "Part",
            "C(operator)": "Operator",
            "Residual": "Repeatability",
        }
    )
    reduced_table = _format_anova_table(reduced_anova, total_ss, total_df)
    return full_table, reduced_table, False, interaction_p

def _variance_components(
    anova: GageRrTable,
    parts: int,
    operators: int,
    replicates: int,
    include_interaction: bool,
) -> tuple[list[tuple[str, float]], float]:
    ms_lookup = {row[0]: float(row[3]) for row in anova.rows if row[0] != "Total"}
    repeatability = ms_lookup.get("Repeatability", 0.0)
    ms_part = ms_lookup.get("Part", 0.0)
    ms_operator = ms_lookup.get("Operator", 0.0)

    interaction = 0.0
    if include_interaction:
        ms_interaction = ms_lookup.get("Part * Operator", 0.0)
        operator = max((ms_operator - ms_interaction) / (parts * replicates), 0.0)
        part = max((ms_part - ms_interaction) / (operators * replicates), 0.0)
        interaction = max((ms_interaction - repeatability) / replicates, 0.0)
        reproducibility = operator + interaction
    else:
        operator = max((ms_operator - repeatability) / (parts * replicates), 0.0)
        part = max((ms_part - repeatability) / (operators * replicates), 0.0)
        reproducibility = operator

    total_gage = repeatability + reproducibility
    total_variation = total_gage + part

    components: list[tuple[str, float]] = [
        ("Total Gage R&R", total_gage),
        ("Repeatability", repeatability),
        ("Reproducibility", reproducibility),
        ("Operator", operator),
    ]
    if include_interaction:
        components.append(("Operator*Part", interaction))
    components.extend(
        [
            ("Part-To-Part", part),
            ("Total Variation", total_variation),
        ]
    )
    return components, total_variation

def _build_variance_table(components: list[tuple[str, float]], total_variation: float) -> GageRrTable:
    rows: list[list[str]] = []
    for label, value in components:
        contribution = 0.0 if total_variation <= 0 else value / total_variation * 100
        rows.append([label, f"{value:.5f}", f"{contribution:.2f}"])
    return GageRrTable(
        title="Variance Components",
        columns=["Source", "VarComp", "%Contribution"],
        rows=rows,
    )

def _build_gage_eval_table(
    components: list[tuple[str, float]],
    total_variation: float,
    specs: GageRrSpecs,
) -> GageRrTable:
    rows: list[list[str]] = []
    total_stddev = math.sqrt(total_variation) if total_variation > 0 else 0.0
    total_study = specs.study_multiplier * total_stddev

    for label, value in components:
        stddev = math.sqrt(value) if value > 0 else 0.0
        study_var = specs.study_multiplier * stddev
        study_pct = 0.0 if total_study <= 0 else study_var / total_study * 100
        if specs.tolerance is not None:
            tol_pct = 0.0 if specs.tolerance <= 0 else study_var / specs.tolerance * 100
            tol_text = f"{tol_pct:.2f}"
        else:
            tol_text = ""
        rows.append(
            [label, f"{stddev:.5f}", f"{study_var:.5f}", f"{study_pct:.2f}", tol_text]
        )

    return GageRrTable(
        title="Gage Evaluation",
        columns=["Source", "StdDev (SD)", "Study Var (6 x SD)", "%Study Var", "%Tolerance"],
        rows=rows,
    )

def _distinct_categories(part_var: float, grr_var: float) -> int:
    if grr_var <= 0 or part_var <= 0:
        return 1
    ndc = 1.41 * math.sqrt(part_var) / math.sqrt(grr_var)
    # AIAG MSA 4th Edition truncates ndc to an integer (not rounding).
    return max(1, int(ndc))

def _parse_float(value: str, fallback: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback

def _assessment_for_percent(value: float) -> tuple[str, str]:
    if value <= 10:
        return "Yes", "acceptable"
    if value <= 30:
        return "Marginal", "marginal"
    return "No", "unacceptable"

def _assistant_summary(
    variance_table: GageRrTable,
    gage_table: GageRrTable,
    *,
    parts: int,
    operators: int,
    replicates: int,
) -> GageRrAssistantSummary:
    variance_lookup = {row[0]: row for row in variance_table.rows}
    gage_lookup = {row[0]: row for row in gage_table.rows}
    total_gage_study = _parse_float(gage_lookup["Total Gage R&R"][3])
    process_assessment, process_status = _assessment_for_percent(total_gage_study)

    tolerance_percent = None
    tolerance_assessment = None
    tolerance_status = None
    if gage_lookup["Total Gage R&R"][4]:
        tolerance_percent = _parse_float(gage_lookup["Total Gage R&R"][4])
        tolerance_assessment, tolerance_status = _assessment_for_percent(tolerance_percent)

    total_contrib = _parse_float(variance_lookup["Total Gage R&R"][2])
    repeat_contrib = _parse_float(variance_lookup["Repeatability"][2])
    repro_contrib = _parse_float(variance_lookup["Reproducibility"][2])
    part_contrib = _parse_float(variance_lookup["Part-To-Part"][2])

    comments = [
        "General rule: <10% acceptable, 10-30% marginal, >30% unacceptable.",
        f"Total gage variation is {total_gage_study:.1f}% of process variation.",
        f"Total Gage R&R contributes {total_contrib:.1f}% of total variation.",
        f"Repeatability contributes {repeat_contrib:.1f}% of total variation.",
        f"Reproducibility contributes {repro_contrib:.1f}% of total variation.",
        f"Part-to-part contributes {part_contrib:.1f}% of total variation.",
    ]

    if parts < 10 or operators < 3:
        comments.append(
            "Measurement variation estimates may be imprecise with fewer than 10 parts or 3 operators."
        )
    elif parts < 35:
        comments.append("More than 10 parts improves the precision of process variation estimates.")

    if replicates < 2:
        comments.append("At least 2 replicates are recommended to estimate repeatability.")

    return GageRrAssistantSummary(
        process_percent=total_gage_study,
        process_assessment=process_assessment,
        process_status=process_status,
        tolerance_percent=tolerance_percent,
        tolerance_assessment=tolerance_assessment,
        tolerance_status=tolerance_status,
        comments=comments,
    )

def _format_table(table: GageRrTable) -> str:
    widths = [len(col) for col in table.columns]
    for row in table.rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(cell))

    def _format_row(row: list[str]) -> str:
        return "  ".join(cell.ljust(widths[idx]) for idx, cell in enumerate(row))

    lines = [table.title, _format_row(table.columns)]
    lines.append("  ".join("-" * width for width in widths))
    lines.extend(_format_row(row) for row in table.rows)
    return "\n".join(lines)

def _sort_labels(labels: Iterable[str]) -> list[str]:
    def _key(label: str) -> tuple[int, str]:
        return (0, f"{int(label):09d}") if str(label).isdigit() else (1, str(label))

    return sorted([str(label) for label in labels], key=_key)

def _spc_constants(subgroup_size: int) -> tuple[float, float, float]:
    constants = {
        2: (1.88, 0.0, 3.267),
        3: (1.023, 0.0, 2.574),
        4: (0.729, 0.0, 2.282),
        5: (0.577, 0.0, 2.114),
        6: (0.483, 0.0, 2.004),
        7: (0.419, 0.076, 1.924),
        8: (0.373, 0.136, 1.864),
        9: (0.337, 0.184, 1.816),
        10: (0.308, 0.223, 1.777),
    }
    if subgroup_size not in constants:
        raise ValueError("Unsupported subgroup size for control chart constants.")
    return constants[subgroup_size]

def _plot_components_of_variation(
    ax: plt.Axes,
    variance_table: GageRrTable,
    gage_table: GageRrTable,
) -> None:
    lookup = {row[0]: row for row in variance_table.rows}
    study_lookup = {row[0]: row for row in gage_table.rows}
    categories = ["Total Gage R&R", "Repeatability", "Reproducibility", "Part-To-Part"]
    contribution = [float(lookup[label][2]) for label in categories]
    study_var = [float(study_lookup[label][3]) for label in categories]

    tolerance = None
    if study_lookup[categories[0]][4]:
        tolerance = [float(study_lookup[label][4]) for label in categories]

    x = np.arange(len(categories))
    width = 0.25 if tolerance is not None else 0.35
    ax.bar(x - width, contribution, width, color="#1f77b4", label="%Contribution")
    ax.bar(x, study_var, width, color="#d62728", label="%Study Var")
    if tolerance is not None:
        ax.bar(x + width, tolerance, width, color="#ffbf00", label="%Tolerance")

    _title(ax, "Components of Variation", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels([label.replace("Total ", "") for label in categories], fontsize=8)
    ax.set_ylabel("Percent", fontsize=9)
    bar_max = max(contribution + study_var + (tolerance or []))
    ax.set_ylim(0, bar_max * 1.2)
    ax.grid(True, axis="y", linestyle=":", alpha=0.6)
    ax.legend(fontsize=7, frameon=True, loc="upper left", bbox_to_anchor=(1.01, 1.0))
    ax.set_facecolor("white")
    _shrink_y_axis(ax)

def _plot_r_chart_by_operator(ax: plt.Axes, df: pd.DataFrame, subgroup_size: int) -> None:
    ranges = df.groupby(["operator", "part"])["measurement"].agg(lambda values: values.max() - values.min())
    r_bar = ranges.mean()
    _a2, d3, d4 = _spc_constants(subgroup_size)
    ucl = d4 * r_bar
    lcl = d3 * r_bar

    operators = _sort_labels(ranges.index.get_level_values(0).unique())
    parts = _sort_labels(ranges.index.get_level_values(1).unique())
    colors = _operator_colors(len(operators))
    for idx, operator in enumerate(operators):
        series = ranges.loc[operator].reindex(parts)
        x_positions = np.arange(1, len(parts) + 1) + idx * len(parts)
        ax.plot(
            x_positions,
            series.values,
            marker="o",
            markersize=3,
            linewidth=0.8,
            color=colors[idx % len(colors)],
        )
        mid = x_positions[0] + (x_positions[-1] - x_positions[0]) / 2
        ax.text(mid, 1.02, operator, transform=ax.get_xaxis_transform(), ha="center", va="bottom", fontsize=8)
        if idx > 0:
            ax.axvline(x_positions[0] - 0.5, color="#6b6b6b", linestyle="--", linewidth=0.8)

    ax.axhline(r_bar, color="#2ca02c", linewidth=1)
    ax.axhline(ucl, color="#d62728", linewidth=1)
    ax.axhline(lcl, color="#d62728", linewidth=1)
    _title(ax, "R Chart by Operator", pad=10)
    ax.set_ylabel("Range", fontsize=9)
    ax.set_xlim(0.5, len(parts) * len(operators) + 0.5)
    ax.set_xticks([])
    ax.grid(True, axis="y", linestyle=":", alpha=0.6)
    ax.set_facecolor("white")

    _set_y_limits(ax, [*ranges.values, r_bar, ucl, lcl])
    _shrink_y_axis(ax)

    x_min, x_max = ax.get_xlim()
    label_x = x_max + (x_max - x_min) * 0.03
    ax.text(label_x, ucl, f"UCL={ucl:.5f}", fontsize=8, va="center", ha="left", clip_on=False)
    ax.text(label_x, r_bar, f"$\\bar{{R}}$={r_bar:.5f}", fontsize=8, va="center", ha="left", clip_on=False)
    ax.text(label_x, lcl, "LCL=0" if lcl <= 0 else f"LCL={lcl:.5f}", fontsize=8, va="center", ha="left", clip_on=False)

def _plot_xbar_chart_by_operator(ax: plt.Axes, df: pd.DataFrame, subgroup_size: int) -> None:
    means = df.groupby(["operator", "part"])["measurement"].mean()
    ranges = df.groupby(["operator", "part"])["measurement"].agg(lambda values: values.max() - values.min())
    r_bar = ranges.mean()
    a2, _d3, _d4 = _spc_constants(subgroup_size)
    grand_mean = df["measurement"].mean()
    ucl = grand_mean + a2 * r_bar
    lcl = grand_mean - a2 * r_bar

    operators = _sort_labels(means.index.get_level_values(0).unique())
    parts = _sort_labels(means.index.get_level_values(1).unique())
    colors = _operator_colors(len(operators))
    for idx, operator in enumerate(operators):
        series = means.loc[operator].reindex(parts)
        x_positions = np.arange(1, len(parts) + 1) + idx * len(parts)
        ax.plot(
            x_positions,
            series.values,
            marker="o",
            markersize=3,
            linewidth=0.8,
            color=colors[idx % len(colors)],
        )
        mid = x_positions[0] + (x_positions[-1] - x_positions[0]) / 2
        ax.text(mid, 1.02, operator, transform=ax.get_xaxis_transform(), ha="center", va="bottom", fontsize=8)
        if idx > 0:
            ax.axvline(x_positions[0] - 0.5, color="#6b6b6b", linestyle="--", linewidth=0.8)

    ax.axhline(grand_mean, color="#2ca02c", linewidth=1)
    ax.axhline(ucl, color="#d62728", linewidth=1)
    ax.axhline(lcl, color="#d62728", linewidth=1)
    _title(ax, "Xbar Chart by Operator", pad=10)
    ax.set_ylabel("Mean", fontsize=9)
    ax.set_xlim(0.5, len(parts) * len(operators) + 0.5)
    ax.set_xticks([])
    ax.grid(True, axis="y", linestyle=":", alpha=0.6)
    ax.set_facecolor("white")

    _set_y_limits(ax, [*means.values, grand_mean, ucl, lcl])
    _shrink_y_axis(ax)

    x_min, x_max = ax.get_xlim()
    label_x = x_max + (x_max - x_min) * 0.03
    ax.text(label_x, ucl, f"UCL={ucl:.5f}", fontsize=8, va="center", ha="left", clip_on=False)
    ax.text(
        label_x,
        grand_mean,
        f"$\\bar{{X}}$={grand_mean:.5f}",
        fontsize=8,
        va="center",
        ha="left",
        clip_on=False,
    )
    ax.text(label_x, lcl, f"LCL={lcl:.5f}", fontsize=8, va="center", ha="left", clip_on=False)

def _plot_measurements_by_part(ax: plt.Axes, df: pd.DataFrame) -> None:
    parts = _sort_labels(df["part"].unique())
    x_positions = np.arange(1, len(parts) + 1)
    all_measurements = []
    for part, x_pos in zip(parts, x_positions):
        values = df[df["part"] == part]["measurement"].values
        all_measurements.extend(values.tolist())
        ax.scatter(
            np.full_like(values, x_pos, dtype=float),
            values,
            color="#8c8c8c",
            s=12,
            alpha=0.7,
            zorder=2,
        )

    means = df.groupby("part")["measurement"].mean().reindex(parts)
    ax.plot(x_positions, means.values, color="#1f77b4", linewidth=1.2, zorder=3)
    ax.scatter(x_positions, means.values, color="#1f77b4", s=20, zorder=4)
    _title(ax, "Measurement by Part", pad=10)
    ax.set_xlabel("Part", fontsize=9)
    ax.grid(True, axis="y", linestyle=":", alpha=0.6)
    ax.set_facecolor("white")
    _set_y_limits(ax, all_measurements)
    _shrink_y_axis(ax)

def _plot_measurements_by_operator(ax: plt.Axes, df: pd.DataFrame) -> None:
    operators = _sort_labels(df["operator"].unique())
    data = [df[df["operator"] == operator]["measurement"].values for operator in operators]
    ax.boxplot(data, tick_labels=operators, patch_artist=True, boxprops=dict(facecolor="#8cb4e2", color="#4c72b0"))
    _title(ax, "Measurement by Operator", pad=10)
    ax.set_xlabel("Operator", fontsize=9)
    ax.grid(True, axis="y", linestyle=":", alpha=0.6)
    ax.set_facecolor("white")
    _set_y_limits(ax, df["measurement"].values)
    _shrink_y_axis(ax)

def _plot_interaction(ax: plt.Axes, df: pd.DataFrame) -> None:
    means = df.groupby(["operator", "part"])["measurement"].mean()
    operators = _sort_labels(means.index.get_level_values(0).unique())
    parts = _sort_labels(df["part"].unique())
    colors = _operator_colors(len(operators))
    for idx, operator in enumerate(operators):
        series = means.loc[operator].reindex(parts)
        ax.plot(parts, series.values, marker="o", markersize=3, linewidth=0.9, color=colors[idx % len(colors)], label=str(operator))

    _title(ax, "Part * Operator Interaction", pad=10)
    ax.set_xlabel("Part", fontsize=9)
    ax.set_ylabel("Average", fontsize=9)
    ax.grid(True, axis="y", linestyle=":", alpha=0.6)
    ax.legend(fontsize=7, loc="upper left", bbox_to_anchor=(1.01, 1), frameon=True, title='Operator')
    ax.set_facecolor("white")
    _set_y_limits(ax, means.values)
    _shrink_y_axis(ax)

def _plot_gage_header(fig: plt.Figure, specs: GageRrSpecs) -> None:
    left_lines = [
        f"Gage name: {specs.gage_name}" if specs.gage_name else "Gage name:",
        f"Date of study: {specs.date_of_study}" if specs.date_of_study else "Date of study:",
    ]
    right_lines = [
        f"Reported by: {specs.reported_by}" if specs.reported_by else "Reported by:",
        f"Tolerance: {specs.tolerance:.3f}" if specs.tolerance is not None else "Tolerance:",
        f"Misc: {specs.misc}" if specs.misc else "Misc:",
    ]
    fig.text(0.06, 0.955, "\n".join(left_lines), fontsize=8, ha="left", va="top")
    fig.text(0.70, 0.955, "\n".join(right_lines), fontsize=8, ha="left", va="top")

def _plot_gage_assistant_panel(
    ax: plt.Axes,
    summary: GageRrAssistantSummary,
    *,
    parts: int,
    operators: int,
    replicates: int,
) -> None:
    ax.set_facecolor("white")
    ax.axis("off")

    lines = [
        "Gage R&R Assistant Summary",
        "",
        "Can you adequately assess process performance?",
        f"{summary.process_assessment} ({summary.process_status}) - {summary.process_percent:.1f}%",
    ]

    if summary.tolerance_percent is not None:
        lines.extend(
            [
                "",
                "Can you sort good parts from bad?",
                (
                    f"{summary.tolerance_assessment} ({summary.tolerance_status}) - "
                    f"{summary.tolerance_percent:.1f}%"
                ),
            ]
        )

    lines.extend(
        [
            "",
            "Study information",
            f"Number of parts: {parts}",
            f"Number of operators: {operators}",
            f"Replicates per part/operator: {replicates}",
            "",
            "Comments",
        ]
    )
    lines.extend(summary.comments)

    ax.text(
        0.02,
        0.98,
        "\n".join(lines),
        ha="left",
        va="top",
        fontsize=8,
        linespacing=1.35,
        wrap=True,
    )

def _plot_assistant_gauge(
    ax: plt.Axes,
    percent: float,
    label: str,
    assessment: str,
    detail_line: Optional[str] = None,
) -> None:
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.45, 1.05)
    ax.axis("off")

    ax.barh(0.5, 10, height=0.28, left=0, color="#2ca02c")
    ax.barh(0.5, 20, height=0.28, left=10, color="#ffbf00")
    ax.barh(0.5, 70, height=0.28, left=30, color="#d62728")
    ax.axvline(percent, ymin=0.54, ymax=0.73, color="#333333", linewidth=2.5)

    ax.text(0, 0.95, label, fontsize=9, fontweight="bold", ha="left")
    ax.text(
        1.02,
        0.5,
        "No",
        fontsize=9,
        fontweight="bold",
        ha="left",
        va="center",
        transform=ax.get_yaxis_transform(),
    )
    ax.text(
        -0.04,
        0.5,
        "Yes",
        fontsize=9,
        fontweight="bold",
        ha="right",
        va="center",
        transform=ax.get_yaxis_transform(),
    )

    tick_y = 0.74
    ax.text(0, tick_y, "0", fontsize=8, ha="right", va="center")
    ax.text(10, tick_y, "10%", fontsize=8, ha="center", va="center")
    ax.text(30, tick_y, "30%", fontsize=8, ha="center", va="center")
    ax.text(100, tick_y, "100%", fontsize=8, ha="right", va="center")
    ax.text(percent, 0.3, f"{percent:.1f}%", fontsize=9, ha="center", va="top")
    _ = assessment
    if detail_line:
        ax.text(-10, 0, detail_line, fontsize=7, ha="left", va="top", clip_on=False)

def _plot_assistant_variation(
    ax: plt.Axes,
    gage_table: GageRrTable,
) -> None:
    lookup = {row[0]: row for row in gage_table.rows}
    labels = ["Total Gage", "Repeat", "Reprod"]
    keys = ["Total Gage R&R", "Repeatability", "Reproducibility"]
    study_values = [float(lookup[key][3]) for key in keys]
    tolerance_values = None
    if lookup[keys[0]][4]:
        tolerance_values = [float(lookup[key][4]) for key in keys]

    x = np.arange(len(labels))
    width = 0.35 if tolerance_values is None else 0.25
    ax.bar(x - width / 2, study_values, width, color="#1f77b4", label="%Study Var")
    if tolerance_values is not None:
        ax.bar(x + width / 2, tolerance_values, width, color="#8cb4e2", label="%Tolerance")

    ax.set_title("Variation by Source", fontsize=10, pad=8, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("Percent", fontsize=8)
    ax.grid(True, axis="y", linestyle=":", alpha=0.6)
    ax.set_facecolor("white")
    max_value = max(study_values + (tolerance_values or []))
    ax.set_ylim(0, max(40, max_value * 1.15))
    ax.axhline(10, color="#2ca02c", linewidth=1, alpha=0.4)
    ax.axhline(30, color="#d62728", linewidth=1, alpha=0.4)
    ax.legend(fontsize=7, frameon=True, loc="upper left", bbox_to_anchor=(1.02, 1.02))
    ax.text(1.02, 10, "10", color="#2ca02c", fontsize=8, ha="left", va="center", transform=ax.get_yaxis_transform())
    ax.text(1.02, 30, "30", color="#d62728", fontsize=8, ha="left", va="center", transform=ax.get_yaxis_transform())

def _render_assistant_report(
    summary: GageRrAssistantSummary,
    *,
    parts: int,
    operators: int,
    replicates: int,
    gage_table: GageRrTable,
    variance_table: GageRrTable,
    output_path: Path,
) -> None:
    fig = plt.figure(figsize=(9.5, 5.1), dpi=150)
    fig.patch.set_facecolor("#e0e0e0")
    fig.suptitle("Gage R&R Study for Measurements\nSummary Report", fontsize=12, fontweight="bold", y=0.98)

    grid = fig.add_gridspec(
        3,
        2,
        width_ratios=[1, 1.6],
        height_ratios=[1.0, 1.0, 1.45],
        hspace=0.3,
        wspace=0.4,
    )
    process_line = (
        f"The measurement system variation equals {summary.process_percent:.1f}% of the process variation.\nThe process variation is estimated from the parts in the study"
    )
    _plot_assistant_gauge(
        fig.add_subplot(grid[0, 0]),
        summary.process_percent,
        "Can you adequately assess process performance?",
        summary.process_status,
        process_line,
    )

    if summary.tolerance_percent is not None:
        tolerance_line = (
            f"The measurement system variation equals {summary.tolerance_percent:.1f}% of the tolerance."
        )
        _plot_assistant_gauge(
            fig.add_subplot(grid[1, 0]),
            summary.tolerance_percent,
            "Can you sort good parts from bad?",
            summary.tolerance_status or "",
            tolerance_line,
        )
    else:
        ax = fig.add_subplot(grid[1, 0])
        ax.axis("off")

    variation_ax = fig.add_subplot(grid[2, 0])
    _plot_assistant_variation(variation_ax, gage_table)
    _shrink_x_axis(variation_ax, 0.9)

    comments_ax = fig.add_subplot(grid[:, 1])
    comments_ax.axis("off")
    comments_ax.set_facecolor("white")

    comments_ax.text(0.02, 0.95, "Study Information", fontsize=9, fontweight="bold", ha="left")
    comments_ax.add_line(plt.Line2D([0.02, 0.98], [0.93, 0.93], color="#666666", linewidth=1))
    study_lines = [
        f"Number of parts in study  {parts}",
        f"Number of operators in study  {operators}",
        f"Number of replicates  {replicates}",
        "(Replicates: Number of times each operator measured each part)",
    ]
    comments_ax.text(0.04, 0.90, "\n".join(study_lines), fontsize=8, ha="left", va="top")

    comments_ax.text(0.02, 0.70, "Comments", fontsize=9, fontweight="bold", ha="left")
    comments_ax.add_line(plt.Line2D([0.02, 0.98], [0.68, 0.68], color="#666666", linewidth=1))
    comments_ax.add_patch(
        Rectangle((0.02, 0.0), 0.96, 0.65, fill=True, facecolor="white", edgecolor="#666666", linewidth=1)
    )
    variance_lookup = {row[0]: row for row in variance_table.rows}
    total_gage_var = _parse_float(variance_lookup["Total Gage R&R"][1])
    repeat_var = _parse_float(variance_lookup["Repeatability"][1])
    repro_var = _parse_float(variance_lookup["Reproducibility"][1])
    total_variation = _parse_float(variance_lookup["Total Variation"][1])
    repeat_meas = 0.0 if total_gage_var <= 0 else repeat_var / total_gage_var * 100
    repro_meas = 0.0 if total_gage_var <= 0 else repro_var / total_gage_var * 100
    repeat_total = 0.0 if total_variation <= 0 else repeat_var / total_variation * 100
    repro_total = 0.0 if total_variation <= 0 else repro_var / total_variation * 100

    comment_lines = [
        "General rules used to determine the capability of the system:",
        "   <10%: acceptable",
        "   10% - 30%: marginal",
        "   >30%: unacceptable",
        "",
        "Examine the bar chart showing the sources of variation. If the",
        "total gage variation is unacceptable, look at repeatability and",
        "reproducibility to guide improvements:",
        "",
        "- Test-Retest component (Repeatability): The variation that",
        "occurs when the same person measures the same item multiple",
        (
            f"times. This equals {repeat_meas:.1f}% of the measurement variation and is"
        ),
        f"{repeat_total:.1f}% of the total variation in the process.",
        "",
        "- Operator and Operator by Part components (Reproducibility):",
        "The variation that occurs when different people measure the",
        (
            f"same item. This equals {repro_meas:.1f}% of the measurement variation"
        ),
        f"and is {repro_total:.1f}% of the total variation in the process.",
        ""
    ]
    comments_ax.text(
        0.04,
        0.63,
        "\n".join(comment_lines),
        ha="left",
        va="top",
        fontsize=8,
        linespacing=1.35,
        wrap=True,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)

def _render_table_figure(
    tables: list[GageRrTable],
    specs: GageRrSpecs,
    distinct_categories: int,
    output_path: Path,
) -> None:
    height = max(6, 1.6 * len(tables) + 2.5)
    fig, axes = plt.subplots(len(tables), 1, figsize=(7.2, height), dpi=150)
    if len(tables) == 1:
        axes = [axes]
    fig.patch.set_facecolor("#e0e0e0")

    for ax, table in zip(axes, tables):
        ax.set_facecolor("white")
        ax.axis("off")
        ax.text(0.02, 1.05, table.title, transform=ax.transAxes, fontsize=9, fontweight="bold", ha="left")
        mpl_table = ax.table(
            cellText=table.rows,
            colLabels=table.columns,
            loc="center",
            cellLoc="left",
            colLoc="left",
        )
        mpl_table.auto_set_font_size(False)
        mpl_table.set_fontsize(8)
        mpl_table.scale(1, 1.2)
        for (row, col), cell in mpl_table.get_celld().items():
            cell.set_edgecolor("#d0d0d0")
            cell.set_linewidth(0.6)
            if row == 0:
                cell.set_text_props(weight="bold")
                cell.set_facecolor("#f4f4f4")
            else:
                cell.set_facecolor("white")

    footer_lines = []
    if specs.tolerance is not None:
        footer_lines.append(f"Process tolerance = {specs.tolerance:g}")
    footer_lines.append(f"Number of Distinct Categories = {distinct_categories}")
    fig.text(0.02, 0.02, "\n".join(footer_lines), fontsize=8, ha="left", va="bottom")
    fig.tight_layout(rect=[0, 0.05, 1, 0.98])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)

def generate_gage_rr_report(
    records: Iterable[GageRrRecord],
    title: str,
    output_path: Path,
    *,
    specs: Optional[GageRrSpecs] = None,
    tables_output_path: Optional[Path] = None,
    assistant_output_path: Optional[Path] = None,
) -> GageRrResult:
    _ensure_fonts()
    specs = specs or GageRrSpecs()
    df = pd.DataFrame(records)
    parts, operators, replicates = _validate_gage_rr_data(df)

    full_table, reduced_table, include_interaction, interaction_p = _anova_tables(df, specs)
    selected_table = full_table if include_interaction else reduced_table
    if selected_table is None:
        raise ValueError("Failed to build ANOVA table.")

    components, total_variation = _variance_components(
        selected_table, parts, operators, replicates, include_interaction
    )
    variance_table = _build_variance_table(components, total_variation)
    gage_eval_table = _build_gage_eval_table(components, total_variation, specs)

    assistant_summary = _assistant_summary(
        variance_table,
        gage_eval_table,
        parts=parts,
        operators=operators,
        replicates=replicates,
    )

    component_lookup = {label: value for label, value in components}
    ndc = _distinct_categories(
        component_lookup.get("Part-To-Part", 0.0),
        component_lookup.get("Total Gage R&R", 0.0),
    )

    fig = plt.figure(figsize=(10, 7.2), dpi=150)
    if _FONT_BOLD_PROP is not None:
        fig_title = fig.suptitle(
            title, fontsize=12, y=0.992, x=0.06, ha="left", fontproperties=_FONT_BOLD_PROP
        )
        fig_title.set_fontweight("bold")
    elif _FONT_PROP is not None:
        fig_title = fig.suptitle(
            title, fontsize=12, y=0.992, x=0.06, ha="left", fontproperties=_FONT_PROP
        )
        fig_title.set_fontweight("bold")
    else:
        fig.suptitle(title, fontsize=12, y=0.992, x=0.06, ha="left", fontweight="bold")
    fig.patch.set_facecolor("#e0e0e0")

    _plot_gage_header(fig, specs)
    grid = fig.add_gridspec(3, 2, hspace=0.5, wspace=0.45)
    _plot_components_of_variation(fig.add_subplot(grid[0, 0]), variance_table, gage_eval_table)
    _plot_measurements_by_part(fig.add_subplot(grid[0, 1]), df)
    _plot_r_chart_by_operator(fig.add_subplot(grid[1, 0]), df, replicates)
    _plot_measurements_by_operator(fig.add_subplot(grid[1, 1]), df)
    _plot_xbar_chart_by_operator(fig.add_subplot(grid[2, 0]), df, replicates)
    _plot_interaction(fig.add_subplot(grid[2, 1]), df)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(rect=[0, 0, 1, 0.86])
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)

    if tables_output_path is None:
        tables_output_path = output_path.with_name(f"{output_path.stem}_tables.png")
    if assistant_output_path is None:
        assistant_output_path = output_path.with_name(f"{output_path.stem}_assistant.png")
    table_list = [full_table]
    if reduced_table is not None:
        table_list.append(reduced_table)
    table_list.extend([variance_table, gage_eval_table])
    _render_table_figure(table_list, specs, ndc, tables_output_path)
    _render_assistant_report(
        assistant_summary,
        parts=parts,
        operators=operators,
        replicates=replicates,
        gage_table=gage_eval_table,
        variance_table=variance_table,
        output_path=assistant_output_path,
    )

    return GageRrResult(
        anova_with_interaction=full_table,
        anova_without_interaction=reduced_table,
        variance_components=variance_table,
        gage_evaluation=gage_eval_table,
        distinct_categories=ndc,
        interaction_p_value=interaction_p,
    )


def generate_sixpack(
    values: Iterable[float],
    specs: CapabilitySpecs,
    title: str,
    output_path: Path,
    *,
    use_downloaded_fonts: Optional[bool] = None,
) -> CapabilityStats:
    if use_downloaded_fonts is not False:
        _ensure_fonts()
    values_array = np.asarray(list(values), dtype=float)
    _validate_capability_inputs(values_array, specs, min_count=5, context="sixpack")

    stats = _capability_stats(values_array, specs)

    fig = plt.figure(figsize=(10, 7), dpi=150)
    if _FONT_BOLD_PROP is not None:
        fig_title = fig.suptitle(title, fontsize=12, y=0.98, fontproperties=_FONT_BOLD_PROP)
        fig_title.set_fontweight("bold")
    elif _FONT_PROP is not None:
        fig_title = fig.suptitle(title, fontsize=12, y=0.98, fontproperties=_FONT_PROP)
        fig_title.set_fontweight("bold")
    else:
        fig.suptitle(title, fontsize=12, y=0.98, fontweight="bold")
    fig.patch.set_facecolor("#e0e0e0")
    grid = fig.add_gridspec(3, 2, hspace=0.6, wspace=0.35)

    _plot_i_chart(fig.add_subplot(grid[0, 0]), values_array, stats)
    _plot_histogram(fig.add_subplot(grid[0, 1]), values_array, stats, specs)
    _plot_mr_chart(fig.add_subplot(grid[1, 0]), values_array)
    _plot_probability(fig.add_subplot(grid[1, 1]), values_array, stats)
    _plot_last_observations(fig.add_subplot(grid[2, 0]), values_array, stats)
    _plot_capability(fig.add_subplot(grid[2, 1]), stats, specs)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)

    return stats

def generate_capability_analysis(
    values: Iterable[float],
    specs: CapabilitySpecs,
    title: str,
    output_path: Path,
    *,
    use_downloaded_fonts: Optional[bool] = None,
) -> CapabilityAnalysisResult:
    if use_downloaded_fonts is not False:
        _ensure_fonts()
    values_array = np.asarray(list(values), dtype=float)
    _validate_capability_inputs(values_array, specs, min_count=5, context="capability analysis")

    stats = _capability_stats(values_array, specs)
    indices = _capability_indices(stats, specs)
    performance = _performance_ppm(values_array, stats, specs)

    _plot_capability_analysis_report(values_array, stats, indices, performance, specs, title, output_path)

    return CapabilityAnalysisResult(stats=stats, indices=indices, performance=performance)


def _synthetic_data(seed: int = 42) -> np.ndarray:
    rng = np.random.default_rng(seed)
    data = rng.normal(loc=104.6, scale=1.1, size=100)
    drift = np.linspace(-0.3, 0.3, num=100)
    return data + drift

def _operator_labels(count: int) -> list[str]:
    if count < 1:
        raise ValueError("Operator count must be at least 1.")
    labels = []
    for idx in range(count):
        labels.append(chr(ord("A") + idx) if idx < 26 else f"Op{idx + 1}")
    return labels

def _synthetic_gage_rr_data(
    *,
    parts_count: int = 10,
    operators_count: int = 3,
    seed: int = 42,
) -> list[GageRrRecord]:
    rng = np.random.default_rng(seed)
    if parts_count < 2:
        raise ValueError("Parts count must be at least 2.")
    if operators_count < 2:
        raise ValueError("Operators count must be at least 2.")
    parts = [str(idx) for idx in range(1, parts_count + 1)]
    operators = _operator_labels(operators_count)
    trials = 3
    part_offsets = rng.normal(loc=0.0, scale=0.6, size=len(parts))
    bias_offsets = np.linspace(-0.2, 0.2, num=len(operators))
    operator_bias = {operator: float(offset) for operator, offset in zip(operators, bias_offsets)}
    records: list[GageRrRecord] = []
    for part, offset in zip(parts, part_offsets):
        for operator in operators:
            for _ in range(trials):
                noise = rng.normal(loc=0.0, scale=0.2)
                measurement = 10.0 + offset + operator_bias[operator] + noise
                records.append(GageRrRecord(part=part, operator=operator, measurement=float(measurement)))
    return records


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a capability sixpack report.")
    parser.add_argument(
        "--download-fonts",
        action="store_true",
        help="Download Plus Jakarta Sans fonts and use them for the report.",
    )
    parser.add_argument(
        "--capability-analysis",
        action="store_true",
        help="Generate a capability analysis (Normal) report.",
    )
    parser.add_argument(
        "--gage-rr",
        action="store_true",
        help="Generate a Gage R&R (ANOVA) report instead of a sixpack.",
    )
    parser.add_argument(
        "--gage-parts",
        type=int,
        default=10,
        help="Number of parts to use for synthetic Gage R&R data.",
    )
    parser.add_argument(
        "--gage-operators",
        type=int,
        default=3,
        help="Number of operators to use for synthetic Gage R&R data.",
    )
    return parser.parse_args()

def main() -> None:
    args = _parse_args()
    if args.download_fonts:
        download_fonts()

    if args.gage_rr:
        output = Path("output/gage_rr_report.png")
        assistant_output = Path("output/gage_rr_assistant.png")
        gage_specs = GageRrSpecs(tolerance=8.0, gage_name="Measurement", reported_by="", misc="")
        result = generate_gage_rr_report(
            _synthetic_gage_rr_data(
                parts_count=args.gage_parts,
                operators_count=args.gage_operators,
            ),
            "Gage R&R (ANOVA) Report for Measurement",
            output,
            specs=gage_specs,
            assistant_output_path=assistant_output,
        )
        print(f"Gage R&R report saved to {output.resolve()}")
        print(f"Gage R&R assistant saved to {assistant_output.resolve()}")
        print(_format_table(result.anova_with_interaction))
        if result.anova_without_interaction is not None:
            print("\n" + _format_table(result.anova_without_interaction))
        print("\n" + _format_table(result.variance_components))
        print("\n" + _format_table(result.gage_evaluation))
        print(f"\nNumber of Distinct Categories = {result.distinct_categories}")
    elif args.capability_analysis:
        values = _synthetic_data()
        specs = CapabilitySpecs(lsl=103.0, usl=110.0, target=104.0)
        output = Path("output/capability_analysis_report.png")

        result = generate_capability_analysis(
            values,
            specs,
            "Process Capability Report for data",
            output,
        )

        print(f"Capability analysis saved to {output.resolve()}")
        print(
            "Capability analysis summary:",
            f"Mean={result.stats.mean:.3f}",
            f"Within Sigma={result.stats.within_sigma:.3f}",
            f"Overall Sigma={result.stats.overall_sigma:.3f}",
        )
    else:
        values = _synthetic_data()
        specs = CapabilitySpecs(lsl=103.0, usl=110.0, target=104.0)
        output = Path("output/sixpack_report.png")

        stats = generate_sixpack(
            values,
            specs,
            "Process Capability Sixpack Report for data",
            output,
        )

        print(f"Sixpack saved to {output.resolve()}")
        print(
            "Capability summary:",
            f"Mean={stats.mean:.3f}",
            f"Within Sigma={stats.within_sigma:.3f}",
            f"Overall Sigma={stats.overall_sigma:.3f}",
        )


if __name__ == "__main__":
    main()
