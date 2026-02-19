# Break-Even Analysis

## Problem

A small business is considering launching a new product. Fixed costs are $25,000 (tooling, marketing). Variable cost per unit is $12. Selling price per unit is $35. What is the break-even quantity? How does the break-even point shift if the price drops 10% or variable costs increase 20%?

## Files

| File | Description |
|------|-------------|
| `breakeven_solver.py` | Symbolic break-even solver with sensitivity analysis using sympy and numpy |

## Requirements

```bash
pip install sympy numpy
```

## Quick Run

```bash
python3 breakeven_solver.py
```

## Expected Output

- Exact symbolic break-even quantity: Q = Fixed / (Price - Variable)
- Base case: ~1087 units
- Sensitivity table showing break-even under price drops and cost increases
- Profit projections at various production volumes

## Algorithm

Symbolic algebra via SymPy to derive the closed-form break-even formula, then numerical evaluation with NumPy for sensitivity analysis. Break-even occurs where Revenue(Q) = Cost(Q), i.e., P*Q = F + V*Q, yielding Q* = F / (P - V). Sensitivity sweeps over price and variable cost perturbations.

## Key Concepts

- **Break-even analysis** -- finding the production volume where profit turns positive
- **Symbolic computation** -- deriving exact formulas with SymPy
- **Sensitivity analysis** -- understanding how parameter changes affect the result
- **Contribution margin** -- Price minus Variable cost per unit
- **Business decision modeling** -- translating financial questions into mathematical models
