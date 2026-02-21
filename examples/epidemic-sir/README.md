# SIR Epidemic Model

## Problem

A disease outbreak in a population of N=10,000. The transmission rate is beta=0.3/day and the recovery rate is gamma=0.1/day (10-day infectious period). Initially 10 individuals are infected, with the rest susceptible. Questions:

- What is the basic reproduction number R0?
- When does the infection peak, and how many are infected at the peak?
- What fraction of the population is ultimately infected?
- What vaccination rate prevents an epidemic (herd immunity threshold)?

## Files

| File | Description |
|------|-------------|
| `sir_solver.py` | ODE-based SIR solver using scipy.integrate.solve_ivp (RK45), with vaccination analysis, equilibrium stability, and 8 independent verification checks |

## Requirements

```bash
pip install numpy scipy
```

## Quick Run

```bash
python3 sir_solver.py
```

## Expected Output

- **R0**: 3.0
- **Peak infection**: around day ~30, with ~2,900 infected simultaneously
- **Final epidemic size**: ~94% of the population ultimately infected
- **Herd immunity threshold**: 67% vaccination rate prevents an epidemic
- **Vaccination analysis**: effective R0 drops below 1.0 at 67% coverage, preventing large outbreaks

## Key Concepts

- **SIR model** -- compartmental model dividing the population into Susceptible, Infected, and Recovered
- **Basic reproduction number (R0)** -- average number of secondary infections from one infected individual in a fully susceptible population
- **Herd immunity threshold** -- minimum fraction of the population that must be immune to prevent epidemic spread (1 - 1/R0)
- **Peak infection** -- the maximum number of simultaneously infected individuals, occurring when dI/dt = 0
- **Final size relation** -- transcendental equation R_inf = 1 - exp(-R0 * R_inf) relating R0 to the total fraction infected
- **Vaccination threshold** -- the vaccination rate v such that R0_eff = R0 * (1 - v) <= 1

## Domain

Numerical ODEs -- Dynamical Systems, Epidemic Modeling.
