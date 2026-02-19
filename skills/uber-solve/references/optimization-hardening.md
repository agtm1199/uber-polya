# Optimization & Production Hardening

**Scope**: All domains
**When to read**: Only when the user needs production-grade performance or the initial solution is too slow. This is Phase 4 of uber-solve -- optional for most problems.

---

## Step 1: Profile

Identify the bottleneck:
- Is it the algorithm complexity? (need better algorithm)
- Is it the constant factor? (need implementation optimization)
- Is it memory? (need space-efficient data structure)
- Is it the solver? (need different solver or tuning)

## Step 2: Algorithmic Optimization

Apply optimizations in order of impact:

1. **Problem reduction**: Remove symmetries, fix variables, tighten bounds
2. **Decomposition**: Break into independent subproblems (connected components, block decomposition)
3. **Preprocessing**: Reduce instance size (remove dominated elements, contract edges)
4. **Better algorithm**: If current is O(n³) and O(n²) exists, switch
5. **Better data structure**: Priority queue, union-find, segment tree, etc.
6. **Solver tuning**: Branching heuristics, cutting planes, warm starts for ILP

## Step 3: Approximation Tier

If exact solution is infeasible for the instance size:

| Approach | When to Use | Guarantee |
|---|---|---|
| PTAS/FPTAS | Exists for problem | (1+ε)-optimal, polynomial in n and 1/ε |
| Constant-factor approximation | Known ratio | α-optimal (state α) |
| Greedy heuristic | Large instance, need speed | Problem-specific bound |
| Local search | Good starting solution available | Local optimum |
| Metaheuristic (SA, GA) | No better option | No formal guarantee (state this) |
| Randomized | Expected good performance | Expected value bound |

**Always state the approximation guarantee explicitly.** Never present a heuristic solution as optimal.

## Step 4: Production Hardening

For deployment-ready code:
- Add input validation with clear error messages
- Add logging (structured, not print statements)
- Add timeout handling (signal-based or iterative check)
- Add memory monitoring for large instances
- Write unit tests for edge cases
- Pin solver library versions

## Performance Tuning by Solver

### NetworkX
- Pure Python: ~10K-100K nodes
- With scipy backend: ~100K-1M nodes
- For larger graphs: consider graph-tool or igraph (C++ backends)
- Use `nx.to_scipy_sparse_array()` for matrix operations on large graphs

### PuLP / CBC
- Good for problems up to ~10K variables, ~50K constraints
- For larger: use Gurobi (free academic license) or CPLEX
- Symmetry breaking constraints speed up ILP significantly
- Warm starts: `var.setInitialValue(val)` for feasible starting solution
- Use `threads=4` for parallel branch-and-bound

### Z3
- Handles millions of Boolean variables (SAT)
- Integer arithmetic: good for ~10K variables with linear constraints
- Non-linear integer arithmetic: much harder, may timeout
- Use `set_param('timeout', 30000)` for time limits (milliseconds)
- Incremental solving: `s.push()` / `s.pop()` for adding/removing constraints

### OR-Tools CP-SAT
- State-of-the-art for many combinatorial problems
- Often beats PuLP/CBC on scheduling and assignment
- Scales to millions of variables for well-structured problems
- Use `solver.parameters.max_time_in_seconds` for time limits
