"""
minitab_dmaic_visuals.py
========================
Minitab-style statistical visualization toolkit specifically tailored for
Six Sigma DMAIC projects, extending and building on:
1. @skill Minitab-style-chart
2. data-six-sigma/minitab_style.py
3. src/sixpack_report.py

Provides:
- Consistent Minitab styling (Frame #e0e0e0, axes white, dotted grid, proper line colors)
- Specialized DMAIC charts:
  1. Define: SIPOC flow diagram & CTQ Pareto Chart
  2. Measure: Process Capability Sixpack / Capability Histogram (Within vs Overall)
  3. Analyze: Multi-vari boxplot, Correlation Heatmap, Main Effects & Interaction Plots
  4. Improve: Regression with prediction bands, DOE factorial optimization plot
  5. Control: I-MR / Xbar-R Control charts with out-of-control rule marking (Western Electric)
"""
from __future__ import annotations

import os
import matplotlib

# In headless/nbconvert batch execution, ensure Agg is used if not running in Jupyter interactive kernel
def _in_interactive_jupyter() -> bool:
    try:
        from IPython import get_ipython
        ip = get_ipython()
        return ip is not None and "IPKernelApp" in getattr(ip, "config", {})
    except Exception:
        return False

if not _in_interactive_jupyter() and "MPLBACKEND" not in os.environ:
    matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
import matplotlib.gridspec as gridspec
from scipy import stats as scipy_stats

# -----------------------------------------------------------------------------
# Color Palette (from Minitab-style-chart skill)
# -----------------------------------------------------------------------------
FRAME = "#e0e0e0"       # outer figure boundary
AXES_BG = "white"       # axes surface
BLUE = "#1f77b4"        # primary individual series
GREEN = "#2ca02c"       # mean / centerline / target
RED = "#d62728"         # UCL / LCL / specification limits / violations
GOLD = "#ffbf00"        # tolerance highlight / marginal
HIST_FILL = "#8cb4e2"   # histogram fill
HIST_EDGE = "#4c72b0"   # histogram border
GRAY = "#8c8c8c"        # neutral scatter points
DARK_GRAY = "#666666"   # box dividers
GRID = "#d3d3d3"        # dotted grid lines

def apply_minitab_theme():
    """Apply global Minitab rcParams."""
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning)

    plt.rcParams.update({
        "figure.facecolor": FRAME,
        "savefig.facecolor": FRAME,
        "axes.facecolor": AXES_BG,
        "axes.edgecolor": DARK_GRAY,
        "axes.linewidth": 0.8,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "grid.linestyle": ":",
        "grid.linewidth": 0.6,
        "grid.color": GRID,
        "grid.alpha": 0.7,
        "axes.titlesize": 10.5,
        "axes.titleweight": "bold",
        "axes.labelsize": 9.0,
        "xtick.labelsize": 8.0,
        "ytick.labelsize": 8.0,
        "legend.fontsize": 8.0,
        "legend.frameon": True,
        "legend.facecolor": "white",
        "legend.edgecolor": "#cccccc",
        "font.sans-serif": ["Microsoft YaHei", "SimHei", "Arial", "DejaVu Sans"],
        "axes.unicode_minus": False,
        "figure.dpi": 110,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
    })

def create_figure(figsize=(9, 5), nrows=1, ncols=1, **kwargs):
    apply_minitab_theme()
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, **kwargs)
    fig.patch.set_facecolor(FRAME)
    if isinstance(axes, np.ndarray):
        for ax in axes.flat:
            ax.set_facecolor(AXES_BG)
    else:
        axes.set_facecolor(AXES_BG)
    return fig, axes

# -----------------------------------------------------------------------------
# DEFINE PHASE VISUALS
# -----------------------------------------------------------------------------
def plot_pareto_chart(data: pd.Series, title="Pareto Chart: Defect Categories", xlabel="Defect Category", ylabel="Count", output_path=None):
    """Minitab Style Pareto chart with descending counts and cumulative % curve."""
    counts = data.sort_values(ascending=False)
    total = counts.sum()
    cum_pct = counts.cumsum() / total * 100

    fig, ax1 = create_figure(figsize=(8.5, 4.8))
    ax2 = ax1.twinx()
    ax2.set_facecolor(AXES_BG)
    ax2.grid(False)

    x = np.arange(len(counts))
    ax1.bar(x, counts.values, color=HIST_FILL, edgecolor=HIST_EDGE, linewidth=0.9, width=0.6)
    ax1.set_xticks(x)
    ax1.set_xticklabels(counts.index, rotation=30, ha="right", fontsize=8.5)
    ax1.set_ylabel(ylabel, fontsize=9)
    ax1.set_xlabel(xlabel, fontsize=9)
    ax1.set_title(title, fontsize=10.5, fontweight="bold", pad=12)

    # Add count text above bars
    for i, v in enumerate(counts.values):
        ax1.text(i, v + 0.02 * max(counts.values), f"{v}", ha="center", va="bottom", fontsize=8)

    # Plot 80% line and cumulative line
    ax2.plot(x, cum_pct.values, color=RED, marker="o", markersize=4, linewidth=1.2, label="Cumulative %")
    ax2.axhline(80, color=DARK_GRAY, linestyle="--", linewidth=1.0, alpha=0.8)
    ax2.text(len(counts) - 0.5, 81, "80% Cutoff", color=DARK_GRAY, fontsize=8, ha="right")
    ax2.set_ylabel("Cumulative Percent (%)", fontsize=9, color=RED)
    ax2.set_ylim(0, 105)

    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path)
    return fig

# -----------------------------------------------------------------------------
# MEASURE PHASE VISUALS (Capability Histogram & Sixpack)
# -----------------------------------------------------------------------------
def plot_capability_histogram(values, lsl, usl, target=None, title="Process Capability Histogram", xlabel="Measurement (mm)", output_path=None):
    """Minitab Style Capability Histogram with Within & Overall normal curves."""
    values = np.asarray(values, dtype=float)
    mean = np.mean(values)
    overall_sigma = np.std(values, ddof=1)
    
    # Within sigma by moving range
    mr = np.abs(np.diff(values))
    within_sigma = np.mean(mr) / 1.128 if len(mr) > 0 else overall_sigma

    fig, ax = create_figure(figsize=(9, 5))
    
    # Density histogram
    n_bins = 15
    ax.hist(values, bins=n_bins, color=HIST_FILL, edgecolor=HIST_EDGE, alpha=0.85, density=True)

    # Normal curves
    xs = np.linspace(min(values.min(), lsl) - 0.5 * overall_sigma, max(values.max(), usl) + 0.5 * overall_sigma, 300)
    ax.plot(xs, scipy_stats.norm.pdf(xs, mean, overall_sigma), color=RED, linewidth=1.5, label=f"Overall (s={overall_sigma:.3f})")
    ax.plot(xs, scipy_stats.norm.pdf(xs, mean, within_sigma), color=BLUE, linewidth=1.5, linestyle="--", label=f"Within (s={within_sigma:.3f})")

    # Spec limits
    ax.axvline(lsl, color=RED, linestyle="--", linewidth=1.2)
    ax.text(lsl, ax.get_ylim()[1] * 0.9, f" LSL={lsl:.2f}", color=RED, fontsize=8.5, fontweight="bold")
    ax.axvline(usl, color=RED, linestyle="--", linewidth=1.2)
    ax.text(usl, ax.get_ylim()[1] * 0.9, f" USL={usl:.2f}", color=RED, fontsize=8.5, fontweight="bold")
    if target is not None:
        ax.axvline(target, color=GREEN, linestyle=":", linewidth=1.2)
        ax.text(target, ax.get_ylim()[1] * 0.8, f" Target={target:.2f}", color=GREEN, fontsize=8.5, fontweight="bold")

    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_yticks([])  # Minitab capability histogram hides density y-ticks
    ax.legend(loc="upper right", framealpha=0.9)

    # Summary box on the side
    cp = (usl - lsl) / (6 * within_sigma) if within_sigma > 0 else 0
    cpk = min((usl - mean) / (3 * within_sigma), (mean - lsl) / (3 * within_sigma)) if within_sigma > 0 else 0
    pp = (usl - lsl) / (6 * overall_sigma) if overall_sigma > 0 else 0
    ppk = min((usl - mean) / (3 * overall_sigma), (mean - lsl) / (3 * overall_sigma)) if overall_sigma > 0 else 0

    stats_text = (
        f"Process Data\n"
        f"------------\n"
        f"Sample N: {len(values)}\n"
        f"Mean: {mean:.3f}\n"
        f"StDev(Within): {within_sigma:.3f}\n"
        f"StDev(Overall): {overall_sigma:.3f}\n\n"
        f"Potential (Within)\n"
        f"------------------\n"
        f"Cp:  {cp:.3f}\n"
        f"Cpk: {cpk:.3f}\n\n"
        f"Overall Capability\n"
        f"------------------\n"
        f"Pp:  {pp:.3f}\n"
        f"Ppk: {ppk:.3f}"
    )
    ax.text(1.02, 0.95, stats_text, transform=ax.transAxes, fontsize=8, family="monospace",
            verticalalignment="top", bbox=dict(boxstyle="square,pad=0.6", facecolor="white", edgecolor=DARK_GRAY, linewidth=0.8))

    fig.tight_layout(rect=[0, 0, 0.82, 1])
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path)
    return fig

# -----------------------------------------------------------------------------
# ANALYZE PHASE VISUALS (Correlation Matrix & ANOVA Boxplots)
# -----------------------------------------------------------------------------
def plot_correlation_heatmap(df: pd.DataFrame, title="Correlation Matrix (Pearson r)", output_path=None):
    """Minitab style clean tabular correlation matrix with color coding."""
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr(method="pearson")
    
    fig, ax = create_figure(figsize=(7.5, 6))
    cax = ax.matshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
    
    fig.colorbar(cax, ax=ax, fraction=0.046, pad=0.04)
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=45, ha="left", fontsize=8.5)
    ax.set_yticklabels(corr.columns, fontsize=8.5)
    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=20)

    for i in range(len(corr.columns)):
        for j in range(len(corr.columns)):
            val = corr.iloc[i, j]
            color = "white" if abs(val) > 0.55 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=color, fontsize=8.5, fontweight="bold")

    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path)
    return fig

def plot_anova_boxplot(df: pd.DataFrame, factor_col: str, response_col: str, title=None, output_path=None):
    """Minitab style group comparison boxplot with mean markers."""
    groups = list(df[factor_col].dropna().unique())
    data = [df[df[factor_col] == g][response_col].dropna().values for g in groups]
    means = [np.mean(d) for d in data]

    fig, ax = create_figure(figsize=(8, 4.8))
    bp = ax.boxplot(
        data,
        tick_labels=[str(g) for g in groups],
        patch_artist=True,
        boxprops=dict(facecolor=HIST_FILL, edgecolor=HIST_EDGE, linewidth=1.0),
        medianprops=dict(color=RED, linewidth=1.5),
        whiskerprops=dict(color=DARK_GRAY, linewidth=1.0),
        capprops=dict(color=DARK_GRAY, linewidth=1.0),
        flierprops=dict(marker="o", markerfacecolor=RED, markeredgecolor=RED, markersize=4)
    )

    # Overlay group means (Minitab style)
    ax.plot(range(1, len(groups) + 1), means, color=GREEN, marker="D", linestyle=":", linewidth=1.2, markersize=5, label="Group Mean")
    
    ax.set_xlabel(factor_col, fontsize=9)
    ax.set_ylabel(response_col, fontsize=9)
    ax.set_title(title or f"Boxplot of {response_col} by {factor_col}", fontsize=10.5, fontweight="bold", pad=12)
    ax.legend(loc="upper right")

    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path)
    return fig

