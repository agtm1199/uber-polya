# Inspector Assignment -- Full Walkthrough

A complete walkthrough of the food safety inspector assignment problem, demonstrating integer linear programming, LP relaxation analysis, sensitivity testing, and stakeholder-ready visualizations through the uber-polya trilogy.

**Runnable code**: `examples/inspector-assignment/`

> **Note**: The skill outputs shown below are representative of what Claude produces. Exact wording, formatting, and detail level will vary between runs.

---

## The Problem

Assign 6 food safety inspectors to 10 facilities to **maximize total expertise**. The facilities come in 5 types (2 each): dairy, meat, bakery, seafood, and beverage. Each inspector has different expertise scores (1-9) for each facility type.

**Constraints**:
- Each inspector handles **at most 3** facilities
- Each facility needs **exactly 1** inspector

**Expertise matrix** (inspector x facility type):

| Inspector | Dairy | Meat | Bakery | Seafood | Beverage |
|-----------|-------|------|--------|---------|----------|
| Alice     | 9     | 7    | 4      | 3       | 6        |
| Bob       | 5     | 9    | 6      | 8       | 3        |
| Carol     | 7     | 4    | 9      | 5       | 8        |
| Dave      | 3     | 6    | 5      | 9       | 4        |
| Eve       | 6     | 3    | 7      | 4       | 9        |
| Frank     | 8     | 5    | 3      | 6       | 7        |

---

## Phase 1: /uber-model

```
/uber-model Assign 6 inspectors to 10 facilities (2 dairy, 2 meat, 2 bakery,
2 seafood, 2 beverage). Maximize total expertise score. Each inspector
handles at most 3 facilities. Each facility needs exactly 1 inspector.
Expertise scores vary by inspector and facility type.
```

Claude works through Polya's understanding and planning phases. Representative output:

### Problem Understanding

> **Problem Type**: Problem to Find (optimization)
> **Unknown**: An assignment of inspectors to facilities that maximizes total expertise
> **Data**:
>   - 6 inspectors: {Alice, Bob, Carol, Dave, Eve, Frank}
>   - 10 facilities: {F1, ..., F10}, each with a type in {dairy, meat, bakery, seafood, beverage}
>   - Expertise matrix: 6 inspectors x 5 facility types, scores from 1-9
>   - Capacity: each inspector handles at most 3 facilities
>   - Coverage: each facility is assigned to exactly 1 inspector
> **Conditions**:
>   1. (Capacity) For each inspector i: |assigned(i)| <= 3
>   2. (Coverage) For each facility f: |assigned_to(f)| = 1
>   3. (Objective) Maximize sum of expertise(inspector, facility_type(f)) over all assignments

### Structure Recognition

> **Structure**: Capacitated Weighted b-Matching on a bipartite graph
>
> This is a weighted bipartite assignment problem with capacity constraints. The bipartite graph has inspectors on one side and facilities on the other. Edge weights are expertise scores. The capacity constraint makes this a b-matching (each node has a degree bound).
>
> | Real-World Concept | Mathematical Object |
> |---|---|
> | Inspector | Left vertex in bipartite graph |
> | Facility | Right vertex in bipartite graph |
> | "Inspector i can inspect facility f" | Edge (i, f) with weight = expertise score |
> | "At most 3 facilities per inspector" | Degree bound b(i) = 3 for left vertices |
> | "Exactly 1 inspector per facility" | Degree bound b(f) = 1 for right vertices |
> | Total expertise | Sum of edge weights in the matching |

### Formal Model

> **Domain**: Optimization (Integer Linear Programming)
> **Variables**: x_{i,f} in {0, 1} for each inspector i and facility f (1 = assigned, 0 = not)
> **Constraints**:
>   1. Capacity: sum_f x_{i,f} <= 3 for each inspector i
>   2. Coverage: sum_i x_{i,f} = 1 for each facility f
> **Objective**: Maximize sum_{i,f} score(i, type(f)) * x_{i,f}
>
> **Key observation**: The constraint matrix is totally unimodular (it is a bipartite incidence matrix with degree bounds). This means the LP relaxation is guaranteed to have an integer optimal solution. We can solve the LP and get the ILP optimum for free.
>
> **Next Steps (for /uber-solve)**: ILP via PuLP/CBC. Expected to solve in milliseconds for this instance size. LP relaxation provides a tight bound.

---

## Phase 2: /uber-solve

```
/uber-solve
```

Claude classifies the problem, implements the ILP, solves it, and runs independent verification.

### Problem Classification

> **Named Problem**: Capacitated Weighted Bipartite b-Matching
> **Complexity Class**: NP-hard in general (ILP), but the constraint matrix is totally unimodular -- LP relaxation is integral, so effectively polynomial
> **Instance Size**: 6 inspectors x 10 facilities = 60 binary variables, 16 constraints
> **Solution Strategy**: ILP solver (PuLP/CBC); LP relaxation as optimality certificate
> **Correctness Guarantee**: Exact optimal (LP relaxation = ILP optimum for TU matrices)

