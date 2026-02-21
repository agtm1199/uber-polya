# Quick-Reference Problem Classification

Rapid pattern matching to go from a real-world problem description to a named mathematical problem, structure, algorithm, and solver. Use this at the start of Phase 2 in uber-model (before reading the full structures.md) or during fast-track mode in uber-polya.

---

## Decision Tree

Start here. Follow the branch that best matches the problem.

```
What is the user trying to do?
│
├─ ASSIGN things to things (people→tasks, resources→needs)
│  ├─ Two groups, one-to-one? ──────────── Bipartite Matching (A15-A17)
│  ├─ Two groups, with preferences? ────── Stable Matching (A17)
│  ├─ One-to-many with capacity? ───────── ILP Assignment (A32)
│  └─ Minimize total cost? ─────────────── Hungarian / linear_sum_assignment (A16)
│
├─ SCHEDULE things (events, tasks, exams)
│  ├─ Avoid conflicts (no overlap)? ────── Graph Coloring (A21-A22)
│  ├─ Respect dependencies (ordering)? ── Topological Sort / Critical Path (A3, A12)
│  ├─ Minimize total time (makespan)? ──── Scheduling ILP (A32) / CP-SAT
│  └─ Select max non-overlapping? ──────── Activity Selection (A43)
│
├─ ROUTE / NAVIGATE (find best path)
│  ├─ Point A to point B? ──────────────── Shortest Path (A8-A11)
│  ├─ Visit all locations? ─────────────── TSP (A28-A30)
│  ├─ Multiple vehicles? ───────────────── Vehicle Routing (OR-Tools)
│  └─ Maximum throughput? ──────────────── Max Flow (A19-A20)
│
├─ SELECT / PACK (choose items under constraints)
│  ├─ Budget/weight limit? ─────────────── Knapsack (A33-A34)
│  ├─ Cover all requirements? ──────────── Set Cover (A47)
│  ├─ Binary yes/no decisions? ─────────── ILP (A32) / SAT (A48)
│  └─ Multi-criteria trade-off? ────────── Multi-objective ILP / Pareto
│
├─ GROUP / PARTITION (classify, cluster)
│  ├─ Into non-overlapping groups? ──────── Set Partition / Graph Partition
│  ├─ By equivalence (same type)? ──────── Equivalence Classes
│  ├─ Balanced groups? ──────────────────── Balanced Partition ILP
│  └─ Find natural clusters? ────────────── Community Detection (NetworkX)
│
├─ COUNT arrangements
│  ├─ Order matters? ────────────────────── Permutations (A63)
│  ├─ Order doesn't matter? ─────────────── Combinations (A64)
│  ├─ With symmetry (rotations)? ────────── Burnside's Lemma (A67)
│  ├─ With overlapping conditions? ──────── Inclusion-Exclusion (A66)
│  └─ Recurrence pattern? ──────────────── DP / Generating Functions (A68)
│
├─ PROVE a mathematical statement
│  ├─ "For all n..." ────────────────────── Mathematical Induction (A74)
│  ├─ "It's impossible..." ──────────────── Contradiction (A75) / Pigeonhole (A77)
│  ├─ "There exists..." ─────────────────── Constructive Proof (A76) / Z3 (A48)
│  └─ Verify a logical claim? ──────────── Z3 SAT/SMT (A48-A50)
│
├─ ANALYZE a network
│  ├─ Find vulnerabilities? ─────────────── Articulation Points / Bridges (A6)
│  ├─ Find communities? ─────────────────── SCC (A5) / Connected Components (A7)
│  ├─ Find most important nodes? ────────── Centrality (NetworkX)
│  └─ Find bottlenecks? ─────────────────── Min Cut / Max Flow (A19)
│
├─ SATISFY constraints (feasibility)
│  ├─ Boolean constraints? ──────────────── SAT (A48)
│  ├─ Integer constraints? ──────────────── SMT / Z3 (A49)
│  ├─ Configuration / Sudoku-like? ──────── CSP (A51-A52)
│  └─ Linear constraints? ──────────────── LP Feasibility (A31)
│
├─ OPTIMIZE a continuous quantity
│  ├─ Convex objective + constraints? ──── cvxpy / Convex Program (A87)
│  ├─ Quadratic cost, linear constraints? ─ QP (A88)
│  ├─ Fit a model to data? ─────────────── Least Squares (A91) / Gauss-Newton (A92)
│  ├─ Smooth, no constraints? ──────────── BFGS (A89) / Gradient Descent (A90)
│  └─ Nonlinear constraints? ───────────── SLSQP / trust-constr (A93)
│
├─ ASSESS probability / risk
│  ├─ What are the odds? ────────────────── Combinatorial Probability
│  ├─ Expected outcome? ─────────────────── Expected Value (A78)
│  ├─ Long-run behavior? ────────────────── Markov Chain (A80)
│  └─ Estimate via simulation? ──────────── Monte Carlo (A81)
│
├─ SOLVE equations / linear systems
│  ├─ System of linear equations? ────────── Gaussian Elimination (A95) / numpy.linalg.solve
│  ├─ Find eigenvalues / modes? ──────────── Eigenvalue Computation (A97)
│  ├─ Reduce dimensions / compress? ──────── SVD (A98)
│  ├─ Solve symbolically? ────────────────── SymPy solve
│  └─ Matrix too large for direct? ──────── Iterative (scipy.sparse)
│
├─ DIFFERENTIATE / INTEGRATE / solve ODE
│  ├─ Rate of change / derivative? ──────── Symbolic Differentiation (A107)
│  ├─ Total / area under curve? ─────────── Symbolic (A108) or Numerical (A109) Integration
│  ├─ Find critical points / optimize? ──── Set f'=0, Second Derivative Test (A107, A113)
│  ├─ Constrained with equalities? ──────── Lagrange Multipliers (A114)
│  ├─ ODE with exact solution? ──────────── SymPy dsolve (A115)
│  └─ ODE (numerical / complex)? ────────── solve_ivp (A116)
│
├─ MEASURE geometry (area, volume, distance, shape)
│  ├─ Area of a region / polygon? ────────── Shoelace / shapely (A117)
│  ├─ Volume of a solid? ─────────────────── Formulas / Integration (A118)
│  ├─ Distance between points? ───────────── Euclidean / scipy.spatial (A119)
│  ├─ Convex hull / bounding region? ─────── ConvexHull (A120)
│  ├─ Nearest neighbor / closest? ────────── KDTree (A123)
│  ├─ Triangle problem (sides/angles)? ──── Law of Cosines/Sines (A125)
│  └─ Spatial partition / zones? ─────────── Voronoi (A121)
│
├─ EVALUATE finances (investment, loan, savings)
│  ├─ Is an investment worth it? ──────────── NPV (A127) / IRR (A128)
│  ├─ What's my loan payment? ─────────────── PMT (A129)
│  ├─ Amortization breakdown? ─────────────── Amortization Schedule (A130)
│  ├─ How much will savings grow? ─────────── Compound Interest (A131) / FV
│  ├─ Value of regular payments? ──────────── Annuity Valuation (A132)
│  ├─ When do I break even? ───────────────── Break-Even (A133)
│  └─ Should I refinance? ─────────────────── Refinancing Comparison (A134)
│
├─ COMPETE / NEGOTIATE (strategic interaction)
│  ├─ Two players, simultaneous moves? ────── Nash Equilibrium (A135-A136)
│  ├─ Zero-sum competition? ───────────────── Minimax (A137)
│  ├─ Share costs / divide profits? ────────── Shapley Value (A138) / Nucleolus (A144)
│  ├─ Divide items fairly? ────────────────── Fair Division (A139-A140)
│  ├─ Design an auction? ──────────────────── Vickrey / VCG (A141, A146)
│  ├─ Repeated interaction? ───────────────── Tit-for-Tat / Repeated Games (A142)
│  ├─ Population dynamics / evolution? ─────── ESS (A143)
│  └─ Negotiate a deal? ──────────────────── Nash Bargaining (A145)
│
├─ DECIDE / CHOOSE (decision analysis)
│  ├─ Simple choice under risk? ───────────── EMV (A147) / Expected Utility (A148)
│  ├─ Sequential decisions? ───────────────── Decision Tree (A149)
│  ├─ Which parameters matter most? ────────── Sensitivity / Tornado (A150)
│  ├─ Rank options by criteria? ───────────── AHP (A151) / TOPSIS (A152)
│  ├─ Eliminate dominated options? ─────────── ELECTRE (A153)
│  ├─ Update beliefs with evidence? ────────── Bayesian Decision (A154)
│  ├─ No probabilities available? ──────────── Minimax Regret (A155)
│  └─ Multiple attributes with utilities? ─── MAUT (A156)
│
├─ OPTIMIZE MULTIPLE objectives (multi-objective)
│  ├─ Find all trade-offs? ────────────────── Pareto Frontier (A157)
│  ├─ Known importance weights? ───────────── Weighted Sum (A158)
│  ├─ Non-convex trade-offs? ──────────────── Epsilon-Constraint (A159)
│  ├─ Complex / black-box objectives? ──────── NSGA-II (A160) / MOEA/D (A161)
│  ├─ Meet target levels? ─────────────────── Goal Programming (A162)
│  ├─ Strict priority ordering? ───────────── Lexicographic (A163)
│  └─ Decision-maker has aspirations? ──────── Reference Point (A164)
│
├─ FORECAST / PREDICT OVER TIME
│  ├─ Single time series, no seasonality? ── ARIMA (S46)
│  ├─ Single series with seasonality? ──────── SARIMA (S47) / Holt-Winters (S48)
│  ├─ Multiple seasonalities / holidays? ──── Prophet (S55)
│  ├─ Multiple related series? ─────────────── VAR (S53)
│  ├─ Understand components? ───────────────── Decomposition (S49)
│  ├─ Volatility / financial risk? ─────────── GARCH (S54)
│  ├─ Is it predictable at all? ────────────── Stationarity tests (S51) / Random walk (S64)
│  └─ What drives what? ────────────────────── Granger causality (S52)
│
├─ DETECT CHANGE / ANOMALY in time series
│  ├─ When did the trend shift? ────────────── Change Point Detection (S56)
│  ├─ What observations are unusual? ────────── Anomaly Detection (S57)
│  ├─ Did an intervention have effect? ──────── Intervention Analysis (S60)
│  ├─ What's the dominant cycle? ────────────── Spectral Analysis (S59)
│  └─ Smooth out noise? ────────────────────── Moving Average (S58)
│
├─ MODEL RANDOM EVENTS over time
│  ├─ Events at constant rate? ─────────────── Poisson Process (S63)
│  ├─ System switching between states? ──────── CTMC (S61)
│  ├─ Queue with arrivals/departures? ──────── Birth-Death Process (S62)
│  ├─ Recurring events (non-exponential)? ──── Renewal Process (S65)
│  └─ Is it a random walk? ─────────────────── Random Walk Analysis (S64)
│
├─ SURVIVAL / TIME-TO-EVENT analysis
│  ├─ Estimate time until event? ────────────── Kaplan-Meier (S39)
│  ├─ Compare survival between groups? ──────── Log-Rank Test (S66)
│  ├─ Effect of factors on hazard? ──────────── Cox PH (S40)
│  ├─ Effect of factors on time? ────────────── AFT Model (S67)
│  └─ Multiple possible events? ─────────────── Competing Risks (S68)
│
├─ CLASSIFY / PREDICT CATEGORY (machine learning)
│  ├─ Need interpretable rules? ──────────────── Decision Tree (S70)
│  ├─ Best accuracy, tabular data? ────────────── Gradient Boosting (S74) / Random Forest (S71)
│  ├─ Small data, simple baseline? ────────────── k-NN (S69) / Naive Bayes (S73)
│  ├─ High-dimensional, clear margin? ─────────── SVM (S72)
│  ├─ Complex nonlinear patterns? ─────────────── MLP Neural Net (S75)
│  └─ Compare multiple models? ────────────────── Model Comparison (S89)
│
├─ PREDICT CONTINUOUS VALUE (ML regression)
│  ├─ Nonlinear relationships? ────────────────── RF Regressor (S76) / GB Regressor (S77)
│  ├─ Need coefficients / inference? ──────────── Linear Regression (S23-S27)
│  └─ Need feature importance? ────────────────── Random Forest (S76) + Feature Selection (S87)
│
├─ FIND GROUPS / CLUSTER / SEGMENT
│  ├─ Know number of clusters?
│  │  ├─ Spherical clusters? ──────────────────── K-Means (S78)
│  │  ├─ Elliptical / overlapping? ────────────── GMM (S81)
│  │  └─ Non-convex shapes? ──────────────────── Spectral Clustering (S82)
│  └─ Unknown number?
│     ├─ Noise / outliers present? ────────────── DBSCAN (S79)
│     └─ Want hierarchy / dendrogram? ─────────── Agglomerative (S80)
│
├─ REDUCE DIMENSIONS / VISUALIZE
│  ├─ Linear reduction / feature compression? ── PCA (S83)
│  ├─ 2D visualization (small data)? ──────────── t-SNE (S84)
│  ├─ 2D visualization (large data)? ──────────── UMAP (S85)
│  └─ Latent constructs / survey data? ────────── Factor Analysis (S86)
│
└─ SELECT FEATURES / TUNE MODEL
   ├─ Too many features? ──────────────────────── Feature Selection (S87)
   ├─ Optimize hyperparameters? ───────────────── Hyperparameter Tuning (S88)
   ├─ Compare models fairly? ──────────────────── Model Comparison (S89)
   └─ Build production workflow? ──────────────── Pipeline Construction (S90)
```

