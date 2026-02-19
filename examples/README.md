# uber-polya Examples

These examples demonstrate the complete uber-polya pipeline:
**Model** (formalize the problem), **Solve** (compute the answer), **Interpret** (explain the results).

## Everyday Problems

These examples show uber-polya solving real-world problems that anyone might face.

| Name | Problem | Algorithm | Key Concepts |
|------|---------|-----------|--------------|
| [shift-scheduling](shift-scheduling/) | Schedule 8 nurses across 3 shifts over 7 days | ILP (PuLP/CBC) | Constraint satisfaction, staffing constraints, night shift rules |
| [budget-optimization](budget-optimization/) | Select projects to maximize ROI under $500K budget | 0/1 Knapsack ILP (PuLP) | Knapsack optimization, efficiency analysis, budget sensitivity |
| [fair-rent](fair-rent/) | Split $3000 rent fairly among 3 roommates | Hungarian + envy-free adjustment (SciPy) | Fair division, envy-freeness, proportionality |
| [route-planning](route-planning/) | Shortest route visiting 8 delivery stops | Held-Karp DP (exact TSP) | Traveling salesman, bitmask DP, nearest-neighbor comparison |
| [project-prioritization](project-prioritization/) | Rank 8 features by 4 weighted criteria | MCDA weighted scoring (NumPy) | Multi-criteria decision analysis, normalization, weight sensitivity |
| [study-schedule](study-schedule/) | Create conflict-free study timetable for 6 subjects | Graph coloring (NetworkX) | Conflict graphs, chromatic number, adjacency constraints |
| [meal-planning](meal-planning/) | Plan 7 dinners minimizing cost within nutrition targets | ILP (PuLP/CBC) | Linear programming, nutrition constraints, cost optimization |
| [team-assignment](team-assignment/) | Assign 6 developers to 6 projects maximizing satisfaction | Hungarian algorithm (SciPy) | Bipartite matching, assignment problem, Monte Carlo comparison |
| [break-even](break-even/) | Find break-even quantity for a new product launch | Symbolic algebra (SymPy) | Break-even analysis, contribution margin, price sensitivity |
| [event-seating](event-seating/) | Seat 12 wedding guests at 3 tables with constraints | ILP (PuLP/CBC) | Constrained partitioning, must-together/apart, quadratic linearization |

## Technical Showcases

These examples demonstrate specific mathematical domains and techniques.

| Name | Domain | Algorithm | Key Concepts |
|------|--------|-----------|--------------|
| [milking-cows](milking-cows/) | Interval scheduling | Greedy sweep, O(N log N) | Interval merging, brute-force verification |
| [inspector-assignment](inspector-assignment/) | Resource allocation | ILP (PuLP/CBC) | Bipartite matching, LP relaxation, sensitivity analysis |
| [portfolio-optimization](portfolio-optimization/) | Continuous optimization | Convex QP (cvxpy, Markowitz) | Efficient frontier, risk-return trade-off, convex duality |
| [tournament-hamiltonian](tournament-hamiltonian/) | Graph theory proof | Induction + Z3 verification | Proof by induction, computational verification |
| [ab-testing](ab-testing/) | Statistical inference | z-test + Bayesian + bootstrap | Hypothesis testing, power analysis, Bayesian A/B |
| [cafe-tips](cafe-tips/) | Statistical inference | t-test + Mann-Whitney + bootstrap | Full Polya cycle, assumption checking, effect sizes |

Each example includes solver code, independent verification, and sample data.
Detailed walkthroughs are in [docs/tutorials/](../docs/tutorials/).

## Requirements

Base (all examples):

```bash
pip install matplotlib numpy
```

ILP examples (shift-scheduling, budget-optimization, meal-planning, event-seating, inspector-assignment):

```bash
pip install pulp
```

Fair division and assignment (fair-rent, team-assignment):

```bash
pip install scipy
```

Break-even analysis:

```bash
pip install sympy
```

Graph coloring (study-schedule):

```bash
pip install networkx
```

Portfolio optimization:

```bash
pip install cvxpy
```

Theorem proving (tournament-hamiltonian):

```bash
pip install z3-solver
```

Statistical inference (ab-testing, cafe-tips):

```bash
pip install scipy statsmodels
```

Or install everything at once:

```bash
pip install matplotlib numpy pulp scipy sympy networkx cvxpy z3-solver statsmodels
```

## Note on Visualizations

Visualization outputs (`.png` files) are not committed to the repository.
Run the visualization scripts in each example directory to generate them.
