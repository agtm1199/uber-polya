# uber-polya

This project is a mathematical problem-solving engine implementing George Polya's "How to Solve It" methodology. It solves real-world problems through a three-phase pipeline: **Model** (formalize the problem), **Solve** (implement and verify), **Interpret** (translate to actionable insight).

## When a User Presents a Problem

Follow the full protocol in `docs/methodology.md` and `AGENTS.md`.

### Pipeline Summary

1. **Phase A -- Model**: Classify the problem (Find vs. Prove). Consult `skills/uber-model/references/` for pattern matching against 91 mathematical structures. Build a formal model with a real-world-to-math mapping table.
2. **Phase B -- Solve**: Select an algorithm from the 305 cataloged in `skills/uber-solve/references/`. Implement a Python solver with `Instance`/`Solution` dataclasses, `solve()`, and `verify()` functions. Verify independently.
3. **Phase C -- Interpret**: Consult `skills/uber-interpret/references/`. Reverse the mapping. Run sensitivity analysis. Generate visualizations. Provide actionable recommendations.

### Key Convention

Ask the user to confirm at each phase gate before proceeding to the next phase.

### Python Code

Solvers use Python 3.10+, `dataclass(frozen=True)` for Instance, separate `verify()` function, `time.perf_counter()` for timing, type hints on all signatures. See `docs/methodology.md` for the full template.

### Output Format

The pipeline supports three output formats (ask the user before starting):
- **Python** (default): solver script + console output + JSON
- **LaTeX/PDF**: professional mathematical report (`.tex` + `.pdf`), no code shown
- **Both**: full Python output AND compiled PDF report

PDF generation uses fpdf2 + matplotlib (no system LaTeX needed). See `utils/latex_renderer.py` and `templates/latex/`.

### Worked Examples

See `examples/` for 36 fully worked problems with runnable solver scripts.
