# Mathematical Structure Catalog

**Scope**: Discrete Mathematics (32 structures), Continuous Optimization (5 structures), Statistical Inference (6 structures), Linear Algebra (4 structures), Calculus (3 structures), Geometry & Trigonometry (4 structures), Financial Mathematics (1 structure), Game Theory (3 structures), Decision Analysis (3 structures), Multi-Objective Optimization (3 structures), Time Series (3 structures), Stochastic Processes (3 structures), Machine Learning (5 structures), Simulation & ODEs (8 structures), Numerical Methods (3 structures), Causal Inference (2 structures), Extended OR (3 structures), Abstract Algebra & Representation Theory (4 structures), Algebraic Combinatorics (3 structures), Stochastic Analysis & SPDEs (3 structures), Algebraic Topology (3 structures), Symplectic & Differential Geometry (3 structures), Advanced Spectral Theory (3 structures), Tensor Analysis (3 structures), RKHS & Krylov Methods (2 structures)

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

## 18. Time Series

### 18.1 Time Series / Temporal Sequence

**Definition**: An ordered sequence of observations indexed by time, where the ordering carries information (autocorrelation, trend, seasonality).

**Indicators**: "over time", "monthly data", "daily values", "trend", "forecast", "seasonal pattern", "time-stamped", "historical data"

**Template**:
```
Observations: y_1, y_2, ..., y_n at times t_1 < t_2 < ... < t_n
Components: y_t = T_t + S_t + R_t (additive) or y_t = T_t × S_t × R_t (multiplicative)
  where T = trend, S = seasonal, R = residual
Goal: forecast y_{n+1}, ..., y_{n+h} or decompose into components
```

**Examples**:
- Monthly sales figures over 3 years
- Daily website traffic with weekly and yearly patterns
- Quarterly GDP growth rates
- Hourly temperature readings

**Key problems**: ARIMA (S46-S47), exponential smoothing (S48), decomposition (S49), Prophet (S55)

---

### 18.2 Seasonal / Cyclical Pattern

**Definition**: A regular, repeating pattern in a time series with a known period (seasonal) or unknown period (cyclical).

**Indicators**: "seasonal", "monthly pattern", "weekly cycle", "holiday effect", "periodic", "same time every year"

**Template**:
```
Period: s (12 for monthly, 7 for daily-weekly, 4 for quarterly)
Seasonal component: S_t = S_{t+s} (repeating with period s)
Seasonal strength: 1 - Var(R) / Var(S + R)
```

**Examples**:
- Ice cream sales peaking in summer (s=12)
- Restaurant traffic peaking on weekends (s=7)
- Retail spending spiking in December (s=12)
- Energy usage higher in winter/summer (s=12)

**Key problems**: SARIMA (S47), Holt-Winters (S48), STL decomposition (S49), spectral analysis (S59)

---

### 18.3 Trend Component

**Definition**: The long-term direction of a time series (increasing, decreasing, or level), after removing seasonal and irregular effects.

**Indicators**: "growing over time", "declining trend", "upward trajectory", "long-term pattern", "year-over-year growth"

**Template**:
```
Trend models:
  Linear: T_t = a + b·t
  Exponential: T_t = a · e^{bt}
  Piecewise linear: T_t = a_i + b_i·t for t in segment i (changepoints)
Stationarity: after removing trend, residuals should be stationary (ADF test)
```

**Examples**:
- Population growth (exponential trend)
- Technology adoption (S-curve / logistic trend)
- Declining manufacturing costs (linear decreasing)
- Stock market long-term growth (stochastic trend / random walk)

**Key problems**: Stationarity tests (S51), change point detection (S56), random walk analysis (S64)

---

## 19. Stochastic Processes

### 19.1 Continuous-Time Markov Chain

**Definition**: A stochastic process on a discrete state space where transitions occur at exponentially distributed random times, with the memoryless property.

**Indicators**: "states", "transition rates", "exponential waiting time", "steady state", "long-run probability", "queue", "up/down system"

**Template**:
```
State space: {0, 1, ..., k}
Generator matrix Q: q_ij = rate from state i to j (i≠j), q_ii = -Σ_{j≠i} q_ij
Transient: P(t) = exp(Qt)
Steady-state: π Q = 0, Σ π_i = 1
```

**Examples**:
- M/M/1 queue (customer arrivals and departures)
- Machine reliability (working/failed states with repair)
- Chemical reaction networks
- Call center staffing models

**Key problems**: CTMC analysis (S61), birth-death process (S62)

---

### 19.2 Point Process

**Definition**: A random process whose realizations are collections of points (events) in time or space.

**Indicators**: "events over time", "arrival times", "count of occurrences", "rate of events", "inter-arrival times"

**Template**:
```
Events: {t_1, t_2, ...} in [0, T]
Rate function: λ(t) (intensity / hazard)
Count: N(s,t) = number of events in (s,t]
Inter-arrivals: X_i = t_i - t_{i-1}
Homogeneous Poisson: X_i ~ Exp(λ), N(0,t) ~ Poisson(λt)
```

**Examples**:
- Customer arrivals at a store
- Earthquakes in a region
- Server request arrivals
- Insurance claims over time

**Key problems**: Poisson process (S63), renewal process (S65)

---

### 19.3 Random Walk / Diffusion

**Definition**: A stochastic process where changes are independent and identically distributed, producing an unpredictable trajectory.

**Indicators**: "random", "unpredictable", "unit root", "stock price", "efficient market", "Brownian motion"

**Template**:
```
Discrete: X_t = X_{t-1} + ε_t, where ε_t ~ iid(0, σ²)
With drift: X_t = μ + X_{t-1} + ε_t
Variance grows: Var(X_t) = σ²·t (non-stationary)
Test: ADF unit root test (S51), variance ratio test (S64)
```

**Examples**:
- Stock prices (geometric random walk)
- Exchange rates under efficient market hypothesis
- Particle diffusion (Brownian motion)
- Random search / foraging paths

**Key problems**: Random walk analysis (S64), stationarity tests (S51), GARCH for volatility (S54)

---

## 20. Machine Learning

### 20.1 Classification Model

**Definition**: A function f: X → {c₁, ..., cₖ} that maps feature vectors to discrete class labels, learned from labeled training examples.

**Indicators**: "classify", "predict category", "which type", "spam or not", "diagnose", "detect fraud", "churn prediction", "sentiment", "label"

**Template**:
```
Features: X = (x₁, x₂, ..., xₚ) ∈ ℝᵖ
Labels: y ∈ {c₁, c₂, ..., cₖ}
Training set: {(Xᵢ, yᵢ)}ᵢ₌₁ⁿ
Model: f̂(X) = argmax_c P(Y=c | X)
Evaluation: accuracy, precision, recall, F1, ROC-AUC
```

**Examples**:
- Email spam detection: X = word frequencies, y ∈ {spam, ham}
- Medical diagnosis: X = symptoms/tests, y ∈ {disease, healthy}
- Customer churn: X = usage metrics, y ∈ {churn, retain}
- Image recognition: X = pixel values, y ∈ {cat, dog, bird, ...}

**Key problems**: k-NN (S69), Decision Tree (S70), Random Forest (S71), SVM (S72), Naive Bayes (S73), Gradient Boosting (S74), MLP (S75)

---

### 20.2 Regression Model (ML)

**Definition**: A function f: X → ℝ that maps feature vectors to continuous values, optimizing a loss function (MSE, MAE) on training data.

