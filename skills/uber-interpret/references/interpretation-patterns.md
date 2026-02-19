# Interpretation Patterns by Domain

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
