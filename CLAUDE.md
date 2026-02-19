# uber-polya

Universal problem-solving engine for Claude Code, implementing George Polya's "How to Solve It" methodology as modular skills.

## Project Structure

```
skills/
  uber-polya/     -- Orchestrator: chains the full pipeline
  uber-model/     -- Phase A: real-world problem → formal mathematical model
    references/   -- heuristics, structures, problem-classification, common-mistakes, model-templates
  uber-solve/     -- Phase B: formal model → verified solution
    references/   -- algorithms, solvers, algorithms-statistics, solvers-statistics, solving-protocols, optimization-hardening
  uber-interpret/ -- Phase C: solution → actionable insight
    references/   -- interpretation-patterns, visualization
examples/         -- Worked examples with solver code and visualizations
docs/             -- Architecture, tutorials, contributing guide
```

## How Skills Work

Each skill is a directory under `skills/` containing a `SKILL.md` and a `references/` folder. The `SKILL.md` is loaded when the user invokes `/skill-name`. Reference files are read on demand (not at invocation) to keep context overhead low.

## Conventions

### SKILL.md files
- YAML frontmatter with `name` and `description` (description contains trigger phrases)
- Structured phases with numbered steps
- Phase gates use `AskUserQuestion` for user confirmation
- Self-check lists after each gate
- Reference files are read via explicit `Read` tool calls at the specified phase
- Keep SKILL.md under 500 lines; move situational content to reference files

### Reference files
- Markdown format with consistent heading structure
- Each entry should be self-contained (definition, when to use, example)
- Use tables for quick-lookup content (algorithm selection, chart selection, pattern matching)
- Cross-reference other files by relative path when relevant

### Worked examples
- Each example gets its own directory under `examples/`
- Required files: `README.md`, solver script (Python), sample input/output
- Solver scripts use `dataclass` for `Instance` and `Solution`, with separate `solve()` and `verify()` functions
- Visualization scripts save to PNG (not committed to repo)

### Python code in examples and solvers
- Python 3.10+, type hints on all signatures
- `from __future__ import annotations` at top
- `dataclass(frozen=True)` for Instance, `dataclass` for Solution
- `time.perf_counter()` for timing
- Independent `verify()` function (must not share logic with solver)
- `#!/usr/bin/env python3` shebang and module docstring

## Adding a New Domain

1. Add algorithms to `skills/uber-solve/references/algorithms.md` (minimum 10 algorithms)
2. Add structures to `skills/uber-model/references/structures.md` (minimum 3 structures)
3. Add solver library entry to `skills/uber-solve/references/solvers.md` (if new library needed)
4. Add interpretation patterns to `skills/uber-interpret/references/interpretation-patterns.md`
5. Add at least 1 worked example under `examples/`
6. Update the classification table in `skills/uber-model/references/problem-classification.md`
7. Update `CHANGELOG.md`

## Testing

Skills are tested through conversation, not unit tests. To test a skill:
1. Invoke the skill with a known problem
2. Verify the output follows the phase structure
3. Verify reference files are read at the correct phase
4. Verify artifacts match the schemas defined in `skills/uber-polya/SKILL.md`
5. Verify the solver produces correct, verified output
6. Try edge cases: vague problems, trivial instances, infeasible instances

## Current State

- **v0.4.0**: Four skills (orchestrator + trilogy) with 139 algorithms (94 discrete/continuous + 45 statistical), 43 structures across 10 domains, 15 solver libraries. Three shipped domains: discrete math, continuous optimization, statistical inference. Model templates for top 5 patterns. Solving protocols and optimization hardening extracted to reference files. Cross-reference indexes in all reference files. Five worked examples.
- **Roadmap**: 11 expansion domains listed in README.md. Contributions welcome per CONTRIBUTING.md.
