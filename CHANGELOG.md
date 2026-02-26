# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.1.0] - 2026-02-25

### Added

- **LaTeX/PDF output support**: Three output modes selectable at invocation:
  - **Python** (default): solver script + console output + JSON (existing behavior)
  - **LaTeX/PDF**: professional mathematical report typeset as `.tex` + compiled `.pdf`
  - **Both**: full Python output AND a compiled PDF report
- **Jinja2 LaTeX templates** (`templates/latex/`):
  - `report.tex.j2`: master document template
  - `preamble.tex.j2`: shared preamble (amsmath, booktabs, graphicx, hyperref, etc.)
  - `section_model.tex.j2`: Phase A formulation (universe, variables, constraints, objective)
  - `section_solve.tex.j2`: Phase B solution (algorithm, verification table, certificate)
  - `section_interpret.tex.j2`: Phase C interpretation (sensitivity, figures, recommendations)
  - `section_appendix.tex.j2`: optional Python solver listing
  - `polya.sty`: custom style with branded environments (`polyamodel`, `polyaresult`, `polyainsight`)
- **`utils/latex_data.py`**: Dataclasses mirroring the three artifact schemas (`FormalModel`, `SolutionReport`, `InterpretationReport`) plus supporting types
- **`utils/latex_renderer.py`**: `LatexRenderer` class with `render_tex()` (Jinja2) and `render_pdf()` (fpdf2 + matplotlib math) methods; optional `compile_tex()` for system LaTeX
- **`utils/render_example.py`**: CLI utility to generate PDF reports from any existing example's `solution.json`
- **Phase D: Generate Report** added to orchestrator (`skills/uber-polya/SKILL.md`) for LaTeX/PDF modes
- **Artifact 4: PDF Report** schema added to orchestrator
- New dependencies: `Jinja2`, `fpdf2`

### Changed

- `skills/uber-polya/SKILL.md`: added Output Format Selection section and Phase D
- `skills/uber-model/SKILL.md`: added LaTeX output instruction at end of Phase 3
- `skills/uber-solve/SKILL.md`: added LaTeX output instruction at end of Phase 3
- `skills/uber-interpret/SKILL.md`: added LaTeX output instruction at end of Phase 4
- `requirements.txt`: added Jinja2 and fpdf2
- `CLAUDE.md`: added templates/ to project structure, LaTeX/PDF conventions section, updated current state

## [0.3.0] - 2026-02-21

### Added

- **Test infrastructure**: 168 automated tests across 2 test suites
  - `tests/test_solvers.py`: 36 smoke tests (subprocess exit code), 13 verification tests (solution.json checks), 3 feasibility tests
  - `tests/test_structure.py`: 116 structural tests (skill dirs, SKILL.md frontmatter, example READMEs, solver scripts, HTML nav bars, root files)
  - `tests/conftest.py`: Shared fixtures for path resolution
  - `pytest.ini`: Test configuration with 120s timeout and slow marker
- **GitHub Actions CI** (`.github/workflows/ci.yml`): Python 3.11 + 3.12 matrix, pip caching, 3-stage test pipeline
- **`requirements.txt`**: All 25 Python dependencies (21 solver libs + pandas + simpy + pytest + pytest-timeout)

### Changed

- Tutorial reframed around `/uber-polya` as single entry point (both `getting-started.md` and `getting-started.html`)
  - Phase headers: "Understand & Model", "Solve & Verify", "Interpret & Recommend"
  - Removed separate `/uber-solve` and `/uber-interpret` invocation steps
  - Sub-skills referenced only as "under the hood" detail
- Footer navigation links removed from all 7 HTML pages (top nav bar is sole navigation)
- "Install Free" button text changed to "Start Now" in `index.html`

### Fixed

- `examples/meal-planning/meal_solver.py`: TypeError crash when PuLP returns infeasible (None objective formatted with f-string)

## [0.2.0] - 2026-02-21

### Added

- **Documentation overhaul**:
  - Standardized nav bar across all 8 HTML pages (Docs, Tutorial, Manifesto, GitHub with SVG icon)
  - Added `.github-link` CSS with inline GitHub Octicon SVG to all pages
  - Updated index.html stats: 305 algorithms, 91 structures, 36 examples, 26 solver libraries, 24 domains
  - Expanded getting-started tutorial from 16 to 36 worked examples (both .md and .html)
  - Added 6 new problem categories to tutorial: time series, survival analysis, ML, simulation, causal inference, OR
  - Updated pip install command across all docs to include all 21 packages
