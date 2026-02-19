#!/usr/bin/env python3
"""Event Seating solver -- Constrained partitioning via ILP.

Seats 12 wedding guests at 3 tables (4 each), respecting must-sit-together
and must-not-sit-together constraints while maximizing total pairwise
affinity. Uses PuLP/CBC for Integer Linear Programming.

Algorithm: Integer Linear Programming (Branch & Bound via CBC).
Complexity: NP-hard in general, but small instances solve fast.
Correctness: Exact optimal, verified independently.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from pulp import (
    LpProblem, LpVariable, LpMaximize, LpBinary,
    LpStatus, value, lpSum, PULP_CBC_CMD
)

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger
log = PolyaLogger()


# --- Data Model ---

@dataclass(frozen=True)
class Instance:
    """Problem instance for event seating."""
    guests: tuple[str, ...]
    n_tables: int
    table_capacity: int
    must_together: tuple[tuple[str, str], ...]      # pairs that MUST sit together
    must_apart: tuple[tuple[str, str], ...]          # pairs that MUST NOT sit together
    affinity: dict[tuple[str, str], int]             # pairwise affinity scores

    @property
    def n_guests(self) -> int:
        return len(self.guests)

    def get_affinity(self, g1: str, g2: str) -> int:
        """Get affinity score for a pair (symmetric)."""
        return self.affinity.get((g1, g2), self.affinity.get((g2, g1), 0))


@dataclass
class Solution:
    """Verified solution with metadata."""
    tables: dict[int, list[str]]       # table_id -> list of guests
    objective: float                   # total affinity score
    is_optimal: bool
    is_feasible: bool
    algorithm: str
    time_seconds: float
    certificate: str
    solver_status: str = ""
    lp_relaxation: float | None = None
    constraint_check: dict[str, bool] = field(default_factory=dict)


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Solve the seating ILP. Returns verified solution."""
    t0 = time.perf_counter()

    guests = instance.guests
    n_tables = instance.n_tables
    cap = instance.table_capacity
    tables = list(range(n_tables))

    # Build ILP
    prob = LpProblem("event_seating", LpMaximize)

    # Binary variables: x[g, t] = 1 if guest g sits at table t
    x = {}
    for g in guests:
        for t in tables:
            x[g, t] = LpVariable(f"x_{g}_{t}", cat=LpBinary)

    # Auxiliary variables: y[g1, g2, t] = 1 if both g1 and g2 sit at table t
    # Used to linearize the quadratic affinity objective
    y = {}
    for i, g1 in enumerate(guests):
        for j, g2 in enumerate(guests):
            if i < j:
                for t in tables:
                    y[g1, g2, t] = LpVariable(f"y_{g1}_{g2}_{t}", cat=LpBinary)

    # Objective: maximize total pairwise affinity at each table
    prob += lpSum(
        instance.get_affinity(g1, g2) * y[g1, g2, t]
        for i, g1 in enumerate(guests)
        for j, g2 in enumerate(guests)
        if i < j
        for t in tables
    ), "total_affinity"

    # Constraint 1: Each guest at exactly one table
    for g in guests:
        prob += (
            lpSum(x[g, t] for t in tables) == 1,
            f"assign_{g}"
        )

    # Constraint 2: Table capacity
    for t in tables:
        prob += (
            lpSum(x[g, t] for g in guests) == cap,
            f"capacity_table_{t}"
        )

    # Constraint 3: Linearization -- y[g1,g2,t] <= x[g1,t] and y[g1,g2,t] <= x[g2,t]
    # and y[g1,g2,t] >= x[g1,t] + x[g2,t] - 1
    for i, g1 in enumerate(guests):
        for j, g2 in enumerate(guests):
            if i < j:
                for t in tables:
                    prob += (y[g1, g2, t] <= x[g1, t], f"lin1_{g1}_{g2}_{t}")
                    prob += (y[g1, g2, t] <= x[g2, t], f"lin2_{g1}_{g2}_{t}")
                    prob += (y[g1, g2, t] >= x[g1, t] + x[g2, t] - 1, f"lin3_{g1}_{g2}_{t}")

    # Constraint 4: Must-sit-together pairs
    for g1, g2 in instance.must_together:
        for t in tables:
            prob += (x[g1, t] == x[g2, t], f"together_{g1}_{g2}_{t}")

    # Constraint 5: Must-not-sit-together pairs
    for g1, g2 in instance.must_apart:
        for t in tables:
            prob += (x[g1, t] + x[g2, t] <= 1, f"apart_{g1}_{g2}_{t}")

    # Solve
    prob.solve(PULP_CBC_CMD(msg=False))
    elapsed = time.perf_counter() - t0

    status = LpStatus[prob.status]
    obj = value(prob.objective) if prob.status == 1 else None

    # Extract tables
    table_assignments: dict[int, list[str]] = {t: [] for t in tables}
    for g in guests:
        for t in tables:
            if value(x[g, t]) is not None and value(x[g, t]) > 0.5:
                table_assignments[t].append(g)

    sol = Solution(
        tables=table_assignments,
        objective=obj,
        is_optimal=(status == "Optimal"),
        is_feasible=False,  # will verify independently
        algorithm="ILP (PuLP/CBC, Branch & Bound)",
        time_seconds=elapsed,
        certificate=f"CBC solver status: {status}",
        solver_status=status,
    )

    # Independent verification
    sol.is_feasible, sol.constraint_check = verify(instance, table_assignments)

    return sol


