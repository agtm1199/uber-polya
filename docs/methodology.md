# uber-polya Methodology

Universal problem-solving protocol implementing George Polya's "How to Solve It." This document is the tool-agnostic reference for any AI coding assistant. For Claude Code-specific skill invocation, see `skills/*/SKILL.md`.

## Pipeline

```
Problem → Phase A: Model → Phase B: Solve → Phase C: Interpret → Actionable Insight
```

## Modes

Determine the mode before starting:

| Mode | When | Phases |
|---|---|---|
| **Full Pipeline** (default) | User wants complete analysis | A → B → C |
| **Fast-Track** | Problem is already mathematically formulated | A (compressed) → B → C |
| **Stop-After-Model** | User says "just model this" | A only |
| **Stop-After-Solve** | User says "just get me the answer" | A → B only |

If unclear, ask the user which depth they want.

---

## Phase A: Model the Problem

**Goal**: Translate a real-world problem into a formal mathematical model.

**Reference files to consult** (paths relative to project root):
1. `skills/uber-model/references/problem-classification.md` -- read first for rapid pattern matching
2. `skills/uber-model/references/heuristics.md` -- Polya's 17 heuristics with Socratic questions
3. `skills/uber-model/references/structures.md` -- 91 mathematical structures across 24 domains
4. `skills/uber-model/references/model-templates.md` -- fill-in-the-blank templates for common patterns
5. `skills/uber-model/references/common-mistakes.md` -- pre-flight checklist (M1-M10), read before finalizing

### Steps

1. **Classify**: Is this a problem to *Find* (value, object, assignment) or to *Prove* (establish truth)?
2. **Understand**: Identify the unknown, the data, and the conditions. Break compound conditions into atomic statements. Introduce notation.
3. **Devise a plan**: Consult the reference files above. Match the problem to known mathematical structures. Propose 1-3 candidate models with trade-offs.
4. **Build formal model**: Construct the complete model with mapping table (real-world concept to mathematical object).
5. **Verify**: Test with a trivial case (n=1 or n=2). Check symmetry. Run the common-mistakes checklist.

### Formal Model Artifact

```
## Formal Model

**Problem Type**: Find / Prove
**Domain**: [Graph Theory / Combinatorics / Optimization / Probability / Statistics / ...]
**Named Problem**: [Classic name if applicable]

**Universe**:
  - [Set definitions]

**Variables**:
  - [symbol]: [meaning] [type/range]

**Structure**: [Core mathematical object and its definition]

**Mapping**:
  | Real-World Concept | Mathematical Object |
  |---|---|
  | ... | ... |

**Constraints**:
  1. [formal constraint] -- [origin: which real-world condition]

**Objective** (find): [Minimize/Maximize/Find/Count]: [formal expression]
**Claim** (prove): [formal statement]

**Suggested Approach**: [algorithm family]
**Complexity Class**: [P / NP-hard / ...]
**Available Tools**: [solver libraries]
```

### Phase A Gate

Present the model and ask the user to confirm before proceeding:
- Yes, proceed to solving
- Mostly correct, but needs adjustment
- No, let's remodel

### Self-Check

- [ ] Every data point maps to a mathematical object
- [ ] Every real-world condition appears as a constraint
- [ ] The unknown is captured in the objective/claim
- [ ] No constraint was added that isn't in the original problem
- [ ] The model passes a trivial-case test (n=1 or n=2)

---

## Phase B: Solve the Model

**Goal**: Select the right algorithm, implement a solver, verify the answer.

**Reference files to consult**:
1. `skills/uber-solve/references/algorithms.md` -- 195 algorithms (discrete, continuous, linear algebra, calculus, geometry, financial, game theory, decision analysis, multi-objective, ODEs, numerical methods, extended OR)
2. `skills/uber-solve/references/algorithms-statistics.md` -- 110 statistical algorithms (inference, time series, stochastic, survival, ML, simulation, queuing, causal)
3. `skills/uber-solve/references/solvers.md` -- 26 solver libraries (discrete/continuous)
4. `skills/uber-solve/references/solvers-statistics.md` -- statistical solver libraries
5. `skills/uber-solve/references/solving-protocols.md` -- domain-specific protocols (graph, ILP, SAT, counting, proof, DP, continuous optimization, statistical inference)
6. `skills/uber-solve/references/optimization-hardening.md` -- performance tuning (read only if needed)

### Steps

1. **Classify**: Map to a named computational problem (MST, shortest path, graph coloring, ILP, t-test, regression, etc.). The name unlocks the algorithm.
2. **Select algorithm**: Choose based on correctness guarantee, complexity, available libraries. Select a verification method and a fallback.
3. **Implement solver**: Write a complete, self-contained Python script (see Solver Conventions below).
4. **Execute and verify**: Run the solver. Independently verify all constraints. Produce an optimality certificate.
5. **Present the Solution Report**.

### Solution Report Artifact

```
## Solution Report

**Answer**: [the solution value / proof / count]
**Objective Value**: [for optimization]
**Optimal**: Yes / No / Unknown
**Feasible**: Yes (all [N] constraints verified) / No
**Algorithm**: [name] | O([complexity])
**Time**: [X.XXXXs]
**Certificate**: [optimality proof description]

### Solution Details
[The assignment, path, proof steps, count breakdown, etc.]

### Verification
[Independent check results -- every constraint checked]
```

### Phase B Gate

If verification passes, proceed. If it fails, debug and re-solve.

### Self-Check

