# Project Prioritization (MCDA)

## Problem

Rank 8 software features by priority using 4 weighted criteria: user impact
(weight 0.4), development effort (0.25, lower is better), strategic alignment
(0.2), and revenue potential (0.15). Each feature is scored 1-10 on each
criterion. Produce a defensible priority ranking.

## Files

| File | Description |
|------|-------------|
| `priority_solver.py` | Multi-criteria decision analysis with weighted scoring |

## Requirements

```bash
pip install numpy
```

## Quick Run

```bash
python3 priority_solver.py
```

## Expected Output

- Ranked list of 8 features with composite scores
- Normalized score breakdown per criterion
- Sensitivity analysis: how rankings change if weights shift
- Independent verification of score computation

## Algorithm

Multi-Criteria Decision Analysis (MCDA) with weighted linear scoring.

- Normalize raw scores to [0, 1] range using min-max normalization
- Invert effort scores (lower effort is better)
- Apply criterion weights and compute weighted composite score
- Rank features by composite score

## Key Concepts

- **MCDA / weighted scoring** -- structured approach to multi-objective decisions
- **Score normalization** -- making heterogeneous criteria comparable
- **Criterion inversion** -- handling "lower is better" metrics
- **Sensitivity analysis** -- testing robustness of rankings to weight changes
- **Transparency** -- full breakdown of how each feature scored