# -----------------------------------------------------------------------------
# IMPROVE PHASE VISUALS (Regression Fit & DOE Main Effects)
# -----------------------------------------------------------------------------
def plot_regression_fit(x, y, xlabel="X", ylabel="Y", title="Fitted Line Plot", output_path=None):
    """Minitab Style Fitted Line Plot with 95% Confidence and Prediction bands."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    slope, intercept, r_value, p_value, std_err = scipy_stats.linregress(x, y)
    r2 = r_value ** 2

    fig, ax = create_figure(figsize=(8.5, 5))
    ax.scatter(x, y, color=BLUE, edgecolors="white", linewidth=0.5, s=28, alpha=0.8, label="Actual Data")

    xs = np.linspace(x.min(), x.max(), 150)
    ys = slope * xs + intercept
    ax.plot(xs, ys, color=RED, linewidth=1.4, label=f"Fit: Y = {intercept:.2f} + {slope:.3f}*X")

    # 95% Confidence Interval band
    n = len(x)
    residuals = y - (slope * x + intercept)
    s_err = np.sqrt(np.sum(residuals**2) / (n - 2))
    t_val = scipy_stats.t.ppf(0.975, df=n - 2)
    ci = t_val * s_err * np.sqrt(1/n + (xs - np.mean(x))**2 / np.sum((x - np.mean(x))**2))
    ax.fill_between(xs, ys - ci, ys + ci, color=RED, alpha=0.15, label="95% CI")

    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=12)
    
    # Model summary box
    summary_text = f"S = {s_err:.4f}\nR-sq = {r2*100:.1f}%\nR-sq(adj) = {(1 - (1-r2)*(n-1)/(n-2))*100:.1f}%\np-val = {p_value:.4f}"
    ax.text(0.04, 0.95, summary_text, transform=ax.transAxes, verticalalignment="top",
            fontsize=8.5, family="monospace", bbox=dict(boxstyle="square,pad=0.5", facecolor="white", edgecolor=DARK_GRAY, linewidth=0.8))

    ax.legend(loc="lower right")
    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path)
    return fig

def plot_doe_main_effects(df: pd.DataFrame, factor_cols: list[str], factor_names: list[str], response_col: str, title="Main Effects Plot (Minitab Style DOE)", output_path=None):
    """Minitab Style Main Effects Plot across multiple experimental factors."""
    n_factors = len(factor_cols)
    overall_mean = df[response_col].mean()

    fig, axes = create_figure(figsize=(3.4 * n_factors, 4.3), nrows=1, ncols=n_factors, sharey=True)
    if n_factors == 1:
        axes = [axes]

    for ax, factor, name in zip(axes, factor_cols, factor_names):
        means = df.groupby(factor, observed=False)[response_col].mean()
        levels = [str(lvl) for lvl in means.index]
        ax.plot(levels, means.values, color=BLUE, marker="o", markersize=6, linewidth=1.5)
        ax.axhline(overall_mean, color=DARK_GRAY, linestyle="--", linewidth=0.9, alpha=0.8)
        ax.set_title(f"Main Effect: {name}", fontsize=9.5, fontweight="bold")
        ax.set_ylabel(f"Mean {response_col}" if ax == axes[0] else "")
        ax.tick_params(axis="x", rotation=15)

    fig.suptitle(title, fontsize=11, fontweight="bold", y=1.02)
    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path)
    return fig

def plot_doe_interaction(df: pd.DataFrame, factor1: str, factor2: str, response_col: str, title=None, output_path=None):
    """Minitab Style Interaction Plot showing non-parallel interaction effects."""
    fig, ax = create_figure(figsize=(7.5, 4.8))
    levels2 = df[factor2].dropna().unique()
    colors = [BLUE, RED, GREEN, GOLD]
    markers = ["o", "s", "^", "D"]

    for idx, lvl2 in enumerate(levels2):
        sub = df[df[factor2] == lvl2]
        means = sub.groupby(factor1, observed=False)[response_col].mean()
        c = colors[idx % len(colors)]
        m = markers[idx % len(markers)]
        ls = "-" if idx == 0 else "--"
        ax.plot([str(k) for k in means.index], means.values, color=c, marker=m, linestyle=ls, linewidth=1.5, markersize=6, label=f"{factor2}: {lvl2}")

    ax.set_title(title or f"Interaction Plot: {factor1} * {factor2} for {response_col}", fontsize=10.5, fontweight="bold", pad=12)
    ax.set_ylabel(f"Mean {response_col}", fontsize=9)
    ax.set_xlabel(factor1, fontsize=9)
    ax.legend(title=factor2, framealpha=0.9)

    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path)
    return fig

def plot_standardized_effects_pareto(effects_dict: dict, alpha=0.05, df_error=8, title="Pareto Chart of the Standardized Effects", response_name="Yield", output_path=None):
    """Minitab Style Pareto Chart of the Standardized Effects for Factorial DOE.
    
    Shows horizontal bars of |t-statistic| for each term, with red dashed line
    at t-critical threshold at given alpha and error degrees of freedom.
    """
    t_crit = scipy_stats.t.ppf(1 - alpha/2, df_error)
    
    sorted_terms = sorted(effects_dict.items(), key=lambda x: abs(x[1]), reverse=True)
    terms = [item[0] for item in sorted_terms]
    values = [abs(item[1]) for item in sorted_terms]
    
    fig, ax = create_figure(figsize=(8.5, 4.8))
    y_pos = np.arange(len(terms))
    
    # Horizontal bars with Minitab blue fill and dark edge
    ax.barh(y_pos, values, color=HIST_FILL, edgecolor=HIST_EDGE, height=0.6, align="center")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(terms, fontsize=9)
    ax.invert_yaxis()
    
    # Reference line for t_crit
    ax.axvline(t_crit, color=RED, linestyle="--", linewidth=1.2)
    ax.text(t_crit, -0.6, f"{t_crit:.3f}", color=RED, ha="center", va="bottom", fontsize=9, fontweight="bold")
    
    ax.set_xlabel("Standardized Effect (|t-value|)", fontsize=9)
    ax.set_ylabel("Term", fontsize=9)
    ax.set_title(f"{title}\n(response is {response_name}, α = {alpha})", fontsize=10.5, fontweight="bold", pad=14)
    
    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path)
    return fig

def plot_multi_vari_chart(df: pd.DataFrame, time_col="Time_Period", piece_col="Piece_ID", value_col="Dimension_mm", title="Multi-Vari Chart", output_path=None):
    """Minitab Style Multi-Vari Chart for nested variation sources."""
    fig, ax = create_figure(figsize=(9.2, 4.8))
    times = df[time_col].unique()
    x_ticks = []
    x_labels = []
    idx = 0.0

    for t_idx, t in enumerate(times):
        sub_t = df[df[time_col] == t]
        pieces = sub_t[piece_col].unique()
        for p in pieces:
            sub_p = sub_t[sub_t[piece_col] == p]
            xs = [idx, idx + 0.25, idx + 0.5]
            ys = sub_p[value_col].values
            ax.plot(xs, ys, marker="o", color=BLUE, linewidth=1.2, markersize=4.5)
            # Group center
            ax.plot([idx + 0.25], [np.mean(ys)], marker="s", color=GREEN, markersize=5.5)
            x_ticks.append(idx + 0.25)
            x_labels.append(str(p))
            idx += 1.0
        if t_idx < len(times) - 1:
            ax.axvline(idx - 0.25, color=DARK_GRAY, linestyle="--", linewidth=0.8, alpha=0.7)

    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels, fontsize=8)
    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=12)
    ax.set_ylabel(value_col, fontsize=9)
    ax.set_xlabel("Sampled Units across Time Categories", fontsize=9)

    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path)
    return fig

def plot_msa_gage_rr_interaction(df: pd.DataFrame, part_col="Part", operator_col="Operator", measurement_col="Measurement", title="Gage R&R: Part * Operator Interaction Plot", output_path=None):
    """Minitab Style Part x Operator interaction plot for Gage R&R."""
    operators = df[operator_col].unique()
    colors = [BLUE, RED, GREEN, GOLD]

    fig, ax = create_figure(figsize=(9, 4.8))
    for idx, op in enumerate(operators):
        sub = df[df[operator_col] == op]
        means = sub.groupby(part_col, observed=False)[measurement_col].mean()
        c = colors[idx % len(colors)]
        ax.plot([str(k) for k in means.index], means.values, marker="o", linewidth=1.2, markersize=5, color=c, label=str(op))

    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=12)
    ax.set_ylabel(f"Average {measurement_col}", fontsize=9)
    ax.set_xlabel(part_col, fontsize=9)
    ax.legend(title=operator_col, framealpha=0.9)

    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path)
    return fig

def plot_attribute_agreement_chart(appraisers: list[str], within_rates: list[float], vs_std_rates: list[float], kappas: list[float], title="Attribute Agreement Analysis (Minitab Style)", output_path=None):
    """Minitab Style Attribute Agreement Analysis Charts: Assessment Agreement (%) & Fleiss/Cohen Kappa."""
    fig, (ax1, ax2) = create_figure(figsize=(9.2, 4.8), nrows=1, ncols=2)
    x = np.arange(len(appraisers))
    w = 0.35

    # 1. Percent Agreement
    ax1.bar(x - w/2, within_rates, width=w, color=BLUE, edgecolor=HIST_EDGE, label="Within Appraiser (%)")
    ax1.bar(x + w/2, vs_std_rates, width=w, color=HIST_FILL, edgecolor=HIST_EDGE, label="vs Standard (%)")
    ax1.axhline(90, color=RED, linestyle="--", linewidth=1.0, label="Target (90%)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(appraisers, fontsize=8.5)
    ax1.set_ylabel("Percent Agreement (%)", fontsize=9)
    ax1.set_ylim(0, 110)
    ax1.set_title("Assessment Agreement (%)", fontsize=10, fontweight="bold", pad=10)
    ax1.legend(loc="lower right", fontsize=7.5)

    for i in range(len(x)):
        ax1.text(x[i] - w/2, within_rates[i] + 1.5, f"{within_rates[i]:.0f}%", ha="center", fontsize=7.5)
        ax1.text(x[i] + w/2, vs_std_rates[i] + 1.5, f"{vs_std_rates[i]:.0f}%", ha="center", fontsize=7.5)

    # 2. Kappa Statistic
    ax2.bar(x, kappas, width=0.45, color=HIST_FILL, edgecolor=HIST_EDGE)
    ax2.axhline(0.75, color=GREEN, linestyle="--", linewidth=1.0, label="Good Agreement (0.75)")
    ax2.axhline(0.40, color=RED, linestyle=":", linewidth=1.0, label="Poor (<0.40)")
    ax2.set_xticks(x)
    ax2.set_xticklabels(appraisers, fontsize=8.5)
    ax2.set_ylabel("Kappa Statistic (K)", fontsize=9)
    ax2.set_ylim(0, 1.05)
    ax2.set_title("Fleiss / Cohen Kappa Statistic", fontsize=10, fontweight="bold", pad=10)
    ax2.legend(loc="lower right", fontsize=7.5)

    for i in range(len(x)):
        ax2.text(x[i], kappas[i] + 0.02, f"{kappas[i]:.3f}", ha="center", fontsize=8, fontweight="bold")

    fig.suptitle(title, fontsize=11, fontweight="bold", y=1.01)
    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path)
    return fig

# -----------------------------------------------------------------------------
# CONTROL PHASE VISUALS (SPC Control Charts XmR)
# -----------------------------------------------------------------------------
def plot_spc_xmr_chart(values, title_x="I-Chart: Individual Measurements", title_mr="MR-Chart: Moving Range", output_path=None):
    """Minitab Style XmR Control Chart pair with UCL, LCL, CL labels on outer margin."""
    values = np.asarray(values, dtype=float)
    n = len(values)
    x = np.arange(1, n + 1)
    
    mean_val = np.mean(values)
    mr = np.abs(np.diff(values))
    mr_bar = np.mean(mr) if len(mr) > 0 else 0
    sigma_within = mr_bar / 1.128

    ucl_x = mean_val + 3 * sigma_within
    lcl_x = mean_val - 3 * sigma_within
    ucl_mr = 3.267 * mr_bar
    lcl_mr = 0.0

    fig, (ax1, ax2) = create_figure(nrows=2, ncols=1, figsize=(9.5, 6.8), sharex=True)

    # 1. Individuals Chart
    ax1.plot(x, values, color=BLUE, marker="o", markersize=3.5, linewidth=0.9)
    ax1.axhline(mean_val, color=GREEN, linewidth=1.1)
    ax1.axhline(ucl_x, color=RED, linewidth=1.1)
    ax1.axhline(lcl_x, color=RED, linewidth=1.1)
    
    # Out of control detection (Rule 1: outside 3 sigma)
    ooc_x = (values > ucl_x) | (values < lcl_x)
    if np.any(ooc_x):
        ax1.plot(x[ooc_x], values[ooc_x], color=RED, marker="s", linestyle="none", markersize=5.5, label="Test 1 Failure")
        ax1.legend(loc="upper left")

    ax1.set_title(title_x, fontsize=10, fontweight="bold", pad=10)
    ax1.set_ylabel("Individual Value", fontsize=8.5)

    # Margin labels for I-Chart
    x_max = n
    lx = x_max + n * 0.02
    ax1.text(lx, ucl_x, f"UCL={ucl_x:.3f}", color=RED, fontsize=8, va="center", clip_on=False)
    ax1.text(lx, mean_val, f"Mean={mean_val:.3f}", color=GREEN, fontsize=8, va="center", clip_on=False)
    ax1.text(lx, lcl_x, f"LCL={lcl_x:.3f}", color=RED, fontsize=8, va="center", clip_on=False)

    # 2. Moving Range Chart
    mr_x = np.arange(2, n + 1)
    ax2.plot(mr_x, mr, color=BLUE, marker="o", markersize=3.5, linewidth=0.9)
    ax2.axhline(mr_bar, color=GREEN, linewidth=1.1)
    ax2.axhline(ucl_mr, color=RED, linewidth=1.1)
    ax2.axhline(lcl_mr, color=RED, linewidth=1.1)

    ooc_mr = (mr > ucl_mr)
    if np.any(ooc_mr):
        ax2.plot(mr_x[ooc_mr], mr[ooc_mr], color=RED, marker="s", linestyle="none", markersize=5.5)

    ax2.set_title(title_mr, fontsize=10, fontweight="bold", pad=10)
    ax2.set_ylabel("Moving Range", fontsize=8.5)
    ax2.set_xlabel("Observation", fontsize=8.5)

    ax2.text(lx, ucl_mr, f"UCL={ucl_mr:.3f}", color=RED, fontsize=8, va="center", clip_on=False)
    ax2.text(lx, mr_bar, f"MR={mr_bar:.3f}", color=GREEN, fontsize=8, va="center", clip_on=False)
    ax2.text(lx, lcl_mr, f"LCL={lcl_mr:.3f}", color=RED, fontsize=8, va="center", clip_on=False)

    fig.tight_layout(rect=[0, 0, 0.88, 1])
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path)
    plt.close(fig)
    return fig

# Table of standard SPC factors for Xbar-R charts (n = 2 to 10)
SPC_XBAR_R_FACTORS = {
    2: {"A2": 1.880, "D3": 0.000, "D4": 3.267, "d2": 1.128},
    3: {"A2": 1.023, "D3": 0.000, "D4": 2.574, "d2": 1.693},
    4: {"A2": 0.729, "D3": 0.000, "D4": 2.282, "d2": 2.059},
    5: {"A2": 0.577, "D3": 0.000, "D4": 2.114, "d2": 2.326},
    6: {"A2": 0.483, "D3": 0.000, "D4": 2.004, "d2": 2.534},
    7: {"A2": 0.419, "D3": 0.076, "D4": 1.924, "d2": 2.704},
    8: {"A2": 0.373, "D3": 0.136, "D4": 1.864, "d2": 2.847},
    9: {"A2": 0.337, "D3": 0.184, "D4": 1.816, "d2": 2.970},
    10: {"A2": 0.308, "D3": 0.223, "D4": 1.777, "d2": 3.078},
}

def plot_spc_xbar_r_chart(data, title_xbar="Xbar Chart of Dimension", title_r="R Chart of Dimension", xlabel="Subgroup", output_path=None):
    """Minitab Style Xbar-R Control Chart for subgrouped continuous measurements."""
    apply_minitab_theme()
    sub = np.asarray(data, dtype=float)
    if sub.ndim == 1:
        raise ValueError("Xbar-R chart requires 2D subgroup data array (k_subgroups, n_samples).")
    k, n = sub.shape

    means = np.mean(sub, axis=1)
    ranges = np.ptp(sub, axis=1)
    xbarbar = float(np.mean(means))
    rbar = float(np.mean(ranges))

    factors = SPC_XBAR_R_FACTORS.get(n, SPC_XBAR_R_FACTORS[5])
    ucl_x = xbarbar + factors["A2"] * rbar
    lcl_x = xbarbar - factors["A2"] * rbar
    ucl_r = factors["D4"] * rbar
    lcl_r = factors["D3"] * rbar

    fig, (ax1, ax2) = create_figure(nrows=2, ncols=1, figsize=(9.5, 6.8), sharex=True)
    x = np.arange(1, k + 1)
    lx = k + k * 0.02

    # 1. Xbar Chart
    ax1.plot(x, means, color=BLUE, marker="o", markersize=3.8, linewidth=0.9, zorder=3)
    ax1.axhline(xbarbar, color=GREEN, linewidth=1.1)
    ax1.axhline(ucl_x, color=RED, linewidth=1.1)
    ax1.axhline(lcl_x, color=RED, linewidth=1.1)

    ooc_x = (means > ucl_x) | (means < lcl_x)
    if np.any(ooc_x):
        ax1.plot(x[ooc_x], means[ooc_x], color=RED, marker="s", linestyle="none", markersize=5.5, label="Test 1 Failure", zorder=4)
        for ox in x[ooc_x]:
            ax1.text(ox, means[ox - 1] + (ucl_x - xbarbar) * 0.08, "1", color=RED, fontsize=8, fontweight="bold", ha="center")
        ax1.legend(loc="upper left", fontsize=8)

    ax1.set_title(title_xbar, fontsize=10, fontweight="bold", pad=10)
    ax1.set_ylabel("Sample Mean", fontsize=8.5)
    ax1.text(lx, ucl_x, f"UCL={ucl_x:.3f}", color=RED, fontsize=8, va="center", clip_on=False)
    ax1.text(lx, xbarbar, f"Xbar={xbarbar:.3f}", color=GREEN, fontsize=8, va="center", clip_on=False)
    ax1.text(lx, lcl_x, f"LCL={lcl_x:.3f}", color=RED, fontsize=8, va="center", clip_on=False)

    # 2. R Chart
    ax2.plot(x, ranges, color=BLUE, marker="o", markersize=3.8, linewidth=0.9, zorder=3)
    ax2.axhline(rbar, color=GREEN, linewidth=1.1)
    ax2.axhline(ucl_r, color=RED, linewidth=1.1)
    ax2.axhline(lcl_r, color=RED, linewidth=1.1)

    ooc_r = (ranges > ucl_r) | (ranges < lcl_r)
    if np.any(ooc_r):
        ax2.plot(x[ooc_r], ranges[ooc_r], color=RED, marker="s", linestyle="none", markersize=5.5, zorder=4)
        for orx in x[ooc_r]:
            ax2.text(orx, ranges[orx - 1] + (ucl_r - rbar) * 0.08, "1", color=RED, fontsize=8, fontweight="bold", ha="center")

    ax2.set_title(title_r, fontsize=10, fontweight="bold", pad=10)
    ax2.set_ylabel("Sample Range", fontsize=8.5)
    ax2.set_xlabel(xlabel, fontsize=8.5)
    ax2.text(lx, ucl_r, f"UCL={ucl_r:.3f}", color=RED, fontsize=8, va="center", clip_on=False)
    ax2.text(lx, rbar, f"R={rbar:.3f}", color=GREEN, fontsize=8, va="center", clip_on=False)
    ax2.text(lx, lcl_r, f"LCL={lcl_r:.3f}", color=RED, fontsize=8, va="center", clip_on=False)

    fig.tight_layout(rect=[0, 0, 0.88, 1])
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path)
    plt.close(fig)
    return fig

def plot_spc_p_chart(defectives, sample_sizes, title="P Chart of Defectives (不合格品率控制图)", xlabel="Sample Number", ylabel="Proportion", output_path=None):
    """Minitab Style P-Chart for fraction nonconforming (supports variable and constant sample sizes)."""
    apply_minitab_theme()
    d = np.asarray(defectives, dtype=float)
    n = np.asarray(sample_sizes, dtype=float)
    if np.isscalar(sample_sizes):
        n = np.full(len(d), sample_sizes, dtype=float)
    k = len(d)
    x = np.arange(1, k + 1)
    p = d / n
    p_bar = float(np.sum(d) / np.sum(n))

    ucl = p_bar + 3 * np.sqrt(p_bar * (1.0 - p_bar) / n)
    lcl = np.maximum(0.0, p_bar - 3 * np.sqrt(p_bar * (1.0 - p_bar) / n))

    fig, ax = create_figure(figsize=(9.2, 4.6))
    ax.plot(x, p, color=BLUE, marker="o", markersize=3.8, linewidth=0.9, zorder=3)
    ax.axhline(p_bar, color=GREEN, linewidth=1.1)

    is_constant_n = np.all(n == n[0])
    if is_constant_n:
        ax.axhline(ucl[0], color=RED, linewidth=1.1)
        ax.axhline(lcl[0], color=RED, linewidth=1.1)
    else:
        ax.step(x, ucl, where="mid", color=RED, linewidth=1.1)
        ax.step(x, lcl, where="mid", color=RED, linewidth=1.1)

    ooc = (p > ucl) | (p < lcl)
    if np.any(ooc):
        ax.plot(x[ooc], p[ooc], color=RED, marker="s", linestyle="none", markersize=5.5, label="Test 1 Failure", zorder=4)
        for ox in x[ooc]:
            ax.text(ox, p[ox - 1] + 0.006, "1", color=RED, fontsize=8, fontweight="bold", ha="center")
        ax.legend(loc="upper left", fontsize=8)

    lx = k + k * 0.02
    ucl_disp = ucl[0] if is_constant_n else np.mean(ucl)
    lcl_disp = lcl[0] if is_constant_n else np.mean(lcl)
    ax.text(lx, ucl_disp, f"UCL={ucl_disp:.4f}", color=RED, fontsize=8, va="center", clip_on=False)
    ax.text(lx, p_bar, f"P={p_bar:.4f}", color=GREEN, fontsize=8, va="center", clip_on=False)
    ax.text(lx, lcl_disp, f"LCL={lcl_disp:.4f}", color=RED, fontsize=8, va="center", clip_on=False)

    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=10)
    ax.set_ylabel(ylabel, fontsize=8.5)
    ax.set_xlabel(xlabel, fontsize=8.5)

    fig.tight_layout(rect=[0, 0, 0.88, 1])
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path)
    plt.close(fig)
    return fig

def plot_spc_np_chart(defectives, sample_size: int, title="NP Chart of Defectives (不合格品数控制图)", xlabel="Sample Number", ylabel="Number Defective", output_path=None):
    """Minitab Style NP-Chart for count of nonconforming items with constant sample size n."""
    apply_minitab_theme()
    d = np.asarray(defectives, dtype=float)
    k = len(d)
    n = float(sample_size)
    x = np.arange(1, k + 1)
    p_bar = float(np.sum(d) / (k * n))
    np_bar = n * p_bar

    ucl = np_bar + 3 * np.sqrt(np_bar * (1.0 - p_bar))
    lcl = max(0.0, np_bar - 3 * np.sqrt(np_bar * (1.0 - p_bar)))

    fig, ax = create_figure(figsize=(9.2, 4.6))
    ax.plot(x, d, color=BLUE, marker="o", markersize=3.8, linewidth=0.9, zorder=3)
    ax.axhline(np_bar, color=GREEN, linewidth=1.1)
    ax.axhline(ucl, color=RED, linewidth=1.1)
    ax.axhline(lcl, color=RED, linewidth=1.1)

    ooc = (d > ucl) | (d < lcl)
    if np.any(ooc):
        ax.plot(x[ooc], d[ooc], color=RED, marker="s", linestyle="none", markersize=5.5, label="Test 1 Failure", zorder=4)
        for ox in x[ooc]:
            ax.text(ox, d[ox - 1] + (ucl - np_bar) * 0.08, "1", color=RED, fontsize=8, fontweight="bold", ha="center")
        ax.legend(loc="upper left", fontsize=8)

    lx = k + k * 0.02
    ax.text(lx, ucl, f"UCL={ucl:.2f}", color=RED, fontsize=8, va="center", clip_on=False)
    ax.text(lx, np_bar, f"NP={np_bar:.2f}", color=GREEN, fontsize=8, va="center", clip_on=False)
    ax.text(lx, lcl, f"LCL={lcl:.2f}", color=RED, fontsize=8, va="center", clip_on=False)

    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=10)
    ax.set_ylabel(ylabel, fontsize=8.5)
    ax.set_xlabel(xlabel, fontsize=8.5)

    fig.tight_layout(rect=[0, 0, 0.88, 1])
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path)
    plt.close(fig)
    return fig

def plot_spc_c_chart(defect_counts, title="C Chart of Defects (缺陷数控制图)", xlabel="Sample Number", ylabel="Defect Count", output_path=None):
    """Minitab Style C-Chart for count of defects on constant inspection unit size."""
    apply_minitab_theme()
    c = np.asarray(defect_counts, dtype=float)
    k = len(c)
    x = np.arange(1, k + 1)
    c_bar = float(np.mean(c))

    ucl = c_bar + 3 * np.sqrt(c_bar)
    lcl = max(0.0, c_bar - 3 * np.sqrt(c_bar))

    fig, ax = create_figure(figsize=(9.2, 4.6))
    ax.plot(x, c, color=BLUE, marker="o", markersize=3.8, linewidth=0.9, zorder=3)
    ax.axhline(c_bar, color=GREEN, linewidth=1.1)
    ax.axhline(ucl, color=RED, linewidth=1.1)
    ax.axhline(lcl, color=RED, linewidth=1.1)

    ooc = (c > ucl) | (c < lcl)
    if np.any(ooc):
        ax.plot(x[ooc], c[ooc], color=RED, marker="s", linestyle="none", markersize=5.5, label="Test 1 Failure", zorder=4)
        for ox in x[ooc]:
            ax.text(ox, c[ox - 1] + (ucl - c_bar) * 0.08, "1", color=RED, fontsize=8, fontweight="bold", ha="center")
        ax.legend(loc="upper left", fontsize=8)

    lx = k + k * 0.02
    ax.text(lx, ucl, f"UCL={ucl:.2f}", color=RED, fontsize=8, va="center", clip_on=False)
    ax.text(lx, c_bar, f"C={c_bar:.2f}", color=GREEN, fontsize=8, va="center", clip_on=False)
    ax.text(lx, lcl, f"LCL={lcl:.2f}", color=RED, fontsize=8, va="center", clip_on=False)

    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=10)
    ax.set_ylabel(ylabel, fontsize=8.5)
    ax.set_xlabel(xlabel, fontsize=8.5)

    fig.tight_layout(rect=[0, 0, 0.88, 1])
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path)
    plt.close(fig)
    return fig

def plot_spc_u_chart(defect_counts, units_inspected, title="U Chart of Defects per Unit (单位缺陷数控制图)", xlabel="Sample Number", ylabel="Defects per Unit", output_path=None):
    """Minitab Style U-Chart for defect rates per inspection unit (supports variable units)."""
    apply_minitab_theme()
    c = np.asarray(defect_counts, dtype=float)
    n = np.asarray(units_inspected, dtype=float)
    if np.isscalar(units_inspected):
        n = np.full(len(c), units_inspected, dtype=float)
    k = len(c)
    x = np.arange(1, k + 1)
    u = c / n
    u_bar = float(np.sum(c) / np.sum(n))

    ucl = u_bar + 3 * np.sqrt(u_bar / n)
    lcl = np.maximum(0.0, u_bar - 3 * np.sqrt(u_bar / n))

    fig, ax = create_figure(figsize=(9.2, 4.6))
    ax.plot(x, u, color=BLUE, marker="o", markersize=3.8, linewidth=0.9, zorder=3)
    ax.axhline(u_bar, color=GREEN, linewidth=1.1)

    is_constant_n = np.all(n == n[0])
    if is_constant_n:
        ax.axhline(ucl[0], color=RED, linewidth=1.1)
        ax.axhline(lcl[0], color=RED, linewidth=1.1)
    else:
        ax.step(x, ucl, where="mid", color=RED, linewidth=1.1)
        ax.step(x, lcl, where="mid", color=RED, linewidth=1.1)

    ooc = (u > ucl) | (u < lcl)
    if np.any(ooc):
        ax.plot(x[ooc], u[ooc], color=RED, marker="s", linestyle="none", markersize=5.5, label="Test 1 Failure", zorder=4)
        for ox in x[ooc]:
            ax.text(ox, u[ox - 1] + 0.15, "1", color=RED, fontsize=8, fontweight="bold", ha="center")
        ax.legend(loc="upper left", fontsize=8)

    lx = k + k * 0.02
    ucl_disp = ucl[0] if is_constant_n else np.mean(ucl)
    lcl_disp = lcl[0] if is_constant_n else np.mean(lcl)
    ax.text(lx, ucl_disp, f"UCL={ucl_disp:.3f}", color=RED, fontsize=8, va="center", clip_on=False)
    ax.text(lx, u_bar, f"U={u_bar:.3f}", color=GREEN, fontsize=8, va="center", clip_on=False)
    ax.text(lx, lcl_disp, f"LCL={lcl_disp:.3f}", color=RED, fontsize=8, va="center", clip_on=False)

    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=10)
    ax.set_ylabel(ylabel, fontsize=8.5)
    ax.set_xlabel(xlabel, fontsize=8.5)

    fig.tight_layout(rect=[0, 0, 0.88, 1])
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path)
    plt.close(fig)
    return fig

# -----------------------------------------------------------------------------
# MINITAB STYLE DATA TABLE CARD VISUAL (Similar to _render_table_figure)
# -----------------------------------------------------------------------------
def render_table_card(table_data, title=None, footer_lines: list[str] = None, output_path=None, figsize=None, col_widths=None, max_width=10.0):
    """Render a DataFrame or multiple DataFrames as a compact, Minitab-style data table card (PNG).
    
    Features:
    - Auto-adaptive column widths: Columns scale proportionally with actual cell contents
    - Tight vertical layout: No excessive blank spaces between titles, table, and footers
    - Frame: #e0e0e0 outer border, #f4f4f4 bold header, #d0d0d0 clean cell borders
    
    table_data can be:
    - A single pd.DataFrame
    - A list of (title_str, pd.DataFrame) tuples
    - A list of dicts: [{'title': str, 'df': DataFrame or 'columns': list, 'rows': list}]
    """
    tables = []
    if isinstance(table_data, pd.DataFrame):
        t_title = title or "Data Table"
        cols = [str(c) for c in table_data.columns]
        rows = [[str(val) for val in row] for row in table_data.values]
        tables.append((t_title, cols, rows, table_data))
    elif isinstance(table_data, list):
        for item in table_data:
            if isinstance(item, tuple) and len(item) == 2:
                t_title, df = item
                cols = [str(c) for c in df.columns]
                rows = [[str(val) for val in row] for row in df.values]
                tables.append((t_title, cols, rows, df))
            elif isinstance(item, dict):
                t_title = item.get("title", "Table")
                df = item.get("df")
                if df is not None:
                    cols = [str(c) for c in df.columns]
                    rows = [[str(val) for val in row] for row in df.values]
                else:
                    cols = [str(c) for c in item.get("columns", [])]
                    rows = [[str(val) for val in r] for r in item.get("rows", [])]
                    df = pd.DataFrame(rows, columns=cols)
                tables.append((t_title, cols, rows, df))
            elif isinstance(item, pd.DataFrame):
                t_title = title or "Data Table"
                cols = [str(c) for c in item.columns]
                rows = [[str(val) for val in row] for row in item.values]
                tables.append((t_title, cols, rows, item))

    if not tables:
        return None

    n_tables = len(tables)
    max_char_count = 0
    all_col_widths = []
    for _, cols, rows, _ in tables:
        lens = []
        for c in cols:
            vals = [str(c)] + [str(r[cols.index(c)]) for r in rows]
            m_l = max(sum(1.7 if ord(ch) > 127 else 1.0 for ch in s) for s in vals)
            lens.append(m_l + 3.0)
        tot_l = sum(lens)
        if tot_l > max_char_count:
            max_char_count = tot_l
        all_col_widths.append([l / tot_l for l in lens])

    if figsize is None:
        fig_w = max(5.6, min(max_width, max_char_count * 0.115 + 0.8))
        row_height = 0.28
        title_height = 0.38
        footer_height = 0.32 if footer_lines else 0.05
        padding = 0.35
        table_heights = [len(rows) * row_height + 0.32 for _, _, rows, _ in tables]
        total_h = sum(table_heights) + n_tables * title_height + footer_height + padding
        fig_h = max(1.8, total_h)
        figsize = (fig_w, fig_h)
    else:
        fig_w, fig_h = figsize
        table_heights = [len(rows) * 0.28 + 0.32 for _, _, rows, _ in tables]

    fig = plt.figure(figsize=figsize, dpi=150)
    fig.patch.set_facecolor(FRAME)

    curr_top = (fig_h - 0.20) / fig_h
    title_height = 0.38
    for idx, ((t_title, cols, rows, _), auto_w, t_h) in enumerate(zip(tables, all_col_widths, table_heights)):
        w_use = col_widths if (col_widths is not None and len(col_widths) == len(cols)) else auto_w
        
        # Title
        fig.text(0.04, curr_top, t_title, fontsize=10, fontweight="bold", color="#1f77b4", va="top", ha="left")
        curr_top -= (title_height / fig_h)

        # Axes for table
        ax_h_ratio = t_h / fig_h
        ax = fig.add_axes([0.04, curr_top - ax_h_ratio, 0.92, ax_h_ratio])
        ax.axis("off")

        mpl_table = ax.table(
            cellText=rows,
            colLabels=cols,
            loc="upper center",
            cellLoc="left",
            colLoc="left",
            colWidths=w_use,
            bbox=[0, 0, 1, 1]
        )
        mpl_table.auto_set_font_size(False)
        mpl_table.set_fontsize(8.5)

        for (r_idx, c_idx), cell in mpl_table.get_celld().items():
            cell.set_edgecolor("#d0d0d0")
            cell.set_linewidth(0.6)
            if r_idx == 0:
                cell.set_text_props(weight="bold", color="#111111")
                cell.set_facecolor("#f4f4f4")
            else:
                cell.set_text_props(color="#222222")
                cell.set_facecolor("white")

        curr_top -= (ax_h_ratio + 0.15 / fig_h)

    if footer_lines:
        footer_text = "\n".join(footer_lines)
        fig.text(0.04, 0.08, footer_text, fontsize=8.2, style="italic", color="#333333", va="bottom", ha="left")

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return fig

# -----------------------------------------------------------------------------
# EXTENDED MINITAB STATISTICAL PLOTTING TOOLKIT
# (Histogram, Boxplot, Dotplot, Interval Plot, Residuals 4-in-1, Fitted Line with PI, Chi-Square, CLT)
# -----------------------------------------------------------------------------
def plot_histogram(values, title="Histogram of Data (with Normal Fit)", xlabel="Value", ylabel="Density", bins=14, output_path=None):
    """Minitab Style Histogram with Normal Fit curve & parameter sidebar box."""
    vals = np.asarray(values, dtype=float)
    vals = vals[~np.isnan(vals)]
    mean_v = np.mean(vals)
    std_v = np.std(vals, ddof=1)
    n = len(vals)

    fig, ax = create_figure(figsize=(8.0, 4.8))
    counts, bin_edges, _ = ax.hist(vals, bins=bins, color=HIST_FILL, edgecolor=HIST_EDGE, linewidth=0.8, density=True)
    xs = np.linspace(vals.min() - 0.2 * std_v, vals.max() + 0.2 * std_v, 150)
    ax.plot(xs, scipy_stats.norm.pdf(xs, mean_v, std_v), color=RED, linewidth=1.4, label="Normal Fit")

    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.grid(True, axis="y", linestyle=":", color=GRID, alpha=0.7)

    stats_text = f"Mean:  {mean_v:.4f}\nStDev: {std_v:.4f}\nN:     {n}"
    ax.text(0.96, 0.94, stats_text, transform=ax.transAxes, fontsize=8.5, family="monospace",
            va="top", ha="right", bbox=dict(boxstyle="square,pad=0.5", facecolor="white", edgecolor=DARK_GRAY, linewidth=0.8))

    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return fig

def plot_single_boxplot(values, label="Data", title="Boxplot of Data (Minitab Style)", ylabel="Value", output_path=None):
    """Minitab Style Single-Variable Boxplot with mean circle-cross and 5-number summary."""
    vals = np.asarray(values, dtype=float)
    vals = vals[~np.isnan(vals)]
    mean_v = np.mean(vals)
    median_v = np.median(vals)
    q1 = np.percentile(vals, 25)
    q3 = np.percentile(vals, 75)
    n = len(vals)

    fig, ax = create_figure(figsize=(6.2, 5.0))
    bp = ax.boxplot(
        [vals],
        tick_labels=[label],
        patch_artist=True,
        widths=0.35,
        boxprops=dict(facecolor=HIST_FILL, edgecolor="#333333", linewidth=0.9),
        medianprops=dict(color=RED, linewidth=1.3),
        whiskerprops=dict(color="#333333", linewidth=0.9),
        capprops=dict(color="#333333", linewidth=0.9),
        flierprops=dict(marker="*", color="#333333", markersize=6, linestyle="none")
    )

    # Mean marker circle with cross
    ax.plot(1, mean_v, marker="o", markerfacecolor="none", markeredgecolor="#111111", markersize=7.0, zorder=5)
    ax.plot(1, mean_v, marker="+", color="#111111", markersize=6.5, zorder=6)

    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=12)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.grid(True, axis="y", linestyle=":", color=GRID, alpha=0.7)

    summary_text = f"N:      {n}\nMean:   {mean_v:.3f}\nQ1:     {q1:.3f}\nMedian: {median_v:.3f}\nQ3:     {q3:.3f}\nIQR:    {q3-q1:.3f}"
    ax.text(0.95, 0.94, summary_text, transform=ax.transAxes, fontsize=8.5, family="monospace",
            va="top", ha="right", bbox=dict(boxstyle="square,pad=0.5", facecolor="white", edgecolor=DARK_GRAY, linewidth=0.8))

    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return fig

def calc_anderson_darling(data):
    """Calculate Anderson-Darling statistic A^2 and Stephens (1974) adjusted p-value."""
    x = np.sort(np.asarray(data, dtype=float))
    x = x[~np.isnan(x)]
    n = len(x)
    mean = np.mean(x)
    s = np.std(x, ddof=1)
    if s == 0 or n < 4:
        return 0.0, 1.0
    z = (x - mean) / s
    p = scipy_stats.norm.cdf(z)
    p = np.clip(p, 1e-15, 1.0 - 1e-15)
    i = np.arange(1, n + 1)
    s_sum = np.sum((2 * i - 1) * (np.log(p) + np.log(1.0 - p[::-1])))
    a2 = -n - s_sum / n
    a2_mod = a2 * (1.0 + 0.75 / n + 2.25 / (n**2))
    if a2_mod >= 0.60:
        pval = np.exp(1.2937 - 5.709 * a2_mod + 0.0186 * (a2_mod**2))
    elif a2_mod > 0.34:
        pval = np.exp(0.9177 - 4.279 * a2_mod - 1.38 * (a2_mod**2))
    elif a2_mod > 0.20:
        pval = 1.0 - np.exp(-8.318 + 42.796 * a2_mod - 59.938 * (a2_mod**2))
    else:
        pval = 1.0 - np.exp(-13.436 + 101.14 * a2_mod - 223.73 * (a2_mod**2))
    return float(a2), float(np.clip(pval, 0.0, 1.0))

def plot_graphical_summary(data, var_name="Data", title=None, output_path=None):
    """Minitab Graphical Summary Report (Summary Report for Data):
    Features:
    - Histogram with fitted normal curve
    - Horizontal boxplot
    - 95% Confidence Intervals for Mean & Median
    - Right sidebar: Anderson-Darling test, Skewness, Kurtosis, 5-Number summary, 95% CIs
    """
    vals = np.asarray(data, dtype=float)
    vals = vals[~np.isnan(vals)]
    n = len(vals)
    if n < 3:
        raise ValueError("At least 3 valid observations required for Graphical Summary Report.")

    mean_v = float(np.mean(vals))
    std_v = float(np.std(vals, ddof=1))
    var_v = float(np.var(vals, ddof=1))
    skew_v = float(scipy_stats.skew(vals, bias=False))
    kurt_v = float(scipy_stats.kurtosis(vals, bias=False))
    min_v = float(np.min(vals))
    q1_v = float(np.percentile(vals, 25))
    med_v = float(np.median(vals))
    q3_v = float(np.percentile(vals, 75))
    max_v = float(np.max(vals))

    a2_stat, p_val = calc_anderson_darling(vals)

    # 95% CI for Mean (t distribution)
    t_crit = scipy_stats.t.ppf(0.975, n - 1)
    mean_ci = (mean_v - t_crit * std_v / np.sqrt(n), mean_v + t_crit * std_v / np.sqrt(n))

    # 95% CI for Median (binomial rank order statistics)
    k_binom = scipy_stats.binom.ppf(0.025, n, 0.5)
    sorted_vals = np.sort(vals)
    k1 = int(max(0, min(n - 1, np.floor(k_binom))))
    k2 = int(max(0, min(n - 1, n - 1 - k1)))
    med_ci = (float(sorted_vals[k1]), float(sorted_vals[k2]))

    # 95% CI for StDev (Chi-square distribution)
    chi2_lo = scipy_stats.chi2.ppf(0.025, n - 1)
    chi2_hi = scipy_stats.chi2.ppf(0.975, n - 1)
    std_ci = (float(np.sqrt((n - 1) * std_v**2 / chi2_hi)), float(np.sqrt((n - 1) * std_v**2 / chi2_lo)))

    # Create figure (Minitab clean layout)
    fig = plt.figure(figsize=(9.2, 6.2), dpi=150)
    fig.patch.set_facecolor("white")

    if title is None:
        title = f"Summary Report for {var_name}"
    fig.suptitle(title, fontsize=13.5, fontweight="bold", y=0.965, color="#111111")

    # Grid: Left 64% subplots, Right 36% statistics sidebar
    gs_main = gridspec.GridSpec(1, 2, width_ratios=[1.75, 1.0], left=0.08, right=0.96, bottom=0.08, top=0.90, wspace=0.18)
    gs_left = gridspec.GridSpecFromSubplotSpec(3, 1, subplot_spec=gs_main[0], height_ratios=[3.3, 0.95, 1.25], hspace=0.35)

    # 1. Top Subplot: Histogram with Normal Fit
    ax_hist = fig.add_subplot(gs_left[0])
    ax_hist.set_facecolor("white")
    counts, bin_edges, _ = ax_hist.hist(vals, bins="auto", color="#7ba2d5", edgecolor="#333333", linewidth=0.8, density=True)
    xs = np.linspace(vals.min() - 0.5 * std_v, vals.max() + 0.5 * std_v, 200)
    ax_hist.plot(xs, scipy_stats.norm.pdf(xs, mean_v, std_v), color="#8b0000", linewidth=1.4)
    ax_hist.grid(True, linestyle=":", color="#e4e4e4", alpha=0.9)
    ax_hist.tick_params(labelsize=8.5)
    for spine in ax_hist.spines.values():
        spine.set_color("#666666")

    # 2. Middle Subplot: Horizontal Boxplot (matching X-axis with histogram)
    ax_box = fig.add_subplot(gs_left[1], sharex=ax_hist)
    ax_box.set_facecolor("white")
    bp = ax_box.boxplot(
        [vals],
        orientation="horizontal",
        widths=0.55,
        patch_artist=True,
        boxprops=dict(facecolor="#7ba2d5", edgecolor="#333333", linewidth=0.8),
        medianprops=dict(color="#333333", linewidth=1.2),
        whiskerprops=dict(color="#333333", linewidth=0.8),
        capprops=dict(color="#333333", linewidth=0.8),
        flierprops=dict(marker="*", color="#333333", markersize=6, linestyle="none")
    )
    ax_box.set_yticks([])
    ax_box.grid(True, linestyle=":", color="#e4e4e4", alpha=0.9)
    for spine in ax_box.spines.values():
        spine.set_color("#666666")

    # 3. Bottom Subplot: 95% Confidence Intervals for Mean and Median
    ax_ci = fig.add_subplot(gs_left[2])
    ax_ci.set_facecolor("white")
    ax_ci.set_title("95% Confidence Intervals", fontsize=9.5, fontweight="bold", pad=4, color="#111111")

    ax_ci.errorbar([mean_v], [1], xerr=[[mean_v - mean_ci[0]], [mean_ci[1] - mean_v]],
                   fmt="o", color="#004b97", ecolor="#004b97", elinewidth=1.2, capsize=4.5, capthick=1.2, markersize=5)
    ax_ci.errorbar([med_v], [0], xerr=[[med_v - med_ci[0]], [med_ci[1] - med_v]],
                   fmt="o", color="#004b97", ecolor="#004b97", elinewidth=1.2, capsize=4.5, capthick=1.2, markersize=5)

    ax_ci.set_yticks([0, 1])
    ax_ci.set_yticklabels(["Median", "Mean"], fontsize=8.5)
    ax_ci.set_ylim(-0.6, 1.6)
    ax_ci.grid(True, linestyle=":", color="#e4e4e4", alpha=0.9)
    ax_ci.tick_params(labelsize=8.5)
    for spine in ax_ci.spines.values():
        spine.set_color("#666666")

    # Right Sidebar: Full Minitab Statistics
    ax_text = fig.add_subplot(gs_main[1])
    ax_text.set_facecolor("white")
    ax_text.axis("off")

    text_content = [
        ("Anderson-Darling Normality Test", ""),
        ("  A-Squared", f"{a2_stat:.2f}"),
        ("  P-Value", f"{p_val:.3f}"),
        ("", ""),
        ("Mean", f"{mean_v:.4f}"),
        ("StDev", f"{std_v:.4f}"),
        ("Variance", f"{var_v:.4f}"),
        ("Skewness", f"{skew_v:.6f}"),
        ("Kurtosis", f"{kurt_v:.6f}"),
        ("N", f"{n}"),
        ("", ""),
        ("Minimum", f"{min_v:.4f}"),
        ("1st Quartile", f"{q1_v:.4f}"),
        ("Median", f"{med_v:.4f}"),
        ("3rd Quartile", f"{q3_v:.4f}"),
        ("Maximum", f"{max_v:.4f}"),
        ("", ""),
        ("95% Confidence Interval for Mean", ""),
        (f"  {mean_ci[0]:.4f}", f"{mean_ci[1]:.4f}"),
        ("95% Confidence Interval for Median", ""),
        (f"  {med_ci[0]:.4f}", f"{med_ci[1]:.4f}"),
        ("95% Confidence Interval for StDev", ""),
        (f"  {std_ci[0]:.4f}", f"{std_ci[1]:.4f}")
    ]

    y_pos = 0.985
    for label, val in text_content:
        if not label and not val:
            y_pos -= 0.022
            continue
        if val == "":
            ax_text.text(0.02, y_pos, label, fontsize=8.8, fontweight="bold", color="#111111", va="top")
        else:
            ax_text.text(0.04, y_pos, label, fontsize=8.2, color="#222222", va="top")
            ax_text.text(0.96, y_pos, val, fontsize=8.2, family="monospace", color="#111111", va="top", ha="right")
        y_pos -= 0.038

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    return fig

def plot_multi_column_boxplot(data_dict, title="Boxplot of Multiple Columns (Minitab Style)", ylabel="Measurement", output_path=None):
    """Minitab Style Multiple Columns Boxplot: side-by-side boxes on same X axis with mean lines & markers."""
    labels = list(data_dict.keys())
    data_list = [np.asarray(data_dict[k], dtype=float)[~np.isnan(data_dict[k])] for k in labels]
    
    fig, ax = create_figure(figsize=(7.8, 5.0))
    bp = ax.boxplot(
        data_list,
        tick_labels=labels,
        patch_artist=True,
        widths=0.4,
        boxprops=dict(facecolor=HIST_FILL, edgecolor="#333333", linewidth=0.9),
        medianprops=dict(color=RED, linewidth=1.3),
        whiskerprops=dict(color="#333333", linewidth=0.9),
        capprops=dict(color="#333333", linewidth=0.9),
        flierprops=dict(marker="*", color="#333333", markersize=6, linestyle="none")
    )

    means = [np.mean(d) for d in data_list]
    for i, m in enumerate(means, start=1):
        ax.plot(i, m, marker="o", markerfacecolor="none", markeredgecolor="#111111", markersize=7.0, zorder=5)
        ax.plot(i, m, marker="+", color="#111111", markersize=6.5, zorder=6)
    
    # 均值连线 (Minitab 连接各组均值)
    if len(means) > 1:
        ax.plot(range(1, len(means) + 1), means, linestyle="--", color="#555555", linewidth=1.0, alpha=0.8, zorder=4)

    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=12)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.grid(True, axis="y", linestyle=":", color=GRID, alpha=0.7)

    # 统计信息窗格 (右上角)
    lines = ["Column Stats:"]
    for k, d in zip(labels, data_list):
        lines.append(f"{k[:10]:<10}: Mean={np.mean(d):.2f}, s={np.std(d, ddof=1):.2f}")
    ax.text(0.96, 0.95, "\n".join(lines), transform=ax.transAxes, fontsize=8.0, family="monospace",
            va="top", ha="right", bbox=dict(boxstyle="square,pad=0.5", facecolor="white", edgecolor=DARK_GRAY, linewidth=0.8))

    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return fig

def plot_multi_column_histogram_paneled(data_dict, title="Paneled Histogram of Multiple Columns (Same Scale)", xlabel="Measurement", output_path=None):
    """Minitab Style Paneled Histogram: vertically stacked subplots sharing identical X-scale with normal curves."""
    labels = list(data_dict.keys())
    data_list = [np.asarray(data_dict[k], dtype=float)[~np.isnan(data_dict[k])] for k in labels]
    k = len(labels)

    all_vals = np.concatenate(data_list)
    x_min, x_max = all_vals.min(), all_vals.max()
    margin = (x_max - x_min) * 0.1
    xlim = (x_min - margin, x_max + margin)

    fig, axes = plt.subplots(k, 1, figsize=(8.0, 2.5 * k), dpi=150, sharex=True)
    fig.patch.set_facecolor("#e0e0e0")
    if k == 1:
        axes = [axes]

    colors = [HIST_FILL, "#a1d99b", "#fcae91", "#bcbddc"]
    for idx, (ax, label, d) in enumerate(zip(axes, labels, data_list)):
        ax.set_facecolor("white")
        mean_v = np.mean(d)
        std_v = np.std(d, ddof=1)
        n = len(d)
        
        c = colors[idx % len(colors)]
        counts, bins, _ = ax.hist(d, bins=12, color=c, edgecolor="#333333", linewidth=0.8, density=True)
        xs = np.linspace(xlim[0], xlim[1], 150)
        ax.plot(xs, scipy_stats.norm.pdf(xs, mean_v, std_v), color=RED, linewidth=1.3)
        ax.axvline(mean_v, color=RED, linestyle="--", linewidth=1.0, alpha=0.7)

        ax.set_xlim(xlim)
        ax.set_ylabel(f"{label}\nDensity", fontsize=8.5)
        ax.grid(True, axis="y", linestyle=":", color=GRID, alpha=0.7)

        stats_box = f"{label}\nMean:  {mean_v:.3f}\nStDev: {std_v:.3f}\nN:     {n}"
        ax.text(0.96, 0.90, stats_box, transform=ax.transAxes, fontsize=8.0, family="monospace",
                va="top", ha="right", bbox=dict(boxstyle="square,pad=0.4", facecolor="white", edgecolor=DARK_GRAY, linewidth=0.7))

    axes[0].set_title(title, fontsize=10.5, fontweight="bold", pad=10)
    axes[-1].set_xlabel(xlabel, fontsize=9)

    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return fig

def plot_multi_column_histogram_overlay(data_dict, title="Overlay Histogram of Multiple Columns (with Normal Fits)", xlabel="Measurement", output_path=None):
    """Minitab Style Overlay Histogram: multiple columns semi-transparently overlaid on single axes."""
    labels = list(data_dict.keys())
    data_list = [np.asarray(data_dict[k], dtype=float)[~np.isnan(data_dict[k])] for k in labels]

    fig, ax = create_figure(figsize=(8.0, 4.8))
    colors = [("#4c72b0", HIST_FILL), ("#2ca02c", "#98df8a"), ("#d62728", "#ff9896"), ("#756bb1", "#bcbddc")]
    all_vals = np.concatenate(data_list)
    xs = np.linspace(all_vals.min() - 0.5, all_vals.max() + 0.5, 200)

    for idx, (label, d) in enumerate(zip(labels, data_list)):
        edge_c, fill_c = colors[idx % len(colors)]
        mean_v = np.mean(d)
        std_v = np.std(d, ddof=1)
        ax.hist(d, bins=12, color=fill_c, edgecolor=edge_c, linewidth=0.9, alpha=0.55, density=True, label=f"{label} (Mean={mean_v:.2f})")
        ax.plot(xs, scipy_stats.norm.pdf(xs, mean_v, std_v), color=edge_c, linewidth=1.5)

    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel("Density", fontsize=9)
    ax.legend(loc="upper right", fontsize=8.5, framealpha=0.9, edgecolor=DARK_GRAY)
    ax.grid(True, axis="y", linestyle=":", color=GRID, alpha=0.7)

    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return fig

def plot_dotplot(values, title="Dotplot of Data", xlabel="Value", output_path=None, bins=35):
    """Minitab Style Dotplot: values binned and stacked vertically as dots."""
    vals = np.asarray(values, dtype=float)
    vals = vals[~np.isnan(vals)]
    
    counts, bin_edges = np.histogram(vals, bins=bins)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    fig, ax = create_figure(figsize=(8.5, 4.0))
    
    for center, count in zip(bin_centers, counts):
        if count > 0:
            ys = np.arange(1, count + 1)
            ax.scatter([center] * count, ys, color=BLUE, s=36, edgecolors="white", linewidths=0.5, zorder=3)
            
    ax.set_ylim(0, max(counts) + 2)
    ax.set_yticks([])
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=12)
    
    mean_v = np.mean(vals)
    s_v = np.std(vals, ddof=1)
    ax.text(0.82, 0.92, f"N = {len(vals)}\nMean = {mean_v:.3f}\nStDev = {s_v:.3f}",
            transform=ax.transAxes, fontsize=8, family="monospace", va="top",
            bbox=dict(boxstyle="square,pad=0.5", facecolor="white", edgecolor=DARK_GRAY, linewidth=0.8))
            
    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path)
    return fig

def plot_interval_plot(centers, lows, highs, labels, title="Interval Plot (95% CI for the Mean)", xlabel="Mean Dimension (mm)", ylabel="Machine", orientation="horizontal", output_path=None):
    """Minitab Style Interval Plot with 95% Confidence Intervals for Means.
    
    Supports:
    - orientation='horizontal' (default in Minitab when aligning with Means table):
      Y-axis = Groups/Categories, X-axis = Value/Mean with horizontal error bars
    - orientation='vertical':
      X-axis = Groups/Categories, Y-axis = Value/Mean with vertical error bars
    """
    centers = np.asarray(centers, dtype=float)
    lows = np.asarray(lows, dtype=float)
    highs = np.asarray(highs, dtype=float)
    grand_mean = np.mean(centers)
    
    fig, ax = create_figure(figsize=(8.5, 4.8))
    
    if orientation == "horizontal":
        y_pos = np.arange(len(centers))
        cap_h = 0.12
        for yi, lo, hi in zip(y_pos, lows, highs):
            ax.hlines(yi, lo, hi, color=BLUE, linewidth=1.5, zorder=2)
            ax.plot([lo, lo], [yi - cap_h, yi + cap_h], color=BLUE, linewidth=1.2, zorder=2)
            ax.plot([hi, hi], [yi - cap_h, yi + cap_h], color=BLUE, linewidth=1.2, zorder=2)
            
        ax.scatter(centers, y_pos, color=BLUE, s=42, edgecolors="white", linewidths=0.6, zorder=3)
        ax.axvline(grand_mean, color=DARK_GRAY, linestyle="--", linewidth=0.9, alpha=0.7)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels([str(l) for l in labels], fontsize=8.5)
        ax.invert_yaxis()
        ax.set_xlabel(xlabel, fontsize=9)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.grid(True, axis="x", linestyle=":", color=GRID, alpha=0.7)
    else:
        x_pos = np.arange(len(centers))
        cap_w = 0.12
        for xi, lo, hi in zip(x_pos, lows, highs):
            ax.plot([xi, xi], [lo, hi], color=BLUE, linewidth=1.5, zorder=2)
            ax.plot([xi - cap_w, xi + cap_w], [lo, lo], color=BLUE, linewidth=1.2, zorder=2)
            ax.plot([xi - cap_w, xi + cap_w], [hi, hi], color=BLUE, linewidth=1.2, zorder=2)
            
        ax.scatter(x_pos, centers, color=BLUE, s=42, edgecolors="white", linewidths=0.6, zorder=3)
        ax.axhline(grand_mean, color=DARK_GRAY, linestyle="--", linewidth=0.9, alpha=0.7)
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels([str(l) for l in labels], fontsize=8.5)
        ax.set_xlabel(ylabel, fontsize=9)
        ax.set_ylabel(xlabel, fontsize=9)
        ax.grid(True, axis="y", linestyle=":", color=GRID, alpha=0.7)
        
    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=12)
    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path)
    return fig

def plot_residuals_4in1(residuals, fitted_vals, title="Residual Plots (4 in 1)", output_path=None):
    """Minitab Style 4-in-1 Residual Diagnostic Plots for Regression and ANOVA."""
    resid = np.asarray(residuals, dtype=float)
    fits = np.asarray(fitted_vals, dtype=float)
    n = len(resid)
    
    fig, axes = create_figure(nrows=2, ncols=2, figsize=(9.6, 7.2))
    ax1, ax2 = axes[0, 0], axes[0, 1]
    ax3, ax4 = axes[1, 0], axes[1, 1]
    
    # 1. Normal Probability Plot of Residuals
    (osm, osr), (slope, intercept, _) = scipy_stats.probplot(resid, dist="norm")
    ax1.scatter(osm, osr, color=BLUE, s=20, edgecolors="white", linewidths=0.4, zorder=3)
    xs = np.linspace(osm.min(), osm.max(), 100)
    ax1.plot(xs, slope * xs + intercept, color=RED, linewidth=1.2)
    ax1.set_title("Normal Probability Plot", fontsize=9.5, fontweight="bold")
    ax1.set_xlabel("Theoretical Quantiles", fontsize=8.5)
    ax1.set_ylabel("Residual", fontsize=8.5)
    
    # 2. Versus Fits (Residuals vs Fitted Values)
    ax2.scatter(fits, resid, color=BLUE, s=20, edgecolors="white", linewidths=0.4, zorder=3)
    ax2.axhline(0.0, color=RED, linestyle="--", linewidth=1.1)
    ax2.set_title("Versus Fits", fontsize=9.5, fontweight="bold")
    ax2.set_xlabel("Fitted Value", fontsize=8.5)
    ax2.set_ylabel("Residual", fontsize=8.5)
    
    # 3. Histogram of Residuals
    ax3.hist(resid, bins=12, color=HIST_FILL, edgecolor=HIST_EDGE, linewidth=0.8)
    ax3.set_title("Histogram", fontsize=9.5, fontweight="bold")
    ax3.set_xlabel("Residual", fontsize=8.5)
    ax3.set_ylabel("Frequency", fontsize=8.5)
    
    # 4. Versus Order (Residuals vs Observation Order)
    order_x = np.arange(1, n + 1)
    ax4.plot(order_x, resid, color=BLUE, marker="o", markersize=3.5, linewidth=0.9, zorder=3)
    ax4.axhline(0.0, color=RED, linestyle="--", linewidth=1.1)
    ax4.set_title("Versus Order", fontsize=9.5, fontweight="bold")
    ax4.set_xlabel("Observation Order", fontsize=8.5)
    ax4.set_ylabel("Residual", fontsize=8.5)
    
    fig.suptitle(title, fontsize=11, fontweight="bold", y=1.01)
    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path)
    return fig

def plot_fitted_line_with_pi(x, y, xlabel="X", ylabel="Y", title="Fitted Line Plot with 95% CI & PI", output_path=None):
    """Minitab Style Fitted Line Plot with both 95% Confidence Interval (CI) and Prediction Interval (PI)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    slope, intercept, r_val, p_val, std_err = scipy_stats.linregress(x, y)
    r2 = r_val ** 2
    
    fig, ax = create_figure(figsize=(8.8, 5.2))
    ax.scatter(x, y, color=BLUE, s=26, edgecolors="white", linewidths=0.5, alpha=0.85, label="Data")
    
    xs = np.linspace(x.min(), x.max(), 150)
    ys = slope * xs + intercept
    ax.plot(xs, ys, color=RED, linewidth=1.4, label=f"Fit: Y = {intercept:.2f} + {slope:.3f}*X")
    
    residuals = y - (slope * x + intercept)
    s_err = np.sqrt(np.sum(residuals**2) / (n - 2))
    t_val = scipy_stats.t.ppf(0.975, df=n - 2)
    x_mean = np.mean(x)
    sum_xx = np.sum((x - x_mean)**2)
    
    ci = t_val * s_err * np.sqrt(1/n + (xs - x_mean)**2 / sum_xx)
    ax.plot(xs, ys + ci, color=RED, linestyle="--", linewidth=0.9, label="95% CI")
    ax.plot(xs, ys - ci, color=RED, linestyle="--", linewidth=0.9)
    
    pi = t_val * s_err * np.sqrt(1 + 1/n + (xs - x_mean)**2 / sum_xx)
    ax.plot(xs, ys + pi, color=GREEN, linestyle=":", linewidth=1.1, label="95% PI")
    ax.plot(xs, ys - pi, color=GREEN, linestyle=":", linewidth=1.1)
    
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=12)
    
    summary_text = (
        f"S = {s_err:.4f}\n"
        f"R-sq = {r2*100:.1f}%\n"
        f"R-sq(adj) = {(1 - (1-r2)*(n-1)/(n-2))*100:.1f}%\n"
        f"p-val = {p_val:.4f}"
    )
    ax.text(0.04, 0.95, summary_text, transform=ax.transAxes, verticalalignment="top",
            fontsize=8.5, family="monospace", bbox=dict(boxstyle="square,pad=0.5", facecolor="white", edgecolor=DARK_GRAY, linewidth=0.8))
            
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path)
    return fig

