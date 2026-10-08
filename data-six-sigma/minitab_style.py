"""Shared Minitab-style plotting helpers for the Data Six Sigma notebooks.

Every course notebook used to hand-roll its own Matplotlib/Seaborn styling
(``steelblue`` bars, ``sns.set_style('whitegrid')``, ad-hoc figure sizes).
That produced 38 notebooks that each looked slightly different and none of
them matched Minitab.

This module centralises the house style described in the
``Minitab-style-chart`` skill so a chart is one function call:

* figure background  ``#e0e0e0``  (Minitab's gray frame)
* axes background   ``white``
* data / within      ``#1f77b4``  blue
* centre line / mean ``#2ca02c``  green
* limits / overall   ``#d62728``  red
* histogram fill     ``#8cb4e2``  with ``#4c72b0`` border
* gold highlight     ``#ffbf00``
* dotted light-gray grid on the primary axis only

Typical use::

    from minitab_style import minitab_hist, minitab_box

    minitab_hist(df['Processing_Time'], title='Histogram of processing time')
"""

from __future__ import annotations

import os

import matplotlib


def _in_ipython() -> bool:
    """True when running inside IPython/Jupyter (inline plotting available)."""
    try:
        from IPython import get_ipython
    except ImportError:
        return False
    return get_ipython() is not None


# Backend selection is deliberately left alone. Forcing "Agg" here would stop
# Jupyter's inline backend from capturing figures, so plt.show() would render
# nothing. Only fall back to Agg for headless *script* usage, detected by the
# absence of any inline/IPython kernel.
if "MPLBACKEND" not in os.environ and not _in_ipython():
    matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler
from matplotlib.patches import Rectangle
from scipy import stats as scipy_stats

__all__ = [
    "FRAME",
    "AXES_BG",
    "BLUE",
    "GREEN",
    "RED",
    "GOLD",
    "HIST_FILL",
    "HIST_EDGE",
    "GRAY",
    "DARK_GRAY",
    "GRID",
    "CATEGORICAL",
    "apply_style",
    "style_axes",
    "new_figure",
    "finish",
    "title",
    "histogram",
    "overlay_density",
    "boxplot",
    "scatter",
    "bar",
    "pareto",
    "probability_plot",
    "control_chart",
    "empirical_cdf",
    "fit_line",
    "residual_chart",
    "annotation_box",
    "boxplot_by_group",
    "stacked_bar",
    "interval_plot",
    "minitab_cmap",
]

# --------------------------------------------------------------------------
# Palette
# --------------------------------------------------------------------------
FRAME = "#e0e0e0"       # outer figure background (Minitab gray)
AXES_BG = "white"       # plotting area
BLUE = "#1f77b4"        # individual values / within-subgroup
GREEN = "#2ca02c"       # centre line, mean, target
RED = "#d62728"         # control & spec limits, overall curve
GOLD = "#ffbf00"        # tolerance highlight
HIST_FILL = "#8cb4e2"   # histogram bars
HIST_EDGE = "#4c72b0"   # histogram bar border
GRAY = "#8c8c8c"        # de-emphasised scatter
DARK_GRAY = "#6b6b6b"   # dividers, box borders
GRID = "#d3d3d3"        # dotted grid lines

# Ordered categorical palette, used for pies / multi-series bars. Declared
# here so notebooks can pass ``colors=ms.CATEGORICAL``.
CATEGORICAL = [BLUE, HIST_FILL, GOLD, GREEN, GRAY, RED]

_TICK_LABELS = 8
_AXIS_LABELS = 9
_TITLES = 10


def apply_style() -> None:
    """Install the Minitab rcParams. Call once per notebook, in the setup cell."""
    plt.rcParams.update(
        {
            "figure.facecolor": FRAME,
            "savefig.facecolor": FRAME,
            "axes.facecolor": AXES_BG,
            "axes.edgecolor": "#666666",
            "axes.linewidth": 0.8,
            "axes.grid": True,
            "axes.grid.axis": "y",
            "grid.linestyle": ":",
            "grid.linewidth": 0.6,
            "grid.color": GRID,
            "grid.alpha": 0.6,
            "axes.titlesize": _TITLES,
            "axes.titleweight": "bold",
            "axes.labelsize": _AXIS_LABELS,
            "axes.axisbelow": True,
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans"],
            "font.size": 9,
            "xtick.labelsize": _TICK_LABELS,
            "ytick.labelsize": _TICK_LABELS,
            "xtick.color": "#333333",
            "ytick.color": "#333333",
            "legend.fontsize": 8,
            "legend.frameon": True,
            "legend.framealpha": 1.0,
            "legend.edgecolor": "#cccccc",
            "legend.facecolor": "white",
            "figure.dpi": 110,
            "savefig.dpi": 150,
            "savefig.bbox": "tight",
            "lines.linewidth": 1.0,
            # So plots that never name a colour still come out Minitab-blue
            # instead of matplotlib's default red/blue cycle.
            "axes.prop_cycle": cycler(color=CATEGORICAL),
            "patch.facecolor": HIST_FILL,
            "patch.edgecolor": HIST_EDGE,
        }
    )


