# uber-polya Examples

These examples demonstrate the complete uber-polya trilogy pipeline:
**Model** (formalize the problem), **Solve** (compute the answer), **Interpret** (explain the results).

## Examples

| Name | Domain | Algorithm | Key Concepts |
|------|--------|-----------|--------------|
| [milking-cows](milking-cows/) | Interval scheduling | Greedy sweep, O(N log N) | Interval merging, brute-force verification |
| [inspector-assignment](inspector-assignment/) | Resource allocation | Integer Linear Programming (PuLP/CBC) | Bipartite matching, LP relaxation, sensitivity analysis |
| [portfolio-optimization](portfolio-optimization/) | Continuous optimization | Convex QP (cvxpy, Markowitz) | Efficient frontier, risk-return trade-off, convex duality |
| [tournament-hamiltonian](tournament-hamiltonian/) | Graph theory proof | Induction + Z3 verification | Proof by induction, computational verification, constructive proof |
| [ab-testing](ab-testing/) | Statistical inference | z-test + Bayesian + bootstrap | Hypothesis testing, power analysis, Bayesian A/B |
| [cafe-tips](cafe-tips/) | Statistical inference | t-test + Mann-Whitney + bootstrap | Full Polya cycle, assumption checking, triple verification, effect sizes |

Each example includes solver code, visualization scripts, and sample data.
Detailed walkthroughs are in [docs/tutorials/](../docs/tutorials/).

## Requirements

Base (all examples):

```bash
pip install matplotlib numpy
```

Inspector assignment (ILP solver):

```bash
pip install pulp
```

Portfolio optimization (convex optimization):

```bash
pip install cvxpy
```

Tournament Hamiltonian (theorem prover):

```bash
pip install z3-solver
```

A/B testing and cafe tips (statistical inference):

```bash
pip install scipy statsmodels
```

Or install everything at once:

```bash
pip install matplotlib numpy pulp cvxpy z3-solver scipy statsmodels
```

## Note on Visualizations

Visualization outputs (`.png` files) are not committed to the repository.
Run the visualization scripts in each example directory to generate them.