---

## Quick Pattern Table

One-line lookup from problem description to solution approach.

| If the user says... | Think... | Structure | Algorithm | Solver |
|---|---|---|---|---|
| "assign X to Y" | Assignment | Bipartite graph | Hungarian (A16) | scipy |
| "schedule with no conflicts" | Coloring | Conflict graph | Greedy/ILP (A21/A32) | NetworkX/PuLP |
| "find the shortest route" | Shortest path | Weighted graph | Dijkstra (A8) | NetworkX |
| "visit all cities" | TSP | Complete graph | Held-Karp/ILP (A28/A32) | OR-Tools |
| "maximize flow/throughput" | Max flow | Capacity network | Edmonds-Karp (A19) | NetworkX |
| "best subset under budget" | Knapsack | Items + capacity | DP (A33) | Custom |
| "cover all requirements" | Set cover | Set family | Greedy (A47) or ILP | PuLP |
| "order tasks with dependencies" | Topological sort | DAG | Kahn's (A3) | NetworkX |
| "project timeline / critical path" | Longest DAG path | DAG | DP (A12) | NetworkX |
| "partition into groups" | Partitioning | Set/graph | ILP (A32) | PuLP |
| "how many ways to arrange" | Counting | Combinatorial | Formula / DP | SymPy |
| "prove for all n" | Induction | Algebraic | Symbolic (A74) | SymPy |
| "is it possible / satisfiable" | SAT/CSP | Boolean/Integer | CDCL (A48) | Z3 |
| "find vulnerabilities in network" | Connectivity | Graph | Bridges/AP (A6) | NetworkX |
| "what's the probability" | Probability | Sample space | Counting / MC | SymPy/numpy |
| "stable matching / pairing" | Stable marriage | Bipartite + prefs | Gale-Shapley (A17) | Custom |
| "minimize cost of connections" | MST | Weighted graph | Kruskal (A13) | NetworkX |
| "find largest clique / group" | Clique | Graph | Bron-Kerbosch (A25) | NetworkX |
| "Euler path / traverse all edges" | Euler circuit | Multigraph | Hierholzer (A26) | NetworkX |
| "round-robin / balanced design" | Latin square | Array | CSP (A52) | Z3 |
| "cyclic / repeating pattern" | Modular arithmetic | Z_n | CRT (A55) | SymPy |
| "integer solutions only" | Diophantine | Number theory | Extended GCD (A54) | SymPy |
| "long-run / steady state" | Markov chain | Transition matrix | Eigenvector (A80) | numpy |
| "optimize with constraints" | ILP | Variables + constraints | Branch & bound (A32) | PuLP |
| "what if / sensitivity" | Sensitivity | (depends on base) | Re-solve with perturbation | (same) |
| "minimize smooth function" | Unconstrained opt | Continuous | BFGS (A89) | scipy |
| "portfolio / risk-return" | QP | Quadratic program | cvxpy QP (A88) | cvxpy |
| "fit a curve / regression" | Least squares | Overdetermined system | lstsq (A91) | numpy/scipy |
| "convex constraints" | Convex program | Conic program | Interior point (A87) | cvxpy |
| "engineering design" | Nonlinear constrained | NLP | SLSQP (A93) | scipy |
| "solve equations / system" | Linear system | Linear system | Gaussian elim (A95) | numpy |
| "eigenvalues / modes / PCA" | Eigenvalue problem | Eigenstructure | eig / SVD (A97-A98) | numpy |
| "rank / independence" | Matrix rank | Matrix | Rank (A103) / SVD | numpy |
| "derivative / rate of change" | Differentiation | Function | Symbolic diff (A107) | SymPy |
| "integral / area under curve" | Integration | Integral | Symbolic (A108) / quad (A109) | SymPy/scipy |
| "ODE / growth / decay" | Differential equation | Diff. equation | dsolve (A115) / solve_ivp (A116) | SymPy/scipy |
| "area of shape / land" | Geometry | Polygon | Shoelace (A117) | shapely |
| "volume / capacity" | Solid geometry | Polyhedron | Formulas (A118) | SymPy |
| "distance / how far" | Distance | Point set | Euclidean (A119) | scipy.spatial |
| "convex hull / boundary" | Convex hull | Point set | Graham scan (A120) | scipy.spatial |
| "triangle / angle / side" | Triangle solving | Triangle | Law of cosines (A125) | math |
| "NPV / is investment worth it" | Investment analysis | Cash flow stream | NPV (A127) | numpy-financial |
| "IRR / return on investment" | Investment analysis | Cash flow stream | IRR (A128) | numpy-financial |
| "mortgage / loan payment" | Loan analysis | Cash flow stream | PMT (A129) | numpy-financial |
| "amortization / pay off" | Amortization | Cash flow stream | Schedule (A130) | numpy-financial |
| "compound interest / savings" | Time value of money | Cash flow stream | FV (A131) | numpy-financial |
| "refinance / compare loans" | Refinancing | Cash flow stream | Comparison (A134) | numpy-financial |
| "break even / payback period" | Break-even | Cash flow stream | Break-even (A133) | numpy/SymPy |
| "compete / pricing war" | Nash equilibrium | Strategic-form game | Support enum (A135) | nashpy |
| "zero-sum / minimax" | Minimax | Strategic-form game | Minimax (A137) | nashpy |
| "fair share / cost allocation" | Shapley value | Cooperative game | Shapley (A138) | Custom |
| "divide fairly / split" | Fair division | Cooperative game | Adjusted winner (A139) | Custom |
| "auction / bidding" | Mechanism design | Strategic-form game | Vickrey/VCG (A141/A146) | Custom |
| "negotiate / bargain" | Bargaining | Extensive-form game | Nash bargaining (A145) | scipy |
| "voting power" | Shapley-Shubik | Cooperative game | Shapley (A138) | Custom |
| "expected value / best bet" | Decision under risk | Decision tree | EMV (A147) | numpy |
| "risk averse / utility" | Expected utility | Preference model | Utility (A148) | numpy |
| "decision tree / stages" | Sequential decision | Decision tree | Backward induction (A149) | Custom |
| "which parameters matter" | Sensitivity analysis | Decision tree | Tornado (A150) | matplotlib |
| "rank options / criteria" | Multi-criteria | Multi-criteria problem | AHP (A151) / TOPSIS (A152) | numpy |
| "best vendor / supplier" | MCDA ranking | Multi-criteria problem | TOPSIS (A152) | numpy |
| "no probabilities / uncertainty" | Minimax regret | Decision tree | Minimax regret (A155) | numpy |
| "trade-off / Pareto" | Multi-objective | Pareto set | Pareto front (A157) | pymoo |
| "balance cost vs quality" | Multi-objective | Objective space | NSGA-II (A160) | pymoo |
| "meet multiple targets" | Goal programming | Goal model | Goal LP (A162) | PuLP |
| "priority ordering of goals" | Lexicographic | Goal model | Lex. opt (A163) | PuLP |
| "forecast / predict next month" | Time series forecast | Time series | ARIMA (S46) / SARIMA (S47) | statsmodels |
| "seasonal pattern / monthly cycle" | Seasonal decomposition | Seasonal pattern | STL (S49) / SARIMA (S47) | statsmodels |
| "trend over time / growing" | Trend analysis | Trend component | Decomposition (S49) | statsmodels |
| "predict with holidays" | Business forecast | Time series | Prophet (S55) | prophet |
| "multiple series together" | Multivariate forecast | Time series | VAR (S53) | statsmodels |
| "volatility / risk of returns" | Volatility modeling | Time series | GARCH (S54) | arch |
| "when did trend change" | Change point | Time series | PELT (S56) | ruptures |
| "detect outliers / anomalies" | Anomaly detection | Time series | Z-score / IQR (S57) | scipy |
| "did intervention help" | Intervention analysis | Time series | ARIMA + exog (S60) | statsmodels |
| "what's the cycle length" | Spectral analysis | Seasonal pattern | Periodogram (S59) | scipy |
| "does X predict Y over time" | Granger causality | Time series | Granger test (S52) | statsmodels |
| "is it random / unpredictable" | Random walk | Random walk | ADF + var ratio (S64) | statsmodels |
| "arrival rate / events per hour" | Poisson process | Point process | Poisson fit (S63) | scipy |
| "queue / waiting time" | Queuing model | CTMC | Birth-death (S62) | scipy |
| "system up/down states" | Reliability | CTMC | Matrix exp (S61) | scipy |
| "time until failure / churn" | Survival analysis | Survival | Kaplan-Meier (S39) | lifelines |
| "compare survival curves" | Group comparison | Survival | Log-rank (S66) | lifelines |
| "risk factors for event" | Hazard modeling | Survival | Cox PH (S40) | lifelines |
| "multiple ways to leave" | Competing risks | Survival | Aalen-Johansen (S68) | lifelines |
| "classify / detect / diagnose" | Classification | Classification model | Random Forest (S71) / GB (S74) | scikit-learn |
| "spam or not / fraud detection" | Binary classification | Classification model | Logistic (S25) / RF (S71) | scikit-learn |
| "which category / type" | Multi-class classification | Classification model | RF (S71) / SVM (S72) | scikit-learn |
| "predict a number / price" | ML regression | Regression model | RF Regressor (S76) / GB (S77) | scikit-learn |
| "best model / which algorithm" | Model comparison | ML Pipeline | Model Comparison (S89) | scikit-learn |
| "segment customers / group" | Clustering | Cluster structure | K-Means (S78) / DBSCAN (S79) | scikit-learn |
| "find natural groups" | Clustering | Cluster structure | GMM (S81) / Hierarchical (S80) | scikit-learn |
| "how many clusters / segments" | Cluster selection | Cluster structure | Elbow + Silhouette (S78) | scikit-learn |
| "reduce features / compress" | Dimensionality reduction | Low-dim embedding | PCA (S83) | scikit-learn |
| "visualize high-dim data" | Embedding visualization | Low-dim embedding | UMAP (S85) / t-SNE (S84) | umap-learn |
| "latent factors / constructs" | Factor analysis | Low-dim embedding | Factor Analysis (S86) | scikit-learn |
| "which features matter" | Feature selection | ML Pipeline | Feature Selection (S87) | scikit-learn |
| "tune / optimize parameters" | Hyperparameter tuning | ML Pipeline | Grid/Random Search (S88) | scikit-learn |
| "too many variables" | Feature reduction | ML Pipeline | PCA (S83) / Selection (S87) | scikit-learn |