def style_axes(ax, *, y_grid: bool = True, x_grid: bool = False) -> None:
    """Apply the white plot area + dotted grid to an existing axes."""
    ax.set_facecolor(AXES_BG)
    ax.grid(y_grid, axis="y", linestyle=":", color=GRID, alpha=0.6, linewidth=0.6)
    if x_grid:
        ax.grid(True, axis="x", linestyle=":", color=GRID, alpha=0.6, linewidth=0.6)
    for spine in ax.spines.values():
        spine.set_color("#666666")
        spine.set_linewidth(0.8)
    ax.tick_params(labelsize=_TICK_LABELS)


def new_figure(nrows: int = 1, ncols: int = 1, figsize=(9.0, 5.0), **kwargs):
    """Create a figure with the Minitab gray frame already applied."""
    apply_style()
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, **kwargs)
    for ax in np.atleast_1d(axes).ravel():
        style_axes(ax)
    return fig, axes


def finish(fig, *, rect=None, show: bool = True):
    """Tidy the layout and render. ``rect`` reserves room for a suptitle."""
    if rect is not None:
        fig.tight_layout(rect=rect)
    else:
        fig.tight_layout()
    if show:
        plt.show()
    return fig


def title(ax, text: str, pad: int = 8) -> None:
    """Bold Minitab-style subplot title."""
    ax.set_title(text, fontsize=_TITLES, fontweight="bold", pad=pad)


# --------------------------------------------------------------------------
# Distribution charts
# --------------------------------------------------------------------------
def histogram(
    values,
    *,
    bins=15,
    title_text: str = "Histogram",
    xlabel: str = "",
    ylabel: str = "Frequency",
    mean_line: bool = True,
    median_line: bool = False,
    normal_fit: bool = False,
    figsize=(9.0, 5.0),
    show: bool = True,
):
    """Minitab-style simple histogram with optional mean / normal overlay."""
    values = np.asarray(pd_series(values), dtype=float)
    values = values[~np.isnan(values)]
    fig, ax = new_figure(figsize=figsize)

    ax.hist(
        values,
        bins=bins,
        color=HIST_FILL,
        edgecolor=HIST_EDGE,
        linewidth=0.8,
        alpha=0.85,
    )
    style_axes(ax)

    if normal_fit and values.size > 2:
        overlay_density(ax, values, mean=values.mean(), sigma=values.std(ddof=1))

    if mean_line:
        m = float(np.mean(values))
        ax.axvline(m, color=RED, linestyle="--", linewidth=1.0,
                   label=f"Mean = {m:.2f}")
    if median_line:
        md = float(np.median(values))
        ax.axvline(md, color=GREEN, linestyle=":", linewidth=1.0,
                   label=f"Median = {md:.2f}")
    if mean_line or median_line:
        ax.legend(loc="best")

    ax.set_xlabel(xlabel, fontsize=_AXIS_LABELS)
    ax.set_ylabel(ylabel, fontsize=_AXIS_LABELS)
    title(ax, title_text)
    return finish(fig, show=show)


def overlay_density(ax, values, *, mean=None, sigma=None, label=None,
                    color=RED, linestyle="-"):
    """Draw a fitted normal PDF over an existing histogram axes."""
    values = np.asarray(pd_series(values), dtype=float)
    values = values[~np.isnan(values)]
    mean = float(np.mean(values)) if mean is None else mean
    sigma = float(np.std(values, ddof=1)) if sigma is None else sigma
    if sigma <= 0:
        return ax
    lo = min(values.min() - 0.5 * sigma, mean - 3 * sigma)
    hi = max(values.max() + 0.5 * sigma, mean + 3 * sigma)
    x = np.linspace(lo, hi, 300)
    ax.plot(x, scipy_stats.norm.pdf(x, mean, sigma), color=color,
            linewidth=1.2, linestyle=linestyle,
            label=label or f"Normal fit (μ={mean:.2f}, σ={sigma:.2f})")
    return ax


