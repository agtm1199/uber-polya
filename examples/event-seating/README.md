# Event Seating

## Problem

Seat 12 wedding guests at 3 tables (4 guests each). Some pairs must sit together (couples). Some pairs must not sit together (feuding relatives). Maximize the total "affinity" score across all tables, where affinity measures how well pairs of guests get along.

## Files

| File | Description |
|------|-------------|
| `seating_solver.py` | Constrained partitioning solver using Integer Linear Programming (PuLP/CBC) |

## Requirements

```bash
pip install pulp numpy
```

## Quick Run

```bash
python3 seating_solver.py
```

## Expected Output

- Optimal seating arrangement for 3 tables of 4 guests each
- All must-sit-together constraints satisfied (couples at same table)
- All must-not-sit-together constraints satisfied (feuding pairs separated)
- Maximum total affinity score

## Algorithm

Integer Linear Programming (ILP) via PuLP/CBC. Binary decision variables x[g,t] indicate whether guest g sits at table t. The objective maximizes the sum of pairwise affinity scores for guests seated at the same table. Constraints enforce: each guest at exactly one table, table capacity of 4, must-sit-together pairs at the same table, must-not-sit-together pairs at different tables.

## Key Concepts

- **Constrained partitioning** -- dividing a set into groups subject to constraints
- **Integer linear programming** -- binary decision variables with linear constraints
- **Pairwise affinity modeling** -- encoding social preferences as an objective function
- **Hard constraints vs soft objectives** -- mandatory seating rules vs preference optimization
- **Linearization of quadratic terms** -- modeling "both at same table" with auxiliary variables
