# Getting Started with uber-polya

A zero-to-hero tutorial. By the end, you will have modeled, solved, and interpreted a mathematical problem entirely through Claude Code slash commands.

## Prerequisites

- **Claude Code** -- Anthropic's CLI for Claude ([installation guide](https://docs.anthropic.com/en/docs/claude-code))
- **Python 3.10+** -- for running the solver code that uber-polya generates

Optional Python packages (installed automatically when needed):

```bash
pip install networkx pulp z3-solver sympy scipy matplotlib numpy cvxpy statsmodels shapely numpy-financial nashpy pymoo prophet arch ruptures lifelines scikit-learn xgboost umap-learn simpy dowhy
```

## Install uber-polya

```bash
git clone https://github.com/agtm1199/uber-polya.git
cd uber-polya
bash install.sh
```

The installer asks where to put the four skills:

1. **Global** (`~/.claude/skills/`) -- available in every project
2. **Local** (`./.claude/skills/`) -- current project only

That is it. No virtual environment, no build step. The skills are plain markdown files that Claude Code reads on demand.

## Your First Problem

Open Claude Code in any project directory and type:

```
/uber-polya I need to schedule 4 exams (A, B, C, D) into the fewest time
slots so that no student has two exams at the same time. Students are
enrolled in these pairs of courses: {A,B}, {A,C}, {B,D}, {C,D}.
```

That's it -- one command. `/uber-polya` handles the entire pipeline automatically. Here's what happens:

### Phase 1 -- Understand & Model

Claude walks through Polya's "Understanding" and "Planning" phases. It asks clarifying questions, then produces a formal model. Representative output:

> **Problem Type**: Problem to Find (optimization)
> **Unknown**: Minimum number of time slots (colors) such that no two conflicting exams share a slot
> **Structure**: Graph coloring on a conflict graph G = (V, E)
>   - Vertices V = {A, B, C, D} (exams)
>   - Edges E = {(A,B), (A,C), (B,D), (C,D)} (student enrolled in both)
> **Objective**: Minimize k such that a proper k-coloring of G exists

### Phase 2 -- Solve & Verify

Claude automatically classifies the problem, selects an algorithm, writes a solver script, runs it, and verifies the result. Representative output:

> **Named Problem**: Graph Coloring (k-coloring)
> **Complexity**: NP-hard in general; O(V + E) for bipartite detection
> **Instance Size**: |V| = 4, |E| = 4
> **Algorithm**: Bipartite 2-coloring via BFS
>
> **Answer**: chromatic number = 2
>   - Slot 1: {A, D}
>   - Slot 2: {B, C}
>
> **Verification**: All 4 edges checked -- no two adjacent vertices share a color. PASS.

### Phase 3 -- Interpret & Recommend

Claude translates the math back into your world. Representative output:

> **Bottom line**: You need exactly 2 time slots. No student has a conflict.
>
> **Schedule**:
>   - Slot 1 (e.g., Monday 9 AM): Exams A and D
>   - Slot 2 (e.g., Monday 2 PM): Exams B and C
>
> **Sensitivity**: If a student enrolls in both A and D, the chromatic number rises to 3 (the conflict graph gains an odd cycle). Monitor enrollment changes.
>
> **Modeling insight**: Whenever you need to assign items to the fewest groups such that conflicting items are separated, model it as graph coloring on a conflict graph.

> **Note**: Claude's exact wording, formatting, and level of detail will vary between runs. The outputs above are representative, not verbatim.

## What Just Happened?

You typed one command and `/uber-polya` orchestrated the entire Polya problem-solving cycle:

| Polya Phase | What uber-polya does |
|-------------|---------------------|
| 1-2: Understand & Plan | Translates your real-world problem into a formal mathematical model |
| 3: Execute | Classifies the problem, selects the right algorithm, solves it, verifies the answer |
| 4: Look Back | Translates the solution back into actionable insight with sensitivity analysis |

Under the hood, `/uber-polya` chains three internal skills (`/uber-model`, `/uber-solve`, `/uber-interpret`). You can also use these individually for finer control -- for example, `/uber-solve` accepts any well-specified math problem, and `/uber-interpret` can explain any solution you hand it.

## Next Steps

**Try the worked examples.** The `examples/` directory contains 36 fully solved problems with runnable code, organized in two categories:

**Everyday Problems** (11 examples):

- **[Shift Scheduling](../../examples/shift-scheduling/)** -- Schedule 8 nurses across 3 shifts over 7 days (ILP)
- **[Budget Optimization](../../examples/budget-optimization/)** -- Select projects to maximize ROI under budget (Knapsack ILP)
- **[Fair Rent](../../examples/fair-rent/)** -- Split rent fairly among 3 roommates (Hungarian + envy-free)
- **[Route Planning](../../examples/route-planning/)** -- Shortest delivery route across 8 stops (Held-Karp TSP)
- **[Project Prioritization](../../examples/project-prioritization/)** -- Rank 8 features by weighted criteria (MCDA)
- **[Study Schedule](../../examples/study-schedule/)** -- Conflict-free timetable for 6 subjects (graph coloring)
- **[Meal Planning](../../examples/meal-planning/)** -- 7 dinners minimizing cost within nutrition targets (ILP)
- **[Team Assignment](../../examples/team-assignment/)** -- Assign 6 developers to 6 projects (Hungarian algorithm)
- **[Break-Even Analysis](../../examples/break-even/)** -- Find break-even quantity for product launch (SymPy)
- **[Event Seating](../../examples/event-seating/)** -- Seat 12 wedding guests at 3 tables with constraints (ILP)
- **[Mortgage Comparison](../../examples/mortgage-analysis/)** -- Compare 3 mortgage options with refinancing analysis (NPV)

