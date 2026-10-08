# Units and Operational Definition

## The Speed Camera Example

You're standing next to a Dutch highway wondering: **How fast do vehicles drive here?**

To answer this, you use a speed camera and measure the speed of each passing vehicle.

| Element | Value |
|---------|-------|
| Variable (CTQ/Y) | Speed |
| Unit | Vehicle |
| Measurement Unit | Kilometers per hour |

---

## Units vs Measurement Units

These two concepts are frequently confused but serve different purposes.

### Units

**Units are people, objects, or phenomena you collect data on.**

- The "things" in your dataset
- Each row in your spreadsheet represents one unit

### Measurement Units

**Measurement units define what a measurement means.**

- The properties of the things you collect data on
- How you express the value (km/h, minutes, percentage, etc.)

| Concept | Question It Answers | Example |
|---------|---------------------|---------|
| Unit | What am I collecting data on? | Vehicle |
| Measurement Unit | What does my measurement mean? | Kilometers per hour |

---

## Example: Train Delays

**Project Goal:** Reduce the delay of trains.

### The Measurement Challenge

When is a train "delayed"? This is a point of discussion:

- When it's 1 minute late?
- When it's more than 3 minutes late?
- When it's more than 10 minutes late?
- When it has a late arrival but on-time departure?
- When it reaches the terminal late but was on-time at intermediate stations?

### The Dutch System's Operational Definition

> A train is delayed after **3 minutes at arrival** for a selection of stations throughout Holland.

| Element | Value |
|---------|-------|
| Variable (CTQ) | Delay time |
| Unit | An arrival (each arrival = one data point) |
| Measurement Unit | Minutes |

---

## What is an Operational Definition?

**An operational definition is the set of agreements on how to measure a variable and what the unit is.**

### Key Insight

> Is there one correct operational definition? **No.**

Operational definitions can be somewhat arbitrary (why 3 minutes and not 5?). The point is not to get a "correct" definition, but to get a **sensible** one that captures the perceived problem.

---

## Example: Contact Center First Time Fix Rate

**Goal:** Measure the percentage of calls an employee can handle without transferring the customer to another department.

### Data Collection

For each call, record: Yes (handled) or No (transferred)

But you want a **rate**—a percentage measured over a time period.

### Identifying the Elements

| Element | Value |
|---------|-------|
| Variable (CTQ) | First time fix rate |
| Unit | Per employee per day (or per employee per week) |
| Measurement Unit | Percentage of calls handled first time right |

---

## Alternative Terminology

Different fields use different names for these concepts.

### For "Unit"

| Alternative Term | Common In |
|------------------|-----------|
| Experimental unit | Research/experiments |
| Observational unit | Observational studies |
| Unit of analysis | Statistics |
| Case | General data analysis |
| Subject | Human subjects research |

### For "Measurement Unit"

Also called: **Unit of measurement**

---

## Summary

- **Units** are people, objects, or phenomena you collect data on
- **Measurement units** define what a measurement means
- **Operational definition** = agreements on how to measure a variable and what the unit is
- There is **never one correct** operational definition—look for the most **sensible** one that captures the perceived problem