def boxplot(
    values,
    *,
    title_text: str = "Boxplot",
    ylabel: str = "",
    xlabel: str = "Observation",
    figsize=(6.0, 5.5),
    show: bool = True,
):
    """Single-variable boxplot in the Minitab palette."""
    values = np.asarray(pd_series(values), dtype=float)
    values = values[~np.isnan(values)]
    fig, ax = new_figure(figsize=figsize)
    ax.boxplot(
        values,
        vert=True,
        widths=0.4,
        patch_artist=True,
        boxprops={"facecolor": HIST_FILL, "edgecolor": HIST_EDGE, "linewidth": 1.0},
        medianprops={"color": RED, "linewidth": 1.4},
        whiskerprops={"color": DARK_GRAY, "linewidth": 1.0},
        capprops={"color": DARK_GRAY, "linewidth": 1.0},
        flierprops={"marker": "o", "markerfacecolor": RED,
                    "markeredgecolor": RED, "markersize": 4, "alpha": 0.7},
    )
    style_axes(ax)
    ax.set_xticks([])
    ax.set_xlabel(xlabel, fontsize=_AXIS_LABELS)
    ax.set_ylabel(ylabel, fontsize=_AXIS_LABELS)
    title(ax, title_text)
    return finish(fig, show=show)


def boxplot_by_group(
    frame,
    group_col: str,
    value_col: str,
    *,
    title_text: str = "Boxplot",
    ylabel: str = "",
    xlabel: str = "",
    figsize=(9.0, 5.0),
    show: bool = True,
):
    """Boxplot of ``value_col`` grouped by ``group_col``."""
    groups = list(dict.fromkeys(frame[group_col].dropna().tolist()))
    data = [frame.loc[frame[group_col] == g, value_col].dropna().values
            for g in groups]
    fig, ax = new_figure(figsize=figsize)
    ax.boxplot(
        data,
        vert=True,
        patch_artist=True,
        widths=0.5,
        boxprops={"facecolor": HIST_FILL, "edgecolor": HIST_EDGE, "linewidth": 1.0},
        medianprops={"color": RED, "linewidth": 1.4},
        whiskerprops={"color": DARK_GRAY, "linewidth": 1.0},
        capprops={"color": DARK_GRAY, "linewidth": 1.0},
        flierprops={"marker": "o", "markerfacecolor": RED,
                    "markeredgecolor": RED, "markersize": 4, "alpha": 0.7},
    )
    style_axes(ax)
    ax.set_xticks(range(1, len(groups) + 1))
    ax.set_xticklabels([str(g) for g in groups], fontsize=_TICK_LABELS)
    ax.set_xlabel(xlabel or group_col, fontsize=_AXIS_LABELS)
    ax.set_ylabel(ylabel or value_col, fontsize=_AXIS_LABELS)
    title(ax, title_text)
    return finish(fig, show=show)


# --------------------------------------------------------------------------
# Categorical charts
# --------------------------------------------------------------------------
def bar(
    labels,
    heights,
    *,
    title_text: str = "Bar Chart",
    xlabel: str = "",
    ylabel: str = "Count",
    value_labels: bool = True,
    color=HIST_FILL,
    edgecolor=HIST_EDGE,
    rotate: int = 0,
    figsize=(9.0, 5.0),
    show: bool = True,
):
    """Vertical bar chart with Minitab bar colours and optional value labels."""
    labels = [str(v) for v in labels]
    heights = np.asarray(pd_series(heights), dtype=float)
    x = np.arange(len(labels))
    fig, ax = new_figure(figsize=figsize)
    ax.bar(x, heights, color=color, edgecolor=edgecolor, linewidth=0.8, alpha=0.9)
    style_axes(ax)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=rotate, ha="right" if rotate else "center",
                       fontsize=_TICK_LABELS)
    ax.set_xlabel(xlabel, fontsize=_AXIS_LABELS)
    ax.set_ylabel(ylabel, fontsize=_AXIS_LABELS)
    if value_labels and len(heights):
        span = float(np.nanmax(heights)) or 1.0
        for xi, h in zip(x, heights):
            ax.text(xi, h + span * 0.02, f"{h:g}", ha="center", va="bottom",
                    fontsize=8, color="#333333")
        ax.set_ylim(0, float(np.nanmax(heights)) * 1.15)
    title(ax, title_text)
    return finish(fig, show=show)


