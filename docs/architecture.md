# Architecture

How four Claude Code skills implement George Polya's problem-solving methodology as a universal problem-solving engine.

## The Polya Foundation

In 1945, mathematician George Polya published "How to Solve It," articulating a four-phase cycle for mathematical problem solving. The uber-polya trilogy maps each of Polya's phases to structured skill workflows.

### Phase 1: Understanding the Problem

*"It is foolish to answer a question that you do not understand."*

Polya's first phase asks: What is the unknown? What are the data? What is the condition? Can you separate the parts of the condition?

This maps to `/uber-model` Phases 0-1. Phase 0 receives the problem and classifies it as a "problem to find" (seeking an unknown value, object, or structure) or a "problem to prove" (establishing truth or falsity). Phase 1 conducts Socratic questioning to extract the unknown, data, conditions, and notation. The phase ends with a structured Problem Understanding block that the user must confirm before proceeding.

### Phase 2: Devising a Plan

*"The main achievement in the solution of a problem is to conceive the idea of a plan."*

Polya's second phase asks: Have you seen it before? Do you know a related problem? Could you restate the problem? Could you solve a part of it?

This maps to `/uber-model` Phase 2 and `/uber-solve` Phases 0-1. In uber-model Phase 2, heuristics from the reference catalog guide the user toward candidate discrete math structures. The skill reads both reference files (heuristics and structures) and proposes 1-3 candidate models with rationale and trade-offs. In uber-solve Phase 0, the chosen model is classified into a named problem class (graph coloring, knapsack, SAT, etc.) with its complexity class, instance size, and solution strategy. Phase 1 selects the specific algorithm, verification method, and fallback.

### Phase 3: Carrying Out the Plan

*"To carry out the plan is much easier; what we need is mainly patience."*

Polya's third phase emphasizes careful execution and step-by-step verification.

This maps to `/uber-solve` Phases 2-3. Phase 2 engineers the solution: a self-contained Python script with typed data models, the solver implementation, independent verification, and timing instrumentation. Phase 3 executes the solver, presents results in a structured Solution Report, and runs the independent verification -- checking every constraint from the formal model, computing optimality certificates, and cross-validating with alternative methods when feasible.

### Phase 4: Looking Back

*"Even fairly good students, when they have obtained the solution of the problem, shut their books and look for something else. Doing so, they miss an important and instructive phase of the work."*

Polya's fourth phase asks: Can you check the result? Can you derive it differently? Can you use the result or the method for some other problem?

This maps to `/uber-interpret` Phases 1-5. Phase 1 translates the mathematical solution back through the real-world mapping. Phase 2 probes robustness through sensitivity analysis and what-if scenarios. Phase 3 generates visualizations. Phase 4 formulates recommendations adapted to the audience. Phase 5 extracts transferable patterns, critiques the method, and builds a reusable decision framework -- the lasting value beyond the current problem.

## Trilogy Architecture

The trilogy skills form a pipeline. Each skill's output feeds the next. The `/uber-polya` orchestrator chains all three automatically.

```
/uber-model               /uber-solve               /uber-interpret
"What IS the problem?"  "What is the ANSWER?"   "What does it MEAN?"

  Real-world  ------>  Formal  ------>  Verified  ------>  Actionable
  problem              Model           Solution           Insight
```

### uber-model Outputs

The modeling skill produces a Problem Understanding block and a Formal Model.

**Problem Understanding** (Phase 1 gate):
- Problem Type: Find or Prove
- Unknown: what we seek, in one sentence
- Data: bulleted list of everything given
- Conditions: numbered atomic constraints
- Notation: symbol-to-meaning mappings
- Figure: ASCII sketch if applicable

**Formal Model** (Phase 3):
- Domain: one of the 10 mathematical domains
- Universe: the set of objects under consideration
- Variables: symbols with meaning and type/range
- Structure: the core mathematical object (graph, formula, ILP, etc.)
- Mapping: real-world concept to mathematical object table
- Constraints: numbered formal constraints
- Objective (for find) or Claim (for prove)

The model also includes a "Next Steps" bridge suggesting an algorithm family, complexity class, and available solver tools for uber-solve.

### uber-solve Outputs

The solving skill produces a Problem Classification and a Solution Report.

**Problem Classification** (Phase 0 gate):
- Named Problem: the textbook problem class
- Complexity Class: P, NP-hard, NP-complete, etc.
- Instance Size: the parameters that determine computational cost
- Solution Strategy: exact polynomial, ILP solver, approximation, etc.
- Selected Algorithm: name with time and space complexity
- Solver Library: NetworkX, PuLP, Z3, SymPy, SciPy, OR-Tools, cvxpy, scipy.stats, statsmodels, or others
- Correctness Guarantee: optimal, (1+e)-approximate, or heuristic with bound

