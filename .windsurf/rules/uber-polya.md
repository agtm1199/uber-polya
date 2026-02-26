# uber-polya Problem-Solving Protocol

Mathematical problem-solving engine implementing George Polya's "How to Solve It." Solves real-world problems through: **Model** (formalize) → **Solve** (implement & verify) → **Interpret** (translate to actionable insight).

## Full Protocol

See `docs/methodology.md` for complete instructions. Summary below.

## Pipeline

### Phase A -- Model the Problem

Translate real-world problem into formal math. Steps:
1. Classify: Find (value/object/assignment) or Prove (establish truth)
2. Understand: identify unknown, data, conditions (Socratic dialogue)
3. Devise plan: consult references, match to structures, propose candidates
4. Build formal model with mapping table (real-world ↔ math)
5. Verify: trivial case test, common-mistakes checklist

**Reference files**: `skills/uber-model/references/` -- problem-classification.md (first), heuristics.md, structures.md, common-mistakes.md (before finalizing)

**Artifact**: Formal Model (Domain, Universe, Variables, Structure, Mapping, Constraints, Objective/Claim)

**Gate**: Present model, ask user to confirm before proceeding.

### Phase B -- Solve the Model

Select algorithm, implement solver, verify. Steps:
1. Classify computational problem (map to named problem class)
2. Select algorithm from 305 cataloged (consult references)
3. Implement Python solver (Instance/Solution dataclasses, solve(), verify())
4. Execute and verify all constraints independently
5. Present Solution Report

**Reference files**: `skills/uber-solve/references/` -- algorithms.md, algorithms-statistics.md, solvers.md, solving-protocols.md

**Artifact**: Solution Report (Answer, Objective, Optimal, Feasible, Algorithm, Time, Certificate)

### Phase C -- Interpret the Solution

Translate back to real-world meaning. Steps:
1. Recover context: mapping, objective type, audience
2. Translate: reverse mapping, one-sentence bottom line
3. Sensitivity: vary 3-5 key parameters, classify robust/sensitive/critical
4. Visualize: 1-3 charts with matplotlib
5. Recommend: actionable advice adapted to audience
6. Knowledge transfer: extract reusable patterns

**Reference files**: `skills/uber-interpret/references/` -- interpretation-patterns.md, visualization.md

**Artifact**: Interpretation Report (Question, Answer, Meaning, Robustness, Recommendations, Limitations)

## Output Format

The pipeline supports three output formats (ask the user before starting):
- **Python** (default): solver script + console output + JSON
- **LaTeX/PDF**: professional mathematical report (`.tex` + `.pdf`), no code shown
- **Both**: full Python output AND compiled PDF report

PDF generation uses fpdf2 + matplotlib (no system LaTeX needed). See `utils/latex_renderer.py` and `templates/latex/`.

## Error Recovery

- Phase B fails → check if model is over-constrained (loop to A) or algorithm wrong (re-classify in B)
- Phase C reveals nonsense → model may be missing a constraint (loop to A)
- User redirects → loop back to earliest affected phase, preserve unaffected work