def stacked_bar(
    frame,
    category_col: str,
    series_cols,
    *,
    title_text: str = "Stacked Bar Chart",
    xlabel: str = "",
    ylabel: str = "Count",
    figsize=(9.0, 5.0),
    show: bool = True,
):
    """Stacked bars of several count columns across categories."""
    cats = list(dict.fromkeys(frame[category_col].dropna().tolist()))
    cols = list(series_cols)
    x = np.arange(len(cats))
    bottom = np.zeros(len(cats))
    palette = [BLUE, HIST_FILL, GOLD, GREEN, GRAY, RED]
    fig, ax = new_figure(figsize=figsize)
    for i, c in enumerate(cols):
        heights = np.array(
            [float((frame.loc[frame[category_col] == cat, c] == True).sum())  # noqa: E712
             for cat in cats]
        )
        ax.bar(x, heights, bottom=bottom, label=str(c),
               color=palette[i % len(palette)], edgecolor="white", linewidth=0.6)
        bottom += heights
    style_axes(ax)
    ax.set_xticks(x)
    ax.set_xticklabels([str(c) for c in cats], fontsize=_TICK_LABELS)
    ax.set_xlabel(xlabel or category_col, fontsize=_AXIS_LABELS)
    ax.set_ylabel(ylabel, fontsize=_AXIS_LABELS)
    ax.legend(loc="best")
    title(ax, title_text)
    return finish(fig, show=show)


def pareto(
    counts,
    *,
    title_text: str = "Pareto Chart",
    xlabel: str = "Cause",
    ylabel: str = "Count",
    threshold: float = 80.0,
    figsize=(10.0, 5.5),
    show: bool = True,
    return_values: bool = False,
):
    """Pareto chart: descending bars + cumulative-% line with the 80% rule.

    ``counts`` may be a pandas Series (index = category) or a plain mapping.
    """
    if hasattr(counts, "sort_values"):
        ordered = counts.sort_values(ascending=False)
        labels = [str(i) for i in ordered.index]
        values = np.asarray(ordered.values, dtype=float)
    else:
        pairs = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
        labels = [str(k) for k, _ in pairs]
        values = np.asarray([v for _, v in pairs], dtype=float)

    total = values.sum()
    cumulative = np.cumsum(values) / total * 100 if total else np.zeros_like(values)

    fig, ax1 = new_figure(figsize=figsize)
    ax2 = ax1.twinx()
    ax2.set_facecolor(AXES_BG)
    ax2.grid(False)

    x = np.arange(len(labels))
    ax1.bar(x, values, color=HIST_FILL, edgecolor=HIST_EDGE,
            linewidth=0.8, alpha=0.9, label=ylabel)
    style_axes(ax1)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=45, ha="right", fontsize=_TICK_LABELS)
    ax1.set_xlabel(xlabel, fontsize=_AXIS_LABELS)
    ax1.set_ylabel(ylabel, fontsize=_AXIS_LABELS)
    if len(values):
        span = float(values.max())
        for xi, v in zip(x, values):
            ax1.text(xi, v + span * 0.02, f"{v:g}", ha="center", va="bottom",
                     fontsize=8, color="#333333")
        ax1.set_ylim(0, span * 1.18)

    ax2.plot(x, cumulative, color=RED, marker="o", markersize=4,
             linewidth=1.2, label="Cumulative %")
    ax2.axhline(threshold, color=DARK_GRAY, linestyle="--", linewidth=1.0,
                alpha=0.7, label=f"{threshold:g}% threshold")
    ax2.set_ylim(0, 105)
    ax2.set_ylabel("Cumulative %", fontsize=_AXIS_LABELS, color=RED)
    ax2.tick_params(axis="y", labelsize=_TICK_LABELS, colors=RED)

    handles = ax1.get_legend_handles_labels()[0] + ax2.get_legend_handles_labels()[0]
    labels_leg = ax1.get_legend_handles_labels()[1] + ax2.get_legend_handles_labels()[1]
    ax1.legend(handles, labels_leg, loc="upper right")

    title(ax1, title_text)
    fig.tight_layout()
    if show:
        plt.show()
    if return_values:
        return labels, values, cumulative
    return fig


