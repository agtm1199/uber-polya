# Workout Plan

## Domain

Discrete optimization / scheduling.

## Algorithm

Integer Linear Programming (ILP) via PuLP/CBC (Branch & Bound).

## Key Concepts

- **Binary decision variables** -- `x[exercise, day] = 1` if exercise is scheduled on that day
- **Muscle volume constraints** -- minimum weekly sets per muscle group modeled as linear inequalities
- **Session time limits** -- total duration per day capped at 60 minutes
- **Consecutive-day ban** -- `x[e, d] + x[e, d+1] <= 1` prevents the same exercise on back-to-back days
- **Time minimization** -- objective sums `duration_min * x[e, d]` over all exercise-day pairs

## Problem

Design a 5-day weekly workout plan selecting exercises from a catalog of 10 exercises.
Each exercise targets one or more muscle groups (chest, back, legs, shoulders, arms, core)
and has a known duration and set count.  The plan must:

1. Meet minimum weekly volume targets (total sets) for each of the six muscle groups.
2. Stay within a 60-minute time limit per session.
3. Never schedule the same exercise on two consecutive days.
4. Minimize total weekly workout time.

## Files

| File | Description |
|------|-------------|
| `workout_solver.py` | ILP solver using PuLP/CBC with independent constraint verification |
| `solution.json` | Sample solver output with schedule, objective, and verification results |
| `README.md` | This file |

## Requirements

```bash
pip install pulp
```

## Quick Run

```bash
python3 workout_solver.py
```

## Expected Output

- Optimal 5-day exercise schedule with per-day breakdown
- Total weekly workout time (minimized)
- Weekly muscle volume vs. targets (all PASS)
- Daily time-usage bars (all within 60-minute cap)
- Exercise frequency table
- Independent verification of all six constraint checks (all PASS)

## Algorithm

Integer Linear Programming (ILP) via PuLP/CBC.

- **50 binary variables** (10 exercises x 5 days)
- **Constraints**:
  - 6 muscle volume constraints (one per muscle group, `>= target`)
  - 5 session time-limit constraints (one per day, `<= 60 min`)
  - 40 consecutive-day constraints (10 exercises x 4 consecutive-day pairs)
- **Objective**: minimize `sum(duration[e] * x[e, d])` over all (exercise, day) pairs
- Solved via CBC Branch & Bound (exact optimal for this small instance)

## Key Concepts

- **Integer Linear Programming** -- optimizing a linear objective subject to linear constraints with integer (here binary) variables
- **Muscle volume** -- total weekly sets targeting a muscle group, summed across all exercise-day assignments
- **Consecutive-day constraint** -- for each exercise, the sum of its binary variables on any two adjacent days is at most 1
- **Session time budget** -- per-day sum of exercise durations must not exceed the time cap
- **Independent verification** -- a separate `verify()` function re-checks every constraint without reusing any solver logic
