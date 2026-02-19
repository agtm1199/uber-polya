# Discrete Mathematics Structure Catalog

A catalog of 32 discrete math structures across 8 domains. Use this to match real-world problems to mathematical models during Phase 2 of the uber-model skill.

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
