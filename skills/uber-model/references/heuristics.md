# Polya's Heuristics for Mathematical Modeling

**Scope**: Universal (heuristics apply to all domains; DM application examples currently provided for Discrete Mathematics)

Seventeen heuristics drawn from George Polya's "How to Solve It," organized by the phase in which they are most useful. Each heuristic includes:
- **When to use**: Conditions that trigger this heuristic
- **Socratic questions**: Questions to ask the user (adapted from Polya)
- **DM application**: How this heuristic applies specifically to discrete mathematics modeling

---

## Phase 1 Heuristics: Understanding the Problem

### H1: Separate the Condition

**When to use**: The problem has a compound condition with multiple requirements joined by "and," "but," "such that," or implicit conjunction.

**Socratic questions**:
- "The condition has several parts. Can you separate them?"
- "Can you write down each part of the condition independently?"
- "Which parts involve the unknown? Which involve only the data?"
- "Are any two parts redundant -- does one imply the other?"
- "Are any two parts contradictory?"

**DM application**: Compound conditions often map to different types of constraints in the model. Separating them reveals:
- **Hard constraints** (must satisfy) vs **soft constraints** (prefer to satisfy)
- **Structural constraints** (define the universe) vs **behavioral constraints** (restrict solutions)
- **Local constraints** (involve one element) vs **global constraints** (involve all elements)

Example: "Assign employees to projects such that each employee handles at most 2 projects, each project has exactly 1 employee, and qualified employees are preferred" separates into:
1. Capacity constraint: degree(employee) <= 2
2. Coverage constraint: degree(project) = 1
3. Qualification constraint: edge exists only if qualified
4. Objective: maximize qualified assignments

---

### H2: Introduce Notation

**When to use**: Always. Begin as soon as the unknown and data are identified.

**Socratic questions**:
- "What letter should denote the unknown?"
- "What names shall we give to the key sets?"
- "Is there a standard notation for this type of object?"
- "Does the notation suggest the right associations?" (n for count, G for graph, w for weight)

**DM application**: Good notation choices in discrete math:
- Sets: uppercase (V, E, S, A, B)
- Elements: lowercase (v, e, s, a, b)
- Counts: n, m, k
- Functions/mappings: f, g, w (weight), c (cost/capacity), d (degree)
- Graphs: G = (V, E), digraphs: D = (V, A)
- Binary variables: x_ij in {0, 1}
- Indicator: 1 if condition, 0 otherwise

Avoid: Overloaded symbols, ambiguous subscripts, notation that hides structure.

---

### H3: Draw a Figure

**When to use**: The problem involves spatial, relational, or structural relationships. Almost always useful for graph-theoretic or combinatorial problems.

**Socratic questions**:
- "Can you draw a picture of this situation?"
- "What would a small example look like if you sketched it?"
- "Can you represent the relationships as a diagram?"
- "What goes on the nodes? What goes on the edges?"

**DM application**: Types of figures useful in discrete math modeling:
- **Graph/network diagram**: Nodes and edges showing relationships
- **Venn diagram**: Set overlaps and containment
- **Hasse diagram**: Partial order relationships
- **Table/matrix**: Bipartite relationships, adjacency, assignment
- **Decision tree**: Branching choices
- **Lattice diagram**: Ordered structures with meets and joins
- **State diagram**: Transitions between states

Use ASCII art when producing figures. Example:
```
  A---B       A → B
  |\ /|       ↑   ↓
  | X |       D ← C
  |/ \|
  C---D
```

---

### H4: Check Feasibility

**When to use**: Before investing effort in modeling, verify the problem can have a solution. Especially important when conditions seem tight or contradictory.

**Socratic questions**:
- "Is it possible to satisfy the condition at all?"
- "Is there an obvious obstruction?"
- "Can you think of even one example that satisfies all conditions?"
- "If you relax one condition, does a solution become easy to find?"
- "Does a counting argument show impossibility?" (e.g., pigeonhole principle)

**DM application**: Quick feasibility checks:
- **Pigeonhole**: n items into k bins, n > k implies some bin has >= 2
- **Parity**: Sum of odd number of odds is odd -- can't equal an even target
- **Degree sum**: Sum of degrees must be even in any graph
- **Capacity**: Total demand <= total supply for feasible flow
- **Bipartiteness**: Odd cycle prevents 2-coloring

---

## Phase 2 Heuristics: Devising a Plan

### H5: Analogy

**When to use**: The problem structure reminds you of something from a different domain. Or: you're stuck and need a fresh perspective by mapping to familiar territory.

**Socratic questions**:
- "Do you know an analogous problem?"
- "Is there a simpler version of this in a different setting?"
- "What if we changed the domain -- would the structure be the same?"
- "Is this the 3D version of a 2D problem you know?"

**DM application**: Classic discrete math analogies:

