# Trip Itinerary

## Problem

Plan a one-day city trip. You have 10 attractions, each with an enjoyment score,
visit duration (minutes), and entry cost ($). You have 8 hours (480 minutes) and
a $100 budget. Select the subset of attractions that maximizes total enjoyment
score without exceeding either budget. This is a variant of the 0/1 knapsack
problem with two capacity constraints (time and money).

## Files

| File | Description |
|------|-------------|
| `trip_solver.py` | 0/1 Knapsack ILP solver with dual constraints using PuLP/CBC |
| `solution.json` | Optimal solution output with selected attractions and totals |

## Requirements

```bash
pip install pulp
```

## Quick Run

```bash
python3 trip_solver.py
```

## Expected Output

- Optimal attraction selection maximizing total enjoyment under 8h and $100
- Budget utilization bars for both time and money
- Per-attraction efficiency analysis (enjoyment per hour and per dollar)
- Sensitivity analysis across budget variations
- Independent verification of all constraints

## Algorithm

0/1 Knapsack with two capacity constraints, formulated as Integer Linear
Programming via PuLP/CBC.

- **10 binary variables** (one per attraction: visit or skip)
- **2 capacity constraints** (total duration <= 480 min, total cost <= $100)
- Objective: maximize sum of enjoyment scores for selected attractions

## Key Concepts

- **Multi-dimensional knapsack** -- 0/1 knapsack generalized to two resource constraints
- **Integer Linear Programming** -- exact optimal solution via Branch & Bound
- **Binary selection** -- each attraction is either fully visited or skipped
- **Dual-budget trade-off** -- balancing time and money simultaneously
- **Sensitivity analysis** -- how the itinerary changes if time or money budgets shift
