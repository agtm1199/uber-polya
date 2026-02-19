# Study Schedule

## Problem

A student has 6 subjects to study across 5 time slots per day (morning, late-morning, afternoon, late-afternoon, evening). Some subjects share prerequisites or overlapping content and should not be studied in adjacent time slots to avoid confusion. Create a weekly study timetable by assigning each subject to a time slot such that conflicting subjects never occupy neighboring slots.

## Files

| File | Description |
|------|-------------|
| `study_solver.py` | Graph coloring solver using NetworkX greedy_color on a subject conflict graph |

## Requirements

```bash
pip install networkx
```

## Quick Run

```bash
python3 study_solver.py
```

## Expected Output

- All 6 subjects assigned to time slots (colors 0-4)
- No two conflicting subjects share adjacent time slots
- A printable weekly timetable grid

## Algorithm

Graph coloring on a conflict graph. Vertices represent subjects, edges represent conflicts (subjects that should not be in adjacent slots). Colors represent time slots. Uses NetworkX's `greedy_color` with the largest-first strategy. An adjacency constraint is enforced by expanding the conflict graph: if subjects A and B conflict, we add edges not just between A-B but also between any subjects whose assigned slots would be adjacent.

## Key Concepts

- **Graph coloring** -- assigning labels (colors/slots) to vertices subject to constraints
- **Conflict graphs** -- modeling incompatibility between entities as edges
- **Greedy coloring heuristic** -- largest-first strategy for efficient approximate coloring
- **Constraint verification** -- independent check that no adjacency conflicts exist
- **Timetable scheduling** -- practical application of combinatorial optimization