# --- Verification (independent of solver) ---

def verify(instance: Instance, tables: dict[int, list[str]]) -> tuple[bool, dict[str, bool]]:
    """Independently verify solution feasibility."""
    checks: dict[str, bool] = {}
    all_ok = True

    # Flatten all assigned guests
    all_assigned = []
    for t, guests_at_t in tables.items():
        all_assigned.extend(guests_at_t)

    # Check 1: All guests assigned
    ok = set(all_assigned) == set(instance.guests)
    checks["all_guests_assigned"] = ok
    if not ok:
        all_ok = False

    # Check 2: No guest at multiple tables
    ok = len(all_assigned) == len(set(all_assigned))
    checks["no_duplicate_assignments"] = ok
    if not ok:
        all_ok = False

    # Check 3: Table capacity
    for t, guests_at_t in tables.items():
        ok = len(guests_at_t) == instance.table_capacity
        checks[f"table_{t}_capacity"] = ok
        if not ok:
            all_ok = False

    # Check 4: Must-sit-together constraints
    guest_table = {}
    for t, guests_at_t in tables.items():
        for g in guests_at_t:
            guest_table[g] = t

    for g1, g2 in instance.must_together:
        ok = guest_table.get(g1) == guest_table.get(g2)
        checks[f"together_{g1}_{g2}"] = ok
        if not ok:
            all_ok = False

    # Check 5: Must-not-sit-together constraints
    for g1, g2 in instance.must_apart:
        ok = guest_table.get(g1) != guest_table.get(g2)
        checks[f"apart_{g1}_{g2}"] = ok
        if not ok:
            all_ok = False

    # Check 6: Recompute objective
    total_affinity = 0
    for t, guests_at_t in tables.items():
        for i, g1 in enumerate(guests_at_t):
            for j, g2 in enumerate(guests_at_t):
                if i < j:
                    total_affinity += instance.get_affinity(g1, g2)
    checks["objective_recomputed"] = total_affinity

    return all_ok, checks


# --- Main ---

