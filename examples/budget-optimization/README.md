# Budget Optimization

## Problem

A startup has a $500K budget and 10 candidate projects. Each project has a fixed
cost and an expected ROI score. Select the subset of projects that maximizes
total ROI without exceeding the budget.

## Files

| File | Description |
|------|-------------|
| `budget_solver.py` | 0/1 Knapsack ILP solver using PuLP/CBC |

## Requirements

```bash
pip install pulp
```

## Quick Run

```bash
python3 budget_solver.py
```

## Expected Output

- Optimal project selection maximizing total ROI score under $500K budget
- Budget utilization percentage
- Per-project selection table
- Independent verification of budget and selection constraints

## Algorithm

0/1 Knapsack formulated as Integer Linear Programming via PuLP/CBC.

- **10 binary variables** (one per project: selected or not)
- **1 budget constraint** (total cost <= $500K)
- Objective: maximize sum of ROI scores for selected projects

## Key Concepts

- **0/1 Knapsack as ILP** -- classic combinatorial optimization with binary selection
- **Budget-constrained selection** -- real-world resource allocation under constraints
- **ROI-driven prioritization** -- scoring and ranking candidate investments
- **Sensitivity analysis** -- effect of budget changes on optimal selection