**Indicators**: "predict value", "estimate amount", "how much", "forecast price", "expected revenue", "regression"

**Template**:
```
Features: X = (x₁, x₂, ..., xₚ) ∈ ℝᵖ
Target: y ∈ ℝ
Training set: {(Xᵢ, yᵢ)}ᵢ₌₁ⁿ
Model: f̂(X) minimizing Σ L(yᵢ, f̂(Xᵢ))
Evaluation: R², RMSE, MAE, cross-validated score
```

**Examples**:
- House price prediction: X = bedrooms, sqft, location; y = price
- Salary estimation: X = experience, education, role; y = salary
- Energy consumption: X = temperature, time, occupancy; y = kWh

**Key problems**: RF Regressor (S76), Gradient Boosting Regressor (S77), also Ridge/Lasso (S27)

---

### 20.3 Cluster Structure

**Definition**: A partition of data points into groups where within-group similarity is high and between-group similarity is low, without labeled training data.

**Indicators**: "group", "segment", "cluster", "find patterns", "types of customers", "natural groupings", "unsupervised", "similar items"

**Template**:
```
Data: {X₁, X₂, ..., Xₙ} ⊂ ℝᵖ (no labels)
Partition: C = {C₁, C₂, ..., Cₖ} where ∪Cⱼ = {1,...,n}
Objective: maximize intra-cluster similarity, minimize inter-cluster similarity
Evaluation: silhouette score, inertia, Calinski-Harabasz, domain interpretation
```

**Examples**:
- Customer segmentation: group customers by purchasing behavior
- Document clustering: group articles by topic similarity
- Gene expression: identify co-expressed gene groups
- Market segmentation: identify distinct market segments

**Key problems**: K-Means (S78), DBSCAN (S79), Hierarchical (S80), GMM (S81), Spectral (S82)

---

### 20.4 Low-Dimensional Embedding

**Definition**: A mapping f: ℝᵖ → ℝᵈ (d ≪ p) that preserves relevant structure (variance, neighborhoods, topology) while reducing dimensionality.

**Indicators**: "visualize", "reduce dimensions", "too many features", "project", "embed", "latent space", "compress features"

**Template**:
```
High-dimensional data: X ∈ ℝⁿˣᵖ
Embedding: Z = f(X) ∈ ℝⁿˣᵈ, d ≪ p
Preservation: structure-dependent (variance for PCA, neighborhoods for t-SNE/UMAP)
Evaluation: explained variance, reconstruction error, visual cluster separation
```

**Examples**:
- Visualize word embeddings in 2D (300-D → 2-D)
- Reduce survey responses to latent factors
- Compress image features before classification
- Explore single-cell RNA-seq data

**Key problems**: PCA (S83), t-SNE (S84), UMAP (S85), Factor Analysis (S86)

---

### 20.5 ML Pipeline / Feature Space

**Definition**: An ordered sequence of data transformations (imputation, scaling, encoding, selection) followed by a learning algorithm, forming a reproducible end-to-end workflow.

**Indicators**: "preprocess", "clean data", "encode categories", "scale features", "missing values", "pipeline", "production model", "deploy"

**Template**:
```
Raw data: X_raw (mixed types, missing values, varying scales)
Transforms: T₁ → T₂ → ... → Tₖ → Model
Pipeline: fit(X_train, y_train), predict(X_new)
Prevents: data leakage (transforms fitted only on training fold)
```

**Examples**:
- ETL + model pipeline for production deployment
- Cross-validated pipeline with preprocessing
- Mixed numeric/categorical feature handling

**Key problems**: Pipeline Construction (S90), Feature Selection (S87), Hyperparameter Tuning (S88)

---

## 21. Simulation & ODEs

### 21.1 ODE / Dynamical System

**Definition**: A system of first-order ordinary differential equations dy/dt = f(t, y) with initial conditions y(t₀) = y₀.

**Indicators**: "rate of change," "growth/decay over time," "population dynamics," "differential equation," "trajectory," "equilibrium point," "stability"

**Template**:
```
State variables: y₁(t), y₂(t), ...
dy₁/dt = f₁(t, y₁, y₂, ...)
dy₂/dt = f₂(t, y₁, y₂, ...)
Initial conditions: y(0) = y₀
Time domain: t ∈ [0, T]
```

**Examples**: SIR epidemic model (dS/dt = -βSI, dI/dt = βSI - γI, dR/dt = γI), predator-prey (Lotka-Volterra), radioactive decay, pharmacokinetics, chemical reactions, mechanical oscillations

**Key problems**: Euler Method (A165), RK4 (A166), Stiff ODE (A167), Phase Portrait (A168), Equilibrium & Stability (A169), Bifurcation (A170), Parameter Estimation (A171), SIR/SEIR (A173), Lotka-Volterra (A174)

---

### 21.2 Queuing System

**Definition**: An arrival process, service mechanism, and queue discipline describing entities waiting for and receiving service. Characterized by Kendall notation A/S/c/K/N/D.

**Indicators**: "waiting time," "queue length," "service rate," "arrival rate," "throughput," "utilization," "customers in system," "how many servers needed"

**Template**:
```
Kendall notation: A/S/c  (arrivals/service/servers)
Arrival rate: λ (customers/unit time)
Service rate: μ (customers/unit time per server)
Servers: c
Capacity: K (finite or ∞)
Discipline: FIFO, priority, etc.
Performance measures: Lq (queue length), Wq (wait time), ρ (utilization)
```

**Examples**: Call center staffing, hospital ER wait times, checkout lanes, network packet buffering, restaurant seating, manufacturing bottlenecks, tech support ticketing

**Key problems**: M/M/1 (S96), M/M/c (S97), M/G/1 (S98), Little's Law (S99), Jackson Network (S100)

---

### 21.3 Simulation Model

**Definition**: A stochastic model where system behavior is observed by generating random samples and tracking state evolution over time, rather than by closed-form analysis.

**Indicators**: "simulate," "what-if scenarios," "Monte Carlo," "uncertainty propagation," "risk analysis," "probability of outcome," "random events," "run many trials"

**Template**:
```
Type: Monte Carlo / Discrete-Event / Agent-Based
Random inputs: X₁ ~ Dist₁(params), X₂ ~ Dist₂(params), ...
System logic: f(X₁, X₂, ...) → output metric
Number of replications: N
Output: E[metric], Var[metric], P(metric > threshold), CI
```

**Examples**: Financial risk (VaR), project completion time, insurance loss estimation, reliability analysis, option pricing, clinical trial simulation, supply chain disruption

**Key problems**: Monte Carlo Integration (S91), Risk Simulation (S92), Importance Sampling (S93), Variance Reduction (S94), Scenario Generation (S95)

---

### 21.4 Discrete-Event System

**Definition**: A system where state changes occur at discrete points in time driven by events, with resources that are acquired, held, and released by entities.

**Indicators**: "process flow," "resource contention," "entities and resources," "discrete events," "factory simulation," "service process," "batch processing"

**Template**:
```
Entities: customers, jobs, packets, ...
Resources: servers, machines, beds, ...
Events: arrive, start_service, finish_service, ...
Queue discipline: FIFO, priority, shortest-job-first
Random durations: inter-arrival ~ Exp(λ), service ~ Dist(params)
Metrics: throughput, utilization, wait time, queue length
Warm-up period: discard initial transient
Run length: N events or T time units × R replications
```