---

## Complexity Quick Check

Before committing to an approach, verify the computational feasibility.

| Problem Class | Complexity | Exact Feasible Up To | Approximation Available? |
|---|---|---|---|
| Shortest path | P | Any size | N/A (already polynomial) |
| MST | P | Any size | N/A |
| Bipartite matching | P | Any size | N/A |
| Max flow | P | Any size | N/A |
| Topological sort | P | Any size | N/A |
| Graph coloring | NP-hard | ~50 vertices (exact) | Greedy: Δ+1 colors |
| TSP | NP-hard | ~20 (DP), ~1000 (ILP) | Christofides: 1.5x |
| Knapsack | NP-hard | ~10^6 (pseudo-poly DP) | FPTAS: (1-ε)x |
| Set cover | NP-hard | ~30 (exact), ~1000 (ILP) | Greedy: ln(n)+1 |
| SAT | NP-complete | ~10^6 vars (modern solvers) | N/A (decision) |
| ILP | NP-hard | ~10K vars (CBC) | LP relaxation bound |
| Independent set | NP-hard | ~25 (bitmask DP) | None good (general) |
| Hamiltonian path | NP-complete | ~20 (DP) | Heuristic only |
| Graph isomorphism | GI-complete | ~1000 (practical) | N/A (decision) |
| Counting problems | #P (some) | ~20 (enumeration) | Sampling / MCMC |
| Convex optimization | P | Any size (via cvxpy) | N/A (already polynomial) |
| Quadratic programming | P (if convex) | Any size | N/A |
| Least squares | P | Any size (O(mn²)) | N/A |
| Nonlinear constrained | NP-hard (general) | ~1000 vars (local opt) | Multi-start heuristic |
| Linear system (Ax=b) | P | Any size (O(n³)) | N/A |
| Eigenvalue / SVD | P | Any size (O(n³)) | N/A |
| Symbolic differentiation | P | Any expression | N/A |
| Symbolic integration | Undecidable (general) | Most standard forms | Numerical quadrature |
| ODE (numerical) | P | Any size (adaptive) | N/A |
| Polygon area / geometry | P | Any size | N/A |
| Convex hull | P (O(n log n)) | Any size | N/A |
| Financial (NPV/IRR/PMT) | P | Any size | N/A |
| Nash equilibrium (2-player) | PPAD-complete | ~20 strategies (support enum) | Lemke-Howson (one equilibrium) |
| Nash equilibrium (N-player) | PPAD-complete | ~5 players, ~10 strategies | Approximate Nash |
| Shapley value | O(2^n) | ~20 players (exact) | Sampling approximation |
| Fair division (N players) | P (round-robin) | Any size | Proportional guarantee |
| Decision tree evaluation | P | Any size (O(nodes)) | N/A |
| AHP / TOPSIS | P | Any size (O(mn)) | N/A |
| NSGA-II | Heuristic | ~100 vars, 2-3 obj | Always finds feasible front |
| MOEA/D | Heuristic | ~100 vars, many obj | Well-distributed front |
| Goal programming | P (LP) | Any size (via LP solver) | N/A |
| ARIMA fitting | P (O(n·p²)) | Any size | N/A |
| SARIMA fitting | P (O(n·(p+P)²)) | Any size | N/A |
| Exponential smoothing | P (O(n)) | Any size | N/A |
| Prophet | P (O(n·iter)) | ~1M observations | N/A |
| Change point (PELT) | P (O(n²)) | ~100K observations | BinSeg (O(n log n)) |
| Spectral analysis (FFT) | P (O(n log n)) | Any size | N/A |
| GARCH fitting | P (O(n·iter)) | Any size | N/A |
| CTMC steady-state | P (O(k³)) | ~1000 states | Iterative methods |
| Poisson process MLE | P (O(n)) | Any size | N/A |
| Kaplan-Meier | P (O(n log n)) | Any size | N/A |
| Cox PH regression | P (O(n·p·iter)) | ~100K subjects | Penalized/regularized |
| Log-rank test | P (O(n log n)) | Any size | N/A |
| k-NN classification | P (O(nd)) | ~100K (brute), any (KD-tree) | N/A |
| Decision tree | P (O(np log n)) | Any size | N/A |
| Random forest | P (O(np log n · T)) | Any size | N/A |
| SVM (RBF kernel) | O(n²-n³) | ~10K samples | LinearSVC for large sparse |
| Gradient boosting | P (O(np log n · T)) | Any size (use XGBoost) | N/A |
| K-Means | P (O(nkp · iter)) | Any size | Mini-batch K-Means |
| DBSCAN | O(n log n) with index | ~100K | HDBSCAN (auto-eps) |
| PCA | P (O(min(np², p³))) | Any size | Randomized PCA |
| t-SNE | O(n² log n) | ~10K | Barnes-Hut approximation |
| UMAP | O(n^1.14) empirical | ~1M | N/A |
| Grid search (k params) | O(grid^k · CV) | ~100 combinations | RandomizedSearchCV |

