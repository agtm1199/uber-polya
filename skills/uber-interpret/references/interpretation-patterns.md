# Interpretation Patterns by Domain

**Scope**: Discrete Mathematics (6 domains), Continuous Optimization (3 patterns)

How to translate mathematical solutions back into real-world meaning. For each domain: what the solution objects represent, how to read them, what to check for robustness, and what limitations to flag.

---

## 1. Graph Theory Solutions

### 1.1 Shortest Path Results

**Math object**: Path P = (v₁, v₂, ..., vₖ) with total weight w(P).

**Translation**:
- Each edge on the path is a step, action, or transition the user should take
- The total weight is the cost, time, or distance of the best route
- Intermediate vertices are waypoints, intermediate states, or handoff points

**Key insights to extract**:
- The path itself (the sequence of actions)
- The total cost (what it costs to follow the optimal path)
- Comparison to naive alternatives (how much better than obvious routes?)
- Bottleneck edge (the single most expensive step)

**Sensitivity**:
- Remove each edge on the path: what's the next-best route? How much worse?
- Increase each edge weight by 10%: does the optimal path change?
- **Critical edge**: the edge whose removal causes the largest increase in path cost

**Limitations**:
- Shortest path assumes costs are fixed and known; real costs may be stochastic
- Path optimality doesn't account for congestion, capacity, or time-varying conditions
- Multiple near-optimal paths may exist; present alternatives within 5-10% of optimal

---

### 1.2 Matching Results

**Math object**: Set of edges M ⊆ E pairing elements of two groups.

**Translation**:
- Each edge in M is an assignment: person→task, resource→need, supply→demand
- Unmatched vertices represent unassigned entities (understaffing or excess)
- Weight of matching is total quality/profit/satisfaction

**Key insights to extract**:
- Who is assigned to what (the assignment table)
- Who is unassigned and why (exposed vertices)
- Quality of each assignment (edge weight)
- Gap between achieved and theoretical maximum

**Sensitivity**:
- Remove the highest-weight edge: how does the matching rearrange?
- Add a new vertex (new employee/project): does it displace existing assignments?
- **Bottleneck pair**: the assignment with lowest quality in the matching

**Limitations**:
- Matching assumes fixed preferences/qualifications; these may evolve
- Perfect matching may not exist; maximum matching may leave gaps
- Weighted matching optimizes total quality but may sacrifice individual fairness

---

### 1.3 Coloring Results

**Math object**: Function c: V → {1, 2, ..., k} with c(u) ≠ c(v) for all edges (u,v).

**Translation**:
- Each color is a group, time slot, channel, or resource
- Vertices of the same color can coexist (no conflicts)
- The number of colors k is the minimum number of groups/slots/resources needed

**Key insights to extract**:
- k = chromatic number → minimum resources required
- The color classes (which items share each group/slot)
- Comparison: k vs naive upper bounds (max degree + 1, n colors)
- If k is large: the problem has dense conflicts

**Sensitivity**:
- Add an edge (new conflict): does k increase?
- Remove a vertex (remove an entity): does k decrease?
- **Critical conflict**: the edge whose removal would reduce k

**Limitations**:
- Coloring assumes binary conflicts (conflict or not); real conflicts may have degrees
- Greedy coloring may use more than χ(G) colors; verify optimality
- Coloring doesn't minimize waste within color classes (balance)

---

### 1.4 Flow Results

**Math object**: Flow function f: E → R⁺ with f(e) ≤ cap(e), flow conservation at all non-terminal vertices.

**Translation**:
- Flow value = throughput, total amount transferred, total served
- Flow on each edge = utilization of that link/route/resource
- Min cut = bottleneck in the system; the cheapest set of disruptions that halts all flow
- Saturated edges (f = cap) = fully utilized resources

**Key insights to extract**:
- Maximum throughput (flow value)
- Bottleneck identification (min cut edges)
- Utilization rates: f(e)/cap(e) for each edge
- Underutilized capacity: edges with large slack

