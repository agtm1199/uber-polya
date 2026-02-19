# Problem-Specific Solving Protocols

**Scope**: All domains (currently: Discrete Mathematics, Continuous Optimization, Statistical Inference)
**When to read**: After classifying the problem in Phase 0 of uber-solve. Read the protocol that matches your problem type.

---

## Protocol: Graph Problems

**Applies to**: Shortest path, MST, matching, coloring, flow, connectivity, Euler/Hamilton.
**See also**: `algorithms.md` sections 1-9, `solvers.md` section 1 (NetworkX)

1. Build the graph using NetworkX
2. Check basic properties: |V|, |E|, connected?, bipartite?, planar?, DAG?
3. These properties determine which algorithms are applicable
4. Use NetworkX built-in algorithms where available (battle-tested, optimized C backends)
5. Verify: check solution against graph properties (e.g., coloring has no adjacent same colors)

**Common pitfall**: Not checking prerequisites before applying an algorithm (S2 in common-mistakes.md). Always verify: non-negative weights for Dijkstra, bipartiteness for Hungarian, acyclicity for topological sort.

---

## Protocol: Optimization Problems (ILP/LP)

**Applies to**: Assignment, knapsack, set cover, facility location, scheduling, any linear model.
**See also**: `algorithms.md` section 10, `solvers.md` sections 2, 5, 6 (PuLP, SciPy, OR-Tools)

1. Formulate in PuLP or OR-Tools
2. Variables: use `LpVariable` with explicit bounds and type (continuous/integer/binary)
3. Constraints: add one per formal constraint, with descriptive names
4. Solve: use CBC (default), or GLPK, or Gurobi if available
5. Check `status == LpStatusOptimal`
6. Extract values, verify feasibility independently
7. Report: primal value, dual bound, gap, solve time

**Common pitfall**: Forgetting integrality (M1 in common-mistakes.md). If binary variables report x=0.9999, round them.

---

## Protocol: SAT/SMT Problems

**Applies to**: Boolean satisfiability, integer constraints, configuration, Sudoku-like puzzles.
**See also**: `algorithms.md` section 13, `solvers.md` section 3 (Z3)

1. Formulate in Z3
2. Variables: `Bool`, `Int`, `Real`, `BitVec` as appropriate
3. Constraints: add one per formal constraint
4. Solve: `solver.check()`
5. If SAT: extract model, verify independently
6. If UNSAT: extract unsat core for explanation
7. For optimization: use Z3's `Optimize()` with `minimize()`/`maximize()`

---

## Protocol: Counting Problems

**Applies to**: Permutations, combinations, partitions, Burnside, inclusion-exclusion.
**See also**: `algorithms.md` section 15, `solvers.md` sections 4, 7 (SymPy, itertools)

1. Identify the counting structure: permutation, combination, partition, Burnside
2. For small n: enumerate and count (verify formula)
3. For large n: use closed-form formula, generating function, or DP
4. Always cross-check with alternative counting method when feasible
5. Use SymPy for symbolic computation and simplification

---

## Protocol: Proof Problems

**Applies to**: Mathematical induction, contradiction, construction, existence proofs.
**See also**: `algorithms.md` section 17, `solvers.md` sections 3, 4 (Z3, SymPy)

1. Classify: direct proof, induction, contradiction, contrapositive, construction
2. For induction: verify base case numerically, prove inductive step symbolically
3. For contradiction: state assumption, derive contradiction, verify logic
4. For construction: build the object, verify it satisfies all conditions
5. Use Z3 for automated verification of logical steps where possible
6. Use SymPy for algebraic manipulation and simplification

---

## Protocol: Number Theory Problems

**Applies to**: GCD/LCM, modular arithmetic, CRT, Diophantine equations, primality.
**See also**: `algorithms.md` section 14, `solvers.md` section 4 (SymPy)

1. Use SymPy's number theory functions (gcd, lcm, factorint, isprime, ntheory)
2. For modular arithmetic: use Python's built-in pow(a, b, mod) for modular exponentiation
3. For CRT: use SymPy's `crt()`
4. For Diophantine: use SymPy's `diophantine()`
5. Verify: substitute solution back into original equation

---

## Protocol: Dynamic Programming

**Applies to**: Knapsack, LCS, edit distance, coin change, matrix chain, subset sum, partition.
**See also**: `algorithms.md` section 11

1. Define state space clearly: what does dp[i][j] represent?
2. Define recurrence relation with base cases
3. Determine order of computation (bottom-up preferred for efficiency)
4. Implement with proper bounds checking
5. Trace back solution path (not just optimal value)
6. Verify: check that the reconstructed solution is feasible and matches dp value

---

## Protocol: Continuous Optimization

**Applies to**: Convex programs, unconstrained minimization, nonlinear least squares, portfolio optimization.
**See also**: `algorithms.md` section 21 (Continuous Optimization), `solvers.md` sections 5, 9 (SciPy, cvxpy)

1. Classify: convex vs. non-convex, constrained vs. unconstrained
2. If convex: use cvxpy (disciplined convex programming -- guarantees global optimum)
3. If unconstrained: use `scipy.optimize.minimize()` with appropriate method (BFGS, L-BFGS-B, Nelder-Mead)
4. If constrained non-convex: use `scipy.optimize.minimize()` with SLSQP or trust-constr
5. Always check: gradient at solution ≈ 0 (or KKT conditions for constrained)
6. For non-convex: run from multiple initial points to guard against local minima
7. Verify: substitute solution back into objective and constraints

**Common pitfall**: Treating a non-convex problem as convex. If the objective or any constraint is non-convex, there's no guarantee of global optimality -- report this explicitly.

---

## Protocol: Statistical Inference

**Applies to**: Hypothesis testing, confidence intervals, regression, Bayesian estimation, survival analysis, A/B testing, power analysis.
**See also**: `algorithms-statistics.md` (45 algorithms), `solvers-statistics.md` (scipy.stats, statsmodels, PyMC, pingouin, lifelines)

1. **Identify the question type**: estimation, comparison, association, prediction, or Bayesian updating
2. **Check assumptions**: normality (Shapiro-Wilk), independence, sample size (n ≥ 30 for CLT), equal variance (Levene's test)
3. **If assumptions violated**: use nonparametric alternative or bootstrap
   - Non-normal groups → Mann-Whitney U (2 groups) or Kruskal-Wallis (3+)
   - Small sample → exact tests (Fisher's, permutation)
   - Heteroscedasticity → Welch's t-test, robust regression
4. **Select test/method** from `algorithms-statistics.md` based on question type and assumption status
5. **Implement** using appropriate library: scipy.stats for tests, statsmodels for regression, PyMC for Bayesian
6. **Report**: point estimate, confidence/credible interval, p-value (if frequentist), effect size, sample size
7. **Verify**: run alternative test (parametric ↔ nonparametric), check residual diagnostics for regression
8. **Never report p-value alone.** Always include effect size and confidence interval.

**Common pitfall**: Reporting "p < 0.05, therefore significant" without effect size. A tiny, meaningless effect can have p < 0.001 with large n. Always report: "The difference was X units (95% CI: [L, U]), Cohen's d = Y, p = Z."