---

## Disambiguation Tips

When two patterns seem equally likely, use these tiebreakers:

**Assignment vs. Set Cover**: If each "task" needs exactly one "worker," it's assignment (matching). If each "requirement" can be satisfied by any of several "sets," it's set cover.

**Coloring vs. Partitioning**: If the constraint is "no two neighbors share a group," it's coloring. If the constraint is "groups must be balanced" or "minimize inter-group edges," it's partitioning.

**Shortest Path vs. TSP**: If you need to go from A to B, it's shortest path. If you need to visit ALL locations and return, it's TSP.

**Knapsack vs. ILP**: Knapsack is a special case of ILP with one constraint (capacity). If there are multiple constraints, model as general ILP.

**SAT vs. ILP**: If all variables are Boolean and all constraints are clauses, use SAT (faster). If variables are integers or constraints are linear inequalities, use ILP.

**Counting vs. Optimization**: "How many?" is counting. "Which is best?" is optimization. "What fraction?" is probability (counting / total).

**Linear System vs. Optimization**: If you need to find values satisfying equations exactly (Ax = b), it's a linear system. If you need to minimize/maximize something subject to constraints, it's optimization.

**Symbolic vs. Numerical**: If an exact closed-form answer matters (proofs, formulas, education), use SymPy (symbolic). If you need a fast numerical answer to a specific instance, use numpy/scipy (numerical).