**Sensitivity**:
- Increase capacity of each min-cut edge by 1: which gives the most throughput gain?
- Decrease capacity of saturated edge: how much flow is lost?
- **Cheapest upgrade**: which single capacity increase yields the biggest improvement?

**Limitations**:
- Flow assumes steady-state; real systems have transients and variability
- Integer flow may be required (e.g., whole trucks, not fractional)
- Multi-commodity flow (multiple product types) is much harder

---

### 1.5 Connectivity Results

**Math object**: Connected components, articulation points, bridges, k-connectivity.

**Translation**:
- Connected component = group of mutually reachable entities
- Articulation point = single point of failure (person, server, intersection)
- Bridge = single critical link whose failure disconnects the system
- k-connectivity = how many simultaneous failures the system can tolerate

**Key insights to extract**:
- Number and size of components (fragmentation)
- Critical nodes and edges (vulnerability)
- Connectivity measure k (resilience)

**Sensitivity**:
- Remove each articulation point: how many components result?
- Add edges between components: cheapest way to improve connectivity?

---

## 2. Optimization Solutions

### 2.1 Linear/Integer Programming Results

**Math object**: Variable values x*, objective value z* = c^T x*, dual values λ*.

**Translation**:
- **Variable values** x*: the decisions to make (how much, which ones, assignments)
- **Objective z***: the best achievable outcome (minimum cost, maximum profit)
- **Dual values λ***: the marginal value of relaxing each constraint by one unit
  - λᵢ = "If constraint i's right-hand side increases by 1, the objective improves by λᵢ"
  - Also called **shadow prices** -- the price you'd pay to relax a constraint
- **Reduced costs**: for non-basic variables, how much the objective coefficient must improve before this variable enters the solution

**Key insights to extract**:
- The optimal decisions (x* values, especially binary ones)
- The optimal objective and its distance from theoretical bounds
- **Binding constraints** (where slack = 0): these are the bottlenecks
- **Shadow prices**: which constraints are most valuable to relax?
- **Reduced costs**: which unused options are closest to being worthwhile?

**Sensitivity**:
- **RHS sensitivity**: For each binding constraint, the range of RHS values over which the current basis remains optimal
- **Objective coefficient sensitivity**: How much can each coefficient change before the solution changes?
- **Parametric analysis**: Vary one parameter continuously and plot the objective

**Standard report**:
```
Binding constraints (bottlenecks):
  Constraint 3 (capacity): shadow price = $12.50/unit
    → Each additional unit of capacity is worth $12.50
  Constraint 7 (budget): shadow price = 1.3 units/$
    → Each additional dollar yields 1.3 units of output

Slack (underutilized resources):
  Constraint 1 (labor): slack = 15 hours
    → 15 hours of unused labor capacity
```

**Limitations**:
- LP assumes linearity; real relationships may be nonlinear
- ILP solution may not be stable (small changes → completely different solution)
- Shadow prices are local: valid only for small perturbations
- Solver may return one of many optimal solutions

---

### 2.2 Knapsack / Selection Results

**Math object**: Selected subset S ⊆ Items with total weight ≤ capacity and maximum value.

**Translation**:
- **Selected items**: what to include (invest in, carry, prioritize)
- **Rejected items**: what to leave out (defer, cut, skip)
- **Marginal items**: items barely included/excluded (the "borderline" decisions)
- **Value density**: value/weight ratio of each item (efficiency metric)

**Key insights to extract**:
- The selection and its total value
- The load factor: total weight / capacity (how full is the "knapsack"?)
- The most valuable rejected item (what's the first thing you'd add with more capacity?)
- The least valuable selected item (what's the first thing you'd cut if capacity shrinks?)

**Sensitivity**:
- Increase capacity by 10%: which new items enter?
- Remove the most valuable item: how does the solution restructure?
- Break ties: if multiple near-optimal solutions, which is most robust?

---

### 2.3 Scheduling Results

