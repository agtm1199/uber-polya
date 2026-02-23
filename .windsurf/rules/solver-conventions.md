# Python Solver Conventions

Standards for uber-polya solver scripts in `examples/`.

## Required Structure

```python
#!/usr/bin/env python3
"""[Problem] solver. O([complexity]). [Correctness guarantee]."""
from __future__ import annotations
import time
from dataclasses import dataclass

@dataclass(frozen=True)
class Instance:
    """Immutable problem instance."""
    ...

@dataclass
class Solution:
    """Solution with metadata."""
    value: ...
    objective: float | None
    is_optimal: bool
    is_feasible: bool
    algorithm: str
    time_seconds: float
    certificate: str | None

def solve(instance: Instance) -> Solution:
    t0 = time.perf_counter()
    # ... algorithm ...
    elapsed = time.perf_counter() - t0
    return Solution(...)

def verify(instance: Instance, solution) -> bool:
    """Independent verification. Must NOT share logic with solve()."""
    ...
```

## Rules

- Python 3.10+, type hints on all signatures
- `from __future__ import annotations` at top
- `@dataclass(frozen=True)` for Instance
- `time.perf_counter()` for timing
- `solve()` and `verify()` are separate, no shared logic
- Deterministic output (seed RNG if randomized)
- Handle edge cases: n=0, n=1, disconnected, infeasible, unbounded
