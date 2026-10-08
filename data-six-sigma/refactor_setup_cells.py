"""Rewrite the shared setup cell in every course notebook.

The notebooks each carried their own styling bootstrap
(``sns.set_style('whitegrid')`` + ad-hoc imports). This replaces the
styling portion with the shared :mod:`minitab_style` house style while
leaving the data-loading part of each setup cell untouched.

Run from the ``data-six-sigma`` directory::

    python refactor_setup_cells.py [--dry-run]
"""

from __future__ import annotations

import argparse
import glob
import json
import re
from pathlib import Path

STYLE_IMPORT = """import sys
from pathlib import Path as _Path

# Shared Minitab-style house style (gray frame, white plot area, Minitab palette)
sys.path.append(str(_Path.cwd().parent))
import minitab_style as ms

ms.apply_style()"""


def is_setup_cell(source: str) -> bool:
    """A setup cell is the one that declares the data file / plotting env.

    Matched on the *first* cell only -- a later cell may legitimately use
    ``sns`` or mention the data file in a comment, so we additionally require
    that the cell is not already drawing anything.
    """
    if "minitab_style" in source:
        return False
    if "DATA_FILE" in source or "da-lss.xlsx" in source:
        return True
    # ``import seaborn as sns`` is the real signal for a styling bootstrap.
    return bool(re.search(r"^\s*import\s+seaborn", source, re.MULTILINE))


def rewrite_setup(source: str, *, keep_seaborn: bool = False) -> str:
    """Drop the ad-hoc seaborn styling, keep imports + data loading."""
    lines = source.splitlines()

    kept: list[str] = []
    for line in lines:
        stripped = line.strip()
        # Drop the seaborn import and its set_style call.
        if stripped == "import seaborn as sns" and not keep_seaborn:
            continue
        if stripped.startswith("sns.set_style"):
            continue
        kept.append(line)

    # Collapse runs of 3+ blank lines left behind by the removals.
    cleaned: list[str] = []
    for line in kept:
        if line.strip() == "" and cleaned and cleaned[-1].strip() == "":
            continue
        cleaned.append(line)

    # matplotlib is still used directly by a few cells; keep the import.
    body = "\n".join(cleaned).rstrip()

    style_block = (
        "\n\n# --- Minitab-style house style -------------------------------------------\n"
        "import sys\n"
        "from pathlib import Path as _Path\n"
        "\n"
        "# minitab_style.py lives in the parent folder of each module directory\n"
        "sys.path.append(str(_Path.cwd().parent))\n"
        "import minitab_style as ms\n"
        "\n"
        "ms.apply_style()"
    )

    # Insert the style block right after the import block (before data loading).
    insert_at = 0
    for i, line in enumerate(cleaned):
        if line.startswith(("DATA_FILE", "xlsx =", "df =", "print(")):
            insert_at = i
            break
    else:
        insert_at = len(cleaned)

    head = "\n".join(cleaned[:insert_at]).rstrip()
    tail = "\n".join(cleaned[insert_at:]).lstrip("\n")
    result = head + style_block + "\n\n" + tail if tail else head + style_block
    return result.rstrip() + "\n"


def process(path: Path, dry_run: bool) -> bool:
    nb = json.loads(path.read_text(encoding="utf-8"))
    changed = False

    # Some cells still call sns.* directly, so only drop the seaborn import
    # when nothing outside the setup cell references it.
    setup_source = ""
    for cell in nb["cells"]:
        if cell["cell_type"] == "code" and is_setup_cell("".join(cell["source"])):
            setup_source = "".join(cell["source"])
            break

    uses_seaborn = any(
        cell["cell_type"] == "code"
        and "minitab_style" not in "".join(cell["source"])
        and re.search(r"\bsns\.", "".join(cell["source"]))
        for cell in nb["cells"]
    ) or bool(re.search(r"\bsns\.", setup_source))

    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell["source"])
        if not is_setup_cell(source):
            continue

        new_source = rewrite_setup(source, keep_seaborn=uses_seaborn)
        cell["source"] = new_source.splitlines(keepends=True)
        cell["outputs"] = []
        cell["execution_count"] = None
        changed = True
        break  # only the first setup cell per notebook

    if changed and not dry_run:
        path.write_text(
            json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    return changed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    files = sorted(Path(p) for p in glob.glob("**/*.ipynb", recursive=True))
    touched = []
    for path in files:
        if process(path, args.dry_run):
            touched.append(path)

    prefix = "[dry-run] " if args.dry_run else ""
    print(f"{prefix}updated setup cells in {len(touched)}/{len(files)} notebooks")
    for path in touched:
        print(f"  {path}")


if __name__ == "__main__":
    main()
