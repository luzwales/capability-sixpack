"""Restyle every plotting cell in the course notebooks to the Minitab house style.

Strategy
--------
``minitab_style.apply_style()`` (already injected into each notebook's setup
cell) installs rcParams for the gray figure frame, white plot area, dotted
grid, fonts and legend frame. That covers the *frame* of every chart
automatically, including charts these notebooks build with raw
``plt``/``seaborn`` calls.

What is left is the *palette*: the notebooks hand-picked ``steelblue``,
``coral``, ``Set2``/``Set3`` palettes and ``edgecolor='black'``. This script
rewrites those to the Minitab constants, and upgrades the most common
single-plot patterns into the :mod:`minitab_style` helpers.

Every rewrite is conservative: chart *semantics* (data, bins, limits, fitted
lines, annotations) are never touched, only colours and a few styling calls.

Run from the ``data-six-sigma`` directory::

    python refactor_charts.py [--dry-run] [--notebook GLOB]
"""

from __future__ import annotations

import argparse
import glob
import json
import re
from pathlib import Path

# --------------------------------------------------------------------------
# Palette rewrites
# --------------------------------------------------------------------------
COLOR_SUBS: list[tuple[str, str]] = [
    # histogram / bar fills
    (r"(['\"])steelblue\1", "ms.HIST_FILL"),
    (r"(['\"])cornflowerblue\1", "ms.HIST_FILL"),
    (r"(['\"])lightsteelblue\1", "ms.HIST_FILL"),
    (r"(['\"])skyblue\1", "ms.HIST_FILL"),
    (r"(['\"])dodgerblue\1", "ms.BLUE"),
    # secondary categorical accents -> gold / gray
    (r"(['\"])coral\1", "ms.GOLD"),
    (r"(['\"])darkorange\1", "ms.GOLD"),
    (r"(['\"])orange\1", "ms.GOLD"),
    (r"(['\"])tomato\1", "ms.RED"),
    (r"(['\"])firebrick\1", "ms.RED"),
    (r"(['\"])seagreen\1", "ms.GREEN"),
    # seaborn colorblind-ish sets -> Minitab primary/blue fill
    (r"(['\"])Set2\1", "[ms.BLUE, ms.HIST_FILL, ms.GOLD, ms.GREEN, ms.GRAY]"),
    (r"(['\"])Set3\1", "[ms.HIST_FILL, ms.BLUE, ms.GOLD, ms.GREEN, ms.GRAY]"),
    (r"(['\"])tab10\1", "[ms.BLUE, ms.GOLD, ms.GREEN, ms.RED, ms.HIST_FILL]"),
    (r"(['\"])tab20\1", "[ms.BLUE, ms.HIST_FILL, ms.GOLD, ms.GREEN, ms.GRAY]"),
    (r"(['\"])muted\1", "[ms.BLUE, ms.HIST_FILL, ms.GOLD, ms.GREEN, ms.GRAY]"),
    (r"(['\"])deep\1", "[ms.BLUE, ms.HIST_FILL, ms.GOLD, ms.GREEN, ms.GRAY]"),
    # explicit edge colours
    (r"edgecolor\s*=\s*(['\"])black\1", "edgecolor=ms.HIST_EDGE"),
    (r"edgecolors?\s*=\s*(['\"])black\1", "edgecolor=ms.HIST_EDGE"),
    (r"color\s*=\s*(['\"])black\1", "color=ms.DARK_GRAY"),
    (r"(['\"])black\1(?=\s*,\s*linewidth)", "ms.DARK_GRAY"),
    # line colours expressed as matplotlib shorthand
    (r"(['\"])r--\1", "color=ms.RED, linestyle='--'"),
    (r"(['\"])b--\1", "color=ms.BLUE, linestyle='--'"),
    (r"(['\"])g--\1", "color=ms.GREEN, linestyle='--'"),
    (r"(['\"])ro-\1", "color=ms.RED, marker='o', linestyle='-'"),
    (r"(['\"])r-(\1?)", "color=ms.RED"),  # guarded below
]

# The 'r-' rule is risky (matches substrings); handle it separately and drop it.
COLOR_SUBS = [c for c in COLOR_SUBS if c[0] != r"(['\"])r-(\1?)"]

# ``sns.set_style`` / ``sns.set_theme`` overrides that fight the house style
STYLE_CALLS = [
    (r"^\s*sns\.set_style\([^)]*\)\s*$", ""),
    (r"^\s*sns\.set_theme\([^)]*\)\s*$", ""),
    (r"^\s*plt\.style\.use\([^)]*\)\s*$", ""),
]

# Explicit seaborn colour= arguments that should become Minitab constants.
# NOTE: seaborn's ``palette=`` expects colour *names* (or a seaborn palette
# name), not a Python list, so those are dropped in favour of ``hue=`` +
# ``legend=False``, letting the rcParams color cycle supply the colours.
SEABORN_COLORS = [
    (r"(sns\.(?:bar|boxplot|violinplot)\w*\([^)]*?)color\s*=\s*(['\"])steelblue\2",
     r"\1color=ms.HIST_FILL"),
]

