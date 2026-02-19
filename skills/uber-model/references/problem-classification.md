# Quick-Reference Problem Classification

Rapid pattern matching to go from a real-world problem description to a named mathematical problem, structure, algorithm, and solver. Use this at the start of Phase 2 in uber-model (before reading the full structures.md) or during fast-track mode in uber-polya.

---

## Decision Tree

Start here. Follow the branch that best matches the problem.

```
What is the user trying to do?
│
├─ ASSIGN things to things (people→tasks, resources→needs)
│  ├─ Two groups, one-to-one? ──────────── Bipartite Matching (A15-A17)
│  ├─ Two groups, with preferences? ────── Stable Matching (A17)
│  ├─ One-to-many with capacity? ───────── ILP Assignment (A32)
│  └─ Minimize total cost? ─────────────── Hungarian / linear_sum_assignment (A16)
│
├─ SCHEDULE things (events, tasks, exams)
│  ├─ Avoid conflicts (no overlap)? ────── Graph Coloring (A21-A22)
│  ├─ Respect dependencies (ordering)? ── Topological Sort / Critical Path (A3, A12)
│  ├─ Minimize total time (makespan)? ──── Scheduling ILP (A32) / CP-SAT
│  └─ Select max non-overlapping? ──────── Activity Selection (A43)
│
├─ ROUTE / NAVIGATE (find best path)
│  ├─ Point A to point B? ──────────────── Shortest Path (A8-A11)
│  ├─ Visit all locations? ─────────────── TSP (A28-A30)
│  ├─ Multiple vehicles? ───────────────── Vehicle Routing (OR-Tools)
│  └─ Maximum throughput? ──────────────── Max Flow (A19-A20)
│
├─ SELECT / PACK (choose items under constraints)
│  ├─ Budget/weight limit? ─────────────── Knapsack (A33-A34)
│  ├─ Cover all requirements? ──────────── Set Cover (A47)
│  ├─ Binary yes/no decisions? ─────────── ILP (A32) / SAT (A48)
│  └─ Multi-criteria trade-off? ────────── Multi-objective ILP / Pareto
│
├─ GROUP / PARTITION (classify, cluster)
│  ├─ Into non-overlapping groups? ──────── Set Partition / Graph Partition
│  ├─ By equivalence (same type)? ──────── Equivalence Classes
│  ├─ Balanced groups? ──────────────────── Balanced Partition ILP
│  └─ Find natural clusters? ────────────── Community Detection (NetworkX)
│
├─ COUNT arrangements
│  ├─ Order matters? ────────────────────── Permutations (A63)
│  ├─ Order doesn't matter? ─────────────── Combinations (A64)
│  ├─ With symmetry (rotations)? ────────── Burnside's Lemma (A67)
│  ├─ With overlapping conditions? ──────── Inclusion-Exclusion (A66)
│  └─ Recurrence pattern? ──────────────── DP / Generating Functions (A68)
│
├─ PROVE a mathematical statement
│  ├─ "For all n..." ────────────────────── Mathematical Induction (A74)
│  ├─ "It's impossible..." ──────────────── Contradiction (A75) / Pigeonhole (A77)
│  ├─ "There exists..." ─────────────────── Constructive Proof (A76) / Z3 (A48)
│  └─ Verify a logical claim? ──────────── Z3 SAT/SMT (A48-A50)
│
├─ ANALYZE a network
│  ├─ Find vulnerabilities? ─────────────── Articulation Points / Bridges (A6)
│  ├─ Find communities? ─────────────────── SCC (A5) / Connected Components (A7)
│  ├─ Find most important nodes? ────────── Centrality (NetworkX)
│  └─ Find bottlenecks? ─────────────────── Min Cut / Max Flow (A19)
│
├─ SATISFY constraints (feasibility)
│  ├─ Boolean constraints? ──────────────── SAT (A48)
│  ├─ Integer constraints? ──────────────── SMT / Z3 (A49)
│  ├─ Configuration / Sudoku-like? ──────── CSP (A51-A52)
│  └─ Linear constraints? ──────────────── LP Feasibility (A31)
│
├─ OPTIMIZE a continuous quantity
│  ├─ Convex objective + constraints? ──── cvxpy / Convex Program (A87)
│  ├─ Quadratic cost, linear constraints? ─ QP (A88)
│  ├─ Fit a model to data? ─────────────── Least Squares (A91) / Gauss-Newton (A92)
│  ├─ Smooth, no constraints? ──────────── BFGS (A89) / Gradient Descent (A90)
│  └─ Nonlinear constraints? ───────────── SLSQP / trust-constr (A93)
│
└─ ASSESS probability / risk
   ├─ What are the odds? ────────────────── Combinatorial Probability
   ├─ Expected outcome? ─────────────────── Expected Value (A78)
   ├─ Long-run behavior? ────────────────── Markov Chain (A80)
   └─ Estimate via simulation? ──────────── Monte Carlo (A81)
```