### The ILP Formulation

The solver (from `examples/inspector-assignment/inspector_solver.py`) builds the model in PuLP:

```python
prob = LpProblem("inspector_assignment", LpMaximize)

# Binary decision variables
x = {(i, f): LpVariable(f"x_{i}_{f}", cat=LpBinary)
     for i in inspectors for f in facilities}

# Objective: maximize total expertise
prob += lpSum(score(i, f) * x[i, f]
              for i in inspectors for f in facilities)

# Capacity: each inspector handles at most 3
for i in inspectors:
    prob += lpSum(x[i, f] for f in facilities) <= 3

# Coverage: each facility gets exactly 1 inspector
for f in facilities:
    prob += lpSum(x[i, f] for i in inspectors) == 1

prob.solve(PULP_CBC_CMD(msg=False))
```

### Solution

> **Objective**: 90 out of 90 theoretical maximum **(100% efficiency)**
> **LP Relaxation**: 90.0 (gap = 0 -- confirms TU integrality)
> **Solver status**: Optimal
> **Time**: ~0.009s
>
> **Assignment**:
>
> | Inspector | Facilities | Specialty | Score |
> |-----------|-----------|-----------|-------|
> | Alice | F1, F2 | Dairy | 9 + 9 = 18 |
> | Bob | F3, F4 | Meat | 9 + 9 = 18 |
> | Carol | F5, F6 | Bakery | 9 + 9 = 18 |
> | Dave | F7, F8 | Seafood | 9 + 9 = 18 |
> | Eve | F9, F10 | Beverage | 9 + 9 = 18 |
> | Frank | (none) | Reserve | 0 |
>
> Every facility is assigned to the inspector with the **highest expertise** for that facility type. A perfect assignment exists because each facility type has a distinct top-scoring inspector.

### Independent Verification

> ```
> capacity_Alice                 PASS  (2 <= 3)
> capacity_Bob                   PASS  (2 <= 3)
> capacity_Carol                 PASS  (2 <= 3)
> capacity_Dave                  PASS  (2 <= 3)
> capacity_Eve                   PASS  (2 <= 3)
> capacity_Frank                 PASS  (0 <= 3)
> coverage_F1 ... coverage_F10   PASS  (each = 1)
> all_facilities_covered         PASS
> objective_recomputed           90
> ```

### Sensitivity: What if an inspector leaves?

> | Inspector Removed | New Objective | Change | Risk Level |
> |-------------------|--------------|--------|------------|
> | Alice leaves | 88 | -2 (-2.2%) | LOW |
> | Bob leaves | 85 | -5 (-5.6%) | MODERATE |
> | Carol leaves | 85 | -5 (-5.6%) | MODERATE |
> | Dave leaves | 86 | -4 (-4.4%) | LOW |
> | Eve leaves | 87 | -3 (-3.3%) | LOW |
> | Frank leaves | 90 | 0 (0.0%) | NONE |

---

## Phase 3: /uber-interpret

```
/uber-interpret
```

Claude translates the ILP solution into stakeholder-ready insights with visualizations and recommendations.

### Bottom Line

> A **perfect assignment exists**. Every facility gets its single best inspector. The total expertise score is 90 out of a theoretical maximum of 90 (100%). Frank is unassigned and serves as reserve capacity.

### Stakeholder Visualizations

Claude generates three charts (see `examples/inspector-assignment/inspector_viz.py`):

**1. Expertise Heatmap** (`viz_assignment_matrix.png`)
A 6x10 matrix showing all expertise scores, with the optimal assignments highlighted by thick borders. The key insight is visible at a glance: every assigned cell contains a 9, the maximum possible score for that facility type.

**2. Sensitivity Tornado** (`viz_sensitivity_tornado.png`)
A horizontal bar chart showing the impact of losing each inspector. Bob and Carol are the most critical (5-point drop each, MODERATE risk). Frank has zero impact (reserve).

**3. Workload Distribution** (`viz_workload_expertise.png`)
Side-by-side bar charts showing facilities per inspector (all at 2 out of 3 capacity) and score contribution (all at 18, except Frank at 0). The workload is perfectly balanced across active inspectors.

### Sensitivity Deep Dive