**Examples**: Manufacturing line simulation, hospital patient flow, airport security screening, call center operations, warehouse order processing

**Key problems**: Event-Driven Simulation Engine (S101), Resource Allocation Simulation (S102), Warm-Up Period Detection (S103)

---

### 21.5 Epidemic / Compartmental Model

**Definition**: A population partitioned into compartments (Susceptible, Infected, Recovered, etc.) with transition rates between compartments governed by ODEs.

**Indicators**: "disease spread," "epidemic," "infection rate," "basic reproduction number," "herd immunity," "SIR," "SEIR," "outbreak"

**Template**:
```
Compartments: S, I, R (or S, E, I, R, etc.)
Population: N = S + I + R
Transmission rate: β (contact rate × transmission probability)
Recovery rate: γ (1 / infectious period)
R₀ = β/γ (basic reproduction number)
dS/dt = -βSI/N
dI/dt = βSI/N - γI
dR/dt = γI
Initial conditions: S(0), I(0), R(0)
```

**Examples**: COVID-19 modeling, flu season forecasting, vaccination strategy optimization, disease eradication threshold

**Key problems**: SIR/SEIR Epidemic Model (A173), ODE solvers (A165-A167), Parameter Estimation (A171)

---

### 21.6 Predator-Prey / Population System

**Definition**: A system of coupled ODEs modeling interacting populations with competition, predation, or cooperation dynamics.

**Indicators**: "predator and prey," "population cycles," "ecological equilibrium," "species interaction," "carrying capacity," "Lotka-Volterra"

**Template**:
```
Populations: x(t) (prey), y(t) (predator)
dx/dt = αx - βxy       (prey growth minus predation)
dy/dt = δxy - γy        (predator growth from predation minus death)
Parameters: α (prey growth), β (predation), γ (predator death), δ (conversion efficiency)
Initial conditions: x(0), y(0)
```

**Examples**: Wolf-deer ecosystems, fish-plankton dynamics, pest-predator biocontrol, competitive market dynamics (analogy)

**Key problems**: Lotka-Volterra (A174), Phase Portrait (A168), Equilibrium & Stability (A169)

---

### 21.7 Birth-Death Process

**Definition**: A continuous-time Markov chain on non-negative integers where transitions are limited to ±1, with state-dependent birth rates λₙ and death rates μₙ.

**Indicators**: "arrivals and departures," "population growth and decline," "birth rate and death rate," "steady-state distribution," "absorption probability"

**Template**:
```
State space: {0, 1, 2, ...}
Birth rate in state n: λₙ
Death rate in state n: μₙ
Balance equations: πₙ₊₁ μₙ₊₁ = πₙ λₙ
Steady-state: πₙ = π₀ ∏(λᵢ/μᵢ₊₁, i=0..n-1)
```

**Examples**: M/M/1 queue (λₙ=λ, μₙ=μ), immigration-emigration, population in limited habitat, machine repair (finite population)

**Key problems**: M/M/1 (S96), M/M/c (S97), CTMC (S61), Birth-Death Process (S62)

---

### 21.8 Random Walk / Stochastic Trajectory

**Definition**: A sequence of random steps, where the position at each time is the cumulative sum of independent increments.

**Indicators**: "random walk," "Brownian motion," "diffusion," "stock price path," "gambler's ruin," "first passage time," "drift"

**Template**:
```
Position: Xₜ = X₀ + Σᵢ Zᵢ
Increments: Zᵢ ~ Dist(μ, σ²)
Drift: μ (mean step)
Volatility: σ (step std dev)
Absorbing barriers: optional (e.g., ruin at 0)
Metrics: E[Xₜ], Var[Xₜ], P(first passage ≤ t)
```

**Examples**: Stock price modeling (geometric Brownian motion), polymer chain length, particle diffusion, gambler's ruin, random search

**Key problems**: Random Walk Analysis (S64), Monte Carlo Risk Simulation (S92)

---

## 22. Numerical Methods

### 22.1 Root-Finding Problem

**Definition**: Find x* such that f(x*) = 0 (or f(x*) = target) for a given continuous function f.

**Indicators**: "find where f equals zero," "solve equation numerically," "break-even point," "equilibrium price," "find the root," "what value of x makes this zero"

**Template**:
```
Function: f(x) = [expression]
Domain: x ∈ [a, b] or starting guess x₀
Target: f(x*) = 0 (or f(x*) = c → solve f(x) - c = 0)
Tolerance: ε (e.g., 1e-10)
```

**Examples**: Break-even quantity, equilibrium price, IRR (internal rate of return), steady-state concentration, intersection of curves

**Key problems**: Bisection (A175), Newton-Raphson (A176), Secant (A177), Brent's (A178), Fixed-Point (A179)

---

### 22.2 Interpolation Problem

**Definition**: Given discrete data points {(xᵢ, yᵢ)}, construct a continuous function that passes through (or approximates) the data, enabling evaluation at new x values.

**Indicators**: "estimate between data points," "fill in missing values," "smooth curve through data," "look up table value," "approximate function"

**Template**:
```
Data: {(x₁,y₁), (x₂,y₂), ..., (xₙ,yₙ)}
Query: y(x*) for x* not in {xᵢ}
Method: linear / polynomial / spline / RBF
Smoothness: C⁰ (linear), C² (cubic spline)
```

**Examples**: Temperature at unmeasured times, material property at untested composition, signal reconstruction, terrain elevation between survey points

**Key problems**: Linear (A180), Lagrange (A181), Cubic Spline (A182), Chebyshev (A183), RBF (A184)

---

### 22.3 Quadrature Problem

**Definition**: Numerically approximate a definite integral ∫ₐᵇ f(x)dx when an analytical antiderivative is not available.

**Indicators**: "numerical integral," "area under curve (no formula)," "total accumulated quantity," "integrate numerically," "quadrature"

**Template**:
```
Integrand: f(x)
Limits: [a, b]
Required accuracy: ε
Method: trapezoidal / Simpson / Gaussian / adaptive
```

**Examples**: Total work done (force × distance), cumulative probability from PDF, total heat transfer, area of complex region

**Key problems**: Trapezoidal Rule (A185), Simpson's Rule (A186), Gaussian Quadrature (A187)

---

## 23. Causal Inference

### 23.1 Causal Graph / DAG

**Definition**: A directed acyclic graph where nodes are variables and edges represent direct causal effects. Used to determine what to control for and whether a causal effect is identifiable.

**Indicators**: "what causes what," "confounders," "colliders," "backdoor path," "causal diagram," "DAG," "adjust for," "control for"

**Template**:
```
Variables: {X₁, X₂, ..., Xₙ}
Treatment: T (intervention variable)
Outcome: Y (response variable)
Edges: T → Y, X₁ → T, X₁ → Y (confounders), ...
Query: P(Y | do(T=t))
Adjustment set: {X₁, ...} (minimal set to block backdoor paths)
```

**Examples**: Does education cause higher income? (confounders: family background, ability), drug efficacy (confounders: age, severity), marketing campaign effect (confounders: existing engagement)

**Key problems**: DAG-Based Identification (S109), Propensity Score Matching (S104), Doubly Robust ATE (S110)

---

### 23.2 Treatment-Outcome Model

**Definition**: A statistical model relating a binary or continuous treatment variable to an outcome, with methods to isolate the causal effect from confounding.

