# Sampling

## The Sampling Problem

You're standing next to a highway wondering: **What is the average speed on this highway?**

Using a speed camera, you measure vehicle speeds. But you can't measure all vehicles—it's impossible to measure two cars passing simultaneously.

**Which vehicles should you select to get a good estimate of average speed?**

This selection process is called **sampling**.

---

## Why Sample?

### Primary Reason

It's often **difficult or impossible** to obtain information on the whole population.

With just one speed camera, you cannot measure every single vehicle passing by.

### When Sampling Isn't Necessary

If you have automated speed cameras above each lane, you can measure the entire population.

### When Sampling Is Preferred

Even when full population data exists, sampling can provide **more detailed information** about a subset than vague information about everyone.

---

## What Makes a Good Sample?

A sample must be **representative**—the selected vehicles should be a good representation of all vehicles passing by.

### Technical Definition

> A representative sample is based on a mechanism that is **independent of the question** you want to answer.

---

## Bad Sampling Strategies

**Question:** What is the average speed on the highway?

| Strategy | Why It Fails |
|----------|--------------|
| Only measure trucks | Trucks always drive slower than other vehicles |
| Only measure left lane | Left lane vehicles drive faster than other lanes |
| Only measure during traffic jams | Cars drive slower than normal during congestion |

All these strategies are **not independent** of the question asked—they systematically bias the result.

---

## Random Sampling

**The solution:** Sample randomly.

### What "Randomly" Means

Each item (vehicle) has an **equal chance of being selected**.

**Example:** If 5,000 vehicles pass by today, each vehicle should have:
- 1/5,000 probability of selection
- = 0.02% chance

---

## Advantages of Random Sampling

### 1. Even Spread Across Types

Random selection ensures vehicles are spread evenly over vehicle types:

| Vehicle Type | In Population | In Sample |
|--------------|---------------|-----------|
| Cars | Most common | Higher likelihood of selection |
| Trucks | Less common | Lower likelihood of selection |
| Motorcycles | Least common | Lowest likelihood of selection |

The sample naturally **mirrors the population proportions**.

### 2. Even Spread Across Time

Random selection spreads vehicles across different times of day:

| Time Period | Driving Behavior |
|-------------|------------------|
| Night | Usually faster |
| Daytime | Normal speeds |
| Traffic jams | Slower speeds |

---

## Critical Warning

> **Never randomly select items yourself.**

Humans are not programmed to make random selections. Unconsciously, you will select items that you:
- Prefer
- Have seen before
- Recognize

**Always use a computer** for random selection.

---

## Random Sampling in Minitab

**Goal:** Select 100 vehicles randomly from 5,000 total vehicles.

### Step 1: Create the Population

1. Go to **Calc → Make Patterned Data → Simple Set of Numbers**
2. Store in column: `Population vehicles`
3. First value: `1`
4. Last value: `5000`
5. Steps: `1`

Result: A column counting 1 to 5,000.

### Step 2: Select Random Sample

1. Go to **Calc → Random Data → Sample From Columns**
2. Number of rows to sample: `100`
3. Sample from: `Population vehicles`
4. Store in: `Sample vehicles`

Result: 100 randomly selected vehicle numbers (e.g., first selection might be #492).

> Running this again will produce different numbers—that's the nature of random selection.

---

## Summary

- **Sampling** is necessary when measuring the entire population is impossible or impractical
- A good sample must be **representative**—independent of the question being asked
- **Random sampling** gives each item an equal chance of selection
- Random samples naturally **mirror population proportions** across types and time
- **Never select randomly yourself**—always use a computer
- Minitab: Use **Calc → Random Data → Sample From Columns**