def plot_contingency_bar_chart(crosstab_df: pd.DataFrame, title="Chi-Square Contingency Bar Chart", xlabel="Category", ylabel="Count", output_path=None):
    """Minitab Style Grouped Bar Chart for Chi-Square Contingency Analysis."""
    fig, ax = create_figure(figsize=(8.5, 4.8))
    categories = crosstab_df.index
    sub_groups = crosstab_df.columns
    n_groups = len(sub_groups)
    
    x = np.arange(len(categories))
    width = 0.7 / n_groups
    colors = [BLUE, HIST_FILL, GOLD, GREEN, GRAY, RED]
    
    for idx, col in enumerate(sub_groups):
        offset = (idx - (n_groups - 1) / 2) * width
        vals = crosstab_df[col].values
        ax.bar(x + offset, vals, width=width, color=colors[idx % len(colors)], edgecolor=HIST_EDGE, linewidth=0.8, label=str(col))
        for xi, v in zip(x + offset, vals):
            ax.text(xi, v + 0.3, str(v), ha="center", va="bottom", fontsize=7.5)
            
    ax.set_xticks(x)
    ax.set_xticklabels([str(c) for c in categories], fontsize=8.5)
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=12)
    ax.legend(title="Classification", framealpha=0.9, fontsize=8)
    
    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path)
    return fig

