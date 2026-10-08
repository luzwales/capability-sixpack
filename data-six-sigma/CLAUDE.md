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
import seaborn as sns
from scipy import stats

sns.set_style('whitegrid')

DATA_FILE = '../data/da-lss.xlsx'
xlsx = pd.ExcelFile(DATA_FILE)

print('Ready for [topic] analysis!')
```

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

- Use seaborn with `hue` parameter and `legend=False` to avoid deprecation warnings
- Use matplotlib `tick_labels` instead of deprecated `labels` parameter
- Match Minitab output style where possible
- Add clear titles and axis labels

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
