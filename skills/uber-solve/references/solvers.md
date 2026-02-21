# Python Solver Ecosystem Reference

**Scope**: Universal (all solver libraries serve multiple domains)

Guide to the solver libraries used by uber-solve. For each library: what it solves, installation, key APIs, and performance notes.

**Python**: Use your project's Python environment (venv, conda, or system Python 3.10+).
**Install**: `pip install <package>` (or `python3 -m pip install <package>`)

---

## 1. NetworkX -- Graph Algorithms

**Solves**: Graph traversal, shortest paths, MST, matching, flow, connectivity, coloring, centrality, community detection.

**Install**: `pip install networkx`

**When to use**: Any graph algorithm. Battle-tested, pure Python with optional C backends (via scipy). Handles graphs up to ~100K nodes comfortably.

### Key APIs

```python
import networkx as nx

# Construction
G = nx.Graph()                    # undirected
D = nx.DiGraph()                  # directed
G.add_edge('a', 'b', weight=3)
G.add_nodes_from(['a', 'b', 'c'])
G.add_weighted_edges_from([('a', 'b', 3), ('b', 'c', 1)])

# Properties
nx.is_connected(G)
nx.is_bipartite(G)
nx.is_directed_acyclic_graph(D)
nx.is_planar(G)
nx.number_connected_components(G)

# Traversal
list(nx.bfs_edges(G, 'a'))
list(nx.dfs_edges(G, 'a'))
list(nx.topological_sort(D))

# Shortest path
nx.shortest_path(G, 'a', 'c')
nx.shortest_path_length(G, 'a', 'c')
nx.dijkstra_path(G, 'a', 'c')
nx.bellman_ford_path(G, 'a', 'c')
dict(nx.all_pairs_shortest_path_length(G))

# MST
T = nx.minimum_spanning_tree(G)

# Matching
M = nx.bipartite.maximum_matching(G, top_nodes)
M = nx.max_weight_matching(G)

# Flow
flow_value, flow_dict = nx.maximum_flow(G, 's', 't')
cut_value, partition = nx.minimum_cut(G, 's', 't')
nx.min_cost_flow(D)

# Coloring
coloring = nx.greedy_color(G, strategy='DSATUR')

# Components
list(nx.connected_components(G))
list(nx.strongly_connected_components(D))
nx.articulation_points(G)
list(nx.bridges(G))

# Clique
list(nx.find_cliques(G))
nx.graph_clique_number(G)

# Euler
nx.has_eulerian_circuit(G)
list(nx.eulerian_circuit(G))

# DAG
nx.dag_longest_path(D)
nx.dag_longest_path_length(D)
nx.transitive_closure(D)

# Centrality
nx.degree_centrality(G)
nx.betweenness_centrality(G)
nx.pagerank(D)

# Export
nx.to_numpy_array(G)
nx.to_scipy_sparse_array(G)
```

### Performance Notes
- Pure Python: handles ~10K-100K nodes
- With scipy backend: handles ~100K-1M nodes
- For larger graphs: consider graph-tool or igraph (C++ backends)

---

## 2. PuLP -- Linear & Integer Programming

**Solves**: LP, ILP, MIP (mixed integer programming), binary programming.

**Install**: `pip install pulp` (includes CBC solver)

**When to use**: Any optimization problem with linear objective and linear constraints. The workhorse for NP-hard problems via ILP formulation.

### Key APIs

