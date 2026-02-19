# Shift Scheduling

## Problem

Schedule 8 nurses across 3 shifts (morning, afternoon, night) over 7 days.
Each shift needs at least 2 nurses. No nurse works more than 5 days total.
No nurse works the night shift on two consecutive days.

## Files

| File | Description |
|------|-------------|
| `shift_solver.py` | ILP solver using PuLP/CBC with constraint verification |

## Requirements

```bash
pip install pulp
```

## Quick Run

```bash
python3 shift_solver.py
```

## Expected Output

- Feasible schedule satisfying all staffing, workload, and consecutive-night constraints
- Total shifts assigned across all nurses
- Per-nurse workload breakdown
- Independent constraint verification (all PASS)

## Algorithm

Integer Linear Programming (ILP) via PuLP/CBC.

- **168 binary variables** (8 nurses x 7 days x 3 shifts)
- **Constraints**: minimum staffing per shift, max days per nurse, at most 1 shift per nurse per day, no consecutive night shifts
- Objective: maximize total shift coverage (equivalently, find a feasible schedule maximizing staffing)

## Key Concepts

- **Nurse scheduling as ILP** -- binary decision variables x[nurse, day, shift]
- **Temporal constraints** -- no consecutive night shifts modeled as pairwise constraints
- **Workload balancing** -- max days constraint ensures fair distribution
- **Independent verification** -- all constraints re-checked outside the solver
