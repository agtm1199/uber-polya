## Summary of Changes

Describe what this PR does and why. Link any related issues (e.g., `Fixes #123`).

## Type of Change

- [ ] Bug fix (corrects wrong results or unexpected behavior)
- [ ] New feature (adds new algorithm, solver, or capability)
- [ ] New domain (adds a complete new problem domain with algorithms, structures, and patterns)
- [ ] New example (adds a worked example under `examples/`)
- [ ] Documentation (updates docs, SKILL.md files, or reference files)
- [ ] Other (describe below)

## Testing

Describe how you tested your changes:

- **Problem tested**:
- **Skill invoked**: (e.g., `/uber-polya`, `/uber-model`, `/uber-solve`, `/uber-interpret`)
- **Result**:
- **Edge cases checked**:

## Checklist

- [ ] Code follows the project conventions in `CLAUDE.md`
- [ ] `verify()` function is independent and does not share logic with the solver
- [ ] New examples include a `README.md` with problem statement, model, solution summary, and run instructions
- [ ] Solver scripts use `dataclass(frozen=True)` for `Instance`, `dataclass` for `Solution`, type hints, and `time.perf_counter()`
- [ ] Reference files added to the correct `references/` directory with consistent heading structure
- [ ] `CHANGELOG.md` updated with a summary of changes
- [ ] No generated files (PNGs, `__pycache__`, `.pyc`) are included in the commit
