---
name: New Worked Example
about: Submit a new worked example for the examples/ directory
title: "[EXAMPLE] "
labels: example
assignees: ''
---

## Problem Description

State the problem clearly, including all inputs, constraints, and what the solution should produce.

## Domain

Which domain does this example belong to? (e.g., discrete math, continuous optimization, game theory, survival analysis)

## Algorithm Used

Which algorithm(s) does the solver use? Reference entries from `skills/uber-solve/references/algorithms.md` if applicable.

## Python Dependencies

List all required Python packages beyond the standard library:

-
-

## Checklist

Before submitting, ensure your example includes:

- [ ] `README.md` with problem statement, model formulation, solution summary, and how-to-run instructions
- [ ] Solver script (`solve_*.py`) with `Instance` and `Solution` dataclasses, `solve()` function, and `__main__` block
- [ ] Independent `verify()` function that does not share logic with the solver
- [ ] Sample output showing the solution and verification result
- [ ] `from __future__ import annotations` and type hints on all signatures
- [ ] `dataclass(frozen=True)` for `Instance`, `dataclass` for `Solution`
- [ ] `time.perf_counter()` for timing
- [ ] `#!/usr/bin/env python3` shebang and module docstring

## Additional Notes

Any extra context, edge cases tested, or visualization details.
