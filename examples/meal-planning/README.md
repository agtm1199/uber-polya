# Meal Planning

## Problem

Plan 7 days of dinners minimizing total grocery cost while meeting weekly nutrition targets: at least 350g protein, at most 14000 calories, and at least 140g fiber. Choose from 10 meals, each with known cost, calories, protein, and fiber per serving. Each meal can be served between 0 and 7 times during the week.

## Files

| File | Description |
|------|-------------|
| `meal_solver.py` | Integer linear programming solver using PuLP for cost-minimized meal planning |

## Requirements

```bash
pip install pulp
```

## Quick Run

```bash
python3 meal_solver.py
```

## Expected Output

- Optimal weekly meal plan with 7 total servings
- Minimum grocery cost while satisfying all nutrition constraints
- Detailed nutrition breakdown per meal and weekly totals

## Algorithm

Integer Linear Programming (ILP) via PuLP/CBC. Decision variables are integer counts of how many times each meal is served (0-7). The objective minimizes total cost. Constraints enforce: exactly 7 total meals, minimum 350g protein, maximum 14000 calories, minimum 140g fiber.

## Key Concepts

- **Linear programming** -- optimizing a linear objective subject to linear constraints
- **Integer variables** -- meal counts must be whole numbers
- **Nutritional constraints** -- modeling dietary requirements as linear inequalities
- **Cost minimization** -- finding the cheapest feasible diet
- **Sensitivity analysis** -- how the plan changes if budgets or requirements shift
