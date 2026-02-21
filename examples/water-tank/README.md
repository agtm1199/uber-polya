# Water Tank Optimization

## Problem

Design an open-top cylindrical tank to hold 1000 liters using the least material (minimize surface area). The tank consists of a circular base and a cylindrical wall with no lid. Given a required volume V, find the radius r and height h that minimize the total sheet-metal area S = pi*r^2 + 2*pi*r*h subject to the volume constraint pi*r^2*h = V.

## Files

| File | Description |
|------|-------------|
| `tank_solver.py` | Symbolic calculus-based optimizer using SymPy for differentiation, critical point analysis, and second derivative test |

## Requirements

```bash
pip install sympy
```

## Quick Run

```bash
python3 tank_solver.py
```

## Expected Output

- Symbolic optimal radius: r* = (V / pi)^(1/3) for open-top
- Symbolic optimal height: h* = (V / pi)^(1/3) = r* (i.e., height equals radius for open-top)
- Numerical surface area for V = 1000 L (1.0 m^3): approximately 5.536 m^2
- Closed-top comparison: r* = (V / (2*pi))^(1/3), S slightly larger
- Material savings versus a cube of equal volume

## Algorithm

Symbolic differentiation and critical point analysis via SymPy. The volume constraint V = pi*r^2*h is used to eliminate h from the surface area expression S(r, h), yielding a single-variable function S(r). Taking dS/dr and setting it to zero gives the optimal radius. The second derivative test confirms the critical point is a minimum. The closed-top variant (S = 2*pi*r^2 + 2*pi*r*h) is solved analogously for comparison.

## Key Concepts

- **Optimization via calculus** -- minimizing a function subject to an equality constraint by substitution
- **Derivatives and critical points** -- setting dS/dr = 0 to find candidate optima
- **Second derivative test** -- confirming d^2S/dr^2 > 0 at the critical point to verify a minimum
- **Lagrange multipliers** -- equivalent formulation for constrained optimization (discussed in solver output)
- **Geometric insight** -- the optimal open-top cylinder has h = r; the optimal closed-top cylinder has h = 2r