> **Structural insight**: The perfect score of 90 exists because the expertise matrix has a clear block-diagonal structure -- each facility type has one dominant inspector. If the expertise scores were more uniform (e.g., all 7s and 8s), the problem would become a genuine trade-off.
>
> **Critical personnel**: Bob and Carol are the highest-risk departures. If either leaves, the solver must reassign their specialty to a less-qualified inspector.
>   - Bob leaving: meat facilities must go to Alice (score 7) or Dave (score 6) instead of Bob (score 9)
>   - Carol leaving: bakery facilities must go to Eve (score 7) instead of Carol (score 9)
>
> **Reserve capacity**: Frank is currently unassigned, but he is the second-best dairy inspector (score 8). He provides insurance against Alice's departure (objective drops only 2 points instead of what it would without a strong backup).
>
> **Capacity slack**: Every active inspector uses 2 of 3 slots. There is room to add 5 more facilities without hiring, though expertise scores for non-specialty types are lower.

### Recommendations

> **Primary recommendation**: Implement the optimal assignment as shown. Every facility gets its best available inspector.
>
> **Key constraints to monitor**:
> 1. Bob and Carol are critical personnel -- cross-train backups for meat and bakery inspection
> 2. The 3-facility capacity limit is not binding (all inspectors are at 2/3) -- future facility additions are feasible without restructuring
>
> **Risk mitigation**:
> - Keep Frank as a dedicated reserve for dairy and beverage coverage
> - If the team drops below 5 inspectors, the remaining capacity (5 x 3 = 15) can still cover all 10 facilities, but with significant expertise degradation
>
> **Limitations**:
> - The model assumes expertise scores are static. In reality, inspectors gain expertise over time through repeated assignments.
> - Travel time between facilities is not modeled. Geographic clustering may override pure expertise optimization.
> - The model treats all facility types equally. Regulatory risk may warrant weighting dairy or meat facilities higher.

### Knowledge Transfer

> **Pattern**: "Assign people to roles by skill, respecting capacity limits" maps to **weighted bipartite b-matching**, solved via ILP.
>
> **Other applications of this pattern**:
> - Student-to-project assignment in courses
> - Nurse-to-shift scheduling in hospitals
> - Truck-to-route assignment in logistics
> - Reviewer-to-paper assignment in peer review
>
> **Key insight**: When the constraint matrix is totally unimodular (bipartite assignment with simple capacity/coverage), the LP relaxation is automatically integral. You get the speed of LP with the exactness of ILP.
>
> **Decision framework**: When you encounter "assign N agents to M tasks by skill with capacity limits," reach for:
> 1. PuLP + CBC for the ILP formulation
> 2. LP relaxation as an optimality certificate
> 3. Sensitivity analysis (remove each agent) to identify personnel risk

---

## Running the Code

```bash
cd examples/inspector-assignment/

# Run the full solver with verification and sensitivity analysis
pip install pulp  # if not already installed
python inspector_solver.py

# Generate the three stakeholder visualizations
pip install matplotlib numpy  # if not already installed
python inspector_viz.py
```

Expected output from `inspector_solver.py`:

```
  SOLUTION REPORT: Food Safety Inspector Assignment

  Status:     Optimal
  Objective:  90 (total expertise score)
  LP Bound:   90.0
  Gap:        0.0 (0.0%)

  ASSIGNMENT DETAILS
  Alice      F1(dairy:9), F2(dairy:9)          2/3    18
  Bob        F3(meat:9), F4(meat:9)            2/3    18
  Carol      F5(bakery:9), F6(bakery:9)        2/3    18
  Dave       F7(seafood:9), F8(seafood:9)      2/3    18
  Eve        F9(beverage:9), F10(beverage:9)   2/3    18
  Frank                                         0/3     0
  TOTAL                                        10/18   90

  SENSITIVITY: What if an inspector leaves?
  Remove Alice : obj 88 (-2, -2.2%)  [LOW risk]
  Remove Bob   : obj 85 (-5, -5.6%)  [MODERATE risk]
  Remove Carol : obj 85 (-5, -5.6%)  [MODERATE risk]
  Remove Dave  : obj 86 (-4, -4.4%)  [LOW risk]
  Remove Eve   : obj 87 (-3, -3.3%)  [LOW risk]
  Remove Frank : obj 90 (+0, +0.0%)  [LOW risk]
```

---

## What You Learned

| Concept | Lesson |
|---------|--------|
| **Modeling** | "Assign people to roles by skill with capacity limits" is weighted bipartite b-matching |
| **Algorithm** | ILP via PuLP/CBC solves in milliseconds for practical instance sizes |
| **Total unimodularity** | Bipartite assignment constraints produce TU matrices -- LP relaxation = ILP optimum |
| **Verification** | LP relaxation bound of 90 = ILP solution of 90 proves optimality with zero gap |
| **Sensitivity** | Removing each agent one at a time reveals personnel risk. Bob and Carol are critical |
| **Interpretation** | Three visualizations (heatmap, tornado, workload) serve different stakeholder needs |
| **Knowledge transfer** | The bipartite ILP pattern applies to any "assign agents to tasks by skill" problem |

Previous: [Milking Cows Walkthrough](milking-cows-walkthrough.md) -- a simpler algorithmic problem with interval merging.