**Math object**: Assignment σ: Jobs → (Machine, Time) with constraints on overlap, precedence, deadlines.

**Translation**:
- **Gantt chart**: visual timeline of who does what when
- **Makespan**: total time from start to finish (measures overall speed)
- **Machine utilization**: fraction of time each machine is busy (measures efficiency)
- **Critical path**: the longest chain of dependent tasks (determines the makespan)
- **Slack**: for each task, how much it can be delayed without affecting the makespan

**Key insights to extract**:
- The schedule itself (Gantt chart)
- Makespan and whether it's optimal
- Critical path tasks (delay any of these → whole project delays)
- Non-critical tasks with slack (can be rescheduled flexibly)
- Machine utilization rates

**Sensitivity**:
- What if a task takes 20% longer than planned?
- What if a machine goes down? (re-solve without that machine)
- What if a new task is added?

---

## 3. Proof Results

### 3.1 Existence Proofs

**Translation**: "Such an object exists" → "It is possible to..."
- **Constructive proof**: You can build the object. Show how.
- **Non-constructive proof**: It exists but the proof doesn't show how to find it.
- **Counting proof**: There are so many objects that at least one must have the property.

**Key insights**:
- Does the proof give a construction method? (actionable vs. theoretical)
- How hard is it to actually find the object? (computational complexity)
- How many such objects exist? (abundance)

---

### 3.2 Impossibility Proofs

**Translation**: "No such object exists" → "It is impossible to..."
- **Hard impossibility**: No amount of resources or cleverness can achieve this
- **Conditional impossibility**: Impossible under the stated constraints (relax them and it might work)

**Key insights**:
- Which constraint causes the impossibility? (remove it → possible)
- What's the closest achievable approximation?
- Is the impossibility worst-case or average-case?

**Actionable**:
- "Since perfect [X] is impossible, the best achievable is [bound]"
- "To make it possible, you would need to relax [specific constraint]"

---

### 3.3 Bound Proofs

**Translation**: "The answer is at least L and at most U" → "You can guarantee..."
- **Upper bound**: "No matter what, you'll never need more than U"
- **Lower bound**: "No matter how clever, you can't do better than L"
- **Tight bound**: "L = U, so the answer is exactly determined"

**Key insights**:
- How tight is the bound? (gap between L and U)
- Is the bound achievable? (constructive or existential?)
- For which instances is the bound tight? (best/worst case characterization)

---

## 4. Counting Results

### 4.1 Exact Counts

**Translation**: "There are exactly N objects satisfying the condition"

**Key insights**:
- Is N large or small relative to expectations?
- What does N imply about probability? (P = favorable / total)
- Does N grow polynomially or exponentially with input size?
- Are the counted objects all equally likely? (uniform distribution assumption)

**Presentation**:
- For small N: list them all
- For medium N: present summary statistics and notable examples
- For large N: express in scientific notation, compare to familiar quantities

---

### 4.2 Asymptotic Counts

**Translation**: "The count grows as f(n) for large n"

**Key insights**:
- Growth rate: polynomial (tractable) vs exponential (intractable)
- Leading constant: for practical sizes, the constant matters
- Crossover point: at what n does the asymptotic behavior dominate?

---

## 5. Probability Results

### 5.1 Probability Values

**Translation**: "The probability is p"

**Presentation by audience**:
- **Technical**: p = 0.0385
- **Decision-maker**: "About 1 in 26" or "3.85% chance"
- **General**: "This happens about once every 26 tries"
- **Risk context**: Compare to familiar probabilities (coin flip, lottery, lightning strike)

**Key insights**:
- Is p high enough to plan for? (decision threshold)
- How does p change with parameters? (sensitivity)
- What's the expected number of occurrences in N trials? (N × p)

---

### 5.2 Expected Value Results

**Translation**: "On average, X = μ"

