# Nash Equilibrium -- Coffee Shop Pricing

**Domain**: Game Theory
**Algorithm**: Support enumeration (nashpy)
**Key Concepts**: Normal-form games, Nash equilibrium, mixed strategies, dominant strategies, best responses, Pareto efficiency

## Problem

Two competing coffee shops on the same street decide simultaneously whether to run a promotion (discount) or hold prices. Each shop's profit depends on both its own action and its competitor's action:

- If both discount, they trigger a destructive price war ($2k each).
- If one discounts while the other holds, the discounter captures market share ($5k) while the holder loses traffic ($3k).
- If both hold prices, they share the market comfortably ($4k each).

This is an anti-coordination game (Game of Chicken variant): each shop wants to do the opposite of its competitor, but they move simultaneously without knowing the other's choice.

A second, richer variant adds a third strategy -- "loyalty program" -- creating a 3x3 symmetric game with circular dominance (Discount beats Hold, Hold beats Loyalty, Loyalty beats Discount), analogous to Rock-Paper-Scissors but with cooperative payoffs on the diagonal.

## Files

| File | Description |
|------|-------------|
| `nash_solver.py` | Full solver: support enumeration, dominant strategy detection, weak dominance, best response analysis, minimax strategies, Pareto analysis, verification |

## Requirements

```bash
pip install nashpy numpy scipy
```

## Quick Run

```bash
python3 nash_solver.py
```

## Expected Output

**2x2 Game (Discount vs Hold -- Anti-coordination)**:
- No strictly dominant strategy for either player
- Two pure-strategy Nash equilibria: (Discount, Hold) at ($5k, $3k) and (Hold, Discount) at ($3k, $5k)
- One mixed-strategy Nash equilibrium: each shop plays 50/50, expected payoff $3.50k each
- Security level: $3.00k/month (guaranteed by pure Hold maximin strategy)

**3x3 Game (Discount vs Hold vs Loyalty -- Circular Dominance)**:
- No strictly dominant or weakly dominated strategy
- Circular best-response structure: Loyalty beats Discount beats Hold beats Loyalty
- No pure-strategy Nash equilibrium (every pure profile is exploitable)
- Unique fully-mixed NE: (3/7 Discount, 1/3 Hold, 5/21 Loyalty)
- Expected payoff at NE: 79/21 ~ $3.762k/month each
- Pareto-dominated by several pure outcomes (e.g., Hold-Hold at $5k each)

## Algorithm

1. **Formulate** as bimatrix game (A, B) where A[i,j] is Player 1's payoff and B[i,j] is Player 2's payoff when Player 1 plays row i and Player 2 plays column j
2. **Enumerate** Nash equilibria via support enumeration (nashpy): for each pair of support sets, solve the indifference conditions
3. **Detect** strictly dominant and weakly dominated strategies
4. **Compute** best response correspondences for each pure strategy
5. **Compute** maximin (security level) strategies via linear programming (scipy)
6. **Analyze** Pareto efficiency of equilibrium outcomes
7. **Verify** independently that no player has a profitable unilateral deviation
8. **Cross-validate** with vertex enumeration to confirm all equilibria found

## Key Concepts

- **Normal-form game** -- a simultaneous-move game represented by payoff matrices
- **Nash equilibrium** -- a strategy profile where no player benefits from unilateral deviation
- **Mixed strategy** -- a probability distribution over pure strategies; the player randomizes
- **Dominant strategy** -- a strategy that yields strictly higher payoff regardless of opponent's choice
- **Best response** -- the optimal strategy given a fixed opponent strategy
- **Support enumeration** -- algorithm that checks all possible support pairs to find equilibria
- **Maximin strategy** -- the strategy that maximizes the player's guaranteed minimum payoff (security level)
- **Pareto efficiency** -- an outcome where no player can improve without making another worse off
- **Anti-coordination game** -- a game where players prefer to choose different strategies (Chicken/Hawk-Dove)
- **Circular dominance** -- a best-response cycle (like Rock-Paper-Scissors) that prevents pure-strategy equilibria
