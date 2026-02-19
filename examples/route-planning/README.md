# Route Planning (TSP)

## Problem

A delivery driver must visit 8 locations in a city and return to the warehouse.
Given distances between all pairs of locations, find the shortest possible route
that visits every location exactly once and returns to the starting point.

## Files

| File | Description |
|------|-------------|
| `route_solver.py` | Exact TSP solver using Held-Karp dynamic programming |

## Requirements

```bash
pip install numpy
```

## Quick Run

```bash
python3 route_solver.py
```

## Expected Output

- Optimal tour visiting all 9 locations (warehouse + 8 stops)
- Total tour distance
- Step-by-step route with individual leg distances
- Comparison with nearest-neighbor heuristic
- Independent verification of tour validity and distance

## Algorithm

Held-Karp dynamic programming for exact TSP solution.

- **Time complexity**: O(n^2 * 2^n) -- feasible for n=9
- **Space complexity**: O(n * 2^n)
- Guaranteed optimal solution (exact algorithm)
- Compared against nearest-neighbor greedy heuristic for context

## Key Concepts

- **Traveling Salesman Problem (TSP)** -- classic NP-hard combinatorial optimization
- **Held-Karp DP** -- exact algorithm using bitmask dynamic programming
- **Nearest-neighbor heuristic** -- greedy baseline for comparison
- **Tour verification** -- independent check that solution visits all cities exactly once
