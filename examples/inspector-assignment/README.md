# Inspector Assignment

## Problem

Assign 6 food safety inspectors to 10 facilities (5 types x 2 each) to
maximize total expertise score. Each inspector handles at most 3 facilities;
each facility needs exactly 1 inspector.

## Files

| File | Description |
|------|-------------|
| `inspector_solver.py` | ILP solver using PuLP/CBC + sensitivity analysis |
| `inspector_viz.py` | Generates 3 stakeholder visualizations |
| `solution.json` | Optimal solution data |

## Requirements

```bash
pip install pulp matplotlib numpy
```

## Quick Run

```bash
python3 inspector_solver.py   # Solve with PuLP/CBC
python3 inspector_viz.py      # Generate 3 stakeholder visualizations
```

## Expected Output

- **Optimal score**: 90/90 (100% efficiency)
- Each facility assigned to its top expert
- 0% optimality gap

## Algorithm

Integer Linear Programming via PuLP/CBC.

- **60 binary variables** (6 inspectors x 10 facilities)
- **16 constraints** (10 facility-coverage + 6 inspector-capacity)
- The LP relaxation is integral (totally unimodular constraint matrix),
  so LP optimal = ILP optimal.

## Key Concepts

- **Bipartite matching as ILP** -- assignment problem formulated with binary decision variables
- **LP relaxation bounds** -- LP solution provides a certificate of optimality for the ILP
- **Sensitivity analysis** -- what-if scenarios for each inspector leaving the team
- **Stakeholder visualization** -- expertise heatmap, tornado chart (impact analysis), workload distribution

## Full Tutorial

See [docs/tutorials/inspector-assignment-walkthrough.md](../../docs/tutorials/inspector-assignment-walkthrough.md)
for a detailed step-by-step walkthrough.