**Key insights**:
- μ is the long-run average, NOT what happens any single time
- Variance/SD tells you how much individual outcomes deviate
- If variance is high: the average is misleading; present the full distribution
- If variance is low: the average is reliable; the result is predictable

**Decision rule**:
- Risk-neutral: choose the option with highest E[X]
- Risk-averse: consider E[X] - k·σ(X) for some risk parameter k
- Minimax: consider worst-case outcome instead

---

## 6. Number Theory Results

**Translation**: "The equation has solutions x = ..." or "n has factors ..."

**Key insights**:
- Integer solutions may be parameterized: "x = 3 + 5t for any integer t"
- Factorization reveals structure: shared factors, coprimality, periodic behavior
- Modular results reveal cyclicity: "this pattern repeats every k steps"

**Practical applications**:
- Scheduling cycles: LCM determines when patterns align
- Fair distribution: GCD determines the largest unit of equal division
- Error detection: Modular arithmetic powers checksums and codes

---

## General Sensitivity Framework

For any solution type, apply this systematic check:

### 1. Input Perturbation
- Vary each numerical input by ±1, ±10%, ±2×
- Record: does the optimal solution change? does the objective change?
- Classify inputs as robust, sensitive, or critical

### 2. Constraint Perturbation
- Tighten each constraint by 10%: is it still feasible?
- Loosen each constraint by 10%: how much does the objective improve?
- Remove each constraint entirely: what's the unconstrained optimum?

### 3. Structural Perturbation
- Add/remove a vertex (entity)
- Add/remove an edge (relationship)
- Change the objective function
- Change the problem type (min → max, find → prove)

### 4. Model Validity Check
- Does the solution satisfy domain-specific common sense?
- Would a domain expert agree with the result?
- Are there real-world constraints not in the model?
- Is the data accurate and complete?

---

## General Limitation Framework

For any model, disclose these categories of limitations:

### 1. Modeling Assumptions
- What was simplified or idealized?
- What real-world factors were omitted?
- What relationships were assumed linear/static/deterministic?

### 2. Data Limitations
- How accurate are the input values?
- Are there missing data points?
- Is the data representative or biased?

### 3. Computational Limitations
- Is the solution proven optimal or heuristic?
- What's the optimality gap?
- Was there a time/memory limit that might have affected quality?

### 4. Scope Limitations
- What questions does this model NOT answer?
- What broader context is missing?
- What would a more sophisticated model capture?

### 5. Temporal Limitations
- When does this solution expire?
- How quickly do the inputs change?
- When should the analysis be refreshed?

---

## 7. Continuous Optimization Solutions

### 7.1 Convex Optimization Results

**Math object**: Optimal point x*, optimal value f(x*), dual variables λ*, constraint slackness.

**Translation**:
- **x***: The optimal allocation, portfolio weights, design parameters, control inputs
- **f(x*)**: The best achievable cost/return/error
- **Dual variables λ***: Sensitivity of the objective to each constraint (same as shadow prices in LP)
- **Active constraints**: Constraints where g_i(x*) = 0 -- these are the binding limitations

**Key insights to extract**:
- The optimal decisions and their real-world meaning
- How close to the unconstrained optimum (how much do constraints cost?)
- Which constraints are active (bottlenecks) vs. slack (have room)
- Dual values: "Relaxing constraint i by one unit improves the objective by λ_i"

**Sensitivity**:
- Vary constraint right-hand sides: how does the optimal value change? (dual values predict this locally)
- Vary objective coefficients: does the optimal point change?
- **Parametric sweep**: For portfolio problems, sweep the risk-return trade-off to generate an efficient frontier

**Limitations**:
- Convexity guarantees global optimum, but the model may not capture non-convex real-world phenomena
- Dual values are local: valid for small perturbations only
- Continuous solutions may need rounding for discrete real-world decisions

---

### 7.2 Least Squares / Regression Results

**Math object**: Coefficient vector β*, residuals r = y - Xβ*, R² statistic.