```python
from pulp import (
    LpProblem, LpVariable, LpMinimize, LpMaximize,
    LpInteger, LpBinary, LpContinuous,
    LpStatus, value, lpSum
)

# Problem
prob = LpProblem("name", LpMinimize)  # or LpMaximize

# Variables
x = LpVariable("x", lowBound=0, upBound=10, cat=LpContinuous)
y = LpVariable("y", cat=LpInteger)    # integer variable
z = LpVariable("z", cat=LpBinary)     # 0/1 variable

# Variable arrays
x = [LpVariable(f"x_{i}", cat=LpBinary) for i in range(n)]
y = {(i,j): LpVariable(f"y_{i}_{j}", lowBound=0, cat=LpInteger)
     for i in range(m) for j in range(n)}

# Objective
prob += lpSum(cost[i] * x[i] for i in range(n)), "total_cost"

# Constraints (named for debugging)
prob += lpSum(x[i] for i in range(n)) >= 5, "min_selection"
prob += x[0] + x[1] <= 1, "conflict_01"

# Solve
prob.solve()  # uses CBC by default

# Results
print(f"Status: {LpStatus[prob.status]}")
print(f"Objective: {value(prob.objective)}")
for v in prob.variables():
    if value(v) > 0:
        print(f"  {v.name} = {value(v)}")
```

### Solver Options
```python
from pulp import PULP_CBC_CMD, GLPK_CMD

# CBC with time limit and gap tolerance
prob.solve(PULP_CBC_CMD(
    msg=True,           # show solver output
    timeLimit=60,       # seconds
    gapRel=0.01,        # stop at 1% optimality gap
    threads=4           # parallel threads
))

# GLPK alternative
prob.solve(GLPK_CMD(msg=True))
```

### Common Patterns

**Binary decision**: x_i in {0,1} -- select item i or not
**Big-M constraint**: If x=1 then y >= 5 → y >= 5 - M(1-x)
**SOS constraints**: At most one of x_1,...,x_k can be nonzero
**Indicator**: If x_i=1 then constraint active → linearize with big-M

### Performance Notes
- CBC: good for problems up to ~10K variables, ~50K constraints
- For larger: use Gurobi (free academic license) or CPLEX
- Symmetry breaking constraints speed up ILP significantly
- Warm starts: `var.setInitialValue(val)` for feasible starting solution

---

## 3. Z3 -- SAT/SMT Solving

**Solves**: SAT, SMT (integers, reals, bit vectors, arrays), optimization, proof checking, UNSAT core extraction.

**Install**: `pip install z3-solver`

**When to use**: Boolean satisfiability, integer constraint satisfaction, automated theorem proving, optimization with non-linear constraints.

### Key APIs

```python
from z3 import (
    Solver, Optimize,
    Bool, Int, Real, BitVec, Array,
    And, Or, Not, Implies, If, Xor,
    ForAll, Exists, Lambda,
    sat, unsat, unknown,
    IntSort, BoolSort,
    Sum, Product, Distinct,
    simplify, prove, is_true
)

# --- SAT ---
s = Solver()
x, y, z = Bools('x y z')
s.add(Or(x, y))
s.add(Implies(x, z))
if s.check() == sat:
    m = s.model()
    print(m[x], m[y], m[z])

# --- Integer arithmetic ---
s = Solver()
a, b = Ints('a b')
s.add(a + b == 10, a > 0, b > 0, a < b)
s.check()
m = s.model()

# --- Optimization ---
opt = Optimize()
x, y = Ints('x y')
opt.add(x >= 0, y >= 0, x + y <= 100)
opt.maximize(3*x + 5*y)
opt.check()

# --- All-different (Sudoku-style) ---
cells = [[Int(f"c_{i}_{j}") for j in range(9)] for i in range(9)]
s = Solver()
for row in cells:
    s.add(Distinct(row))
    for c in row:
        s.add(And(c >= 1, c <= 9))

# --- Proof by contradiction ---
s = Solver()
n = Int('n')
s.add(n > 0)
s.add(Not(n * (n + 1) % 2 == 0))  # negate what we want to prove
assert s.check() == unsat  # contradiction → theorem is true

# --- UNSAT core ---
s = Solver()
p1 = Bool('p1')
s.assert_and_track(x > 0, p1)     # tracked assertion
# ... more tracked assertions
if s.check() == unsat:
    core = s.unsat_core()  # which assertions are conflicting

# --- Quantifiers ---
x = Int('x')
prove(ForAll(x, Implies(x > 0, x * x > 0)))
```

