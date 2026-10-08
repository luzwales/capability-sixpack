# Minitab to Python Reference Index

Quick lookup for finding Python implementations of Minitab techniques in the course notebooks.

---

## Analysis Selection Guide

Use this decision tree to select the appropriate analysis method:

| Y Variable | X Variable | Method | Notebook |
|------------|------------|--------|----------|
| Numerical | Categorical | ANOVA / Kruskal-Wallis | [module-5](../module-5-numerical-outcomes/) |
| Numerical | Numerical | Regression / Correlation | [module-6](../module-6-correlation-analysis/) |
| Categorical | Categorical | Chi-Square | [01-chi-square-analysis](../module-7-categorical-outcomes/01-chi-square-analysis.ipynb) |
| Categorical | Numerical | Logistic Regression | [02-logistic-regression](../module-7-categorical-outcomes/02-logistic-regression.ipynb) |

---

## By Technique

### Data Visualization

| Technique | Minitab Menu | Notebook |
|-----------|--------------|----------|
| Histogram | Graph → Histogram | [03-visualizing-numerical](../module-2-data-visualization/03-visualizing-numerical.ipynb) |
| Box Plot | Graph → Boxplot | [03-visualizing-numerical](../module-2-data-visualization/03-visualizing-numerical.ipynb) |
| Pie Chart | Graph → Pie Chart | [04-visualizing-categorical](../module-2-data-visualization/04-visualizing-categorical.ipynb) |
| Bar Chart | Graph → Bar Chart | [04-visualizing-categorical](../module-2-data-visualization/04-visualizing-categorical.ipynb) |
| Pareto Chart | Stat → Quality Tools → Pareto | [05-pareto-analysis](../module-2-data-visualization/05-pareto-analysis.ipynb) |
| Scatter Plot | Graph → Scatterplot | [06-visualizing-two-variables](../module-2-data-visualization/06-visualizing-two-variables.ipynb) |

### Descriptive Statistics

| Technique | Minitab Menu | Notebook |
|-----------|--------------|----------|
| Descriptive Statistics | Stat → Basic Statistics → Display Descriptive Statistics | [02-descriptive-statistics](../module-2-data-visualization/02-descriptive-statistics.ipynb) |
| Numerical vs Categorical | — | [01-numerical-categorical](../module-2-data-visualization/01-numerical-categorical.ipynb) |

### Probability Distributions

| Technique | Minitab Menu | Notebook |
|-----------|--------------|----------|
| Normal Distribution | Stat → Basic Statistics | [03-normal-lognormal-weibull](../module-3-probability-distributions/03-normal-lognormal-weibull.ipynb) |
| Lognormal Distribution | Stat → Reliability | [03-normal-lognormal-weibull](../module-3-probability-distributions/03-normal-lognormal-weibull.ipynb) |
| Weibull Distribution | Stat → Reliability | [03-normal-lognormal-weibull](../module-3-probability-distributions/03-normal-lognormal-weibull.ipynb) |
| Probability Plot | Graph → Probability Plot | [04-probability-plot](../module-3-probability-distributions/04-probability-plot.ipynb) |
| Empirical CDF | Graph → Empirical CDF | [05-empirical-cdf](../module-3-probability-distributions/05-empirical-cdf.ipynb) |
| Confidence Intervals | Stat → Basic Statistics | [02-estimation-confidence-intervals](../module-3-probability-distributions/02-estimation-confidence-intervals.ipynb) |

### Hypothesis Testing

| Technique | Minitab Menu | Notebook |
|-----------|--------------|----------|
| Hypothesis Testing Concepts | — | [02-hypothesis-testing](../module-4-statistical-testing/02-hypothesis-testing.ipynb) |
| Causality | — | [03-causality](../module-4-statistical-testing/03-causality.ipynb) |

### Numerical Y + Categorical X

| Technique | Minitab Menu | Notebook |
|-----------|--------------|----------|
| One-Way ANOVA | Stat → ANOVA → One-Way | [01-anova-introduction](../module-5-numerical-outcomes/01-anova-introduction.ipynb), [02-anova-analysis](../module-5-numerical-outcomes/02-anova-analysis.ipynb) |
| ANOVA Residuals | — | [03-anova-residuals](../module-5-numerical-outcomes/03-anova-residuals.ipynb) |
| Kruskal-Wallis Test | Stat → Nonparametrics → Kruskal-Wallis | [04-kruskal-wallis-test](../module-5-numerical-outcomes/04-kruskal-wallis-test.ipynb) |
| Two-Sample T-Test | Stat → Basic Statistics → 2-Sample t | [05-two-sample-t-test](../module-5-numerical-outcomes/05-two-sample-t-test.ipynb) |
| Equality of Variances | Stat → ANOVA → Test for Equal Variances | [06-equality-variances-test](../module-5-numerical-outcomes/06-equality-variances-test.ipynb) |

