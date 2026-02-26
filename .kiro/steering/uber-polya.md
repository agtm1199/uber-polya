---
inclusion: always
name: uber-polya
description: Polya-method problem-solving pipeline (Model → Solve → Interpret)
---

# uber-polya Problem-Solving Protocol

Mathematical problem-solving engine implementing George Polya's "How to Solve It." Solves real-world problems through a three-phase pipeline: **Model** → **Solve** → **Interpret**.

## Full Protocol

See `docs/methodology.md` for complete step-by-step instructions.

## Pipeline Summary

### Phase A -- Model

Translate real-world problem into formal math using Socratic dialogue.
- Classify: Find vs. Prove
- Match to known structures (91 across 24 domains)
- Build formal model with real-world-to-math mapping
- **References**: `skills/uber-model/references/` (problem-classification.md first, then heuristics.md, structures.md, common-mistakes.md)
- **Gate**: Present model, confirm with user before proceeding

### Phase B -- Solve

Select algorithm, implement and verify.
- Classify computational problem, select from 305 algorithms
- Implement Python solver (Instance/Solution dataclasses, solve(), verify())
- Verify all constraints independently
- **References**: `skills/uber-solve/references/` (algorithms.md, solvers.md, solving-protocols.md)

### Phase C -- Interpret

Translate solution to actionable insight.
- Reverse mapping, one-sentence bottom line
- Sensitivity analysis (3-5 parameters, classify robust/sensitive/critical)
- Visualizations (matplotlib), recommendations, knowledge transfer
- **References**: `skills/uber-interpret/references/` (interpretation-patterns.md, visualization.md)

## Artifacts

- **Formal Model**: Domain, Universe, Variables, Structure, Mapping, Constraints, Objective/Claim
- **Solution Report**: Answer, Objective Value, Optimal, Feasible, Algorithm, Time, Certificate
- **Interpretation Report**: Question, Answer, Meaning, Robustness, Recommendations, Limitations

## Output Format

Three formats available (ask user before starting):
- **Python** (default): solver script + console output + JSON
- **LaTeX/PDF**: professional mathematical report (`.tex` + `.pdf`), no code shown
- **Both**: full Python output AND compiled PDF report

PDF uses fpdf2 + matplotlib (no system LaTeX needed). See `utils/latex_renderer.py` and `templates/latex/`.

## Worked Examples

36 examples in `examples/` with runnable Python solvers.
