<div align="center">

# uber-polya

**Don't guess. Solve.**

The first math problem-solver for AI coding assistants. Free, open-source, and works across 7+ platforms.

[![GitHub Stars](https://img.shields.io/github/stars/agtm1199/uber-polya?style=social)](https://github.com/agtm1199/uber-polya/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/agtm1199/uber-polya?style=social)](https://github.com/agtm1199/uber-polya/network/members)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-1.0.0-green.svg)](CHANGELOG.md)
[![CI](https://github.com/agtm1199/uber-polya/actions/workflows/ci.yml/badge.svg)](https://github.com/agtm1199/uber-polya/actions/workflows/ci.yml)

[Docs](https://agtm1199.github.io/uber-polya/guide.html) | [Tutorial](https://agtm1199.github.io/uber-polya/getting-started.html) | [Manifesto](https://agtm1199.github.io/uber-polya/manifesto.html) | [Contributing](CONTRIBUTING.md)

<!-- Add social links once created:
[![Discord](https://img.shields.io/badge/Discord-Join-5865F2?style=flat&logo=discord&logoColor=white)](YOUR_DISCORD_LINK)
[![X (Twitter)](https://img.shields.io/badge/Follow-000000?style=flat&logo=x&logoColor=white)](YOUR_X_LINK)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat&logo=linkedin&logoColor=white)](YOUR_LINKEDIN_LINK)
-->

</div>

---

You describe what you're trying to figure out. uber-polya finds the mathematical structure hiding inside your problem, solves it with the right algorithm, checks the answer, and gives you the result: a schedule, a plan, a decision, a budget, a ranking, a proof -- whatever you need.

```
/uber-polya Schedule 12 nurses across 3 shifts so nobody works more than 5 days

uber-polya:
  1. Understands  -> "This is a constraint satisfaction problem"
  2. Models       -> ILP with 252 binary variables, 48 constraints
  3. Solves       -> Optimal schedule in 0.3 seconds
  4. Verifies     -> All constraints satisfied, optimality proven
  5. Delivers     -> A shift schedule you can use today
```

Describe your problem. Get a verified solution. That's it.

---

<details>
<summary><strong>Why uber-polya?</strong></summary>

<br>

Most real-world problems -- business or personal -- have a mathematical structure hiding inside them. Scheduling is graph coloring. Budgeting is linear programming. Pricing is optimization. Route planning is TSP. But finding that structure, picking the right algorithm, writing correct solver code, and verifying the answer takes expertise most people don't have.

uber-polya does all of that in one conversation. It implements George Polya's four-phase problem-solving cycle (*How to Solve It*, 1945) as an executable pipeline:

1. **Understand** -- Socratic dialogue to extract what you really need
2. **Model** -- Finds the mathematical structure, classifies the problem
3. **Solve** -- Selects the right algorithm, writes verified solver code, runs it
4. **Interpret** -- Translates the answer into actionable insight with visualizations

The pipeline is collaborative: uber-polya asks questions, you confirm understanding, and the solution is built together -- not dictated.

</details>

## Quick Start

**1. Install**

```bash
git clone https://github.com/agtm1199/uber-polya.git
cd uber-polya
bash install.sh
```

The installer asks whether to install globally (`~/.claude/skills/`, available in all projects) or locally (`./.claude/skills/`, current project only).

**2. Solve a problem**

Open Claude Code and type:

```
/uber-polya I need to schedule 4 exams into time slots so no student has two exams at the same time.
```

**3. Get a verified result**

uber-polya handles the entire pipeline automatically. One command, one conversation, one verified result.

Under the hood, `/uber-polya` orchestrates three internal skills (`/uber-model`, `/uber-solve`, `/uber-interpret`) that you can also use individually for finer control.

---

## How It Works

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

Each skill's output feeds the next. The pipeline is Socratic: uber-polya asks questions, you confirm understanding, and the solution is built collaboratively.

---

## What Can uber-polya Solve?

Every problem in these tables has a mathematical structure. uber-polya finds it and solves it.

<details>
<summary><strong>Business Problems</strong> (18 problem types)</summary>

<br>

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
| Sales forecasting | "Forecast next quarter's revenue" | Time series (SARIMA / Holt-Winters) | Forecast + confidence intervals |
| Customer churn | "Predict which customers will leave" | Classification (Random Forest) | Risk scores + key factors |
| Training impact | "Did our training program boost sales?" | Causal inference (DiD / propensity) | Effect size + confidence interval |
| Call center staffing | "How many agents for 95% SLA?" | Queuing theory (M/M/c) | Staffing table + cost analysis |
| Subscriber retention | "When will customers cancel?" | Survival analysis (Cox PH) | Survival curves + risk factors |
| Inventory ordering | "How much to order, when to reorder?" | Inventory optimization (EOQ) | Order quantity + reorder point |
| Container loading | "Pack 50 shipments into fewest trucks" | Bin packing (ILP) | Packing plan + utilization |
| Vendor ranking | "Rank vendors balancing cost, quality, speed" | Multi-objective optimization (Pareto) | Pareto frontier + trade-offs |
| Product configuration | "Can we build this with all customer requirements?" | SAT / constraint satisfaction | Valid configuration or proof of infeasibility |
| Demand patterns | "Model customer arrival patterns for staffing" | Stochastic processes (Markov / Poisson) | Arrival model + peak hours |

</details>

<details>
<summary><strong>Personal Problems</strong> (15 problem types)</summary>

<br>

| Problem | You say... | uber-polya finds... | You get... |
|---------|-----------|---------------------|-----------|
| Meal planning | "Plan meals for the week within budget" | Linear programming | Meal plan + grocery list |
| Rent splitting | "Split rent fairly among 3 roommates" | Fair division / allocation | Dollar amounts per person |
| Study schedule | "Schedule study sessions across 5 subjects" | Graph coloring / scheduling | Weekly study timetable |
| Apartment ranking | "Pick the best apartment from these 10" | Multi-criteria decision analysis | Ranked list + trade-offs |
| Expense splitting | "Split trip expenses among friends" | Fair allocation | Split table |
| Refinancing | "Should I refinance my mortgage?" | NPV / break-even analysis | Yes/no + savings timeline |
| Budget forecasting | "Will I stay within budget this year?" | Time series forecasting | Monthly forecast + alerts |
| Garden fencing | "Maximize garden area with 100 ft of fence" | Calculus optimization | Optimal dimensions + layout |
| Room painting | "How much paint for these oddly-shaped rooms?" | Computational geometry | Quantity + cost estimate |
| Solar payback | "When does my solar panel investment pay off?" | Root finding / break-even | Payback date + savings curve |
| Recipe scaling | "Scale this recipe for 50 people" | Linear algebra (systems of equations) | Adjusted ingredient quantities |
| Raffle odds | "What are my chances of winning this raffle?" | Discrete probability | Probability + expected value |
| Medication timing | "When do drug levels peak and trough?" | ODE modeling (pharmacokinetics) | Dosing schedule + level chart |
| Moving logistics | "Fit all furniture into fewest truck loads" | Bin packing | Loading plan + trips needed |
| House hunting | "Balance commute, price, and schools across 15 houses" | Multi-objective optimization (Pareto) | Shortlist of non-dominated options |

</details>

---

## Worked Examples

36 fully worked examples with solver code, verification, and sample output.

<details>
<summary><strong>Everyday Problems</strong> (11 examples)</summary>

<br>

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

</details>

<details>
<summary><strong>Technical Showcases</strong> (25 examples)</summary>

<br>

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

</details>

---

## What's Under the Hood

<details>
<summary><strong>The Knowledge Base</strong> -- 305 algorithms, 91 structures, 26 solver libraries</summary>

<br>

| Catalog | Entries |
|---------|---------|
| Polya's Heuristics | 17 heuristics with Socratic questions |
| Structure Catalog | 91 structures across 24 mathematical domains |
| Problem Classification | Decision tree + pattern table for rapid matching |
| Algorithm Catalogs | 305 algorithms (discrete math, continuous optimization, statistics, time series, stochastic processes, survival analysis, machine learning, simulation, queuing theory, ODEs, numerical methods, causal inference, extended OR, linear algebra, calculus, geometry, financial math, game theory, decision analysis, multi-objective optimization) |
| Solver Ecosystem | 26 Python libraries (NetworkX, PuLP, Z3, SymPy, SciPy, OR-Tools, cvxpy, statsmodels, PyMC, shapely, numpy-financial, nashpy, pymoo, prophet, arch, ruptures, lifelines, scikit-learn, xgboost, umap-learn, simpy, dowhy, and more) |
| Interpretation Patterns | Domain-specific math-to-reality translation |
| Visualization Guide | 37 chart types with matplotlib templates |

</details>

<details>
<summary><strong>25 Domains Covered</strong></summary>

<br>

Graph Theory, Combinatorics, Set Theory, Logic, Number Theory, Relations & Orders, Optimization, Discrete Probability, Continuous Optimization, Statistical Inference, Time Series Analysis, Stochastic Processes, Survival Analysis, Machine Learning, Simulation & ODEs, Numerical Methods, Causal Inference, Extended Operations Research, Linear Algebra, Calculus, Geometry & Trigonometry, Financial Mathematics, Game Theory, Decision Analysis, Multi-Objective Optimization.

</details>

<details>
<summary><strong>Expansion Roadmap</strong></summary>

<br>

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

Domains marked **Shipped** are fully integrated. **Planned** domains have clear implementation paths and are accepting contributions. New domains plug in as reference files without changing the core Polya workflow.

</details>

---

## Cross-Platform Compatibility

uber-polya ships native instruction files for 7+ AI coding assistants. Each tool gets the full Polya methodology (Model -> Solve -> Interpret) through its native config format.

<p align="center">
  <img src="https://img.shields.io/badge/Claude_Code-191919?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code" />
  <img src="https://img.shields.io/badge/OpenAI_Codex-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI Codex" />
  <img src="https://img.shields.io/badge/GitHub_Copilot-000000?style=for-the-badge&logo=githubcopilot&logoColor=white" alt="GitHub Copilot" />
  <img src="https://img.shields.io/badge/Cursor-000000?style=for-the-badge&logo=cursor&logoColor=white" alt="Cursor" />
  <img src="https://img.shields.io/badge/Windsurf-5865F2?style=for-the-badge&logo=codeium&logoColor=white" alt="Windsurf" />
  <img src="https://img.shields.io/badge/Amazon_Kiro-FF9900?style=for-the-badge&logo=amazon&logoColor=white" alt="Amazon Kiro" />
  <img src="https://img.shields.io/badge/Qoder-1E90FF?style=for-the-badge&logo=alibabadotcom&logoColor=white" alt="Qoder" />
  <img src="https://img.shields.io/badge/Antigravity-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Antigravity" />
</p>

<details>
<summary><strong>Platform config details</strong></summary>

<br>

| Tool | Config File(s) | Format |
|---|---|---|
| ![Anthropic](https://img.shields.io/badge/-Anthropic-191919?style=flat-square&logo=anthropic&logoColor=white) **Claude Code** | `CLAUDE.md` + `skills/*/SKILL.md` | Skills with YAML frontmatter |
| ![OpenAI](https://img.shields.io/badge/-OpenAI-412991?style=flat-square&logo=openai&logoColor=white) **Codex** | `AGENTS.md` | Plain markdown (cross-tool standard) |
| ![Copilot](https://img.shields.io/badge/-Copilot-000000?style=flat-square&logo=githubcopilot&logoColor=white) **GitHub Copilot** | `.github/copilot-instructions.md` + `AGENTS.md` | Markdown |
| ![Cursor](https://img.shields.io/badge/-Cursor-000000?style=flat-square&logo=cursor&logoColor=white) **Cursor** | `.cursor/rules/uber-polya.mdc`, `solver-conventions.mdc` | Markdown with glob targeting |
| ![Windsurf](https://img.shields.io/badge/-Windsurf-5865F2?style=flat-square&logo=codeium&logoColor=white) **Windsurf** | `.windsurf/rules/uber-polya.md`, `solver-conventions.md` | Markdown |
| ![Kiro](https://img.shields.io/badge/-Kiro-FF9900?style=flat-square&logo=amazon&logoColor=white) **Amazon Kiro** | `.kiro/steering/uber-polya.md`, `solver-conventions.md` | Markdown with YAML frontmatter |
| ![Qoder](https://img.shields.io/badge/-Qoder-1E90FF?style=flat-square&logo=alibabadotcom&logoColor=white) ![Antigravity](https://img.shields.io/badge/-Antigravity-4285F4?style=flat-square&logo=google&logoColor=white) **+ others** | `AGENTS.md` | Cross-tool standard (60K+ repos) |

The reference files (`skills/*/references/`) are pure markdown -- readable by any tool. The 36 worked examples use standard Python with no tool-specific dependencies.

</details>

---

## Requirements

- **Claude Code** (Anthropic's CLI) -- the runtime for skills
- **Python 3.10+** -- for running generated solver code

<details>
<summary><strong>Optional Python packages</strong> (installed as needed)</summary>

<br>

```bash
pip install networkx pulp z3-solver sympy scipy matplotlib numpy cvxpy statsmodels shapely numpy-financial nashpy pymoo prophet arch ruptures lifelines scikit-learn xgboost umap-learn simpy dowhy
```

</details>

---

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

## Contributing

Contributions welcome! Whether it's a new domain, algorithm, worked example, or bug fix -- see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Please note that this project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).

## Citation

If you use uber-polya in your work, please cite it:

```bibtex
@software{uber_polya,
  title = {uber-polya: Universal Problem-Solving Engine},
  url = {https://github.com/agtm1199/uber-polya},
  license = {Apache-2.0},
  year = {2025}
}
```

Or in text:

> uber-polya: Universal Problem-Solving Engine. https://github.com/agtm1199/uber-polya. Apache-2.0 License.

## License

[Apache 2.0](LICENSE) -- free to use, modify, and distribute.

## Acknowledgments

George Polya, *How to Solve It* (1945). The heuristic framework, Socratic questioning methodology, and four-phase problem-solving cycle that underpin this project are adapted from his work.

---

<div align="center">

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=agtm1199/uber-polya&type=Date)](https://star-history.com/#agtm1199/uber-polya&Date)

</div>