**Translation**:
- **β_j**: "A one-unit increase in variable j is associated with a β_j change in the outcome, holding other variables constant"
- **R²**: "The model explains R²×100% of the variation in the outcome"
- **Residuals**: The unexplained part -- what the model misses
- **Prediction**: ŷ_new = X_new β* with confidence interval

**Key insights to extract**:
- Which variables have the largest coefficients (most influential)
- Which variables have coefficients near zero (unimportant)
- R² value: how good is the fit overall?
- Residual pattern: any systematic error? (plot residuals vs. fitted values)

**Sensitivity**:
- Remove each variable: how much does R² drop?
- Add noise to input data: how stable are the coefficients?
- **Outlier influence**: does removing any single data point change the result substantially?

**Limitations**:
- Correlation is not causation -- β_j doesn't mean "changing x_j causes the outcome to change"
- Extrapolation beyond the data range is unreliable
- Assumes linear relationship (check residual plots)
- Multicollinearity can make individual coefficients unstable even if overall prediction is good

---

### 7.3 Nonlinear Optimization Results

**Math object**: Local minimum x*, objective f(x*), KKT conditions.

**Translation**:
- **x***: The locally best design/parameters/decision
- **"Locally optimal"**: Better than all nearby alternatives, but a different starting point might find a better solution
- **KKT multipliers**: Same interpretation as dual variables -- sensitivity to constraints

**Key insights to extract**:
- The solution and its real-world meaning
- How many local minima were found (if multi-start was used)
- Gap between best local minimum and any known lower bound
- Which constraints are active

**Sensitivity**:
- Run from 5-10 random initial points: do they all converge to the same solution?
- If not: report the range of solutions found and flag non-convexity
- Vary key parameters: does the local minimum shift smoothly or jump?

**Limitations**:
- **Non-convex problems have no guarantee of global optimality.** Always state this explicitly.
- Gradient-based methods may miss disconnected feasible regions
- Numerical convergence depends on scaling and conditioning

---

## 8. Statistical Inference Solutions

### 8.1 Hypothesis Test Results

**Math object**: Test statistic T, p-value, effect size d, confidence interval (L, U), sample sizes n₁, n₂.

**Translation**:
- **p-value**: "If there were truly no difference, we'd see a result this extreme only p×100% of the time"
  - p < 0.001: "Very strong evidence against no difference"
  - p < 0.05: "Moderate evidence against no difference"
  - p > 0.05: "Insufficient evidence to conclude a difference" (NOT "no difference exists")
- **Effect size**: The practical magnitude of the difference
  - Cohen's d < 0.2: negligible, d ≈ 0.5: medium, d ≈ 0.8: large
  - "The difference was d standard deviations"
- **Confidence interval**: "We are 95% confident the true difference lies between L and U"
  - If CI contains 0: consistent with no difference
  - Width of CI indicates precision

**Key insights to extract**:
- Is the effect statistically significant? (p-value)
- Is the effect practically meaningful? (effect size -- a large sample can make a tiny effect "significant")
- How precise is our estimate? (CI width)
- How much statistical power did we have? (could we have missed a real effect?)

**Standard report**:
```
Result: Group A (mean=4.2, SD=1.1, n=50) vs Group B (mean=5.1, SD=1.3, n=50)
Difference: 0.9 units (95% CI: [0.42, 1.38])
Effect size: Cohen's d = 0.75 (medium-to-large)
Test: Welch's t(96) = 3.74, p = 0.0003
Conclusion: Statistically significant and practically meaningful difference.
```

**Sensitivity**:
- Power analysis: "With these sample sizes, we had 92% power to detect this effect"
- What sample size would detect a smaller effect?
- How does the conclusion change at α = 0.01 vs. α = 0.05?

**Limitations**:
- Statistical significance ≠ practical importance (large n can make trivial effects significant)
- p-value is NOT the probability that H₀ is true
- Multiple testing: if you ran 20 tests, expect 1 false positive at α = 0.05
- CI assumes correct model (check assumptions: normality, independence)

