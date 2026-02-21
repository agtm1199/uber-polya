# Pareto Optimization -- Product Design Trade-offs

**Domain**: Multi-Objective Optimization
**Algorithm**: Epsilon-constraint method + Pareto filtering
**Key Concepts**: Pareto frontier, epsilon-constraint, knee point, trade-off rates, utopia/nadir points, non-dominance

## Problem

A manufacturing company designs a product with two competing objectives: minimize cost and maximize durability (equivalently, minimize inverse durability). There are 3 design variables -- material thickness, alloy grade, and coating level -- each with physical bounds. The goal is to find the Pareto frontier (the set of non-dominated designs), identify the knee point (best compromise), and quantify the trade-off rates along the frontier.

**Design Variables**:
- Material thickness: [1.0, 10.0] mm
- Alloy grade: [1.0, 5.0] (index)
- Coating level: [0.5, 3.0] (index)

**Objectives**:
- Minimize cost: f1(x) = 2*thickness + 5*alloy^2 + 3*coating
- Minimize inverse durability: f2(x) = -ln(thickness) - 2*alloy - 1.5*coating^0.8

## Files

| File | Description |
|------|-------------|
| `pareto_solver.py` | Epsilon-constraint Pareto solver with knee point detection, utopia/nadir computation, trade-off analysis, and independent verification |

## Requirements

```bash
pip install numpy scipy
```

## Quick Run

```bash
python3 pareto_solver.py
```

## Expected Output

- 50 candidate solutions generated via epsilon-constraint sweeps
- Pareto front filtered to ~20-40 non-dominated points
- Weighted-sum solutions for comparison
- Knee point identified at the point of maximum curvature
- Utopia point (infeasible ideal) and nadir point (worst of the bests)
- Trade-off rates (marginal rate of substitution) along the frontier
- Full independent verification (non-dominance, bounds, objective recomputation)
- Solution saved to `solution.json`

## Algorithm

1. **Individual optima**: Minimize each objective independently to establish the feasible objective range
2. **Epsilon-constraint sweep**: Fix one objective as a constraint (durability >= epsilon) and optimize the other (cost), sweeping epsilon across the feasible range
3. **Weighted-sum comparison**: Solve scalarized problems min w1*f1 + w2*f2 for a grid of weights
4. **Pareto filter**: Remove dominated points -- a point is dominated if another point is at least as good in all objectives and strictly better in at least one
5. **Knee point**: Find the point on the Pareto front with maximum curvature (largest angle formed by its neighbors), indicating the best marginal trade-off
6. **Utopia/nadir**: The utopia point is the (infeasible) vector of individually optimal objectives; the nadir point is the worst objective value attained by any Pareto-optimal solution in each dimension
7. **Trade-off rates**: Compute the marginal rate of substitution (delta f2 / delta f1) between consecutive Pareto points

## Key Concepts

- **Pareto optimality**: A solution is Pareto-optimal if no other feasible solution improves one objective without worsening another
- **Epsilon-constraint method**: Convert a multi-objective problem into a sequence of single-objective problems by constraining all but one objective
- **Knee point**: The point on the Pareto front where the trade-off rate changes most sharply -- often the best practical compromise
- **Utopia point**: The ideal (usually infeasible) point formed by the best value of each objective independently
- **Nadir point**: The worst objective values among Pareto-optimal solutions -- defines the "box" bounding the Pareto front
- **Marginal rate of substitution**: How much of one objective must be sacrificed to gain a unit of improvement in another
- **Non-dominance**: The defining property of Pareto-optimal solutions -- no other solution is at least as good in every objective
