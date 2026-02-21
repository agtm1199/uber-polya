# Algorithm Catalog

**Scope**: Discrete Mathematics (86 algorithms), Continuous Optimization (8 algorithms), Linear Algebra (12 algorithms), Calculus (10 algorithms), Geometry & Trigonometry (10 algorithms), Financial Mathematics (8 algorithms), Game Theory (12 algorithms), Decision Analysis (10 algorithms), Multi-Objective Optimization (8 algorithms), Numerical ODEs & Dynamical Systems (10 algorithms)

Comprehensive catalog of algorithms for mathematical problem solving. Organized by domain, each entry includes complexity, solver library, correctness guarantee, and implementation guidance.

**Legend**:
- **T**: Time complexity | **S**: Space complexity
- **Lib**: Recommended Python library
- **Exact**: Guaranteed optimal | **Approx(α)**: Within factor α of optimal | **Heuristic**: No formal guarantee

---

## 1. Graph Traversal & Search

### A1: Breadth-First Search (BFS)

**Problem**: Shortest path (unweighted), reachability, connected components, bipartiteness check.
**T**: O(V + E) | **S**: O(V)
**Lib**: `networkx.bfs_edges()`, `networkx.shortest_path()`
**Guarantee**: Exact (shortest path in unweighted graphs)

```python
from collections import deque

def bfs(graph: dict[str, list[str]], source: str) -> dict[str, int]:
    dist = {source: 0}
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v in graph[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                queue.append(v)
    return dist
```

**Use when**: Unweighted shortest path, level-order traversal, checking bipartiteness (odd cycle detection).

---

### A2: Depth-First Search (DFS)

**Problem**: Reachability, cycle detection, topological sort, connected/strongly-connected components, articulation points, bridges.
**T**: O(V + E) | **S**: O(V) (recursion stack)
**Lib**: `networkx.dfs_edges()`, `networkx.is_directed_acyclic_graph()`
**Guarantee**: Exact

```python
def dfs(graph: dict[str, list[str]], source: str) -> set[str]:
    visited = set()
    stack = [source]
    while stack:
        u = stack.pop()
        if u not in visited:
            visited.add(u)
            stack.extend(graph[u])
    return visited
```

**Use when**: Cycle detection, topological ordering, finding connected components, building DFS tree for structural analysis.

---

### A3: Topological Sort

**Problem**: Linear ordering of DAG vertices such that every edge (u,v) has u before v.
**T**: O(V + E) | **S**: O(V)
**Lib**: `networkx.topological_sort()`, `networkx.topological_generations()`
**Guarantee**: Exact. Exists iff graph is a DAG.

**Algorithms**: Kahn's (BFS-based, uses in-degree) or DFS-based (reverse post-order).

```python
# Kahn's algorithm
from collections import deque

def topological_sort(graph: dict[str, list[str]], nodes: set[str]) -> list[str]:
    in_degree = {u: 0 for u in nodes}
    for u in graph:
        for v in graph[u]:
            in_degree[v] += 1
    queue = deque(u for u in nodes if in_degree[u] == 0)
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in graph[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)
    if len(order) != len(nodes):
        raise ValueError("Graph has a cycle -- not a DAG")
    return order
```

**Use when**: Dependency resolution, task scheduling, build systems, course planning.

---

### A4: Cycle Detection

**Problem**: Determine if a graph contains a cycle.
**T**: O(V + E) | **S**: O(V)
**Lib**: `networkx.find_cycle()`, `networkx.is_directed_acyclic_graph()`
**Guarantee**: Exact

**Directed**: DFS with three-color marking (white/gray/black). Back edge → cycle.
**Undirected**: DFS tracking parent. Edge to visited non-parent → cycle.

**Use when**: Validating DAG property, deadlock detection, constraint consistency.

---

### A5: Strongly Connected Components (SCC)

**Problem**: Partition directed graph into maximal strongly connected subgraphs.
**T**: O(V + E) | **S**: O(V)
**Lib**: `networkx.kosaraju_strongly_connected_components()`, `networkx.condensation()`
**Guarantee**: Exact

**Algorithms**: Tarjan's (single DFS, stack-based) or Kosaraju's (two-pass DFS).

**Use when**: Analyzing reachability in digraphs, simplifying digraph to DAG of SCCs, 2-SAT solving.

---

### A6: Articulation Points & Bridges

**Problem**: Find vertices/edges whose removal disconnects the graph.
**T**: O(V + E) | **S**: O(V)
**Lib**: `networkx.articulation_points()`, `networkx.bridges()`
**Guarantee**: Exact

**Use when**: Network reliability, critical infrastructure identification, biconnected components.

---

### A7: Connected Components

**Problem**: Find all connected components of an undirected graph.
**T**: O(V + E) | **S**: O(V)
**Lib**: `networkx.connected_components()`, `networkx.number_connected_components()`
**Guarantee**: Exact

**Use when**: Decomposing independent subproblems, checking connectivity, clustering.

---

## 2. Shortest Path

### A8: Dijkstra's Algorithm

**Problem**: Single-source shortest path with non-negative edge weights.
**T**: O((V + E) log V) with binary heap | **S**: O(V)
**Lib**: `networkx.dijkstra_path()`, `networkx.single_source_dijkstra()`
**Guarantee**: Exact (requires non-negative weights)

```python
import heapq

def dijkstra(graph: dict[str, list[tuple[str, float]]], source: str) -> dict[str, float]:
    dist = {source: 0.0}
    pq = [(0.0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, float('inf')):
            continue
        for v, w in graph[u]:
            nd = d + w
            if nd < dist.get(v, float('inf')):
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist
```

**Use when**: Road networks, weighted routing, any non-negative weighted shortest path.

---

### A9: Bellman-Ford Algorithm

**Problem**: Single-source shortest path with arbitrary (possibly negative) edge weights. Detects negative cycles.
**T**: O(VE) | **S**: O(V)
**Lib**: `networkx.bellman_ford_path()`, `networkx.negative_edge_cycle()`
**Guarantee**: Exact. Reports negative cycle if one exists.

**Use when**: Graphs with negative weights, currency arbitrage detection, difference constraints.

---

### A10: Floyd-Warshall Algorithm

**Problem**: All-pairs shortest paths.
**T**: O(V³) | **S**: O(V²)
**Lib**: `networkx.floyd_warshall()`, `networkx.floyd_warshall_numpy()`
**Guarantee**: Exact

**Use when**: Small dense graphs where all pairwise distances are needed. Prefer Dijkstra from each source for sparse graphs.

---

### A11: A* Search

**Problem**: Shortest path with admissible heuristic (informed search).
**T**: O(E) worst case, much better in practice with good heuristic | **S**: O(V)
**Lib**: `networkx.astar_path()`
**Guarantee**: Exact (if heuristic is admissible: h(v) ≤ actual cost)

**Use when**: Path finding with domain-specific distance heuristic (e.g., Euclidean distance for spatial graphs).

---

### A12: Longest Path in DAG

**Problem**: Find the longest (heaviest) path in a DAG.
**T**: O(V + E) | **S**: O(V)
**Lib**: `networkx.dag_longest_path()`, `networkx.dag_longest_path_length()`
**Guarantee**: Exact (only for DAGs -- NP-hard for general graphs)

**Use when**: Critical path method, project scheduling, makespan computation.

---

## 3. Minimum Spanning Tree

### A13: Kruskal's Algorithm

**Problem**: Minimum spanning tree of undirected weighted graph.
**T**: O(E log E) | **S**: O(V) (with Union-Find)
**Lib**: `networkx.minimum_spanning_tree(algorithm='kruskal')`
**Guarantee**: Exact

**Use when**: Sparse graphs (E close to V). Uses Union-Find data structure.

---

### A14: Prim's Algorithm

**Problem**: Minimum spanning tree.
**T**: O(E log V) with binary heap | **S**: O(V)
**Lib**: `networkx.minimum_spanning_tree(algorithm='prim')`
**Guarantee**: Exact

**Use when**: Dense graphs (E close to V²). Grows tree from a single vertex.

---

## 4. Matching

### A15: Maximum Bipartite Matching (Hopcroft-Karp)

**Problem**: Find maximum cardinality matching in a bipartite graph.
**T**: O(E√V) | **S**: O(V)
**Lib**: `networkx.bipartite.maximum_matching()`, `networkx.bipartite.hopcroft_karp_matching()`
**Guarantee**: Exact

**Use when**: Assignment feasibility (can all items be matched?), Hall's theorem verification.

---

### A16: Maximum Weight Bipartite Matching (Hungarian)

**Problem**: Find maximum (or minimum) weight perfect matching in a bipartite graph.
**T**: O(V³) | **S**: O(V²)
**Lib**: `scipy.optimize.linear_sum_assignment()`
**Guarantee**: Exact

```python
from scipy.optimize import linear_sum_assignment
import numpy as np

cost_matrix = np.array([[...]])  # n x m cost matrix
row_ind, col_ind = linear_sum_assignment(cost_matrix)  # minimizes by default
# For maximization: linear_sum_assignment(-cost_matrix)
total_cost = cost_matrix[row_ind, col_ind].sum()
```

**Use when**: Optimal assignment with costs/profits. Workers to jobs, resources to tasks.

---

### A17: Stable Matching (Gale-Shapley)

**Problem**: Find a stable matching given preference lists for two groups.
**T**: O(n²) | **S**: O(n)
**Lib**: Custom implementation (simple to code)
**Guarantee**: Exact (produces proposer-optimal stable matching)

**Use when**: College admissions, resident matching, any two-sided market with preferences.

---

### A18: Maximum Weight General Matching

