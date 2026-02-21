# uber-polya

**Don't guess. Solve.**

uber-polya is the first math problem-solver skill for Claude Code and 25+ compatible platforms. It's free, open-source, and turns real-world problems -- business or personal -- into mathematically verified solutions.

You describe what you're trying to figure out. uber-polya finds the mathematical structure hiding inside your problem, solves it with the right algorithm, checks the answer, and gives you the result: a schedule, a plan, a decision, a budget, a ranking, a proof -- whatever you need.

Describe your problem. Get a verified solution.

```
/uber-polya Schedule 12 nurses across 3 shifts so nobody works more than 5 days

uber-polya:
  1. Understands  -> "This is a constraint satisfaction problem"
  2. Models       -> ILP with 252 binary variables, 48 constraints
  3. Solves       -> Optimal schedule in 0.3 seconds
  4. Verifies     -> All constraints satisfied, optimality proven
  5. Delivers     -> A shift schedule you can use today
```

## What Can uber-polya Solve?

Every problem in this table has a mathematical structure. uber-polya finds it and solves it.

### Business Problems

| Problem | You say... | uber-polya finds... | You get... |
|---------|-----------|---------------------|-----------|
| Shift scheduling | "Schedule 12 nurses across 3 shifts" | Constraint satisfaction / ILP | A shift schedule (table) |
| Project selection | "Pick the best 5 of 20 projects under budget" | Knapsack optimization | Ranked list + ROI analysis |
| Task assignment | "Assign inspectors to regions, minimize travel" | Bipartite matching | Assignment matrix |
| Route planning | "Route 4 trucks across 30 delivery stops" | Vehicle routing (TSP variant) | Optimized routes + map |
| Pricing | "Price this product to maximize revenue" | Optimization with demand model | Recommended price + sensitivity |
| A/B testing | "Is this test result statistically real?" | Hypothesis testing | Yes/no + confidence + power analysis |
| Portfolio allocation | "Allocate investments to minimize risk" | Quadratic programming | Efficient frontier + allocation |
| Build vs. buy | "Should we build or buy this component?" | Decision tree / expected value | Recommendation + break-even |

### Personal Problems

| Problem | You say... | uber-polya finds... | You get... |
|---------|-----------|---------------------|-----------|
| Meal planning | "Plan meals for the week within budget" | Linear programming | Meal plan + grocery list |
| Rent splitting | "Split rent fairly among 3 roommates" | Fair division / allocation | Dollar amounts per person |
| Study schedule | "Schedule study sessions across 5 subjects" | Graph coloring / scheduling | Weekly study timetable |
| Apartment ranking | "Pick the best apartment from these 10" | Multi-criteria decision analysis | Ranked list + trade-offs |
| Expense splitting | "Split trip expenses among friends" | Fair allocation | Split table |
| Refinancing | "Should I refinance my mortgage?" | NPV / break-even analysis | Yes/no + savings timeline |

## Installation

```bash
git clone https://github.com/agtm1199/uber-polya.git
cd uber-polya
bash install.sh
```

The installer asks whether to install globally (`~/.claude/skills/`, available in all projects) or locally (`./.claude/skills/`, current project only).

## Quick Start

Open Claude Code and type:

```
/uber-polya I need to schedule 4 exams into time slots so no student has two exams at the same time.
```

uber-polya guides you through the complete pipeline:
1. **Understand** -- Socratic dialogue to extract what you really need
2. **Model** -- Classifies as graph coloring on a conflict graph
3. **Solve** -- Selects the right algorithm, writes verified solver code, runs it
4. **Interpret** -- Translates the answer, sensitivity analysis, visualizations, recommendations

Or use individual skills for more control:
- `/uber-model` -- formalize a problem into a mathematical model
- `/uber-solve` -- solve a mathematical model with the right algorithm
- `/uber-interpret` -- interpret and visualize a solution for stakeholders

## How It Works

uber-polya implements George Polya's four-phase problem-solving cycle (from *How to Solve It*, 1945) as an executable meta-algorithm:

```
/uber-polya (orchestrator)

/uber-model            /uber-solve             /uber-interpret
"What IS the           "What is the            "What does it
 problem?"              ANSWER?"                MEAN?"

 Real-world    -->     Formal Model    -->     Verified       -->    Actionable
 problem               (math)                 Solution              Insight

 Polya Phases          Polya Phase            Polya Phase
 1-2: Understand       3: Execute             4: Look Back
 & Plan
```