**Calculus vs. Optimization**: If the user wants to find a max/min of a formula with a known expression, use calculus (set derivative = 0). If the problem has constraints or many variables, use optimization (ILP, BFGS, etc.).

**Geometry vs. Calculus**: If the shape is a standard polygon/solid, use geometry formulas. If the region is bounded by curves (e.g., area between two functions), use integration.

**NPV vs. Break-Even**: NPV answers "is this investment worth it at a given rate?" Break-even answers "when does this investment pay for itself?" Use both together for a complete picture.

**Game Theory vs. Decision Analysis**: If there's an opponent who reacts strategically (their payoff depends on your choice AND vice versa), it's game theory. If there's uncertainty but no strategic opponent (nature, market), it's decision analysis.

**Nash Equilibrium vs. Optimization**: If you're finding the best strategy GIVEN that others also optimize, it's Nash. If you're optimizing from a single decision-maker's perspective, it's optimization.

**MCDA vs. Multi-Objective Optimization**: If you have a fixed set of alternatives to rank, it's MCDA (AHP/TOPSIS). If you can generate new solutions by optimizing, it's multi-objective optimization (NSGA-II/goal programming).

**Fair Division vs. Assignment**: If items are indivisible and players have preferences, it's fair division. If the goal is to minimize total cost or maximize total utility (no fairness concern), it's assignment.