---

## Quick Pattern Table

One-line lookup from problem description to solution approach.

| If the user says... | Think... | Structure | Algorithm | Solver |
|---|---|---|---|---|
| "assign X to Y" | Assignment | Bipartite graph | Hungarian (A16) | scipy |
| "schedule with no conflicts" | Coloring | Conflict graph | Greedy/ILP (A21/A32) | NetworkX/PuLP |
| "find the shortest route" | Shortest path | Weighted graph | Dijkstra (A8) | NetworkX |
| "visit all cities" | TSP | Complete graph | Held-Karp/ILP (A28/A32) | OR-Tools |
| "maximize flow/throughput" | Max flow | Capacity network | Edmonds-Karp (A19) | NetworkX |
| "best subset under budget" | Knapsack | Items + capacity | DP (A33) | Custom |
| "cover all requirements" | Set cover | Set family | Greedy (A47) or ILP | PuLP |
| "order tasks with dependencies" | Topological sort | DAG | Kahn's (A3) | NetworkX |
| "project timeline / critical path" | Longest DAG path | DAG | DP (A12) | NetworkX |
| "partition into groups" | Partitioning | Set/graph | ILP (A32) | PuLP |
| "how many ways to arrange" | Counting | Combinatorial | Formula / DP | SymPy |
| "prove for all n" | Induction | Algebraic | Symbolic (A74) | SymPy |
| "is it possible / satisfiable" | SAT/CSP | Boolean/Integer | CDCL (A48) | Z3 |
| "find vulnerabilities in network" | Connectivity | Graph | Bridges/AP (A6) | NetworkX |
| "what's the probability" | Probability | Sample space | Counting / MC | SymPy/numpy |
| "stable matching / pairing" | Stable marriage | Bipartite + prefs | Gale-Shapley (A17) | Custom |
| "minimize cost of connections" | MST | Weighted graph | Kruskal (A13) | NetworkX |
| "find largest clique / group" | Clique | Graph | Bron-Kerbosch (A25) | NetworkX |
| "Euler path / traverse all edges" | Euler circuit | Multigraph | Hierholzer (A26) | NetworkX |
| "round-robin / balanced design" | Latin square | Array | CSP (A52) | Z3 |
| "cyclic / repeating pattern" | Modular arithmetic | Z_n | CRT (A55) | SymPy |
| "integer solutions only" | Diophantine | Number theory | Extended GCD (A54) | SymPy |
| "long-run / steady state" | Markov chain | Transition matrix | Eigenvector (A80) | numpy |
| "optimize with constraints" | ILP | Variables + constraints | Branch & bound (A32) | PuLP |
| "what if / sensitivity" | Sensitivity | (depends on base) | Re-solve with perturbation | (same) |
| "minimize smooth function" | Unconstrained opt | Continuous | BFGS (A89) | scipy |
| "portfolio / risk-return" | QP | Quadratic program | cvxpy QP (A88) | cvxpy |
| "fit a curve / regression" | Least squares | Overdetermined system | lstsq (A91) | numpy/scipy |
| "convex constraints" | Convex program | Conic program | Interior point (A87) | cvxpy |
| "engineering design" | Nonlinear constrained | NLP | SLSQP (A93) | scipy |

---

## Complexity Quick Check

Before committing to an approach, verify the computational feasibility.