def plot_clt_simulation(sample_means_n5, sample_means_n30, population_data=None, title="Central Limit Theorem Demonstration", output_path=None):
    """Demonstrate Central Limit Theorem: Population distribution vs Sample size N=5 and N=30 means."""
    fig, axes = create_figure(nrows=1, ncols=3, figsize=(10.5, 4.0), sharey=False)
    
    if population_data is not None:
        axes[0].hist(population_data, bins=20, color=GRAY, edgecolor=DARK_GRAY, density=True)
        axes[0].set_title("Population (Skewed)", fontsize=9.5, fontweight="bold")
    else:
        pop = np.random.exponential(scale=2.0, size=2000)
        axes[0].hist(pop, bins=20, color=GRAY, edgecolor=DARK_GRAY, density=True)
        axes[0].set_title("Population (Exponential)", fontsize=9.5, fontweight="bold")
    axes[0].set_yticks([])
    axes[0].set_xlabel("X")
    
    axes[1].hist(sample_means_n5, bins=18, color=HIST_FILL, edgecolor=HIST_EDGE, density=True)
    m5, s5 = np.mean(sample_means_n5), np.std(sample_means_n5, ddof=1)
    xs5 = np.linspace(sample_means_n5.min(), sample_means_n5.max(), 100)
    axes[1].plot(xs5, scipy_stats.norm.pdf(xs5, m5, s5), color=RED, linewidth=1.3)
    axes[1].set_title("Sample Means (N=5)", fontsize=9.5, fontweight="bold")
    axes[1].set_yticks([])
    axes[1].set_xlabel("Sample Mean")
    
    axes[2].hist(sample_means_n30, bins=18, color=BLUE, edgecolor=HIST_EDGE, density=True)
    m30, s30 = np.mean(sample_means_n30), np.std(sample_means_n30, ddof=1)
    xs30 = np.linspace(sample_means_n30.min(), sample_means_n30.max(), 100)
    axes[2].plot(xs30, scipy_stats.norm.pdf(xs30, m30, s30), color=RED, linewidth=1.3)
    axes[2].set_title("Sample Means (N=30, Normal)", fontsize=9.5, fontweight="bold")
    axes[2].set_yticks([])
    axes[2].set_xlabel("Sample Mean")
    
    fig.suptitle(title, fontsize=11, fontweight="bold", y=1.02)
    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path)
    return fig