- **Expansion roadmap**: Added 14 Planned domains and 9 Unlikely domains to README
  - Planned: PDEs, dynamical systems, spatial statistics, geodesy, option pricing, risk management, agent-based modeling, Fourier analysis, DSP, information theory, classical control, modern control, population dynamics, epidemiology
  - Unlikely: abstract algebra, real analysis, complex analysis, calculus of variations, actuarial science, reinforcement learning, coding theory, cryptography, phylogenetics

### Changed

- Manifesto title: "Every Problem Is a Math Problem" → "Most of Your Problems Are Math Problems"
- README Documentation section: updated manifesto link text
- All 8 HTML docs pages: consistent 4-item nav bar (was inconsistent mix of 3-5 items)

---

_Internal development milestones below (v0.3.0–v1.0.0) detail the per-phase changes._

---

## [1.0.0] - 2026-02-21

### Added

- **Numerical Methods domain** seeded end-to-end:
  - 3 new structures in structures.md (§22: root-finding problem, interpolation problem, quadrature problem)
  - 13 new algorithms in algorithms.md:
    - §30 Root Finding (A175-A179): bisection, Newton-Raphson, secant, Brent's, fixed-point iteration
    - §31 Interpolation & Approximation (A180-A184): linear, Lagrange, cubic spline, Chebyshev, RBF
    - §32 Numerical Integration (A185-A187): trapezoidal, Simpson's, Gaussian quadrature
  - 3 new interpretation patterns (§19.1: root-finding, §19.2: interpolation, §19.3: quadrature)
  - 1 new chart type (§35 root/interpolation plot)
  - **Root Finding & Interpolation** worked example (examples/root-finding/)
- **Causal Inference domain** seeded end-to-end:
  - 2 new structures in structures.md (§23: causal graph/DAG, treatment-outcome model)
  - 7 new algorithms in algorithms-statistics.md (S104-S110):
    - §19 Causal Inference: propensity score matching, difference-in-differences, instrumental variables, regression discontinuity, synthetic control, DAG-based identification, doubly robust ATE
  - dowhy solver reference in solvers-statistics.md (§13)
  - 2 new interpretation patterns (§20.1: treatment effect, §20.2: causal DAG)
  - 1 new chart type (§36 causal effect plot)
  - **Causal Inference -- Job Training Program** worked example (examples/causal-inference/)
- **Extended Operations Research domain** seeded end-to-end:
  - 3 new structures in structures.md (§24: inventory model, packing/bin problem, facility location model)
  - 8 new algorithms in algorithms.md:
    - §33 Extended OR (A188-A195): EOQ, newsvendor, safety stock, job shop scheduling, flow shop scheduling, bin packing FFD, facility location p-median, capacitated VRP
  - 3 new interpretation patterns (§21.1: inventory policy, §21.2: scheduling/routing, §21.3: packing/location)
  - 1 new chart type (§37 inventory policy chart)
  - **Inventory Optimization -- EOQ & Newsvendor** worked example (examples/inventory-optimization/)
  - **Bin Packing -- Container Loading** worked example (examples/bin-packing/)
- Problem classification decision tree expanded with 11 new branches (FIND ROOT, INTERPOLATE, INTEGRATE, CAUSAL EFFECT, MANAGE INVENTORY, PACK, LOCATE, SCHEDULE JOBS, ROUTE VEHICLES)
- 19 new quick-lookup patterns, 10 new complexity entries, 7 new disambiguation tips
- Cross-reference indexes updated in all modified reference files

### Changed

- algorithms.md scope: 174 → 195 algorithms (added 13 numerical methods + 8 extended OR)
- algorithms-statistics.md scope: 103 → 110 algorithms (added 7 causal inference)
- structures.md scope: 83 → 91 structures (added 3+2+3 for numerical/causal/OR)
- solvers-statistics.md: 12 → 13 solver library entries (added dowhy)
- interpretation-patterns.md: 37 → 43 pattern groups (added 6 for numerical/causal/OR)
- visualization.md: 34 → 37 chart types (added root/interpolation, causal effect, inventory policy)
- Updated README: 305 algorithms, 26 solver libraries, 91 structures, 24 domains, 36 examples

