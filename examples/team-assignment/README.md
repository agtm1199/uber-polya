# Team Assignment

## Problem

Assign 6 developers to 6 projects (one developer per project, one project per developer). Each developer has rated their interest in each project on a scale of 1-10. Find the assignment that maximizes total satisfaction across all developer-project pairs.

## Files

| File | Description |
|------|-------------|
| `team_solver.py` | Assignment problem solver using scipy's Hungarian algorithm |

## Requirements

```bash
pip install numpy scipy
```

## Quick Run

```bash
python3 team_solver.py
```

## Expected Output

- Optimal one-to-one assignment of developers to projects
- Maximum total satisfaction score
- Comparison against worst-case and random assignments

## Algorithm

Hungarian algorithm (Kuhn-Munkres) via `scipy.optimize.linear_sum_assignment`. Since the algorithm minimizes cost, we negate the preference matrix to convert maximization into minimization. The algorithm runs in O(n^3) and guarantees a globally optimal assignment.

## Key Concepts

- **Assignment problem** -- classic combinatorial optimization on bipartite graphs
- **Hungarian algorithm** -- exact polynomial-time solver for assignment problems
- **Cost matrix negation** -- converting maximization to minimization
- **Bipartite matching** -- one-to-one mapping between two disjoint sets
- **Optimality certificate** -- comparison with theoretical bounds
