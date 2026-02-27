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
templates/
  latex/          -- Jinja2 LaTeX templates + polya.sty style for PDF reports
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

### LaTeX/PDF output
- Output format (Python / LaTeX-PDF / Both) is selected at the start of `/uber-polya`
- LaTeX source generated via Jinja2 templates in `templates/latex/` using custom delimiters (`\VAR{}`, `\BLOCK{}`)
- PDF compiled via `fpdf2` + `matplotlib.mathtext` (no system LaTeX installation required)
- Data flows through `utils/latex_data.py` dataclasses (`FormalModel`, `SolutionReport`, `InterpretationReport`)
- Rendering handled by `utils/latex_renderer.py` (`LatexRenderer` class)
- `utils/render_example.py` can generate reports from any existing example's `solution.json`
- Custom style `templates/latex/polya.sty` provides branded environments and colors

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

## Cross-Tool Compatibility

`docs/methodology.md` is the tool-agnostic version of the Polya protocol. It contains the same pipeline, artifacts, and self-checks as the SKILL.md files but uses generic language instead of Claude Code tool names. Other AI tools (Codex, Copilot, Cursor, Windsurf, Kiro) reference it through their native config files (`AGENTS.md`, `.github/copilot-instructions.md`, `.cursor/rules/`, `.windsurf/rules/`, `.kiro/steering/`).

## Current State

- **v1.2.0**: Research-level mathematics expansion. Eight new domain sections in structures.md (25-32): abstract algebra & representation theory, algebraic combinatorics, stochastic analysis & SPDEs, algebraic topology, symplectic & differential geometry, advanced spectral theory, tensor analysis, RKHS & Krylov spaces. Eight new algorithm sections (34-41, A196-A230): 35 new algorithms covering representation theory, algebraic combinatorics, SPDEs/regularity structures, algebraic topology, symplectic geometry, advanced spectral graph theory, tensor decomposition, advanced numerical linear algebra. Four new solver entries (§15-§18): SageMath, GAP, tensorly, scipy.sparse.linalg. Seven new interpretation pattern sections (22-28). Total: ~340 algorithms, ~116 structures across 32 domains, 30 solver libraries. Twenty-six shipped domains.
- **v1.1.0**: LaTeX/PDF output support. Three output modes (Python / LaTeX-PDF / Both) selectable at invocation. Jinja2 templates in `templates/latex/`, pure-Python PDF generation via fpdf2 + matplotlib (no system LaTeX needed). New utilities: `utils/latex_data.py`, `utils/latex_renderer.py`, `utils/render_example.py`. New dependencies: Jinja2, fpdf2.
- **v1.0.0**: Four skills (orchestrator + trilogy) with 305 algorithms (195 discrete/continuous/linear-algebra/calculus/geometry/financial/game-theory/decision-analysis/multi-objective/ODEs/numerical-methods/extended-OR + 110 statistical/time-series/stochastic/survival/ML/simulation/queuing/causal), 91 structures across 24 domains, 26 solver libraries. Eighteen shipped domains: discrete math, continuous optimization, statistical inference, time series analysis, stochastic processes, survival analysis, linear algebra, calculus, geometry & trigonometry, financial mathematics, game theory, decision analysis, multi-objective optimization, machine learning, simulation & ODEs, numerical methods, causal inference, extended operations research. All high-relevance mathematical branches covered. Thirty-six worked examples.
- **Roadmap**: Expansion domains listed in README.md. Contributions welcome per CONTRIBUTING.md.