| Source Problem | Analogous Problem | Shared Structure |
|---|---|---|
| Map coloring | Exam scheduling | Graph coloring |
| Shortest route | Cheapest network path | Weighted shortest path |
| Worker assignment | Stable marriage | Bipartite matching |
| Bin packing | Memory allocation | Bin packing / knapsack |
| Circuit design | Boolean satisfiability | SAT |
| Protein folding | Lattice path optimization | Dynamic programming |
| Epidemic spread | Information cascade | Graph diffusion |
| Voting systems | Tournament ranking | Tournament graphs |
| Supply chain | Network flow | Max flow / min cut |
| DNA sequence | String matching | Edit distance |
| Team formation | Set cover | Covering problem |
| Puzzle solving | State space search | BFS/DFS on implicit graph |

---

### H6: Decomposition

**When to use**: The problem is large or has clearly separable parts. A compound condition has been separated (H1) and the parts can be attacked independently.

**Socratic questions**:
- "Can you break this into smaller, independent subproblems?"
- "Is there a natural partition of the data?"
- "If you solved one part, would the rest become easier?"
- "Can you identify a bottleneck -- one key subproblem that unlocks the rest?"

**DM application**: Decomposition patterns in discrete math:
- **Graph decomposition**: Connected components, biconnected components, strongly connected components
- **Divide and conquer**: Split input, solve halves, combine
- **Constraint decomposition**: Solve structural constraints first, then optimize
- **Temporal decomposition**: Model in stages (build feasibility, then optimize)
- **Hierarchical decomposition**: Solve at coarse level, refine at fine level

---

### H7: Generalization (Inventor's Paradox)

**When to use**: The specific problem seems hard. Counterintuitively, a more general version may be easier because it provides more structure to work with.

*Polya: "The more ambitious plan may have more chances of success."*

**Socratic questions**:
- "Would a more general version of this problem actually be easier?"
- "If you replaced specific numbers with variables, does a pattern emerge?"
- "Can you parameterize the problem?"
- "Does proving a stronger statement give you more to work with?"

**DM application**:
- Proving "the sum of first n cubes equals [n(n+1)/2]^2" is easier than proving "1+8+27+64=100" because the general form reveals the pattern and enables induction.
- Finding "the optimal assignment for any bipartite graph" is easier than a specific instance because you can use general algorithms.
- Modeling "resource allocation with k resource types" may reveal structure hidden when k=1.

---

### H8: Specialization

**When to use**: The general problem is opaque. Test with small, concrete cases to discover patterns before modeling the general case.

**Socratic questions**:
- "What happens if n = 1? n = 2? n = 3?"
- "Can you solve a tiny example by hand?"
- "What does the answer look like for the simplest non-trivial case?"
- "Do you see a pattern in these special cases?"

**DM application**: Specialization strategies:
- **Small cases**: Set n=1,2,3 and enumerate
- **Extreme cases**: What if a constraint is removed? What if it's maximally tight?
- **Symmetric cases**: What if all elements are identical?
- **Degenerate cases**: Empty graph, complete graph, single node
- **Known instances**: Is there a named special case? (e.g., bipartite is a special case of general graph)

---

### H9: Working Backwards

**When to use**: The unknown is well-defined but the path from data to unknown is unclear. Start from what you want and ask what would be needed to produce it.

**Socratic questions**:
- "Suppose you had the answer. What would it look like?"
- "What mathematical object would contain or represent the answer?"
- "What would need to be true for this answer to be correct?"
- "Working back from the answer, what's the last step before you have it?"

**DM application**:
- If the unknown is a coloring → you need a graph → what are the conflicts?
- If the unknown is an optimal path → you need a weighted graph → what are the costs?
- If the unknown is a proof → what's the last inference step → what lemma is needed?
- If the unknown is a count → what are you counting → what's the counting structure?

---

### H10: Auxiliary Elements

**When to use**: The direct connection between data and unknown is missing. Introducing a helper variable, intermediate structure, or auxiliary problem creates a stepping stone.

**Socratic questions**:
- "Should you introduce some auxiliary element to make the connection?"
- "Is there an intermediate quantity that connects what you know to what you seek?"
- "Would a helper graph, a dummy node, or a slack variable help?"
- "Can you introduce a new variable that simplifies the constraints?"

**DM application**: Common auxiliary elements:
- **Dummy nodes**: Source/sink in network flow
- **Slack variables**: Convert inequalities to equalities in LP
- **Complement graph**: G' where edges represent non-adjacency
- **Auxiliary graph**: Line graph, intersection graph, conflict graph
- **Indicator variables**: x_ij = 1 if item i assigned to bin j
- **Intermediate results**: First count something easier, then transform

---

### H11: Restate the Problem

**When to use**: The current formulation is stuck. A different perspective may unlock progress.

**Socratic questions**:
- "Could you restate the problem in different terms?"
- "What if you looked at the complement instead?"
- "Can you phrase this as a different type of problem entirely?"
- "Go back to definitions. What does [key term] really mean?"
- "What is the contrapositive of what you're trying to prove?"

**DM application**: Restatement strategies:
- **Dualization**: Max flow ↔ min cut, matching ↔ vertex cover
- **Complementation**: Find max independent set ↔ find min vertex cover
- **Contrapositive**: Prove "if not B then not A" instead of "if A then B"
- **Negation**: "No assignment exists" ↔ "every assignment violates some condition"
- **Change of representation**: Adjacency matrix ↔ edge list ↔ incidence matrix

