# uber-polya v0.2.0 Release Notes

**Don't guess. Solve.** The biggest release since launch -- 15 new mathematical domains, 20 new worked examples, and a complete documentation overhaul.

## What's New

### 15 New Mathematical Domains (v0.1.0 had 3)

uber-polya now covers **25 mathematical domains** with **305 algorithms**, **91 structures**, and **26 solver libraries**.

| Domain | Algorithms | Solver Libraries |
|--------|-----------|-----------------|
| Linear Algebra | 12 | numpy.linalg, scipy.linalg |
| Calculus | 10 | SymPy, scipy.integrate |
| Geometry & Trigonometry | 10 | shapely, scipy.spatial |
| Financial Mathematics | 8 | numpy-financial |
| Game Theory | 12 | nashpy |
| Decision Analysis | 10 | numpy, scipy |
| Multi-Objective Optimization | 8 | pymoo |
| Time Series Analysis | 15 | prophet, arch, ruptures |
| Stochastic Processes | 5 | scipy |
| Survival Analysis | 5 | lifelines |
| Machine Learning | 22 | scikit-learn, xgboost, umap-learn |
| Simulation & ODEs | 23 | simpy, scipy.integrate |
| Numerical Methods | 13 | scipy.optimize, scipy.interpolate |
| Causal Inference | 7 | dowhy, scikit-learn |
| Extended Operations Research | 8 | PuLP, OR-Tools |

### 20 New Worked Examples (v0.1.0 had 16)

**Everyday Problems** (11 total, +1 new):
- Mortgage Comparison -- NPV + amortization analysis

**Technical Showcases** (25 total, +19 new):

| Example | Domain | Algorithm |
|---------|--------|-----------|
| Traffic Flow | Linear algebra | Gaussian elimination |
| Water Tank | Calculus | Symbolic differentiation |
| Land Survey | Geometry | Shoelace + convex hull |
| Nash Equilibrium | Game theory | Support enumeration |
| Vendor Selection | Decision analysis | AHP + TOPSIS |
| Pareto Optimization | Multi-objective | Epsilon-constraint + Pareto filter |
| Sales Forecast | Time series | SARIMA + Holt-Winters |
| Anomaly Detection | Time series | Z-score + PELT change point |
| Customer Survival | Survival analysis | Kaplan-Meier + Cox PH |
| Customer Churn | Machine learning | Random Forest + Gradient Boosting |
| Customer Segmentation | Machine learning | K-Means + DBSCAN + GMM |
| Feature Importance | Machine learning | PCA + feature selection |
| Call Center Queuing | Queuing theory | M/M/c + simpy DES |
| SIR Epidemic Model | ODEs | SIR + vaccination analysis |
| Monte Carlo Risk | Simulation | MC risk + convergence |
| Root Finding | Numerical methods | Bisection + Newton + Brent |
| Causal Inference | Causal inference | Propensity matching + DiD |
| Inventory Optimization | Operations research | EOQ + newsvendor |
| Bin Packing | Operations research | FFD + ILP optimal |

Every example includes runnable Python code with independent `verify()` functions.

### Documentation Overhaul

- **Consistent navigation** across all 8 HTML doc pages: Docs, Tutorial, Manifesto, GitHub (with icon)
- **Expanded tutorial** with step-by-step instructions covering all 36 examples and 14 problem categories
- **Updated stats** throughout: 305 algorithms, 91 structures, 36 examples, 26 solver libraries, 24 domains
- **Expansion roadmap** now shows 18 shipped + 14 planned + 9 unlikely domains

### Manifesto Update

Title changed from "Every Problem Is a Math Problem" to "Most of Your Problems Are Math Problems" -- more accurate, less presumptuous.

## By the Numbers

| Metric | v0.1.0 | v0.2.0 |
|--------|--------|--------|
| Algorithms | 86 | **305** |
| Structures | 32 | **91** |
| Solver Libraries | 6 | **26** |
| Worked Examples | 16 | **36** |
| Domains | 3 | **25** |
| Chart Types | 14 | **37** |
| Heuristics | 17 | 17 |

## Installation

```bash
git clone https://github.com/agtm1199/uber-polya.git
cd uber-polya
bash install.sh
```

## Requirements

- Claude Code (Anthropic's CLI)
- Python 3.10+

Optional packages:
```bash
pip install networkx pulp z3-solver sympy scipy matplotlib numpy cvxpy statsmodels shapely numpy-financial nashpy pymoo prophet arch ruptures lifelines scikit-learn xgboost umap-learn simpy dowhy
```

## License

Apache 2.0 -- free to use, modify, and distribute.
