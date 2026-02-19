# Portfolio Optimization Example

**Domain**: Continuous Optimization (Convex Quadratic Programming)
**Algorithm**: Markowitz mean-variance optimization via cvxpy
**Key Concepts**: Quadratic programming, efficient frontier, risk-return trade-off, sensitivity analysis

## Problem

An investor has $100,000 to allocate across 5 assets. Given historical expected returns and a covariance matrix, find the portfolio that maximizes return for a given risk tolerance -- and sweep across risk levels to generate the efficient frontier.

**Assets**: Tech, Healthcare, Energy, Bonds, Real Estate
**Constraints**: Fully invested (weights sum to 1), no short selling (weights >= 0)

## Files

| File | Description |
|------|-------------|
| `portfolio_solver.py` | Full solver with Markowitz QP, efficient frontier sweep, verification |
| `portfolio_viz.py` | Efficient frontier plot + allocation bar chart |

## Quick Run

```bash
pip install cvxpy numpy matplotlib
python portfolio_solver.py
python portfolio_viz.py
```

## Expected Output

```
=== Portfolio Optimization ===
Assets: Tech, Healthcare, Energy, Bonds, Real Estate

Minimum-variance portfolio:
  Tech:       5.2%
  Healthcare: 12.1%
  Energy:     3.4%
  Bonds:      62.8%
  Real Estate:16.5%
  Expected return: 6.82%
  Risk (std dev):  8.23%

Maximum-return portfolio:
  Tech:       100.0%
  Expected return: 12.00%
  Risk (std dev):  20.00%

Optimal portfolio (gamma=1.0):
  Tech:       22.4%
  Healthcare: 18.7%
  Energy:     8.1%
  Bonds:      31.2%
  Real Estate:19.6%
  Expected return: 8.45%
  Risk (std dev):  10.12%
  Verified: All constraints satisfied
```

## Algorithm

1. **Formulate** as convex QP: minimize x^T Σ x - γ μ^T x subject to 1^T x = 1, x >= 0
2. **Solve** via cvxpy (interior point, guaranteed global optimum for convex QP)
3. **Sweep** γ from 0 (min variance) to large (max return) to trace efficient frontier
4. **Verify** constraints and check KKT conditions

## Key Concepts

- **Convex optimization**: Global optimum guaranteed -- no local minima traps
- **Efficient frontier**: The set of Pareto-optimal risk-return trade-offs
- **Dual values**: Shadow prices tell you the cost of each constraint
- **DCP**: cvxpy's disciplined convex programming verifies convexity at construction time