Each skill's output feeds the next. The pipeline is Socratic: uber-polya asks questions, you confirm understanding, and the solution is built collaboratively -- not dictated.

## Worked Examples

### Everyday Problems

| Example | Problem | Algorithm |
|---------|---------|-----------|
| [Shift Scheduling](examples/shift-scheduling/) | Schedule 8 nurses across 3 shifts over 7 days | ILP (PuLP/CBC) |
| [Budget Optimization](examples/budget-optimization/) | Select projects to maximize ROI under budget | 0/1 Knapsack ILP |
| [Fair Rent](examples/fair-rent/) | Split rent fairly among 3 roommates | Hungarian + envy-free adjustment |
| [Route Planning](examples/route-planning/) | Shortest delivery route across 8 stops | Held-Karp DP (exact TSP) |
| [Project Prioritization](examples/project-prioritization/) | Rank 8 features by weighted criteria | MCDA weighted scoring |
| [Study Schedule](examples/study-schedule/) | Conflict-free study timetable for 6 subjects | Graph coloring (NetworkX) |
| [Meal Planning](examples/meal-planning/) | Plan 7 dinners minimizing cost, meeting nutrition targets | ILP (PuLP/CBC) |
| [Team Assignment](examples/team-assignment/) | Assign 6 developers to 6 projects | Hungarian algorithm (SciPy) |
| [Break-Even Analysis](examples/break-even/) | Find break-even quantity for product launch | Symbolic algebra (SymPy) |
| [Event Seating](examples/event-seating/) | Seat 12 wedding guests at 3 tables with constraints | ILP (PuLP/CBC) |
| [Mortgage Comparison](examples/mortgage-analysis/) | Compare 3 mortgage options with refinancing analysis | NPV + amortization (numpy-financial) |

### Technical Showcases

| Example | Domain | Algorithm |
|---------|--------|-----------|
| [Milking Cows](examples/milking-cows/) | Interval merging | Sort + sweep, O(N log N) |
| [Inspector Assignment](examples/inspector-assignment/) | Bipartite ILP | PuLP/CBC solver |
| [Portfolio Optimization](examples/portfolio-optimization/) | Convex QP | cvxpy (Markowitz) |
| [Tournament Hamiltonian](examples/tournament-hamiltonian/) | Graph proof | Induction + Z3 |
| [A/B Testing](examples/ab-testing/) | Statistical inference | z-test + Bayesian + bootstrap |
| [Cafe Tips](examples/cafe-tips/) | Statistical inference | t-test + Mann-Whitney + bootstrap |
| [Traffic Flow](examples/traffic-flow/) | Linear algebra | Gaussian elimination (numpy) |
| [Water Tank](examples/water-tank/) | Calculus optimization | Symbolic differentiation (SymPy) |
| [Land Survey](examples/land-survey/) | Computational geometry | Shoelace + convex hull (shapely) |
| [Nash Equilibrium](examples/nash-equilibrium/) | Game theory | Support enumeration (nashpy) |
| [Vendor Selection](examples/vendor-selection/) | Decision analysis (MCDA) | AHP + TOPSIS (numpy) |
| [Pareto Optimization](examples/pareto-optimization/) | Multi-objective optimization | Epsilon-constraint + Pareto filter |
| [Sales Forecast](examples/sales-forecast/) | Time series analysis | SARIMA + Holt-Winters (statsmodels) |
| [Anomaly Detection](examples/anomaly-detection/) | Time series analysis | Z-score + PELT change point (ruptures) |
| [Customer Survival](examples/customer-survival/) | Survival analysis | Kaplan-Meier + Cox PH (lifelines) |
| [Customer Churn Classification](examples/classification/) | Machine learning | Random Forest + Gradient Boosting (scikit-learn) |
| [Customer Segmentation](examples/clustering/) | Machine learning | K-Means + DBSCAN + GMM (scikit-learn) |
| [Feature Importance](examples/feature-importance/) | Machine learning | PCA + Feature Selection + Model Comparison |
| [Call Center Queuing](examples/queuing-system/) | Queuing theory | M/M/c + simpy DES verification |
| [SIR Epidemic Model](examples/epidemic-sir/) | Numerical ODEs | SIR ODE + vaccination analysis (scipy) |
| [Monte Carlo Project Risk](examples/monte-carlo-risk/) | Simulation | MC risk simulation + convergence analysis |
| [Root Finding & Interpolation](examples/root-finding/) | Numerical methods | Bisection + Newton + Brent + cubic spline |
| [Causal Inference](examples/causal-inference/) | Causal inference | Propensity matching + DiD + doubly robust |
| [Inventory Optimization](examples/inventory-optimization/) | Operations research | EOQ + newsvendor + safety stock |
| [Bin Packing](examples/bin-packing/) | Operations research | First Fit Decreasing + ILP optimal |