| Problem Class | Complexity | Exact Feasible Up To | Approximation Available? |
|---|---|---|---|
| Shortest path | P | Any size | N/A (already polynomial) |
| MST | P | Any size | N/A |
| Bipartite matching | P | Any size | N/A |
| Max flow | P | Any size | N/A |
| Topological sort | P | Any size | N/A |
| Graph coloring | NP-hard | ~50 vertices (exact) | Greedy: Δ+1 colors |
| TSP | NP-hard | ~20 (DP), ~1000 (ILP) | Christofides: 1.5x |
| Knapsack | NP-hard | ~10^6 (pseudo-poly DP) | FPTAS: (1-ε)x |
| Set cover | NP-hard | ~30 (exact), ~1000 (ILP) | Greedy: ln(n)+1 |
| SAT | NP-complete | ~10^6 vars (modern solvers) | N/A (decision) |
| ILP | NP-hard | ~10K vars (CBC) | LP relaxation bound |
| Independent set | NP-hard | ~25 (bitmask DP) | None good (general) |
| Hamiltonian path | NP-complete | ~20 (DP) | Heuristic only |
| Graph isomorphism | GI-complete | ~1000 (practical) | N/A (decision) |
| Counting problems | #P (some) | ~20 (enumeration) | Sampling / MCMC |
| Convex optimization | P | Any size (via cvxpy) | N/A (already polynomial) |
| Quadratic programming | P (if convex) | Any size | N/A |
| Least squares | P | Any size (O(mn²)) | N/A |
| Nonlinear constrained | NP-hard (general) | ~1000 vars (local opt) | Multi-start heuristic |

---

## Disambiguation Tips

When two patterns seem equally likely, use these tiebreakers:

**Assignment vs. Set Cover**: If each "task" needs exactly one "worker," it's assignment (matching). If each "requirement" can be satisfied by any of several "sets," it's set cover.

**Coloring vs. Partitioning**: If the constraint is "no two neighbors share a group," it's coloring. If the constraint is "groups must be balanced" or "minimize inter-group edges," it's partitioning.

**Shortest Path vs. TSP**: If you need to go from A to B, it's shortest path. If you need to visit ALL locations and return, it's TSP.

**Knapsack vs. ILP**: Knapsack is a special case of ILP with one constraint (capacity). If there are multiple constraints, model as general ILP.

**SAT vs. ILP**: If all variables are Boolean and all constraints are clauses, use SAT (faster). If variables are integers or constraints are linear inequalities, use ILP.

**Counting vs. Optimization**: "How many?" is counting. "Which is best?" is optimization. "What fraction?" is probability (counting / total).

---

## Cross-Reference Index

After identifying the problem type here, consult the corresponding reference files:

| Problem Category | Structures (structures.md) | Algorithms (algorithms.md) | Protocols (solving-protocols.md) |
|---|---|---|---|
| ASSIGN | §1.4 Bipartite Graph, §7.1 ILP | §4 Matching (A15-A17), §10 ILP (A32) | Protocol: Optimization (ILP/LP) |
| SCHEDULE | §1.1 Simple Graph, §7.3 Scheduling | §6 Coloring (A21-A22), §1 Topo Sort (A3) | Protocol: Graph, Protocol: Optimization |
| ROUTE | §1.3 Weighted Graph | §2 Shortest Path (A8-A12), §9 TSP (A28-A30) | Protocol: Graph |
| SELECT/PACK | §7.1 ILP | §10 ILP (A32), §11 DP (A33-A34) | Protocol: Optimization, Protocol: DP |
| GROUP | §3.4 Set Partition | §10 ILP (A32) | Protocol: Optimization |
| COUNT | §2 Combinatorics | §15 Counting (A63-A69) | Protocol: Counting |
| PROVE | §4 Logic | §17 Proof (A74-A77) | Protocol: Proof |
| ANALYZE network | §1 Graph Theory | §1 Traversal (A1-A7), §5 Flow (A19) | Protocol: Graph |
| SATISFY | §4.4 CSP | §13 SAT/SMT/CSP (A48-A52) | Protocol: SAT/SMT |
| OPTIMIZE continuous | §9 Continuous Optimization | §21 Continuous Opt (A87-A94) | Protocol: Continuous Optimization |
| ASSESS probability | §8 Discrete Probability | §18 Probability (A78-A81) | Protocol: Counting |

Also see: **common-mistakes.md** for pitfalls specific to each problem category.