**Solution Report** (Phase 3):
- Answer: the solution value, proof, or count
- Objective Value: for optimization problems
- Optimal: yes/no/unknown
- Feasible: yes with constraint count verified
- Algorithm and complexity
- Timing in seconds
- Certificate: optimality proof description
- Verification details: constraint-by-constraint check

The report also includes the complete solver script -- a self-contained Python file with type hints, dataclasses, separate verify() function, and timing.

### uber-interpret Outputs

The interpretation skill produces five deliverables across its phases.

**Solution Translation** (Phase 1): reverse mapping from math to reality, with the bottom-line sentence.

**Sensitivity Analysis** (Phase 2): parameter sensitivity table (robust/sensitive/critical classification), structural sensitivity, optimality gap analysis, and 2-3 what-if scenarios.

**Visualizations** (Phase 3): 1-3 charts selected by result type -- graph diagrams, heatmaps, Gantt charts, tornado diagrams, distribution charts, flow diagrams, Pareto frontiers, Hasse diagrams, group comparison bars, QQ plots, regression plots, forest plots, or posterior distributions -- each with interpretive annotation.

**Recommendations** (Phase 4): primary recommendation, key constraints to monitor, risk factors, quick wins, and limitations. Adapted to the audience: technical, decision-maker, domain expert, or general.

**Knowledge Transfer** (Phase 5): transferable pattern extraction, method critique, generalization inventory, reusable decision framework, and validation plan.

## The Reference Knowledge Base

Fifteen reference files provide the domain knowledge that powers the skills. Each is a curated catalog designed to be read on demand during a specific skill phase. All reference files carry cross-reference indexes linking entries to counterparts in other files.

### uber-model references (5 files)

**heuristics.md** -- Seventeen heuristics drawn from Polya's "How to Solve It," organized by phase. Each heuristic includes trigger conditions, Socratic questions adapted from Polya, and mathematical modeling applications. Phase 1 heuristics (H1-H4) address understanding: separating conditions, introducing notation, drawing figures, checking feasibility. Phase 2 heuristics (H5-H12) address planning: analogy, decomposition, generalization (the Inventor's Paradox), specialization, working backwards, auxiliary elements, restatement, and related problems. Phase 3 heuristics (H13-H14) address execution: step verification and gap detection. Phase 4 heuristics (H15-H17) address reflection: result verification, method generalization, and connection to known results.

**structures.md** -- A catalog of 43 mathematical structures across 10 domains. Each entry provides a one-line formal definition, real-world indicator phrases that suggest the structure, a formal notation template, concrete examples mapping real-world scenarios to math, and the classic named problems associated with it. The 10 domains are Graph Theory (simple graph, digraph, weighted graph, bipartite graph, tree, DAG, hypergraph, multigraph), Combinatorics (permutations, combinations, integer partitions, compositions, Latin squares), Set Theory (sets/multisets, set systems, power set, set partition), Logic (propositional, predicate, modal/deontic, constraint satisfaction), Number Theory (modular arithmetic, divisibility, Diophantine equations), Relations & Orders (partial order, equivalence relation, lattice), Optimization (ILP, search space, scheduling model), Discrete Probability (sample space, random variables), Continuous Optimization (unconstrained optimization, convex program, quadratic program, least-squares, nonlinear constrained), and Statistical Inference (random variable/distribution, statistical hypothesis, regression model, Bayesian model, sample/population, experimental design). A cross-domain pattern table maps 36+ real-world patterns to their primary structure.

**problem-classification.md** -- A quick-reference decision tree and pattern lookup table for rapid problem classification. Routes problems through branching questions (discrete vs. continuous, find vs. prove, optimization vs. counting, etc.) to a named problem class with suggested structures and algorithms.

**common-mistakes.md** -- Sixteen common anti-patterns across modeling (M1-M10), solving (S1-S6), and interpretation (I1-I6). Each mistake includes symptoms, prevention, and fix. Used as a pre-flight checklist before finalizing a formal model.

**model-templates.md** -- Fill-in-the-blank formal model templates for the 5 most common problem patterns: assignment/matching, scheduling/coloring, routing/shortest path, selection/knapsack, and dependency ordering. Each template includes a skeleton with placeholders, a fill-in checklist, and a quick variant guide.

### uber-solve references (6 files)

