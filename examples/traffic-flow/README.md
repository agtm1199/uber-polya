# Traffic Flow Analysis

## Problem

A city has 4 intersections (A, B, C, D) connected by one-way streets forming
a loop with one diagonal cross street. Traffic flow counts are known at
external entry/exit points (balanced: 800 in = 800 out):

- 500 cars/hour enter intersection A from the north
- 600 cars/hour exit intersection B to the east
- 300 cars/hour enter intersection C from the south
- 200 cars/hour exit intersection D to the west

Internal road segments carry unknown flows x1..x5:

- x1: A -> B
- x2: B -> C
- x3: C -> D
- x4: D -> A
- x5: A -> C (diagonal)

A traffic sensor on the B -> C road measures x2 = 200 cars/hour.

Find the flow on each internal road segment using conservation of flow
(flow in = flow out) at every intersection, combined with the sensor reading.

## Files

| File | Description |
|------|-------------|
| `traffic_solver.py` | Linear algebra solver using numpy with rank/null-space analysis |

## Requirements

```bash
pip install numpy
```

## Quick Run

```bash
python3 traffic_solver.py
```

## Expected Output

- Rank of the coefficient matrix and null space dimension
- A particular (minimum-norm) solution via least squares
- Null space basis vector describing the family of all solutions
- Independent verification that conservation holds at every intersection
- Interpretation of the underdetermined system (one free parameter)

## Algorithm

Gaussian elimination / `numpy.linalg.lstsq` for the underdetermined linear system.

- **5 unknowns** (internal road flows x1..x5)
- **5 equations** (4 flow conservation + 1 sensor reading)
- **Rank 4, nullity 1** -- the system has a one-dimensional family of solutions
- The minimum-norm particular solution is returned, along with the null space basis vector

## Key Concepts

- **Linear systems from network flow** -- conservation of flow yields Ax = b
- **Underdetermined systems** -- more unknowns than independent equations (rank < n)
- **Rank analysis** -- rank and nullity reveal degrees of freedom
- **Null space** -- basis vectors describe the family of all solutions
- **Least-squares / minimum-norm** -- lstsq returns the smallest-norm solution when infinitely many exist
- **Independent verification** -- flow conservation re-checked outside the solver
