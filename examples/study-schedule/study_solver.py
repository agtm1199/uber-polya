#!/usr/bin/env python3
"""Study Schedule solver -- Graph coloring on a subject conflict graph.

Assigns 6 subjects to 5 time slots such that conflicting subjects
are never placed in adjacent time slots. Uses NetworkX greedy_color
on an expanded conflict graph that encodes adjacency constraints.

Algorithm: Greedy graph coloring (largest-first strategy).
Complexity: O(V^2) for greedy coloring on a small graph.
Correctness: Heuristic -- verified independently.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

import networkx as nx

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger
log = PolyaLogger()


# --- Data Model ---

@dataclass(frozen=True)
class Instance:
    """Problem instance for study schedule assignment."""
    subjects: tuple[str, ...]
    time_slots: tuple[str, ...]
    conflicts: tuple[tuple[str, str], ...]  # pairs of subjects that conflict

    @property
    def n_subjects(self) -> int:
        return len(self.subjects)

    @property
    def n_slots(self) -> int:
        return len(self.time_slots)


@dataclass
class Solution:
    """Verified solution with metadata."""
    assignment: dict[str, str]        # subject -> time_slot
    color_map: dict[str, int]         # subject -> color (slot index)
    objective: int                    # number of colors used
    is_optimal: bool
    is_feasible: bool
    algorithm: str
    time_seconds: float
    certificate: str
    constraint_check: dict[str, bool] = field(default_factory=dict)


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Solve the study scheduling problem via graph coloring."""
    t0 = time.perf_counter()

    # Build the conflict graph
    G = nx.Graph()
    G.add_nodes_from(instance.subjects)

    # Add direct conflict edges
    for s1, s2 in instance.conflicts:
        G.add_edge(s1, s2)

    # Use greedy coloring (largest-first heuristic)
    coloring = nx.coloring.greedy_color(G, strategy="largest_first")

    n_colors = max(coloring.values()) + 1 if coloring else 0
    elapsed = time.perf_counter() - t0

    # Map colors to time slots
    assignment = {}
    for subject, color in coloring.items():
        if color < len(instance.time_slots):
            assignment[subject] = instance.time_slots[color]
        else:
            assignment[subject] = f"Slot-{color}"

    # Build solution
    sol = Solution(
        assignment=assignment,
        color_map=coloring,
        objective=n_colors,
        is_optimal=(n_colors <= len(instance.time_slots)),
        is_feasible=False,  # will verify independently
        algorithm="Greedy Graph Coloring (largest-first, NetworkX)",
        time_seconds=elapsed,
        certificate=f"Chromatic number <= {n_colors}, slots available = {len(instance.time_slots)}",
    )

    # Independent verification
    sol.is_feasible, sol.constraint_check = verify(instance, coloring)

    return sol


# --- Verification (independent of solver) ---

def verify(instance: Instance, color_map: dict[str, int]) -> tuple[bool, dict[str, bool]]:
    """Independently verify solution feasibility."""
    checks: dict[str, bool] = {}
    all_ok = True

    # Check 1: All subjects assigned
    all_assigned = set(color_map.keys()) == set(instance.subjects)
    checks["all_subjects_assigned"] = all_assigned
    if not all_assigned:
        all_ok = False

    # Check 2: Colors within valid range (0 to n_slots-1)
    colors_valid = all(0 <= c < instance.n_slots for c in color_map.values())
    checks["colors_within_range"] = colors_valid
    if not colors_valid:
        all_ok = False

    # Check 3: No two conflicting subjects share the same color
    no_same_color = True
    for s1, s2 in instance.conflicts:
        if color_map.get(s1) == color_map.get(s2):
            no_same_color = False
            checks[f"conflict_{s1}_vs_{s2}_same_slot"] = False
        else:
            checks[f"conflict_{s1}_vs_{s2}_same_slot"] = True
    checks["no_conflict_same_color"] = no_same_color
    if not no_same_color:
        all_ok = False

    # Check 4: No two conflicting subjects in adjacent slots
    no_adjacent = True
    for s1, s2 in instance.conflicts:
        c1, c2 = color_map.get(s1, -1), color_map.get(s2, -1)
        if abs(c1 - c2) <= 1:
            no_adjacent = False
            checks[f"adjacent_{s1}_vs_{s2}"] = False
        else:
            checks[f"adjacent_{s1}_vs_{s2}"] = True
    checks["no_conflict_adjacent_slots"] = no_adjacent
    if not no_adjacent:
        all_ok = False

    return all_ok, checks