### Performance Notes
- Handles millions of Boolean variables (SAT)
- Integer arithmetic: good for ~10K variables with linear constraints
- Non-linear integer arithmetic: much harder, may timeout
- Use `set_param('timeout', 30000)` for time limits (milliseconds)
- Incremental solving: `s.push()` / `s.pop()` for adding/removing constraints

---

## 4. SymPy -- Symbolic Mathematics

**Solves**: Symbolic algebra, calculus, number theory, combinatorics, equation solving, proof verification.

**Install**: `pip install sympy`

**When to use**: Symbolic computation, closed-form solutions, number theory, generating functions, mathematical proof steps.

### Key APIs

```python
from sympy import (
    symbols, Symbol, Integer, Rational, oo,
    simplify, expand, factor, collect,
    solve, solveset, diophantine,
    gcd, lcm, factorint, isprime, totient, mod_inverse,
    binomial, factorial, catalan, bell, fibonacci,
    Sum, Product, summation,
    Eq, Ne, Lt, Le, Gt, Ge,
    sqrt, log, exp, pi, E,
    Matrix, eye, zeros,
    Function, Lambda,
    Piecewise, Min, Max,
    series, fps, limit,
    primerange, prime, nextprime,
)
from sympy.ntheory.modular import crt
from sympy.combinatorics import Permutation, PermutationGroup
from sympy.utilities.iterables import partitions, multiset_permutations

# --- Algebra ---
x, y, n, k = symbols('x y n k')
expr = expand((x + y)**5)
result = factor(x**4 - 1)
simplified = simplify(expr)

# --- Equation solving ---
solve(x**2 - 5*x + 6, x)          # [2, 3]
solve([x + y - 10, x - y - 4], [x, y])  # {x: 7, y: 3}

# --- Number theory ---
gcd(12, 18)         # 6
factorint(360)       # {2: 3, 3: 2, 5: 1}
isprime(97)          # True
totient(12)          # 4
mod_inverse(3, 7)    # 5 (since 3*5 ≡ 1 mod 7)
crt([3, 5, 7], [2, 3, 2])  # CRT solution

# --- Combinatorics ---
binomial(10, 3)      # 120
factorial(10)        # 3628800
catalan(5)           # 42

# --- Summation ---
summation(k**2, (k, 1, n))  # n(n+1)(2n+1)/6
summation(1/k, (k, 1, n))   # harmonic number (symbolic)

# --- Diophantine equations ---
from sympy.solvers.diophantine import diophantine
from sympy import symbols
x, y = symbols('x y', integer=True)
diophantine(3*x + 5*y - 17)  # set of parametric solutions

# --- Series / Generating functions ---
series(1/(1-x), x, 0, 6)    # 1 + x + x^2 + ... + O(x^6)

# --- Matrix operations ---
M = Matrix([[1, 2], [3, 4]])
M.det()         # -2
M.eigenvals()   # eigenvalues
M**n            # symbolic matrix power (if possible)
```

### Performance Notes
- Symbolic: slow for large expressions, but exact
- Number theory functions: fast for numbers up to ~10^18
- `factorint()`: uses trial division + Pollard's rho + ECM
- For numerical speed: use `sympy.N()` or switch to numpy

---

## 5. SciPy -- Scientific Computing

**Solves**: Linear programming, sparse linear algebra, optimization, statistics, signal processing.

**Install**: `pip install scipy`

**When to use**: Numerical linear algebra, LP (not ILP), statistical distributions, sparse matrix operations.

### Key APIs