- [ ] All constraints verified as SATISFIED
- [ ] Optimality certificate produced (or gap reported)
- [ ] Independent verification method used (not just trusting the solver)
- [ ] Edge cases handled (empty input, single element, disconnected components)
- [ ] Solution is reproducible (deterministic or seeded)

---

## Phase C: Interpret the Solution

**Goal**: Translate the formal solution back into real-world meaning, with sensitivity analysis and actionable recommendations.

**Reference files to consult**:
1. `skills/uber-interpret/references/interpretation-patterns.md` -- domain-specific translation patterns
2. `skills/uber-interpret/references/visualization.md` -- 37+ chart types with matplotlib templates

### Steps

1. **Recover context**: Reconstruct the mapping (math to real-world), identify the objective type, determine the audience (technical / decision-maker / domain expert / general).
2. **Translate**: Reverse the mapping for every solution element. State the bottom line in one sentence with no math jargon.
3. **Sensitivity analysis**: Vary 3-5 key parameters (+-10%, +-25%, +-50%). Classify each as robust, sensitive, or critical. Identify binding constraints. Run 2-3 what-if scenarios.
4. **Visualize**: Select 1-3 appropriate chart types. Generate Python matplotlib scripts with clear titles, labeled axes, annotations.
5. **Recommend**: Formulate specific, actionable recommendations. List key constraints to monitor, risk factors, quick wins, and limitations.
6. **Transfer knowledge**: Extract the reusable pattern ([real-world pattern] -> [structure] -> [algorithm]). Provide a decision framework for when to reuse this approach. Suggest a validation plan.

### Interpretation Report Artifact

```
## Interpretation Report

### The Question
[One sentence: what were we trying to find/prove/count?]

### The Answer
[One sentence: the bottom line result in real-world language]

### What This Means
[2-3 paragraphs translating the solution]

### How Robust Is This?
[Sensitivity summary with parameter classification: robust/sensitive/critical]

### Recommendations
[Actionable next steps]

### Limitations
[What the model doesn't capture]
```

### Self-Check

- [ ] Bottom line is stated in one clear sentence (no math jargon)
- [ ] Every mathematical object is mapped back to real-world meaning
- [ ] At least 3 parameters tested for sensitivity
- [ ] Recommendations are specific and actionable (not generic)
- [ ] Limitations are honestly disclosed
- [ ] Audience level is appropriate

---

## Python Solver Conventions

All solver scripts follow these standards:

```python
#!/usr/bin/env python3
"""[Problem name] solver. O([complexity]) time. [Correctness guarantee]."""
from __future__ import annotations
import time
from dataclasses import dataclass

@dataclass(frozen=True)
class Instance:
    """Problem instance -- immutable input data."""
    ...

@dataclass
class Solution:
    """Solution with metadata."""
    value: ...              # The answer
    objective: float | None # Objective value (optimization)
    is_optimal: bool        # Optimality proven?
    is_feasible: bool       # All constraints satisfied?
    algorithm: str          # Algorithm used
    time_seconds: float     # Wall-clock time
    certificate: str | None # Optimality certificate

def solve(instance: Instance) -> Solution:
    """Solve the instance."""
    t0 = time.perf_counter()
    # ... algorithm ...
    elapsed = time.perf_counter() - t0
    return Solution(...)

def verify(instance: Instance, solution) -> bool:
    """Independently verify feasibility. Must not share logic with solve()."""
    ...

if __name__ == "__main__":
    instance = Instance(...)
    sol = solve(instance)
    print(f"Solution: {sol.value}")
    print(f"Optimal: {sol.is_optimal}, Feasible: {sol.is_feasible}")
    print(f"Time: {sol.time_seconds:.4f}s")
```

**Requirements**: Python 3.10+, type hints on all signatures, `from __future__ import annotations`, `dataclass(frozen=True)` for Instance, `time.perf_counter()` for timing, separate `verify()` function independent of solver logic.

---

## Error Recovery

### Phase B fails (solver error, infeasible, timeout)
1. Check if the model is over-constrained -> loop back to Phase A
2. Check if the algorithm choice was wrong -> re-classify in Phase B
3. Check if the instance is too large -> switch to approximation

### Phase C reveals nonsensical results
1. The model may be missing a real-world constraint -> loop back to Phase A
2. The solution may be a degenerate edge case -> re-examine in Phase B
3. The audience may need a different framing -> adjust in Phase C

### User redirects mid-pipeline
- Acknowledge immediately
- Determine which phase the change affects
- Loop back to the earliest affected phase
- Preserve work from unaffected phases

---

## Fast-Track Protocol

When the problem is already mathematically formulated:

1. Skip Socratic dialogue. Consult `problem-classification.md`, match to a named problem class, build the Formal Model directly.
2. Present for confirmation only: "I recognize this as [named problem]. Here's the formal model. Shall I proceed?"
3. Proceed to Phase B upon confirmation.
4. Still run the common-mistakes checklist. Speed should not sacrifice correctness.

---

## Non-Interactive Mode

If operating in a non-interactive environment (no ability to ask the user questions):
- Use Full Pipeline mode by default
- At phase gates, proceed with best judgment and clearly note assumptions
- Present the solver script for the user to run manually if code execution is unavailable
- Include all three artifacts (Formal Model, Solution Report, Interpretation Report) in the final output

---

## Project Structure Quick Reference

```
skills/
  uber-model/references/     -- Modeling catalogs (structures, heuristics, templates)
  uber-solve/references/      -- Algorithm & solver catalogs (305 algorithms, 26 libraries)
  uber-interpret/references/  -- Interpretation patterns & visualization templates
examples/                     -- 36 worked examples with runnable Python solvers
docs/                         -- Architecture, tutorials, this methodology guide
```