**Indicators**: "treatment effect," "causal impact," "does X cause Y," "what would have happened without treatment," "counterfactual," "ATE," "ATT"

**Template**:
```
Treatment: T ∈ {0, 1} (binary) or continuous
Outcome: Y (continuous or binary)
Covariates: X = [X₁, ..., Xₚ]
Estimand: ATE = E[Y(1) - Y(0)] or ATT = E[Y(1) - Y(0) | T=1]
Identification strategy: matching / DiD / IV / RDD / synthetic control
Assumptions: no unmeasured confounders / parallel trends / exclusion restriction / continuity
```

**Examples**: A/B test analysis (with non-compliance), policy evaluation, medical treatment effect, job training program impact

**Key problems**: Propensity Score Matching (S104), Difference-in-Differences (S105), Instrumental Variables (S106), Regression Discontinuity (S107), Synthetic Control (S108), Doubly Robust ATE (S110)

---

## 24. Extended Operations Research

### 24.1 Inventory Model

**Definition**: A model for managing stock levels — when to order, how much to order — balancing ordering costs, holding costs, and stockout costs under deterministic or stochastic demand.

**Indicators**: "inventory," "reorder point," "safety stock," "economic order quantity," "stockout," "how much to order," "when to reorder"

**Template**:
```
Demand: D (units/period), deterministic or D ~ Dist(μ,σ)
Ordering cost: K (fixed cost per order)
Holding cost: h (per unit per period)
Stockout/shortage cost: p (per unit)
Lead time: L (periods)
Decision: Q (order quantity), s (reorder point)
Objective: minimize total cost = ordering + holding + shortage
```

**Examples**: Warehouse inventory management, retail stock replenishment, spare parts management, pharmaceutical inventory

**Key problems**: EOQ (A188), Newsvendor (A189), Safety Stock (A190)

---

### 24.2 Packing / Bin Problem

**Definition**: Pack items of various sizes into containers of fixed capacity, minimizing the number of containers or maximizing the value packed.

**Indicators**: "pack into bins," "fit items in containers," "cutting stock," "minimize waste," "how many containers needed"

**Template**:
```
Items: {(size₁), (size₂), ..., (sizeₙ)}
Bin capacity: C
Objective: minimize number of bins used
Variant: 1D bin packing, 2D cutting stock, 3D container loading
```

**Examples**: Packing boxes into trucks, cutting rolls of material, memory allocation, scheduling tasks into time slots

**Key problems**: Bin Packing FFD (A193), Knapsack (A33-A34), ILP (A32)

---

### 24.3 Facility Location Model

**Definition**: Choose locations for facilities (warehouses, stores, hospitals) to serve demand points, minimizing total cost (distance + fixed costs) subject to capacity constraints.

**Indicators**: "where to put," "facility location," "warehouse placement," "minimize distance to customers," "how many locations," "coverage"

**Template**:
```
Demand points: {d₁, d₂, ..., dₙ} with demands wᵢ
Candidate locations: {f₁, f₂, ..., fₘ}
Distance/cost: cᵢⱼ (cost to serve demand i from facility j)
Fixed cost: Fⱼ (cost to open facility j)
Number to open: p (or minimize total cost including fixed)
Objective: min Σᵢ Σⱼ wᵢ cᵢⱼ xᵢⱼ + Σⱼ Fⱼ yⱼ
```

**Examples**: Warehouse network design, hospital siting, fire station placement, retail store network, EV charging station placement

**Key problems**: Facility Location p-Median (A194), Capacitated VRP (A195), ILP (A32)

---

## 25. Abstract Algebra & Representation Theory

### 25.1 Group Representation

**Definition**: A homomorphism ρ: G → GL(V) from a group G to the group of invertible linear transformations on a vector space V, encoding group elements as matrices.

**Indicators**: "symmetry group acts on," "representation of," "how a group transforms," "character theory," "decompose into irreducibles," "Fourier analysis on groups"

**Template**:
```
Group: G (finite, compact, p-adic, Lie, ...)
Vector space: V over field F (usually ℂ)
Representation: ρ: G → GL(V)
Character: χ_ρ(g) = Tr(ρ(g))
Decomposition: V ≅ ⊕ᵢ nᵢ Vᵢ (irreducible decomposition)
```

**Examples**:
- Molecular symmetry: G = symmetry group of molecule, V = space of atomic orbitals
- Signal processing on groups: Fourier transform as representation decomposition
- Particle physics: representations of SU(3) classify quarks and hadrons

**Key problems**: Character table computation (A196), Induced representation (A199), Decomposition into irreducibles

---

### 25.2 Character / Trace

**Definition**: The character of a representation ρ is the function χ: G → ℂ defined by χ(g) = Tr(ρ(g)). Characters determine representations up to isomorphism.

**Indicators**: "trace of representation," "character table," "class function," "orthogonality relations," "multiplicity of irreducible"

**Template**:
```
Character: χ: G → ℂ, χ(g) = Tr(ρ(g))
Orthogonality: ⟨χᵢ, χⱼ⟩ = (1/|G|) Σ_{g∈G} χᵢ(g) χⱼ(g)* = δᵢⱼ
Decomposition: ⟨χ_V, χᵢ⟩ = multiplicity of Vᵢ in V
```

**Examples**:
- Counting orbits via Burnside's lemma (uses characters of permutation representation)
- Determining molecular vibration modes via character tables
- Constructing error-correcting codes from group characters

**Key problems**: Character table computation (A196), Burnside/Polya counting (A69)

---

### 25.3 Module over Ring

**Definition**: An abelian group M equipped with a scalar multiplication R × M → M satisfying ring-module axioms. Generalizes vector spaces (modules over fields) and representations (modules over group algebras).

**Indicators**: "module structure," "ring action," "annihilator," "torsion," "free module," "projective module," "Whittaker model"

**Template**:
```
Ring: R (commutative or noncommutative)
Module: M (left R-module or right R-module)
Structure maps: R × M → M satisfying r(m + m') = rm + rm', (r + s)m = rm + sm, etc.
Special cases: R = k[G] gives G-representation; R = ℤ gives abelian group
```

**Examples**:
- Whittaker models: module over p-adic group algebra with prescribed character on unipotent radical
- Homology groups as modules over the group ring
- Cryptographic lattices as ℤ-modules

**Key problems**: Whittaker model construction (A197), Rankin-Selberg integral evaluation (A198)

---

### 25.4 Lie Group / Lie Algebra

**Definition**: A Lie group G is a smooth manifold with compatible group structure. Its Lie algebra 𝔤 = T_e G is the tangent space at the identity with Lie bracket [·,·], encoding infinitesimal symmetries.

**Indicators**: "continuous symmetry group," "Lie algebra," "root system," "Cartan subalgebra," "Weyl group," "semisimple," "lattice in Lie group"

**Template**:
```
Lie group: G (e.g., GL_n(ℝ), SL_n(ℝ), SO(n), Sp(2n))
Lie algebra: 𝔤 = T_e G with bracket [X, Y]
Exponential map: exp: 𝔤 → G
Root system: Φ ⊂ 𝔤* (for semisimple 𝔤)
Lattice: Γ ⊂ G discrete, G/Γ has finite volume
```

**Examples**:
- Rotation group SO(3) in physics: Lie algebra = angular momentum operators
- Uniform lattices Γ in semisimple Lie groups (number theory, geometry)
- Gauge theories: Lie group = gauge group, connections on principal bundles