```python
from scipy.optimize import linear_sum_assignment, linprog
from scipy.sparse.csgraph import shortest_path, connected_components
from scipy.linalg import eig
import numpy as np

# --- Assignment (Hungarian) ---
cost = np.array([[4, 1, 3], [2, 0, 5], [3, 2, 2]])
row_ind, col_ind = linear_sum_assignment(cost)
print(f"Optimal cost: {cost[row_ind, col_ind].sum()}")

# --- Linear programming ---
# Minimize c^T x subject to A_ub x <= b_ub, A_eq x = b_eq
result = linprog(
    c=[1, 2],                    # objective coefficients
    A_ub=[[-1, -1], [1, -1]],   # inequality constraint matrix
    b_ub=[-3, 1],                # inequality bounds
    bounds=[(0, None), (0, None)],  # variable bounds
    method='highs'               # recommended solver
)
print(f"Optimal: {result.fun}, x = {result.x}")

# --- Sparse graph shortest path ---
from scipy.sparse import csr_matrix
graph = csr_matrix([[0, 1, 2], [0, 0, 1], [0, 0, 0]])
dist, predecessors = shortest_path(graph, return_predecessors=True)
```

---

## 6. OR-Tools (Google) -- Constraint Programming & Routing

**Solves**: CP-SAT (constraint programming), vehicle routing, scheduling, assignment, bin packing.

**Install**: `pip install ortools`

**When to use**: Complex scheduling, vehicle routing, constraint programming problems. Often faster than PuLP for combinatorial optimization.

### Key APIs

```python
from ortools.sat.python import cp_model

# --- CP-SAT Solver ---
model = cp_model.CpModel()

# Variables
x = model.new_int_var(0, 10, 'x')
y = model.new_int_var(0, 10, 'y')
b = model.new_bool_var('b')

# Constraints
model.add(x + y <= 15)
model.add(x != y)
model.add_all_different([x, y])

# Objective
model.maximize(3 * x + 2 * y)

# Solve
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 60.0
status = solver.solve(model)

if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    print(f"x={solver.value(x)}, y={solver.value(y)}")
    print(f"Objective: {solver.objective_value}")

# --- Vehicle Routing ---
from ortools.constraint_solver import routing_enums_pb2, pywrapcp

manager = pywrapcp.RoutingIndexManager(num_locations, num_vehicles, depot)
routing = pywrapcp.RoutingModel(manager)
# ... setup distance callback, solve
```

### Performance Notes
- CP-SAT: state-of-the-art for many combinatorial problems
- Often beats PuLP/CBC on scheduling and assignment problems
- Built-in support for no-overlap, cumulative, circuit constraints
- Scales to millions of variables for well-structured problems

---

## 7. itertools -- Combinatorial Generation (stdlib)

**Solves**: Permutation/combination generation, Cartesian products, enumeration.

**Install**: Built-in (no install needed)

**When to use**: Brute-force enumeration for small instances, generating candidate solutions, exhaustive search.

### Key APIs

```python
import itertools

list(itertools.permutations([1,2,3]))        # all 6 permutations
list(itertools.permutations([1,2,3], 2))     # all 2-permutations
list(itertools.combinations([1,2,3,4], 2))   # all C(4,2)=6 combinations
list(itertools.combinations_with_replacement([1,2,3], 2))
list(itertools.product([0,1], repeat=3))     # all 2^3 binary strings
list(itertools.chain.from_iterable(lists))   # flatten

# Subset enumeration (power set)
def powerset(s):
    return itertools.chain.from_iterable(
        itertools.combinations(s, r) for r in range(len(s) + 1)
    )
```

---

## 8. numpy -- Numerical Arrays

**Solves**: Matrix operations, linear algebra, random number generation, statistical computation.

**Install**: `pip install numpy`

**When to use**: Transition matrices (Markov chains), adjacency matrices, numerical computation, Monte Carlo.

### Key APIs for DM

```python
import numpy as np

# Adjacency matrix
A = np.array([[0,1,1],[1,0,0],[1,0,0]])

# Matrix power (paths of length k)
Ak = np.linalg.matrix_power(A, 3)  # number of walks of length 3

# Eigenvalues (spectral graph theory)
eigenvalues = np.linalg.eigvalsh(A)

# Stationary distribution of Markov chain
P = np.array([[0.9, 0.1], [0.3, 0.7]])
vals, vecs = np.linalg.eig(P.T)
stat = vecs[:, np.isclose(vals, 1)].real.flatten()
stat /= stat.sum()

# Random generation
rng = np.random.default_rng(42)  # reproducible
samples = rng.choice(10, size=100, replace=True)
```