**algorithms.md** -- A comprehensive catalog of 94 discrete math and continuous optimization algorithms organized into 21 sections. Each entry specifies time complexity, space complexity, recommended Python library, correctness guarantee (exact, approximation ratio, or heuristic), and implementation guidance with code snippets. Coverage spans graph traversal, shortest path, MST, matching, network flow, coloring, independent set/vertex cover/clique, Euler/Hamilton, TSP, LP/ILP, dynamic programming patterns, greedy algorithms, SAT/SMT/CSP, number theory, combinatorial counting, order theory, proof techniques, discrete probability, search/backtracking, and continuous optimization (BFGS, gradient descent, cvxpy DCP, QP, least squares, Gauss-Newton, SQP, interior point). An algorithm selection matrix maps each problem class to the recommended algorithm by instance size.

**algorithms-statistics.md** -- A catalog of 45 statistical inference algorithms covering hypothesis testing (z-test, t-test, paired t, Mann-Whitney, Wilcoxon, chi-squared, Fisher's exact, ANOVA, Kruskal-Wallis), regression (OLS, logistic, GLM, robust), Bayesian methods (conjugate priors, MCMC, Bayesian A/B), estimation (MLE, CI, bootstrap CI, effect sizes), and resampling (permutation test, bootstrap). Each entry specifies the test conditions, assumptions, Python implementation, and interpretation guidance.

**solvers.md** -- A guide to the discrete math and continuous optimization Python solver ecosystem: what each library solves, installation, key APIs with code examples, and performance notes. Covers NetworkX, PuLP, Z3, SymPy, SciPy, OR-Tools, itertools, numpy, and cvxpy. A solver selection guide maps each problem type to primary and fallback solvers.

**solvers-statistics.md** -- A guide to the statistical inference Python solver ecosystem. Covers scipy.stats (distribution functions, hypothesis tests), statsmodels (regression, time series, GLMs), scikit-learn (ML-adjacent statistical methods), PyMC (Bayesian MCMC), pingouin (quick statistical tests), and lifelines (survival analysis).

**solving-protocols.md** -- Nine domain-specific step-by-step solving workflows: Graph, ILP/LP, SAT/SMT, Counting, Proof, Number Theory, Dynamic Programming, Continuous Optimization, and Statistical Inference. Each protocol specifies the phases, checks, and common pitfalls for its domain.

**optimization-hardening.md** -- Performance tuning and production hardening guide for Phase 4. Covers profiling, algorithmic optimization, approximation tiers, memory reduction, and production-grade engineering. Read only when the initial solution is too slow or needs production-grade performance.

### uber-interpret references (2 files)

**interpretation-patterns.md** -- Domain-specific patterns for translating mathematical solutions back into real-world meaning. Covers graph theory results (shortest path, matching, coloring, flow, connectivity), optimization results (LP/ILP with shadow prices and reduced costs, knapsack/selection, scheduling), proof results (existence, impossibility, bounds), counting results (exact and asymptotic), probability results (probability values with audience-adapted presentation, expected value with risk framing), number theory results, convex optimization results (optimal point, dual variables, sensitivity), and statistical inference results (hypothesis test interpretation, regression results, confidence/credible intervals, Bayesian posteriors). Includes a general sensitivity framework and a general limitation framework.

**visualization.md** -- A chart selection matrix mapping 20+ result types to primary and secondary chart types. Provides complete matplotlib/seaborn/NetworkX code templates for annotated graph diagrams, assignment matrix heatmaps, Gantt charts, tornado diagrams, scenario comparison bar charts, distribution bar charts, Pareto frontier scatter plots, flow diagrams, Hasse diagrams, proof step visualizations, group comparison bars with CI, QQ plots, regression plots, residual plots, forest plots, and posterior distribution plots. Includes a colorblind-friendly palette, typography standards, layout rules, and audience adaptation guidelines.

## Design Principles

### Socratic, not didactic

The skills ask questions that could have occurred to the user. They present understanding and let the user confirm, correct, or refine. This follows Polya's central insight: "Leave the user a reasonable share of the work." Phase gates use AskUserQuestion to ensure the user drives the thinking, not Claude.

### Verify everything

Every solution includes independent verification. uber-solve requires a separate `verify()` function that re-checks every constraint independently of the solver logic. For optimization, it computes optimality certificates (LP relaxation bounds, dual solutions, exhaustive comparison for small instances). For proofs, it verifies each logical step. Never trust a solver output without checking it.

### Right tool for the job

Algorithm selection follows the problem class and instance size, not a one-size-fits-all approach. The algorithm selection matrix in algorithms.md maps each problem class to three tiers: small (n <= 25, exact exponential algorithms), medium (n <= 1000, ILP/SAT solvers), and large (n > 1000, approximation algorithms or heuristics). The skill explicitly states the correctness guarantee: exact optimal, proven approximation ratio, or heuristic with no formal bound.

### Audience adaptation

uber-interpret adapts its output to four audiences. Technical readers get algorithm names, complexity bounds, dual values, and theorem references. Decision-makers get the bottom line, percentages, business trade-offs, and cost of alternatives. Domain experts get domain vocabulary, practical implications, and validation steps. General audiences get plain language, concrete analogies, and "this means you should..." conclusions.

### Knowledge transfer

Every problem teaches a reusable pattern. uber-model Phase 4 extracts a "Modeling Insight" connecting real-world patterns to DM structures. uber-interpret Phase 5 builds a transferable pattern, a generalization inventory, and a reusable decision framework with trigger conditions and key diagnostic questions. The goal is not just to solve this problem, but to equip the user to recognize and solve similar problems independently.

### Cyclic, not linear

Any phase can loop back to an earlier one when new understanding emerges. uber-model explicitly supports this: "If the model feels wrong, return to the earliest phase where the issue originated." uber-interpret's error recovery sends users back to uber-model when solutions do not make practical sense. The Polya cycle is a cycle, not a waterfall.

## Why Start With Discrete Mathematics?

Polya's method is universal, but our implementation begins with discrete mathematics for practical reasons:

1. **Cleanest complexity theory.** Discrete problems have a well-defined hierarchy (P, NP, PSPACE, EXPTIME) that directly maps to algorithm selection. When you identify "graph coloring," you immediately know: NP-hard, use greedy for small instances, ILP for medium, heuristic for large. No other domain has this level of classification maturity.

2. **Most mature solver ecosystem.** Libraries like NetworkX, PuLP, Z3, and OR-Tools have decades of development, millions of users, and well-documented APIs. They provide the reliable foundation that verified solving demands.

3. **Polya's own territory.** Many of Polya's examples in "How to Solve It" are discrete or algebraic: geometry problems with integer solutions, combinatorial puzzles, number theory. The heuristics map naturally to discrete structure recognition.

4. **Verification is exact.** Discrete solutions can be verified by exhaustive enumeration (for small instances) or by checking certificates (LP relaxation bounds, SAT proofs). This enables the "verify everything" principle without numerical tolerance issues.

Starting with discrete math provides the strongest foundation. Each subsequent domain builds on this base while adapting to its own verification paradigm (convergence for optimization, confidence intervals for statistics, cross-validation for ML).

## Expansion Architecture

The uber-polya framework is designed for modular domain expansion. Each new domain adds content at three levels without changing the core Polya workflow:

### Level 1: Reference Files

New domains add reference files to the existing skill directories:

```
skills/uber-model/references/
├── heuristics.md              # Polya's heuristics (shipped)
├── structures.md              # 43 structures, 10 domains (shipped)
├── problem-classification.md  # Decision tree (shipped)
├── common-mistakes.md         # 16 anti-patterns (shipped)
└── model-templates.md         # 5 formal model templates (shipped)

skills/uber-solve/references/
├── algorithms.md              # Discrete math + continuous opt (shipped)
├── solvers.md                 # Discrete math + continuous solvers (shipped)
├── algorithms-statistics.md   # Statistical inference (shipped)
├── solvers-statistics.md      # Statistical solvers (shipped)
├── solving-protocols.md       # 9 domain-specific protocols (shipped)
├── optimization-hardening.md  # Production hardening (shipped)
├── algorithms-ml.md           # Machine learning (planned)
└── solvers-ml.md              # scikit-learn, PyTorch (planned)

skills/uber-interpret/references/
├── interpretation-patterns.md # 8 pattern sections (shipped)
└── visualization.md           # 20+ chart types (shipped)
```

### Level 2: Protocol Sections

Each SKILL.md gains new protocol sections for domain-specific workflows:

- **uber-model**: New structure entries in `structures.md` (e.g., "Feature Matrix," "Time Series")
- **uber-solve**: New solving protocols in `solving-protocols.md` and domain-specific algorithm catalogs
- **uber-interpret**: New interpretation patterns (model performance metrics, convergence diagnostics)

### Level 3: Classification Expansion

The Phase 0 classification table in uber-solve grows to recognize new problem types:

| Shipped (Discrete) | Shipped (Continuous) | Shipped (Statistical) | Planned (ML) |
|---|---|---|---|
| Graph coloring | Convex optimization | Hypothesis testing (t, chi², ANOVA) | Classification |
| ILP | Quadratic programming | Regression (OLS, logistic, GLM) | Clustering |
| SAT | Gradient descent / BFGS | Bayesian inference (MCMC, conjugate) | Dimensionality reduction |
| Knapsack | Interior point / SQP | Survival analysis (KM, Cox PH) | Feature selection |

The classification tree branches on "Is this discrete or continuous?" and "Is this inferential?" as the first decisions, then routes to domain-specific protocols.
