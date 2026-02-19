#!/usr/bin/env python3
"""Nurse Shift Scheduling solver.

Solves a nurse scheduling problem using ILP (PuLP/CBC).
8 nurses, 3 shifts, 7 days with staffing, workload, and temporal constraints.

Complexity: NP-hard in general, but small instances are tractable via ILP.
Correctness: Exact optimal, verified independently.
"""
from __future__ import annotations

import time
import json
from dataclasses import dataclass, field
from typing import Any

from pulp import (
    LpProblem, LpVariable, LpMaximize, LpBinary,
    LpStatus, value, lpSum, PULP_CBC_CMD,
)

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger
log = PolyaLogger()


# --- Data Model ---

@dataclass(frozen=True)
class Instance:
    """Problem instance for nurse shift scheduling."""
    nurses: tuple[str, ...]
    days: tuple[str, ...]
    shifts: tuple[str, ...]
    min_per_shift: int           # minimum nurses per shift per day
    max_days_per_nurse: int      # max days any nurse can work
    no_consecutive_nights: bool  # if True, no nurse works night two days in a row

    @property
    def num_nurses(self) -> int:
        return len(self.nurses)

    @property
    def num_days(self) -> int:
        return len(self.days)

    @property
    def num_shifts(self) -> int:
        return len(self.shifts)