---

## 9. cvxpy -- Convex Optimization

**Solves**: Convex optimization (LP, QP, SOCP, SDP, exponential cone), disciplined convex programming.

**Install**: `pip install cvxpy`

**When to use**: Any optimization problem where the objective is convex and constraints define a convex set. cvxpy verifies convexity at problem construction time and rejects non-convex formulations, so you get either a guaranteed global optimum or a clear error.

### Key APIs

```python
import cvxpy as cp
import numpy as np

# --- Variables ---
x = cp.Variable(n)                    # vector variable
X = cp.Variable((m, n))               # matrix variable
b = cp.Variable(n, boolean=True)      # mixed-integer (MILP via MIP solver)

# --- Objective ---
objective = cp.Minimize(cp.quad_form(x, Q))        # quadratic
objective = cp.Minimize(cp.norm(x, 1))              # L1 norm
objective = cp.Maximize(expected_return @ x)         # linear

# --- Constraints ---
constraints = [
    cp.sum(x) == 1,                   # equality
    x >= 0,                           # elementwise inequality
    cp.norm(x, 2) <= 1,              # second-order cone
    X >> 0,                           # positive semidefinite
    cp.quad_form(x, Sigma) <= risk,  # quadratic
]

# --- Solve ---
prob = cp.Problem(objective, constraints)
prob.solve()                          # uses ECOS/SCS/OSQP by default
# prob.solve(solver=cp.MOSEK)        # commercial solver (faster for SDP)

# --- Results ---
print(f"Status: {prob.status}")       # 'optimal', 'infeasible', 'unbounded'
print(f"Optimal value: {prob.value}")
print(f"Optimal x: {x.value}")

# --- Dual values ---
for i, c in enumerate(constraints):
    print(f"Constraint {i} dual: {c.dual_value}")
```

### Common Patterns

**Portfolio optimization** (Markowitz):
```python
x = cp.Variable(n)
ret = mu @ x                         # expected return
risk = cp.quad_form(x, Sigma)        # portfolio variance
prob = cp.Problem(cp.Maximize(ret - gamma * risk), [cp.sum(x) == 1, x >= 0])
```

**Lasso regression** (sparse recovery):
```python
beta = cp.Variable(p)
loss = cp.sum_squares(A @ beta - y)
reg = lambd * cp.norm(beta, 1)
prob = cp.Problem(cp.Minimize(loss + reg))
```

**Efficient frontier** (sweep over risk tolerance):
```python
for gamma in [0.1, 0.5, 1.0, 5.0, 10.0]:
    prob = cp.Problem(cp.Maximize(mu @ x - gamma * cp.quad_form(x, Sigma)),
                      [cp.sum(x) == 1, x >= 0])
    prob.solve()
    results.append((np.sqrt(risk.value), ret.value))
```

### Performance Notes
- ECOS (default for SOCP): good for problems up to ~10K variables
- SCS: scales better for large problems, but lower accuracy
- OSQP: fast for QP, handles ~100K variables
- MOSEK: commercial, fastest for SDP and large conic programs
- Problem construction overhead: cache the problem and use `prob.solve(warm_start=True)` for parametric sweeps

---

## Solver Selection Guide