---

### 8.2 Regression Results

**Math object**: Coefficients β̂, standard errors SE(β̂), p-values, R², residuals, prediction intervals.

**Translation**:
- **β̂_j**: "For each one-unit increase in X_j, Y changes by β̂_j units, holding other predictors constant"
- **R²**: "The model explains R²×100% of the variation in Y"
  - R² = 0.7 means "70% of the variation is explained"
  - R² = 0.3 doesn't mean the model is bad -- depends on the domain
- **p-value for β̂_j**: "Evidence that X_j has a nonzero relationship with Y"
- **Prediction interval**: Wider than CI -- covers where a NEW observation might fall

**Key insights to extract**:
- Which predictors matter most? (largest |β̂_j| after standardizing, or smallest p-value)
- How good is the overall fit? (R², adjusted R²)
- Are there any assumption violations? (residual plots)
- How well does the model predict new data? (cross-validated R²)

**Standard report**:
```
Model: Price = $45,000 + $120/sqft × Area + $8,500 × Bedrooms - $2,000/year × Age
R² = 0.78, Adjusted R² = 0.76
F(3, 96) = 112.4, p < 0.001

Key coefficients:
  Area:     +$120/sqft  (95% CI: [$95, $145], p < 0.001) -- strongest predictor
  Bedrooms: +$8,500     (95% CI: [$3,200, $13,800], p = 0.002)
  Age:      -$2,000/yr  (95% CI: [-$3,100, -$900], p = 0.004)
```

**Sensitivity**:
- Remove each predictor: how much does R² drop? (variable importance)
- Cross-validation R²: how well does the model generalize?
- Influential observations: Cook's distance > 1 flags influential points

**Limitations**:
- Regression shows association, NOT causation
- Extrapolation beyond the data range is unreliable
- Multicollinearity inflates standard errors (check VIF > 10)
- Omitted variable bias: unmeasured confounders can distort coefficients

---

### 8.3 Confidence/Credible Interval Results

**Math object**: Interval (L, U) with coverage probability 1-α.

**Translation**:
- **Frequentist CI**: "If we repeated this study many times, 95% of such intervals would contain the true value"
  - NOT "there is a 95% probability the true value is in this interval"
- **Bayesian credible interval**: "There is a 95% probability the parameter lies in this interval" (given the prior and data)
  - This IS a direct probability statement (under the Bayesian framework)

**Key insights to extract**:
- Point estimate (center of interval)
- Precision: narrow interval = precise estimate, wide = uncertain
- Does the interval contain a meaningful threshold? (e.g., does CI for difference contain 0?)
- Asymmetry: if the interval is lopsided, the distribution is skewed

**Presentation by audience**:
- **Technical**: "95% CI: [2.3, 4.7], SE = 0.6, n = 120"
- **Decision-maker**: "The true value is between 2.3 and 4.7, most likely around 3.5"
- **General**: "We're quite confident the answer is somewhere between 2 and 5"

**Sensitivity**:
- How does the interval width change with sample size? (halving width requires 4× sample)
- What confidence level changes the decision? (90% CI vs. 95% CI vs. 99% CI)

---

### 8.4 Bayesian Posterior Results

**Math object**: Posterior distribution P(θ|data), credible intervals, posterior predictive distribution.

**Translation**:
- **Posterior mean/median**: "Our best estimate of the parameter after seeing the data"
- **Credible interval**: "There is a 95% probability the parameter is in this range"
- **Prior → Posterior**: "Before seeing data, we believed θ was around [prior mean]. After seeing the data, we updated to [posterior mean]."
- **P(θ > threshold)**: "The probability that the parameter exceeds the threshold is X%"

**Key insights to extract**:
- How much did the data change our beliefs? (compare prior and posterior)
- How certain are we? (posterior width)
- What is the probability of a practically meaningful effect? P(|θ| > ROPE)
- Posterior predictive: what do we expect for future observations?

