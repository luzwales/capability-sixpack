# Data Analytics for Lean Six Sigma

A Python-based adaptation of a Lean Six Sigma data analytics course, translating Minitab workflows to Python/Jupyter notebooks.

## Project Overview

This repository demonstrates statistical analysis techniques from a Lean Six Sigma curriculum, implemented in Python instead of Minitab. Each notebook combines conceptual explanations with practical code examples.

### What This Demonstrates

- **Python data analysis:** pandas, scipy, statsmodels, matplotlib, seaborn
- **Statistical knowledge:** Six Sigma methodology applied to real business problems
- **Tool translation:** Minitab workflows mapped to equivalent Python code
- **Practical application:** Real course datasets, not toy examples

---

## Modules

### Module 1: Introduction to Lean Six Sigma

Conceptual foundations (markdown files):

| Document | Topic |
|----------|-------|
| [intro-lean-six-sigma](module-1-intro-minitab/intro-lean-six-sigma.md) | What is Lean Six Sigma |
| [data-and-dmaic](module-1-intro-minitab/data-and-dmaic.md) | DMAIC roadmap |
| [organizing-data](module-1-intro-minitab/organizing-data.md) | Data organization principles |
| [sampling](module-1-intro-minitab/sampling.md) | Sampling strategies |
| [selecting-ctqs](module-1-intro-minitab/selecting-ctqs.md) | Critical to Quality factors |
| [units-operational-definition](module-1-intro-minitab/units-operational-definition.md) | Units and operational definitions |

### Module 2: Data Visualization

| Notebook | Topic | Key Concepts |
|----------|-------|--------------|
| [01-numerical-categorical](module-2-data-visualization/01-numerical-categorical.ipynb) | Data Types | Numerical vs categorical, discrete vs continuous |
| [02-descriptive-statistics](module-2-data-visualization/02-descriptive-statistics.ipynb) | Summary Statistics | Mean, median, std dev, quartiles, IQR |
| [03-visualizing-numerical](module-2-data-visualization/03-visualizing-numerical.ipynb) | Numerical Graphs | Histograms, boxplots, skewness |
| [04-visualizing-categorical](module-2-data-visualization/04-visualizing-categorical.ipynb) | Categorical Graphs | Pie charts, bar charts, tally tables |
| [05-pareto-analysis](module-2-data-visualization/05-pareto-analysis.ipynb) | Pareto Charts | 80/20 principle, vital few vs trivial many |
| [06-visualizing-two-variables](module-2-data-visualization/06-visualizing-two-variables.ipynb) | Two-Variable Graphs | Scatterplots, grouped boxplots, stacked bars |
| [07-exercise-investigation-time](module-2-data-visualization/07-exercise-investigation-time.ipynb) | Practice Exercise | Applying all Module 2 techniques |
| [08-exercise-coffee-batch](module-2-data-visualization/08-exercise-coffee-batch.ipynb) | Practice Exercise | Boxplot with groups, identifying influence factors |

### Module 3: Probability Distributions

| Notebook | Topic | Key Concepts |
|----------|-------|--------------|
| [01-population-vs-sampling](module-3-probability-distributions/01-population-vs-sampling.ipynb) | Population & Sampling | Population vs sample, statistical inference |
| [02-estimation-confidence-intervals](module-3-probability-distributions/02-estimation-confidence-intervals.ipynb) | Estimation | Sample statistics, population parameters, confidence intervals |
| [03-normal-lognormal-weibull](module-3-probability-distributions/03-normal-lognormal-weibull.ipynb) | Distribution Types | Normal, Weibull, Lognormal; fitting distributions to data |
| [04-probability-plot](module-3-probability-distributions/04-probability-plot.ipynb) | Probability Plots | Finding best-fit distribution, Anderson-Darling statistic |
| [05-empirical-cdf](module-3-probability-distributions/05-empirical-cdf.ipynb) | Empirical CDF | Calculate percentages, service level agreements |
| [06-normal-distribution-properties](module-3-probability-distributions/06-normal-distribution-properties.ipynb) | Normal Properties | μ and σ parameters, 68-95-99.7 rule |
| [07-exercise-length-stay](module-3-probability-distributions/07-exercise-length-stay.ipynb) | Practice Exercise | Probability plot + Empirical CDF workflow |

### Module 4: Statistical Testing

| Notebook | Topic | Key Concepts |
|----------|-------|--------------|
| [01-intro-data-analysis](module-4-statistical-testing/01-intro-data-analysis.ipynb) | Introduction | CTQ vs influence factors, choosing analysis methods |
| [02-hypothesis-testing](module-4-statistical-testing/02-hypothesis-testing.ipynb) | Hypothesis Testing | H₀ vs H₁, p-values, 0.05 threshold |
| [03-causality](module-4-statistical-testing/03-causality.ipynb) | Causality | Correlation vs causation, four causality errors |

### Module 5: Numerical Outcomes

