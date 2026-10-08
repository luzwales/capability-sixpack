# Data Six Sigma Project Guidelines

## Project Overview

This repository adapts the **Data Analytics for Lean Six Sigma** Coursera course (University of Amsterdam) from Minitab to Python/Jupyter notebooks. Each notebook corresponds to a specific course video/section.

---

## Core Principles

### Source Fidelity

**ONLY include content from the provided transcript.** Do not:
- Add "educational illustrations" or extra examples
- Create simulated data to demonstrate concepts
- Add comparisons or scenarios not in the transcript
- Freelance with "helpful" additions
- Invent examples to clarify points

If the transcript mentions something, include it. If it doesn't, don't add it.

### Data Sources

**ALWAYS use actual course data from `data/da-lss.xlsx`.**

See [reference/data-dictionary.ipynb](reference/data-dictionary.ipynb) for complete documentation of each sheet including columns, data types, skiprows values, and load code.

**NEVER generate simulated data** unless the transcript explicitly describes creating example data for illustration.

---

## Notebook Patterns

### Structure

```markdown
# Topic Title

**Module N: Module Name** | Lean Six Sigma Data Analytics

---

## Section from Transcript

[Content matching transcript]
```

- Use `---` dividers between major sections
- Include tables to summarize concepts (as shown in course)
- Match the course narrative and examples exactly
- End with Summary/Key Takeaways section

### Setup Cell

```python
# Setup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# --- Minitab-style house style -------------------------------------------
import sys
from pathlib import Path as _Path

# minitab_style.py lives in the parent folder of each module directory
sys.path.append(str(_Path.cwd().parent))
import minitab_style as ms

ms.apply_style()

DATA_FILE = '../data/da-lss.xlsx'
xlsx = pd.ExcelFile(DATA_FILE)

print('Ready for [topic] analysis!')
```

**NEVER** call `sns.set_style()`, `sns.set_theme()` or `plt.style.use()` —
they fight the house style. `ms.apply_style()` already configures the gray
figure frame, white plot area, dotted grid, fonts and color cycle.

### Output Formatting

```python
print('SECTION HEADER')
print('=' * 50)
print(f'Result: {value:.4f}')
```

### Data Loading

Always verify the correct `skiprows` value by examining the Excel sheet structure first:

```python
# Check sheet structure BEFORE writing loader
df = pd.read_excel(xlsx, sheet_name='SheetName', header=None)
print(df.head(15))  # Find where data actually starts
```

Standard loader pattern:
```python
def load_dataname():
    df = pd.read_excel(xlsx, sheet_name='SheetName', skiprows=N, header=0, usecols=[...])
    df.columns = ['Col1', 'Col2', ...]
    return df.dropna()
```

---

## Visualization Guidelines

**All charts use the shared house style in `minitab_style.py`.** Never
hand-pick colors or call `sns.set_style()`.

### Preferred: use the helpers

Each returns a fully-styled figure in one call.

```python
ms.histogram(df['col'], title_text='Histogram of col', xlabel='col', normal_fit=True)
ms.boxplot(df['col'], ylabel='col')
ms.boxplot_by_group(df, 'shift', 'col', xlabel='Shift', ylabel='col')
ms.bar(df['cat'].value_counts().index, df['cat'].value_counts().values, xlabel='Category')
ms.pareto(df['cause'].value_counts(), xlabel='Cause')
ms.scatter(df['x'], df['y'], fit=True, xlabel='X', ylabel='Y')
ms.residual_chart(df['x'], df['y'], xlabel='X')
ms.probability_plot(df['col'])
ms.empirical_cdf(df['col'])
ms.control_chart(df['col'], ylabel='col')
ms.interval_plot(centers, lows, highs, labels)
```

### When raw matplotlib/seaborn is unavoidable

`ms.apply_style()` still applies the frame, grid, fonts and color cycle, so
inherit it and use the palette constants:

```python
ax.bar(x, y, color=ms.HIST_FILL, edgecolor=ms.HIST_EDGE)   # bars/histograms
ax.plot(x, y, color=ms.BLUE)          # data series / within-subgroup
ax.axhline(v, color=ms.RED)           # control & spec limits
ax.axhline(v, color=ms.GREEN)         # centre line / mean / target
colors=ms.CATEGORICAL                 # multi-category pies and bars
```

- Use `tick_labels`, never the removed `labels` kwarg (matplotlib >= 3.9)
- Use seaborn with `hue` + `legend=False` to avoid deprecation warnings
- Add clear titles and axis labels

### Before committing a notebook

```bash
python run_all_notebooks.py            # execute all, report pass/fail
python run_all_notebooks.py --module 6 # just module 6
```

---

## What to Include vs Exclude

**INCLUDE:**
- Exact examples from transcript
- Statistical concepts explained in the video
- Formulas and interpretations as presented
- Business context from the scenario
- Data analysis steps shown in Minitab

**EXCLUDE:**
- Additional examples "for clarity"
- Simulated data comparisons
- Extended explanations beyond transcript
- Alternative approaches not mentioned
- "Best practices" additions

---

## When Adding New Content

1. User provides transcript
2. Identify the data source mentioned (which Excel sheet)
3. Verify data structure and correct skiprows (see data-dictionary.ipynb)
4. Implement ONLY what's in the transcript
5. Update README.md with new entry
6. If anything is unclear, ASK - don't assume
