"""Execute every notebook in the course and report pass/fail.

Used to verify that the Minitab-style refactor did not break any analysis.

    python run_all_notebooks.py            # execute all
    python run_all_notebooks.py --module 6 # only module-6 notebooks
"""

from __future__ import annotations

import argparse
import glob
import os
import subprocess
import sys
import time
from pathlib import Path

PY = sys.executable


def run_one(nb_path: Path, timeout: int = 600) -> tuple[bool, str, float]:
    """Execute a notebook in place; return (ok, message, seconds)."""
    cwd = nb_path.parent
    start = time.time()
    try:
        proc = subprocess.run(
            [
                PY, "-m", "jupyter", "nbconvert",
                "--to", "notebook", "--execute",
                "--inplace", "--ExecutePreprocessor.timeout=300",
                str(nb_path.name),
            ],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return False, f"timeout after {timeout}s", time.time() - start

    elapsed = time.time() - start
    if proc.returncode == 0:
        return True, "ok", elapsed

    # Surface the real exception, not the nbconvert noise.
    err = proc.stderr
    for line in reversed(err.splitlines()):
        if "Error" in line or "error" in line:
            return False, line.strip()[:200], elapsed
    return False, err.strip().splitlines()[-1][:200] if err.strip() else "unknown", elapsed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--module", default="")
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()

    pattern = f"module-{args.module}-*/**.ipynb" if args.module else "**/*.ipynb"
    files = sorted(Path(p) for p in glob.glob(pattern, recursive=True))

    # nbconvert needs a writable HOME for its config
    os.environ.setdefault("JUPYTER_PATH", "")

    passed, failed = [], []
    for path in files:
        ok, msg, elapsed = run_one(path, timeout=args.timeout)
        rel = path.as_posix()
        if ok:
            passed.append(rel)
            print(f"PASS  {elapsed:6.1f}s  {rel}")
        else:
            failed.append((rel, msg))
            print(f"FAIL  {elapsed:6.1f}s  {rel}\n        {msg}")

    print(f"\n{len(passed)}/{len(files)} notebooks executed successfully")
    if failed:
        print("\nFailures:")
        for rel, msg in failed:
            print(f"  {rel}\n    {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