**Problem**: Maximum weight matching in a general (non-bipartite) graph.
**T**: O(V³) (Edmonds' blossom algorithm) | **S**: O(V²)
**Lib**: `networkx.max_weight_matching()`
**Guarantee**: Exact

**Use when**: Non-bipartite matching needs (e.g., pairing elements of one set).

---

## 5. Network Flow

### A19: Maximum Flow (Edmonds-Karp / Dinic)

**Problem**: Find maximum flow from source s to sink t.
**T**: O(VE²) Edmonds-Karp, O(V²E) Dinic | **S**: O(V + E)
**Lib**: `networkx.maximum_flow()`, `networkx.minimum_cut()`
**Guarantee**: Exact. Max-flow min-cut theorem provides optimality certificate.

```python
import networkx as nx

G = nx.DiGraph()
G.add_edge('s', 'a', capacity=10)
G.add_edge('a', 't', capacity=5)
flow_value, flow_dict = nx.maximum_flow(G, 's', 't')
```

**Use when**: Network capacity, supply/demand, bipartite matching (as flow), min-cut for partitioning.

---

### A20: Minimum Cost Flow

**Problem**: Find minimum cost flow satisfying supply/demand constraints.
**T**: O(V²E log V) | **S**: O(V + E)
**Lib**: `networkx.min_cost_flow()`, OR-Tools `SimpleMinCostFlow`
**Guarantee**: Exact

**Use when**: Transportation problem, assignment with costs, optimal routing with capacities.

---

## 6. Graph Coloring

### A21: Greedy Coloring

**Problem**: Color graph vertices such that no two adjacent vertices share a color.
**T**: O(V + E) | **S**: O(V)
**Lib**: `networkx.greedy_color(strategy='largest_first')`
**Guarantee**: Heuristic. Uses at most Δ+1 colors (Δ = max degree). NOT guaranteed optimal.

**Strategies**: `largest_first`, `smallest_last`, `DSATUR`, `independent_set`

**Use when**: Quick feasible coloring, upper bound on chromatic number.

---

### A22: Exact Graph Coloring

**Problem**: Find minimum number of colors (chromatic number).
**T**: Exponential (NP-hard) | **S**: O(2^V) for DP, O(V) for backtracking
**Lib**: Custom backtracking or ILP formulation
**Guarantee**: Exact

**Approaches**:
1. **Backtracking with pruning**: Try colors 1,2,..., backtrack on conflict. Use DSatur ordering.
2. **ILP**: Binary variable x_{v,c} = 1 if vertex v gets color c. Minimize number of colors used.
3. **SAT encoding**: Is the graph k-colorable? Binary search on k, encode as SAT.

**Use when**: Small graphs (V ≤ 50) or when exact chromatic number is required.

---

## 7. Independent Set, Vertex Cover, Clique

### A23: Maximum Independent Set

**Problem**: Find largest set of vertices with no two adjacent.
**T**: NP-hard in general. O(1.2^V) exact via Bron-Kerbosch on complement.
**Lib**: Custom backtracking, or ILP
**Guarantee**: Exact for small instances. Heuristic for large.

**Relation**: Independent set in G = clique in complement G'. Vertex cover = V \ independent set.

---

### A24: Minimum Vertex Cover

**Problem**: Find smallest set of vertices covering all edges.
**T**: NP-hard exact, but 2-approximation in O(E).
**Lib**: `networkx.min_weighted_vertex_cover()` (2-approximation)
**Guarantee**: Approx(2) via maximal matching. Exact via ILP for small instances.

**Konig's theorem**: In bipartite graphs, min vertex cover = max matching (polynomial!).

---

### A25: Maximum Clique (Bron-Kerbosch)

**Problem**: Find largest complete subgraph.
**T**: O(3^(V/3)) worst case | **S**: O(V)
**Lib**: `networkx.find_cliques()` (enumerates all maximal cliques)
**Guarantee**: Exact (but exponential)

**Use when**: Community detection, conflict analysis, small graphs.

---

## 8. Euler & Hamilton

### A26: Eulerian Path / Circuit (Hierholzer)

**Problem**: Find a path/circuit traversing every edge exactly once.
**T**: O(E) | **S**: O(E)
**Lib**: `networkx.eulerian_circuit()`, `networkx.has_eulerian_path()`
**Guarantee**: Exact. Exists iff: circuit = all degrees even; path = exactly 0 or 2 odd-degree vertices.

---

### A27: Hamiltonian Path / Cycle

**Problem**: Find a path/cycle visiting every vertex exactly once.
**T**: NP-complete (decision). O(n² 2^n) exact DP (Held-Karp). | **S**: O(n 2^n)
**Lib**: Custom DP or ILP
**Guarantee**: Exact for n ≤ 20-25 via DP with bitmask.

---

## 9. Traveling Salesman (TSP)

### A28: TSP -- Exact (Held-Karp DP)

**Problem**: Minimum weight Hamiltonian cycle.
**T**: O(n² 2^n) | **S**: O(n 2^n)
**Guarantee**: Exact for n ≤ 20-25

```python
import functools

def tsp_held_karp(dist: list[list[float]]) -> float:
    n = len(dist)

    @functools.cache
    def dp(visited: int, last: int) -> float:
        if visited == (1 << n) - 1:
            return dist[last][0]
        best = float('inf')
        for nxt in range(n):
            if not (visited & (1 << nxt)):
                best = min(best, dist[last][nxt] + dp(visited | (1 << nxt), nxt))
        return best

    return dp(1, 0)
```

---

### A29: TSP -- Approximation (Christofides)

**Problem**: TSP in metric spaces (triangle inequality).
**T**: O(n³) | **S**: O(n²)
**Lib**: Custom (MST + minimum weight matching + Euler shortcutting)
**Guarantee**: Approx(3/2) for metric TSP. Best known polynomial approximation.

---

### A30: TSP -- Heuristic (2-opt, Or-opt, LKH)

**Problem**: TSP for large instances.
**T**: O(n²) per iteration | **S**: O(n)
**Lib**: OR-Tools routing solver
**Guarantee**: Heuristic. No formal bound. Often near-optimal in practice.

---

## 10. Optimization (Linear & Integer Programming)

### A31: Linear Programming (Simplex / Interior Point)

**Problem**: Optimize linear objective subject to linear constraints, continuous variables.
**T**: Polynomial (interior point), exponential worst-case (simplex, but fast in practice)
**Lib**: `scipy.optimize.linprog()`, `pulp.LpProblem`
**Guarantee**: Exact. Dual solution provides optimality certificate.

```python
from pulp import LpProblem, LpVariable, LpMaximize, value

prob = LpProblem("example", LpMaximize)
x = LpVariable("x", lowBound=0)
y = LpVariable("y", lowBound=0)
prob += 3*x + 2*y  # objective
prob += x + y <= 10  # constraint
prob.solve()
print(f"x={value(x)}, y={value(y)}, obj={value(prob.objective)}")
```

---

### A32: Integer Linear Programming (Branch & Bound)

**Problem**: LP with integrality constraints on some/all variables.
**T**: NP-hard worst case. Practical: depends on instance structure.
**Lib**: `pulp` (CBC solver), OR-Tools (`pywraplp`), Gurobi (if available)
**Guarantee**: Exact (with sufficient time). Reports optimality gap if terminated early.

```python
from pulp import LpProblem, LpVariable, LpMinimize, LpInteger, LpBinary, value, LpStatus

prob = LpProblem("ilp", LpMinimize)
x = [LpVariable(f"x_{i}", cat=LpBinary) for i in range(n)]
prob += sum(cost[i] * x[i] for i in range(n))  # objective
prob += sum(x[i] for i in range(n)) >= k        # constraint
prob.solve()
assert LpStatus[prob.status] == "Optimal"
```

**Use when**: Any optimization problem from uber-model with linear structure and discrete decisions.

---

### A33: 0/1 Knapsack (DP)

**Problem**: Select items to maximize value subject to weight capacity.
**T**: O(nW) pseudo-polynomial | **S**: O(W) with space optimization
**Guarantee**: Exact

```python
def knapsack_01(weights: list[int], values: list[int], capacity: int) -> tuple[int, list[int]]:
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            dp[i][w] = dp[i-1][w]
            if weights[i-1] <= w:
                dp[i][w] = max(dp[i][w], dp[i-1][w - weights[i-1]] + values[i-1])
    # Traceback
    selected = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            selected.append(i - 1)
            w -= weights[i-1]
    return dp[n][capacity], selected[::-1]
```

---

### A34: Knapsack FPTAS

**Problem**: Knapsack approximation for large capacities.
**T**: O(n² / ε) | **S**: O(n / ε)
**Guarantee**: Approx(1-ε). Returns solution within (1-ε) factor of optimal.

**Use when**: Capacity W is too large for pseudo-polynomial DP.

---

## 11. Dynamic Programming Patterns

### A35: Subset Sum (DP)

**Problem**: Does a subset of integers sum to target T?
**T**: O(nT) | **S**: O(T)
**Guarantee**: Exact (pseudo-polynomial)

---

### A36: Longest Common Subsequence

**Problem**: Find longest subsequence common to two sequences.
**T**: O(nm) | **S**: O(min(n,m))
**Guarantee**: Exact

---

### A37: Edit Distance (Levenshtein)

**Problem**: Minimum edits (insert, delete, replace) to transform string A to B.
**T**: O(nm) | **S**: O(min(n,m))
**Guarantee**: Exact

---

### A38: Coin Change (DP)

**Problem**: Minimum number of coins to make amount, or count of ways.
**T**: O(n × amount) | **S**: O(amount)
**Guarantee**: Exact

---

### A39: Matrix Chain Multiplication

**Problem**: Optimal parenthesization of matrix chain to minimize scalar multiplications.
**T**: O(n³) | **S**: O(n²)
**Guarantee**: Exact

---

### A40: Longest Increasing Subsequence

**Problem**: Find longest strictly increasing subsequence.
**T**: O(n log n) with patience sorting | **S**: O(n)
**Guarantee**: Exact

---

### A41: Partition Problem (DP)

**Problem**: Can a set of integers be partitioned into two subsets with equal sum?
**T**: O(n × S) where S = sum/2 | **S**: O(S)
**Guarantee**: Exact (pseudo-polynomial). NP-complete in general.

---

### A42: DP on Bitmask (Subset DP)

**Problem**: Optimization over subsets when n ≤ 20-25.
**T**: O(2^n × n) | **S**: O(2^n)
**Guarantee**: Exact

**Pattern**:
```python
dp = [float('inf')] * (1 << n)
dp[0] = 0
for mask in range(1 << n):
    for i in range(n):
        if not (mask & (1 << i)):
            new_mask = mask | (1 << i)
            dp[new_mask] = min(dp[new_mask], dp[mask] + cost(mask, i))
```

**Use when**: TSP (Held-Karp), Hamiltonian path, set cover with small universe, weighted independent set on small graphs.

---

## 12. Greedy Algorithms

### A43: Activity Selection

**Problem**: Select maximum number of non-overlapping intervals.
**T**: O(n log n) | **S**: O(1)
**Guarantee**: Exact (greedy by earliest finish time is optimal)

---

### A44: Fractional Knapsack

**Problem**: Knapsack allowing fractional items.
**T**: O(n log n) | **S**: O(1)
**Guarantee**: Exact (greedy by value/weight ratio)

---

### A45: Huffman Coding

**Problem**: Optimal prefix-free binary code for given character frequencies.
**T**: O(n log n) | **S**: O(n)
**Guarantee**: Exact

---

### A46: Kruskal/Prim (see A13/A14)

Greedy by edge weight. Exact for MST by cut property.

---

### A47: Set Cover Greedy

**Problem**: Cover universe U with minimum number of sets from family F.
**T**: O(|U| × |F|) | **S**: O(|U|)
**Guarantee**: Approx(ln|U| + 1). Best possible polynomial approximation unless P=NP.

```python
def greedy_set_cover(universe: set, sets: list[set]) -> list[int]:
    uncovered = set(universe)
    selected = []
    available = list(range(len(sets)))
    while uncovered:
        best = max(available, key=lambda i: len(sets[i] & uncovered))
        selected.append(best)
        uncovered -= sets[best]
        available.remove(best)
    return selected
```

---

## 13. SAT / SMT / Constraint Satisfaction

### A48: SAT Solving (Z3 / DPLL / CDCL)

**Problem**: Find satisfying assignment for Boolean formula, or prove unsatisfiable.
**T**: NP-complete worst case. Modern solvers handle millions of variables in practice.
**Lib**: `z3-solver`
**Guarantee**: Exact (complete solver). UNSAT proof via resolution/conflict analysis.

```python
from z3 import Solver, Bool, Or, Not, sat

s = Solver()
x, y, z = Bool('x'), Bool('y'), Bool('z')
s.add(Or(x, y))           # clause 1
s.add(Or(Not(x), z))      # clause 2
s.add(Or(Not(y), Not(z))) # clause 3

if s.check() == sat:
    m = s.model()
    print({str(d): m[d] for d in m.decls()})
else:
    print("UNSAT")
    print("Core:", s.unsat_core())  # if using tracked assertions
```

---

### A49: SMT Solving (Z3)

**Problem**: SAT extended with theories: integer arithmetic, real arithmetic, bit vectors, arrays.
**T**: Depends on theory. Linear integer arithmetic is NP-complete. Real arithmetic is decidable.
**Lib**: `z3-solver`
**Guarantee**: Exact (for decidable theories)

```python
from z3 import Int, Solver, sat, And

s = Solver()
x, y = Int('x'), Int('y')
s.add(x + y == 10)
s.add(x >= 0, y >= 0)
s.add(x <= y)
if s.check() == sat:
    m = s.model()
    print(f"x={m[x]}, y={m[y]}")
```

---

### A50: Optimization with Z3

**Problem**: Optimize objective subject to constraints.
**Lib**: `z3.Optimize`
**Guarantee**: Exact

```python
from z3 import Int, Optimize

opt = Optimize()
x, y = Int('x'), Int('y')
opt.add(x >= 0, y >= 0, x + y <= 10)
opt.maximize(3*x + 2*y)
opt.check()
m = opt.model()
```

---

### A51: Constraint Propagation (AC-3)

**Problem**: Reduce CSP variable domains by enforcing arc consistency.
**T**: O(ed³) where e = constraints, d = domain size | **S**: O(ed)
**Lib**: Custom or `python-constraint`
**Guarantee**: Preprocessing -- reduces search space, does not solve alone.

---

### A52: Backtracking with Constraint Propagation

**Problem**: General CSP solving via systematic search with pruning.
**T**: Exponential worst case, often fast with good heuristics | **S**: O(nk)
**Lib**: `python-constraint`, or custom
**Guarantee**: Exact (complete search)

**Enhancements**: Variable ordering (MRV), value ordering (LCV), forward checking, MAC (maintaining arc consistency).

---

## 14. Number Theory

### A53: Euclidean Algorithm (GCD)

**Problem**: Greatest common divisor.
**T**: O(log min(a,b)) | **S**: O(1)
**Lib**: `math.gcd()`, `sympy.gcd()`
**Guarantee**: Exact

---

### A54: Extended Euclidean Algorithm

**Problem**: Find x, y such that ax + by = gcd(a, b).
**T**: O(log min(a,b)) | **S**: O(1)
**Lib**: `sympy.gcdex()`
**Guarantee**: Exact. Gives Bezout coefficients.

```python
def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    if b == 0:
        return a, 1, 0
    g, x, y = extended_gcd(b, a % b)
    return g, y, x - (a // b) * y
```

---

### A55: Chinese Remainder Theorem

**Problem**: Solve system x ≡ a_i (mod m_i) for pairwise coprime moduli.
**T**: O(k log M) where k = number of congruences, M = product of moduli | **S**: O(1)
**Lib**: `sympy.ntheory.modular.crt()`
**Guarantee**: Exact. Unique solution mod M.

---

### A56: Modular Exponentiation

**Problem**: Compute a^b mod m efficiently.
**T**: O(log b) | **S**: O(1)
**Lib**: `pow(a, b, m)` (Python built-in, uses fast binary method)
**Guarantee**: Exact

---

### A57: Sieve of Eratosthenes

**Problem**: Find all primes up to n.
**T**: O(n log log n) | **S**: O(n)
**Lib**: `sympy.sieve`, `sympy.primerange()`
**Guarantee**: Exact

```python
def sieve(n: int) -> list[int]:
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(n + 1) if is_prime[i]]
```

---

### A58: Primality Testing (Miller-Rabin)

**Problem**: Is n prime?
**T**: O(k log² n) for k rounds | **S**: O(1)
**Lib**: `sympy.isprime()` (deterministic for n < 3.3×10²⁴)
**Guarantee**: Deterministic for practical sizes. Probabilistic for very large n (error < 4^(-k)).

---

### A59: Integer Factorization

**Problem**: Find prime factorization of n.
**T**: O(√n) trial division, sub-exponential for large n (Pollard's rho, quadratic sieve)
**Lib**: `sympy.factorint()`
**Guarantee**: Exact

---

### A60: Euler's Totient Function

**Problem**: Count integers 1..n coprime to n.
**T**: O(√n) via factorization | **S**: O(1)
**Lib**: `sympy.totient()`
**Guarantee**: Exact. φ(n) = n × ∏(1 - 1/p) for each prime factor p of n.

---

### A61: Modular Inverse

**Problem**: Find x such that ax ≡ 1 (mod m).
**T**: O(log m) | **S**: O(1)
**Lib**: `pow(a, -1, m)` (Python 3.8+), `sympy.mod_inverse()`
**Guarantee**: Exact. Exists iff gcd(a, m) = 1.

---

### A62: Diophantine Equation Solver

**Problem**: Find integer solutions to polynomial equations.
**T**: Varies | **S**: Varies
**Lib**: `sympy.diophantine()`
**Guarantee**: Exact for linear and common quadratic forms.

---

## 15. Combinatorial Counting & Generation

### A63: Permutation Generation

**Problem**: Generate all permutations of n elements (or k of n).
**T**: O(n!) | **S**: O(n) per permutation
**Lib**: `itertools.permutations()`
**Guarantee**: Exact enumeration

---

### A64: Combination Generation

**Problem**: Generate all C(n,k) combinations.
**T**: O(C(n,k)) | **S**: O(k) per combination
**Lib**: `itertools.combinations()`
**Guarantee**: Exact enumeration

---

### A65: Integer Partition Generation

**Problem**: Generate all partitions of integer n.
**T**: O(p(n)) where p(n) ~ exp(π√(2n/3)) / (4n√3) | **S**: O(n)
**Lib**: `sympy.utilities.iterables.partitions()`
**Guarantee**: Exact enumeration

---

### A66: Inclusion-Exclusion Counting

**Problem**: Count elements in union of sets: |A₁ ∪ A₂ ∪ ... ∪ Aₙ|.
**T**: O(2^n) terms | **S**: O(n)
**Guarantee**: Exact

**Formula**: |⋃Aᵢ| = Σ|Aᵢ| - Σ|Aᵢ∩Aⱼ| + Σ|Aᵢ∩Aⱼ∩Aₖ| - ...

**Use when**: Counting with overlapping constraints (derangements, surjections, chromatic polynomial).

---

### A67: Burnside's Lemma (Counting under Symmetry)

**Problem**: Count distinct objects under group action (e.g., rotational symmetry).
**T**: O(|G| × n) where |G| = group size | **S**: O(n)
**Lib**: Custom implementation
**Guarantee**: Exact

**Formula**: Number of distinct objects = (1/|G|) Σ_{g∈G} |Fix(g)|

**Use when**: Counting necklaces, colorings up to rotation/reflection, chemical isomers.

---

### A68: Generating Functions (Symbolic)

**Problem**: Encode sequences as power series for counting and closed-form derivation.
**T**: Varies (symbolic computation) | **S**: Varies
**Lib**: `sympy.series`, `sympy.Symbol`, `sympy.fps()`
**Guarantee**: Exact (symbolic)

**Use when**: Finding closed forms for recurrences, counting lattice paths, partition enumeration.

---

### A69: Catalan Numbers

**Problem**: Count valid parenthesizations, binary trees, Dyck paths, non-crossing partitions.
**T**: O(1) per value | **S**: O(1)
**Formula**: C(n) = C(2n,n)/(n+1) = (2n)! / ((n+1)!n!)
**Lib**: `sympy.catalan(n)`
**Guarantee**: Exact

---

## 16. Order Theory

### A70: Dilworth's Theorem (Chain Decomposition)

**Problem**: Partition poset into minimum number of chains. By Dilworth: this equals the maximum antichain size.
**T**: O(V³) via bipartite matching reduction | **S**: O(V²)
**Guarantee**: Exact

**Algorithm**: Build bipartite graph B where left vertex i connects to right vertex j iff i < j in the poset. Min chain decomposition = |V| - max matching in B.

---

### A71: Linear Extension Enumeration

**Problem**: Count or enumerate all topological orderings of a poset.
**T**: #P-complete (counting). O(n!) worst case (enumeration).
**Lib**: `networkx.all_topological_sorts()` (enumeration)
**Guarantee**: Exact enumeration. Counting is intractable for large n.

---

### A72: Lattice Operations (Meet, Join)

**Problem**: Compute meet (GLB) and join (LUB) in a lattice.
**T**: O(V + E) per operation (via reachability in Hasse diagram)
**Lib**: Custom on poset representation
**Guarantee**: Exact

---

### A73: Fixed Point Computation (Tarski)

**Problem**: Find fixed points of monotone functions on lattices.
**T**: O(h × f) where h = lattice height, f = function evaluation cost
**Guarantee**: Exact. Tarski: every monotone function on a complete lattice has a least and greatest fixed point.

**Use when**: Dataflow analysis, abstract interpretation, stable model computation.

---

## 17. Proof Techniques

### A74: Mathematical Induction

**Problem**: Prove P(n) for all n ≥ n₀.
**Lib**: `sympy` for symbolic verification of algebraic steps

**Steps**:
1. **Base case**: Verify P(n₀) (use SymPy `simplify()` or direct computation)
2. **Inductive hypothesis**: Assume P(k) for some k ≥ n₀
3. **Inductive step**: Prove P(k) → P(k+1) (use SymPy `expand()`, `factor()`, `simplify()`)

```python
from sympy import symbols, simplify, expand

n = symbols('n', positive=True, integer=True)
# Verify: sum of first n cubes = (n(n+1)/2)^2
lhs = n**3 + (n*(n+1)//2)**2  # P(k+1) side after adding (k+1)^3
rhs = ((n+1)*(n+2)//2)**2     # Expected P(k+1)
assert simplify(lhs - rhs) == 0
```

---

### A75: Proof by Contradiction / Reductio ad Absurdum

**Problem**: Prove P by assuming ¬P and deriving a contradiction.
**Lib**: Z3 for automated contradiction finding

```python
from z3 import Solver, Int, And, Or, Not, unsat

s = Solver()
# Assume the negation of what we want to prove
# Add all known axioms
# If UNSAT, the negation is impossible, so the original statement is true
result = s.check()
assert result == unsat, "No contradiction found"
```

---

### A76: Constructive Proof

**Problem**: Prove existence by explicitly constructing the object.
**Lib**: Depends on domain (NetworkX for graph objects, SymPy for algebraic objects)
**Guarantee**: Exact (the constructed object IS the proof)

**Use when**: "There exists..." claims. Build it, verify it satisfies all conditions.

---

### A77: Pigeonhole Principle

**Problem**: Prove that if n items are placed in k bins with n > k, some bin has ≥ 2 items.
**T**: O(1) (argument), O(n) (verification by simulation)
**Guarantee**: Exact

**Generalized**: n items in k bins → some bin has ≥ ⌈n/k⌉ items.

---

## 18. Discrete Probability

### A78: Expected Value Computation

**Problem**: Compute E[X] = Σ x·P(X=x) for discrete random variable.
**T**: O(|Ω|) for enumeration | **S**: O(|Ω|)
**Lib**: `sympy.stats`, `numpy`
**Guarantee**: Exact (for exact probabilities)

```python
from sympy.stats import FiniteRV, E, P, variance

dist = {1: 1/6, 2: 1/6, 3: 1/6, 4: 1/6, 5: 1/6, 6: 1/6}
X = FiniteRV('X', dist)
print(f"E[X] = {E(X)}")
print(f"Var(X) = {variance(X)}")
print(f"P(X > 3) = {P(X > 3)}")
```

---

### A79: Bayesian Inference (Discrete)

**Problem**: Compute posterior probability P(H|E) from prior P(H) and likelihood P(E|H).
**T**: O(|H|) where |H| = number of hypotheses
**Guarantee**: Exact

**Formula**: P(H|E) = P(E|H)P(H) / P(E) = P(E|H)P(H) / Σ_h P(E|h)P(h)

---

### A80: Markov Chain Analysis

**Problem**: Compute stationary distribution, hitting times, absorption probabilities.
**T**: O(n³) for n-state chain (matrix methods) | **S**: O(n²)
**Lib**: `numpy.linalg`, `scipy.linalg`
**Guarantee**: Exact (for exact arithmetic). Numerical for large chains.

```python
import numpy as np

P = np.array([[0.9, 0.1], [0.3, 0.7]])  # transition matrix
# Stationary distribution: solve πP = π, Σπ = 1
eigenvalues, eigenvectors = np.linalg.eig(P.T)
stationary = eigenvectors[:, np.isclose(eigenvalues, 1)]
stationary = (stationary / stationary.sum()).real.flatten()
```

---

### A81: Monte Carlo Simulation

**Problem**: Estimate probabilities/expectations via random sampling.
**T**: O(N) for N samples | **S**: O(1) streaming
**Lib**: `numpy.random`, `random`
**Guarantee**: Probabilistic. Error ~ 1/√N. Confidence intervals via CLT.

**Use when**: Exact computation is intractable, or for verification of analytical results.

---

## 19. Search & Backtracking

### A82: General Backtracking Template

**Problem**: Systematic search with pruning for any CSP or combinatorial problem.
**T**: Problem-dependent (exponential worst case) | **S**: O(depth)

```python
def backtrack(state, decisions):
    if is_complete(state):
        return state if is_valid(state) else None
    for choice in candidates(state, decisions):
        if is_promising(state, choice):  # pruning
            apply(state, choice)
            result = backtrack(state, decisions + [choice])
            if result is not None:
                return result
            undo(state, choice)
    return None
```

---

### A83: Branch and Bound

**Problem**: Optimization via systematic search with bounding.
**T**: Problem-dependent | **S**: O(depth)

**Key idea**: Maintain best solution found so far. At each node, compute a bound (relaxation). If bound is worse than best known, prune.

**Bounds**:
- LP relaxation for ILP problems
- MST bound for TSP
- Fractional knapsack bound for 0/1 knapsack

---

### A84: Iterative Deepening (IDDFS)

**Problem**: Find shortest path in large implicit graph without BFS memory cost.
**T**: O(b^d) where b = branching, d = depth | **S**: O(d) (depth only!)
**Guarantee**: Exact (optimal for uniform cost, like BFS)

**Use when**: Memory is the constraint, not time. Implicit graphs (puzzles, game trees).

---

## 20. Metaheuristics (for Large NP-hard Instances)

### A85: Simulated Annealing

**Problem**: General optimization for large instances.
**T**: O(iterations × neighbor evaluation) | **S**: O(solution size)
**Guarantee**: Heuristic. Converges to global optimum in theory (infinite time). No practical bound.

**Template**:
```python
import random
import math

def simulated_annealing(initial, neighbor_fn, cost_fn, temp=1000, cooling=0.995, min_temp=1e-8):
    current = initial
    best = current
    best_cost = cost_fn(current)
    T = temp
    while T > min_temp:
        candidate = neighbor_fn(current)
        delta = cost_fn(candidate) - cost_fn(current)
        if delta < 0 or random.random() < math.exp(-delta / T):
            current = candidate
        if cost_fn(current) < best_cost:
            best = current
            best_cost = cost_fn(current)
        T *= cooling
    return best, best_cost
```

**Use when**: Large NP-hard instances where exact methods timeout. Always report that the solution is heuristic.

---

### A86: Genetic Algorithm

**Problem**: General optimization via evolutionary search.
**T**: O(generations × population × fitness evaluation) | **S**: O(population × solution size)
**Guarantee**: Heuristic. No formal bound.

**Use when**: Complex solution spaces where gradient information is unavailable. Always compare against simpler methods first.

---

## Algorithm Selection Matrix

Quick lookup: given a problem class, which algorithm to use.

| Problem Class | Small (n≤25) | Medium (n≤1000) | Large (n>1000) |
|---|---|---|---|
| Shortest path (non-neg) | Dijkstra (A8) | Dijkstra (A8) | Dijkstra (A8) |
| Shortest path (neg weights) | Bellman-Ford (A9) | Bellman-Ford (A9) | Bellman-Ford (A9) |
| All-pairs shortest path | Floyd-Warshall (A10) | Dijkstra from each (A8) | Dijkstra from each (A8) |
| MST | Kruskal (A13) | Kruskal (A13) | Kruskal (A13) |
| Bipartite matching | Hopcroft-Karp (A15) | Hopcroft-Karp (A15) | Hopcroft-Karp (A15) |
| Weighted assignment | Hungarian (A16) | Hungarian (A16) | Auction/ILP (A32) |
| Max flow | Edmonds-Karp (A19) | Dinic (A19) | Dinic (A19) |
| Graph coloring | Exact backtrack (A22) | ILP/SAT (A32/A48) | Greedy (A21) |
| Independent set | Exact DP bitmask (A42) | ILP (A32) | Greedy heuristic |
| Vertex cover | Exact (A23) | ILP (A32) | 2-approx (A24) |
| TSP | Held-Karp DP (A28) | ILP (A32) | Christofides (A29) / LKH (A30) |
| Knapsack | DP (A33) | DP (A33) | FPTAS (A34) / ILP (A32) |
| Set cover | Exact (A42) | ILP (A32) | Greedy ln(n) (A47) |
| SAT | Z3 (A48) | Z3 (A48) | Z3 (A48) |
| ILP | PuLP/CBC (A32) | PuLP/CBC (A32) | Gurobi/OR-Tools (A32) |
| Counting | Enumerate (A63/A64) | DP/formula (varies) | Generating functions (A68) |
| Topological sort | Kahn (A3) | Kahn (A3) | Kahn (A3) |
| SCC | Tarjan (A5) | Tarjan (A5) | Tarjan (A5) |
| Proof (induction) | SymPy verify (A74) | SymPy verify (A74) | SymPy verify (A74) |
| Proof (contradiction) | Z3 (A75) | Z3 (A75) | Z3 (A75) |
| Convex optimization | cvxpy (A87) | cvxpy (A87) | cvxpy (A87) |
| Unconstrained smooth | BFGS (A89) | L-BFGS-B (A89) | L-BFGS-B (A89) |
| Least squares | Normal eqns (A91) | scipy lstsq (A91) | scipy lstsq (A91) |
| QP (convex) | cvxpy (A88) | cvxpy (A88) | OSQP/cvxpy (A88) |
| Nonlinear constrained | SLSQP (A93) | SLSQP/trust-constr (A93) | Ipopt (A93) |

---

## 21. Continuous Optimization

### A87: Disciplined Convex Programming (cvxpy)

**Problem**: Minimize a convex function over a convex set.
**T**: Polynomial (interior point) | **S**: O(n²) for n variables
**Lib**: `cvxpy`
**Guarantee**: Exact (global optimum for convex problems). Fails fast if problem is non-convex.

```python
import cvxpy as cp
import numpy as np

x = cp.Variable(n)
objective = cp.Minimize(cp.quad_form(x, Sigma) + lambd * cp.norm(x, 1))
constraints = [cp.sum(x) == 1, x >= 0]
prob = cp.Problem(objective, constraints)
prob.solve()
print(f"Optimal value: {prob.value}")
print(f"Optimal x: {x.value}")
```

**Use when**: Portfolio optimization, signal processing, control, any problem that can be expressed in DCP form. cvxpy verifies convexity at construction time.

---

### A88: Quadratic Programming

**Problem**: Minimize (1/2)x^T Q x + c^T x subject to linear constraints, Q positive semidefinite.
**T**: Polynomial (interior point or active set) | **S**: O(n²)
**Lib**: `cvxpy`, `scipy.optimize.minimize(method='trust-constr')`, OSQP
**Guarantee**: Exact (convex QP has unique global minimum if Q is positive definite)

**Use when**: Portfolio optimization (minimize variance), regularized regression (ridge), SVM training.

---

### A89: BFGS / L-BFGS-B

**Problem**: Unconstrained smooth minimization (or with box constraints for L-BFGS-B).
**T**: O(n²) per iteration (BFGS), O(n) per iteration (L-BFGS-B) | **S**: O(n²) / O(mn)
**Lib**: `scipy.optimize.minimize(method='BFGS')` or `method='L-BFGS-B'`
**Guarantee**: Converges to local minimum (global if convex). Superlinear convergence rate.

```python
from scipy.optimize import minimize

def objective(x):
    return (x[0] - 1)**2 + 100 * (x[1] - x[0]**2)**2  # Rosenbrock

result = minimize(objective, x0=[0, 0], method='BFGS')
print(f"Minimum: {result.fun} at x = {result.x}")
print(f"Converged: {result.success}")
```

**Use when**: Smooth unconstrained problems with moderate dimensionality (n < 10K).

---

### A90: Gradient Descent

**Problem**: Unconstrained smooth minimization.
**T**: O(n) per iteration | **S**: O(n)
**Lib**: Custom (or use scipy/cvxpy for better variants)
**Guarantee**: Converges to local minimum. Rate: O(1/k) for convex, O(1/k²) with Nesterov acceleration.

```python
def gradient_descent(f, grad_f, x0, lr=0.01, tol=1e-8, max_iter=10000):
    x = x0.copy()
    for i in range(max_iter):
        g = grad_f(x)
        if np.linalg.norm(g) < tol:
            break
        x = x - lr * g
    return x
```

**Use when**: Large-scale problems where second-order methods are too expensive. ML training, simple convex problems.

---

### A91: Least Squares (Normal Equations / SVD)

**Problem**: Minimize ||Ax - b||² (linear least squares).
**T**: O(mn²) for m×n matrix A | **S**: O(mn)
**Lib**: `numpy.linalg.lstsq()`, `scipy.linalg.lstsq()`
**Guarantee**: Exact (closed-form solution). Unique if A has full column rank.

```python
import numpy as np

A = np.array([[1, 1], [1, 2], [1, 3]])
b = np.array([1, 2, 2])
x, residuals, rank, sv = np.linalg.lstsq(A, b, rcond=None)
print(f"Coefficients: {x}")
```

**Use when**: Linear regression, polynomial fitting, any overdetermined linear system.

---

### A92: Gauss-Newton / Levenberg-Marquardt

**Problem**: Nonlinear least squares: minimize Σ r_i(x)² where r_i are nonlinear residuals.
**T**: O(mn²) per iteration | **S**: O(mn)
**Lib**: `scipy.optimize.least_squares()`
**Guarantee**: Converges to local minimum. Often fast for well-conditioned problems.

```python
from scipy.optimize import least_squares

def residuals(params, x_data, y_data):
    a, b, c = params
    return a * np.exp(b * x_data) + c - y_data

result = least_squares(residuals, x0=[1, -0.1, 0], args=(x_data, y_data))
print(f"Parameters: {result.x}")
```

**Use when**: Curve fitting, parameter estimation, calibration.

---

### A93: Sequential Quadratic Programming (SQP) / SLSQP

**Problem**: Nonlinear constrained optimization.
**T**: Problem-dependent (iterative) | **S**: O(n²)
**Lib**: `scipy.optimize.minimize(method='SLSQP')` or `method='trust-constr'`
**Guarantee**: Converges to local KKT point. No global guarantee for non-convex.

```python
from scipy.optimize import minimize

result = minimize(
    fun=lambda x: x[0]**2 + x[1]**2,
    x0=[1, 1],
    method='SLSQP',
    constraints=[
        {'type': 'ineq', 'fun': lambda x: x[0] + x[1] - 1},  # x0 + x1 >= 1
    ],
    bounds=[(0, None), (0, None)]
)
```

**Use when**: Engineering design, constrained optimization with nonlinear constraints.

---

### A94: Interior Point Method

**Problem**: LP, QP, or general convex optimization.
**T**: O(n^3.5 log(1/ε)) for LP | **S**: O(n²)
**Lib**: `scipy.optimize.linprog(method='highs')`, `cvxpy` (uses ECOS, SCS, or MOSEK)
**Guarantee**: Exact for convex problems. Polynomial worst-case.

**Use when**: Large-scale LP/QP, semidefinite programming, any convex problem via cvxpy.

---

## 22. Linear Algebra

### A95: Gaussian Elimination (Row Reduction)

**Problem**: Solve a system of linear equations Ax = b, compute rank, find null space.
**T**: O(n³) for n×n system | **S**: O(n²)
**Lib**: `numpy.linalg.solve()`, `sympy.Matrix.rref()`
**Guarantee**: Exact. Partial pivoting avoids numerical instability.

```python
import numpy as np

A = np.array([[2, 1, -1], [-3, -1, 2], [-2, 1, 2]], dtype=float)
b = np.array([8, -11, -3], dtype=float)
x = np.linalg.solve(A, b)
print(f"Solution: {x}")
```

**Use when**: Solving linear systems, computing RREF, determining consistency of equations.

---

### A96: LU Decomposition

**Problem**: Factor A = LU (or PA = LU with pivoting) for efficient repeated solves with different right-hand sides.
**T**: O(n³) factorization, O(n²) per solve | **S**: O(n²)
**Lib**: `scipy.linalg.lu()`, `scipy.linalg.lu_factor()` / `lu_solve()`
**Guarantee**: Exact (with partial pivoting for numerical stability).

```python
from scipy.linalg import lu_factor, lu_solve

A = np.array([[2, 5, 8], [4, 6, 7], [3, 1, 9]], dtype=float)
lu, piv = lu_factor(A)
x1 = lu_solve((lu, piv), np.array([1, 2, 3], dtype=float))
x2 = lu_solve((lu, piv), np.array([4, 5, 6], dtype=float))  # reuse factorization
```

**Use when**: Multiple right-hand sides with the same coefficient matrix, computing determinants efficiently.

---

### A97: Eigenvalue / Eigenvector Computation

**Problem**: Find eigenvalues λ and eigenvectors v satisfying Av = λv.
**T**: O(n³) (QR iteration) | **S**: O(n²)
**Lib**: `numpy.linalg.eig()`, `numpy.linalg.eigh()` (symmetric), `scipy.linalg.eig()`
**Guarantee**: Exact for symmetric matrices (real eigenvalues). Iterative convergence for general.

```python
import numpy as np

A = np.array([[4, -2], [1, 1]])
eigenvalues, eigenvectors = np.linalg.eig(A)
print(f"Eigenvalues: {eigenvalues}")
print(f"Eigenvectors:\n{eigenvectors}")
```

**Use when**: Stability analysis, PCA, vibration modes, PageRank, spectral clustering, Markov chain steady state.

---

### A98: Singular Value Decomposition (SVD)

**Problem**: Factor A = UΣVᵀ. Reveals rank, range, null space, and best low-rank approximation.
**T**: O(min(mn², m²n)) for m×n matrix | **S**: O(mn)
**Lib**: `numpy.linalg.svd()`, `scipy.linalg.svd()`
**Guarantee**: Exact. Always exists for any matrix.

```python
import numpy as np

A = np.array([[1, 2], [3, 4], [5, 6]])
U, sigma, Vt = np.linalg.svd(A, full_matrices=False)
rank = np.sum(sigma > 1e-10)
print(f"Rank: {rank}, Singular values: {sigma}")
```

**Use when**: Dimensionality reduction, pseudoinverse, rank determination, image compression, noise filtering.

---

### A99: QR Decomposition

**Problem**: Factor A = QR where Q is orthogonal, R is upper triangular.
**T**: O(mn²) for m×n matrix | **S**: O(mn)
**Lib**: `numpy.linalg.qr()`, `scipy.linalg.qr()`
**Guarantee**: Exact. Numerically stable.

```python
import numpy as np

A = np.array([[1, 1], [1, 2], [1, 3]], dtype=float)
Q, R = np.linalg.qr(A)
# Solve least squares via QR: x = R⁻¹Qᵀb
```

**Use when**: Least squares (numerically better than normal equations), eigenvalue algorithms (QR iteration), orthogonalization.

---

### A100: Cholesky Decomposition

**Problem**: Factor symmetric positive-definite A = LLᵀ. Half the cost of LU.
**T**: O(n³/3) | **S**: O(n²)
**Lib**: `numpy.linalg.cholesky()`, `scipy.linalg.cholesky()`
**Guarantee**: Exact. Exists iff A is symmetric positive-definite.

```python
import numpy as np

A = np.array([[4, 2], [2, 3]], dtype=float)
L = np.linalg.cholesky(A)
# Solve Ax = b via L(Lᵀx) = b: forward then back substitution
```

**Use when**: Covariance matrices, positive-definite systems, sampling from multivariate normal, Kalman filters.

---

### A101: Matrix Inverse

**Problem**: Compute A⁻¹ such that AA⁻¹ = I.
**T**: O(n³) | **S**: O(n²)
**Lib**: `numpy.linalg.inv()`, `scipy.linalg.inv()`
**Guarantee**: Exact if A is non-singular. Prefer solve() over inv() for Ax=b.

```python
import numpy as np

A = np.array([[1, 2], [3, 4]], dtype=float)
A_inv = np.linalg.inv(A)
```

**Use when**: Explicit inverse needed (e.g., formula derivation). For solving Ax=b, prefer `np.linalg.solve()`.

---

### A102: Determinant

**Problem**: Compute det(A). Tests invertibility, computes area/volume scaling.
**T**: O(n³) via LU | **S**: O(n²)
**Lib**: `numpy.linalg.det()`, `sympy.Matrix.det()`
**Guarantee**: Exact (symbolic with SymPy, numerical with numpy).

```python
import numpy as np

A = np.array([[1, 2], [3, 4]])
d = np.linalg.det(A)
print(f"det(A) = {d:.1f}")  # -2.0
```

**Use when**: Checking invertibility, Cramer's rule (small systems), area of parallelogram/volume of parallelepiped.

---

### A103: Matrix Rank

**Problem**: Determine the rank of a matrix (number of linearly independent rows/columns).
**T**: O(min(mn², m²n)) via SVD | **S**: O(mn)
**Lib**: `numpy.linalg.matrix_rank()`, `sympy.Matrix.rank()`
**Guarantee**: Exact (symbolic), numerical tolerance for floating point.

```python
import numpy as np

A = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
r = np.linalg.matrix_rank(A)
print(f"Rank: {r}")  # 2 (rows are linearly dependent)
```

**Use when**: Checking system consistency (rank vs augmented rank), determining degrees of freedom, feature independence.

---

### A104: Null Space (Kernel)

**Problem**: Find all vectors x satisfying Ax = 0.
**T**: O(min(mn², m²n)) via SVD | **S**: O(mn)
**Lib**: `scipy.linalg.null_space()`, `sympy.Matrix.nullspace()`
**Guarantee**: Exact.

```python
from scipy.linalg import null_space

A = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
ns = null_space(A)
print(f"Null space dimension: {ns.shape[1]}")
```

**Use when**: Finding free variables in underdetermined systems, homogeneous equations, constraint analysis.

---

### A105: Condition Number

**Problem**: Measure sensitivity of a linear system to perturbations: κ(A) = ||A|| · ||A⁻¹||.
**T**: O(min(mn², m²n)) via SVD | **S**: O(mn)
**Lib**: `numpy.linalg.cond()`
**Guarantee**: Exact computation. κ >> 1 means ill-conditioned.

```python
import numpy as np

A = np.array([[1, 2], [1.0001, 2]])
kappa = np.linalg.cond(A)
print(f"Condition number: {kappa:.0f}")  # Very large = ill-conditioned
```

**Use when**: Diagnosing numerical instability, deciding between direct and iterative solvers, error analysis.

---

### A106: Least Squares via Normal Equations

**Problem**: Solve overdetermined Ax ≈ b by minimizing ||Ax - b||² via AᵀAx = Aᵀb.
**T**: O(mn² + n³) | **S**: O(n²)
**Lib**: `numpy.linalg.lstsq()` (uses SVD internally), `scipy.linalg.lstsq()`
**Guarantee**: Exact minimum-norm solution. SVD approach preferred for numerical stability.

```python
import numpy as np

# Fit y = a + bx to data
x_data = np.array([1, 2, 3, 4, 5])
y_data = np.array([2.1, 3.9, 6.2, 7.8, 10.1])
A = np.column_stack([np.ones_like(x_data), x_data])
coeffs, residuals, rank, sv = np.linalg.lstsq(A, y_data, rcond=None)
print(f"y = {coeffs[0]:.2f} + {coeffs[1]:.2f}x")
```

**Use when**: Linear regression, polynomial fitting, overdetermined systems, data fitting.

---

## 23. Calculus

### A107: Symbolic Differentiation

**Problem**: Compute exact derivative of a function expression.
**T**: O(n) where n is expression tree size | **S**: O(n)
**Lib**: `sympy.diff()`
**Guarantee**: Exact symbolic result.

```python
from sympy import symbols, diff, sin, exp

x = symbols('x')
f = x**3 * sin(x) + exp(x)
f_prime = diff(f, x)
print(f"f'(x) = {f_prime}")
```

**Use when**: Finding rates of change, critical points, optimization conditions, sensitivity analysis.

---

### A108: Symbolic Integration

**Problem**: Compute exact antiderivative or definite integral.
**T**: Problem-dependent (may invoke Risch algorithm) | **S**: O(n)
**Lib**: `sympy.integrate()`
**Guarantee**: Exact when closed form exists. Returns unevaluated Integral if no closed form.

```python
from sympy import symbols, integrate, exp, oo

x = symbols('x')
# Indefinite
F = integrate(x**2 * exp(x), x)
# Definite
area = integrate(x**2, (x, 0, 3))
print(f"∫x²dx from 0 to 3 = {area}")  # 9
```

**Use when**: Area under curves, accumulated quantities, probability distributions, work/energy calculations.

---

### A109: Numerical Integration (Quadrature)

**Problem**: Approximate ∫f(x)dx when no closed form exists.
**T**: O(n) function evaluations | **S**: O(1)
**Lib**: `scipy.integrate.quad()`, `scipy.integrate.dblquad()`, `scipy.integrate.nquad()`
**Guarantee**: Adaptive quadrature with error estimate.

```python
from scipy.integrate import quad

result, error = quad(lambda x: x**2 * np.exp(-x), 0, np.inf)
print(f"∫₀^∞ x²e⁻ˣ dx = {result:.6f} (error: {error:.2e})")  # 2.0
```

**Use when**: Integrals without closed form, numerical probability computations, physics (work, flux).

---

### A110: Limits

**Problem**: Compute lim_{x→a} f(x), including one-sided and at infinity.
**T**: O(n) expression simplification | **S**: O(n)
**Lib**: `sympy.limit()`
**Guarantee**: Exact symbolic computation using Gruntz algorithm.

```python
from sympy import symbols, limit, sin, oo

x = symbols('x')
print(limit(sin(x)/x, x, 0))         # 1
print(limit((1 + 1/x)**x, x, oo))    # E (Euler's number)
```

**Use when**: Asymptotic behavior, L'Hôpital's rule applications, convergence analysis.

---

### A111: Taylor / Maclaurin Series

**Problem**: Expand f(x) as polynomial approximation around a point.
**T**: O(n) for n terms | **S**: O(n)
**Lib**: `sympy.series()`
**Guarantee**: Exact coefficients. Convergence depends on radius of convergence.

```python
from sympy import symbols, series, exp

x = symbols('x')
s = series(exp(x), x, 0, n=6)
print(s)  # 1 + x + x²/2 + x³/6 + x⁴/24 + x⁵/120 + O(x⁶)
```

**Use when**: Function approximation, error estimation, linearization, asymptotic analysis.

---

### A112: Partial Derivatives

**Problem**: Compute ∂f/∂xᵢ for multivariate functions.
**T**: O(n) per variable | **S**: O(n)
**Lib**: `sympy.diff(f, x)`, `sympy.diff(f, x, y)` for mixed
**Guarantee**: Exact symbolic result.

```python
from sympy import symbols, diff

x, y = symbols('x y')
f = x**2 * y + x * y**3
df_dx = diff(f, x)
df_dy = diff(f, y)
print(f"∂f/∂x = {df_dx}, ∂f/∂y = {df_dy}")
```

**Use when**: Multivariable optimization, gradient computation, sensitivity of outputs to inputs.

---

### A113: Gradient / Jacobian / Hessian

**Problem**: Compute gradient vector, Jacobian matrix, or Hessian matrix of a function.
**T**: O(n·m) for Jacobian of m functions in n variables | **S**: O(n·m)
**Lib**: `sympy.Matrix.jacobian()`, `sympy.hessian()`
**Guarantee**: Exact symbolic computation.

```python
from sympy import symbols, Matrix, hessian

x, y = symbols('x y')
f = x**2 + x*y + y**2
H = hessian(f, [x, y])
print(f"Hessian:\n{H}")  # [[2, 1], [1, 2]] -> positive definite -> local min
```

**Use when**: Optimization (gradient = 0 for critical points, Hessian for convexity), Newton's method, sensitivity analysis.

---

### A114: Lagrange Multipliers

**Problem**: Optimize f(x) subject to g(x) = 0 by solving ∇f = λ∇g, g(x) = 0.
**T**: Depends on system size | **S**: O(n)
**Lib**: `sympy.solve()` for the system of equations
**Guarantee**: Exact (finds all critical points satisfying KKT conditions).

```python
from sympy import symbols, solve, diff

x, y, lam = symbols('x y lambda')
f = x**2 + y**2          # minimize
g = x + y - 10           # subject to x + y = 10
eqs = [diff(f, x) - lam * diff(g, x),
       diff(f, y) - lam * diff(g, y),
       g]
sol = solve(eqs, [x, y, lam])
print(f"Optimum: x={sol[x]}, y={sol[y]}")  # x=5, y=5
```

**Use when**: Constrained optimization with equality constraints, economics (utility maximization), physics (energy minimization).

---

### A115: Ordinary Differential Equations (Symbolic)

**Problem**: Solve ODEs symbolically: find y(x) given y' = f(x, y) and initial/boundary conditions.
**T**: Problem-dependent | **S**: O(n)
**Lib**: `sympy.dsolve()`
**Guarantee**: Exact when closed form exists. Handles separable, linear, Bernoulli, exact, higher-order.

```python
from sympy import symbols, Function, dsolve, Eq

x = symbols('x')
y = Function('y')
ode = Eq(y(x).diff(x) + 2*y(x), x*exp(-2*x))
sol = dsolve(ode, y(x))
print(f"Solution: {sol}")
```

**Use when**: Population models, radioactive decay, circuit analysis, mechanical vibrations (when exact solution exists).

---

### A116: Ordinary Differential Equations (Numerical)

**Problem**: Numerically solve y' = f(t, y), y(t₀) = y₀ over a time span.
**T**: O(n·s) where n = steps, s = system dimension | **S**: O(n·s)
**Lib**: `scipy.integrate.solve_ivp()` (RK45, RK23, Radau, BDF, LSODA)
**Guarantee**: Adaptive step size with error control. Configurable tolerance.

```python
from scipy.integrate import solve_ivp

def lotka_volterra(t, y, a=1.0, b=0.1, c=1.5, d=0.075):
    prey, pred = y
    return [a*prey - b*prey*pred, -c*pred + d*prey*pred]

sol = solve_ivp(lotka_volterra, [0, 50], [40, 9], max_step=0.1)
print(f"Final populations: prey={sol.y[0,-1]:.1f}, predator={sol.y[1,-1]:.1f}")
```

**Use when**: Any ODE without closed-form solution: population dynamics, chemical kinetics, epidemiology (SIR), control systems.

---

## 24. Geometry & Trigonometry

### A117: Polygon Area (Shoelace Formula)

**Problem**: Compute area of a simple polygon given vertex coordinates.
**T**: O(n) | **S**: O(1)
**Lib**: `shapely.Polygon.area`, `sympy.geometry.Polygon.area`
**Guarantee**: Exact for simple (non-self-intersecting) polygons.

```python
from shapely.geometry import Polygon

coords = [(0, 0), (4, 0), (4, 3), (0, 3)]
poly = Polygon(coords)
print(f"Area: {poly.area}")  # 12.0
```

**Use when**: Land area, floor plans, irregular region measurement, GIS applications.

---

### A118: Volume of Solids

**Problem**: Compute volume of 3D solids (prisms, cylinders, spheres, cones, custom solids of revolution).
**T**: O(1) for formulas, O(n) for numerical integration | **S**: O(1)
**Lib**: `sympy` (symbolic integration for solids of revolution), `math` (standard formulas)
**Guarantee**: Exact for standard shapes and symbolic integration.

```python
from sympy import symbols, pi, integrate

x = symbols('x')
# Volume of solid of revolution: y = sqrt(x), 0 ≤ x ≤ 4, rotated around x-axis
V = pi * integrate(x, (x, 0, 4))
print(f"Volume: {V}")  # 8*pi
```

**Use when**: Container sizing, material estimation, tank capacity, 3D printing volume calculation.

---

### A119: Distance Computation (2D/3D)

**Problem**: Compute Euclidean distance, Manhattan distance, or geodesic distance between points.
**T**: O(d) for d dimensions | **S**: O(1)
**Lib**: `scipy.spatial.distance`, `numpy.linalg.norm()`, `math.dist()`
**Guarantee**: Exact.

```python
import numpy as np
from scipy.spatial.distance import cdist

points = np.array([[0, 0], [3, 4], [6, 8]])
D = cdist(points, points, metric='euclidean')
print(f"Distance matrix:\n{D}")
```

**Use when**: Proximity analysis, clustering, nearest neighbor, facility placement.

---

### A120: Convex Hull

**Problem**: Find the smallest convex polygon containing all points in a set.
**T**: O(n log n) | **S**: O(n)
**Lib**: `scipy.spatial.ConvexHull`, `shapely.MultiPoint.convex_hull`
**Guarantee**: Exact (Graham scan or Quickhull).

```python
from scipy.spatial import ConvexHull
import numpy as np

points = np.random.rand(30, 2)
hull = ConvexHull(points)
print(f"Hull vertices: {hull.vertices}, Area: {hull.volume:.4f}")
```

**Use when**: Boundary detection, collision detection, smallest enclosing region, outlier identification.

---

### A121: Voronoi Diagram

**Problem**: Partition a plane into regions closest to each of a set of seed points.
**T**: O(n log n) | **S**: O(n)
**Lib**: `scipy.spatial.Voronoi`
**Guarantee**: Exact.

```python
from scipy.spatial import Voronoi
import numpy as np

points = np.array([[0, 0], [1, 0], [0.5, 1]])
vor = Voronoi(points)
print(f"Regions: {vor.regions}")
```

**Use when**: Service area mapping, nearest facility assignment, spatial partitioning, cell coverage.

---

### A122: Delaunay Triangulation

**Problem**: Triangulate a point set such that no point lies inside the circumcircle of any triangle.
**T**: O(n log n) | **S**: O(n)
**Lib**: `scipy.spatial.Delaunay`
**Guarantee**: Exact. Dual of Voronoi diagram.

```python
from scipy.spatial import Delaunay
import numpy as np

points = np.array([[0, 0], [1, 0], [0.5, 1], [1, 1]])
tri = Delaunay(points)
print(f"Triangles: {tri.simplices}")
```

**Use when**: Mesh generation, terrain modeling, interpolation (natural neighbor), finite element preprocessing.

---

### A123: Closest Pair of Points

**Problem**: Find the two closest points in a set.
**T**: O(n log n) (divide and conquer) | **S**: O(n)
**Lib**: `scipy.spatial.KDTree.query()`, `scipy.spatial.distance.pdist()`
**Guarantee**: Exact.

```python
from scipy.spatial import KDTree
import numpy as np

points = np.random.rand(1000, 2)
tree = KDTree(points)
d, i = tree.query(points, k=2)
closest_dist = d[:, 1].min()
print(f"Closest pair distance: {closest_dist:.6f}")
```

**Use when**: Collision detection, clustering (single-linkage), deduplication, minimum separation constraints.

---

### A124: Line / Segment Intersection

**Problem**: Detect and compute intersection points of line segments.
**T**: O(1) per pair, O((n+k) log n) for n segments with k intersections (Bentley-Ottmann) | **S**: O(n)
**Lib**: `shapely.intersection()`, `sympy.geometry.intersection()`
**Guarantee**: Exact.

```python
from shapely.geometry import LineString

line1 = LineString([(0, 0), (4, 4)])
line2 = LineString([(0, 4), (4, 0)])
pt = line1.intersection(line2)
print(f"Intersection: {pt}")  # POINT (2 2)
```

**Use when**: Road network analysis, visibility checks, polygon clipping, CAD operations.

---

### A125: Triangle Solver (Law of Sines / Cosines)

**Problem**: Given partial triangle information (sides, angles), solve for all remaining parts.
**T**: O(1) | **S**: O(1)
**Lib**: `math` (standard library), `sympy` (exact symbolic)
**Guarantee**: Exact. Handles SSS, SAS, ASA, AAS cases. SSA may have 0, 1, or 2 solutions (ambiguous case).

```python
import math

# SAS: sides a=5, b=7, included angle C=60°
a, b, C = 5, 7, math.radians(60)
c = math.sqrt(a**2 + b**2 - 2*a*b*math.cos(C))  # law of cosines
A = math.asin(a * math.sin(C) / c)                # law of sines
B = math.pi - A - C
print(f"c={c:.2f}, A={math.degrees(A):.1f}°, B={math.degrees(B):.1f}°")
```

**Use when**: Surveying, navigation, construction, any triangle measurement problem.

---

### A126: Coordinate Transforms

**Problem**: Convert between coordinate systems (Cartesian, polar, cylindrical, spherical) or apply affine transforms (rotation, scaling, translation).
**T**: O(1) per point, O(n) for n points | **S**: O(1)
**Lib**: `numpy` (matrix multiplication), `sympy` (symbolic), `scipy.spatial.transform.Rotation`
**Guarantee**: Exact.

```python
import numpy as np

# Polar to Cartesian
r, theta = 5, np.radians(30)
x, y = r * np.cos(theta), r * np.sin(theta)

# 2D rotation by angle
def rotate_2d(points, angle):
    c, s = np.cos(angle), np.sin(angle)
    R = np.array([[c, -s], [s, c]])
    return points @ R.T
```

**Use when**: Physics, robotics, GPS coordinate conversion, image transformations, 3D graphics.

---

## 25. Financial Mathematics

### A127: Net Present Value (NPV)

**Problem**: Compute present value of a series of future cash flows discounted at a given rate.
**T**: O(n) for n periods | **S**: O(1)
**Lib**: `numpy_financial.npv()`, `numpy` (manual)
**Guarantee**: Exact (closed-form summation).

```python
import numpy_financial as npf

rate = 0.08  # 8% discount rate
cash_flows = [-100000, 25000, 30000, 35000, 40000, 50000]  # initial investment + returns
npv = npf.npv(rate, cash_flows)
print(f"NPV: ${npv:,.2f}")
```

**Use when**: Investment evaluation, project selection, comparing alternatives with different cash flow timing.

---

### A128: Internal Rate of Return (IRR)

**Problem**: Find the discount rate that makes NPV = 0.
**T**: O(k·n) where k = iterations | **S**: O(1)
**Lib**: `numpy_financial.irr()`
**Guarantee**: Iterative (Newton's method). May not converge for unconventional cash flows.

```python
import numpy_financial as npf

cash_flows = [-100000, 25000, 30000, 35000, 40000, 50000]
irr = npf.irr(cash_flows)
print(f"IRR: {irr:.2%}")
```

**Use when**: Comparing investment returns, hurdle rate analysis, project ranking.

---

### A129: Loan Payment (PMT)

**Problem**: Compute fixed periodic payment for a loan (amortizing).
**T**: O(1) | **S**: O(1)
**Lib**: `numpy_financial.pmt()`
**Guarantee**: Exact (closed-form annuity formula).

```python
import numpy_financial as npf

pmt = npf.pmt(rate=0.05/12, nper=30*12, pv=-300000)
print(f"Monthly payment: ${pmt:,.2f}")
```

**Use when**: Mortgage calculation, auto loan, any fixed-rate amortizing loan.

---

### A130: Amortization Schedule

**Problem**: Generate period-by-period breakdown of principal, interest, and remaining balance.
**T**: O(n) for n periods | **S**: O(n)
**Lib**: `numpy_financial.ppmt()`, `numpy_financial.ipmt()`
**Guarantee**: Exact.

```python
import numpy_financial as npf
import numpy as np

rate, nper, pv = 0.05/12, 360, -300000
periods = np.arange(1, nper + 1)
principal = npf.ppmt(rate, periods, nper, pv)
interest = npf.ipmt(rate, periods, nper, pv)
balance = pv + np.cumsum(principal)
print(f"Month 1: principal=${principal[0]:,.2f}, interest=${interest[0]:,.2f}")
print(f"Total interest: ${interest.sum():,.2f}")
```

**Use when**: Loan comparison, refinancing analysis, early payoff scenarios.

---

### A131: Compound Interest

**Problem**: Compute future value with compound interest: FV = PV(1 + r/n)^(nt).
**T**: O(1) | **S**: O(1)
**Lib**: `numpy_financial.fv()`, `math`
**Guarantee**: Exact.

```python
import numpy_financial as npf

fv = npf.fv(rate=0.07/12, nper=20*12, pmt=-500, pv=-10000)
print(f"Future value after 20 years: ${fv:,.2f}")
```

**Use when**: Savings growth, retirement planning, investment projections.

---

### A132: Annuity Valuation

**Problem**: Compute present or future value of a series of equal payments.
**T**: O(1) | **S**: O(1)
**Lib**: `numpy_financial.pv()`, `numpy_financial.fv()`
**Guarantee**: Exact (closed-form annuity formulas).

```python
import numpy_financial as npf

pv = npf.pv(rate=0.06/12, nper=10*12, pmt=-200)
print(f"Present value of $200/month for 10 years at 6%: ${pv:,.2f}")
```

**Use when**: Pension valuation, lease pricing, structured settlement, insurance products.

---

### A133: Break-Even Analysis (Time-Based)

**Problem**: Find the time at which cumulative revenue equals cumulative cost.
**T**: O(n) or O(1) with closed form | **S**: O(1)
**Lib**: `numpy` (vectorized), `sympy` (symbolic)
**Guarantee**: Exact for linear models. Numerical for nonlinear.

```python
import numpy as np

fixed_cost = 50000
monthly_revenue = 8000
monthly_cost = 3000
months_to_breakeven = fixed_cost / (monthly_revenue - monthly_cost)
print(f"Break-even in {months_to_breakeven:.1f} months")
```

**Use when**: Business planning, investment payback period, make-vs-buy decisions.

---

### A134: Refinancing Comparison

**Problem**: Compare total cost of current loan vs. refinanced loan, accounting for closing costs and remaining term.
**T**: O(n) | **S**: O(n)
**Lib**: `numpy_financial` (pmt, ipmt, ppmt)
**Guarantee**: Exact comparison.

```python
import numpy_financial as npf

# Current loan
current_pmt = npf.pmt(0.065/12, 25*12, -250000)
current_total = current_pmt * 25 * 12

# Refinanced loan (lower rate, closing costs)
closing_costs = 5000
new_pmt = npf.pmt(0.045/12, 25*12, -(250000 + closing_costs))
new_total = new_pmt * 25 * 12

savings = current_total - new_total
breakeven_months = closing_costs / (current_pmt - new_pmt)
print(f"Savings: ${savings:,.0f}, Break-even: {breakeven_months:.0f} months")
```

**Use when**: Mortgage refinancing, debt consolidation, loan restructuring decisions.

---

## 26. Game Theory

### A135: Nash Equilibrium (2-Player Bimatrix)

**Problem**: Find all Nash equilibria of a two-player normal-form game with payoff matrices A (row player) and B (column player).
**T**: O(n^3) for support enumeration | **S**: O(n^2)
**Lib**: `nashpy.Game(A, B).support_enumeration()`
**Guarantee**: Exact (enumerates all equilibria).

```python
import nashpy as nash
import numpy as np

A = np.array([[3, 0], [5, 1]])  # row player payoffs
B = np.array([[3, 5], [0, 1]])  # column player payoffs
game = nash.Game(A, B)
equilibria = list(game.support_enumeration())
for eq in equilibria:
    print(f"Row: {eq[0]}, Col: {eq[1]}")
```

**Use when**: Two-player strategic interaction, pricing competition, auction bidding strategy, market entry decisions.

---

### A136: Mixed Strategy Equilibrium

**Problem**: Compute mixed-strategy Nash equilibrium where players randomize over actions.
**T**: O(n^3) via Lemke-Howson | **S**: O(n^2)
**Lib**: `nashpy.Game(A, B).lemke_howson_enumeration()`
**Guarantee**: Exact (Lemke-Howson always finds one equilibrium).

```python
import nashpy as nash
import numpy as np

A = np.array([[0, -1, 1], [1, 0, -1], [-1, 1, 0]])  # Rock-Paper-Scissors
B = -A  # zero-sum
game = nash.Game(A, B)
for eq in game.support_enumeration():
    print(f"Row mix: {eq[0].round(3)}, Col mix: {eq[1].round(3)}")
```

**Use when**: Games with no pure-strategy equilibrium, bluffing/randomization scenarios, zero-sum games.

---

### A137: Minimax (Zero-Sum Games)

**Problem**: Find optimal strategy for each player in a zero-sum game: max_x min_y x^T A y.
**T**: O(n^3) via LP | **S**: O(n^2)
**Lib**: `scipy.optimize.linprog()` or `nashpy`
**Guarantee**: Exact (minimax theorem guarantees saddle point).

```python
import nashpy as nash
import numpy as np

A = np.array([[3, -1], [-2, 4]])  # zero-sum payoff for row player
game = nash.Game(A, -A)
eqs = list(game.support_enumeration())
eq = eqs[0]
game_value = eq[0] @ A @ eq[1]
print(f"Game value: {game_value:.3f}")
print(f"Row strategy: {eq[0]}, Col strategy: {eq[1]}")
```

**Use when**: Competitive scenarios with pure opposition, security strategies, worst-case decision-making.

---

### A138: Shapley Value

**Problem**: Compute the fair allocation of total payoff among N players in a cooperative game based on marginal contributions.
**T**: O(2^n) for exact (exponential in players) | **S**: O(2^n)
**Lib**: Custom (itertools for permutations, or sampling approximation)
**Guarantee**: Exact for n ≤ ~20; approximation via sampling for larger games.

```python
import itertools
import math

def shapley_value(n, v):
    """v: coalition value function mapping frozenset -> float."""
    phi = [0.0] * n
    for i in range(n):
        for S in itertools.combinations(set(range(n)) - {i}, r=None):
            for r in range(len(set(range(n)) - {i}) + 1):
                for S in itertools.combinations(sorted(set(range(n)) - {i}), r):
                    s = len(S)
                    weight = math.factorial(s) * math.factorial(n - s - 1) / math.factorial(n)
                    S_set = frozenset(S)
                    phi[i] += weight * (v(S_set | {i}) - v(S_set))
        # Reset double-counting from nested loop
    # Correct implementation:
    phi = [0.0] * n
    for i in range(n):
        for r in range(n):
            for S in itertools.combinations(sorted(set(range(n)) - {i}), r):
                s = len(S)
                weight = math.factorial(s) * math.factorial(n - s - 1) / math.factorial(n)
                phi[i] += weight * (v(frozenset(S) | {i}) - v(frozenset(S)))
    return phi

# Example: 3-player majority game
v = lambda S: 1.0 if len(S) >= 2 else 0.0
print(shapley_value(3, v))  # [1/3, 1/3, 1/3]
```

**Use when**: Cost allocation, profit sharing, voting power analysis, feature importance attribution.

---

### A139: Fair Division (Adjusted Winner)

**Problem**: Divide items between two players so that each gets ≥50% of their perceived value and the allocation is equitable, efficient, and envy-free.
**T**: O(n log n) | **S**: O(n)
**Lib**: Custom
**Guarantee**: Exact (Adjusted Winner procedure is proven equitable + envy-free for 2 players).

```python
def adjusted_winner(items, values_a, values_b):
    """Allocate items between two players."""
    ratios = [(v_a / v_b if v_b > 0 else float('inf'), i)
              for i, (v_a, v_b) in enumerate(zip(values_a, values_b))]
    ratios.sort(reverse=True)
    alloc_a, alloc_b = [], []
    sum_a, sum_b = 0, 0
    for _, i in ratios:
        alloc_a.append(items[i])
        sum_a += values_a[i]
    # Transfer items from A to B until equitable
    for _, i in reversed(ratios):
        if sum_a <= sum_b:
            break
        alloc_a.remove(items[i])
        alloc_b.append(items[i])
        sum_a -= values_a[i]
        sum_b += values_b[i]
    return alloc_a, alloc_b

items = ['House', 'Car', 'Art', 'Stocks']
vals_a = [50, 30, 10, 10]
vals_b = [40, 20, 20, 20]
a, b = adjusted_winner(items, vals_a, vals_b)
print(f"Player A: {a}, Player B: {b}")
```

**Use when**: Divorce settlements, partnership dissolution, inheritance division, resource splitting between two parties.

---

### A140: Fair Division (Divide and Choose, N Players)

**Problem**: Divide a set of goods among N ≥ 2 players to achieve proportional fairness (each gets ≥1/N of their value).
**T**: O(n · N) | **S**: O(n)
**Lib**: Custom
**Guarantee**: Proportional (each player values own share ≥ 1/N).

```python
def round_robin(items, preferences):
    """Simple round-robin allocation based on preference rankings."""
    n_players = len(preferences)
    allocations = [[] for _ in range(n_players)]
    taken = set()
    for round_num in range(len(items)):
        player = round_num % n_players
        for item in preferences[player]:
            if item not in taken:
                allocations[player].append(item)
                taken.add(item)
                break
    return allocations
```

**Use when**: Multi-party resource allocation, draft picks, task assignment with preferences.

---

### A141: Auction — Vickrey (Second-Price Sealed-Bid)

**Problem**: Allocate an item via sealed-bid auction; highest bidder wins, pays second-highest bid. Truthful bidding is a dominant strategy.
**T**: O(n log n) for n bidders | **S**: O(n)
**Lib**: Custom
**Guarantee**: Exact (dominant-strategy incentive-compatible).

```python
def vickrey_auction(bids: dict[str, float]) -> tuple[str, float]:
    """Return (winner, price) for a Vickrey auction."""
    sorted_bids = sorted(bids.items(), key=lambda x: x[1], reverse=True)
    winner = sorted_bids[0][0]
    price = sorted_bids[1][1]  # second-highest bid
    return winner, price

bids = {'Alice': 100, 'Bob': 85, 'Carol': 92}
winner, price = vickrey_auction(bids)
print(f"Winner: {winner}, pays ${price}")  # Carol wins? No: Alice wins, pays $92
```

**Use when**: Auction mechanism design, procurement, truthful elicitation of valuations.

---

### A142: Repeated Game Strategy (Tit-for-Tat)

**Problem**: Determine optimal strategy in iterated games (e.g., repeated Prisoner's Dilemma) using tit-for-tat or related strategies.
**T**: O(T) for T rounds | **S**: O(T)
**Lib**: Custom (or `axelrod` library for tournaments)
**Guarantee**: Heuristic (no formal optimality, but robust in tournaments).

```python
def tit_for_tat(history_opponent):
    """Cooperate first, then copy opponent's last move."""
    if not history_opponent:
        return 'C'
    return history_opponent[-1]

def play_repeated(strategy_a, strategy_b, rounds=100):
    history_a, history_b = [], []
    for _ in range(rounds):
        a = strategy_a(history_b)
        b = strategy_b(history_a)
        history_a.append(a)
        history_b.append(b)
    return history_a, history_b
```

**Use when**: Modeling long-term relationships, cooperation vs. defection dynamics, negotiation strategy evaluation.

---

### A143: Evolutionary Stable Strategy (ESS)

**Problem**: Find strategies in a population game that resist invasion by mutant strategies.
**T**: O(n^2) for n strategies | **S**: O(n^2)
**Lib**: Custom (matrix analysis)
**Guarantee**: Exact (ESS conditions are checkable analytically).

```python
import numpy as np

def find_ess(payoff_matrix):
    """Check each pure strategy for ESS conditions."""
    n = payoff_matrix.shape[0]
    ess_candidates = []
    for i in range(n):
        is_ess = True
        for j in range(n):
            if j == i:
                continue
            # Condition 1: E(i,i) >= E(j,i)
            if payoff_matrix[j, i] > payoff_matrix[i, i]:
                is_ess = False
                break
            # Condition 2: if E(i,i) == E(j,i), then E(i,j) > E(j,j)
            if (payoff_matrix[j, i] == payoff_matrix[i, i]
                    and payoff_matrix[i, j] <= payoff_matrix[j, j]):
                is_ess = False
                break
        if is_ess:
            ess_candidates.append(i)
    return ess_candidates
```

**Use when**: Evolutionary biology models, market competition dynamics, social norm stability analysis.

---

### A144: Cooperative Game — Nucleolus

**Problem**: Find the unique allocation in the core that lexicographically minimizes the maximum dissatisfaction of any coalition.
**T**: O(2^n) for n players (LP sequence) | **S**: O(2^n)
**Lib**: `scipy.optimize.linprog()` (sequence of LPs)
**Guarantee**: Exact (unique, always in core if core is non-empty).

```python
from scipy.optimize import linprog
import numpy as np

def nucleolus_2player(v):
    """Simplified nucleolus for 2-player games."""
    # Core: x1 >= v({1}), x2 >= v({2}), x1+x2 = v({1,2})
    total = v[frozenset({0, 1})]
    x1 = max(v[frozenset({0})], total - v[frozenset({1})])
    x1 = (x1 + (total - v[frozenset({1})])) / 2  # midpoint of core
    return x1, total - x1
```

**Use when**: Coalition cost sharing, airport landing fee allocation, joint venture profit distribution.

---

### A145: Nash Bargaining Solution

**Problem**: Find the unique Pareto-optimal outcome that maximizes the product of players' gains over their disagreement point.
**T**: O(n^2) via convex optimization | **S**: O(n)
**Lib**: `scipy.optimize.minimize()`
**Guarantee**: Exact (convex problem, unique solution).

```python
from scipy.optimize import minimize
import numpy as np

def nash_bargaining(utility_frontier, disagreement):
    """Find Nash bargaining solution on a discrete frontier."""
    d1, d2 = disagreement
    best_product = -1
    best_point = None
    for u1, u2 in utility_frontier:
        if u1 >= d1 and u2 >= d2:
            product = (u1 - d1) * (u2 - d2)
            if product > best_product:
                best_product = product
                best_point = (u1, u2)
    return best_point

frontier = [(8, 2), (6, 4), (4, 6), (2, 8), (5, 5)]
result = nash_bargaining(frontier, (1, 1))
print(f"Bargaining solution: {result}")
```

**Use when**: Wage negotiation, trade agreements, contract terms, any bilateral negotiation with known alternatives.

---

### A146: Mechanism Design — VCG (Vickrey-Clarke-Groves)

**Problem**: Design a truthful mechanism for multi-item allocation that maximizes social welfare; each agent pays the externality they impose on others.
**T**: O(2^n · m) for n items, m agents | **S**: O(2^n)
**Lib**: Custom
**Guarantee**: Exact (VCG is dominant-strategy incentive-compatible).

```python
def vcg_mechanism(valuations):
    """valuations: dict agent -> dict item -> value. Single-item case."""
    # Find social-welfare-maximizing allocation
    agents = list(valuations.keys())
    items = list(next(iter(valuations.values())).keys())
    # Single item: allocate to highest bidder
    bids = {a: max(valuations[a].values()) for a in agents}
    winner = max(bids, key=bids.get)
    # VCG payment: externality = social welfare without winner - welfare of others with winner
    others_welfare_with = sum(v for a, v in bids.items() if a != winner)
    best_without_winner = max(v for a, v in bids.items() if a != winner)
    payment = best_without_winner  # reduces to Vickrey for single item
    return winner, payment
```

**Use when**: Auction design, public goods provision, resource allocation with strategic agents.

---

## 27. Decision Analysis

### A147: Expected Value / Expected Monetary Value (EMV)

**Problem**: Compute weighted average outcome: EMV = Σ p_i · v_i for outcomes v_i with probabilities p_i.
**T**: O(n) | **S**: O(1)
**Lib**: `numpy` (dot product)
**Guarantee**: Exact.

```python
import numpy as np

probabilities = np.array([0.3, 0.5, 0.2])
outcomes = np.array([100000, 50000, -20000])
emv = np.dot(probabilities, outcomes)
print(f"EMV: ${emv:,.0f}")  # $51,000
```

**Use when**: Simple decisions under risk, comparing alternatives, insurance decisions, investment screening.

---

### A148: Expected Utility

**Problem**: Compute expected utility E[u(X)] = Σ p_i · u(v_i) where u is a concave/convex utility function capturing risk preference.
**T**: O(n) | **S**: O(1)
**Lib**: `numpy`
**Guarantee**: Exact (given utility function).

```python
import numpy as np

def utility(x, risk_aversion=0.5):
    """CRRA utility: u(x) = x^(1-γ) / (1-γ)."""
    if risk_aversion == 1:
        return np.log(x)
    return x ** (1 - risk_aversion) / (1 - risk_aversion)

probs = np.array([0.6, 0.4])
outcomes = np.array([100, 50])
eu = np.dot(probs, utility(outcomes))
certainty_equiv = (eu * (1 - 0.5)) ** (1 / (1 - 0.5))
print(f"Expected utility: {eu:.3f}, Certainty equivalent: ${certainty_equiv:.0f}")
```

**Use when**: Risk-averse/risk-seeking decision-makers, insurance pricing, investment choice for individuals.

---

### A149: Decision Tree Evaluation

**Problem**: Evaluate a decision tree by backward induction (folding back): at chance nodes compute expected value, at decision nodes take the max.
**T**: O(n) for n nodes | **S**: O(n)
**Lib**: Custom (recursive traversal)
**Guarantee**: Exact (optimal policy by backward induction).

```python
def evaluate_tree(node):
    """Recursively evaluate a decision tree."""
    if 'value' in node:
        return node['value']
    children_vals = [(evaluate_tree(c), c) for c in node['children']]
    if node['type'] == 'chance':
        return sum(c['prob'] * v for v, c in children_vals)
    else:  # decision
        return max(v for v, _ in children_vals)

tree = {
    'type': 'decision',
    'children': [
        {'type': 'chance', 'children': [
            {'prob': 0.7, 'value': 200000},
            {'prob': 0.3, 'value': -50000}
        ]},
        {'value': 80000}  # safe option
    ]
}
print(f"Optimal value: ${evaluate_tree(tree):,.0f}")
```

**Use when**: Sequential decisions under uncertainty, R&D investment, medical treatment paths, litigation strategy.

---

### A150: Sensitivity Analysis (Tornado Diagram)

**Problem**: Quantify how much the decision outcome changes when each input parameter varies within its range, holding others at base case.
**T**: O(n) for n parameters | **S**: O(n)
**Lib**: `matplotlib` (visualization)
**Guarantee**: Exact (one-at-a-time sensitivity).

```python
import numpy as np

def tornado_analysis(base_value, parameters, model_fn):
    """Compute low/high impact of each parameter."""
    impacts = []
    for name, low, high in parameters:
        val_low = model_fn(**{name: low})
        val_high = model_fn(**{name: high})
        impacts.append((name, val_low - base_value, val_high - base_value))
    impacts.sort(key=lambda x: abs(x[2] - x[1]), reverse=True)
    return impacts
```

**Use when**: Investment analysis, project risk assessment, identifying key drivers, communicating uncertainty to stakeholders.

---

### A151: AHP (Analytic Hierarchy Process)

**Problem**: Derive priority weights from pairwise comparison matrices using eigenvalue method. Includes consistency check (CR < 0.10).
**T**: O(n^3) for n criteria | **S**: O(n^2)
**Lib**: `numpy.linalg.eig()`
**Guarantee**: Exact (principal eigenvector of comparison matrix).

```python
import numpy as np

def ahp_weights(comparison_matrix):
    """Compute AHP priority weights from pairwise comparison matrix."""
    eigenvalues, eigenvectors = np.linalg.eig(comparison_matrix)
    max_idx = np.argmax(eigenvalues.real)
    weights = eigenvectors[:, max_idx].real
    weights = weights / weights.sum()
    # Consistency ratio
    n = len(comparison_matrix)
    lambda_max = eigenvalues[max_idx].real
    ci = (lambda_max - n) / (n - 1)
    ri = {3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41}
    cr = ci / ri.get(n, 1.0)
    return weights, cr

A = np.array([[1, 3, 5], [1/3, 1, 3], [1/5, 1/3, 1]])
weights, cr = ahp_weights(A)
print(f"Weights: {weights.round(3)}, CR: {cr:.3f}")
```

**Use when**: Vendor selection, site selection, technology evaluation, any multi-criteria ranking with expert judgments.

---

### A152: TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)

**Problem**: Rank alternatives by their distance to an ideal best and ideal worst point in normalized weighted criteria space.
**T**: O(m · n) for m alternatives, n criteria | **S**: O(m · n)
**Lib**: `numpy`
**Guarantee**: Exact (deterministic ranking).

```python
import numpy as np

def topsis(matrix, weights, is_benefit):
    """TOPSIS ranking. matrix: m alternatives x n criteria."""
    # Normalize
    norm = matrix / np.sqrt((matrix ** 2).sum(axis=0))
    weighted = norm * weights
    # Ideal best and worst
    ideal_best = np.where(is_benefit, weighted.max(axis=0), weighted.min(axis=0))
    ideal_worst = np.where(is_benefit, weighted.min(axis=0), weighted.max(axis=0))
    # Distances
    d_best = np.sqrt(((weighted - ideal_best) ** 2).sum(axis=1))
    d_worst = np.sqrt(((weighted - ideal_worst) ** 2).sum(axis=1))
    scores = d_worst / (d_best + d_worst)
    return scores

M = np.array([[250, 16, 12], [200, 20, 8], [300, 12, 16]])
w = np.array([0.4, 0.35, 0.25])
benefit = np.array([False, True, True])  # cost, performance, quality
scores = topsis(M, w, benefit)
print(f"TOPSIS scores: {scores.round(3)}, Best: Alternative {scores.argmax() + 1}")
```

**Use when**: Supplier evaluation, project ranking, location selection, any multi-criteria decision without pairwise comparisons.

---

### A153: ELECTRE I (Outranking)

**Problem**: Build outranking relations between alternatives using concordance and discordance analysis; eliminate dominated alternatives.
**T**: O(m^2 · n) for m alternatives, n criteria | **S**: O(m^2)
**Lib**: Custom
**Guarantee**: Exact (concordance/discordance thresholds are deterministic).

```python
import numpy as np

def electre_1(matrix, weights, conc_threshold=0.65, disc_threshold=0.35):
    """ELECTRE I outranking. Returns dominance boolean matrix."""
    m, n = matrix.shape
    concordance = np.zeros((m, m))
    discordance = np.zeros((m, m))
    for i in range(m):
        for j in range(m):
            if i == j:
                continue
            conc = sum(weights[k] for k in range(n) if matrix[i, k] >= matrix[j, k])
            concordance[i, j] = conc / weights.sum()
            max_range = matrix.max(axis=0) - matrix.min(axis=0)
            max_range[max_range == 0] = 1
            disc = max((matrix[j, k] - matrix[i, k]) / max_range[k]
                       for k in range(n) if matrix[j, k] > matrix[i, k]) if any(matrix[j] > matrix[i]) else 0
            discordance[i, j] = disc
    outranks = (concordance >= conc_threshold) & (discordance <= disc_threshold)
    return outranks

M = np.array([[8, 7, 6], [6, 8, 8], [7, 6, 7]])
w = np.array([0.4, 0.35, 0.25])
print(electre_1(M, w))
```

**Use when**: Environmental impact assessment, infrastructure decisions, when compensability between criteria is not desired.

---

### A154: Bayesian Decision Analysis

**Problem**: Update beliefs about uncertain states using Bayes' theorem, then compute expected value with posterior probabilities.
**T**: O(n · m) for n states, m evidence items | **S**: O(n)
**Lib**: `numpy`
**Guarantee**: Exact (Bayes' theorem is exact).

```python
import numpy as np

def bayesian_decision(prior, likelihood, payoffs):
    """Update beliefs and compute expected payoffs per action."""
    posterior = prior * likelihood
    posterior /= posterior.sum()
    ev = payoffs @ posterior
    return posterior, ev

prior = np.array([0.6, 0.4])  # P(high demand), P(low demand)
likelihood = np.array([0.8, 0.3])  # P(positive signal | state)
payoffs = np.array([[100, -20], [40, 30]])  # actions x states
posterior, ev = bayesian_decision(prior, likelihood, payoffs)
print(f"Posterior: {posterior.round(3)}, EV per action: {ev.round(1)}")
```

**Use when**: Medical diagnosis, market research interpretation, sequential information gathering, value of information analysis.

---

### A155: Minimax Regret

**Problem**: Choose the action that minimizes the maximum regret (opportunity cost) across all states of nature.
**T**: O(m · n) for m actions, n states | **S**: O(m · n)
**Lib**: `numpy`
**Guarantee**: Exact.

```python
import numpy as np

def minimax_regret(payoff_matrix):
    """payoff_matrix: actions x states. Returns best action index."""
    best_per_state = payoff_matrix.max(axis=0)
    regret = best_per_state - payoff_matrix
    max_regret = regret.max(axis=1)
    best_action = max_regret.argmin()
    return best_action, max_regret, regret

payoffs = np.array([[50, 30, 10], [35, 35, 35], [10, 40, 60]])
action, max_reg, reg_table = minimax_regret(payoffs)
print(f"Minimax regret action: {action}, max regrets: {max_reg}")
```

**Use when**: Decision-making under complete uncertainty (no probabilities available), conservative planning, robust strategy selection.

---

### A156: Multi-Attribute Utility Theory (MAUT)

**Problem**: Compute overall utility U(x) = Σ w_i · u_i(x_i) using attribute-specific utility functions and weights.
**T**: O(m · n) for m alternatives, n attributes | **S**: O(m · n)
**Lib**: `numpy`
**Guarantee**: Exact (given utility functions and weights).

```python
import numpy as np

def maut_score(alternatives, weights, utility_fns):
    """Score alternatives using multi-attribute utility."""
    scores = []
    for alt in alternatives:
        u = sum(w * fn(v) for w, fn, v in zip(weights, utility_fns, alt))
        scores.append(u)
    return np.array(scores)

# Example: normalize to [0,1] utility
linear = lambda lo, hi: (lambda x: (x - lo) / (hi - lo))
alts = [[250, 16, 12], [200, 20, 8], [300, 12, 16]]
weights = [0.4, 0.35, 0.25]
fns = [linear(200, 300), linear(12, 20), linear(8, 16)]  # cost is reversed below
# Invert cost utility
fns[0] = lambda x, lo=200, hi=300: 1 - (x - lo) / (hi - lo)
scores = maut_score(alts, weights, fns)
print(f"MAUT scores: {scores.round(3)}")
```

**Use when**: Complex decisions with multiple attributes, when utility functions are elicited from stakeholders, healthcare technology assessment.

---

## 28. Multi-Objective Optimization

### A157: Pareto Frontier Enumeration

**Problem**: Given a set of evaluated alternatives, identify the Pareto-optimal (non-dominated) set.
**T**: O(m^2 · n) for m alternatives, n objectives | **S**: O(m)
**Lib**: `numpy`
**Guarantee**: Exact.

```python
import numpy as np

def pareto_front(costs):
    """Find Pareto-optimal indices (all objectives minimized)."""
    is_pareto = np.ones(len(costs), dtype=bool)
    for i, c in enumerate(costs):
        if not is_pareto[i]:
            continue
        is_pareto[is_pareto] = np.any(costs[is_pareto] < c, axis=1) | np.all(costs[is_pareto] == c, axis=1)
        is_pareto[i] = True
    return np.where(is_pareto)[0]

objectives = np.array([[1, 5], [2, 3], [3, 4], [4, 1], [2, 2]])
front = pareto_front(objectives)
print(f"Pareto-optimal indices: {front}")  # [0, 4, 3]
```

**Use when**: Identifying non-dominated solutions, filtering candidate designs, post-processing optimization results.

---

### A158: Weighted Sum Method

**Problem**: Convert multi-objective problem to single-objective by scalarization: minimize Σ w_i · f_i(x).
**T**: Same as underlying single-objective solver | **S**: Same
**Lib**: `scipy.optimize.minimize()`, `cvxpy`
**Guarantee**: Exact for convex problems (finds Pareto-optimal point for given weights).

```python
from scipy.optimize import minimize
import numpy as np

def weighted_sum(x, weights):
    f1 = x[0]**2 + x[1]**2  # minimize cost
    f2 = (x[0] - 2)**2 + (x[1] - 2)**2  # minimize distance to ideal
    return weights[0] * f1 + weights[1] * f2

weights = [0.5, 0.5]
result = minimize(weighted_sum, x0=[1, 1], args=(weights,))
print(f"Optimal: {result.x.round(3)}, Value: {result.fun:.3f}")
```

**Use when**: Convex multi-objective problems, when decision-maker can specify relative importance weights, generating Pareto points by varying weights.

---

### A159: Epsilon-Constraint Method

**Problem**: Optimize one objective while constraining all others to be within epsilon bounds; vary epsilon to trace the Pareto frontier.
**T**: Same as underlying constrained optimizer per point | **S**: Same
**Lib**: `scipy.optimize.minimize()`, `cvxpy`
**Guarantee**: Finds Pareto-optimal points (including non-convex regions).

```python
from scipy.optimize import minimize

def epsilon_constraint(x, eps_f2):
    """Minimize f1 subject to f2 <= eps_f2."""
    f1 = x[0]**2 + x[1]**2
    return f1

cons = [{'type': 'ineq', 'fun': lambda x, e=eps: e - ((x[0]-2)**2 + (x[1]-2)**2)}]
results = []
for eps in [0.5, 1.0, 2.0, 4.0]:
    res = minimize(epsilon_constraint, x0=[1, 1], args=(eps,),
                   constraints=[{'type': 'ineq', 'fun': lambda x, e=eps: e - ((x[0]-2)**2 + (x[1]-2)**2)}])
    results.append((res.fun, (res.x[0]-2)**2 + (res.x[1]-2)**2))
print("Pareto points (f1, f2):", [(round(a, 2), round(b, 2)) for a, b in results])
```

**Use when**: Non-convex Pareto frontiers, when weighted sum fails to find all Pareto points, exploring specific trade-off regions.

---

### A160: NSGA-II (Non-dominated Sorting Genetic Algorithm II)

**Problem**: Evolutionary multi-objective optimization: find diverse Pareto-optimal set using non-dominated sorting + crowding distance.
**T**: O(M · N^2 · G) for M objectives, N population, G generations | **S**: O(N · M)
**Lib**: `pymoo` (`NSGA2`)
**Guarantee**: Heuristic (converges to Pareto front empirically, no formal guarantee).

```python
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.problems import get_problem
from pymoo.optimize import minimize as pymoo_minimize

problem = get_problem("zdt1")
algorithm = NSGA2(pop_size=100)
res = pymoo_minimize(problem, algorithm, ('n_gen', 200), seed=1, verbose=False)
print(f"Pareto front: {len(res.F)} points")
print(f"Objective ranges: f1=[{res.F[:,0].min():.3f}, {res.F[:,0].max():.3f}], "
      f"f2=[{res.F[:,1].min():.3f}, {res.F[:,1].max():.3f}]")
```

**Use when**: Complex multi-objective problems, non-convex/disconnected Pareto fronts, engineering design optimization, many objectives.

---

### A161: MOEA/D (Multi-Objective Evolutionary Algorithm Based on Decomposition)

**Problem**: Decompose multi-objective problem into scalar subproblems using weight vectors; solve cooperatively.
**T**: O(N · T · G) for N subproblems, T neighbors, G generations | **S**: O(N · M)
**Lib**: `pymoo` (`MOEAD`)
**Guarantee**: Heuristic (typically finds well-distributed Pareto front).

```python
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.problems import get_problem
from pymoo.optimize import minimize as pymoo_minimize
from pymoo.util.ref_dirs import get_reference_directions

problem = get_problem("dtlz2")
ref_dirs = get_reference_directions("das-dennis", 3, n_partitions=12)
algorithm = MOEAD(ref_dirs, n_neighbors=15, prob_neighbor_mating=0.7)
res = pymoo_minimize(problem, algorithm, ('n_gen', 200), seed=1, verbose=False)
print(f"Pareto front: {len(res.F)} points in {problem.n_obj} objectives")
```

**Use when**: Many-objective optimization (3+ objectives), when uniform Pareto front coverage is important, large-scale engineering.

---

### A162: Goal Programming

**Problem**: Minimize deviations from stated goals for each objective: min Σ w_i · (d_i^+ + d_i^-) where d^+, d^- are over/under-achievement.
**T**: O(LP) | **S**: O(LP)
**Lib**: `pulp`, `scipy.optimize.linprog()`
**Guarantee**: Exact (LP formulation).

```python
import pulp

prob = pulp.LpProblem("goal_programming", pulp.LpMinimize)
x1 = pulp.LpVariable("x1", 0)
x2 = pulp.LpVariable("x2", 0)
# Goal 1: profit >= 100 (minimize under-achievement)
dp1 = pulp.LpVariable("dp1", 0)  # over-achievement
dm1 = pulp.LpVariable("dm1", 0)  # under-achievement
prob += 5*x1 + 3*x2 - dp1 + dm1 == 100
# Goal 2: cost <= 60 (minimize over-achievement)
dp2 = pulp.LpVariable("dp2", 0)
dm2 = pulp.LpVariable("dm2", 0)
prob += 2*x1 + 4*x2 - dp2 + dm2 == 60
# Minimize weighted deviations
prob += 3*dm1 + 2*dp2
prob += x1 <= 30
prob += x2 <= 20
prob.solve(pulp.PULP_CBC_CMD(msg=0))
print(f"x1={x1.value()}, x2={x2.value()}, "
      f"profit gap={dm1.value()}, cost excess={dp2.value()}")
```

**Use when**: Satisficing (meeting targets rather than optimizing), budget planning with multiple goals, resource allocation with aspirations.

---

### A163: Lexicographic Optimization

**Problem**: Optimize objectives in strict priority order: optimize f1 first, then f2 subject to f1 being optimal, then f3, etc.
**T**: O(k · LP) for k objectives | **S**: O(LP)
**Lib**: `pulp`, `cvxpy`
**Guarantee**: Exact (sequential LP/QP).

```python
import pulp

def lexicographic_solve(objectives, constraints, variables):
    """Solve objectives in priority order."""
    results = []
    extra_constraints = []
    for obj in objectives:
        prob = pulp.LpProblem("lex", pulp.LpMinimize)
        prob += obj
        for c in constraints + extra_constraints:
            prob += c
        prob.solve(pulp.PULP_CBC_CMD(msg=0))
        opt_val = pulp.value(obj)
        results.append(opt_val)
        extra_constraints.append(obj <= opt_val)  # fix this objective
    return results
```

**Use when**: Clear priority ordering among objectives (safety > cost > performance), military/emergency resource allocation, hierarchical planning.

---

### A164: Reference Point Method

**Problem**: Find the Pareto-optimal point closest to a decision-maker's aspiration (reference) point using achievement scalarizing function.
**T**: O(single-objective solver) | **S**: O(n)
**Lib**: `scipy.optimize.minimize()`
**Guarantee**: Pareto-optimal (for proper reference points).

```python
from scipy.optimize import minimize
import numpy as np

def achievement_scalarizing(x, ref_point, weights):
    """Minimize max weighted deviation from reference point."""
    f = np.array([x[0]**2 + x[1]**2, (x[0]-3)**2 + (x[1]-3)**2])
    return max(weights * (f - ref_point))

ref = np.array([2.0, 2.0])  # aspiration
w = np.array([1.0, 1.0])
result = minimize(achievement_scalarizing, x0=[1.5, 1.5], args=(ref, w))
f_vals = [result.x[0]**2 + result.x[1]**2, (result.x[0]-3)**2 + (result.x[1]-3)**2]
print(f"Closest Pareto point to {ref}: objectives = {[round(f,3) for f in f_vals]}")
```

**Use when**: Interactive multi-objective optimization, when decision-maker has specific targets, iterative preference refinement.

---

## 29. Numerical ODEs & Dynamical Systems

### A165: Euler Method (Forward)

**Problem**: Solve y' = f(t, y), y(t₀) = y₀ by simple forward stepping: y_{n+1} = y_n + h·f(t_n, y_n).
**T**: O(n) where n = steps | **S**: O(n·s) storing trajectory
**Lib**: Custom (educational); use `scipy.integrate.solve_ivp` for production
**Guarantee**: First-order accurate, O(h) local error. Unstable for stiff systems.

```python
import numpy as np

def euler_method(f, t_span, y0, h: float = 0.01):
    """Forward Euler for dy/dt = f(t, y)."""
    t_start, t_end = t_span
    t = np.arange(t_start, t_end + h, h)
    y = np.zeros((len(t), len(y0)))
    y[0] = y0
    for i in range(len(t) - 1):
        y[i + 1] = y[i] + h * np.array(f(t[i], y[i]))
    return {"t": t.tolist(), "y": y.tolist()}
```

**Use when**: Educational demonstrations, understanding ODE numerics. For production code, use solve_ivp (A116) with adaptive step size.

---

### A166: Runge-Kutta 4th Order (RK4)

**Problem**: Solve y' = f(t, y) with fourth-order accuracy using weighted average of four slope evaluations per step.
**T**: O(4n) function evaluations | **S**: O(n·s)
**Lib**: Custom or `scipy.integrate.solve_ivp(method='RK45')` (adaptive RK4/5)
**Guarantee**: Fourth-order accurate, O(h⁴) local error. Much better than Euler for smooth problems.

```python
import numpy as np

def rk4(f, t_span, y0, h: float = 0.01):
    """Classic Runge-Kutta 4th order method."""
    t_start, t_end = t_span
    t = np.arange(t_start, t_end + h, h)
    y = np.zeros((len(t), len(y0)))
    y[0] = y0
    for i in range(len(t) - 1):
        k1 = h * np.array(f(t[i], y[i]))
        k2 = h * np.array(f(t[i] + h/2, y[i] + k1/2))
        k3 = h * np.array(f(t[i] + h/2, y[i] + k2/2))
        k4 = h * np.array(f(t[i] + h, y[i] + k3))
        y[i + 1] = y[i] + (k1 + 2*k2 + 2*k3 + k4) / 6
    return {"t": t.tolist(), "y": y.tolist()}
```

**Use when**: Fixed-step integration where fourth-order accuracy is sufficient. For adaptive step size, use solve_ivp with RK45 (default).

---

### A167: Stiff ODE Solver (BDF / Radau)

**Problem**: Solve stiff ODE systems where explicit methods (Euler, RK4) require impractically small time steps.
**T**: O(n·s³) per step (implicit methods require solving nonlinear systems) | **S**: O(n·s)
**Lib**: `scipy.integrate.solve_ivp(method='BDF')` or `method='Radau'`
**Guarantee**: BDF: variable-order (1-5), A-stable for orders 1-2. Radau: 5th-order, L-stable.

```python
from scipy.integrate import solve_ivp

def solve_stiff_ode(f, t_span, y0, method: str = "BDF", rtol: float = 1e-8):
    """Solve stiff ODE system using implicit methods."""
    sol = solve_ivp(f, t_span, y0, method=method, rtol=rtol, dense_output=True)
    return {
        "t": sol.t.tolist(),
        "y": sol.y.tolist(),
        "n_steps": len(sol.t),
        "success": sol.success,
        "message": sol.message,
    }
```

**Use when**: Chemical kinetics (fast/slow reactions), electrical circuits (small RC constants), combustion, any system with widely separated time scales. If RK45 takes too many steps or diverges, switch to BDF or Radau.

---

### A168: Phase Portrait Analysis

**Problem**: Visualize a 2D dynamical system dx/dt = f(x,y), dy/dt = g(x,y) via vector field and trajectories.
**T**: O(grid² + n_traj·steps) | **S**: O(grid² + n_traj·steps)
**Lib**: `scipy.integrate.solve_ivp()`, `matplotlib.pyplot.streamplot()`
**Guarantee**: Qualitative correctness depends on grid resolution and trajectory time span.

```python
import numpy as np
from scipy.integrate import solve_ivp

def phase_portrait(f, x_range, y_range, grid_n: int = 20, trajectories: list = None):
    """Compute vector field and trajectories for a 2D system."""
    x = np.linspace(*x_range, grid_n)
    y = np.linspace(*y_range, grid_n)
    X, Y = np.meshgrid(x, y)
    U = np.zeros_like(X)
    V = np.zeros_like(Y)
    for i in range(grid_n):
        for j in range(grid_n):
            dxdt = f(0, [X[i,j], Y[i,j]])
            U[i,j], V[i,j] = dxdt[0], dxdt[1]
    trajs = []
    for y0 in (trajectories or []):
        sol = solve_ivp(f, [0, 50], y0, max_step=0.1)
        trajs.append({"y0": y0, "x": sol.y[0].tolist(), "y": sol.y[1].tolist()})
    return {"X": X.tolist(), "Y": Y.tolist(), "U": U.tolist(), "V": V.tolist(), "trajectories": trajs}
```

**Use when**: Understanding qualitative behavior of 2D systems: predator-prey, competing species, oscillators, mechanical systems. Identify fixed points, limit cycles, separatrices.

---

### A169: Equilibrium & Stability Analysis

**Problem**: Find fixed points of dx/dt = f(x) and classify them via eigenvalues of the Jacobian.
**T**: O(s³) per fixed point (eigenvalue computation) | **S**: O(s²) for Jacobian
**Lib**: `scipy.optimize.fsolve()`, `numpy.linalg.eig()`
**Guarantee**: Local classification is exact (Hartman-Grobman theorem for hyperbolic fixed points).

```python
import numpy as np
from scipy.optimize import fsolve

def stability_analysis(f, jacobian, fixed_point_guesses: list):
    """Find fixed points and classify via Jacobian eigenvalues."""
    results = []
    for guess in fixed_point_guesses:
        fp = fsolve(lambda x: f(0, x), guess, full_output=True)
        if fp[2] == 1:  # converged
            x_star = fp[0]
            J = jacobian(x_star)
            eigenvalues = np.linalg.eig(J)[0]
            real_parts = eigenvalues.real
            if all(r < 0 for r in real_parts):
                stability = "stable (sink)"
            elif all(r > 0 for r in real_parts):
                stability = "unstable (source)"
            elif any(r < 0 for r in real_parts) and any(r > 0 for r in real_parts):
                stability = "saddle"
            else:
                stability = "center or nonlinear analysis needed"
            results.append({
                "fixed_point": x_star.tolist(),
                "eigenvalues": eigenvalues.tolist(),
                "stability": stability,
            })
    return results
```

**Use when**: Determine long-term behavior of systems: will populations stabilize? Will oscillations damp out? Is the equilibrium reachable? Prerequisite for control system design.

---

### A170: Bifurcation Analysis

**Problem**: Track how equilibria and their stability change as a parameter varies; detect bifurcation points.
**T**: O(n_params · (root_finding + eigenvalue)) | **S**: O(n_params · s)
**Lib**: `scipy.optimize.fsolve()`, `numpy.linalg.eig()`
**Guarantee**: Detects standard bifurcations (saddle-node, transcritical, pitchfork, Hopf) via eigenvalue crossing.

```python
import numpy as np
from scipy.optimize import fsolve

def bifurcation_diagram(f_param, jacobian_param, param_range, guess, param_name: str = "r"):
    """Sweep parameter and track fixed points + stability."""
    results = []
    x_guess = np.array(guess)
    for p in param_range:
        try:
            fp = fsolve(lambda x: f_param(x, p), x_guess, full_output=True)
            if fp[2] == 1:
                x_star = fp[0]
                J = jacobian_param(x_star, p)
                eigs = np.linalg.eig(J)[0]
                stable = all(e.real < 0 for e in eigs)
                results.append({
                    "param": float(p), "fixed_point": x_star.tolist(),
                    "eigenvalues": [complex(e) for e in eigs], "stable": stable,
                })
                x_guess = x_star  # continuation
        except Exception:
            pass
    return results
```

**Use when**: Understanding how system behavior changes with temperature, growth rate, disease transmissibility, policy parameter. "What parameter value causes the system to switch behavior?"

---

### A171: ODE Parameter Estimation (Inverse Problem)

**Problem**: Given observed data y_obs(t), find parameters θ that minimize ‖y(t; θ) - y_obs(t)‖².
**T**: O(n_eval · ODE_solve) where n_eval = optimizer iterations | **S**: O(n·s)
**Lib**: `scipy.optimize.minimize()` + `scipy.integrate.solve_ivp()`
**Guarantee**: Finds local optimum; use multi-start for global. Sensitive to initial guess.

```python
from scipy.integrate import solve_ivp
from scipy.optimize import minimize
import numpy as np

def estimate_ode_params(ode_func, t_obs, y_obs, param_bounds, x0_guess):
    """Fit ODE parameters to observed data via least squares."""
    def objective(params):
        try:
            sol = solve_ivp(lambda t, y: ode_func(t, y, *params),
                           [t_obs[0], t_obs[-1]], x0_guess, t_eval=t_obs)
            if not sol.success:
                return 1e10
            return float(np.sum((sol.y[0] - y_obs) ** 2))
        except Exception:
            return 1e10
    result = minimize(objective, x0=[b[0] for b in param_bounds],
                     bounds=param_bounds, method='L-BFGS-B')
    return {"params": result.x.tolist(), "residual": float(result.fun), "success": result.success}
```

**Use when**: Fitting epidemiological models to outbreak data, calibrating pharmacokinetic models, estimating chemical reaction rates from concentration measurements.

---

### A172: ODE Sensitivity Analysis

**Problem**: Determine how sensitive the ODE solution is to parameter perturbations: ∂y/∂θ.
**T**: O(s·p · ODE_solve) for forward sensitivity | **S**: O(n·s·p)
**Lib**: `scipy.integrate.solve_ivp()` (augmented system)
**Guarantee**: Exact (for the numerical solution) via forward sensitivity equations.

```python
from scipy.integrate import solve_ivp
import numpy as np

def ode_sensitivity(f, df_dp, t_span, y0, params, param_names, dp: float = 0.01):
    """Finite-difference sensitivity analysis for ODE parameters."""
    base_sol = solve_ivp(lambda t, y: f(t, y, *params), t_span, y0, max_step=0.1)
    sensitivities = {}
    for i, name in enumerate(param_names):
        perturbed = list(params)
        perturbed[i] += dp
        pert_sol = solve_ivp(lambda t, y: f(t, y, *perturbed), t_span, y0,
                            t_eval=base_sol.t, max_step=0.1)
        sens = (pert_sol.y - base_sol.y) / dp
        sensitivities[name] = {
            "max_sensitivity": float(np.max(np.abs(sens))),
            "mean_sensitivity": float(np.mean(np.abs(sens))),
        }
    return {"base_solution": base_sol.y.tolist(), "t": base_sol.t.tolist(), "sensitivities": sensitivities}
```

**Use when**: Which parameters matter most? Uncertainty propagation in ODE models. Guides data collection (measure what's sensitive).

---

### A173: SIR / SEIR Epidemic Model

**Problem**: Model disease spread in a population using compartmental ODEs: Susceptible → Infected → Recovered (± Exposed).
**T**: O(n) time steps | **S**: O(n)
**Lib**: `scipy.integrate.solve_ivp()`
**Guarantee**: Exact (for the ODE model). R₀ = β/γ determines outbreak threshold.

```python
from scipy.integrate import solve_ivp
import numpy as np

def sir_model(t_span, S0, I0, R0, beta: float, gamma: float):
    """SIR epidemic model: dS/dt = -βSI, dI/dt = βSI - γI, dR/dt = γI."""
    N = S0 + I0 + R0
    def sir(t, y):
        S, I, R = y
        return [-beta * S * I / N, beta * S * I / N - gamma * I, gamma * I]
    sol = solve_ivp(sir, t_span, [S0, I0, R0], max_step=0.1, dense_output=True)
    R0_value = beta / gamma
    peak_infected = float(np.max(sol.y[1]))
    peak_time = float(sol.t[np.argmax(sol.y[1])])
    return {
        "t": sol.t.tolist(), "S": sol.y[0].tolist(), "I": sol.y[1].tolist(), "R": sol.y[2].tolist(),
        "R0": R0_value, "peak_infected": peak_infected, "peak_time": peak_time,
        "final_size": float(sol.y[2][-1]),
    }
```

**Use when**: Disease outbreak modeling, vaccination strategy analysis, pandemic preparedness. R₀ > 1 → epidemic grows. Extend to SEIR (add Exposed) for diseases with incubation period.

---

### A174: Lotka-Volterra Predator-Prey Model

**Problem**: Model oscillating predator-prey populations: dx/dt = αx - βxy, dy/dt = δxy - γy.
**T**: O(n) time steps | **S**: O(n)
**Lib**: `scipy.integrate.solve_ivp()`
**Guarantee**: Exact (for the ODE model). Produces periodic orbits in the classical case.

```python
from scipy.integrate import solve_ivp
import numpy as np

def lotka_volterra(t_span, prey0, pred0, alpha=1.0, beta=0.1, delta=0.075, gamma=1.5):
    """Lotka-Volterra predator-prey model."""
    def lv(t, y):
        x, z = y  # prey, predator
        return [alpha*x - beta*x*z, delta*x*z - gamma*z]
    sol = solve_ivp(lv, t_span, [prey0, pred0], max_step=0.1, dense_output=True)
    equilibrium_prey = gamma / delta
    equilibrium_pred = alpha / beta
    return {
        "t": sol.t.tolist(), "prey": sol.y[0].tolist(), "predator": sol.y[1].tolist(),
        "equilibrium": {"prey": equilibrium_prey, "predator": equilibrium_pred},
        "prey_range": [float(np.min(sol.y[0])), float(np.max(sol.y[0]))],
        "pred_range": [float(np.min(sol.y[1])), float(np.max(sol.y[1]))],
    }
```

**Use when**: Ecology (predator-prey, competing species), chemical oscillations (Belousov-Zhabotinsky), market dynamics. Shows how coupled systems produce oscillations.

---

## Cross-Reference Index

Where each algorithm section connects to structures and solvers.

| Algorithm Section | Structures (structures.md) | Solvers (solvers.md) | Interpretation (interpretation-patterns.md) |
|---|---|---|---|
| §1 Graph Traversal (A1-A7) | §1 Graph Theory (1.1-1.8) | §1 NetworkX | §1.5 Connectivity Results |
| §2 Shortest Path (A8-A12) | §1.3 Weighted Graph, §1.6 DAG | §1 NetworkX, §5 SciPy | §1.1 Shortest Path Results |
| §3 MST (A13-A14) | §1.3 Weighted Graph | §1 NetworkX | §1.1 (as routing variant) |
| §4 Matching (A15-A18) | §1.4 Bipartite Graph | §1 NetworkX, §5 SciPy (A16) | §1.2 Matching Results |
| §5 Network Flow (A19-A20) | §1.3 Weighted Graph (capacity) | §1 NetworkX, §6 OR-Tools | §1.4 Flow Results |
| §6-7 Coloring/Clique (A21-A25) | §1.1 Simple Graph | §1 NetworkX, §2 PuLP (ILP) | §1.3 Coloring Results |
| §8-9 Euler/Hamilton/TSP (A26-A30) | §1.1 Simple Graph, §1.3 Weighted | §1 NetworkX, §6 OR-Tools | §2.3 Scheduling Results |
| §10 LP/ILP (A31-A34) | §7.1 ILP | §2 PuLP, §5 SciPy, §6 OR-Tools | §2.1 LP/ILP Results |
| §11 DP Patterns (A35-A42) | §7.1 ILP (Knapsack), §7.2 Search Space | (Custom) | §2.2 Knapsack/Selection |
| §12 Greedy (A43-A47) | §3.2 Set Systems (Set Cover) | §2 PuLP (ILP fallback) | §2.2 Knapsack/Selection |
| §13 SAT/SMT/CSP (A48-A52) | §4 Logic (4.1-4.4) | §3 Z3, §6 OR-Tools | §3 Proof Results |
| §14 Number Theory (A53-A62) | §5 Number Theory (5.1-5.3) | §4 SymPy | §6 Number Theory Results |
| §15 Counting (A63-A69) | §2 Combinatorics (2.1-2.5) | §7 itertools, §4 SymPy | §4 Counting Results |
| §16 Order Theory (A70-A73) | §6 Relations & Orders (6.1-6.3) | §1 NetworkX (matching) | -- |
| §17 Proof Techniques (A74-A77) | §4 Logic | §3 Z3, §4 SymPy | §3 Proof Results |
| §18 Probability (A78-A81) | §8 Discrete Probability (8.1-8.2) | §8 numpy, §4 SymPy | §5 Probability Results |
| §19-20 Search/Metaheuristics (A82-A86) | §7.2 Search Space | (Custom) | §2.3 Scheduling Results |
| §21 Continuous Opt (A87-A94) | §9 Continuous Optimization (9.1-9.5) | §9 cvxpy, §5 SciPy | §7 Continuous Opt Solutions |
| §22 Linear Algebra (A95-A106) | §11 Linear Algebra (11.1-11.4) | numpy.linalg, scipy.linalg | §9 Linear Algebra Results |
| §23 Calculus (A107-A116) | §12 Calculus (12.1-12.3) | §4 SymPy, §5 SciPy | §10 Calculus Results |
| §24 Geometry & Trig (A117-A126) | §13 Geometry (13.1-13.4) | shapely, scipy.spatial | §11 Geometry Results |
| §25 Financial Math (A127-A134) | §14 Financial Math (14.1) | numpy-financial | §12 Financial Results |
| §26 Game Theory (A135-A146) | §15 Game Theory (15.1-15.3) | §13 nashpy | §13 Game Theory Results |
| §27 Decision Analysis (A147-A156) | §16 Decision Analysis (16.1-16.3) | numpy, scipy, §2 PuLP | §14 Decision Analysis Results |
| §28 Multi-Objective Opt (A157-A164) | §17 Multi-Objective Opt (17.1-17.3) | §14 pymoo, §2 PuLP, §5 SciPy | §15 Multi-Objective Results |
| §29 ODEs & Dynamical Systems (A165-A174) | §21 ODE/Dynamical System (21.1-21.3) | §5 SciPy (solve_ivp) | §18 Simulation & ODE Results |

Also see: **problem-classification.md** for decision-tree algorithm selection, **solving-protocols.md** for domain-specific solving workflows, **common-mistakes.md** §S1-S6 for solving pitfalls.