def plot_root_cause_validation_report(df: pd.DataFrame, factor_col="Operator", response_col="Accuracy_Pct", title_main="ROOT CAUSE 1-ACCURACY- STATISTICAL ANALYSIS", subtitle="ROOT CAUSE VALIDATION: OPERATOR", output_path=None):
    """Minitab Style Composite Root Cause Statistical Validation Report.
    
    Layout matches standard Six Sigma Executive Validation slide:
    - Top banner & subtitle
    - Box 1: Analysis of Variance (DF, SS, MS, F, P)
    - Box 2: Means with 95% CI & Pooled StDev
    - Box 3: Factor Information
    - Box 4: Boxplot of Response by Factor with mean-connect lines & outliers
    - Bottom Left: Statistical Conclusion statement
    - Bottom Right: P-value badge with checkmark
    """
    import matplotlib.patches as patches
    
    groups = list(df[factor_col].dropna().unique())
    box_data = [df[df[factor_col] == g][response_col].dropna().values for g in groups]
    ns = [len(d) for d in box_data]
    means = [np.mean(d) for d in box_data]
    stdevs = [np.std(d, ddof=1) for d in box_data]
    
    k = len(groups)
    total_n = sum(ns)
    df_factor = k - 1
    df_error = total_n - k
    
    grand_mean = df[response_col].mean()
    ss_factor = sum(n * (m - grand_mean)**2 for n, m in zip(ns, means))
    ss_error = sum(sum((x - m)**2 for x in d) for d, m in zip(box_data, means))
    ss_total = ss_factor + ss_error
    
    ms_factor = ss_factor / df_factor if df_factor > 0 else 0
    ms_error = ss_error / df_error if df_error > 0 else 0
    f_val = ms_factor / ms_error if ms_error > 0 else 0
    p_val = 1 - scipy_stats.f.cdf(f_val, df_factor, df_error) if ms_error > 0 else 1.0
    
    pooled_s = np.sqrt(ms_error)
    t_crit = scipy_stats.t.ppf(0.975, df_error)
    
    cis = []
    for m, n in zip(means, ns):
        margin = t_crit * pooled_s / np.sqrt(n)
        cis.append(f"({m - margin:.3f}, {m + margin:.3f})")
        
    fig = plt.figure(figsize=(11.5, 7.8), dpi=150)
    fig.patch.set_facecolor("white")

    # 1. Header Banner
    fig.text(0.5, 0.965, title_main, fontsize=16, fontweight="bold", ha="center", va="top", color="#111111")
    line_ax = fig.add_axes([0.04, 0.932, 0.92, 0.003])
    line_ax.set_facecolor("#1a5276")
    line_ax.axis("off")
    fig.text(0.04, 0.915, subtitle, fontsize=13, fontweight="bold", ha="left", va="top", color="#111111")

    # 2. Box 1: ANOVA Table
    ax1 = fig.add_axes([0.04, 0.63, 0.35, 0.26])
    rect1 = patches.Rectangle((0, 0), 1, 1, transform=ax1.transAxes, linewidth=0.9, edgecolor="#333333", facecolor="white", zorder=0)
    ax1.add_patch(rect1)
    ax1.text(0.03, 0.88, "Analysis of Variance", color="#1f77b4", fontsize=10.5, fontweight="bold", transform=ax1.transAxes)

    headers1 = ["Source", "DF", "Adj SS", "Adj MS", "F-Value", "P-Value"]
    data1 = [
        [str(factor_col), str(df_factor), f"{ss_factor:.2f}", f"{ms_factor:.3f}", f"{f_val:.2f}", f"{p_val:.3f}"],
        ["Error", str(df_error), f"{ss_error:.2f}", f"{ms_error:.3f}", "", ""],
        ["Total", str(total_n - 1), f"{ss_total:.2f}", "", "", ""]
    ]
    t1 = ax1.table(cellText=data1, colLabels=headers1, loc="center", cellLoc="left", colLoc="left",
                   bbox=[0.02, 0.04, 0.96, 0.72])
    t1.auto_set_font_size(False)
    t1.set_fontsize(7.5)
    for (r, c), cell in t1.get_celld().items():
        cell.set_edgecolor("none")
        if r == 0:
            cell.set_text_props(weight="bold")
    ax1.axis("off")

    # 3. Box 2: Means Table
    ax2 = fig.add_axes([0.04, 0.17, 0.35, 0.44])
    rect2 = patches.Rectangle((0, 0), 1, 1, transform=ax2.transAxes, linewidth=0.9, edgecolor="#333333", facecolor="white", zorder=0)
    ax2.add_patch(rect2)
    ax2.text(0.03, 0.92, "Means", color="#1f77b4", fontsize=10.5, fontweight="bold", transform=ax2.transAxes)

    headers2 = [str(factor_col), "N", "Mean", "StDev", "95% CI"]
    data2 = [
        [str(g), str(n), f"{m:.3f}", f"{s:.3f}", ci_str]
        for g, n, m, s, ci_str in zip(groups, ns, means, stdevs, cis)
    ]
    t2 = ax2.table(cellText=data2, colLabels=headers2, loc="center", cellLoc="left", colLoc="left",
                   colWidths=[0.19, 0.08, 0.17, 0.14, 0.38], bbox=[0.02, 0.10, 0.95, 0.74])
    t2.auto_set_font_size(False)
    t2.set_fontsize(7.0)
    for (r, c), cell in t2.get_celld().items():
        cell.set_edgecolor("none")
        if r == 0:
            cell.set_text_props(weight="bold")

    ax2.text(0.04, 0.04, f"Pooled StDev = {pooled_s:.5f}", style="italic", fontsize=7.5, color="#333333", transform=ax2.transAxes)
    ax2.axis("off")

    # 4. Box 3: Factor Information
    ax3 = fig.add_axes([0.43, 0.76, 0.53, 0.13])
    rect3 = patches.Rectangle((0, 0), 1, 1, transform=ax3.transAxes, linewidth=0.9, edgecolor="#333333", facecolor="white", zorder=0)
    ax3.add_patch(rect3)
    ax3.text(0.02, 0.74, "Factor Information", color="#1f77b4", fontsize=10.5, fontweight="bold", transform=ax3.transAxes)

    headers3 = ["Factor", "Levels", "Values"]
    val_str = ". ".join(str(g) for g in groups)
    data3 = [[str(factor_col), str(k), val_str]]
    t3 = ax3.table(cellText=data3, colLabels=headers3, loc="center", cellLoc="left", colLoc="left",
                   bbox=[0.02, 0.10, 0.96, 0.50])
    t3.auto_set_font_size(False)
    t3.set_fontsize(8.0)
    for (r, c), cell in t3.get_celld().items():
        cell.set_edgecolor("none")
        if r == 0:
            cell.set_text_props(weight="bold")
    ax3.axis("off")

    # 5. Box 4: Boxplot of Response by Factor
    ax4 = fig.add_axes([0.43, 0.17, 0.53, 0.53])
    rect4 = patches.Rectangle((0, 0), 1, 1, transform=ax4.transAxes, linewidth=0.9, edgecolor="#333333", facecolor="white", zorder=0)
    ax4.add_patch(rect4)
    ax4.set_facecolor("white")

    bp = ax4.boxplot(
        box_data,
        tick_labels=[str(g) for g in groups],
        patch_artist=True,
        boxprops=dict(facecolor="#729ece", edgecolor="#333333", linewidth=0.8),
        medianprops=dict(color="#2c3e50", linewidth=1.1),
        whiskerprops=dict(color="#333333", linewidth=0.8),
        capprops=dict(color="#333333", linewidth=0.8),
        flierprops=dict(marker="*", color="#333333", markersize=6, linestyle="none")
    )

    x_indices = np.arange(1, len(groups) + 1)
    ax4.plot(x_indices, means, color="#666666", linestyle="-", linewidth=0.9, zorder=4)
    for xi, mi in zip(x_indices, means):
        ax4.plot(xi, mi, marker="o", markerfacecolor="none", markeredgecolor="#444444", markersize=6.5, zorder=5)
        ax4.plot(xi, mi, marker="+", color="#444444", markersize=6.0, zorder=6)

    ax4.set_title(f"Boxplot of {response_col}", fontsize=10, fontweight="bold", pad=10)
    ax4.set_xlabel(str(factor_col), fontsize=8.5)
    ax4.set_ylabel(str(response_col), fontsize=8.5)
    ax4.grid(True, linestyle=":", color="#e0e0e0", alpha=0.8)

    # 6. Bottom Conclusion & P-value badge
    verdict = "significantly impacts" if p_val < 0.05 else "does not significantly impact"
    conclusion_text = (
        f"Conclusion: With a P-value of {p_val:.3f} (< 0.05 at 95% confidence level), we can\\n"
        f"validate {factor_col} as a critical root cause factor because there is statistical\\n"
        f"evidence that {factor_col} {verdict} {response_col}."
    )
    fig.text(0.04, 0.09, conclusion_text, fontsize=9.2, color="#111111", ha="left", va="top")

    # P-value box on right
    ax_b = fig.add_axes([0.77, 0.02, 0.19, 0.11])
    ax_b.axis("off")
    rect_b = patches.Rectangle((0, 0), 1, 1, transform=ax_b.transAxes, linewidth=0.8, edgecolor="#777777", facecolor="white")
    ax_b.add_patch(rect_b)
    ax_b.text(0.5, 0.84, f"P-value = {p_val:.3f}", fontsize=11, fontweight="bold", ha="center", va="top", color="#111111")

    chk_x = [0.22, 0.45, 0.82]
    chk_y = [0.44, 0.22, 0.64]
    ax_b.plot(chk_x, chk_y, color="#d62728", linewidth=4.2, solid_capstyle="round")

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return fig