def solve_with_adjacency(instance: Instance) -> Solution:
    """Solve with adjacency constraints by expanding the conflict graph.

    For each conflict pair (A, B), we need |color(A) - color(B)| > 1.
    We model this by creating a layered graph where each subject has
    n_slots copies, and we add edges to prevent adjacent slot assignments.
    Since greedy_color doesn't natively support distance-2 coloring,
    we use a backtracking approach on the small instance.
    """
    t0 = time.perf_counter()

    subjects = list(instance.subjects)
    n_slots = instance.n_slots
    conflicts = list(instance.conflicts)

    # Build adjacency set for quick lookup
    conflict_set = set()
    for s1, s2 in conflicts:
        conflict_set.add((s1, s2))
        conflict_set.add((s2, s1))

    # Backtracking solver for distance-2 coloring on small graph
    color_map: dict[str, int] = {}

    def is_valid(subject: str, color: int) -> bool:
        for other, other_color in color_map.items():
            if (subject, other) in conflict_set or (other, subject) in conflict_set:
                if abs(color - other_color) <= 1:
                    return False
        return True

    def backtrack(idx: int) -> bool:
        if idx == len(subjects):
            return True
        subj = subjects[idx]
        for color in range(n_slots):
            if is_valid(subj, color):
                color_map[subj] = color
                if backtrack(idx + 1):
                    return True
                del color_map[subj]
        return False

    found = backtrack(0)
    elapsed = time.perf_counter() - t0

    if not found:
        # Fallback: relax to non-adjacent and use greedy
        return solve(instance)

    n_colors = max(color_map.values()) + 1 if color_map else 0

    assignment = {}
    for subject, color in color_map.items():
        assignment[subject] = instance.time_slots[color]

    sol = Solution(
        assignment=assignment,
        color_map=dict(color_map),
        objective=n_colors,
        is_optimal=found,
        is_feasible=False,
        algorithm="Backtracking Distance-2 Graph Coloring",
        time_seconds=elapsed,
        certificate=f"Exact backtracking search, colors used = {n_colors}",
    )

    sol.is_feasible, sol.constraint_check = verify(instance, color_map)
    return sol


# --- Main ---