**Sensitivity vs. Multi-Objective**: If you're varying one parameter at a time to see impact, it's sensitivity analysis. If you're optimizing multiple objectives simultaneously, it's multi-objective optimization.

**ARIMA vs. Exponential Smoothing**: Both forecast univariate time series. ARIMA models autocorrelation explicitly (good for complex patterns); exponential smoothing is simpler and often competitive for short horizons. When in doubt, try both and compare AIC.

**ARIMA vs. Prophet**: ARIMA is better for clean, regular time series. Prophet handles irregular dates, missing data, holidays, and multiple seasonalities better. Prophet is easier for non-statisticians.

**Change Point vs. Anomaly**: Change points are persistent shifts (the process changes). Anomalies are temporary outliers (the process stays the same). A price regime change is a change point; a flash crash is an anomaly.

**Poisson Process vs. Renewal Process**: If inter-arrival times are exponential (memoryless), it's Poisson. If inter-arrival times follow another distribution, it's a renewal process. Test exponentiality of inter-arrivals.

**Kaplan-Meier vs. Cox PH**: Kaplan-Meier estimates the survival curve nonparametrically (no covariates). Cox PH models how covariates affect hazard. Use KM for description, Cox PH for explanation.

**Cox PH vs. AFT**: Cox PH models the hazard ratio (multiplicative effect on risk). AFT models the acceleration factor (multiplicative effect on time). AFT is more intuitive ("this factor doubles the time to event") but Cox PH is more flexible.