## What's Under the Hood

### The Knowledge Base

305 algorithms, 91 structures, 17 heuristics, 26 solver libraries -- curated, cross-referenced, and organized for rapid problem-solving.

| Catalog | Entries |
|---------|---------|
| Polya's Heuristics | 17 heuristics with Socratic questions |
| Structure Catalog | 91 structures across 24 mathematical domains |
| Problem Classification | Decision tree + pattern table for rapid matching |
| Algorithm Catalogs | 305 algorithms (discrete math, continuous optimization, statistics, time series, stochastic processes, survival analysis, machine learning, simulation, queuing theory, ODEs, numerical methods, causal inference, extended OR, linear algebra, calculus, geometry, financial math, game theory, decision analysis, multi-objective optimization) |
| Solver Ecosystem | 26 Python libraries (NetworkX, PuLP, Z3, SymPy, SciPy, OR-Tools, cvxpy, statsmodels, PyMC, shapely, numpy-financial, nashpy, pymoo, prophet, arch, ruptures, lifelines, scikit-learn, xgboost, umap-learn, simpy, dowhy, and more) |
| Interpretation Patterns | Domain-specific math-to-reality translation |
| Visualization Guide | 37 chart types with matplotlib templates |

### Domains Covered

Graph Theory, Combinatorics, Set Theory, Logic, Number Theory, Relations & Orders, Optimization, Discrete Probability, Continuous Optimization, Statistical Inference, Time Series Analysis, Stochastic Processes, Survival Analysis, Machine Learning, Simulation & ODEs, Numerical Methods, Causal Inference, Extended Operations Research, Linear Algebra, Calculus, Geometry & Trigonometry, Financial Mathematics, Game Theory, Decision Analysis, Multi-Objective Optimization.

### Expansion Roadmap