| Problem Type | Primary Solver | Fallback |
|---|---|---|
| Graph algorithm | NetworkX | igraph, graph-tool |
| Shortest path (large) | scipy.sparse.csgraph | NetworkX |
| Bipartite assignment | scipy.linear_sum_assignment | PuLP ILP |
| LP (continuous) | scipy.linprog (HiGHS) | cvxpy / PuLP |
| ILP / MIP | PuLP (CBC) | OR-Tools CP-SAT |
| QP (convex) | cvxpy (OSQP) | scipy trust-constr |
| Convex optimization | cvxpy | scipy.optimize |
| Nonlinear constrained | scipy.optimize (SLSQP) | cvxpy (if convex) |
| Least squares | numpy.linalg.lstsq | scipy.optimize.least_squares |
| Nonlinear least squares | scipy.optimize.least_squares | custom Gauss-Newton |
| SAT / Boolean | Z3 | pysat |
| SMT / Integer constraints | Z3 | -- |
| Constraint programming | OR-Tools CP-SAT | Z3 |
| Vehicle routing | OR-Tools routing | ILP |
| Scheduling | OR-Tools CP-SAT | ILP |
| Symbolic math | SymPy | -- |
| Number theory | SymPy | gmpy2 |
| Combinatorial counting | SymPy + itertools | -- |
| Markov chains | numpy | scipy |
| Monte Carlo | numpy.random | -- |
| Generating functions | SymPy series | -- |
| Linear system Ax=b | numpy.linalg.solve | scipy.linalg.solve |
| Eigenvalues / SVD | numpy.linalg.eig / svd | scipy.linalg.eig |
| Matrix decomposition | scipy.linalg (lu, qr, cholesky) | numpy.linalg |
| Differentiation / integration | SymPy (symbolic) | scipy.integrate (numerical) |
| ODE solving | scipy.integrate.solve_ivp | SymPy dsolve (symbolic) |
| Polygon area / intersection | shapely | SymPy.geometry |
| Voronoi / convex hull | scipy.spatial | shapely |
| Nearest neighbors | scipy.spatial.KDTree | sklearn.neighbors |
| NPV / IRR / PMT | numpy-financial | custom |
| Amortization | numpy-financial (ppmt, ipmt) | custom |

## §10: shapely — Computational Geometry

**Install**: `pip install shapely`

**When to use**: Polygon area/perimeter, point-in-polygon, intersection/union of shapes, buffering, convex hull, spatial predicates (contains, overlaps, touches).

**Key functions**:
- `Polygon(coords).area`, `.length` — area and perimeter
- `Point.distance(other)` — distance between geometries
- `geom1.intersection(geom2)` — geometric intersection
- `geom1.union(geom2)` — geometric union
- `MultiPoint(pts).convex_hull` — convex hull

**Quick example**:
```python
from shapely.geometry import Polygon, Point, LineString

lot = Polygon([(0,0), (100,0), (100,80), (50,100), (0,80)])
print(f"Area: {lot.area:.0f} sq units")
print(f"Perimeter: {lot.length:.1f} units")
print(f"Contains (50,50)? {lot.contains(Point(50, 50))}")
```

**Performance**: Pure Python geometry engine. Fast for 2D operations. For massive point sets (>100K), combine with `scipy.spatial` for spatial indexing.

---

## §11: scipy.spatial — Spatial Algorithms

**Install**: `pip install scipy` (usually pre-installed)

**When to use**: Voronoi diagrams, Delaunay triangulation, convex hull, KD-trees for nearest neighbor, distance matrices. Complements shapely for point-set geometry.

**Key functions**:
- `ConvexHull(points)` — convex hull with vertices and volume
- `Voronoi(points)` — Voronoi diagram
- `Delaunay(points)` — Delaunay triangulation
- `KDTree(points).query(x, k)` — k-nearest neighbors
- `distance.cdist(A, B)` — pairwise distance matrix

**Quick example**:
```python
from scipy.spatial import ConvexHull, KDTree
import numpy as np

points = np.random.rand(100, 2)
hull = ConvexHull(points)
tree = KDTree(points)
d, i = tree.query([0.5, 0.5], k=3)
print(f"Hull area: {hull.volume:.4f}, 3 nearest: {i}")
```

**Performance**: C-optimized. Handles millions of points. KDTree query is O(log n) average.

---

## §12: numpy-financial — Financial Calculations

**Install**: `pip install numpy-financial`

**When to use**: Time value of money (NPV, IRR, PMT, PV, FV), amortization schedules, loan analysis, investment evaluation.