**Classification vs. Regression**: If the target is categorical (yes/no, type A/B/C), it's classification. If the target is continuous (price, temperature, score), it's regression. "Binary outcome" is classification even if coded as 0/1.

**Classification (ML) vs. Logistic Regression (Stats)**: Both predict categories. Use logistic regression (S25) when you need p-values, odds ratios, and interpretability. Use ML classifiers (S69-S75) when you need maximum prediction accuracy.

**K-Means vs. GMM**: K-Means produces hard assignments (each point belongs to exactly one cluster) and assumes spherical clusters. GMM produces soft assignments (probability of belonging to each cluster) and handles elliptical clusters. Use GMM when clusters overlap.

**K-Means vs. DBSCAN**: K-Means requires specifying k and finds spherical clusters. DBSCAN finds clusters of arbitrary shape and identifies noise points, but requires tuning eps. Use DBSCAN when you don't know k or when data has outliers.

**PCA vs. t-SNE/UMAP**: PCA is a linear method — fast, deterministic, and the components are interpretable. t-SNE/UMAP are nonlinear — better for visualization but distances between distant points are NOT meaningful. Use PCA for preprocessing/feature reduction, t-SNE/UMAP for visualization only.

**Feature Selection vs. PCA**: Feature selection keeps original features (interpretable). PCA creates new features as linear combinations (less interpretable). Use feature selection when you need to explain which original variables matter.