## [0.9.0] - 2026-02-20

### Added

- **Simulation & ODEs domain** seeded end-to-end:
  - 8 new structures in structures.md (§21: ODE/dynamical system, queuing system, simulation model, discrete-event system, epidemic/compartmental model, predator-prey/population system, birth-death process, random walk/stochastic trajectory)
  - 10 new algorithms in algorithms.md (A165-A174: §29 Numerical ODEs & Dynamical Systems -- Euler, RK4, stiff ODE solver, phase portrait, equilibrium & stability, bifurcation, ODE parameter estimation, ODE sensitivity, SIR/SEIR, Lotka-Volterra)
  - 13 new algorithms in algorithms-statistics.md (S91-S103):
    - §16 Monte Carlo Methods (S91-S95): MC integration, risk simulation, importance sampling, variance reduction, scenario generation
    - §17 Queuing Theory (S96-S100): M/M/1, M/M/c, M/G/1, Little's Law, Jackson network
    - §18 Discrete-Event Simulation (S101-S103): event-driven engine, resource allocation, warm-up detection
  - simpy solver reference in solvers-statistics.md (§12)
  - 5 new interpretation patterns (§18.1: ODE/dynamics, §18.2: epidemic model, §18.3: queuing system, §18.4: Monte Carlo, §18.5: DES results)
  - 4 new chart types in visualization.md (§31 phase portrait, §32 epidemic curve, §33 queue performance dashboard, §34 Monte Carlo convergence)
  - **Call Center Queuing Analysis** worked example (examples/queuing-system/)
  - **SIR Epidemic Model** worked example (examples/epidemic-sir/)
  - **Monte Carlo Project Risk Analysis** worked example (examples/monte-carlo-risk/)
- Problem classification decision tree expanded with 3 new branches (SIMULATE/WHAT-IF, ANALYZE QUEUE, MODEL DYNAMICS/ODE) and 12 new quick-lookup patterns
- 8 new complexity quick-check entries in problem-classification.md
- 5 new disambiguation tips in problem-classification.md
- Cross-reference indexes updated in all modified reference files

### Changed

- algorithms.md scope: 164 → 174 algorithms (added 10 for ODEs & dynamical systems)
- algorithms-statistics.md scope: 90 → 103 algorithms (added 13 for MC/queuing/DES)
- structures.md scope: 75 → 83 structures (added 8 for simulation & ODEs)
- solvers-statistics.md: 11 → 12 solver library entries (added simpy)
- interpretation-patterns.md: 32 → 37 pattern groups (added 5 for simulation/ODE)
- visualization.md: 30 → 34 chart types (added phase portrait, epidemic curve, queue dashboard, MC convergence)
- Updated README: 277 algorithms, 25 solver libraries, 83 structures, 21 domains, 32 examples

## [0.8.0] - 2026-02-20

### Added

- **Machine Learning domain** seeded end-to-end:
  - 5 new structures in structures.md (§20: classification model, regression model (ML), cluster structure, low-dimensional embedding, ML pipeline/feature space)
  - 22 new algorithms in algorithms-statistics.md (S69-S90):
    - §11 Classification (S69-S75): k-NN, Decision Tree, Random Forest, SVM, Naive Bayes, Gradient Boosting, MLP Neural Network
    - §12 ML Regression (S76-S77): Decision Tree/RF Regressor, Gradient Boosting Regressor
    - §13 Clustering (S78-S82): K-Means, DBSCAN, Agglomerative, GMM, Spectral Clustering
    - §14 Dimensionality Reduction (S83-S86): PCA, t-SNE, UMAP, Factor Analysis
    - §15 Model Selection & Feature Engineering (S87-S90): Feature Selection, Hyperparameter Tuning, Model Comparison, Pipeline Construction
  - xgboost solver reference in solvers-statistics.md (§10), umap-learn solver (§11)
  - Expanded scikit-learn solver entry (§3) with full ML APIs (classifiers, clustering, dim reduction, pipelines)
  - 3 new interpretation patterns (§17.1: classification results, §17.2: clustering results, §17.3: dimensionality reduction results)
  - 3 new chart types in visualization.md (§28 confusion matrix heatmap, §29 ROC/PR curve, §30 cluster scatter plot)
  - **Customer Churn Classification** worked example (examples/classification/)
  - **Customer Segmentation via Clustering** worked example (examples/clustering/)
  - **Feature Importance & Model Comparison** worked example (examples/feature-importance/)