# --------------------------------------------------------------------------
# Relationship charts
# --------------------------------------------------------------------------
def scatter(
    x,
    y,
    *,
    title_text: str = "Scatterplot",
    xlabel: str = "X",
    ylabel: str = "Y",
    fit: bool = False,
    color=BLUE,
    figsize=(7.0, 5.5),
    show: bool = True,
):
    """Scatterplot with an optional least-squares reference line."""
    x = np.asarray(pd_series(x), dtype=float)
    y = np.asarray(pd_series(y), dtype=float)
    mask = ~(np.isnan(x) | np.isnan(y))
    x, y = x[mask], y[mask]

    fig, ax = new_figure(figsize=figsize)
    ax.scatter(x, y, color=color, s=22, alpha=0.8, edgecolors="white",
               linewidths=0.4, zorder=3)
    style_axes(ax)

    if fit and x.size > 2 and np.ptp(x) > 0:
        slope, intercept = np.polyfit(x, y, 1)
        r = np.corrcoef(x, y)[0, 1]
        xs = np.linspace(x.min(), x.max(), 100)
        ax.plot(xs, slope * xs + intercept, color=RED, linewidth=1.2,
                label=f"y = {slope:.3f}x + {intercept:.2f}   (r = {r:.3f})")
        ax.legend(loc="best")

    ax.set_xlabel(xlabel, fontsize=_AXIS_LABELS)
    ax.set_ylabel(ylabel, fontsize=_AXIS_LABELS)
    title(ax, title_text)
    return finish(fig, show=show)


def fit_line(ax, x, y, *, color=RED, label=None, confidence: bool = False):
    """Overlay a least-squares fit (and optional 95% CI band) on ``ax``."""
    x = np.asarray(pd_series(x), dtype=float)
    y = np.asarray(pd_series(y), dtype=float)
    mask = ~(np.isnan(x) | np.isnan(y))
    x, y = x[mask], y[mask]
    if x.size < 3 or np.ptp(x) == 0:
        return None
    slope, intercept, r, p, stderr = scipy_stats.linregress(x, y)
    xs = np.linspace(x.min(), x.max(), 100)
    ax.plot(xs, slope * xs + intercept, color=color, linewidth=1.3,
            label=label or f"Fit: y = {slope:.3f}x + {intercept:.2f}")
    if confidence:
        n = x.size
        yhat = slope * x + intercept
        ss_res = float(((y - yhat) ** 2).sum())
        s_err = np.sqrt(ss_res / (n - 2))
        tcrit = scipy_stats.t.ppf(0.975, n - 2)
        mean_se = s_err * np.sqrt(1 / n + (xs - x.mean()) ** 2 /
                                  float(((x - x.mean()) ** 2).sum()))
        pred_se = s_err * np.sqrt(1 + 1 / n + (xs - x.mean()) ** 2 /
                                  float(((x - x.mean()) ** 2).sum()))
        ax.fill_between(xs, slope * xs + intercept - tcrit * pred_se,
                        slope * xs + intercept + tcrit * pred_se,
                        color=color, alpha=0.12, linewidth=0)
    return slope, intercept, r, p, stderr


def residual_chart(x, y, *, title_text: str = "Residual Plot",
                   xlabel: str = "X", ylabel: str = "Residual",
                   figsize=(7.0, 5.0), show: bool = True):
    """Residuals vs fitted, with the zero reference line."""
    x = np.asarray(pd_series(x), dtype=float)
    y = np.asarray(pd_series(y), dtype=float)
    mask = ~(np.isnan(x) | np.isnan(y))
    x, y = x[mask], y[mask]
    slope, intercept = np.polyfit(x, y, 1)
    resid = y - (slope * x + intercept)

    fig, ax = new_figure(figsize=figsize)
    ax.scatter(x, resid, color=BLUE, s=22, alpha=0.8, edgecolors="white",
               linewidths=0.4, zorder=3)
    ax.axhline(0.0, color=RED, linewidth=1.1)
    style_axes(ax)
    ax.set_xlabel(xlabel, fontsize=_AXIS_LABELS)
    ax.set_ylabel(ylabel, fontsize=_AXIS_LABELS)
    title(ax, title_text)
    return finish(fig, show=show)