# -----------------------------------------------------------------------------
# COMPLETE MINITAB "GRAPH" MENU SUITE
# (Scatterplot, Matrix Plot, Bubble Plot, Marginal Plot, Stem-and-Leaf,
#  Probability Plot, Empirical CDF, Probability Distribution Plot,
#  Individual Value Plot, Line Plot)
# -----------------------------------------------------------------------------
def plot_scatterplot(x, y, title="Scatterplot of Y vs X", xlabel="X", ylabel="Y", fit_line=True, output_path=None):
    """Minitab Style Scatterplot: with optional linear regression fit, S, and R-Sq box."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = ~(np.isnan(x) | np.isnan(y))
    x, y = x[mask], y[mask]

    fig, ax = create_figure(figsize=(7.5, 4.8))
    ax.scatter(x, y, color=BLUE, edgecolors="white", s=35, linewidths=0.5, zorder=3)

    if fit_line and len(x) >= 3:
        slope, intercept, r, p, stderr = scipy_stats.linregress(x, y)
        xs = np.linspace(x.min(), x.max(), 100)
        ax.plot(xs, slope * xs + intercept, color=RED, linewidth=1.3, zorder=4)
        r2 = r**2 * 100
        s_err = np.sqrt(np.sum((y - (slope * x + intercept))**2) / (len(x) - 2))
        stats_text = f"Y = {intercept:.3f} + {slope:.3f}*X\nS = {s_err:.3f}\nR-Sq = {r2:.1f}%"
        ax.text(0.96, 0.94, stats_text, transform=ax.transAxes, fontsize=8.5, family="monospace",
                va="top", ha="right", bbox=dict(boxstyle="square,pad=0.5", facecolor="white", edgecolor=DARK_GRAY, linewidth=0.8))

    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=10)
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.grid(True, linestyle=":", color=GRID, alpha=0.7)

    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return fig

def plot_matrix_plot(df: pd.DataFrame, columns: list[str] = None, title="Matrix Plot of Variables", output_path=None):
    """Minitab Style Matrix Plot: pairwise scatterplot matrix with diagonal variable histograms."""
    if columns is None:
        columns = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])][:5]
    cols = list(columns)
    k = len(cols)
    if k < 2:
        raise ValueError("Matrix plot requires at least 2 numerical columns.")

    fig, axes = plt.subplots(k, k, figsize=(2.4 * k, 2.4 * k), dpi=150)
    fig.patch.set_facecolor(FRAME)
    if k == 1:
        axes = np.array([[axes]])

    for i in range(k):
        for j in range(k):
            ax = axes[i, j]
            ax.set_facecolor(AXES_BG)
            if i == j:
                # Diagonal: Histogram and variable name
                v = df[cols[i]].dropna()
                ax.hist(v, color=HIST_FILL, edgecolor=HIST_EDGE, linewidth=0.6, density=True)
                ax.text(0.5, 0.85, cols[i], transform=ax.transAxes, ha="center", va="center",
                        fontsize=8.5, fontweight="bold", color="#111111")
                ax.set_yticks([])
            else:
                ax.scatter(df[cols[j]], df[cols[i]], color=BLUE, alpha=0.65, edgecolors="white", s=16, linewidths=0.3)
            ax.tick_params(labelsize=7)
            ax.grid(True, linestyle=":", color=GRID, alpha=0.6)
            for spine in ax.spines.values():
                spine.set_color(DARK_GRAY)

    fig.suptitle(title, fontsize=11, fontweight="bold", y=0.985)
    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return fig

def plot_bubble_plot(x, y, size, title="Bubble Plot of Y vs X", xlabel="X", ylabel="Y", size_label="Size", output_path=None):
    """Minitab Style Bubble Plot: scatter plot with points sized proportionally to a 3rd variable."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    size = np.asarray(size, dtype=float)
    mask = ~(np.isnan(x) | np.isnan(y) | np.isnan(size))
    x, y, size = x[mask], y[mask], size[mask]

    fig, ax = create_figure(figsize=(7.5, 4.8))
    s_norm = 40 + (size - size.min()) / (size.max() - size.min() + 1e-9) * 260
    ax.scatter(x, y, s=s_norm, color=HIST_FILL, edgecolors=HIST_EDGE, linewidths=1.0, alpha=0.65, zorder=3)

    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=10)
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.grid(True, linestyle=":", color=GRID, alpha=0.7)

    # Reference legend
    for sz_val, label_str in [(size.min(), f"Min ({size.min():.1f})"), (np.median(size), f"Med ({np.median(size):.1f})"), (size.max(), f"Max ({size.max():.1f})")]:
        s_sz = 40 + (sz_val - size.min()) / (size.max() - size.min() + 1e-9) * 260
        ax.scatter([], [], s=s_sz, color=HIST_FILL, edgecolors=HIST_EDGE, alpha=0.65, label=label_str)
    ax.legend(title=size_label, loc="upper right", fontsize=8, framealpha=0.9, edgecolor=DARK_GRAY)

    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return fig

