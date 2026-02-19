# Pre-Built Model Templates

**Scope**: Universal (templates for the 5 most common problem patterns)

Fill-in-the-blank formal model templates for rapid modeling. Each template is a skeleton that Claude fills by mapping the user's domain language to the template's placeholders. Read the template that matches the problem classification from problem-classification.md.

---

## How to Use These Templates

1. Identify the problem type using **problem-classification.md**
2. Select the matching template below
3. Replace each `⟨placeholder⟩` with the user's domain-specific entities
4. Walk through the checklist at the end of each template
5. Present the filled template to the user for confirmation

---

## Template 1: Assignment / Matching

**Use when**: The user wants to assign items from one group to items in another group (people to tasks, resources to needs, students to courses).

**Matches**: ASSIGN branch in problem-classification.md
**Structure**: Bipartite Graph (structures.md §1.4) or ILP (§7.1)
**Algorithm**: Hungarian (A16), Hopcroft-Karp (A15), or ILP (A32)

### Formal Model

```
SETS
  ⟨left_set_name⟩ = {⟨entity_1⟩, ⟨entity_2⟩, ..., ⟨entity_m⟩}    -- ⟨left_description⟩
  ⟨right_set_name⟩ = {⟨entity_1⟩, ⟨entity_2⟩, ..., ⟨entity_n⟩}   -- ⟨right_description⟩

PARAMETERS
  ⟨score_name⟩[i][j] = ⟨score_description⟩ for i in ⟨left_set⟩, j in ⟨right_set⟩
  ⟨capacity_left⟩ = max assignments per ⟨left_entity⟩    (default: 1)
  ⟨capacity_right⟩ = max assignments per ⟨right_entity⟩  (default: 1)

DECISION VARIABLES
  x[i][j] in {0, 1}  -- 1 if ⟨left_entity⟩ i assigned to ⟨right_entity⟩ j

OBJECTIVE
  ⟨Maximize/Minimize⟩ Σ_i Σ_j ⟨score_name⟩[i][j] * x[i][j]

CONSTRAINTS
  C1 (⟨left⟩ capacity):   Σ_j x[i][j] <= ⟨capacity_left⟩    for all i
  C2 (⟨right⟩ capacity):  Σ_i x[i][j] <= ⟨capacity_right⟩   for all j
  C3 (coverage, if needed): Σ_i x[i][j] >= 1                  for all j
  C4 (eligibility):         x[i][j] = 0 if ⟨not_eligible(i,j)⟩
```

### Fill-in Checklist

- [ ] Both sets clearly identified and enumerated
- [ ] Score/cost matrix defined (or set to 1 if unweighted matching)
- [ ] Capacity constraints reflect real limits (one-to-one? one-to-many?)
- [ ] Coverage requirement specified (must every right entity be assigned?)
- [ ] Eligibility restrictions captured (not all pairs may be valid)
- [ ] Objective direction correct (maximize quality? minimize cost?)
- [ ] Integrality: x is binary, not continuous (see common-mistakes.md M1)

### Quick Variant Guide

| Variant | Change |
|---|---|
| One-to-one (perfect matching) | capacity_left = capacity_right = 1, coverage = 1 |
| One-to-many (workload) | capacity_left > 1 |
| Minimum cost assignment | Minimize objective |
| Maximum weight matching | Maximize objective |
| Feasibility only (no optimization) | Drop objective, check if assignment exists |
| With preferences (stable matching) | Use Gale-Shapley (A17) instead of ILP |

---

## Template 2: Scheduling / Coloring

**Use when**: The user wants to schedule events into time slots with no conflicts, or assign resources so no two conflicting entities share the same resource.

**Matches**: SCHEDULE branch in problem-classification.md
**Structure**: Simple Graph (structures.md §1.1) for conflict graph, then Coloring
**Algorithm**: Greedy coloring (A21), exact coloring (A22), or ILP (A32)

### Formal Model

```
SETS
  ⟨entity_set⟩ = {⟨entity_1⟩, ..., ⟨entity_n⟩}        -- ⟨things to schedule⟩
  ⟨resource_set⟩ = {⟨slot_1⟩, ..., ⟨slot_k⟩}           -- ⟨time slots / rooms / channels⟩
    (k may be a variable to minimize)

CONFLICT GRAPH
  V = ⟨entity_set⟩
  E = {{⟨entity_i⟩, ⟨entity_j⟩} : ⟨conflict_condition(i, j)⟩}
  -- Two entities conflict if ⟨they share a student / use same machine / etc.⟩

DECISION VARIABLES
  color[i] in {1, ..., k}  -- the ⟨resource⟩ assigned to ⟨entity⟩ i

OBJECTIVE
  Minimize k  (= number of distinct ⟨resources⟩ used)

CONSTRAINTS
  C1 (no conflicts): color[i] ≠ color[j]  for all {i, j} in E
  C2 (capacity, if applicable): |{i : color[i] = c}| <= ⟨max_per_slot⟩  for all c
  C3 (preassignments, if any): color[⟨entity⟩] = ⟨fixed_slot⟩
```