# --------------------------------------------------------------------------
# Distribution-fit diagnostics
# --------------------------------------------------------------------------
def probability_plot(values, *, title_text: str = "Normal Probability Plot",
                     xlabel: str = "Observation", figsize=(7.0, 5.5),
                     show: bool = True, reference: bool = True):
    """Normal probability plot with AD statistic, Minitab style."""
    values = np.asarray(pd_series(values), dtype=float)
    values = np.sort(values[~np.isnan(values)])
    n = values.size
    fig, ax = new_figure(figsize=figsize)

    (osm, osr), (slope, intercept, _) = scipy_stats.probplot(values, dist="norm")
    slope = float(np.asarray(slope).ravel()[0])
    intercept = float(np.asarray(intercept).ravel()[0])
    ax.scatter(osm, values, color=BLUE, s=22, alpha=0.85,
               edgecolors="white", linewidths=0.4, zorder=3)

    xs = np.linspace(osm.min(), osm.max(), 100)
    if reference:
        ax.plot(xs, slope * xs + intercept, color=RED, linewidth=1.2)
        se = slope
        band = 1.36 / np.sqrt(n) * np.sqrt(1 + (xs - osm.mean()) ** 2 /
                                           float(((osm - osm.mean()) ** 2).sum()))
        ax.plot(xs, slope * xs + intercept + 1.96 * se * band, color=RED,
                linestyle="--", linewidth=0.9, alpha=0.7)
        ax.plot(xs, slope * xs + intercept - 1.96 * se * band, color=RED,
                linestyle="--", linewidth=0.9, alpha=0.7)

    style_axes(ax)
    ax.set_yticks([])
    ax.set_xlabel(xlabel, fontsize=_AXIS_LABELS)
    ad = scipy_stats.anderson(values, dist="norm")
    p_val = ad.significance_level[2] if ad.statistic > ad.critical_values[2] else \
        ad.pvalue if hasattr(ad, "pvalue") else float("nan")
    annotation_box(
        ax,
        "Anderson-Darling",
        [("AD statistic", f"{ad.statistic:.3f}"),
         ("p-value", f"{p_val:.4f}")],
    )
    title(ax, title_text)
    return finish(fig, show=show)


def empirical_cdf(values, *, title_text: str = "Empirical CDF",
                  xlabel: str = "Observation", ylabel: str = "Cumulative Probability",
                  theoretical: bool = True, figsize=(7.0, 5.5), show: bool = True):
    """Empirical cumulative distribution, optionally with a normal reference."""
    values = np.asarray(pd_series(values), dtype=float)
    values = np.sort(values[~np.isnan(values)])
    n = values.size
    y = np.arange(1, n + 1) / n
    fig, ax = new_figure(figsize=figsize)
    ax.step(values, y, where="post", color=BLUE, linewidth=1.3, label="Empirical CDF")
    if theoretical and n > 2:
        mu, sigma = values.mean(), values.std(ddof=1)
        if sigma > 0:
            xs = np.linspace(values.min(), values.max(), 200)
            ax.plot(xs, scipy_stats.norm.cdf(xs, mu, sigma), color=RED,
                    linestyle="--", linewidth=1.1, label="Normal CDF")
            ax.legend(loc="lower right")
    style_axes(ax)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel(xlabel, fontsize=_AXIS_LABELS)
    ax.set_ylabel(ylabel, fontsize=_AXIS_LABELS)
    title(ax, title_text)
    return finish(fig, show=show)


def control_chart(
    values,
    *,
    title_text: str = "I-Chart",
    xlabel: str = "Observation",
    ylabel: str = "Value",
    figsize=(9.0, 4.5),
    show: bool = True,
):
    """Individuals control chart with 3-sigma limits labelled outside the axes."""
    values = np.asarray(pd_series(values), dtype=float)
    values = values[~np.isnan(values)]
    x = np.arange(1, values.size + 1)
    mean = float(values.mean())
    sigma = float(values.std(ddof=1))
    ucl, lcl = mean + 3 * sigma, mean - 3 * sigma

    fig, ax = new_figure(figsize=figsize)
    ax.plot(x, values, color=BLUE, marker="o", markersize=3, linewidth=0.8, zorder=3)
    ax.axhline(mean, color=GREEN, linewidth=1.1)
    ax.axhline(ucl, color=RED, linewidth=1.1)
    ax.axhline(lcl, color=RED, linewidth=1.1)
    style_axes(ax)
    ax.set_xlabel(xlabel, fontsize=_AXIS_LABELS)
    ax.set_ylabel(ylabel, fontsize=_AXIS_LABELS)
    title(ax, title_text)

    x0, x1 = ax.get_xlim()
    lx = x1 + (x1 - x0) * 0.03
    for y, text, color in (
        (ucl, f"UCL={ucl:.3f}", RED),
        (mean, f"X̄={mean:.3f}", GREEN),
        (lcl, f"LCL={lcl:.3f}", RED),
    ):
        ax.text(lx, y, text, fontsize=8, va="center", ha="left",
                clip_on=False, color=color)
    return finish(fig, show=show)