**Standard report**:
```
Bayesian A/B Test Results:
  Variant A: posterior mean = 3.2% (95% CrI: [2.8%, 3.6%])
  Variant B: posterior mean = 3.8% (95% CrI: [3.3%, 4.3%])
  P(B > A) = 94.3%
  Expected lift: +0.6 percentage points (95% CrI: [-0.1%, +1.3%])
  Recommendation: B is very likely better, but the lift could be small.
```

**Sensitivity**:
- Prior sensitivity: how does the posterior change with different priors?
  - If the conclusion is robust to reasonable priors: strong evidence
  - If the conclusion flips: the data is insufficient to overcome prior uncertainty
- How much more data would substantially narrow the posterior?

**Limitations**:
- Results depend on the prior (always disclose prior choice and rationale)
- MCMC may not have converged (check R-hat < 1.01, ESS > 400)
- Posterior predictive checks: does the model generate data that looks like the real data?

---

## Cross-Reference Index

Which visualization to use for each result type, and where results come from.

| Interpretation Section | Visualization (visualization.md) | Algorithms (algorithms.md) | Structures (structures.md) |
|---|---|---|---|
| §1.1 Shortest Path | §1 Graph Diagram (annotated) | §2 Shortest Path (A8-A12) | §1.3 Weighted Graph |
| §1.2 Matching | §2 Assignment Matrix Heatmap | §4 Matching (A15-A18) | §1.4 Bipartite Graph |
| §1.3 Coloring | §1 Graph Diagram (colored) | §6 Coloring (A21-A22) | §1.1 Simple Graph |
| §1.4 Flow | §8 Flow Diagram | §5 Network Flow (A19-A20) | §1.3 Weighted Graph |
| §1.5 Connectivity | §1 Graph Diagram (components) | §1 Traversal (A5-A7) | §1.1-1.2 Graphs |
| §2.1 LP/ILP | §4 Tornado (sensitivity), §5 Scenario Comparison | §10 LP/ILP (A31-A34) | §7.1 ILP |
| §2.2 Knapsack | §6 Distribution Bar Chart | §11 DP (A33-A34) | §7.1 ILP |
| §2.3 Scheduling | §3 Gantt Chart | §1 Traversal (A3 Topo Sort), §10 ILP | §7.3 Scheduling Model |
| §3 Proofs | §10 Proof Step Visualization | §17 Proof Techniques (A74-A77) | §4 Logic |
| §4 Counting | §6 Distribution Bar Chart | §15 Counting (A63-A69) | §2 Combinatorics |
| §5 Probability | §6 Distribution/PMF, §7 Pareto | §18 Probability (A78-A81) | §8 Discrete Probability |
| §6 Number Theory | (text-based) | §14 Number Theory (A53-A62) | §5 Number Theory |
| §7.1 Convex Opt | §7 Pareto Frontier, §4 Tornado | §21 Continuous Opt (A87-A88) | §9.2 Convex Program |
| §7.2 Least Squares | §6 Bar Chart (coefficients), scatter (fit) | §21 Continuous Opt (A91-A92) | §9.4 Least Squares |
| §7.3 Nonlinear Opt | §7 Pareto, §5 Scenario Comparison | §21 Continuous Opt (A93-A94) | §9.5 Nonlinear Constrained |
| §8.1 Hypothesis Tests | §11 Group Comparison (bar+CI) | algorithms-statistics.md S6-S17 | §10.2 Statistical Hypothesis |
| §8.2 Regression | §13 Regression Plot, §14 Residual Plot | algorithms-statistics.md S23-S30 | §10.3 Regression Model |
| §8.3 CI/CrI | §11 Group Comparison, §15 Forest Plot | algorithms-statistics.md S18-S22 | §10.1 Random Variable |
| §8.4 Bayesian | §16 Posterior Plot | algorithms-statistics.md S31-S35 | §10.4 Bayesian Model |

Also see: **common-mistakes.md** §I1-I6 for interpretation pitfalls.