| Domain | Status | What It Adds |
|--------|--------|--------------|
| Discrete Mathematics | Shipped | 86 algorithms, 32 structures, 8 solver libraries |
| Continuous Optimization | Shipped | 8 algorithms, 5 structures, cvxpy/scipy |
| Statistical Inference | Shipped | 45 algorithms, 6 structures, 6 solver libraries |
| Linear Algebra | Shipped | 12 algorithms, 4 structures, numpy.linalg/scipy.linalg |
| Calculus | Shipped | 10 algorithms, 3 structures, SymPy/scipy.integrate |
| Geometry & Trigonometry | Shipped | 10 algorithms, 4 structures, shapely/scipy.spatial |
| Financial Mathematics | Shipped | 8 algorithms, 1 structure, numpy-financial |
| Game Theory | Shipped | 12 algorithms, 3 structures, nashpy |
| Decision Analysis | Shipped | 10 algorithms, 3 structures, numpy/scipy |
| Multi-Objective Optimization | Shipped | 8 algorithms, 3 structures, pymoo |
| Time Series Analysis | Shipped | 15 algorithms, 3 structures, prophet/arch/ruptures |
| Stochastic Processes | Shipped | 5 algorithms, 3 structures, scipy |
| Survival Analysis | Shipped | 5 algorithms (3 new + 2 existing), lifelines |
| Machine Learning | Shipped | 22 algorithms, 5 structures, scikit-learn/xgboost/umap-learn |
| Simulation & ODEs | Shipped | 23 algorithms (10 ODE + 13 simulation), 8 structures, simpy/scipy.integrate |
| Numerical Methods | Shipped | 13 algorithms, 3 structures, scipy.optimize/interpolate/integrate |
| Causal Inference | Shipped | 7 algorithms, 2 structures, dowhy/scikit-learn |
| Extended Operations Research | Shipped | 8 algorithms, 3 structures, PuLP/OR-Tools |
| Partial Differential Equations | Planned | Heat, wave, diffusion equations -- FEniCS, FiPy |
| Dynamical Systems & Chaos | Planned | Stability, attractors, bifurcation analysis |
| Spatial Statistics | Planned | Geostatistics, spatial autocorrelation -- geopandas, PySAL |
| Spherical Geometry / Geodesy | Planned | Great circle distance, geodesic calculations -- geopy |
| Option Pricing | Planned | Black-Scholes, binomial lattice -- QuantLib |
| Risk Management | Planned | VaR, CVaR, stress testing |
| Agent-Based Modeling | Planned | Agent simulation, emergent behavior -- mesa |
| Fourier Analysis / Spectral Methods | Planned | FFT, spectral decomposition -- scipy.fft |
| Digital Signal Processing | Planned | Filtering, convolution, spectral analysis -- scipy.signal |
| Information Theory | Planned | Entropy, mutual information, KL divergence -- scipy.stats |
| Classical Control | Planned | PID control, stability margins -- python-control |
| Modern Control | Planned | State-space, LQR, Kalman filtering -- python-control, filterpy |
| Population Dynamics | Planned | Lotka-Volterra, predator-prey models (extends Simulation & ODEs) |
| Epidemiology | Planned | SIR, SEIR, compartmental models (extends Simulation & ODEs) |
| Abstract Algebra | Unlikely | Group theory, ring theory, field extensions |
| Real Analysis | Unlikely | Measure theory, convergence, completeness |
| Complex Analysis | Unlikely | Contour integration, conformal mapping, residues |
| Calculus of Variations | Unlikely | Euler-Lagrange, optimal control |
| Actuarial Science | Unlikely | Life tables, annuity pricing, loss models |
| Reinforcement Learning | Unlikely | MDP, Q-learning, policy gradient |
| Coding Theory | Unlikely | Error-correcting codes, Hamming, Reed-Solomon |
| Cryptography | Unlikely | RSA, elliptic curves, hash functions |
| Phylogenetics | Unlikely | Evolutionary trees, maximum likelihood |

Domains marked **Shipped** are fully integrated. **Planned** domains have clear implementation paths and are accepting contributions. **Unlikely** domains are outside the primary scope but could be added by community contributors. New domains plug in as reference files without changing the core Polya workflow. Contributions welcome -- see [CONTRIBUTING.md](CONTRIBUTING.md).

## Requirements

- **Claude Code** (Anthropic's CLI) -- the runtime for skills
- **Python 3.10+** -- for running generated solver code

Optional Python packages (installed as needed):

```bash
pip install networkx pulp z3-solver sympy scipy matplotlib numpy cvxpy statsmodels shapely numpy-financial nashpy pymoo prophet arch ruptures lifelines scikit-learn xgboost umap-learn simpy dowhy
```

## Design Principles

1. **Socratic, not didactic.** Asks questions that could have occurred to you. Never lectures.
2. **Verify everything.** Every solution includes independent verification.
3. **Right tool for the job.** Algorithm selection based on problem class and instance size.
4. **Audience adaptation.** Results adapted for technical, decision-maker, or general audiences.
5. **Knowledge transfer.** Every problem teaches a reusable modeling pattern.
6. **Modular expansion.** New domains plug in without changing the core workflow.

## Documentation

- [The Manifesto](docs/manifesto.md) -- Why most of your problems are math problems
- [Architecture](docs/architecture.md) -- How Polya's method maps to the skills
- [Getting Started](docs/tutorials/getting-started.md) -- Your first problem
- [Creating Skills](docs/creating-skills.md) -- Build on this framework
- [Contributing](CONTRIBUTING.md) -- Add algorithms, domains, or examples

## Cross-Platform Compatibility

uber-polya uses the Agent Skills open standard. It works on any platform that supports it:

- Claude Code (Anthropic)
- OpenAI Codex CLI
- Cursor
- GitHub Copilot
- Mistral Vibe
- And 25+ more

## License

[Apache 2.0](LICENSE) -- free to use, modify, and distribute.

## Acknowledgments

George Polya, *How to Solve It* (1945). The heuristic framework, Socratic questioning methodology, and four-phase problem-solving cycle that underpin this project are adapted from his work.