**Key problems**: p-adic valuation & local field arithmetic (A200), Surgery exact sequence (A213)

---

## 26. Algebraic Combinatorics

### 26.1 Symmetric Function

**Definition**: A formal power series f(x₁, x₂, ...) in infinitely many variables that is invariant under all permutations of variables. The ring Λ of symmetric functions has bases: monomial (m_λ), elementary (e_λ), homogeneous (h_λ), power sum (p_λ), Schur (s_λ).

**Indicators**: "symmetric polynomial," "Schur function," "power sum," "partition into parts," "generating function for partitions," "Young diagram"

**Template**:
```
Ring: Λ = lim_{←} ℤ[x₁,...,xₙ]^{S_n}
Partition: λ = (λ₁ ≥ λ₂ ≥ ... ≥ λₖ > 0), |λ| = Σλᵢ
Schur function: s_λ = det(h_{λᵢ - i + j})₁≤i,j≤k (Jacobi-Trudi)
Inner product: ⟨s_λ, s_μ⟩ = δ_{λμ}
```

**Examples**:
- Counting standard Young tableaux of given shape
- Representation theory of S_n: irreducibles ↔ partitions ↔ Schur functions
- Eigenvalue distributions of random matrices (Schur-Weyl duality)

**Key problems**: Schur function expansion (A202), RSK correspondence (A203)

---

### 26.2 Young Tableau / Partition Function

**Definition**: A Young diagram of shape λ is an array of boxes with λᵢ boxes in row i. A standard Young tableau (SYT) is a filling of the diagram with 1,...,n such that entries increase along rows and columns. A semistandard Young tableau (SSYT) allows repeated entries, increasing weakly in rows and strictly in columns.

**Indicators**: "Young diagram," "Young tableau," "Robinson-Schensted," "hook length," "Kostka numbers," "Littlewood-Richardson"

**Template**:
```
Shape: λ = (λ₁, ..., λₖ) partition of n
SYT: T: boxes → {1,...,n} bijection, rows/columns increasing
SSYT: T: boxes → ℕ, rows weakly increasing, columns strictly increasing
Hook length: h(u) = arm(u) + leg(u) + 1 for box u
Number of SYT: f^λ = n! / ∏_{u} h(u) (hook length formula)
```

**Examples**:
- RSK correspondence: bijection between permutations and pairs of SYT
- Representations of GL_n: highest weight ↔ partition ↔ SSYT
- Schubert calculus: intersection numbers computed via Littlewood-Richardson rule

**Key problems**: RSK correspondence (A203), Schur function expansion (A202)

---

### 26.3 Macdonald Polynomial

**Definition**: Macdonald polynomials P_λ(x; q, t) are a two-parameter family of symmetric functions that specialize to Schur (q=t), Hall-Littlewood (q=0), Jack (t=qᵅ, q→1), and zonal polynomials. They are uniquely determined by triangularity with respect to the monomial basis and orthogonality with respect to a (q,t)-inner product.

**Indicators**: "Macdonald polynomial," "q,t-analog," "interpolation polynomial," "ASEP," "Koornwinder," "double affine Hecke algebra"

**Template**:
```
Parameters: q, t ∈ ℂ (or formal variables)
Macdonald polynomial: P_λ(x; q, t) ∈ Λ_ℚ(q,t)
Characterization: P_λ = m_λ + Σ_{μ<λ} c_{λμ} m_μ and ⟨P_λ, P_μ⟩_{q,t} = 0 for λ ≠ μ
Specializations: P_λ(x; q, q) = s_λ(x), P_λ(x; 0, t) = P_λ(x; t) (Hall-Littlewood)
ASEP connection: interpolation polynomials related to stationary measures of ASEP
```