if __name__ == "__main__":
    # Build instance: 12 guests, 3 tables of 4
    guest_names = (
        "Alice", "Ben", "Carol", "Dan",
        "Eve", "Frank", "Grace", "Henry",
        "Iris", "Jack", "Karen", "Leo",
    )

    # Affinity matrix (symmetric, only upper triangle stored)
    # Higher = these people enjoy each other's company more
    affinity_data = {
        # Couples (high affinity)
        ("Alice", "Ben"): 10,
        ("Carol", "Dan"): 10,
        ("Eve", "Frank"): 10,
        ("Grace", "Henry"): 10,
        # Good friends
        ("Alice", "Carol"): 7,
        ("Alice", "Eve"): 6,
        ("Ben", "Dan"): 5,
        ("Ben", "Frank"): 6,
        ("Carol", "Grace"): 7,
        ("Dan", "Henry"): 5,
        ("Eve", "Iris"): 8,
        ("Frank", "Jack"): 7,
        ("Grace", "Karen"): 6,
        ("Henry", "Leo"): 5,
        ("Iris", "Karen"): 7,
        ("Jack", "Leo"): 8,
        # Acquaintances
        ("Alice", "Grace"): 3,
        ("Alice", "Iris"): 4,
        ("Ben", "Henry"): 3,
        ("Ben", "Jack"): 4,
        ("Carol", "Eve"): 4,
        ("Carol", "Karen"): 3,
        ("Dan", "Frank"): 3,
        ("Dan", "Leo"): 4,
        ("Eve", "Grace"): 3,
        ("Frank", "Henry"): 4,
        ("Grace", "Iris"): 3,
        ("Henry", "Karen"): 2,
        ("Iris", "Leo"): 3,
        ("Jack", "Karen"): 4,
        # Feuds (low affinity, but we enforce separation via constraints)
        ("Alice", "Frank"): 1,
        ("Ben", "Grace"): 1,
        ("Carol", "Henry"): 1,
    }

    instance = Instance(
        guests=guest_names,
        n_tables=3,
        table_capacity=4,
        must_together=(
            ("Alice", "Ben"),      # couple
            ("Carol", "Dan"),      # couple
            ("Eve", "Frank"),      # couple
            ("Grace", "Henry"),    # couple
        ),
        must_apart=(
            ("Alice", "Grace"),    # feuding in-laws
            ("Ben", "Henry"),      # old rivalry
            ("Carol", "Eve"),      # personality clash
        ),
        affinity=affinity_data,
    )

    sol = solve(instance)

    # --- Print Solution Report ---
    log.header("SOLUTION REPORT: Wedding Seating Arrangement")

    log.step("PROBLEM SETUP")
    log.metric("Guests:", str(instance.n_guests), tag="DATA")
    log.metric("Tables:", str(instance.n_tables), tag="DATA")
    log.metric("Capacity/table:", str(instance.table_capacity), tag="DATA")
    log.metric("Must-together pairs:", str(len(instance.must_together)), tag="DATA")
    log.metric("Must-apart pairs:", str(len(instance.must_apart)), tag="DATA")
    log.metric("Affinity pairs:", str(len(instance.affinity)), tag="DATA")
    log.blank()

    log.info("Must sit together:", tag="DATA")
    for g1, g2 in instance.must_together:
        log.info(f"  {g1} & {g2} (couple)", tag="DATA")

    log.info("Must NOT sit together:", tag="DATA")
    for g1, g2 in instance.must_apart:
        log.info(f"  {g1} vs {g2}", tag="DATA")
    log.blank()

    # Solver results
    log.step("SOLVER RESULTS")
    log.metric("Status:", sol.solver_status, tag="RESULT")
    log.metric("Optimal:", str(sol.is_optimal), tag="RESULT")
    log.metric("Feasible:", str(sol.is_feasible), tag="RESULT")
    log.metric("Total affinity:", str(sol.objective), tag="RESULT")
    log.metric("Algorithm:", sol.algorithm, tag="SOLVE")
    log.metric("Time:", f"{sol.time_seconds:.4f}s", tag="TIMING")
    log.blank()

    # Table assignments
    log.step("SEATING ARRANGEMENT")
    for t, guests_at_t in sol.tables.items():
        log.blank()
        table_affinity = 0
        pairs = []
        for i, g1 in enumerate(guests_at_t):
            for j, g2 in enumerate(guests_at_t):
                if i < j:
                    aff = instance.get_affinity(g1, g2)
                    table_affinity += aff
                    pairs.append((g1, g2, aff))

        log.info(f"TABLE {t + 1} (affinity sum: {table_affinity})", tag="ASSIGN")
        log.table_row(f"  Guests: {', '.join(guests_at_t)}", tag="TABLE")

        # Show pairwise affinities at this table
        for g1, g2, aff in pairs:
            is_couple = (g1, g2) in instance.must_together or (g2, g1) in instance.must_together
            label = " (couple)" if is_couple else ""
            log.table_row(f"    {g1:<8} -- {g2:<8}: affinity {aff}{label}", tag="STATS")

    log.blank()

    # Constraint satisfaction summary
    log.step("CONSTRAINT SATISFACTION")

    log.info("Must-sit-together:", tag="CHECK")
    guest_table = {}
    for t, guests_at_t in sol.tables.items():
        for g in guests_at_t:
            guest_table[g] = t
    for g1, g2 in instance.must_together:
        same = guest_table[g1] == guest_table[g2]
        log.check(f"{g1} & {g2} at same table (Table {guest_table[g1] + 1})", same, tag="VERIFY")

    log.blank()
    log.info("Must-NOT-sit-together:", tag="CHECK")
    for g1, g2 in instance.must_apart:
        diff = guest_table[g1] != guest_table[g2]
        log.check(
            f"{g1} (Table {guest_table[g1] + 1}) apart from {g2} (Table {guest_table[g2] + 1})",
            diff, tag="VERIFY",
        )
    log.blank()

    # ILP statistics
    log.step("ILP MODEL STATISTICS")
    n_binary_x = instance.n_guests * instance.n_tables
    n_pairs = instance.n_guests * (instance.n_guests - 1) // 2
    n_binary_y = n_pairs * instance.n_tables
    n_total_vars = n_binary_x + n_binary_y
    n_assign = instance.n_guests
    n_cap = instance.n_tables
    n_lin = n_pairs * instance.n_tables * 3
    n_together = len(instance.must_together) * instance.n_tables
    n_apart = len(instance.must_apart) * instance.n_tables
    n_total_constraints = n_assign + n_cap + n_lin + n_together + n_apart

    log.metric("Binary vars (x):", str(n_binary_x), tag="MODEL")
    log.metric("Binary vars (y):", str(n_binary_y), tag="MODEL")
    log.metric("Total variables:", str(n_total_vars), tag="MODEL")
    log.metric("Assignment constr:", str(n_assign), tag="MODEL")
    log.metric("Capacity constr:", str(n_cap), tag="MODEL")
    log.metric("Linearization constr:", str(n_lin), tag="MODEL")
    log.metric("Together constr:", str(n_together), tag="MODEL")
    log.metric("Apart constr:", str(n_apart), tag="MODEL")
    log.metric("Total constraints:", str(n_total_constraints), tag="MODEL")
    log.blank()

    # Per-table affinity breakdown
    log.step("AFFINITY BREAKDOWN BY TABLE")
    log.table_row(f"{'Table':>8} {'Guests':>8} {'Pairs':>8} {'Affinity':>10} {'Avg/pair':>10}", tag="TABLE")
    log.divider()
    total_aff_check = 0
    for t, guests_at_t in sol.tables.items():
        n_at_t = len(guests_at_t)
        n_pairs_t = n_at_t * (n_at_t - 1) // 2
        aff_t = 0
        for i, g1 in enumerate(guests_at_t):
            for j, g2 in enumerate(guests_at_t):
                if i < j:
                    aff_t += instance.get_affinity(g1, g2)
        avg = aff_t / n_pairs_t if n_pairs_t > 0 else 0
        total_aff_check += aff_t
        log.table_row(
            f"{t + 1:>8} {n_at_t:>8} {n_pairs_t:>8} {aff_t:>10} {avg:>10.1f}",
            tag="ASSIGN",
        )
    log.table_row(
        f"{'TOTAL':>8} {instance.n_guests:>8} {'':>8} {total_aff_check:>10}",
        tag="RESULT",
    )
    log.blank()

    # Independent verification
    log.step("INDEPENDENT VERIFICATION")
    for check_name, result in sol.constraint_check.items():
        if isinstance(result, bool):
            log.check(check_name, result, tag="VERIFY")
        else:
            log.check(check_name, result, tag="VERIFY")
    log.blank()

    log.divider(style="thick")

    # Save JSON
    output = {
        "tables": {str(k): v for k, v in sol.tables.items()},
        "objective": sol.objective,
        "is_optimal": sol.is_optimal,
        "is_feasible": sol.is_feasible,
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
        "must_together_satisfied": all(
            guest_table[g1] == guest_table[g2]
            for g1, g2 in instance.must_together
        ),
        "must_apart_satisfied": all(
            guest_table[g1] != guest_table[g2]
            for g1, g2 in instance.must_apart
        ),
        "model_stats": {
            "total_variables": n_total_vars,
            "total_constraints": n_total_constraints,
        },
    }
    with open(str(Path(__file__).parent / "solution.json"), "w") as f:
        json.dump(output, f, indent=2)
    log.success("solution.json", tag="SAVE")