---

### H12: Related Problem

**When to use**: You recognize the unknown type but can't find the right structure. Look for a solved problem whose unknown is the same type.

**Socratic questions**:
- "Do you know a problem with the same type of unknown?"
- "Here is a problem related to yours, already solved. Could you use its method?"
- "Could you use the result of a simpler, related problem?"
- "What's the textbook name for this type of problem?"

**DM application**: Consult the cross-domain pattern table in `structures.md`. Match the unknown type:
- Unknown is an assignment → matching, assignment problem, stable marriage
- Unknown is a count → combinatorial counting, inclusion-exclusion, generating functions
- Unknown is an ordering → topological sort, Hamiltonian path, linear extension
- Unknown is a partition → graph partition, set partition, number partition
- Unknown is a truth value → SAT, constraint satisfaction, proof

---

## Phase 3 Heuristics: Carrying Out the Plan

### H13: Step Verification

**When to use**: Always, during model construction. Check each mapping and constraint as you write it.

**Socratic questions**:
- "Can you see clearly that this mapping is correct?"
- "Does this constraint accurately capture the original condition?"
- "If you substitute a concrete example, does the constraint hold?"
- "Is this step justified by the problem statement, or are you adding an assumption?"

**DM application**: For each constraint in the formal model:
1. Trace it back to a specific condition in the Problem Understanding
2. Test with a concrete example that should satisfy it
3. Test with a concrete example that should violate it
4. Verify the constraint correctly distinguishes the two

---

### H14: Gap Detection

**When to use**: The model is nearly complete but something feels missing or disconnected.

**Socratic questions**:
- "Is there a logical gap between your data and your constraints?"
- "Does every piece of data appear somewhere in the model?"
- "Is there a condition from Phase 1 that has no corresponding constraint?"
- "Are there implicit assumptions you haven't formalized?"

**DM application**: Common gaps:
- Forgetting the non-negativity constraint (x >= 0)
- Missing the integrality constraint (x in Z, not R)
- Omitting boundary conditions (what happens at n=0?)
- Assuming connectivity without stating it
- Assuming finiteness without stating it

---

## Phase 4 Heuristics: Looking Back

### H15: Result Verification

**When to use**: Always, after the model is complete.

**Socratic questions**:
- "Can you check the model with a very simple example?"
- "What happens at the boundaries -- empty input, single element, maximum size?"
- "Does the model degenerate correctly in trivial cases?"
- "Is the model symmetric where the problem is symmetric?"

**DM application**: Verification tests:
- **Trivial case**: n=0 or n=1 should give trivial/obvious result
- **Small case**: n=2 or n=3 should be verifiable by hand
- **Extreme case**: All constraints tight, or all relaxed
- **Symmetry**: Swap equivalent elements; model should be invariant
- **Dimension**: If input scales by factor k, does the objective scale correctly?

---

### H16: Method Generalization

**When to use**: After successful modeling, consider what broader class of problems this model handles.

**Socratic questions**:
- "Can you use this model, or the method, for some other problem?"
- "What if you relaxed one constraint -- what broader problem would this become?"
- "Is this a special case of a more general model?"
- "What family of problems does this belong to?"

**DM application**: Identify the problem's place in the landscape:
- Is this a special case of a known NP-hard problem? (complexity implications)
- Is this a restricted case that admits polynomial algorithms?
- Does the model generalize to weighted, directed, or multi-dimensional versions?
- Can the same structure model problems in different domains?

---

### H17: Connection to Known Results

**When to use**: After the model is complete, connect it to the existing body of discrete mathematics.

**Socratic questions**:
- "Does this model have a standard name in the literature?"
- "What theorems apply to this structure?"
- "Who first studied this type of problem?"
- "What is the best known algorithm or bound?"

**DM application**: Naming the model enables:
- Looking up known results, bounds, and algorithms
- Finding open problems and active research
- Communicating the model to others using shared vocabulary
- Leveraging existing software implementations

---

## Cross-Reference Index

| Heuristic | Most Relevant References |
|---|---|
| H1 Separate the Condition | **common-mistakes.md** M4 (over-constraining), M5 (under-constraining) |
| H3 Draw a Figure | **structures.md** Cross-Domain Pattern Table (match diagram to structure) |
| H5 Analogy | **problem-classification.md** Quick Pattern Table (natural language → structure) |
| H8 Specialization | **common-mistakes.md** S5 (missing edge cases) |
| H10 Auxiliary Elements | **structures.md** §7.1 ILP (slack/indicator variables), §1 Graph Theory (dummy nodes) |
| H11 Restate / H12 Related | **problem-classification.md** Disambiguation Tips, **structures.md** Cross-Domain Pattern Table |
| H13 Step Verification | **common-mistakes.md** M1-M10 (all modeling mistakes) |
| H17 Known Results | **algorithms.md** Algorithm Selection Matrix, **solvers.md** Solver Selection Guide |
