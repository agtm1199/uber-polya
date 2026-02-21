# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.6.0] - 2026-02-20

### Added

- **Game Theory domain** seeded end-to-end:
  - 3 new structures in structures.md (§15: strategic-form game, extensive-form game, coalition/cooperative game)
  - 12 new algorithms in algorithms.md (A135-A146: Nash equilibrium, mixed strategy, minimax, Shapley value, fair division, Vickrey auction, repeated games, ESS, nucleolus, Nash bargaining, VCG mechanism)
  - nashpy solver reference in solvers.md (§13)
  - 2 new interpretation patterns (§13: Nash equilibrium results, Shapley value/fair division results)
  - 1 new chart type in visualization.md (§22 payoff matrix heatmap)
  - **Nash Equilibrium — Coffee Shop Pricing** worked example (examples/nash-equilibrium/)
- **Decision Analysis domain** seeded end-to-end:
  - 3 new structures in structures.md (§16: decision tree/influence diagram, preference model/utility function, multi-criteria problem)
  - 10 new algorithms in algorithms.md (A147-A156: EMV, expected utility, decision tree evaluation, sensitivity/tornado, AHP, TOPSIS, ELECTRE, Bayesian decision, minimax regret, MAUT)
  - 2 new interpretation patterns (§14: EMV/decision tree results, MCDA ranking results)
  - 1 new chart type in visualization.md (§23 tornado/sensitivity chart)
  - **Vendor Selection — Cloud Infrastructure** worked example (examples/vendor-selection/)
- **Multi-Objective Optimization domain** seeded end-to-end:
  - 3 new structures in structures.md (§17: Pareto set/efficient frontier, objective space, goal/aspiration model)
  - 8 new algorithms in algorithms.md (A157-A164: Pareto frontier enumeration, weighted sum, epsilon-constraint, NSGA-II, MOEA/D, goal programming, lexicographic optimization, reference point method)
  - pymoo solver reference in solvers.md (§14)
  - 2 new interpretation patterns (§15: Pareto frontier results, goal programming results)
  - 1 new chart type in visualization.md (§24 Pareto frontier plot)
  - **Pareto Optimization — Product Design** worked example (examples/pareto-optimization/)
- Problem classification decision tree expanded with 3 new branches (COMPETE/NEGOTIATE, DECIDE/CHOOSE, OPTIMIZE MULTIPLE) and 19 new quick-lookup patterns
- 10 new complexity quick-check entries in problem-classification.md
- 6 new disambiguation tips in problem-classification.md
- 13 new entries in cross-domain pattern table (structures.md)
- Cross-reference indexes updated in all modified reference files

### Changed

- algorithms.md scope: 134 → 164 algorithms (added 30 across 3 new domains)
- structures.md scope: 55 → 64 structures (added 9 across 3 new domains)
- solvers.md: 12 → 14 solver library entries (added nashpy, pymoo)
- interpretation-patterns.md: 20 → 26 pattern groups (added 6 across 3 new domains)
- visualization.md: 21 → 24 chart types (added payoff matrix heatmap, tornado/sensitivity chart, Pareto frontier plot)
- Updated README: 209 algorithms, 19 solver libraries, 64 structures, 17 domains, 23 examples

## [0.5.0] - 2026-02-20

### Added

- **Linear Algebra domain** seeded end-to-end:
  - 4 new structures in structures.md (§11: matrix/linear map, vector space, linear system, eigenstructure)
  - 12 new algorithms in algorithms.md (A95-A106: Gaussian elimination, LU, eigenvalue, SVD, QR, Cholesky, inverse, determinant, rank, null space, condition number, least squares)
  - numpy.linalg and scipy.linalg solver references (submodules of existing libraries)
  - 2 new interpretation patterns (§9: linear system solutions, eigenvalue/SVD results)
  - 2 new chart types in visualization.md (§17 matrix heatmap, §18 scree/spectrum plot)
  - **Traffic Flow Analysis** worked example (examples/traffic-flow/) -- linear system with conservation of flow
- **Calculus domain** seeded end-to-end:
  - 3 new structures in structures.md (§12: function/curve, integral/accumulated quantity, differential equation)
  - 10 new algorithms in algorithms.md (A107-A116: symbolic differentiation, symbolic integration, numerical integration, limits, Taylor series, partial derivatives, gradient/Jacobian/Hessian, Lagrange multipliers, symbolic ODE, numerical ODE)
  - SymPy (existing) and scipy.integrate (existing) as primary solvers
  - 2 new interpretation patterns (§10: derivative/rate results, integral/accumulated results)
  - 1 new chart type in visualization.md (§19 annotated function plot)
  - **Water Tank Optimization** worked example (examples/water-tank/) -- calculus optimization with SymPy
- **Geometry & Trigonometry domain** seeded end-to-end:
  - 4 new structures in structures.md (§13: polygon/planar region, polyhedron/3D solid, point set/spatial config, triangle)
  - 10 new algorithms in algorithms.md (A117-A126: polygon area, volume, distance, convex hull, Voronoi, Delaunay, closest pair, line intersection, triangle solver, coordinate transforms)
  - shapely and scipy.spatial solver references in solvers.md (§10-§11)
  - 1 new interpretation pattern (§11: spatial measurement results)
  - 1 new chart type in visualization.md (§20 geometric diagram)
  - **Land Survey Analysis** worked example (examples/land-survey/) -- polygon area, convex hull, containment with shapely
- **Financial Mathematics domain** seeded end-to-end:
  - 1 new structure in structures.md (§14: cash flow stream)
  - 8 new algorithms in algorithms.md (A127-A134: NPV, IRR, PMT, amortization schedule, compound interest, annuity valuation, break-even, refinancing comparison)
  - numpy-financial solver reference in solvers.md (§12)
  - 2 new interpretation patterns (§12: investment analysis, loan/amortization results)
  - 1 new chart type in visualization.md (§21 cash flow/amortization chart)
  - **Mortgage Comparison Analysis** worked example (examples/mortgage-analysis/) -- 3-option mortgage comparison with numpy-financial
- Problem classification decision tree expanded with 5 new branches (SOLVE equations, DIFFERENTIATE/INTEGRATE, MEASURE geometry, EVALUATE finances) and 19 new quick-lookup patterns
- 6 new disambiguation tips in problem-classification.md
- Cross-reference indexes updated in all modified reference files
- 16 new entries in cross-domain pattern table (structures.md)

### Changed

- algorithms.md scope: 94 → 134 algorithms (added 40 across 4 new domains)
- structures.md scope: 43 → 55 structures (added 12 across 4 new domains)
- solvers.md: 9 → 12 solver library entries (added shapely, scipy.spatial, numpy-financial)
- interpretation-patterns.md: 13 → 20 pattern groups (added 7 across 4 new domains)
- visualization.md: 16 → 21 chart types (added matrix heatmap, scree plot, function plot, geometric diagram, cash flow chart)
- Updated README: 179 algorithms, 17 solver libraries, 55 structures, 14 domains, 20 examples

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
