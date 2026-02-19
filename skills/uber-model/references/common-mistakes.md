# Common Mistakes & Anti-Patterns

A pre-flight checklist of mistakes that frequently occur during modeling, solving, and interpretation. Read this during Phase 3 of uber-model (before finalizing the formal model) and during Phase 0 of uber-solve (before selecting an algorithm).

---

## Modeling Mistakes (uber-model)

### M1: Forgetting Integrality

**Mistake**: Modeling a discrete decision as a continuous variable.
**Example**: "Assign employees to projects" modeled with x_ij in [0,1] instead of x_ij in {0,1}. The LP relaxation may assign 0.5 of an employee to each of two projects.
**Fix**: If the real-world quantity is inherently discrete (people, items, yes/no decisions), use integer or binary variables.
**Check**: For each variable, ask: "Can this take a fractional value in the real world?"

---

### M2: Wrong Edge Direction

**Mistake**: Reversing the direction of arcs in a directed graph.
**Example**: "Course A is a prerequisite for Course B" modeled as edge B→A instead of A→B. This reverses the dependency.
**Fix**: Convention: arc (u,v) means "u must come before v" or "u leads to v." State the convention explicitly.
**Check**: Pick one edge and read it aloud: "Does [source] really [relationship] [target]?"

---

### M3: Conflating Decision Variables with Parameters

**Mistake**: Treating a given constant as a variable to optimize, or treating a decision variable as fixed data.
**Example**: Capacity per employee is a given parameter (data), not something to optimize. The assignment x_ij is the decision variable.
**Fix**: Before building the model, explicitly list: (1) What is given (parameters/data), (2) What we choose (decision variables), (3) What we measure (objective).
**Check**: Is this quantity something we *choose*, or something we *know*?

---

### M4: Over-Constraining

**Mistake**: Adding constraints that aren't in the original problem, often from unstated assumptions.
**Example**: User says "assign inspectors to facilities." Modeler adds "each inspector handles exactly 2 facilities" when the user only said "at most 3."
**Fix**: Every constraint must trace back to a specific condition in the Problem Understanding (Phase 1). If it doesn't, it's an assumption -- flag it.
**Check**: For each constraint, point to the sentence in the problem statement that requires it.

---

### M5: Under-Constraining

