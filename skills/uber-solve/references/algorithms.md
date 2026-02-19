# Algorithm Catalog

**Scope**: Discrete Mathematics (86 algorithms), Continuous Optimization (8 algorithms)

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

Also see: **problem-classification.md** for decision-tree algorithm selection, **solving-protocols.md** for domain-specific solving workflows, **common-mistakes.md** §S1-S6 for solving pitfalls.