def plot_marginal_plot(x, y, title="Marginal Plot of Y vs X", xlabel="X", ylabel="Y", marginal_type="histogram", output_path=None):
    """Minitab Style Marginal Plot: central scatterplot surrounded by marginal histograms or boxplots on top and right."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = ~(np.isnan(x) | np.isnan(y))
    x, y = x[mask], y[mask]

    fig = plt.figure(figsize=(7.5, 6.0), dpi=150)
    fig.patch.set_facecolor(FRAME)
    gs = gridspec.GridSpec(2, 2, width_ratios=[4, 1], height_ratios=[1, 4], hspace=0.08, wspace=0.08)
    
    ax_top = fig.add_subplot(gs[0, 0])
    ax_main = fig.add_subplot(gs[1, 0])
    ax_right = fig.add_subplot(gs[1, 1])

    for a in [ax_top, ax_main, ax_right]:
        a.set_facecolor(AXES_BG)
        for spine in a.spines.values():
            spine.set_color(DARK_GRAY)

    # Main scatter
    ax_main.scatter(x, y, color=BLUE, edgecolors="white", s=28, linewidths=0.4, zorder=3)
    ax_main.grid(True, linestyle=":", color=GRID, alpha=0.7)
    ax_main.set_xlabel(xlabel, fontsize=9)
    ax_main.set_ylabel(ylabel, fontsize=9)

    # Marginals
    if marginal_type == "boxplot":
        ax_top.boxplot([x], orientation="horizontal", patch_artist=True,
                       boxprops=dict(facecolor=HIST_FILL, edgecolor=DARK_GRAY), widths=0.6)
        ax_right.boxplot([y], orientation="vertical", patch_artist=True,
                        boxprops=dict(facecolor=HIST_FILL, edgecolor=DARK_GRAY), widths=0.6)
    else:
        ax_top.hist(x, bins=15, color=HIST_FILL, edgecolor=HIST_EDGE, linewidth=0.6)
        ax_right.hist(y, bins=15, orientation="horizontal", color=HIST_FILL, edgecolor=HIST_EDGE, linewidth=0.6)

    ax_top.set_xlim(ax_main.get_xlim())
    ax_right.set_ylim(ax_main.get_ylim())
    ax_top.set_xticks([])
    ax_top.set_yticks([])
    ax_right.set_xticks([])
    ax_right.set_yticks([])

    fig.suptitle(title, fontsize=10.5, fontweight="bold", y=0.985)
    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return fig

def plot_stem_and_leaf(values, var_name="Data", leaf_unit=None, output_path=None):
    """Minitab Style Stem-and-Leaf Card: Depth (cumulative frequency), Stem, and Leaves with header."""
    vals = np.asarray(values, dtype=float)
    vals = vals[~np.isnan(vals)]
    n = len(vals)
    if n == 0:
        raise ValueError("Stem-and-leaf requires at least 1 observation.")

    # Determine scale
    vals_int = np.round(vals * 10).astype(int)
    stems = vals_int // 10
    leaves = vals_int % 10
    
    unique_stems = sorted(list(set(stems)))
    stem_leaves = {}
    for s in unique_stems:
        stem_leaves[s] = sorted(list(leaves[stems == s]))
    
    counts = [len(stem_leaves[s]) for s in unique_stems]
    cum_up = np.cumsum(counts)
    cum_down = np.cumsum(counts[::-1])[::-1]
    med_idx = np.where(cum_up >= (n + 1) / 2)[0][0]
    
    unit_str = "0.1" if leaf_unit is None else str(leaf_unit)
    lines = [f"Stem-and-Leaf Display: {var_name}", f"Stem-and-leaf of {var_name}  N = {n}", f"Leaf Unit = {unit_str}", ""]
    lines.append(f"{'Depth':>5}  {'Stem':>4}  {'Leaves'}")
    lines.append("-" * 46)
    
    for i, s in enumerate(unique_stems):
        l_str = " ".join(str(x) for x in stem_leaves[s])
        if i < med_idx:
            depth_str = str(cum_up[i])
        elif i == med_idx:
            depth_str = f"({counts[i]})"
        else:
            depth_str = str(cum_down[i])
        lines.append(f"{depth_str:>5}  {s:>4}  {l_str}")
    
    fig, ax = create_figure(figsize=(6.8, 4.6))
    ax.axis("off")
    ax.text(0.04, 0.94, "\n".join(lines), family="monospace", fontsize=8.5, va="top", ha="left",
            bbox=dict(boxstyle="square,pad=0.8", facecolor="white", edgecolor=DARK_GRAY, linewidth=0.8))
    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return fig

def plot_probability_plot(values, title="Probability Plot of Data", xlabel="Observation", output_path=None):
    """Minitab Style Probability Plot (Normal): nonlinear probability paper percent scale with 95% CI bands & AD test."""
    vals = np.sort(np.asarray(values, dtype=float))
    vals = vals[~np.isnan(vals)]
    n = len(vals)
    if n < 3:
        raise ValueError("Probability plot requires at least 3 observations.")

    mean_v = float(np.mean(vals))
    std_v = float(np.std(vals, ddof=1))
    
    # Minitab plotting position: (i - 0.375) / (n + 0.25)
    i = np.arange(1, n + 1)
    p = (i - 0.375) / (n + 0.25)
    z_obs = scipy_stats.norm.ppf(p)
    
    fig, ax = create_figure(figsize=(7.8, 5.0))
    ax.scatter(vals, z_obs, color=BLUE, edgecolors="white", s=28, linewidths=0.4, zorder=3)
    
    # Linear fit line
    xs = np.linspace(vals.min() - 0.3 * std_v, vals.max() + 0.3 * std_v, 150)
    zs = (xs - mean_v) / std_v
    ax.plot(xs, zs, color=RED, linewidth=1.3, zorder=4)
    
    # 95% Confidence Band
    se = (1.0 / scipy_stats.norm.pdf(zs)) * np.sqrt(scipy_stats.norm.cdf(zs) * (1 - scipy_stats.norm.cdf(zs)) / n)
    ax.plot(xs, zs + 1.96 * se, color=RED, linestyle="--", linewidth=0.9, alpha=0.7)
    ax.plot(xs, zs - 1.96 * se, color=RED, linestyle="--", linewidth=0.9, alpha=0.7)
    
    p_ticks = np.array([0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99])
    z_ticks = scipy_stats.norm.ppf(p_ticks)
    ax.set_yticks(z_ticks)
    ax.set_yticklabels([f"{pt * 100:g}" for pt in p_ticks], fontsize=8)
    ax.set_ylim(scipy_stats.norm.ppf(0.005), scipy_stats.norm.ppf(0.995))
    ax.set_ylabel("Percent", fontsize=9)
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=10)
    ax.grid(True, linestyle=":", color=GRID, alpha=0.7)
    
    ad_stat, p_val = calc_anderson_darling(vals)
    stats_text = f"Mean:    {mean_v:.4f}\nStDev:   {std_v:.4f}\nN:       {n}\nAD:      {ad_stat:.3f}\nP-Value: {p_val:.3f}"
    ax.text(0.96, 0.06, stats_text, transform=ax.transAxes, fontsize=8.0, family="monospace", va="bottom", ha="right",
            bbox=dict(boxstyle="square,pad=0.5", facecolor="white", edgecolor=DARK_GRAY, linewidth=0.8))

    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return fig

def plot_empirical_cdf(values, title="Empirical CDF of Data", xlabel="Observation", ylabel="Cumulative Probability", output_path=None):
    """Minitab Style Empirical CDF Plot: step curve overlaid with fitted continuous normal CDF."""
    vals = np.sort(np.asarray(values, dtype=float))
    vals = vals[~np.isnan(vals)]
    n = len(vals)
    y = np.arange(1, n + 1) / n

    fig, ax = create_figure(figsize=(7.5, 4.8))
    ax.step(vals, y, where="post", color=BLUE, linewidth=1.4, label="Empirical CDF")
    
    mean_v, std_v = np.mean(vals), np.std(vals, ddof=1)
    xs = np.linspace(vals.min() - 0.2 * std_v, vals.max() + 0.2 * std_v, 200)
    ax.plot(xs, scipy_stats.norm.cdf(xs, mean_v, std_v), color=RED, linestyle="--", linewidth=1.2, label=f"Normal (Mean={mean_v:.2f}, s={std_v:.2f})")
    
    ax.set_ylim(-0.02, 1.05)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=10)
    ax.legend(loc="lower right", fontsize=8.5, framealpha=0.9, edgecolor=DARK_GRAY)
    ax.grid(True, linestyle=":", color=GRID, alpha=0.7)

    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return fig

def plot_probability_distribution_plot(dist="norm", params=(50.0, 0.4), shade_type="two_tailed", alpha=0.05, title="Distribution Plot", xlabel="Value", output_path=None):
    """Minitab Style Probability Distribution Plot: bell curve with shaded alpha rejection region & critical cutoffs."""
    mu, sigma = params
    xs = np.linspace(mu - 3.8 * sigma, mu + 3.8 * sigma, 300)
    ys = scipy_stats.norm.pdf(xs, mu, sigma)

    fig, ax = create_figure(figsize=(7.8, 4.5))
    ax.plot(xs, ys, color=BLUE, linewidth=1.4)

    z_crit = scipy_stats.norm.ppf(1 - alpha / 2)
    x_lo, x_hi = mu - z_crit * sigma, mu + z_crit * sigma

    if shade_type == "two_tailed":
        ax.fill_between(xs[xs <= x_lo], ys[xs <= x_lo], color="#ff9896", alpha=0.6)
        ax.fill_between(xs[xs >= x_hi], ys[xs >= x_hi], color="#ff9896", alpha=0.6)
        ax.axvline(x_lo, color=RED, linestyle="--", linewidth=1.0)
        ax.axvline(x_hi, color=RED, linestyle="--", linewidth=1.0)
        ax.text(x_lo, scipy_stats.norm.pdf(x_lo, mu, sigma) * 1.1, f"{x_lo:.3f}\n(α/2={alpha/2})", ha="right", fontsize=8, color=RED)
        ax.text(x_hi, scipy_stats.norm.pdf(x_hi, mu, sigma) * 1.1, f"{x_hi:.3f}\n(α/2={alpha/2})", ha="left", fontsize=8, color=RED)
    elif shade_type == "upper":
        x_cut = mu + scipy_stats.norm.ppf(1 - alpha) * sigma
        ax.fill_between(xs[xs >= x_cut], ys[xs >= x_cut], color="#ff9896", alpha=0.6)
        ax.axvline(x_cut, color=RED, linestyle="--", linewidth=1.0)
        ax.text(x_cut, scipy_stats.norm.pdf(x_cut, mu, sigma) * 1.1, f"{x_cut:.3f}\n(α={alpha})", ha="left", fontsize=8, color=RED)

    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=10)
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel("Density", fontsize=9)
    ax.grid(True, linestyle=":", color=GRID, alpha=0.7)

    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return fig

def plot_individual_value_plot(data_dict: dict, title="Individual Value Plot of Measurements", ylabel="Measurement", output_path=None):
    """Minitab Style Individual Value Plot: jittered individual points by group with mean diamond markers and connecting line."""
    labels = list(data_dict.keys())
    fig, ax = create_figure(figsize=(7.8, 5.0))
    means = []

    for idx, (label, vals) in enumerate(data_dict.items(), start=1):
        v = np.asarray(vals, dtype=float)[~np.isnan(vals)]
        means.append(np.mean(v))
        jitter = np.random.uniform(-0.1, 0.1, size=len(v))
        ax.scatter(idx + jitter, v, color=HIST_FILL, edgecolors=HIST_EDGE, s=30, linewidths=0.6, alpha=0.75, zorder=3)
        ax.plot(idx, np.mean(v), marker="D", color="#004b97", markersize=6.5, zorder=5)

    if len(means) > 1:
        ax.plot(range(1, len(means) + 1), means, linestyle="--", color="#555555", linewidth=1.0, alpha=0.8, zorder=4)

    ax.set_xticks(range(1, len(labels) + 1))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=10)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.grid(True, axis="y", linestyle=":", color=GRID, alpha=0.7)

    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return fig

def plot_line_plot(y, x=None, title="Line Plot of Measurements", xlabel="Observation", ylabel="Measurement", output_path=None):
    """Minitab Style Line Plot: sequential time-series with point markers and mean reference line."""
    y = np.asarray(y, dtype=float)
    if x is None:
        x = np.arange(1, len(y) + 1)
    else:
        x = np.asarray(x)

    fig, ax = create_figure(figsize=(8.0, 4.4))
    ax.plot(x, y, color=BLUE, linewidth=1.3, marker="o", markersize=4.0, markerfacecolor=HIST_FILL, markeredgecolor=BLUE, zorder=3)
    ax.axhline(np.mean(y), color=RED, linestyle="--", linewidth=1.1, label=f"Mean = {np.mean(y):.3f}")

    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return fig

def plot_fishbone_diagram(
    effect_text: str = "Dimension\nVariation\n(尺寸超差)",
    categories: list = None,
    highlight_causes: list = None,
    title: str = "Cause-and-Effect (Fishbone) Diagram - Minitab Style",
    output_path: str = None
):
    """Minitab Style Cause-and-Effect (Fishbone / Ishikawa) Diagram.
    
    Parameters
    ----------
    effect_text : str
        The effect/problem box text (fish head).
    categories : list of dict, optional
        Custom 6M or 5M1E categories. If None, uses standard manufacturing 6M breakdown.
    highlight_causes : list of str, optional
        Key root causes to highlight with a red marker box / text.
    title : str
        Title of the diagram.
    output_path : str, optional
        Path to save the resulting PNG image.
    """
    import matplotlib.patches as patches

    if categories is None:
        top_branches = [
            ("Personnel (人)", 22, 50, [("Training Deficit (培训不足)", 24), ("Operator Fatigue (人员疲劳)", 16), ("Shift Handover (交接班差异)", 8)]),
            ("Machines (机)", 46, 50, [("Spindle Vibration (主轴偏摆)", 24), ("Tool Wear (刀具磨损)", 16), ("Fixture Clamping (工装夹紧)", 8)]),
            ("Materials (料)", 70, 50, [("Hardness Drift (硬度离散)", 22), ("Supplier Batch (批次公差)", 12)])
        ]
        bottom_branches = [
            ("Methods (法)", 22, 50, [("SOP Compliance (规程执行)", -8), ("Coolant Ratio (切削液配比)", -16), ("Feed Rate High (进给量偏高)", -24)]),
            ("Measurement (测)", 46, 50, [("Gage R&R (量具重复性)", -8), ("Calibration Drift (校准漂移)", -16), ("Thermal Bias (测量温差)", -24)]),
            ("Environment (环)", 70, 50, [("Ambient Temp (车间温差)", -12), ("Floor Vibration (地面震动)", -22)])
        ]
    else:
        top_branches = categories[:3]
        bottom_branches = categories[3:]

    if highlight_causes is None:
        highlight_causes = ["Shift Handover (交接班差异)", "Feed Rate High (进给量偏高)"]

    apply_minitab_theme()
    fig, ax = plt.subplots(figsize=(10.5, 6.2), dpi=150)
    fig.patch.set_facecolor(FRAME)
    ax.set_facecolor(AXES_BG)

    ax.set_xlim(0, 105)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Outer white canvas box inside gray margin
    canvas_rect = patches.Rectangle((2, 2), 101, 96, facecolor="white", edgecolor="#999999", linewidth=1.0, zorder=1)
    ax.add_patch(canvas_rect)

    # Main spine: (8, 50) -> (84, 50)
    ax.annotate("", xy=(84, 50), xytext=(8, 50),
                arrowprops=dict(arrowstyle="->", lw=2.4, color="#222222"), zorder=3)

    # Effect box (Head of fish)
    effect_box = patches.FancyBboxPatch((84, 39), 17.5, 22,
                                       boxstyle="square,pad=0.2",
                                       facecolor=HIST_FILL, edgecolor="#222222", linewidth=1.5, zorder=5)
    ax.add_patch(effect_box)
    ax.text(92.75, 50, effect_text, ha="center", va="center",
            fontsize=10.5, fontweight="bold", color="#111111", zorder=6)

    # Draw Top Branches (slanted down-right to spine)
    for cat_name, spine_x, spine_y, subcauses in top_branches:
        top_x = spine_x - 14
        top_y = 86
        ax.annotate("", xy=(spine_x, spine_y), xytext=(top_x, top_y),
                    arrowprops=dict(arrowstyle="->", lw=1.6, color="#333333"), zorder=3)
        cat_box = patches.FancyBboxPatch((top_x - 9.5, top_y - 1.5), 19, 7.5,
                                         boxstyle="square,pad=0.2",
                                         facecolor="#f0f4f8", edgecolor=HIST_EDGE, linewidth=1.1, zorder=4)
        ax.add_patch(cat_box)
        ax.text(top_x, top_y + 2.2, cat_name, ha="center", va="center",
                fontsize=9.0, fontweight="bold", color="#111111", zorder=5)

        for cause_text, y_offset in subcauses:
            bone_y = spine_y + y_offset
            t = (bone_y - spine_y) / (top_y - spine_y)
            branch_pt_x = spine_x + t * (top_x - spine_x)
            bone_start_x = branch_pt_x - 14
            is_hl = any(hc in cause_text for hc in highlight_causes)
            bone_color = RED if is_hl else "#555555"
            ax.plot([bone_start_x, branch_pt_x], [bone_y, bone_y], color=bone_color, lw=1.2 if is_hl else 1.0, zorder=3)
            txt_color = RED if is_hl else "#222222"
            ax.text(bone_start_x + 0.3, bone_y + 1.1, cause_text, fontsize=7.6,
                    fontweight="bold" if is_hl else "normal", color=txt_color, va="bottom", ha="left", zorder=4)
            if is_hl:
                hl_rect = patches.FancyBboxPatch(
                    (bone_start_x - 0.6, bone_y + 0.1),
                    (branch_pt_x - bone_start_x) + 0.8,
                    3.3,
                    boxstyle="round,pad=0.2",
                    facecolor="#fff0f0",
                    edgecolor=RED,
                    linestyle="--",
                    linewidth=0.9,
                    zorder=3
                )
                ax.add_patch(hl_rect)

    # Draw Bottom Branches (slanted up-right to spine)
    for cat_name, spine_x, spine_y, subcauses in bottom_branches:
        bot_x = spine_x - 14
        bot_y = 14
        ax.annotate("", xy=(spine_x, spine_y), xytext=(bot_x, bot_y),
                    arrowprops=dict(arrowstyle="->", lw=1.6, color="#333333"), zorder=3)
        cat_box = patches.FancyBboxPatch((bot_x - 9.5, bot_y - 6), 19, 7.5,
                                         boxstyle="square,pad=0.2",
                                         facecolor="#f0f4f8", edgecolor=HIST_EDGE, linewidth=1.1, zorder=4)
        ax.add_patch(cat_box)
        ax.text(bot_x, bot_y - 2.2, cat_name, ha="center", va="center",
                fontsize=9.0, fontweight="bold", color="#111111", zorder=5)

        for cause_text, y_offset in subcauses:
            bone_y = spine_y + y_offset
            t = (bone_y - spine_y) / (bot_y - spine_y)
            branch_pt_x = spine_x + t * (bot_x - spine_x)
            bone_start_x = branch_pt_x - 14
            is_hl = any(hc in cause_text for hc in highlight_causes)
            bone_color = RED if is_hl else "#555555"
            ax.plot([bone_start_x, branch_pt_x], [bone_y, bone_y], color=bone_color, lw=1.2 if is_hl else 1.0, zorder=3)
            txt_color = RED if is_hl else "#222222"
            ax.text(bone_start_x + 0.3, bone_y + 1.1, cause_text, fontsize=7.6,
                    fontweight="bold" if is_hl else "normal", color=txt_color, va="bottom", ha="left", zorder=4)
            if is_hl:
                hl_rect = patches.FancyBboxPatch(
                    (bone_start_x - 0.6, bone_y + 0.1),
                    (branch_pt_x - bone_start_x) + 0.8,
                    3.3,
                    boxstyle="round,pad=0.2",
                    facecolor="#fff0f0",
                    edgecolor=RED,
                    linestyle="--",
                    linewidth=0.9,
                    zorder=3
                )
                ax.add_patch(hl_rect)

    # Title
    ax.text(50, 94.5, title, fontsize=12, fontweight="bold", ha="center", va="center", color="#111111", zorder=5)

    fig.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return fig

