# Mathematical Structure Catalog

**Scope**: Discrete Mathematics (32 structures), Continuous Optimization (5 structures), Statistical Inference (6 structures), Linear Algebra (4 structures), Calculus (3 structures), Geometry & Trigonometry (4 structures), Financial Mathematics (1 structure), Game Theory (3 structures), Decision Analysis (3 structures), Multi-Objective Optimization (3 structures)

A catalog of mathematical structures organized by domain. Use this to match real-world problems to mathematical models during Phase 2 of the uber-model skill.

Each entry has:
- **Definition**: One-line formal definition
- **Indicators**: Real-world phrases that suggest this structure
- **Template**: Formal notation template
- **Examples**: Real-world to math mappings
- **Key problems**: Classic named problems

---

## 1. Graph Theory

### 1.1 Simple Graph

**Definition**: G = (V, E) where V is a finite set of vertices and E is a set of unordered pairs from V.

**Indicators**: "relationships", "connections", "friends", "adjacent", "neighbors", "linked", "compatible", "incompatible", "conflict"

**Template**:
```
V = {v1, v2, ..., vn}        -- the entities
E = {{vi, vj} : condition}   -- pairs that are related
```

**Examples**:
- Social network: V = people, E = {(a,b) : a knows b}
- Conflict graph: V = tasks, E = {(a,b) : a conflicts with b}
- Compatibility graph: V = items, E = {(a,b) : a compatible with b}

**Key problems**: Connectivity, coloring, independent set, vertex cover, clique, Hamiltonian cycle, planarity

---

### 1.2 Directed Graph (Digraph)

**Definition**: D = (V, A) where A is a set of ordered pairs (arcs) from V.

**Indicators**: "depends on", "precedes", "leads to", "flows to", "one-way", "prerequisite", "causes", "implies"

**Template**:
```
V = {v1, v2, ..., vn}
A = {(vi, vj) : vi [relation] vj}   -- direction matters
```

**Examples**:
- Prerequisite structure: V = courses, A = {(a,b) : a is prerequisite for b}
- Web pages: V = pages, A = {(a,b) : a links to b}
- Causal model: V = events, A = {(a,b) : a causes b}

**Key problems**: Reachability, shortest path, topological sort, strongly connected components, cycle detection

---

### 1.3 Weighted Graph

**Definition**: G = (V, E, w) where w: E -> R assigns a weight (cost, distance, capacity) to each edge.

**Indicators**: "distance", "cost", "time", "weight", "capacity", "strength", "similarity score"

**Template**:
```
G = (V, E, w)
w(e) = [cost/distance/capacity] for each edge e
```

**Examples**:
- Road network: V = cities, E = roads, w = distance in km
- Communication network: V = servers, E = links, w = bandwidth
- Similarity graph: V = items, E = pairs, w = similarity score

**Key problems**: Shortest path (Dijkstra, Bellman-Ford), minimum spanning tree (Kruskal, Prim), traveling salesman

---

### 1.4 Bipartite Graph

**Definition**: G = (X, Y, E) where V = X ∪ Y, X ∩ Y = ∅, and every edge connects an element of X to an element of Y.

**Indicators**: "assign", "match", "pair", "two types", "employees and projects", "students and courses", "supply and demand"

**Template**:
```
X = {x1, ..., xm}   -- type 1 entities
Y = {y1, ..., yn}   -- type 2 entities
E = {(xi, yj) : xi [can be matched to] yj}
```

**Examples**:
- Job assignment: X = workers, Y = jobs, E = {(w,j) : w qualified for j}
- Course enrollment: X = students, Y = courses, E = {(s,c) : s wants c}
- Buyer-seller: X = buyers, Y = sellers, E = {(b,s) : b willing to buy from s}