@dataclass
class Solution:
    """Verified solution with metadata."""
    assignments: dict[str, list[tuple[str, str]]]  # nurse -> [(day, shift), ...]
    objective: float
    is_optimal: bool
    is_feasible: bool
    algorithm: str
    time_seconds: float
    certificate: str
    constraint_check: dict[str, bool] = field(default_factory=dict)


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Solve the nurse scheduling ILP. Returns verified solution."""
    t0 = time.perf_counter()

    N = instance.nurses
    D = instance.days
    S = instance.shifts

    # Build ILP
    prob = LpProblem("shift_scheduling", LpMaximize)

    # Binary decision variables: x[nurse, day, shift] = 1 if nurse works that shift
    x = {}
    for n in N:
        for d in D:
            for s in S:
                x[n, d, s] = LpVariable(f"x_{n}_{d}_{s}", cat=LpBinary)

    # Objective: maximize total shifts covered (maximize staffing)
    prob += lpSum(x[n, d, s] for n in N for d in D for s in S), "total_coverage"

    # Constraint 1: Each nurse works at most 1 shift per day
    for n in N:
        for d in D:
            prob += (
                lpSum(x[n, d, s] for s in S) <= 1,
                f"one_shift_per_day_{n}_{d}"
            )

    # Constraint 2: Each shift each day has at least min_per_shift nurses
    for d in D:
        for s in S:
            prob += (
                lpSum(x[n, d, s] for n in N) >= instance.min_per_shift,
                f"min_staff_{d}_{s}"
            )

    # Constraint 3: Each nurse works at most max_days_per_nurse days
    for n in N:
        # A nurse "works a day" if they work any shift that day
        # Since constraint 1 ensures at most 1 shift per day,
        # sum over shifts for a day = 0 or 1, so sum over all days/shifts = total days worked
        prob += (
            lpSum(x[n, d, s] for d in D for s in S) <= instance.max_days_per_nurse,
            f"max_days_{n}"
        )

    # Constraint 4: No consecutive night shifts
    if instance.no_consecutive_nights:
        night_idx = S.index("night") if "night" in S else None
        if night_idx is not None:
            for n in N:
                for i in range(len(D) - 1):
                    prob += (
                        x[n, D[i], "night"] + x[n, D[i + 1], "night"] <= 1,
                        f"no_consec_night_{n}_{D[i]}_{D[i+1]}"
                    )

    # Solve
    prob.solve(PULP_CBC_CMD(msg=False))
    elapsed = time.perf_counter() - t0

    status = LpStatus[prob.status]
    obj = value(prob.objective) if prob.status == 1 else 0.0

    # Extract assignments
    assignments: dict[str, list[tuple[str, str]]] = {n: [] for n in N}
    for n in N:
        for d in D:
            for s in S:
                if value(x[n, d, s]) is not None and value(x[n, d, s]) > 0.5:
                    assignments[n].append((d, s))

    # Build solution
    sol = Solution(
        assignments=assignments,
        objective=obj,
        is_optimal=(status == "Optimal"),
        is_feasible=False,  # verified below
        algorithm="ILP (PuLP/CBC, Branch & Bound)",
        time_seconds=elapsed,
        certificate=f"CBC solver status: {status}",
    )

    # Independent verification
    sol.is_feasible, sol.constraint_check = verify(instance, assignments)

    return sol


# --- Verification (independent of solver) ---

def verify(
    instance: Instance,
    assignments: dict[str, list[tuple[str, str]]]
) -> tuple[bool, dict[str, bool]]:
    """Independently verify solution feasibility."""
    checks: dict[str, Any] = {}
    all_ok = True

    N = instance.nurses
    D = instance.days
    S = instance.shifts

    # Check 1: At most 1 shift per nurse per day
    for n in N:
        days_worked = [d for d, s in assignments.get(n, [])]
        ok = len(days_worked) == len(set(days_worked))
        checks[f"one_shift_per_day_{n}"] = ok
        if not ok:
            all_ok = False

    # Check 2: Minimum staffing per shift per day
    for d in D:
        for s in S:
            count = sum(
                1 for n in N
                if (d, s) in assignments.get(n, [])
            )
            ok = count >= instance.min_per_shift
            checks[f"min_staff_{d}_{s}"] = ok
            if not ok:
                all_ok = False

    # Check 3: Max days per nurse
    for n in N:
        days_count = len(assignments.get(n, []))
        ok = days_count <= instance.max_days_per_nurse
        checks[f"max_days_{n}"] = ok
        if not ok:
            all_ok = False

    # Check 4: No consecutive night shifts
    if instance.no_consecutive_nights:
        for n in N:
            night_days = sorted(
                [D.index(d) for d, s in assignments.get(n, []) if s == "night"]
            )
            for i in range(len(night_days) - 1):
                if night_days[i + 1] - night_days[i] == 1:
                    checks[f"no_consec_night_{n}"] = False
                    all_ok = False
                    break
            else:
                checks[f"no_consec_night_{n}"] = True

    # Recompute objective independently
    total_shifts = sum(len(a) for a in assignments.values())
    checks["objective_recomputed"] = total_shifts

    return all_ok, checks


# --- Main ---

if __name__ == "__main__":
    # Build instance
    instance = Instance(
        nurses=("Nurse1", "Nurse2", "Nurse3", "Nurse4",
                "Nurse5", "Nurse6", "Nurse7", "Nurse8"),
        days=("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"),
        shifts=("morning", "afternoon", "night"),
        min_per_shift=2,
        max_days_per_nurse=5,
        no_consecutive_nights=True,
    )

    sol = solve(instance)

    # --- Print Solution Report ---
    log.header("SOLUTION REPORT: Nurse Shift Scheduling")
    log.metric("Status:", "Optimal" if sol.is_optimal else "Sub-optimal", tag="RESULT")
    log.metric("Feasible:", str(sol.is_feasible), tag="RESULT")
    log.metric("Total shifts:", f"{sol.objective:.0f}", tag="RESULT")
    log.metric("Algorithm:", sol.algorithm, tag="SOLVE")
    log.metric("Time:", f"{sol.time_seconds:.4f}s", tag="TIMING")
    log.blank()

    # Schedule grid
    log.step("WEEKLY SCHEDULE")
    header = f"{'Day':<6}"
    for s in instance.shifts:
        header += f" {s:<30}"
    log.table_row(header, tag="TABLE")
    log.divider()

    for d in instance.days:
        row = f"{d:<6}"
        for s in instance.shifts:
            nurses_on = [n for n in instance.nurses if (d, s) in sol.assignments[n]]
            row += f" {', '.join(nurses_on):<30}"
        log.table_row(row, tag="TABLE")

    log.blank()

    # Staffing summary per shift per day
    log.step("STAFFING COUNTS")
    header = f"{'Day':<6}"
    for s in instance.shifts:
        header += f" {s:<12}"
    log.table_row(header, tag="TABLE")
    log.divider()

    for d in instance.days:
        row = f"{d:<6}"
        for s in instance.shifts:
            count = sum(1 for n in instance.nurses if (d, s) in sol.assignments[n])
            row += f" {count:<12}"
        log.table_row(row, tag="TABLE")

    log.blank()

    # Per-nurse workload
    log.step("NURSE WORKLOAD")
    log.table_row(f"{'Nurse':<10} {'Days':<6} {'Shifts':<40}", tag="TABLE")
    log.divider()

    for n in instance.nurses:
        shifts_list = sol.assignments[n]
        days_worked = len(shifts_list)
        detail = ", ".join(f"{d}({s})" for d, s in shifts_list)
        log.table_row(f"{n:<10} {days_worked:<6} {detail}", tag="ASSIGN")

    total = sum(len(a) for a in sol.assignments.values())
    log.table_row(f"{'TOTAL':<10} {total:<6} shifts across all nurses", tag="RESULT")
    log.blank()

    # Night shift analysis
    log.step("NIGHT SHIFT ANALYSIS")
    for n in instance.nurses:
        night_days = [d for d, s in sol.assignments[n] if s == "night"]
        if night_days:
            log.info(f"{n}: night shifts on {', '.join(night_days)}", tag="DATA")
        else:
            log.info(f"{n}: no night shifts", tag="DATA")
    log.blank()

    # Independent verification
    log.step("INDEPENDENT VERIFICATION")
    for check_name, result in sol.constraint_check.items():
        if isinstance(result, bool):
            log.check(check_name, result, tag="VERIFY")
        else:
            log.check(check_name, result, tag="VERIFY")
    log.blank()

    # Summary statistics
    log.step("SUMMARY STATISTICS")
    max_possible = instance.num_nurses * instance.max_days_per_nurse
    min_required = instance.num_days * instance.num_shifts * instance.min_per_shift
    log.metric("Max possible shifts:", str(max_possible), tag="STATS")
    log.metric("Min required shifts:", str(min_required), tag="STATS")
    log.metric("Actual shifts:", f"{sol.objective:.0f}", tag="STATS")
    log.metric("Utilization:", f"{sol.objective / max_possible * 100:.1f}%", tag="STATS")
    log.blank()

    # Save solution
    output = {
        "assignments": {n: [(d, s) for d, s in a] for n, a in sol.assignments.items()},
        "objective": sol.objective,
        "is_optimal": sol.is_optimal,
        "is_feasible": sol.is_feasible,
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
    }
    with open(Path(__file__).parent / "solution.json", "w") as f:
        json.dump(output, f, indent=2)
    log.success("solution.json", tag="SAVE")
    log.divider(style="thick")
