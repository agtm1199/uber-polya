# Potluck Planning

## Problem

Assign 8 guests to 5 dish categories (appetizer, salad, main, side, dessert) for a potluck dinner. Each guest rates their effort/skill for each category on a 1-5 scale (lower = easier for them). Every category must be covered by at least 1 guest and at most 2 guests. Minimize total effort across all assignments.

## Files

| File | Description |
|------|-------------|
| `potluck_solver.py` | ILP solver using PuLP/CBC with coverage constraints |

## Requirements

```bash
pip install pulp
```

## Quick Run

```bash
python3 potluck_solver.py
```

## Expected Output

- Optimal assignment of guests to dish categories minimizing total effort
- All 5 categories covered (some by 2 guests since 8 > 5)
- Independent constraint verification (all PASS)
- Comparison against theoretical bounds and random assignment

## Algorithm

Integer Linear Programming (ILP) via PuLP/CBC.

- **40 binary variables** (8 guests x 5 categories)
- **Constraints**: one category per guest, min/max coverage per category
- Objective: minimize sum of effort scores across all guest-category assignments

## Key Concepts

- **Generalized assignment problem** -- many-to-one mapping with coverage constraints
- **ILP formulation** -- binary decision variables with linear constraints
- **Coverage constraints** -- every category must have at least 1 contributor, at most 2
- **Independent verification** -- 6 checks: guest assignment, category validity, min/max coverage, effort recomputation, guest count
- **Sensitivity analysis** -- impact of each guest dropping out