### Fill-in Checklist

- [ ] Entity set identified (what is being scheduled?)
- [ ] Conflict condition precisely defined (when can't two entities share a slot?)
- [ ] Conflict graph is undirected (conflicts are symmetric -- see common-mistakes.md M2)
- [ ] Resource set is explicit or to be minimized
- [ ] Capacity per slot considered (or unlimited?)
- [ ] Any preassigned / fixed slots captured
- [ ] Is the objective to minimize slots, or to fit into a fixed number?

### Quick Variant Guide

| Variant | Change |
|---|---|
| Fixed number of slots (k given) | Feasibility: can we k-color the graph? |
| Minimize slots used | Optimization: minimize chromatic number |
| Weighted conflicts | Edges have weights; use weighted coloring or ILP |
| With preferences | Add soft constraints or secondary objective |
| List coloring (restricted choices) | Each entity has a list of valid slots |
| With precedence constraints | Combine with DAG / topological sort (A3) |

---

## Template 3: Routing / Shortest Path

**Use when**: The user wants to find the best route between locations, or visit a set of locations optimally.

**Matches**: ROUTE branch in problem-classification.md
**Structure**: Weighted Graph (structures.md §1.3) or Weighted Digraph (§1.2)
**Algorithm**: Dijkstra (A8), Bellman-Ford (A9), TSP (A28-A30)

### Formal Model

```
GRAPH
  V = {⟨location_1⟩, ..., ⟨location_n⟩}       -- ⟨locations / nodes / stops⟩
  E = {(⟨loc_i⟩, ⟨loc_j⟩) : ⟨connection_exists(i,j)⟩}
  w(i, j) = ⟨cost / distance / time from i to j⟩

  Directed?  ⟨yes/no⟩  -- are routes one-way?
  Negative weights?  ⟨yes/no⟩  -- determines algorithm choice

QUERY TYPE (choose one)
  □ Point-to-point: Find shortest path from ⟨source⟩ to ⟨target⟩
  □ Single-source: Find shortest paths from ⟨source⟩ to all others
  □ All-pairs: Find shortest paths between all pairs
  □ Visit all: Find route visiting ⟨all / subset⟩ of locations (TSP variant)

CONSTRAINTS (if any)
  C1 (must-visit): Path must pass through ⟨waypoints⟩
  C2 (capacity): Vehicle carries at most ⟨capacity⟩ units
  C3 (time windows): Location i must be visited between ⟨t_start⟩ and ⟨t_end⟩

OUTPUT
  Path: sequence of vertices (⟨v_1⟩, ⟨v_2⟩, ..., ⟨v_k⟩)
  Cost: Σ w(v_i, v_{i+1})
```

### Fill-in Checklist

- [ ] Graph is correctly directed or undirected (see common-mistakes.md M2)
- [ ] Edge weights are all non-negative? (determines Dijkstra vs Bellman-Ford)
- [ ] Query type selected (point-to-point vs all-pairs vs TSP)
- [ ] Source and target specified (for point-to-point)
- [ ] Additional constraints captured (capacity, time windows, must-visit)
- [ ] TSP variant: must return to start? visit all or subset?

### Quick Variant Guide

| Variant | Algorithm | Solver |
|---|---|---|
| Shortest path, non-negative weights | Dijkstra (A8) | NetworkX |
| Shortest path, negative weights | Bellman-Ford (A9) | NetworkX |
| All-pairs shortest path | Floyd-Warshall (A10) or repeated Dijkstra | NetworkX |
| Visit all locations, return home (TSP) | Held-Karp (A28) for n<=20, ILP for larger | OR-Tools |
| Multiple vehicles | Vehicle Routing Problem | OR-Tools routing |
| Maximum throughput | Max Flow (A19) | NetworkX |

---

## Template 4: Selection / Knapsack

**Use when**: The user wants to choose the best subset of items under a budget, weight, or resource constraint.

**Matches**: SELECT/PACK branch in problem-classification.md
**Structure**: ILP (structures.md §7.1)
**Algorithm**: Knapsack DP (A33), ILP (A32), or Set Cover (A47)

### Formal Model

```
SETS
  ⟨item_set⟩ = {⟨item_1⟩, ..., ⟨item_n⟩}    -- ⟨items / projects / features⟩

PARAMETERS
  ⟨value_name⟩[i] = ⟨benefit / profit / score⟩ of item i
  ⟨cost_name⟩[i]  = ⟨cost / weight / size⟩ of item i
  ⟨budget⟩         = ⟨total capacity / budget limit⟩

DECISION VARIABLES
  x[i] in {0, 1}  -- 1 if ⟨item⟩ i is selected

OBJECTIVE
  Maximize Σ_i ⟨value_name⟩[i] * x[i]

CONSTRAINTS
  C1 (budget):      Σ_i ⟨cost_name⟩[i] * x[i] <= ⟨budget⟩
  C2 (min select):  Σ_i x[i] >= ⟨min_items⟩  (if applicable)
  C3 (max select):  Σ_i x[i] <= ⟨max_items⟩  (if applicable)
  C4 (dependencies): x[j] <= x[i]  if ⟨item j requires item i⟩
  C5 (conflicts):    x[i] + x[j] <= 1  if ⟨items i,j are mutually exclusive⟩
  C6 (coverage):     Σ_{i in S_j} x[i] >= 1 for each requirement j  (set cover variant)
```

### Fill-in Checklist

- [ ] Items and their values clearly identified
- [ ] Cost/weight for each item defined
- [ ] Budget/capacity constraint quantified
- [ ] Variables are binary (see common-mistakes.md M1)
- [ ] Dependencies between items captured (if any)
- [ ] Mutually exclusive items captured (if any)
- [ ] Is this pure selection or does it have coverage requirements?
- [ ] Objective is maximize value (not minimize cost -- unless cost minimization)

### Quick Variant Guide

| Variant | Change |
|---|---|
| Classic 0/1 knapsack | Single budget constraint, binary variables |
| Multiple knapsacks | Multiple capacity constraints (multi-dimensional) |
| Fractional allowed | Relax x to [0,1] -- greedy by value/cost ratio (A44) |
| Set cover | Objective: minimize items selected; constraint: cover all requirements |
| Multi-criteria | Multiple objectives → Pareto analysis or weighted sum |
| Unbounded (copies allowed) | x[i] in {0, 1, 2, ...} instead of binary |

---

## Template 5: Dependency Ordering

**Use when**: The user wants to order tasks respecting dependencies, find a critical path, or determine if a valid ordering exists.

**Matches**: SCHEDULE (dependencies) branch in problem-classification.md
**Structure**: DAG (structures.md §1.6)
**Algorithm**: Topological Sort (A3), Critical Path / Longest Path (A12)

### Formal Model

```
SETS
  ⟨task_set⟩ = {⟨task_1⟩, ..., ⟨task_n⟩}     -- ⟨tasks / courses / build steps⟩

PARAMETERS
  ⟨duration⟩[i] = ⟨time / effort⟩ for task i   (if scheduling)

DEPENDENCY GRAPH
  V = ⟨task_set⟩
  A = {(⟨task_i⟩, ⟨task_j⟩) : ⟨task_i must complete before task_j⟩}
  -- This must be a DAG (no circular dependencies)

QUERY TYPE (choose one)
  □ Valid ordering: Find any topological sort of the DAG
  □ All valid orderings: Enumerate all topological sorts
  □ Critical path: Find the longest path (= minimum makespan)
  □ Earliest/latest start: Compute slack for each task
  □ Feasibility: Can all dependencies be satisfied? (= is it a DAG?)

OUTPUT
  Ordering: (⟨task_π(1)⟩, ⟨task_π(2)⟩, ..., ⟨task_π(n)⟩) respecting all dependencies
  Critical path: sequence of tasks with zero slack
  Makespan: sum of durations along critical path
  Slack[i]: latest_start[i] - earliest_start[i]
```

### Fill-in Checklist

- [ ] All tasks identified and enumerated
- [ ] Dependencies are directed correctly: (prerequisite → dependent) (see common-mistakes.md M2)
- [ ] Graph is verified to be acyclic (cycle = impossible ordering)
- [ ] Task durations specified (for critical path analysis)
- [ ] Resource constraints considered? (if tasks compete for machines, this becomes a scheduling ILP -- see Template 2)
- [ ] Query type selected (ordering vs critical path vs feasibility)

### Quick Variant Guide

| Variant | Algorithm | Solver |
|---|---|---|
| Any valid ordering | Topological Sort (A3) | NetworkX |
| Critical path (makespan) | Longest Path in DAG (A12) | NetworkX |
| All valid orderings | All Topological Sorts (A71) | NetworkX |
| With resource constraints | Scheduling ILP (A32) | PuLP / OR-Tools |
| Detect cycles | Cycle Detection (A4) | NetworkX |
| Parallel execution | Critical path + slack analysis | NetworkX |

---

## Cross-Reference Index

| Template | Structures (structures.md) | Algorithms (algorithms.md) | Protocols (solving-protocols.md) |
|---|---|---|---|
| 1. Assignment | §1.4 Bipartite, §7.1 ILP | §4 Matching (A15-A17), §10 ILP (A32) | Optimization (ILP/LP) |
| 2. Scheduling | §1.1 Simple Graph, §7.3 Scheduling | §6 Coloring (A21-A22), §10 ILP (A32) | Graph, Optimization |
| 3. Routing | §1.3 Weighted Graph, §1.2 Digraph | §2 Shortest Path (A8-A12), §9 TSP (A28-A30) | Graph |
| 4. Selection | §7.1 ILP | §10 ILP (A32), §11 DP (A33-A34) | Optimization, DP |
| 5. Dependency | §1.6 DAG | §1 Topo Sort (A3), §2 Longest Path (A12) | Graph |

Also see: **problem-classification.md** for identifying which template to use, **common-mistakes.md** for pitfalls specific to each pattern.
