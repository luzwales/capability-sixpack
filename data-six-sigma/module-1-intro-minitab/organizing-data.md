# Organizing Your Data

## The First Step

Ever looked at your dataset wanting to make a statistical analysis but had no clue where to start?

> **Organize your dataset before analyzing your dataset.**

---

## Basic Data Structure

Data is organized based on **units** and **variables**.

| Element | Definition | Stored In |
|---------|------------|-----------|
| Unit | An individual case; the thing being measured | Rows |
| Variable | A property of the unit that was measured | Columns |

---

## Example: Bank Cross-Border Transfers

**Context:** You're a department head at a bank handling cross-border money transfers (e.g., Netherlands → United States or China).

### The Problem

Sometimes things go wrong:
- Wrong currency used
- Wrong amount transferred
- Wrong language

When mistakes occur, clients submit **reclaims**. You initiate an **investigation** to solve each reclaim.

### Building the Dataset

Each reclaim gets a unique number for administrative purposes:

| Reclaim | Total Time | Type | Iterations |
|---------|------------|------|------------|
| 1 | 30 | AN | 3 |
| 2 | 45 | BX | 2 |
| 3 | 22 | AN | 1 |
| 4 | 38 | CY | 4 |
| 5 | 51 | BX | 5 |

### Variables Explained

| Variable | What It Measures |
|----------|------------------|
| Reclaim | Unique identifier |
| Total Time | Days to solve (CTQ - Critical to Quality) |
| Type | Category of reclaim (AN, BX, CY, etc.) |
| Iterations | Number of contacts with foreign counterparty |

---

## Units: The Rows

**Units are the things being measured**—in this example, each reclaim.

We collected data on **5 reclaims = 5 units**.

### Alternative Terminology

| Term | Usage |
|------|-------|
| Experimental unit | Experiments/research |
| Observational unit | Observational studies |
| Case | General data analysis |

> Units are **always stored in the rows** of your dataset.

---

## Variables: The Columns

**Variables are the properties of the units that you measured.**

In our example, we measured **4 variables** for each unit:
1. Reclaim number
2. Total time
3. Type
4. Iterations

> Variables are **always stored in the columns** of your dataset.

---

## Why This Structure Matters

> Most statistical software packages require data organized this way: **units in rows, variables in columns**.

Organizing your data properly makes analysis much easier.

---

## Measurement Units

Looking at Total Time = 30 for the first reclaim—what does "30" mean?

- 30 hours?
- 30 days?
- 30 weeks?

The **measurement unit** tells you what the value means. In this example: **days**.

So the first reclaim took **30 days** to finish.

---

## Summary

- A dataset consists of **units** (rows) and **variables** (columns)
- **Units** = individual cases, things being measured (also called experimental/observational units or cases)
- **Variables** = properties of units that were measured
- **Always organize**: units in rows, variables in columns
- **Measurement units** are required to understand what data values mean
- **Organize first, analyze second**