def interval_plot(
    centers,
    lows,
    highs,
    labels=None,
    *,
    title_text: str = "Interval Plot",
    xlabel: str = "",
    ylabel: str = "",
    figsize=(8.0, 5.0),
    show: bool = True,
):
    """Minitab-style interval plot (point estimate with error bars)."""
    centers = np.asarray(pd_series(centers), dtype=float)
    lows = np.asarray(pd_series(lows), dtype=float)
    highs = np.asarray(pd_series(highs), dtype=float)
    y = np.arange(len(centers))
    fig, ax = new_figure(figsize=figsize)
    for yi, lo, hi in zip(y, lows, highs):
        ax.hlines(yi, lo, hi, color=BLUE, linewidth=1.2)
    ax.plot(centers, y, "o", color=BLUE, markersize=5, zorder=3)
    style_axes(ax, y_grid=False, x_grid=True)
    ax.set_yticks(y)
    ax.set_yticklabels([str(v) for v in (labels if labels is not None else centers)],
                       fontsize=_TICK_LABELS)
    ax.invert_yaxis()
    ax.set_xlabel(xlabel, fontsize=_AXIS_LABELS)
    ax.set_ylabel(ylabel, fontsize=_AXIS_LABELS)
    title(ax, title_text)
    return finish(fig, show=show)


# --------------------------------------------------------------------------
# Layout helpers
# --------------------------------------------------------------------------
def annotation_box(ax, heading: str, rows, *, loc: str = "upper left",
                   fontsize: float = 8.0):
    """Boxed, borderless summary panel in the Minitab sidebar style.

    ``rows`` is an iterable of ``(label, value)`` pairs. Position uses
    axes coordinates so the panel sits inside the plot frame.
    """
    rows = list(rows)
    if loc == "upper left":
        x, y, ha, va = 0.03, 0.97, "left", "top"
    elif loc == "upper right":
        x, y, ha, va = 0.97, 0.97, "right", "top"
    elif loc == "lower left":
        x, y, ha, va = 0.03, 0.03, "left", "bottom"
    else:
        x, y, ha, va = 0.97, 0.03, "right", "bottom"

    line_h = 0.075
    height = (len(rows) + 1) * line_h + 0.06
    width = 0.44
    left = x if ha == "left" else x - width
    bottom = y - height if va == "top" else y

    ax.add_patch(
        Rectangle((left, bottom), width, height, transform=ax.transAxes,
                  facecolor="white", edgecolor="#666666", linewidth=0.9,
                  zorder=5, clip_on=False)
    )
    ax.text(left + 0.02, bottom + height - 0.045, heading, transform=ax.transAxes,
            fontsize=fontsize, fontweight="bold", zorder=6)
    for i, (label, value) in enumerate(rows):
        yy = bottom + height - 0.045 - (i + 1) * line_h
        ax.text(left + 0.02, yy, str(label), transform=ax.transAxes,
                fontsize=fontsize, zorder=6)
        ax.text(left + width - 0.02, yy, str(value), transform=ax.transAxes,
                fontsize=fontsize, ha="right", zorder=6)
    return ax


def pd_series(values):
    """Accept numpy arrays, lists, or pandas Series without importing pandas."""
    if hasattr(values, "to_numpy"):
        return values.to_numpy()
    return values


def minitab_cmap(name: str = "minitab"):
    """A discrete Minitab-coloured colormap for pandas ``colormap=``.

    ``DataFrame.plot(colormap=...)`` needs a *registered colormap object*, so a
    plain list of colors will not work. This builds one from
    :data:`CATEGORICAL`, registering it on first use.
    """
    from matplotlib import colormaps

    if name not in colormaps:
        from matplotlib.colors import ListedColormap

        colormaps.register(
            ListedColormap(CATEGORICAL, name=name), name=name, force=True
        )
    return colormaps[name]