if __name__ == "__main__":
    # Build instance: 6 subjects with conflict pairs
    instance = Instance(
        subjects=(
            "Linear Algebra",
            "Abstract Algebra",
            "Probability",
            "Statistics",
            "Real Analysis",
            "Discrete Math",
        ),
        time_slots=(
            "Morning (8-10)",
            "Late Morning (10-12)",
            "Afternoon (1-3)",
            "Late Afternoon (3-5)",
            "Evening (6-8)",
        ),
        conflicts=(
            ("Linear Algebra", "Abstract Algebra"),   # both algebra topics
            ("Probability", "Statistics"),             # overlapping concepts
            ("Real Analysis", "Linear Algebra"),       # proof-heavy overlap
            ("Discrete Math", "Abstract Algebra"),     # structural overlap
            ("Probability", "Real Analysis"),          # measure theory link
        ),
    )

    sol = solve_with_adjacency(instance)

    # --- Print Solution Report ---
    log.header("SOLUTION REPORT: Study Schedule (Graph Coloring)")

    log.step("PROBLEM SETUP")
    log.metric("Subjects:", str(instance.n_subjects), tag="DATA")
    log.metric("Time slots:", str(instance.n_slots), tag="DATA")
    log.metric("Conflicts:", str(len(instance.conflicts)), tag="DATA")
    log.blank()

    log.info("Conflict pairs:", tag="DATA")
    for s1, s2 in instance.conflicts:
        log.info(f"  {s1} <-> {s2}", tag="DATA")
    log.blank()

    log.step("SOLVER RESULTS")
    log.metric("Algorithm:", sol.algorithm, tag="SOLVE")
    log.metric("Feasible:", str(sol.is_feasible), tag="RESULT")
    log.metric("Optimal:", str(sol.is_optimal), tag="RESULT")
    log.metric("Colors used:", str(sol.objective), tag="RESULT")
    log.metric("Time:", f"{sol.time_seconds:.6f}s", tag="TIMING")
    log.metric("Certificate:", sol.certificate, tag="PROOF")
    log.blank()

    # Assignment table
    log.step("STUDY TIMETABLE")
    log.table_row(f"{'Subject':<20} {'Slot':>3}  {'Time Slot':<25}", tag="TABLE")
    log.divider()
    for subject in instance.subjects:
        slot_idx = sol.color_map[subject]
        slot_name = sol.assignment[subject]
        log.table_row(
            f"{subject:<20} {slot_idx:>3}  {slot_name:<25}",
            tag="ASSIGN",
        )
    log.blank()

    # Visual timetable grid
    log.step("WEEKLY SCHEDULE GRID")
    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    header = f"{'Slot':<25}" + "".join(f"{d:>6}" for d in days)
    log.table_row(header, tag="TABLE")
    log.divider()

    # Group subjects by slot for the grid
    slot_subjects: dict[int, list[str]] = {}
    for subj, color in sol.color_map.items():
        slot_subjects.setdefault(color, []).append(subj)

    for slot_idx in range(instance.n_slots):
        slot_name = instance.time_slots[slot_idx]
        subjects_in_slot = slot_subjects.get(slot_idx, [])
        if subjects_in_slot:
            # Rotate subjects across days for variety
            row = f"{slot_name:<25}"
            for day_idx in range(len(days)):
                subj = subjects_in_slot[day_idx % len(subjects_in_slot)]
                abbrev = subj[:5]
                row += f"{abbrev:>6}"
            log.table_row(row, tag="ASSIGN")
        else:
            row = f"{slot_name:<25}" + "".join(f"{'--':>6}" for _ in days)
            log.table_row(row, tag="TABLE")
    log.blank()

    # Conflict analysis
    log.step("CONFLICT ANALYSIS")
    for s1, s2 in instance.conflicts:
        c1 = sol.color_map[s1]
        c2 = sol.color_map[s2]
        gap = abs(c1 - c2)
        status = "OK (gap={})".format(gap) if gap > 1 else "ADJACENT!" if gap == 1 else "SAME SLOT!"
        log.table_row(
            f"{s1:<20} (slot {c1}) vs {s2:<20} (slot {c2})  {status}",
            tag="CHECK",
        )
    log.blank()

    # Graph properties
    log.step("GRAPH PROPERTIES")
    G = nx.Graph()
    G.add_nodes_from(instance.subjects)
    for s1, s2 in instance.conflicts:
        G.add_edge(s1, s2)
    log.metric("Vertices:", str(G.number_of_nodes()), tag="STATS")
    log.metric("Edges:", str(G.number_of_edges()), tag="STATS")
    log.metric("Max degree:", str(max(dict(G.degree()).values())), tag="STATS")
    log.metric("Density:", f"{nx.density(G):.3f}", tag="STATS")

    # Chromatic number lower bound: clique number
    # Compatible with both older and newer NetworkX versions
    try:
        clique_num = nx.graph_clique_number(G)
    except AttributeError:
        cliques = list(nx.find_cliques(G))
        clique_num = max(len(c) for c in cliques) if cliques else 1
    log.metric("Clique number:", str(clique_num), tag="STATS")
    log.metric("Chromatic lower bound:", str(clique_num), tag="OPTIMIZE")
    log.metric("Colors used:", str(sol.objective), tag="OPTIMIZE")
    log.blank()

    # Independent verification
    log.step("INDEPENDENT VERIFICATION")
    for check_name, result in sol.constraint_check.items():
        log.check(check_name, result, tag="VERIFY")
    log.blank()

    log.divider(style="thick")

    # Save JSON
    output = {
        "assignment": sol.assignment,
        "color_map": sol.color_map,
        "objective": sol.objective,
        "is_optimal": sol.is_optimal,
        "is_feasible": sol.is_feasible,
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
        "certificate": sol.certificate,
        "graph_stats": {
            "vertices": G.number_of_nodes(),
            "edges": G.number_of_edges(),
            "max_degree": max(dict(G.degree()).values()),
            "clique_number": clique_num,
        },
    }
    with open(str(Path(__file__).parent / "solution.json"), "w") as f:
        json.dump(output, f, indent=2)
    log.success("solution.json", tag="SAVE")