**Key problems**: Maximum matching (Hungarian), stable matching, vertex cover (Konig's theorem), Hall's theorem

---

### 1.5 Tree

**Definition**: Connected acyclic graph. Equivalently: connected graph with n-1 edges on n vertices.

**Indicators**: "hierarchy", "parent-child", "taxonomy", "organizational chart", "file system", "decision tree", "branching"

**Template**:
```
T = (V, E) where |E| = |V| - 1, connected
Root r in V (if rooted)
parent(v) for each v != r
children(v) = {u : parent(u) = v}
```

**Examples**:
- Organization: V = employees, edges = reporting relationships, root = CEO
- Classification: V = categories, edges = subcategory relations
- Decision: V = states, edges = choices, leaves = outcomes

**Key problems**: Spanning tree, lowest common ancestor, tree isomorphism, Huffman coding, tree decomposition

---

### 1.6 Directed Acyclic Graph (DAG)

**Definition**: Directed graph with no directed cycles.

**Indicators**: "dependencies", "prerequisites", "before/after", "stages", "pipeline", "workflow", "task ordering"

**Template**:
```
D = (V, A), no directed cycle
Topological order: v1, v2, ..., vn where (vi, vj) in A implies i < j
```

**Examples**:
- Build system: V = tasks, A = {(a,b) : a must complete before b}
- Course plan: V = courses, A = {(a,b) : a prerequisite for b}
- Data pipeline: V = processing steps, A = {(a,b) : a feeds into b}

**Key problems**: Topological sort, longest path (critical path), transitive closure, DAG shortest path

---

### 1.7 Hypergraph

**Definition**: H = (V, E) where E is a family of subsets of V (hyperedges can connect more than 2 vertices).

**Indicators**: "group constraint", "involves multiple parties", "committee", "shared resource", "multi-way relationship"

**Template**:
```
V = {v1, ..., vn}
E = {e1, ..., em} where each ei ⊆ V, |ei| >= 2
```

**Examples**:
- Meeting scheduling: V = time slots, E = {participants needed for each meeting}
- Database design: V = attributes, E = {functional dependencies}
- Chemical reactions: V = molecules, E = {sets that react together}

**Key problems**: Hypergraph coloring, transversals, set cover

---

### 1.8 Multigraph

**Definition**: Graph allowing multiple edges between the same pair of vertices.

**Indicators**: "multiple connections", "parallel routes", "redundant links", "repeated interactions"

**Template**:
```
G = (V, E) where E is a multiset of pairs from V
```

**Examples**:
- Flight network: V = airports, E = {flights} (multiple flights between same cities)
- Communication: V = people, E = {messages} (multiple messages between same pair)

**Key problems**: Eulerian path/circuit, edge connectivity

---

## 2. Combinatorics

### 2.1 Permutations

**Definition**: Ordered arrangements of n elements, or k elements chosen from n.

**Indicators**: "arrange", "order matters", "sequence", "ranking", "lineup", "schedule order"

**Template**:
```
P(n, k) = n! / (n-k)!    -- k-permutations of n
n!                         -- all permutations of n
```

**Examples**:
- Race finishing order: P(10, 3) = first, second, third from 10 runners
- Password: 26^k = k-character strings from alphabet
- Seating arrangement: n! ways to seat n people in a row

**Key problems**: Counting permutations, permutation groups, derangements, inversions

---

### 2.2 Combinations

**Definition**: Unordered selections of k elements from n.

**Indicators**: "choose", "select", "team of k from n", "committee", "subset", "how many ways"

**Template**:
```
C(n, k) = n! / (k!(n-k)!)
```

**Examples**:
- Committee: C(20, 5) = choose 5 from 20 people
- Lottery: C(49, 6) = choose 6 numbers from 49
- Feature selection: C(100, 10) = choose 10 features from 100

**Key problems**: Binomial coefficients, Pascal's triangle, Vandermonde identity, stars and bars

---

### 2.3 Partitions (Integer)

**Definition**: Ways to write integer n as sum of positive integers, ignoring order.

**Indicators**: "split a total", "distribute evenly", "break into parts", "decompose a number"

**Template**:
```
n = a1 + a2 + ... + ak where a1 >= a2 >= ... >= ak >= 1
```

**Examples**:
- Budget allocation: Split $100 among departments
- Load balancing: Distribute n tasks across k identical servers

**Key problems**: Partition function p(n), generating functions, Ferrers diagrams, restricted partitions

---

### 2.4 Compositions

**Definition**: Ordered partitions -- ways to write n as ordered sum of positive integers.

**Indicators**: "sequence of steps summing to total", "ordered allocation", "stages"

**Template**:
```
n = a1 + a2 + ... + ak where ai >= 1, order matters
Number of compositions of n into k parts: C(n-1, k-1)
```

**Examples**:
- Road trip stages: Total 500 miles, split into 3 daily legs (order matters)
- Investment over time: Allocate budget across quarters

**Key problems**: Counting compositions, restricted compositions

---

### 2.5 Latin Squares

**Definition**: n x n array filled with n different symbols, each occurring exactly once in each row and column.

**Indicators**: "round-robin", "balanced design", "each pairing exactly once", "Sudoku-like"

**Template**:
```
L[i][j] in {1, ..., n}
for all i: {L[i][j] : j = 1..n} = {1, ..., n}
for all j: {L[i][j] : i = 1..n} = {1, ..., n}
```

**Examples**:
- Round-robin tournament: Each team plays every other exactly once per round
- Experimental design: Each treatment applied once per row and column

**Key problems**: Latin square completion, orthogonal Latin squares, Sudoku

---

## 3. Set Theory

### 3.1 Sets and Multisets

**Definition**: Set = unordered collection of distinct elements. Multiset = allows repeated elements.

**Indicators**: "collection", "group", "members", "belongs to", "contains", "elements"

**Template**:
```
S = {x : P(x)}     -- set builder notation
|S| = n             -- cardinality
S ∪ T, S ∩ T, S \ T, S^c   -- operations
```

**Examples**:
- Inventory: S = {items in stock}
- Skills: S_i = {skills of employee i}
- Requirements: R = {features needed}

**Key problems**: Membership, inclusion-exclusion, union/intersection bounds

---

### 3.2 Set Systems (Families of Sets)

**Definition**: F = {S1, S2, ..., Sm} where each Si ⊆ U for some universe U.

**Indicators**: "overlapping groups", "coverage", "hitting set", "which groups cover which elements"

**Template**:
```
U = {u1, ..., un}         -- universe
F = {S1, ..., Sm}         -- family of subsets
Si ⊆ U for each i
```

**Examples**:
- Service areas: U = customers, Si = customers served by facility i
- Test suites: U = code paths, Si = paths covered by test i
- Skills matrix: U = required skills, Si = skills of employee i

**Key problems**: Set cover, hitting set, sunflower lemma, VC dimension

---

### 3.3 Power Set

**Definition**: P(S) = {T : T ⊆ S}, the set of all subsets. |P(S)| = 2^|S|.

**Indicators**: "all possible subsets", "every combination", "feature subsets", "all subgroups"

**Template**:
```
P(S) = {∅, {a}, {b}, {a,b}, ...}
|P(S)| = 2^n
```

**Examples**:
- Feature selection: Evaluate all subsets of features
- Coalition game: Consider all possible coalitions of players

**Key problems**: Enumeration, Boolean lattice, monotone functions

---

### 3.4 Set Partition

**Definition**: A partition of S into blocks B1, ..., Bk where Bi ∩ Bj = ∅ and B1 ∪ ... ∪ Bk = S.

**Indicators**: "classify", "group into categories", "cluster", "divide into non-overlapping groups"

**Template**:
```
{B1, B2, ..., Bk} where:
  Bi ≠ ∅ for all i
  Bi ∩ Bj = ∅ for i ≠ j
  B1 ∪ B2 ∪ ... ∪ Bk = S
```

**Examples**:
- Customer segmentation: Partition customers into market segments
- Equivalence classes: Partition by equivalence relation
- Load balancing: Partition tasks into worker groups

**Key problems**: Bell numbers (counting partitions), Stirling numbers, balanced partition, graph partitioning

---

## 4. Logic

### 4.1 Propositional Logic

**Definition**: Formulas built from Boolean variables, connectives (AND, OR, NOT, IMPLIES), evaluated as true/false.

**Indicators**: "if-then rules", "conditions", "true or false", "satisfiable", "consistent"

**Template**:
```
Variables: p, q, r, ...
Formula: φ = (p ∧ q) → r
Satisfying assignment: {p=T, q=T, r=T}
```

**Examples**:
- Business rules: "If premium customer AND order > $100, then free shipping"
- Configuration: "If feature A selected, then feature B required"
- Eligibility: "Must satisfy (age >= 18 AND citizen) OR (has visa)"

**Key problems**: SAT, tautology, CNF conversion, resolution

---

### 4.2 Predicate Logic

**Definition**: Extension of propositional logic with quantifiers (forall, exists) and predicates over domains.

**Indicators**: "for all", "there exists", "every", "some", "no X satisfies", "universal rule"

**Template**:
```
Domain D
Predicates: P(x), Q(x,y), ...
Formula: ∀x ∈ D: P(x) → ∃y ∈ D: Q(x,y)
```

**Examples**:
- Regulatory compliance: "For all products p: if food(p) then has_label(p)"
- Database query: "Find all x such that enrolled(x, 'CS101') and not enrolled(x, 'CS102')"
- Specification: "Every server must be connected to at least one backup"

**Key problems**: Validity, satisfiability, model checking, Skolemization

---

### 4.3 Modal / Deontic Logic

**Definition**: Logic with modalities: necessity (□), possibility (◇), obligation (O), permission (P).

**Indicators**: "must", "may", "should", "required", "permitted", "forbidden", "obligated"

**Template**:
```
O(φ)  -- it is obligatory that φ
P(φ)  -- it is permitted that φ
F(φ)  -- it is forbidden that φ  (= O(¬φ))
```

**Examples**:
- Regulatory: "Food products must display allergen information" → O(display_allergens(x))
- Policy: "Employees may work remotely on Fridays" → P(remote(e, friday))
- Ethics: "It is forbidden to share customer data without consent" → F(share(data) ∧ ¬consent)

**Key problems**: Deontic consistency, obligation conflict detection, norm compliance checking

---

### 4.4 Constraint Satisfaction

**Definition**: A set of variables, each with a domain, and a set of constraints restricting allowed value combinations.

**Indicators**: "constraints", "restrictions", "must satisfy", "feasible assignment", "valid configuration"

**Template**:
```
Variables: x1, ..., xn
Domains: D1, ..., Dn
Constraints: C1, ..., Cm (each Ci restricts a subset of variables)
Find: assignment xi ∈ Di satisfying all Ci
```

**Examples**:
- Scheduling: Variables = time slots for events, domains = available times, constraints = no conflicts
- Sudoku: Variables = cells, domains = {1..9}, constraints = row/col/box uniqueness
- Configuration: Variables = component choices, domains = options, constraints = compatibility

**Key problems**: CSP, arc consistency, backtracking, constraint propagation

---

## 5. Number Theory

### 5.1 Modular Arithmetic

**Definition**: Arithmetic on integers modulo n. a ≡ b (mod n) iff n | (a - b).

**Indicators**: "remainder", "cyclic", "repeating pattern", "clock arithmetic", "periodic", "divisible by"

**Template**:
```
Z_n = {0, 1, ..., n-1}
a ≡ b (mod n)
Operations: + (mod n), × (mod n)
```

**Examples**:
- Scheduling: Days of week cycle mod 7
- Hashing: h(x) = x mod m
- Checksum: ISBN check digit, Luhn algorithm

**Key problems**: Chinese Remainder Theorem, modular exponentiation, discrete logarithm, Euler's theorem

---

### 5.2 Divisibility Structures

**Definition**: Relationships based on divisibility: a | b (a divides b).

**Indicators**: "divides evenly", "factor", "multiple", "GCD", "LCM", "prime factorization"

**Template**:
```
a | b iff ∃k: b = ka
gcd(a, b), lcm(a, b)
Prime factorization: n = p1^a1 × p2^a2 × ... × pk^ak
```

**Examples**:
- Resource sharing: GCD gives largest common divisor for equal partitioning
- Synchronization: LCM gives first common recurrence

**Key problems**: GCD (Euclidean algorithm), primality testing, factorization, Bezout's identity

---

### 5.3 Diophantine Equations

**Definition**: Polynomial equations where only integer solutions are sought.

**Indicators**: "integer solution", "whole numbers only", "exact division", "no fractions"

**Template**:
```
f(x1, ..., xn) = 0 where xi ∈ Z
Example: ax + by = c has solutions iff gcd(a,b) | c
```

**Examples**:
- Coin problem: How to make change for $n using coins of value a, b, c?
- Resource allocation: Buy x items at $3 and y items at $5 to spend exactly $100

**Key problems**: Linear Diophantine equations, Frobenius number, Pell's equation

---

## 6. Relations and Orders

### 6.1 Partial Order

**Definition**: A relation ≤ on set S that is reflexive, antisymmetric, and transitive. (S, ≤) is a poset.

**Indicators**: "ranking with ties", "hierarchy", "prerequisite", "dominates", "at least as good as", "subsumes"

**Template**:
```
(S, ≤) where:
  a ≤ a (reflexive)
  a ≤ b and b ≤ a implies a = b (antisymmetric)
  a ≤ b and b ≤ c implies a ≤ c (transitive)
```

**Examples**:
- Task dependencies: (Tasks, must-precede)
- Subset ordering: (P(S), ⊆)
- Divisibility: (N, |) where a ≤ b iff a | b
- Skill levels: (Certifications, prerequisite-of)

**Key problems**: Topological sort, chain/antichain (Dilworth), width, linear extension, maximal/minimal elements

---

### 6.2 Equivalence Relation

**Definition**: A relation ~ on set S that is reflexive, symmetric, and transitive. Partitions S into equivalence classes.

**Indicators**: "same as", "equivalent", "interchangeable", "classify", "group by", "indistinguishable"

**Template**:
```
~ on S where:
  a ~ a (reflexive)
  a ~ b implies b ~ a (symmetric)
  a ~ b and b ~ c implies a ~ c (transitive)
Equivalence classes: [a] = {b ∈ S : b ~ a}
S/~ = {[a] : a ∈ S}  -- quotient set
```

**Examples**:
- Congruence: Integers mod n
- Isomorphism: Graphs up to relabeling
- Equivalence of configurations: States that behave identically

**Key problems**: Counting equivalence classes (Burnside), partition refinement, quotient structures

---

### 6.3 Lattice

**Definition**: A poset where every pair of elements has a unique least upper bound (join) and greatest lower bound (meet).

**Indicators**: "most specific common generalization", "least common specialization", "hierarchy with merging", "concept lattice"

**Template**:
```
(L, ≤) where:
  a ∨ b exists (join / LUB) for all a, b
  a ∧ b exists (meet / GLB) for all a, b
```

**Examples**:
- Subset lattice: (P(S), ⊆) with join = ∪, meet = ∩
- Divisor lattice: (divisors of n, |) with join = lcm, meet = gcd
- Concept hierarchy: Formal concept analysis

**Key problems**: Lattice completion, fixed point theorem (Tarski), concept lattice construction

---

## 7. Algorithms and Optimization

### 7.1 Integer Linear Program (ILP)

**Definition**: Optimize a linear objective subject to linear constraints with integer variables.

**Indicators**: "maximize", "minimize", "subject to", "optimal", "budget", "allocate", "best assignment"

**Template**:
```
Maximize/Minimize: c^T x
Subject to: Ax ≤ b
            x ∈ Z^n (or x ∈ {0,1}^n)
```

**Examples**:
- Knapsack: Maximize value subject to weight capacity
- Facility location: Minimize cost subject to coverage requirements
- Scheduling: Minimize makespan subject to precedence and resource constraints

**Key problems**: Knapsack, bin packing, facility location, vehicle routing, set cover

---

### 7.2 Search Space

**Definition**: An implicit graph of states and transitions, explored to find a goal state.

**Indicators**: "puzzle", "state", "moves", "reach the goal", "explore possibilities", "configuration"

**Template**:
```
States: S (possibly exponentially many)
Initial state: s0
Goal test: is_goal(s) -> bool
Transitions: next(s) -> set of states
Cost: c(s, s') (optional)
```

**Examples**:
- Puzzle: States = board configurations, transitions = legal moves
- Planning: States = world states, transitions = actions
- Game: States = positions, transitions = legal plays

**Key problems**: BFS, DFS, A*, state space reduction, symmetry breaking

---

### 7.3 Scheduling Model

**Definition**: Assign jobs to machines/times to optimize some objective (makespan, lateness, etc.).

**Indicators**: "schedule", "deadline", "processing time", "machines", "jobs", "makespan", "order of operations"

**Template**:
```
Jobs: J = {j1, ..., jn} with processing times p_i, deadlines d_i
Machines: M = {m1, ..., mk}
Assignment: σ: J → M × T (machine and start time)
Constraints: no overlap on same machine, precedence, deadlines
Objective: minimize makespan / total lateness / etc.
```

**Examples**:
- Factory: Schedule production jobs across machines
- Operating system: Schedule processes on CPUs
- Project management: Schedule tasks with dependencies (critical path)

**Key problems**: Job shop, flow shop, open shop, single machine scheduling, critical path method

---

## 8. Discrete Probability

### 8.1 Sample Space

**Definition**: Finite set Ω of outcomes with probability function P: Ω → [0,1] where Σ P(ω) = 1.

**Indicators**: "chance", "probability", "random", "likely", "odds", "fair", "biased"

**Template**:
```
Ω = {ω1, ..., ωn}
P(ωi) >= 0, Σ P(ωi) = 1
Event A ⊆ Ω, P(A) = Σ_{ω ∈ A} P(ω)
```

**Examples**:
- Dice: Ω = {1,2,3,4,5,6}, P(i) = 1/6
- Card draw: Ω = 52 cards, P(card) = 1/52
- A/B test: Ω = {convert, not_convert}, P(convert) = p

**Key problems**: Conditional probability, Bayes' theorem, independence, expected value

---

### 8.2 Random Variables (Discrete)

**Definition**: Function X: Ω → R mapping outcomes to numerical values.

**Indicators**: "expected value", "average outcome", "variance", "distribution", "how much on average"

**Template**:
```
X: Ω → R
E[X] = Σ x · P(X = x)
Var(X) = E[X^2] - (E[X])^2
```

**Examples**:
- Revenue: X = revenue from random customer
- Waiting time: X = number of trials until first success (geometric)
- Defects: X = number of defective items in batch (binomial)

**Key problems**: Expected value, variance, Markov/Chebyshev bounds, distribution fitting

---

## Cross-Domain Pattern Table

Quick lookup: match a real-world pattern to its primary discrete math structure.

| Real-World Pattern | Primary Structure | Classic Problem | Domain |
|---|---|---|---|
| Scheduling conflicts | Simple graph | Graph coloring | Graph Theory |
| Network routing | Weighted digraph | Shortest path | Graph Theory |
| Task assignment | Bipartite graph | Maximum matching | Graph Theory |
| Dependency ordering | DAG | Topological sort | Graph Theory |
| Hierarchical organization | Tree | Spanning tree | Graph Theory |
| Supply/demand flow | Weighted digraph | Max flow / min cut | Graph Theory |
| Resource allocation | ILP | Knapsack / bin packing | Optimization |
| Optimal selection under budget | ILP | 0/1 Knapsack | Optimization |
| Facility placement | ILP + Graph | Facility location | Optimization |
| Team formation | Set system | Set cover | Set Theory |
| Customer segmentation | Set partition | Clustering | Set Theory |
| Grouping/classification | Equivalence relation | Equivalence classes | Relations |
| Rule compliance checking | Predicate logic + CSP | SAT / model checking | Logic |
| Configuration validation | CSP | Constraint satisfaction | Logic |
| Obligation/permission modeling | Deontic logic | Norm consistency | Logic |
| Ranking with incomparables | Partial order | Linear extension | Relations |
| Counting arrangements | Permutation / Combination | Enumeration | Combinatorics |
| Fair division | Set partition | Balanced partition | Combinatorics |
| Round-robin tournament | Latin square | Tournament scheduling | Combinatorics |
| Sequencing with distance | Weighted graph | TSP | Graph Theory |
| Puzzle / state exploration | Search space | BFS / A* | Algorithms |
| Cyclic/periodic behavior | Modular arithmetic | CRT | Number Theory |
| Exact change problem | Diophantine equation | Coin change | Number Theory |
| Risk assessment | Sample space + RV | Expected value | Probability |
| Binary yes/no decisions | Boolean formula | SAT | Logic |
| Workflow pipeline | DAG | Critical path | Graph Theory |
| Stable pairing | Bipartite graph | Stable marriage | Graph Theory |
| Coverage / redundancy | Set system | Set cover / hitting set | Set Theory |
| Concept hierarchy | Lattice | Concept lattice | Relations |
| Multi-party interaction | Hypergraph | Hypergraph coloring | Graph Theory |
| Minimize cost / maximize return | Convex program | Convex optimization | Continuous Opt |
| Fit a model to data | Least squares | Regression / curve fitting | Continuous Opt |
| Balance risk and return | Quadratic program | Portfolio optimization | Continuous Opt |
| Find minimum of smooth function | Unconstrained optimization | Gradient descent | Continuous Opt |
| Smooth optimization with constraints | Constrained optimization | Interior point / SLSQP | Continuous Opt |
| Compare groups (before/after, A/B) | Hypothesis test | t-test / ANOVA | Statistical Inference |
| Predict outcome from variables | Regression model | Linear / logistic regression | Statistical Inference |
| Estimate parameter from data | MLE / Bayesian posterior | Confidence / credible interval | Statistical Inference |
| Check if data follows pattern | Distribution / GOF test | KS test / chi-squared GOF | Statistical Inference |
| Time-to-event with dropouts | Survival model | Kaplan-Meier / Cox PH | Statistical Inference |
| Update belief with new evidence | Bayesian model | Prior → posterior | Statistical Inference |
| Solve for unknowns | Linear system | Gaussian elimination | Linear Algebra |
| Transform data | Matrix / linear map | Matrix multiplication | Linear Algebra |
| Find dominant mode / stability | Eigenstructure | Eigenvalue problem | Linear Algebra |
| Reduce dimensions / compress | SVD / eigenstructure | SVD / PCA | Linear Algebra |
| Rate of change / slope | Function / curve | Differentiation | Calculus |
| Total / accumulated quantity | Integral | Integration | Calculus |
| Growth / decay over time | Differential equation | ODE solving | Calculus |
| Optimize smooth function | Function / curve | Lagrange multipliers | Calculus |
| Area of region / land | Polygon / planar region | Shoelace formula | Geometry |
| Volume / capacity | Polyhedron / 3D solid | Volume formulas | Geometry |
| Nearest / closest / farthest | Point set | Closest pair / Voronoi | Geometry |
| Triangle measurement | Triangle | Law of cosines / sines | Geometry |
| Investment comparison | Cash flow stream | NPV / IRR | Financial Math |
| Loan / mortgage payment | Cash flow stream | PMT / amortization | Financial Math |
| Savings / retirement planning | Cash flow stream | Compound interest / FV | Financial Math |
| Pricing / bidding competition | Strategic-form game | Nash equilibrium | Game Theory |
| Negotiate / bargain | Extensive-form game | Bargaining solution | Game Theory |
| Divide fairly / share costs | Cooperative game | Shapley value | Game Theory |
| Auction / procurement | Strategic-form game | Vickrey / VCG mechanism | Game Theory |
| Voting power analysis | Cooperative game | Shapley-Shubik index | Game Theory |
| Choose best option under risk | Decision tree | Expected value / EMV | Decision Analysis |
| Rank alternatives by criteria | Multi-criteria problem | AHP / TOPSIS | Decision Analysis |
| Risk tolerance / insurance | Utility function | Expected utility | Decision Analysis |
| Decide with no probabilities | Decision tree | Minimax regret | Decision Analysis |
| Balance cost vs. quality | Pareto set | Pareto frontier | Multi-Objective Opt |
| Meet multiple targets | Goal model | Goal programming | Multi-Objective Opt |
| Explore design trade-offs | Objective space | NSGA-II / MOEA/D | Multi-Objective Opt |

---

## 9. Continuous Optimization

### 9.1 Unconstrained Optimization

**Definition**: Minimize f(x) where x in R^n and f is a smooth (differentiable) function with no constraints.

**Indicators**: "minimize", "find the best", "optimal value", "no constraints", "smooth", "gradient"

**Template**:
```
min f(x)
x in R^n
Necessary condition: ∇f(x*) = 0
Sufficient condition: ∇²f(x*) positive definite
```

**Examples**:
- Curve fitting: Minimize sum of squared residuals
- Neural network training: Minimize loss function
- Maximum likelihood: Minimize negative log-likelihood

**Key problems**: Gradient descent, Newton's method, BFGS, conjugate gradient

---

### 9.2 Convex Program

**Definition**: Minimize a convex function over a convex set. Global minimum is guaranteed.

**Indicators**: "convex", "guaranteed optimal", "no local minima", "cone program", "semidefinite"

**Template**:
```
minimize    f(x)          -- convex objective
subject to  g_i(x) <= 0  -- convex inequality constraints
            Ax = b        -- affine equality constraints
```

**Examples**:
- Portfolio optimization: Minimize variance subject to target return
- Optimal control: Minimize quadratic cost subject to linear dynamics
- Signal reconstruction: Minimize L1 norm subject to measurements

**Key problems**: Linear programming (LP), quadratic programming (QP), second-order cone programming (SOCP), semidefinite programming (SDP)

---

### 9.3 Quadratic Program (QP)

**Definition**: Minimize a quadratic objective subject to linear constraints.

**Indicators**: "quadratic cost", "variance", "trade-off between two objectives", "regularization"

**Template**:
```
minimize    (1/2) x^T Q x + c^T x
subject to  Ax <= b
            x >= 0
```
where Q is positive semidefinite (for convexity).

**Examples**:
- Portfolio: Minimize variance (x^T Σ x) subject to target return (μ^T x >= r)
- Regression with regularization: Minimize ||Ax - b||^2 + λ||x||^2
- Optimal allocation: Quadratic cost with linear constraints

**Key problems**: Portfolio optimization, support vector machines, regularized regression

---

### 9.4 Least Squares

**Definition**: Minimize ||Ax - b||^2, the sum of squared residuals.

**Indicators**: "fit", "regression", "best line", "minimize error", "residuals", "data fitting"

**Template**:
```
minimize    ||Ax - b||_2^2
Solution:   x* = (A^T A)^{-1} A^T b  (normal equations)
```

**Examples**:
- Linear regression: Fit y = Xβ to data
- Calibration: Fit model parameters to measurements
- Signal processing: Estimate signal from noisy observations

**Key problems**: Linear regression, nonlinear least squares (Gauss-Newton), weighted least squares, total least squares

---

### 9.5 Nonlinear Constrained Optimization

**Definition**: Minimize a (possibly non-convex) function subject to nonlinear constraints.

**Indicators**: "nonlinear", "complex constraints", "engineering design", "may have local minima"

**Template**:
```
minimize    f(x)
subject to  g_i(x) <= 0   (inequality constraints)
            h_j(x) = 0    (equality constraints)
            x_L <= x <= x_U (bounds)
```

**Examples**:
- Engineering design: Minimize weight subject to stress constraints
- Chemical process: Maximize yield subject to thermodynamic constraints
- Trajectory optimization: Minimize fuel subject to dynamics

**Key problems**: KKT conditions, penalty methods, augmented Lagrangian, sequential quadratic programming (SQP)

---

## 10. Statistical Inference

### 10.1 Random Variable / Distribution

**Definition**: A random variable X: Ω → R mapping outcomes to numbers, with a distribution describing its probability behavior (PDF/PMF, CDF, parameters).

**Indicators**: "distribution", "random", "probability of", "what are the chances", "average", "expected", "variance", "spread"

**Template**:
```
X ~ Distribution(parameters)
E[X] = μ (mean/expected value)
Var(X) = σ² (variance)
P(X ∈ A) = ∫_A f(x)dx  or  Σ_{x∈A} p(x)
```

**Examples**:
- Customer wait times: X ~ Exponential(λ)
- Defect counts per batch: X ~ Poisson(μ)
- Test scores: X ~ Normal(μ, σ²)
- Conversion rates: X ~ Bernoulli(p)

**Key problems**: Distribution fitting (MLE), parameter estimation, goodness-of-fit testing, probability computation

---

### 10.2 Statistical Hypothesis

**Definition**: A formal statement about a population parameter, tested against data. H₀ (null) vs. H₁ (alternative), with a test statistic, rejection region, and significance level α.

**Indicators**: "is there a difference", "compare groups", "significant", "test whether", "does X affect Y", "A/B test"

**Template**:
```
H₀: θ = θ₀  (or μ₁ = μ₂, or p₁ = p₂)
H₁: θ ≠ θ₀  (two-sided) or θ > θ₀ (one-sided)
Test statistic: T = f(data)
Reject H₀ if |T| > t_critical  (equivalently, if p-value < α)
Report: test statistic, p-value, effect size, confidence interval
```

**Examples**:
- A/B test: "Does the new design increase conversions?" (H₀: p_A = p_B)
- Quality control: "Is the batch mean within spec?" (H₀: μ = μ₀)
- Clinical trial: "Does the drug lower blood pressure?" (H₀: μ_drug = μ_placebo)
- Survey: "Is satisfaction related to age group?" (H₀: independence)

**Key problems**: t-tests, chi-squared tests, ANOVA, Fisher's exact, Mann-Whitney, permutation tests

---

### 10.3 Regression Model

**Definition**: A model relating a response variable Y to one or more predictor variables X, with a functional form and error term: Y = f(X; β) + ε.

**Indicators**: "predict", "relationship between", "how does X affect Y", "model", "forecast", "explain variation", "factors influencing"

**Template**:
```
Y = β₀ + β₁X₁ + β₂X₂ + ... + βₚXₚ + ε
ε ~ N(0, σ²)  (OLS assumptions)
Estimate β by minimizing Σ(yᵢ - ŷᵢ)²
Report: β̂, SE(β̂), p-values, R², CI for β, residual diagnostics
```

**Examples**:
- Housing: Price = f(sqft, bedrooms, location, age)
- Sales: Revenue = f(ad_spend, season, price)
- Health: Blood pressure = f(age, weight, exercise, diet)
- Binary: P(churn) = sigmoid(β₀ + β₁·tenure + β₂·usage) (logistic)

**Key problems**: OLS, logistic regression, Ridge/Lasso, GLM, quantile regression, robust regression

---

### 10.4 Bayesian Model

**Definition**: A model that combines prior beliefs about parameters with observed data to produce a posterior distribution: P(θ|data) ∝ P(data|θ) × P(θ).

**Indicators**: "prior belief", "update with data", "posterior", "credible interval", "probability that parameter is", "what do we believe after seeing"

**Template**:
```
Prior:      π(θ)           -- what we believe before data
Likelihood: L(data|θ)      -- how data arises given θ
Posterior:  π(θ|data) ∝ L(data|θ) × π(θ)
Report: posterior mean/median, credible interval, P(θ > threshold)
```

**Examples**:
- A/B test: Beta(1,1) prior on conversion rate, updated with click data
- Reliability: Gamma prior on failure rate, updated with survival data
- Survey: Normal prior on population mean, updated with sample
- Drug efficacy: Prior from previous studies, updated with new trial

**Key problems**: Conjugate priors, MAP estimation, MCMC, variational inference, model comparison

---

### 10.5 Sample / Population

**Definition**: A population is the complete set of items of interest. A sample is a subset drawn from the population. Statistical inference generalizes from sample to population.

**Indicators**: "sample size", "how many do I need", "representative", "margin of error", "power", "generalize"

**Template**:
```
Population: N items with parameter θ (unknown)
Sample: n items drawn (randomly, independently)
Estimator: θ̂ = f(sample) estimates θ
SE(θ̂) decreases as O(1/√n) -- larger samples = more precision
Power = P(reject H₀ | H₁ true) -- increases with n and effect size
```

**Examples**:
- Survey design: "How many respondents to get ±3% margin?"
- A/B test: "How many users per variant to detect a 5% lift?"
- Clinical trial: "How many patients to have 80% power?"
- Quality inspection: "How many items to sample from the batch?"

**Key problems**: Sample size determination, power analysis, sampling design, margin of error calculation

---

### 10.6 Experimental Design

**Definition**: A structured plan for collecting data to test causal hypotheses, controlling for confounding variables through randomization, blocking, and replication.

**Indicators**: "experiment", "treatment", "control group", "randomize", "confound", "causal", "factorial", "blocking"

**Template**:
```
Units: N subjects/items
Treatments: k levels of factor(s)
Design: Completely randomized / Blocked / Factorial / Crossover
Assignment: Random allocation to treatment groups
Outcome: Y measured for each unit
Analysis: ANOVA / regression / Bayesian (depending on design)
```

**Examples**:
- A/B test: 2 treatments (old vs. new), random assignment, measure conversion
- Factorial: 2 × 3 design (drug dose × exercise level), measure blood pressure
- Blocked: Block by age group, randomize treatment within blocks
- Before/after: Same subjects measured pre and post intervention (paired design)

**Key problems**: Randomization, blocking, factorial design, sample size, power analysis, multiple comparisons

---

## 11. Linear Algebra

### 11.1 Matrix / Linear Map

**Definition**: An m×n matrix A represents a linear map from R^n to R^m. Encodes systems of linear equations, transformations, and relationships.

**Indicators**: "system of equations", "transform", "matrix", "linear relationship", "coefficients", "unknowns"

**Template**:
```
A ∈ R^{m×n}
Ax = b       -- system of linear equations
rank(A)      -- number of independent equations
ker(A)       -- solution space of Ax = 0
```

**Examples**:
- Traffic flow: Conservation equations at each intersection
- Input-output model: Industry production relationships (Leontief)
- Circuit analysis: Kirchhoff's laws as linear system

**Key problems**: Solve Ax = b, rank, null space, least squares, eigenvalues

---

### 11.2 Vector Space

**Definition**: A set V with addition and scalar multiplication satisfying closure, associativity, identity, inverse, distributivity. Dimension = number of basis vectors.

**Indicators**: "span", "basis", "dimension", "linear combination", "independent", "subspace"

**Template**:
```
V = span{v1, v2, ..., vk}
dim(V) = k if {v1, ..., vk} linearly independent
Projection of u onto V: proj_V(u) = A(A^T A)^{-1} A^T u
```

**Examples**:
- Signal space: Signals as vectors, Fourier components as basis
- Feature space: Data points as vectors in R^n
- Solution space: All solutions to a homogeneous system

**Key problems**: Basis finding, dimension, projection, orthogonalization (Gram-Schmidt)

---

### 11.3 Linear System

**Definition**: A set of m linear equations in n unknowns: Ax = b. May be consistent (has solutions) or inconsistent.

**Indicators**: "solve for", "find unknowns", "balance equations", "system of equations", "how much of each"

**Template**:
```
a₁₁x₁ + a₁₂x₂ + ... + a₁ₙxₙ = b₁
a₂₁x₁ + a₂₂x₂ + ... + a₂ₙxₙ = b₂
...
aₘ₁x₁ + aₘ₂x₂ + ... + aₘₙxₙ = bₘ

Unique solution iff rank(A) = rank([A|b]) = n
Infinite solutions iff rank(A) = rank([A|b]) < n
No solution iff rank(A) < rank([A|b])
```

**Examples**:
- Recipe blending: How much of each ingredient to achieve target nutrition
- Chemical balancing: Balance a chemical equation
- Economic equilibrium: Supply-demand intersection

**Key problems**: Gaussian elimination, LU factorization, condition number, least squares (if overdetermined)

---

### 11.4 Eigenstructure

**Definition**: For a square matrix A, eigenvalue λ and eigenvector v satisfy Av = λv. Reveals fundamental modes, stability, and decomposition.

**Indicators**: "dominant mode", "stability", "steady state", "principal component", "natural frequency", "growth rate"

**Template**:
```
Av = λv
det(A - λI) = 0           -- characteristic polynomial
Spectrum: {λ₁, λ₂, ..., λₙ}
A = PDP⁻¹                 -- diagonalization (if possible)
```

**Examples**:
- PageRank: Dominant eigenvector of link matrix
- Population dynamics: Growth rates as eigenvalues of Leslie matrix
- Vibration analysis: Natural frequencies from stiffness/mass eigenvalues
- PCA: Principal components as eigenvectors of covariance matrix

**Key problems**: Eigenvalue computation, spectral decomposition, SVD, stability analysis, power method

---

## 12. Calculus

### 12.1 Function / Curve

**Definition**: A rule f: D → R assigning each input x in domain D a unique output f(x). Curves are the graph {(x, f(x)) : x ∈ D}.

**Indicators**: "function", "formula", "equation", "rate of change", "slope", "tangent", "curve"

**Template**:
```
f: D ⊂ R^n → R^m
Derivative: f'(x) = lim_{h→0} [f(x+h) - f(x)] / h
Integral: ∫_a^b f(x) dx = F(b) - F(a) where F' = f
Critical points: f'(x) = 0
```

**Examples**:
- Revenue curve: R(q) = p(q) · q where p is demand function
- Growth model: f(t) = population at time t
- Cost function: C(x) = fixed + variable × x

**Key problems**: Differentiation, integration, optimization, root finding, Taylor approximation

---

### 12.2 Integral / Accumulated Quantity

**Definition**: The integral ∫_a^b f(x) dx represents accumulated total — area, work, probability, total change.

**Indicators**: "total", "accumulated", "area under", "over the interval", "how much altogether", "net change"

**Template**:
```
Total = ∫_a^b f(x) dx
Average value = (1/(b-a)) ∫_a^b f(x) dx
Arc length = ∫_a^b √(1 + [f'(x)]²) dx
```

**Examples**:
- Total revenue over time: ∫₀ᵀ r(t) dt
- Probability: P(a ≤ X ≤ b) = ∫_a^b f_X(x) dx
- Work done by force: W = ∫ F(x) dx
- Distance traveled: ∫₀ᵀ |v(t)| dt

**Key problems**: Definite integration (symbolic/numerical), improper integrals, double/triple integrals, line integrals

---

### 12.3 Differential Equation

**Definition**: An equation involving a function y(t) and its derivatives: F(t, y, y', y'', ...) = 0. Models how quantities change over time.

**Indicators**: "rate of change", "growth", "decay", "over time", "dynamics", "evolves", "approaches equilibrium"

**Template**:
```
ODE: dy/dt = f(t, y),  y(t₀) = y₀
Linear ODE: y' + p(t)y = q(t)
System: dy/dt = Ay + g(t)  (matrix form)
Equilibria: f(t, y*) = 0
Stability: eigenvalues of Jacobian at y*
```

**Examples**:
- Population: dP/dt = rP(1 - P/K) (logistic growth)
- Radioactive decay: dN/dt = -λN
- Epidemiology: SIR model (S'=-βSI, I'=βSI-γI, R'=γI)
- Drug concentration: dC/dt = -kC (first-order elimination)

**Key problems**: Analytical solution (separation, integrating factor), numerical solution (Euler, RK4), stability analysis, phase portrait

---

## 13. Geometry & Trigonometry

### 13.1 Polygon / Planar Region

**Definition**: A closed plane figure bounded by straight line segments (polygon) or curves. Characterized by vertices, edges, area, perimeter, centroid.

**Indicators**: "area", "perimeter", "shape", "region", "boundary", "lot", "floor plan", "land"

**Template**:
```
Polygon: P = {v₁, v₂, ..., vₙ} (ordered vertices)
Area (shoelace): A = (1/2)|Σᵢ(xᵢyᵢ₊₁ - xᵢ₊₁yᵢ)|
Perimeter: L = Σᵢ |vᵢ₊₁ - vᵢ|
Centroid: C = (1/n)Σᵢ vᵢ  (for vertices; weighted for area)
```

**Examples**:
- Land parcel: Compute area from surveyor coordinates
- Floor plan: Total area, room layout
- Coverage zone: Service area of a facility

**Key problems**: Area computation, point-in-polygon test, convexity check, polygon intersection/union

---

### 13.2 Polyhedron / 3D Solid

**Definition**: A 3D solid bounded by flat faces (polyhedron) or curved surfaces. Characterized by volume, surface area, vertices, edges, faces.

**Indicators**: "volume", "capacity", "surface area", "3D", "solid", "container", "tank"

**Template**:
```
Common formulas:
  Box:      V = lwh,           SA = 2(lw + lh + wh)
  Cylinder: V = πr²h,          SA = 2πr² + 2πrh
  Sphere:   V = (4/3)πr³,      SA = 4πr²
  Cone:     V = (1/3)πr²h,     SA = πr² + πrl
  Solid of revolution: V = π∫ₐᵇ [f(x)]² dx
```

**Examples**:
- Tank capacity: Volume of cylindrical or spherical tank
- Packaging: Surface area for material cost, volume for contents
- Construction: Concrete volume for foundations

**Key problems**: Volume/surface area computation, optimization (maximize volume for given surface area)

---

### 13.3 Point Set / Spatial Configuration

**Definition**: A collection of points in R^d. Properties include distances, nearest neighbors, convex hull, clustering, Voronoi partition.

**Indicators**: "points", "locations", "closest", "farthest", "spread", "cluster", "nearest", "spatial"

**Template**:
```
S = {p₁, p₂, ..., pₙ} ⊂ R^d
Distance: d(pᵢ, pⱼ) = ||pᵢ - pⱼ||
Convex hull: smallest convex set containing S
Voronoi: partition into nearest-point regions
```

**Examples**:
- Store locations: Find optimal placement minimizing customer travel
- GPS points: Compute bounding region, nearest neighbor
- Sensor network: Coverage area via Voronoi diagram

**Key problems**: Convex hull, Voronoi diagram, Delaunay triangulation, closest pair, k-nearest neighbors

---

### 13.4 Triangle

**Definition**: A 3-sided polygon defined by 3 vertices, 3 sides, and 3 angles. The fundamental unit of geometry — any polygon can be triangulated.

**Indicators**: "triangle", "angle", "side", "height", "distance between three points", "surveying"

**Template**:
```
Triangle ABC with sides a, b, c opposite angles A, B, C
Law of cosines: c² = a² + b² - 2ab cos(C)
Law of sines:   a/sin(A) = b/sin(B) = c/sin(C)
Area: (1/2)ab sin(C) = √[s(s-a)(s-b)(s-c)]  (Heron's)
  where s = (a+b+c)/2
```

**Examples**:
- Surveying: Distance across a river using angle measurements
- Navigation: Triangulation to determine position
- Construction: Roof pitch, rafter lengths

**Key problems**: Triangle solving (SSS, SAS, ASA, AAS, SSA), area, circumscribed/inscribed circles

---

## 14. Financial Mathematics

### 14.1 Cash Flow Stream

**Definition**: A time-indexed sequence of monetary inflows (+) and outflows (−). The foundation of all financial valuation.

**Indicators**: "investment", "loan", "mortgage", "payment", "return", "interest", "present value", "future value", "annuity"

**Template**:
```
Cash flows: CF = {C₀, C₁, C₂, ..., Cₙ} at times {0, 1, 2, ..., n}
Discount rate: r (per period)
NPV = Σₜ Cₜ / (1+r)^t
IRR: rate r* such that NPV(r*) = 0
PMT (annuity): C = PV · r / (1 - (1+r)^{-n})
FV = PV · (1+r)^n
```

**Examples**:
- Mortgage: PV = loan amount, C = monthly payment, r = monthly rate
- Investment: C₀ = -initial cost, C₁..Cₙ = annual returns
- Savings: Regular deposits growing at compound interest
- Refinancing: Compare NPV of old vs. new loan cash flows

**Key problems**: NPV, IRR, PMT, amortization, compound interest, annuity valuation, break-even period

---

## 15. Game Theory

### 15.1 Strategic-Form (Normal-Form) Game

**Definition**: A simultaneous-move game defined by: N players, action sets A_1, ..., A_N, and payoff functions u_i: A_1 × ... × A_N → R for each player.

**Indicators**: "compete", "pricing war", "negotiate", "strategic interaction", "players choose simultaneously", "payoff matrix", "best response"

**Template**:
```
Players: {1, 2, ..., N}
Actions: A_i for each player i
Payoffs: u_i(a_1, ..., a_N) for each player i
Nash equilibrium: no player can unilaterally improve
  u_i(a_i*, a_{-i}*) ≥ u_i(a_i, a_{-i}*) for all a_i in A_i
```

**Examples**:
- Pricing competition: two firms set prices simultaneously
- Market entry: firms decide whether to enter a market
- Resource sharing: players choose how much to contribute to public good
- Bidding strategy: bidders choose bids in a sealed-bid auction

**Key problems**: Nash equilibrium, dominant strategies, mixed strategies, minimax (zero-sum)

---

### 15.2 Extensive-Form Game

**Definition**: A sequential game represented as a game tree: nodes (decision points), edges (actions), information sets (what a player knows), and terminal payoffs.

**Indicators**: "sequential", "moves first", "observes", "game tree", "bluff", "perfect/imperfect information", "backward induction"

**Template**:
```
Game tree: T = (V, E) with root
Players: assigned to decision nodes
Information sets: partition of each player's nodes
Actions: edges from each node
Payoffs: at terminal nodes
Solve by backward induction (perfect info) or sequential equilibrium (imperfect info)
```

**Examples**:
- Ultimatum game: proposer offers split, responder accepts or rejects
- Stackelberg competition: leader commits to quantity, follower responds
- Negotiation rounds: alternating offers over multiple rounds
- Entry deterrence: incumbent threatens, entrant decides

**Key problems**: Subgame-perfect equilibrium, backward induction, commitment strategies

---

### 15.3 Coalition / Cooperative Game

**Definition**: A game where players can form binding coalitions. Defined by a set N of players and a characteristic function v: 2^N → R mapping each coalition to its worth.

**Indicators**: "coalition", "alliance", "cooperate", "share costs", "divide profits", "voting power", "fair allocation"

**Template**:
```
Players: N = {1, 2, ..., n}
Characteristic function: v(S) for each coalition S ⊆ N
Core: allocations (x_1, ..., x_n) with Σx_i = v(N) and Σ_{i∈S} x_i ≥ v(S) for all S
Shapley value: φ_i = Σ_S [|S|!(n-|S|-1)!/n!] [v(S∪{i}) - v(S)]
```

**Examples**:
- Airport landing fees: airlines share runway costs by coalition value
- Joint venture: partners allocate profit based on contributions
- Voting power: Shapley-Shubik index for weighted voting systems
- Cost sharing: municipalities share infrastructure costs

**Key problems**: Shapley value, nucleolus, core, fair division

---

## 16. Decision Analysis

### 16.1 Decision Tree / Influence Diagram

**Definition**: A graphical model of sequential decisions under uncertainty. Decision nodes (squares), chance nodes (circles), and value nodes (diamonds) connected by arcs showing information flow.

**Indicators**: "decide", "then observe", "if...then", "risk", "uncertainty", "what should I do", "sequential choice", "stages"

**Template**:
```
Decision tree:
  Decision node → action edges → chance nodes → outcome edges → payoffs
  Solve by backward induction (fold back):
    At chance nodes: E[V] = Σ p_i · V_i
    At decision nodes: V* = max_a E[V | action a]
Value of information: VOI = E[V | with info] - E[V | without info]
```

**Examples**:
- R&D investment: invest → test result (success/fail) → commercialize or abandon
- Medical treatment: test → diagnosis → treatment choice → outcome
- Litigation: settle now vs. go to trial (win/lose) with discovery stages
- Market entry: enter → demand (high/low) → expand or contract

**Key problems**: Expected value, decision tree evaluation, value of perfect information, value of imperfect information

---

### 16.2 Preference Model / Utility Function

**Definition**: A function u: X → R representing a decision-maker's preferences over outcomes, possibly under risk. Captures risk attitude (risk-averse: concave, risk-neutral: linear, risk-seeking: convex).

**Indicators**: "prefer", "risk averse", "risk tolerance", "utility", "certainty equivalent", "indifferent between"

**Template**:
```
Utility function: u(x) (monotonic)
Risk aversion: u concave → risk-averse (Jensen's inequality: u(E[X]) > E[u(X)])
Certainty equivalent: CE where u(CE) = E[u(X)]
Risk premium: RP = E[X] - CE
Common forms:
  CRRA: u(x) = x^(1-γ) / (1-γ) (constant relative risk aversion)
  CARA: u(x) = -e^(-αx) (constant absolute risk aversion)
```

**Examples**:
- Insurance pricing: willingness to pay above expected loss
- Investment choice: selecting between risky and safe assets
- Salary negotiation: guaranteed vs. variable compensation
- Medical decision: certain outcome vs. risky treatment

**Key problems**: Expected utility, certainty equivalent, risk premium, utility elicitation

---

### 16.3 Multi-Criteria Problem

**Definition**: A decision with multiple competing objectives evaluated across several criteria, where alternatives are ranked by aggregating scores.

**Indicators**: "trade-off", "rank", "compare options", "criteria", "weighted score", "best overall", "vendor selection"

**Template**:
```
Alternatives: A = {a_1, ..., a_m}
Criteria: C = {c_1, ..., c_n} with weights w = (w_1, ..., w_n), Σw_i = 1
Performance matrix: P[i,j] = score of alternative i on criterion j
Aggregation: TOPSIS, AHP, ELECTRE, weighted sum, or MAUT
Result: ranking or outranking relation
```

**Examples**:
- Vendor selection: evaluate suppliers on cost, quality, delivery, service
- Site selection: compare locations on cost, access, labor, zoning
- Technology evaluation: compare platforms on features, cost, scalability, support
- Apartment ranking: compare units on rent, commute, size, amenities

**Key problems**: AHP, TOPSIS, ELECTRE, MAUT, sensitivity analysis

---

## 17. Multi-Objective Optimization

### 17.1 Pareto Set / Efficient Frontier

**Definition**: The set of all feasible solutions where no objective can be improved without worsening another. Also called the Pareto front or efficient frontier.

**Indicators**: "trade-off", "multiple objectives", "balance", "Pareto", "efficient frontier", "no solution dominates all"

**Template**:
```
Objectives: f_1(x), ..., f_k(x) (all minimized without loss of generality)
Pareto dominance: x dominates y iff f_i(x) ≤ f_i(y) for all i and f_j(x) < f_j(y) for some j
Pareto front: {x : no feasible y dominates x}
Trade-off rate: df_i/df_j along the Pareto front (marginal rate of substitution)
```

**Examples**:
- Cost vs. quality: cheaper products sacrifice quality
- Risk vs. return: efficient frontier in portfolio optimization
- Speed vs. fuel: faster delivery uses more fuel
- Accuracy vs. interpretability: complex models are harder to explain

**Key problems**: Pareto frontier enumeration, scalarization, NSGA-II

---

### 17.2 Objective Space

**Definition**: The image of the feasible set under the objective functions. Each feasible solution x maps to a point (f_1(x), ..., f_k(x)) in R^k.

**Indicators**: "objective values", "feasible region in objective space", "attainable set", "utopia point"

**Template**:
```
Objective space: Y = {(f_1(x), ..., f_k(x)) : x ∈ X}
Utopia point: y* = (min f_1, ..., min f_k) — ideal but usually infeasible
Nadir point: worst values on Pareto front per objective
Mapping: decision space X → objective space Y via f
```

**Examples**:
- Scatter plot of cost vs. quality for all design alternatives
- Risk-return plot in portfolio optimization
- Performance-price plot for product comparison
- Emissions-cost plot for energy policy alternatives

**Key problems**: Reference point method, achievement scalarizing, utopia/nadir estimation

---

### 17.3 Goal / Aspiration Model

**Definition**: A multi-objective model where the decision-maker specifies target levels (goals) for each objective, and the solver minimizes deviations from these goals.

**Indicators**: "target", "aspiration", "goal", "at least X for objective 1 and at most Y for objective 2", "satisfice"

**Template**:
```
Goals: g_1, ..., g_k (target level for each objective)
Deviations: d_i^+ (over-achievement), d_i^- (under-achievement)
f_i(x) - d_i^+ + d_i^- = g_i for all i
Minimize: Σ w_i · (d_i^+ + d_i^-) or lexicographic over priority levels
```

**Examples**:
- Budget planning: meet profit target, don't exceed spending
- Manufacturing: meet production target, minimize defects, don't exceed overtime
- Urban planning: house enough residents, maintain green space, limit costs
- Scheduling: meet deadlines, balance workload, minimize overtime

**Key problems**: Goal programming, lexicographic optimization, satisficing

---

## Cross-Reference Index

Where to go next after identifying a structure.

| Structure Section | Algorithms (algorithms.md) | Solvers (solvers.md) | Interpretation (interpretation-patterns.md) |
|---|---|---|---|
| 1. Graph Theory | §1 Traversal (A1-A7), §2 Shortest Path (A8-A12), §3 MST (A13-A14), §4 Matching (A15-A18), §5 Flow (A19-A20), §6 Coloring (A21-A22), §7 Ind. Set/Cover/Clique (A23-A25), §8 Euler/Hamilton (A26-A27), §9 TSP (A28-A30) | §1 NetworkX, §5 SciPy | §1 Graph Theory Solutions |
| 2. Combinatorics | §15 Counting & Generation (A63-A69) | §7 itertools, §4 SymPy | §4 Counting Results |
| 3. Set Theory | §12 Greedy (A47 Set Cover), §10 Optimization (A32 ILP) | §2 PuLP | §2.2 Knapsack/Selection |
| 4. Logic | §13 SAT/SMT/CSP (A48-A52) | §3 Z3, §6 OR-Tools | §3 Proof Results |
| 5. Number Theory | §14 Number Theory (A53-A62) | §4 SymPy | §6 Number Theory Results |
| 6. Relations & Orders | §16 Order Theory (A70-A73), §1 Traversal (A3 Topo Sort) | §1 NetworkX, §4 SymPy | -- |
| 7. Algorithms & Optimization | §10 LP/ILP (A31-A34) | §2 PuLP, §5 SciPy, §6 OR-Tools | §2 Optimization Solutions |
| 8. Discrete Probability | §18 Probability (A78-A81) | §8 numpy, §4 SymPy | §5 Probability Results |
| 9. Continuous Optimization | §21 Continuous Opt (A87-A94) | §9 cvxpy, §5 SciPy | §7 Continuous Opt Solutions |
| 10. Statistical Inference | algorithms-statistics.md S1-S45 | solvers-statistics.md (scipy.stats, statsmodels, PyMC, pingouin, lifelines) | §8 Statistical Inference Solutions |
| 11. Linear Algebra | §22 Linear Algebra (A95-A106) | numpy.linalg, scipy.linalg | §9 Linear Algebra Results |
| 12. Calculus | §23 Calculus (A107-A116) | §4 SymPy, §5 SciPy | §10 Calculus Results |
| 13. Geometry & Trigonometry | §24 Geometry & Trig (A117-A126) | shapely, scipy.spatial | §11 Geometry Results |
| 14. Financial Mathematics | §25 Financial Math (A127-A134) | numpy-financial | §12 Financial Results |
| 15. Game Theory | §26 Game Theory (A135-A146) | §13 nashpy | §13 Game Theory Results |
| 16. Decision Analysis | §27 Decision Analysis (A147-A156) | numpy, scipy, §2 PuLP | §14 Decision Analysis Results |
| 17. Multi-Objective Optimization | §28 Multi-Objective Opt (A157-A164) | §14 pymoo, §2 PuLP, §5 SciPy | §15 Multi-Objective Results |

Also see: **problem-classification.md** for rapid pattern matching from natural language to structure, **common-mistakes.md** for modeling pitfalls by structure type.
