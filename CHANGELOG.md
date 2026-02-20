# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.4.0] - 2026-02-18

### Added

- **Continuous optimization domain** seeded end-to-end:
  - 5 new structures in structures.md (§9: unconstrained opt, convex program, QP, least squares, nonlinear constrained)
  - 8 new algorithms in algorithms.md (A87-A94: cvxpy DCP, QP, BFGS, gradient descent, least squares, Gauss-Newton, SQP, interior point)
  - cvxpy solver reference in solvers.md (§9)
  - 3 new interpretation patterns (§7: convex opt, least squares, nonlinear opt)
  - Continuous optimization entries in problem-classification.md decision tree and pattern table
- `references/model-templates.md` -- fill-in-the-blank formal model templates for 5 common patterns (assignment, scheduling, routing, selection, dependency ordering)
- `references/solving-protocols.md` -- 8 domain-specific solving workflows (graph, ILP/LP, SAT/SMT, counting, proof, number theory, DP, continuous optimization)
- `references/optimization-hardening.md` -- Phase 4 performance tuning and production hardening guide (extracted from uber-solve SKILL.md)
- **Portfolio Optimization** worked example (examples/portfolio-optimization/) -- Markowitz QP with cvxpy, efficient frontier, visualization
- **Tournament Hamiltonian Path** worked example (examples/tournament-hamiltonian/) -- proof by induction with Z3 verification
- **Statistical inference domain** seeded end-to-end:
  - 6 new structures in structures.md (§10: random variable, hypothesis, regression, Bayesian, sample/population, experimental design)
  - 45 algorithms in algorithms-statistics.md (hypothesis tests, regression, Bayesian methods, estimation, resampling)
  - 6 solver libraries in solvers-statistics.md (scipy.stats, statsmodels, scikit-learn, PyMC, pingouin, lifelines)
  - 4 new interpretation patterns (§8: hypothesis tests, regression, CI/CrI, Bayesian posterior)
  - 6 new chart types in visualization.md (§11-§16: group comparison, QQ plot, regression, residual, forest, posterior)
- **A/B Testing** worked example (examples/ab-testing/) -- z-test, Bayesian, bootstrap, power analysis
- **Cafe Tips** worked example (examples/cafe-tips/) -- full Polya cycle demo: t-test, Mann-Whitney, permutation, bootstrap, Bayesian, power analysis, visualizations
- **10 Everyday Problem** worked examples: shift-scheduling, budget-optimization, fair-rent, route-planning, project-prioritization, study-schedule, meal-planning, team-assignment, break-even, event-seating
- Cross-reference indexes in all reference files linking structures → algorithms → solvers → interpretation → visualization

### Changed

- uber-model now references 5 files (added model-templates.md); scope updated to include statistical inference
- uber-solve SKILL.md slimmed: extracted Phase 4 and protocols into reference files (~140 lines → 2-line read-on-demand)
- uber-solve now references 6 files (added solving-protocols.md, optimization-hardening.md, algorithms-statistics.md, solvers-statistics.md)
- All reference files now carry **Scope** tags for multi-domain awareness
- heuristics.md and structures.md titles updated from "Discrete Math" to "Mathematical" (universal branding)
- Updated README: 139 algorithms, 15 solver libraries, 43 structures, 10 domains, 16 examples

## [0.3.0] - 2026-02-18

### Added

- `/uber-polya` orchestrator skill -- chains Model → Solve → Interpret as a single invocation
  - Full pipeline, fast-track, stop-after-model, and stop-after-solve modes
  - Structured artifact schemas (Formal Model, Solution Report, Interpretation Report)
- `CLAUDE.md` project-level instructions for Claude Code
- `references/common-mistakes.md` -- 16 anti-patterns across modeling (M1-M10), solving (S1-S6), and interpretation (I1-I6)
- `references/problem-classification.md` -- decision tree and quick-lookup table for rapid problem classification
- Self-evaluation checklists after every phase gate in all three skills

### Changed

- uber-model now references 4 reference files (added problem-classification.md and common-mistakes.md)
- Updated install.sh to include uber-polya orchestrator
- Updated README with orchestrator documentation and expanded reference catalog table

## [0.2.0] - 2026-02-18

### Changed

- Rebranded from dm-polya to **uber-polya** -- universal problem-solving framework
- Renamed skills: dm-model → uber-model, dm-solve → uber-solve, dm-interpret → uber-interpret
- Reframed documentation from "discrete mathematics" to universal scope with modular expansion
- Updated all SKILL.md titles, descriptions, and trigger phrases for universal coverage
- Added expansion roadmap (11 planned domains) to README
- Added "Why Start With Discrete Mathematics?" and "Expansion Architecture" to architecture docs
- Added "Contribute a New Domain" guide to CONTRIBUTING.md

## [0.1.0] - 2026-02-18

### Added

- `/uber-model` skill: Socratic modeling guide with 4 Polya phases
  - 17 Polya heuristics adapted for discrete mathematics
  - 32 DM structures across 8 domains with real-world pattern matching
- `/uber-solve` skill: Algorithm selection and verified solver engineering
  - 85+ algorithms with complexity, solver libraries, and implementation patterns
  - Python solver ecosystem guide (NetworkX, PuLP, Z3, SymPy, SciPy, OR-Tools)
- `/uber-interpret` skill: Solution interpretation for stakeholders
  - Domain-specific translation patterns (math to real-world)
  - Visualization guide with 14+ chart types and matplotlib templates
- Two worked examples:
  - **Milking Cows** (USACO): interval merging, O(N log N), with brute-force verification
  - **Inspector Assignment**: bipartite ILP with sensitivity analysis and stakeholder visualizations
- Installation script with global/project-level options
- Architecture documentation and tutorials