### Numerical Y + Numerical X

| Technique | Minitab Menu | Notebook |
|-----------|--------------|----------|
| Correlation | Stat → Basic Statistics → Correlation | [01-correlation](../module-6-correlation-analysis/01-correlation.ipynb) |
| Simple Linear Regression | Stat → Regression → Fitted Line Plot | [02-intro-regression](../module-6-correlation-analysis/02-intro-regression.ipynb), [03-regression-analysis](../module-6-correlation-analysis/03-regression-analysis.ipynb) |
| Regression Residuals | — | [04-regression-residuals](../module-6-correlation-analysis/04-regression-residuals.ipynb) |
| Prediction Intervals | Stat → Regression → Options | [05-regression-prediction-intervals](../module-6-correlation-analysis/05-regression-prediction-intervals.ipynb) |
| Quadratic Regression | Stat → Regression → Fitted Line Plot (Quadratic) | [06-quadratic-regression](../module-6-correlation-analysis/06-quadratic-regression.ipynb) |

### Categorical Y

| Technique | Minitab Menu | Notebook |
|-----------|--------------|----------|
| Chi-Square Analysis | Stat → Tables → Cross Tabulation and Chi-Square | [01-chi-square-analysis](../module-7-categorical-outcomes/01-chi-square-analysis.ipynb) |
| Logistic Regression | Stat → Regression → Binary Fitted Line Plot | [02-logistic-regression](../module-7-categorical-outcomes/02-logistic-regression.ipynb) |

---

## By DMAIC Phase

| Phase | Techniques | Notebooks |
|-------|------------|-----------|
| **Define** | CTQ selection, Operational definitions | [module-1](../module-1-intro-minitab/) |
| **Measure** | Pareto analysis, Sampling, Descriptive stats | [module-2](../module-2-data-visualization/) |
| **Analyze** | Distributions, Probability plots, Hypothesis testing | [module-3](../module-3-probability-distributions/), [module-4](../module-4-statistical-testing/) |
| **Improve** | ANOVA, T-tests, Regression, Chi-square | [module-5](../module-5-numerical-outcomes/), [module-6](../module-6-correlation-analysis/), [module-7](../module-7-categorical-outcomes/) |
| **Control** | Before/after comparison (Two-sample t-test) | [05-two-sample-t-test](../module-5-numerical-outcomes/05-two-sample-t-test.ipynb) |

---

## Exercises

Practice notebooks applying multiple techniques:

| Exercise | Techniques Used | Notebook |
|----------|-----------------|----------|
| Investigation Time | Descriptive stats, Visualization | [07-exercise-investigation-time](../module-2-data-visualization/07-exercise-investigation-time.ipynb) |
| Coffee Batch | Descriptive stats, Visualization | [08-exercise-coffee-batch](../module-2-data-visualization/08-exercise-coffee-batch.ipynb) |
| Length of Stay | Probability distributions | [07-exercise-length-stay](../module-3-probability-distributions/07-exercise-length-stay.ipynb) |
| Productivity | ANOVA, Kruskal-Wallis | [07-exercise-productivity](../module-5-numerical-outcomes/07-exercise-productivity.ipynb) |
| Department | ANOVA | [08-exercise-department](../module-5-numerical-outcomes/08-exercise-department.ipynb) |
| Picking | Regression, Prediction intervals | [07-exercise-picking](../module-6-correlation-analysis/07-exercise-picking.ipynb) |
| Printers | Chi-square | [03-exercise-printers](../module-7-categorical-outcomes/03-exercise-printers.ipynb) |
| Students | Logistic regression | [04-exercise-students](../module-7-categorical-outcomes/04-exercise-students.ipynb) |

---

## Python Libraries Quick Reference

```python
import pandas as pd          # Data manipulation
import numpy as np           # Numerical operations
import matplotlib.pyplot as plt  # Visualization
import seaborn as sns        # Statistical visualization
from scipy import stats      # Statistical tests
import statsmodels.api as sm # Regression, GLM
```

**Install:** `pip install -r requirements.txt`