**Mistake**: Forgetting an implicit constraint that the user takes for granted.
**Common omissions**:
- Non-negativity: x >= 0 (quantities can't be negative)
- Integrality: x in Z (can't hire 2.7 people)
- Connectivity: the solution graph must be connected (not assumed by default)
- Finiteness: the universe is finite (critical for counting)
- Uniqueness: each element used at most once (no double-counting)
- Boundary conditions: what happens at n=0 or when a set is empty

**Fix**: After building the model, systematically check: non-negativity, integrality, connectivity, boundary behavior.
**Check**: "If I gave this model to a solver with no other context, could it produce a solution that's technically feasible but obviously wrong?"

---

### M6: Wrong Graph Type

**Mistake**: Using an undirected graph when the relationship is asymmetric, or a simple graph when parallel edges matter.
**Examples**:
- "A follows B on social media" is directed (A→B), not undirected
- "Multiple flights between two cities" needs a multigraph, not a simple graph
- "Three people share a meeting" needs a hyperedge, not pairwise edges

**Fix**: Ask: "Is the relationship symmetric? Can there be multiple relationships between the same pair? Can a relationship involve more than two entities?"
**Check**: Review the Indicators section of each graph type in structures.md.

---

### M7: Objective-Constraint Confusion

**Mistake**: Putting an objective into a constraint, or a constraint into the objective.
**Example**: "Minimize cost while ensuring quality >= 7" should be: Objective = minimize cost, Constraint = quality >= 7. NOT: Objective = minimize (cost - lambda * quality).
**Fix**: The objective is what you optimize. Constraints are what you must satisfy. If the user says "while" or "subject to" or "such that," that's a constraint.
**Exception**: Multi-objective problems legitimately combine objectives. If unsure, ask the user.

---

### M8: Ignoring the Complement/Dual

**Mistake**: Modeling the problem directly when the complement or dual formulation is simpler.
**Examples**:
- "Find the largest group with no conflicts" (independent set) is equivalent to "find the smallest set covering all conflicts" (vertex cover): |IS| + |VC| = |V|
- "Maximize flow" has the dual "find minimum cut" which may be more interpretable
- "Find vertices NOT in the solution" may be easier than "find vertices IN the solution"

**Fix**: During Phase 2 (Devising a Plan), always ask: "Would the complement, dual, or negation be simpler?" (Heuristic H11: Restate the Problem)

---

### M9: Scale Mismatch

**Mistake**: Mixing units or scales in the same model without normalization.
**Example**: Edge weights combining "distance in km" and "time in hours" without converting to a common unit or weighting scheme.
**Fix**: All data in the model must be in compatible units. If combining different quantities, explicitly define the weighting and state the trade-off.
**Check**: Do all edge weights / constraint coefficients have the same units? If not, is the conversion explicit?

---

### M10: Assuming Linearity

**Mistake**: Using a linear model when the real relationship is nonlinear.
**Examples**:
- "Doubling staff doubles output" -- often false due to coordination overhead
- "Cost per unit is constant" -- may have volume discounts or step functions
- "Quality is proportional to time spent" -- often has diminishing returns

**Fix**: Ask: "Does doubling the input double the output?" If not, the model needs nonlinear terms or piecewise-linear approximation.

---

## Solving Mistakes (uber-solve)

### S1: Greedy on NP-Hard Problems

**Mistake**: Applying a greedy algorithm to a problem that requires exact methods, without acknowledging the approximation.
**Example**: Using greedy coloring and reporting the result as "the minimum number of colors" when graph coloring is NP-hard.
**Fix**: Always classify the problem's complexity first (Phase 0 of uber-solve). If NP-hard, use ILP/SAT for exact solutions on small instances, or explicitly state the approximation ratio.
**Check**: "Is this problem in P? If not, is my algorithm exact or approximate?"

---

### S2: Wrong Algorithm for Graph Type

**Mistake**: Applying an algorithm that requires a specific graph property to a graph that doesn't have it.
**Examples**:
- Dijkstra on a graph with negative weights (gives wrong answer)
- Bipartite matching on a non-bipartite graph
- Topological sort on a graph with cycles
- Longest path via DP on a graph with cycles (only works on DAGs)

**Fix**: Before selecting an algorithm, verify the prerequisites: non-negative weights, bipartiteness, acyclicity, connectivity, planarity.
**Check**: "Does my graph satisfy the algorithm's preconditions?"

---

### S3: Not Verifying Independently

**Mistake**: Trusting the solver's output without independent verification.
**Example**: PuLP reports "Optimal" but you don't check whether the solution actually satisfies all constraints.
**Fix**: The `verify()` function must be independent of the `solve()` function. It re-checks every constraint from the formal model. Never trust a solver without verification.

---

### S4: Ignoring Numerical Issues

**Mistake**: Treating floating-point solver output as exact.
**Examples**:
- Binary variable x = 0.9999999 treated as 0 instead of 1
- Constraint satisfied within tolerance (1e-8) but violated in exact arithmetic
- Comparing floating-point values with `==` instead of `abs(a-b) < epsilon`

**Fix**: Round binary variables. Use tolerance-aware comparisons. For exact answers, use SymPy Rational or Z3 exact mode.

---

### S5: Missing Edge Cases

**Mistake**: Not handling degenerate inputs.
**Common edge cases**:
- Empty input (n=0): should return trivial solution, not crash
- Single element (n=1): degenerate but valid
- Disconnected graph: must decompose or handle components
- All-equal weights: many optimal solutions, algorithm must handle ties
- Infeasible instance: must detect and report, not loop forever

**Fix**: Test with n=0, n=1, disconnected input, all-identical input, and a known-infeasible instance before declaring the solver correct.

---

### S6: Premature Approximation

**Mistake**: Using a heuristic or approximation when an exact solution is feasible.
**Example**: Using simulated annealing for a 15-node TSP when Held-Karp DP can solve it exactly in milliseconds.
**Fix**: Consult the Algorithm Selection Matrix in algorithms.md. Use exact methods for small/medium instances. Only approximate when exact methods are demonstrably infeasible.

---

## Interpretation Mistakes (uber-interpret)

### I1: Presenting Math Instead of Meaning

**Mistake**: Reporting "x_{2,5} = 1, objective = 47" without translating back to "Employee 2 is assigned to Project 5, total skill match score is 47 out of 60."
**Fix**: Every mathematical symbol must be mapped back to its real-world meaning. The user should never need to decode subscripts.

---

### I2: Overstating Precision

**Mistake**: Reporting "the probability is 0.038461538..." when "about 1 in 26" is more appropriate for the audience.
**Fix**: Match precision to the audience and the data's accuracy. If inputs are estimates, the output shouldn't imply 10-digit precision.

---

### I3: Ignoring Model Limitations

**Mistake**: Presenting the optimal solution as "the answer" without disclosing what the model doesn't capture.
**Example**: "The optimal schedule has no conflicts" -- but the model doesn't account for travel time between rooms.
**Fix**: Every interpretation must include a Limitations section listing what the model assumes and what it ignores.

---

### I4: Sensitivity Theater

**Mistake**: Running sensitivity analysis on parameters that obviously don't matter, while ignoring the ones that do.
**Example**: Varying a cost coefficient by ±10% when the real uncertainty is in whether a constraint will change structurally.
**Fix**: Identify the 3-5 parameters the user is most uncertain about, and test those. Ask if unsure.

---

### I5: Recommendations Without Justification

**Mistake**: Saying "you should do X" without connecting the recommendation to the mathematical result.
**Fix**: Every recommendation must trace to a specific finding: "Because constraint C3 is the binding bottleneck (shadow price = $12.50/unit), increasing capacity here gives the best return."

---

### I6: Confusing Optimal with Good

**Mistake**: Implying that "optimal" means "the right thing to do" without acknowledging that optimality is relative to the model.
**Example**: The mathematically optimal assignment maximizes skill match but ignores team dynamics, which aren't in the model.
**Fix**: Frame as: "This is optimal *given the model*. If [unstated factor] matters, the recommendation may change."

---

## Cross-Reference Index

| Mistake | Where It Matters Most |
|---|---|
| M1 Integrality | **structures.md** §7.1 ILP, **solvers.md** §2 PuLP |
| M2 Edge Direction | **structures.md** §1.2 Digraph vs §1.1 Simple Graph |
| M3 Variables vs Parameters | **structures.md** §7.1 ILP (variable/constraint distinction) |
| M6 Wrong Graph Type | **structures.md** §1 Graph Theory (all 8 types), **problem-classification.md** Decision Tree |
| M7 Objective vs Constraint | **structures.md** §7.1 ILP, **algorithms.md** §10 LP/ILP |
| M10 Assuming Linearity | **structures.md** §9 Continuous Optimization, **algorithms.md** §21 Continuous Opt |
| S1 Greedy on NP-hard | **algorithms.md** Algorithm Selection Matrix, **problem-classification.md** Complexity Quick Check |
| S2 Wrong Algorithm | **algorithms.md** Cross-Reference Index (structure → algorithm mapping) |
| S6 Premature Approximation | **algorithms.md** Algorithm Selection Matrix (small/medium/large columns) |
| I1-I6 Interpretation | **interpretation-patterns.md** (all sections), **visualization.md** Chart Selection Matrix |