---

## Cross-Reference Index

After identifying the problem type here, consult the corresponding reference files:

| Problem Category | Structures (structures.md) | Algorithms (algorithms.md) | Protocols (solving-protocols.md) |
|---|---|---|---|
| ASSIGN | §1.4 Bipartite Graph, §7.1 ILP | §4 Matching (A15-A17), §10 ILP (A32) | Protocol: Optimization (ILP/LP) |
| SCHEDULE | §1.1 Simple Graph, §7.3 Scheduling | §6 Coloring (A21-A22), §1 Topo Sort (A3) | Protocol: Graph, Protocol: Optimization |
| ROUTE | §1.3 Weighted Graph | §2 Shortest Path (A8-A12), §9 TSP (A28-A30) | Protocol: Graph |
| SELECT/PACK | §7.1 ILP | §10 ILP (A32), §11 DP (A33-A34) | Protocol: Optimization, Protocol: DP |
| GROUP | §3.4 Set Partition | §10 ILP (A32) | Protocol: Optimization |
| COUNT | §2 Combinatorics | §15 Counting (A63-A69) | Protocol: Counting |
| PROVE | §4 Logic | §17 Proof (A74-A77) | Protocol: Proof |
| ANALYZE network | §1 Graph Theory | §1 Traversal (A1-A7), §5 Flow (A19) | Protocol: Graph |
| SATISFY | §4.4 CSP | §13 SAT/SMT/CSP (A48-A52) | Protocol: SAT/SMT |
| OPTIMIZE continuous | §9 Continuous Optimization | §21 Continuous Opt (A87-A94) | Protocol: Continuous Optimization |
| ASSESS probability | §8 Discrete Probability | §18 Probability (A78-A81) | Protocol: Counting |
| SOLVE equations | §11 Linear Algebra | §22 Linear Algebra (A95-A106) | (Direct solve) |
| DIFFERENTIATE/INTEGRATE | §12 Calculus | §23 Calculus (A107-A116) | (Symbolic/Numerical) |
| MEASURE geometry | §13 Geometry | §24 Geometry (A117-A126) | (Direct compute) |
| EVALUATE finances | §14 Financial Math | §25 Financial Math (A127-A134) | (Direct compute) |
| COMPETE/NEGOTIATE | §15 Game Theory | §26 Game Theory (A135-A146) | (Custom / nashpy) |
| DECIDE/CHOOSE | §16 Decision Analysis | §27 Decision Analysis (A147-A156) | (Custom / numpy) |
| OPTIMIZE MULTIPLE | §17 Multi-Objective Opt | §28 Multi-Objective (A157-A164) | (pymoo / PuLP) |
| FORECAST/PREDICT | §18 Time Series | algorithms-statistics.md S46-S60 | (statsmodels / prophet) |
| DETECT CHANGE/ANOMALY | §18 Time Series | algorithms-statistics.md S56-S60 | (ruptures / scipy) |
| MODEL RANDOM EVENTS | §19 Stochastic Processes | algorithms-statistics.md S61-S65 | (scipy / custom) |
| SURVIVAL/TIME-TO-EVENT | §10 Statistical Inference | algorithms-statistics.md S39-S40, S66-S68 | (lifelines) |
| CLASSIFY/PREDICT CATEGORY | §20.1 Classification Model | algorithms-statistics.md S69-S75 | (scikit-learn / xgboost) |
| PREDICT VALUE (ML) | §20.2 Regression Model (ML) | algorithms-statistics.md S76-S77 | (scikit-learn / xgboost) |
| CLUSTER/SEGMENT | §20.3 Cluster Structure | algorithms-statistics.md S78-S82 | (scikit-learn) |
| REDUCE DIMENSIONS | §20.4 Low-Dim Embedding | algorithms-statistics.md S83-S86 | (scikit-learn / umap-learn) |
| SELECT FEATURES/TUNE | §20.5 ML Pipeline | algorithms-statistics.md S87-S90 | (scikit-learn) |

Also see: **common-mistakes.md** for pitfalls specific to each problem category.
