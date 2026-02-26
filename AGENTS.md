# uber-polya

Universal problem-solving engine implementing George Polya's "How to Solve It" methodology. Turns real-world problems into mathematically verified solutions with actionable insights.

## What This Does

uber-polya solves problems through a three-phase pipeline:

1. **Model** (Phase A): Translate the real-world problem into a formal mathematical model using Socratic dialogue, 91 mathematical structures, and 17 Polya heuristics.
2. **Solve** (Phase B): Select the right algorithm from 305 cataloged algorithms, implement a verified Python solver, and prove correctness.
3. **Interpret** (Phase C): Translate the solution back into real-world meaning with sensitivity analysis, visualizations, and actionable recommendations.

## How to Use

When a user presents a problem to solve, follow the full protocol in `docs/methodology.md`. That document contains:

- Step-by-step instructions for each phase
- Structured artifact schemas (Formal Model, Solution Report, Interpretation Report)
- Reference file paths and when to consult them
- Self-checks, error recovery, and fast-track shortcuts
- Python solver coding conventions

### Quick Start

1. Classify the problem: Is it a problem to *Find* or to *Prove*?
2. Consult `skills/uber-model/references/problem-classification.md` for rapid pattern matching
3. Follow Phase A → Phase B → Phase C as documented in `docs/methodology.md`
4. At each phase gate, present your work and ask the user to confirm before proceeding

## Project Structure

```
skills/
  uber-polya/               Orchestrator: chains the full pipeline
  uber-model/               Phase A: real-world problem → formal model
    references/             Heuristics, structures, problem classification, common mistakes
  uber-solve/               Phase B: formal model → verified solution
    references/             305 algorithms, 26 solver libraries, solving protocols
  uber-interpret/           Phase C: solution → actionable insight
    references/             Interpretation patterns, 37+ visualization templates
templates/
  latex/                    Jinja2 LaTeX templates + polya.sty for PDF reports
examples/                   36 worked examples with runnable Python solvers
docs/
  methodology.md            Full tool-agnostic protocol (start here)
  architecture.md           System design and expansion patterns
  creating-skills.md        How to build custom skills
```

## Reference Files

Consult these on demand (not all at once) at the phases specified:

| File | Phase | Purpose |
|---|---|---|
| `skills/uber-model/references/problem-classification.md` | A (start) | Rapid pattern matching via decision tree |
| `skills/uber-model/references/heuristics.md` | A | Polya's 17 Socratic heuristics |
| `skills/uber-model/references/structures.md` | A | 91 mathematical structures with indicators |
| `skills/uber-model/references/model-templates.md` | A | Fill-in-the-blank model templates |
| `skills/uber-model/references/common-mistakes.md` | A (end) | Pre-flight checklist (M1-M10) |
| `skills/uber-solve/references/algorithms.md` | B | 195 discrete/continuous algorithms |
| `skills/uber-solve/references/algorithms-statistics.md` | B | 110 statistical/ML algorithms |
| `skills/uber-solve/references/solvers.md` | B | 26 solver library guides |
| `skills/uber-solve/references/solvers-statistics.md` | B | Statistical solver libraries |
| `skills/uber-solve/references/solving-protocols.md` | B | Domain-specific solving protocols |
| `skills/uber-interpret/references/interpretation-patterns.md` | C | Domain translation patterns |
| `skills/uber-interpret/references/visualization.md` | C | Chart selection and matplotlib templates |

## Python Solver Conventions

Solvers must be complete, self-contained Python 3.10+ scripts:

- `from __future__ import annotations` at top
- `@dataclass(frozen=True)` for `Instance`, `@dataclass` for `Solution`
- Separate `solve()` and `verify()` functions (verify must not share logic with solver)
- `time.perf_counter()` for timing
- Type hints on all function signatures
- Deterministic output (seed RNG if randomized)

See `docs/methodology.md` for the full template.

## Output Format

The pipeline supports three output formats (ask the user before starting):
- **Python** (default): solver script + console output + JSON
- **LaTeX/PDF**: professional mathematical report (`.tex` + `.pdf`), no code shown
- **Both**: full Python output AND compiled PDF report

PDF generation uses `fpdf2` + `matplotlib` (no system LaTeX needed). See `utils/latex_renderer.py` and `templates/latex/`.

## Worked Examples

The `examples/` directory contains 36 fully worked problems with runnable code, covering: discrete math, continuous optimization, statistical inference, time series, survival analysis, machine learning, simulation, causal inference, numerical methods, and operations research.

## Domains Covered (24)

Discrete Math, Continuous Optimization, Statistical Inference, Linear Algebra, Calculus, Geometry & Trigonometry, Financial Mathematics, Game Theory, Decision Analysis, Multi-Objective Optimization, Time Series, Stochastic Processes, Survival Analysis, Machine Learning, Simulation & ODEs, Numerical Methods, Causal Inference, Extended Operations Research.