**Technical Showcases** (25 examples):

- **[Milking Cows](../tutorials/milking-cows-walkthrough.md)** -- Interval merging, O(N log N) sort-and-sweep
- **[Inspector Assignment](../tutorials/inspector-assignment-walkthrough.md)** -- Capacitated bipartite ILP, LP relaxation, sensitivity analysis
- **[Portfolio Optimization](../../examples/portfolio-optimization/)** -- Markowitz QP with cvxpy, efficient frontier
- **[Tournament Hamiltonian](../../examples/tournament-hamiltonian/)** -- Proof by induction with Z3 verification
- **[A/B Testing](../../examples/ab-testing/)** -- z-test, Bayesian, bootstrap, power analysis
- **[Cafe Tips](../../examples/cafe-tips/)** -- t-test, Mann-Whitney, permutation, bootstrap, Bayesian
- **[Traffic Flow](../../examples/traffic-flow/)** -- Gaussian elimination for network flow (numpy)
- **[Water Tank](../../examples/water-tank/)** -- Symbolic differentiation for optimization (SymPy)
- **[Land Survey](../../examples/land-survey/)** -- Shoelace + convex hull area computation (shapely)
- **[Nash Equilibrium](../../examples/nash-equilibrium/)** -- Support enumeration for 2-player games (nashpy)
- **[Vendor Selection](../../examples/vendor-selection/)** -- AHP + TOPSIS multi-criteria analysis (numpy)
- **[Pareto Optimization](../../examples/pareto-optimization/)** -- Epsilon-constraint + Pareto filter (pymoo)
- **[Sales Forecast](../../examples/sales-forecast/)** -- SARIMA + Holt-Winters time series (statsmodels)
- **[Anomaly Detection](../../examples/anomaly-detection/)** -- Z-score + PELT change point detection (ruptures)
- **[Customer Survival](../../examples/customer-survival/)** -- Kaplan-Meier + Cox PH survival analysis (lifelines)
- **[Customer Churn Classification](../../examples/classification/)** -- Random Forest + Gradient Boosting (scikit-learn)
- **[Customer Segmentation](../../examples/clustering/)** -- K-Means + DBSCAN + GMM clustering (scikit-learn)
- **[Feature Importance](../../examples/feature-importance/)** -- PCA + Feature Selection + Model Comparison (scikit-learn)
- **[Call Center Queuing](../../examples/queuing-system/)** -- M/M/c queuing + DES verification (simpy)
- **[SIR Epidemic Model](../../examples/epidemic-sir/)** -- SIR ODE + vaccination analysis (scipy)
- **[Monte Carlo Project Risk](../../examples/monte-carlo-risk/)** -- MC risk simulation + convergence analysis (numpy)
- **[Root Finding & Interpolation](../../examples/root-finding/)** -- Bisection + Newton + Brent + cubic spline (scipy)
- **[Causal Inference](../../examples/causal-inference/)** -- Propensity matching + DiD + doubly robust (scikit-learn)
- **[Inventory Optimization](../../examples/inventory-optimization/)** -- EOQ + newsvendor + safety stock (scipy)
- **[Bin Packing](../../examples/bin-packing/)** -- First Fit Decreasing + ILP optimal (PuLP)

**Try your own problem.** Good candidates for `/uber-polya`:

- Scheduling (exams, meetings, shifts) -- graph coloring or ILP
- Assignment (people to tasks, resources to jobs) -- bipartite matching or ILP
- Routing (deliveries, network paths) -- shortest path, flow, TSP
- Counting (arrangements, combinations, probabilities) -- combinatorics, inclusion-exclusion
- Feasibility ("Is it possible to...?") -- SAT, constraint satisfaction
- Optimization (minimize cost, maximize profit) -- continuous optimization, convex QP
- Comparing groups ("Is A better than B?") -- hypothesis testing, A/B tests
- Prediction (forecast outcomes from data) -- regression, Bayesian inference
- Time series (forecasting, anomaly detection) -- SARIMA, change point detection
- Survival analysis (churn, equipment failure) -- Kaplan-Meier, Cox PH
- Machine learning (classification, clustering, feature selection) -- Random Forest, K-Means, PCA
- Simulation (queuing, epidemics, Monte Carlo risk) -- DES, SIR ODE, MC sampling
- Causal inference (treatment effects, policy evaluation) -- propensity matching, DiD
- Operations research (inventory, bin packing, lot sizing) -- EOQ, newsvendor, first-fit decreasing

Start with `/uber-polya <describe your problem in plain English>` and let Claude handle the rest.
