# Debt Payoff Optimization

**Domain**: Financial Mathematics (Debt Repayment)
**Algorithm**: Greedy month-by-month simulation (Avalanche vs Snowball)
**Key Concepts**: Debt avalanche, debt snowball, greedy allocation, amortization, interest minimization

## Problem

You have 4 debts with different balances, interest rates, and minimum payments:

| Debt | Balance | APR | Min Payment |
|------|---------|-----|-------------|
| Credit Card | $6,200 | 22.99% | $120/mo |
| Car Loan | $12,000 | 6.50% | $250/mo |
| Student Loan | $25,000 | 4.50% | $280/mo |
| Personal Loan | $3,500 | 15.00% | $75/mo |

**Total debt**: $46,700. **Total minimums**: $725/mo. **Extra available**: $500/mo.

Find the optimal allocation of extra payments to minimize total interest paid
over time. Compare two strategies:

1. **Avalanche** (highest interest rate first) -- mathematically optimal among
   greedy single-target strategies
2. **Snowball** (lowest balance first) -- psychologically motivating but costs
   more in interest

## Files

| File | Description |
|------|-------------|
| `debt_solver.py` | Month-by-month simulation with avalanche and snowball strategies |
| `solution.json` | Computed results with both strategies and comparison |

## Requirements

No external dependencies beyond Python 3.10+ standard library.

```bash
# No pip install needed
```

## Quick Run

```bash
python3 debt_solver.py
```

## Expected Output

- Total interest paid under each strategy
- Months to complete payoff under each strategy
- Head-to-head comparison table showing interest savings
- Payoff timeline showing when each debt reaches zero (avalanche)
- Independent verification (5 checks per strategy)

## Algorithm

Month-by-month greedy simulation:

1. **Accrue interest** on all debts (monthly_rate = APR / 12)
2. **Pay minimums** on every debt with remaining balance
3. **Allocate extra** (plus freed minimums from paid-off debts) to the
   highest-priority target debt
4. **Cascade surplus** -- if the target is paid off mid-allocation, redirect
   remaining funds to the next priority debt
5. Repeat until all balances reach zero

The **avalanche** strategy prioritizes debts by descending APR, which is provably
optimal because it minimizes the balance-weighted average interest rate at every
step. The **snowball** strategy prioritizes by ascending balance for faster
psychological wins.

## Key Concepts

- **Debt avalanche** -- always attack the highest interest rate first to minimize total cost
- **Debt snowball** -- pay off smallest balances first for quick wins and motivation
- **Freed minimum cascading** -- when a debt is eliminated, its minimum payment redirects to the next target, accelerating payoff
- **Greedy allocation** -- at each step, commit all available extra funds to one target rather than splitting
- **Amortization with extra payments** -- how additional principal payments reduce both the timeline and total interest