# ``palette=[...]`` (a raw list) is invalid for seaborn: remove the argument.
SEABORN_BAD_PALETTE = re.compile(r",?\s*palette\s*=\s*\[[^\]]*\]")

# ``colormap=[...]`` is invalid too -- pandas needs a registered colormap
# object, which minitab_style provides.
COLORMAP_LIST = re.compile(r"colormap\s*=\s*\[[^\]]*\]")

IS_PLOT = re.compile(
    r"(plt\.(?:hist|plot|scatter|bar|barh|boxplot|pie|step|fill_between|errorbar|"
    r"hlines|vlines|axhline|axvline|subplots|figure)\s*\()"
    r"|(sns\.\w+\s*\()"
    r"|(ax\d?\.set_title\s*\()"
)

# Cells that reference the ``ms`` namespace need the style import to be
# reachable. Normally the setup cell provides it, but a few notebooks have no
# setup cell at all -- inject a minimal bootstrap into the first code cell.
STYLE_BOOTSTRAP = """# --- Minitab-style house style -------------------------------------------
import sys
from pathlib import Path as _Path

# minitab_style.py lives in the parent folder of each module directory
sys.path.append(str(_Path.cwd().parent))
import minitab_style as ms

ms.apply_style()"""


def needs_style_import(nb: dict) -> bool:
    """Does any cell use ``ms.*`` without the setup cell defining it?"""
    has_bootstrap = any(
        cell["cell_type"] == "code" and "import minitab_style" in "".join(cell["source"])
        for cell in nb["cells"]
    )
    if has_bootstrap:
        return False
    return any(
        cell["cell_type"] == "code" and re.search(r"\bms\.", "".join(cell["source"]))
        for cell in nb["cells"]
    )


def has_plotting(source: str) -> bool:
    """Does this cell draw anything? (setup cells are excluded upstream)"""
    if "minitab_style" in source and "ms." in source:
        # already-migrated helper cell, still fine to restyle
        pass
    return bool(IS_PLOT.search(source))


def restyle(source: str) -> str:
    """Apply palette + style-call rewrites to one cell."""
    out = source

    for pattern, repl in SEABORN_COLORS:
        out = re.sub(pattern, repl, out, flags=re.DOTALL)

    # A raw list is not a valid seaborn palette; drop it and let the rcParams
    # color cycle (set by ms.apply_style) colour the categories.
    out = SEABORN_BAD_PALETTE.sub("", out)
    out = COLORMAP_LIST.sub("colormap=ms.minitab_cmap()", out)

    for pattern, repl in COLOR_SUBS:
        out = re.sub(pattern, repl, out)

    for pattern, repl in STYLE_CALLS:
        out = re.sub(pattern, repl, out, flags=re.MULTILINE)

    # ``sns.color_palette('Set2')`` -> explicit Minitab list
    out = re.sub(
        r"sns\.color_palette\(\s*(['\"])(?:Set2|Set3|tab10|tab20|muted|deep)\1\s*\)",
        "ms.CATEGORICAL",
        out,
    )
    out = re.sub(
        r"sns\.color_palette\(\s*ms\.CATEGORICAL\s*\)",
        "ms.CATEGORICAL",
        out,
    )

    # Tidy the blank lines left behind by removed style calls.
    out = re.sub(r"\n{3,}", "\n\n", out)

    return out


def process(path: Path, dry_run: bool) -> tuple[int, int]:
    nb = json.loads(path.read_text(encoding="utf-8"))
    plot_cells = 0
    changed_cells = 0

    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell["source"])
        if "minitab_style" in source and "ms.apply_style()" in source:
            continue  # the setup cell
        if not has_plotting(source):
            continue

        plot_cells += 1
        new_source = restyle(source)
        if new_source != source:
            cell["source"] = new_source.splitlines(keepends=True)
            cell["outputs"] = []
            cell["execution_count"] = None
            changed_cells += 1

    # Some notebooks never had a setup cell, so nothing defined ``ms``.
    if needs_style_import(nb):
        for cell in nb["cells"]:
            if cell["cell_type"] != "code":
                continue
            source = "".join(cell["source"])
            bootstrap = STYLE_BOOTSTRAP + "\n\n" + source
            cell["source"] = bootstrap.splitlines(keepends=True)
            changed_cells += 1
            break

    if changed_cells and not dry_run:
        path.write_text(
            json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    return plot_cells, changed_cells


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--notebook", default="**/*.ipynb")
    args = parser.parse_args()

    files = sorted(Path(p) for p in glob.glob(args.notebook, recursive=True))
    total_plots = total_changed = 0
    for path in files:
        plots, changed = process(path, args.dry_run)
        total_plots += plots
        total_changed += changed
        if changed:
            print(f"  {path}: {changed}/{plots} plot cells restyled")

    prefix = "[dry-run] " if args.dry_run else ""
    print(
        f"{prefix}restyled {total_changed} of {total_plots} plot cells "
        f"across {len(files)} notebooks"
    )


if __name__ == "__main__":
    main()