**Key functions**:
- `npf.npv(rate, cashflows)` — net present value
- `npf.irr(cashflows)` — internal rate of return
- `npf.pmt(rate, nper, pv)` — periodic payment
- `npf.fv(rate, nper, pmt, pv)` — future value
- `npf.pv(rate, nper, pmt)` — present value
- `npf.ppmt(rate, per, nper, pv)` — principal portion of payment
- `npf.ipmt(rate, per, nper, pv)` — interest portion of payment

**Quick example**:
```python
import numpy_financial as npf

# Should I invest $100K for returns of $25K/yr for 5 years at 8%?
npv = npf.npv(0.08, [-100000, 25000, 25000, 25000, 25000, 25000])
irr = npf.irr([-100000, 25000, 25000, 25000, 25000, 25000])
pmt = npf.pmt(0.05/12, 30*12, -300000)  # mortgage payment
print(f"NPV: ${npv:,.0f}, IRR: {irr:.1%}, Monthly: ${pmt:,.2f}")
```

**Performance**: Vectorized numpy operations. Handles large cash flow arrays efficiently.

---

## Installation One-Liner

```bash
pip install networkx pulp z3-solver sympy scipy ortools numpy cvxpy shapely numpy-financial
```

## Dependency Check Script

```python
#!/usr/bin/env python3
"""Check solver library availability."""
libs = {
    'networkx': 'networkx',
    'pulp': 'pulp',
    'z3': 'z3',
    'sympy': 'sympy',
    'scipy': 'scipy',
    'ortools': 'ortools.sat.python.cp_model',
    'numpy': 'numpy',
    'cvxpy': 'cvxpy',
    'shapely': 'shapely',
    'numpy-financial': 'numpy_financial',
}
for name, module in libs.items():
    try:
        m = __import__(module)
        ver = getattr(m, '__version__', 'unknown')
        print(f"  [OK] {name} {ver}")
    except ImportError:
        print(f"  [MISSING] {name} -- pip install {name}")
```

---

## Cross-Reference Index

| Solver | Primary Structures (structures.md) | Key Algorithms (algorithms.md) |
|---|---|---|
| §1 NetworkX | §1 Graph Theory (all), §6 Relations & Orders | §1-§9 Graph algorithms (A1-A30), §16 Order Theory (A70-A71) |
| §2 PuLP | §7.1 ILP | §10 LP/ILP (A31-A34), §12 Set Cover (A47) |
| §3 Z3 | §4 Logic (4.1-4.4) | §13 SAT/SMT/CSP (A48-A52), §17 Proof (A74-A77) |
| §4 SymPy | §5 Number Theory, §2 Combinatorics | §14 Number Theory (A53-A62), §15 Counting (A63-A69), §17 Proof (A74) |
| §5 SciPy | §1.4 Bipartite Graph, §7.1 ILP (LP relaxation) | §4 Matching (A16 Hungarian), §10 LP (A31), §21 Continuous (A89-A93) |
| §6 OR-Tools | §7.3 Scheduling, §7.1 ILP | §10 ILP (A32), §9 TSP (A30), §13 CSP (A51-A52) |
| §7 itertools | §2 Combinatorics (2.1-2.4) | §15 Counting/Generation (A63-A65) |
| §8 numpy | §8 Discrete Probability | §18 Probability (A78-A81), §21 Continuous (A91) |
| §9 cvxpy | §9 Continuous Optimization (9.1-9.5) | §21 Continuous Opt (A87-A88, A94) |
| §10 shapely | §13 Geometry (13.1-13.3) | §24 Geometry (A117, A119, A124) |
| §11 scipy.spatial | §13 Geometry (13.3) | §24 Geometry (A120-A123) |
| §12 numpy-financial | §14 Financial Math (14.1) | §25 Financial Math (A127-A134) |

Note: numpy.linalg and scipy.linalg (used for §22 Linear Algebra, A95-A106) are submodules of numpy and scipy (§5, §8) — no separate install needed. SymPy (§4) handles §23 Calculus (A107-A116).

Also see: **solving-protocols.md** for solver usage within specific problem-type workflows, **optimization-hardening.md** for solver-specific performance tuning.