- Problem classification decision tree expanded with 6 new branches (CLASSIFY, PREDICT VALUE, CLUSTER/SEGMENT, REDUCE DIMENSIONS, SELECT FEATURES, TUNE MODEL) and 15 new quick-lookup patterns
- 12 new complexity quick-check entries in problem-classification.md
- 7 new disambiguation tips in problem-classification.md
- Cross-reference indexes updated in all modified reference files

### Changed

- algorithms-statistics.md scope: 68 → 90 algorithms (added 22 for machine learning)
- structures.md scope: 70 → 75 structures (added 5 for ML)
- solvers-statistics.md: 9 → 11 solver library entries (added xgboost, umap-learn); expanded scikit-learn entry
- interpretation-patterns.md: 29 → 32 pattern groups (added 3 for ML)
- visualization.md: 27 → 30 chart types (added confusion matrix, ROC/PR curve, cluster scatter)
- Updated README: 254 algorithms, 24 solver libraries, 75 structures, 20 domains, 29 examples

## [0.7.0] - 2026-02-21

### Added

- **Time Series Analysis domain** seeded end-to-end:
  - 3 new structures in structures.md (§18: time series/temporal sequence, seasonal/cyclical pattern, trend component)
  - 15 new algorithms in algorithms-statistics.md (S46-S60: ARIMA, SARIMA, exponential smoothing, decomposition, ACF/PACF, stationarity tests, Granger causality, VAR, GARCH, Prophet, change point detection, anomaly detection, moving average, spectral analysis, intervention analysis)
  - prophet solver reference in solvers-statistics.md (§7), arch solver (§8), ruptures solver (§9)
  - 2 new interpretation patterns (§16.1: time series forecast results, §16.2: decomposition/trend results)
  - 2 new chart types in visualization.md (§25 time series decomposition plot, §26 forecast plot with CI bands)
  - **Sales Forecast — Monthly Retail Revenue** worked example (examples/sales-forecast/)
  - **Anomaly Detection — Server Response Times** worked example (examples/anomaly-detection/)
- **Stochastic Processes domain** seeded end-to-end:
  - 3 new structures in structures.md (§19: continuous-time Markov chain, point process, random walk/diffusion)
  - 5 new algorithms in algorithms-statistics.md (S61-S65: CTMC, birth-death process, Poisson process, random walk analysis, renewal process)
- **Survival Analysis domain** completed:
  - 3 new algorithms in algorithms-statistics.md (S66-S68: log-rank test, accelerated failure time, competing risks)
  - 1 new interpretation pattern (§16.3: survival/time-to-event results)
  - 1 new chart type in visualization.md (§27 survival curve / Kaplan-Meier)
  - **Customer Survival — SaaS Subscription Churn** worked example (examples/customer-survival/)
- Problem classification decision tree expanded with 4 new branches (FORECAST/PREDICT, DETECT CHANGE/ANOMALY, MODEL RANDOM EVENTS, SURVIVAL/TIME-TO-EVENT) and 20 new quick-lookup patterns
- 13 new complexity quick-check entries in problem-classification.md
- 7 new disambiguation tips in problem-classification.md
- 6 new entries in cross-domain pattern table (structures.md)
- Cross-reference indexes updated in all modified reference files

### Changed

- algorithms-statistics.md scope: 45 → 68 algorithms (added 23 across 3 domains)
- structures.md scope: 64 → 70 structures (added 6 across 2 new domains)
- solvers-statistics.md: 6 → 9 solver library entries (added prophet, arch, ruptures)
- interpretation-patterns.md: 26 → 29 pattern groups (added 3 for time series/survival)
- visualization.md: 24 → 27 chart types (added decomposition plot, forecast plot, survival curve)
- Updated README: 232 algorithms, 22 solver libraries, 70 structures, 19 domains, 26 examples

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

## [0.2.0-dev] - 2026-02-18

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