| Notebook | Topic | Key Concepts |
|----------|-------|--------------|
| [01-anova-introduction](module-5-numerical-outcomes/01-anova-introduction.ipynb) | ANOVA Basics | When to use ANOVA, organizing data, wide vs long format |
| [02-anova-analysis](module-5-numerical-outcomes/02-anova-analysis.ipynb) | ANOVA Analysis | F-statistic, p-value, R-squared, significant vs relevant |
| [03-anova-residuals](module-5-numerical-outcomes/03-anova-residuals.ipynb) | Residual Analysis | Normality check, outliers, four-in-one plot |
| [04-kruskal-wallis-test](module-5-numerical-outcomes/04-kruskal-wallis-test.ipynb) | Kruskal-Wallis | Non-parametric alternative, comparing medians |
| [05-two-sample-t-test](module-5-numerical-outcomes/05-two-sample-t-test.ipynb) | Two-Sample T-Test | Comparing means of two groups, Student's t-test |
| [06-equality-variances-test](module-5-numerical-outcomes/06-equality-variances-test.ipynb) | Equal Variances Test | Levene's test, comparing variation across groups |
| [07-exercise-productivity](module-5-numerical-outcomes/07-exercise-productivity.ipynb) | Exercise: Productivity | ANOVA workflow, residual analysis, Kruskal-Wallis alternative |
| [08-exercise-department](module-5-numerical-outcomes/08-exercise-department.ipynb) | Exercise: Department | ANOVA with non-normal residuals, effect size consideration |

### Module 6: Correlation Analysis

| Notebook | Topic | Key Concepts |
|----------|-------|--------------|
| [01-correlation](module-6-correlation-analysis/01-correlation.ipynb) | Correlation | Definition, positive/negative, interpretation rules, causation warning |
| [02-intro-regression](module-6-correlation-analysis/02-intro-regression.ipynb) | Introduction to Regression | When to use, tea bag example, four steps overview |
| [03-regression-analysis](module-6-correlation-analysis/03-regression-analysis.ipynb) | Regression Analysis | Fitted line plot, p-value, R-squared, big fish vs small fish |
| [04-regression-residuals](module-6-correlation-analysis/04-regression-residuals.ipynb) | Regression Residuals | Residual analysis, normality check, outliers, assumption validation |
| [05-regression-prediction-intervals](module-6-correlation-analysis/05-regression-prediction-intervals.ipynb) | Prediction Intervals | 95% prediction interval, 97.5% upper limit, CTQ performance |
| [06-quadratic-regression](module-6-correlation-analysis/06-quadratic-regression.ipynb) | Quadratic Regression | Curved relationships, when linear fails, R² comparison |
| [07-exercise-picking](module-6-correlation-analysis/07-exercise-picking.ipynb) | Exercise: Picking | Regression with prediction intervals for planning |

### Module 7: Categorical Outcomes

| Notebook | Topic | Key Concepts |
|----------|-------|--------------|
| [01-chi-square-analysis](module-7-categorical-outcomes/01-chi-square-analysis.ipynb) | Chi-Square Analysis | Categorical Y + categorical X, cross-tabulation, expected counts |
| [02-logistic-regression](module-7-categorical-outcomes/02-logistic-regression.ipynb) | Logistic Regression | Categorical Y + numerical X, S-curve, event/trial format |
| [03-exercise-printers](module-7-categorical-outcomes/03-exercise-printers.ipynb) | Exercise: Printers | Chi-square with observed vs expected comparison |
| [04-exercise-students](module-7-categorical-outcomes/04-exercise-students.ipynb) | Exercise: Students | Logistic regression, causality warning |

---

## Reference

| Document | Description |
|----------|-------------|
| [minitab-to-python.md](reference/minitab-to-python.md) | Index of techniques with links to relevant notebooks |
| [data-dictionary.ipynb](reference/data-dictionary.ipynb) | Documentation of all datasets in da-lss.xlsx |

---

## Tools & Libraries

```python
pandas       # Data manipulation
numpy        # Numerical operations
matplotlib   # Visualization
seaborn      # Statistical visualizations
scipy        # Statistical tests
statsmodels  # Regression, GLM, ANOVA tables
openpyxl     # Excel file reading
```

---

## Data

Course data is in `data/da-lss.xlsx` (19 datasets).

See [reference/data-dictionary.ipynb](reference/data-dictionary.ipynb) for complete documentation of each sheet including columns, data types, and load code.

---

## Getting Started

```bash
# Clone the repository
git clone https://github.com/yourusername/data-six-sigma.git
cd data-six-sigma

# Install dependencies
pip install -r requirements.txt

# Open Jupyter
jupyter notebook
```

---

## Course Source

**Data Analytics for Lean Six Sigma**
University of Amsterdam (Coursera)
https://www.coursera.org/learn/data-analytics-for-lean-six-sigma

---

## License

Educational use. Course content adapted from IBIS UvA Lean Six Sigma curriculum.