**Examples**:
- Stationary distributions of the asymmetric simple exclusion process (ASEP)
- Hilbert schemes of points on surfaces (Haiman's theorem: n! conjecture)
- Knot invariants via refined Chern-Simons theory

**Key problems**: Macdonald polynomial recurrence (A201), ASEP transition matrix (A204)

---

## 27. Stochastic Analysis & SPDEs

### 27.1 Gaussian Free Field

**Definition**: The Gaussian free field (GFF) on a domain D ⊂ ℝᵈ is the centered Gaussian process with covariance given by the Green's function of the Laplacian: Cov(φ(x), φ(y)) = G_D(x, y). On a torus 𝕋ᵈ with mass m > 0, the covariance is (m² − Δ)⁻¹.

**Indicators**: "Gaussian free field," "GFF," "random distribution," "log-correlated field," "quantum field theory," "Φ⁴ measure," "stochastic quantization"

**Template**:
```
Domain: D = 𝕋ᵈ (torus) or bounded domain in ℝᵈ
Covariance: C = (m² − Δ)⁻¹ (massive GFF) or G_D (Dirichlet GFF)
Cameron-Martin space: H¹(D) (for massive GFF on 𝕋ᵈ)
Regularity: φ ∈ C^{−d/2+1−ε}(D) a.s. (distributional for d ≥ 2)
```

**Examples**:
- Statistical mechanics: scaling limit of discrete height functions
- Constructive QFT: building block for Φ⁴ models
- Random geometry: Liouville quantum gravity via exponential of GFF

**Key problems**: Gaussian free field sampling (A205), Cameron-Martin shift (A207)

---

### 27.2 Regularity Structure / Paracontrolled Distribution

**Definition**: Regularity structures (Hairer) and paracontrolled distributions (Gubinelli-Imkeller-Perkowski) are frameworks for giving meaning to and solving singular stochastic PDEs where products of distributions are ill-defined. They provide renormalization-compatible local descriptions of solution regularity.

**Indicators**: "regularity structure," "paracontrolled," "singular SPDE," "subcritical," "renormalization," "Φ⁴₃," "KPZ equation," "stochastic quantization"

**Template**:
```
SPDE: ∂_t u = Δu + F(u, ∇u) + ξ on D, where ξ is space-time white noise
Regularity: u ∈ C^α for some α < 0 (distributional)
Model: (A, T, G) = (index set, model space, structure group) for regularity structures
Renormalization: subtract divergent counterterms C₁(ε), C₂(ε), ... as regularization ε → 0
Fixed-point: u = K * (F(u) + ξ) in modelled distribution space D^γ
```

**Examples**:
- Φ⁴₃ model: ∂_t u = Δu − u³ + ∞·u + ξ on 𝕋³ (requires Wick renormalization)
- KPZ equation: ∂_t h = Δh + (∂_x h)² + ξ on 𝕋¹
- Parabolic Anderson model: ∂_t u = Δu + u·ξ

**Key problems**: Regularity structure reconstruction (A208), Paracontrolled ansatz (A209), Wick renormalization (A206)

---

### 27.3 Renormalization

**Definition**: The process of systematically removing infinities from a quantum field theory or singular SPDE by adjusting (renormalizing) parameters and counterterms as a regularization cutoff is removed. In the SPDE context, counterterms are deterministic corrections to divergent products of random distributions.

**Indicators**: "renormalization," "counterterm," "Wick ordering," "normal ordering," "mass renormalization," "setting-sun diagram," "BPHZ," "Feynman diagram"

**Template**:
```
Regularized equation: ∂_t u_ε = Δu_ε − (u_ε³ − C₁(ε)u_ε − C₂(ε)u_ε) + ξ_ε
Counterterms: C₁(ε) ~ c₁ε⁻¹ (tadpole), C₂(ε) ~ c₂ log(ε⁻¹) (setting-sun) for d=3
Renormalized limit: u_ε → u as ε → 0 in appropriate topology
Cameron-Martin theorem: shift by ψ ∈ H¹ preserves Gaussian measure equivalence
Singularity under interaction: Φ⁴₃ measure ⊥ shifted measure for λ ≠ 0 and ψ ≠ 0
```

**Examples**:
- Φ⁴₃ on 𝕋³: two counterterms (tadpole + logarithmic mass renormalization)
- KPZ equation: one counterterm (Wick renormalization of gradient squared)
- Dynamical sine-Gordon equation

**Key problems**: Wick renormalization (A206), Cameron-Martin shift (A207), Regularity structure reconstruction (A208)

---

## 28. Algebraic Topology

### 28.1 Homotopy Group / Spectrum

**Definition**: The n-th homotopy group π_n(X, x₀) is the group of homotopy classes of based maps (Sⁿ, *) → (X, x₀). A spectrum E is a sequence of pointed spaces {Eₙ} with structure maps ΣEₙ → Eₙ₊₁, representing a generalized cohomology theory E*(X) = [X, E] in the stable homotopy category.

**Indicators**: "homotopy group," "fundamental group," "higher homotopy," "spectrum," "stable homotopy," "cohomology theory," "Eilenberg-MacLane space"

**Template**:
```
Space: X (CW complex or simplicial set)
Homotopy groups: πₙ(X) = [Sⁿ, X] (based homotopy classes)
Spectrum: E = {Eₙ, σₙ: ΣEₙ → Eₙ₊₁}
Cohomology: Eⁿ(X) = [X, Eₙ] (represented by spectrum)
Stable homotopy category: SH (triangulated, symmetric monoidal)
```

**Examples**:
- π₁(X) classifies covering spaces of X
- K-theory spectrum KU represents complex K-theory
- Thom spectra represent cobordism theories

**Key problems**: Homotopy group computation (A210), Spectral sequence (A211)

---

### 28.2 Operad

**Definition**: An operad O is a collection {O(n)}_{n≥0} of objects (spaces, chain complexes, spectra) with composition maps encoding n-ary operations and their interactions. An N_∞ operad encodes multiplicative norms in equivariant homotopy theory, interpolating between naive and genuine commutativity.

**Indicators**: "operad," "N-infinity operad," "multiplicative norm," "algebraic structure up to homotopy," "E-infinity," "A-infinity," "operadic algebra"

**Template**:
```
Operad: O = {O(n)}_{n≥0} with Σₙ-action and composition maps
γ: O(k) × O(n₁) × ... × O(nₖ) → O(n₁ + ... + nₖ)
Algebra over O: space X with O(n) × X^n → X satisfying associativity/equivariance
N_∞ operad: equivariant operad between N_∞ (additive) and E_∞ (fully commutative)
Indexing system: specifies which transfers/norms exist for subgroups H ≤ G
```

**Examples**:
- E_∞ operads: encode homotopy-commutative ring structures (e.g., on K-theory)
- A_∞ operads: encode homotopy-associative (but not commutative) structures
- N_∞ operads: classify equivariant commutative ring structures by indexing systems

**Key problems**: Equivariant fixed-point theorem (A212), Spectral sequence (A211)

---

### 28.3 Equivariant Stable Category

**Definition**: For a finite group G, the G-equivariant stable homotopy category SH_G is the stabilization of the category of G-spaces with respect to representation spheres S^V for all real G-representations V. Objects are genuine G-spectra, which support RO(G)-graded homotopy groups, geometric fixed points, and norm maps.

**Indicators**: "equivariant spectrum," "genuine G-spectrum," "geometric fixed points," "slice filtration," "Hill-Hopkins-Ravenel," "norm map," "representation sphere"

**Template**:
```
Group: G (finite)
Category: SH_G (genuine G-spectra)
Grading: RO(G)-graded homotopy groups π_V^G(E)
Fixed points: E^G (categorical), Φ^G(E) (geometric)
Slice filtration: ... ⊂ τ^G_{≥n+1} ⊂ τ^G_{≥n} ⊂ ... (stratification by "complexity")
Norm: N_H^G: SH_H → SH_G (multiplicative induction)
```

**Examples**:
- Hill-Hopkins-Ravenel solution of Kervaire invariant one problem uses slice filtration
- Real K-theory KR as C₂-equivariant spectrum
- Equivariant cobordism MU_G

**Key problems**: Equivariant fixed-point theorem (A212), Spectral sequence (A211)

---

## 29. Symplectic & Differential Geometry

### 29.1 Symplectic Manifold

**Definition**: A symplectic manifold (M²ⁿ, ω) is an even-dimensional smooth manifold equipped with a closed nondegenerate 2-form ω (dω = 0, ωⁿ ≠ 0). By Darboux's theorem, locally (M, ω) looks like (ℝ²ⁿ, Σ dpᵢ ∧ dqᵢ).

**Indicators**: "symplectic form," "phase space," "Hamiltonian system," "Darboux coordinates," "symplectomorphism," "area-preserving"

**Template**:
```
Manifold: (M^{2n}, ω) with dω = 0 and ω^n ≠ 0
Darboux coordinates: (p₁,...,pₙ, q₁,...,qₙ) with ω = Σ dpᵢ ∧ dqᵢ
Hamiltonian vector field: X_H defined by ι_{X_H} ω = −dH
Symplectomorphism: φ: (M, ω) → (M, ω) with φ*ω = ω
```

**Examples**:
- Classical mechanics: phase space T*Q with canonical symplectic form
- Kähler manifolds: complex manifolds with compatible symplectic structure
- Coadjoint orbits of Lie groups carry natural symplectic structures

**Key problems**: Hamiltonian flow integration (A215), Moser trick (A216)

---

### 29.2 Lagrangian Submanifold

**Definition**: A Lagrangian submanifold L of a symplectic manifold (M²ⁿ, ω) is an n-dimensional submanifold such that ω|_L = 0 (the symplectic form restricts to zero on L). Lagrangian submanifolds are "half-dimensional" and maximally isotropic.

**Indicators**: "Lagrangian submanifold," "Lagrangian torus," "special Lagrangian," "Lagrangian isotopy," "Lagrangian surgery," "Floer homology"

**Template**:
```
Ambient: (M^{2n}, ω) symplectic
Lagrangian: L^n ⊂ M with dim L = n and ω|_L = 0
Polyhedral Lagrangian: piecewise-linear Lagrangian surface (in ℝ⁴ with standard ω)
Smoothing: replace corners/edges by smooth patches preserving Lagrangian condition
Maslov class: μ ∈ H¹(L; ℤ), obstruction to grading
```

**Examples**:
- Zero section of T*Q is Lagrangian in (T*Q, ω_can)
- Real locus ℝPⁿ ⊂ ℂPⁿ is Lagrangian
- Polyhedral Lagrangians: PL surfaces in ℝ⁴ with ω = dp₁∧dq₁ + dp₂∧dq₂

**Key problems**: Lagrangian isotopy (A214), Hamiltonian flow integration (A215)

---

### 29.3 Hamiltonian Isotopy

**Definition**: A Hamiltonian isotopy is a smooth family of symplectomorphisms {φₜ}_{t∈[0,1]} generated by a (possibly time-dependent) Hamiltonian function H_t, meaning dφₜ/dt = X_{Hₜ} ∘ φₜ. Two Lagrangian submanifolds are Hamiltonian isotopic if one can be deformed to the other through Lagrangians via such a flow.

**Indicators**: "Hamiltonian isotopy," "Hamiltonian diffeomorphism," "Lagrangian smoothing via isotopy," "smoothable Lagrangian," "Weinstein neighborhood"

**Template**:
```
Flow: φₜ: M → M with φ₀ = id, generated by X_{Hₜ}
Condition: φₜ*ω = ω for all t (symplectomorphisms)
Lagrangian isotopy: L₀, L₁ Lagrangian with L₁ = φ₁(L₀)
Smoothing: polyhedral Lagrangian L_PL → smooth Lagrangian L_smooth via Hamiltonian isotopy
```

**Examples**:
- Smoothing polyhedral surfaces: replace corners by smooth patches, connected by Hamiltonian deformation
- Arnold conjecture: Hamiltonian isotopies have at least as many fixed points as topology demands
- Floer homology: invariant of Lagrangian pairs under Hamiltonian isotopy

**Key problems**: Lagrangian isotopy (A214), Moser trick (A216)

---

## 30. Advanced Spectral Theory

### 30.1 Graph Laplacian Spectrum

**Definition**: For a graph G = (V, E) with edge weights w_e, the Laplacian L = Σ_{e={i,j}} w_e (eᵢ − eⱼ)(eᵢ − eⱼ)ᵀ is a positive semidefinite matrix. Its eigenvalues 0 = λ₁ ≤ λ₂ ≤ ... ≤ λₙ encode connectivity, expansion, mixing time, and partitioning properties.

**Indicators**: "graph Laplacian," "spectral gap," "algebraic connectivity," "Fiedler vector," "Cheeger inequality," "ε-light," "spectral partitioning"

**Template**:
```
Graph: G = (V, E) with weights wₑ ≥ 0
Edge Laplacian: Lₑ = wₑ (eᵢ − eⱼ)(eᵢ − eⱼ)ᵀ
Total Laplacian: L = Σₑ Lₑ, spectrum 0 = λ₁ ≤ ... ≤ λₙ
Normalized: L̃ = D⁻¹/²LD⁻¹/² (normalized Laplacian)
ε-light subset: S ⊆ V with L_S ⪯ εL (in Loewner order)
```

**Examples**:
- Network partitioning: Fiedler vector (eigenvector for λ₂) gives bisection
- Random walks: mixing time ∝ 1/λ₂
- Graph sparsification: approximate L by sparse matrix L̃ with L̃ ≈ εL

**Key problems**: BSS barrier method (A217), Graph Laplacian partitioning (A220)

---

### 30.2 Free Probability / Free Convolution

**Definition**: Free probability (Voiculescu) is a noncommutative probability theory where the notion of independence is replaced by "freeness" (free independence). The free additive convolution μ ⊞ ν describes the spectral distribution of A + B when A, B are freely independent. The R-transform linearizes free additive convolution.

**Indicators**: "free probability," "free convolution," "R-transform," "free independence," "random matrix," "free entropy," "Voiculescu"

**Template**:
```
Noncommutative probability space: (A, φ) with φ: A → ℂ tracial
Free independence: mixed moments factor through non-crossing partitions
R-transform: R_μ(z) with G_μ(z) = 1/(z − R_μ(G_μ(z))) (Cauchy transform relation)
Free additive convolution: R_{μ⊞ν} = R_μ + R_ν
Free multiplicative convolution: S_{μ⊠ν} = S_μ · S_ν
```

**Examples**:
- Wigner semicircle law: free CLT for freely independent random variables
- Marchenko-Pastur law: free Poisson distribution (eigenvalues of sample covariance)
- Additive free convolution of spectral distributions in random matrix theory

**Key problems**: Free additive convolution (A218), Interlacing polynomials MSS (A219)

---

### 30.3 Interlacing Polynomial Family

**Definition**: A family of real-rooted polynomials {fᵢ}ᵢ is an interlacing family if every convex combination Σ αᵢ fᵢ (αᵢ ≥ 0, Σαᵢ = 1) is real-rooted. By the barrier method of Marcus-Spielman-Srivastava (MSS), if the expected polynomial E[f] has largest root ≤ r, then at least one fᵢ has largest root ≤ r.

**Indicators**: "interlacing polynomial," "real-rooted," "common interlacing," "MSS method," "Kadison-Singer," "restricted invertibility," "barrier function"

**Template**:
```
Polynomial: p(x) = Σ aₖ xᵏ with all roots real
Interlacing: p₁ ≺ p₂ if roots of p₁ and p₂ alternate
Interlacing family: {f₁, ..., fₘ} with Σ αᵢ fᵢ real-rooted for all convex combinations
Barrier function: Φᵤ(A) = Tr((uI − A)⁻¹) (resolvent potential)
BSS argument: bound Φ, show max root of random matrix bounded by u
```

**Examples**:
- Kadison-Singer problem (solved by MSS 2015): paving conjecture via interlacing
- Ramanujan graph existence: random lifts have spectral gap via interlacing
- Graph sparsification: thin subsets of edges approximate full Laplacian

**Key problems**: Interlacing polynomials MSS (A219), BSS barrier method (A217)

---

## 31. Tensor Analysis

### 31.1 Tensor Space / Multilinear Map

**Definition**: A tensor of order k over vector spaces V₁, ..., Vₖ is an element of the tensor product V₁ ⊗ ... ⊗ Vₖ. Equivalently, a k-linear map V₁* × ... × Vₖ* → ℝ. In coordinates, T = Σ Tᵢ₁...ᵢₖ eᵢ₁ ⊗ ... ⊗ eᵢₖ.

**Indicators**: "tensor," "multilinear," "tensor product," "contraction," "outer product," "tensor rank," "multiway array"

**Template**:
```
Tensor: T ∈ V₁ ⊗ V₂ ⊗ ... ⊗ Vₖ (order k)
Components: T_{i₁i₂...iₖ} ∈ ℝ (with respect to bases)
Rank: minimum r such that T = Σⱼ₌₁ʳ v₁ⱼ ⊗ v₂ⱼ ⊗ ... ⊗ vₖⱼ
Contraction: Σᵢ T_{...i...} S_{...i...} (summing over shared index)
Flattenings: T_{(k)} = matricization along mode k
```

**Examples**:
- Stress-energy tensor in physics: T_μν encodes energy/momentum density
- Multiway data: users × items × time → ratings tensor
- Moment tensors in statistics: E[x ⊗ x ⊗ x] captures third-order structure

**Key problems**: CP-ALS (A221), Tucker/HOSVD (A222)

---

### 31.2 Tensor Decomposition (CP/Tucker)

**Definition**: The CP (Canonical Polyadic) decomposition writes a tensor T as a sum of rank-1 terms: T ≈ Σᵣ λᵣ a_r ⊗ b_r ⊗ c_r. The Tucker decomposition writes T ≈ G ×₁ A ×₂ B ×₃ C where G is a smaller core tensor. ALS (Alternating Least Squares) solves each factor matrix while fixing others.

**Indicators**: "CP decomposition," "PARAFAC," "Tucker decomposition," "HOSVD," "tensor rank," "tensor factorization," "alternating least squares," "missing data"

**Template**:
```
CP: T ≈ Σᵣ₌₁ᴿ λᵣ aᵣ ⊗ bᵣ ⊗ cᵣ (minimize ||T − T̂||_F)
Tucker: T ≈ G ×₁ A ×₂ B ×₃ C (core tensor G, factor matrices A, B, C)
ALS subproblem: fix B, C → solve for A via least squares
Missing data: mask Ω, minimize Σ_{(i,j,k)∈Ω} (T_{ijk} − T̂_{ijk})²
Kernelized: replace finite-dimensional mode with RKHS, use kernel trick
```

**Examples**:
- Chemometrics: decompose fluorescence spectra (samples × excitation × emission)
- Recommender systems: users × items × context tensor factorization
- Neuroimaging: voxels × time × subjects tensor decomposition

**Key problems**: CP-ALS (A221), Tucker/HOSVD (A222), Tensor train (A223), Randomized decomposition (A224)

---

### 31.3 Tensor Network

**Definition**: A tensor network is a graph where nodes represent tensors and edges represent index contractions. The full contraction of the network yields a scalar or lower-order tensor. Tensor networks generalize matrix multiplication and provide efficient representations of high-dimensional tensors.

**Indicators**: "tensor network," "tensor train," "MPS," "DMRG," "contraction order," "bond dimension," "tree tensor network"

**Template**:
```
Network: graph G = (V, E) with tensor Tᵥ at each vertex v
Edges: e ∈ E represents contraction of shared index
Bond dimension: max dimension along contracted edges
Tensor train: T_{i₁...iₙ} = A₁[i₁] · A₂[i₂] · ... · Aₙ[iₙ] (matrix product)
Contraction cost: depends on elimination order (NP-hard to optimize in general)
```

**Examples**:
- Quantum many-body physics: matrix product states (MPS), DMRG
- Machine learning: tensor network layers as structured linear maps
- Quantum circuit simulation: tensor network contraction

**Key problems**: Tensor train (A223), CP-ALS (A221)

---

## 32. Reproducing Kernel Hilbert Spaces & Krylov Methods

### 32.1 RKHS / Kernel

**Definition**: A reproducing kernel Hilbert space (RKHS) H_k on a set X is a Hilbert space of functions f: X → ℝ with a kernel k: X × X → ℝ such that f(x) = ⟨f, k(x, ·)⟩_H for all f ∈ H_k, x ∈ X (reproducing property). The kernel encodes the geometry of the function space.

**Indicators**: "kernel method," "RKHS," "reproducing kernel," "Mercer's theorem," "kernel trick," "feature map," "Gaussian kernel," "Gram matrix"

**Template**:
```
Kernel: k: X × X → ℝ, symmetric positive definite
RKHS: H_k = closure of span{k(x, ·) : x ∈ X}
Reproducing property: f(x) = ⟨f, k(x, ·)⟩
Feature map: φ: X → H_k, φ(x) = k(x, ·), with k(x,y) = ⟨φ(x), φ(y)⟩
Kernel trick: inner products in H_k computed via k without explicit φ
Gram matrix: K_{ij} = k(xᵢ, xⱼ) for data points x₁, ..., xₙ
```

**Examples**:
- Kernel SVM: classification in high-dimensional feature space via kernel
- Gaussian processes: prior over functions defined by kernel
- Kernelized tensor decomposition: infinite-dimensional modes via kernel trick

**Key problems**: Preconditioned CG (A226), Kronecker preconditioning (A229)

---

### 32.2 Krylov Subspace

**Definition**: For a matrix A and vector b, the k-th Krylov subspace is K_k(A, b) = span{b, Ab, A²b, ..., A^{k-1}b}. Krylov methods (CG, GMRES, Lanczos) find approximate solutions to Ax = b or eigenvalue problems by searching within K_k, requiring only matrix-vector products (matrix-free).

**Indicators**: "Krylov subspace," "conjugate gradient," "GMRES," "Lanczos," "matrix-free," "preconditioner," "iterative solver," "sparse linear system"

**Template**:
```
System: Ax = b (A ∈ ℝⁿˣⁿ, possibly sparse or available only as operator)
Krylov subspace: K_k(A, b) = span{b, Ab, ..., A^{k-1}b}
CG: for SPD A, minimizes ||x − x*||_A over x₀ + K_k(A, r₀)
Preconditioner: M ≈ A with M⁻¹ cheap to apply; solve M⁻¹Ax = M⁻¹b
PCG convergence: ||eₖ||_A / ||e₀||_A ≤ 2(√κ(M⁻¹A) − 1)/(√κ(M⁻¹A) + 1))^k
```

**Examples**:
- Large sparse linear systems from FEM/PDE discretization
- Eigenvalue computation for large matrices (Lanczos algorithm)
- Kronecker-structured systems: (A₁ ⊗ A₂ ⊗ ... ⊗ Aₖ)x = b (exploit structure)

**Key problems**: Conjugate gradient (A225), Preconditioned CG (A226), GMRES (A227), Block Krylov (A228), Kronecker preconditioning (A229), Matrix-free operators (A230)

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
| 18. Time Series | algorithms-statistics.md S46-S60 | statsmodels, prophet | §16 Time Series Results |
| 19. Stochastic Processes | algorithms-statistics.md S61-S65 | scipy.linalg, scipy.stats | §16.3 Survival/Process Results |
| 20. Machine Learning | algorithms-statistics.md S69-S90 | scikit-learn, xgboost, umap-learn | §17 Machine Learning Results |
| 21. Simulation & ODEs | algorithms.md §29 (A165-A174), algorithms-statistics.md S91-S103 | scipy.integrate, simpy, numpy | §18 Simulation & ODE Results |
| 22. Numerical Methods | algorithms.md §30-§32 (A175-A187) | scipy.optimize, scipy.interpolate, scipy.integrate | §19 Numerical Methods Results |
| 23. Causal Inference | algorithms-statistics.md S104-S110 | scikit-learn, statsmodels, dowhy | §20 Causal Inference Results |
| 24. Extended OR | algorithms.md §33 (A188-A195) | PuLP, OR-Tools, scipy | §21 Extended OR Results |
| 25. Abstract Algebra & Representation Theory | §34 (A196-A200) | §15 SageMath, §16 GAP, §4 SymPy | §23 Representation Theory Results |
| 26. Algebraic Combinatorics | §35 (A201-A204) | §15 SageMath, §4 SymPy | §24 Algebraic Combinatorics Results |
| 27. Stochastic Analysis & SPDEs | §36 (A205-A209) | §5 SciPy, §4 SymPy | §22 Stochastic Analysis Results |
| 28. Algebraic Topology | §37 (A210-A213) | §15 SageMath, §4 SymPy | §25 Algebraic Topology Results |
| 29. Symplectic & Differential Geometry | §38 (A214-A216) | §5 SciPy, §4 SymPy | §26 Symplectic Geometry Results |
| 30. Advanced Spectral Theory | §39 (A217-A220) | §1 NetworkX, §18 scipy.sparse.linalg | §27 Spectral Graph Theory Results |
| 31. Tensor Analysis | §40 (A221-A224) | §17 tensorly, §8 numpy | §28 Tensor Decomposition Results |
| 32. RKHS & Krylov Methods | §41 (A225-A230) | §18 scipy.sparse.linalg, §5 SciPy | §19 Numerical Methods Results |

Also see: **problem-classification.md** for rapid pattern matching from natural language to structure, **common-mistakes.md** for modeling pitfalls by structure type.
