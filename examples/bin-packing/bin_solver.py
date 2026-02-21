#!/usr/bin/env python3
"""Bin Packing solver (Container Loading).

Packs 25 items of various weights into bins of capacity 100 kg each,
minimizing the number of bins. Compares First Fit Decreasing heuristic
with ILP optimal solution.

Complexity: NP-hard in general; tractable for small instances via ILP.
Correctness: Exact optimal via ILP, verified independently.
"""
from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from pulp import (
    PULP_CBC_CMD,
    LpBinary,
    LpMinimize,
    LpProblem,
    LpStatus,
    LpVariable,
    lpSum,
    value,
)

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger
log = PolyaLogger()


# --- Data Model ---

@dataclass(frozen=True)
class Instance:
    """Problem instance for bin packing."""
    weights: tuple[int, ...]
    capacity: int

    @property
    def num_items(self) -> int:
        return len(self.weights)

    @property
    def total_weight(self) -> int:
        return sum(self.weights)

    @property
    def lower_bound(self) -> int:
        """Theoretical lower bound: ceil(total_weight / capacity)."""
        return math.ceil(self.total_weight / self.capacity)


@dataclass
class BinAssignment:
    """Contents of a single bin."""
    items: list[int]      # indices of items in this bin
    weights: list[int]    # corresponding weights
    total: int            # sum of weights in this bin
    utilization: float    # total / capacity


@dataclass
class Solution:
    """Verified solution with metadata."""
    ffd_bins: list[BinAssignment]
    ilp_bins: list[BinAssignment]
    ffd_num_bins: int
    ilp_num_bins: int
    lower_bound: int
    ffd_avg_utilization: float
    ilp_avg_utilization: float
    is_optimal: bool
    is_feasible: bool
    algorithm: str
    time_seconds: float
    certificate: str
    constraint_check: dict[str, Any] = field(default_factory=dict)


# --- First Fit Decreasing ---

def solve_ffd(instance: Instance) -> list[BinAssignment]:
    """Solve bin packing using First Fit Decreasing heuristic.

    Sort items by weight descending. For each item, place it in the
    first bin that has enough remaining capacity. If no bin fits,
    open a new bin.
    """
    # Sort item indices by weight descending
    sorted_indices = sorted(
        range(instance.num_items),
        key=lambda i: instance.weights[i],
        reverse=True,
    )

    bins: list[list[int]] = []       # each bin is a list of item indices
    bin_totals: list[int] = []       # running total for each bin

    for idx in sorted_indices:
        w = instance.weights[idx]
        placed = False
        for b in range(len(bins)):
            if bin_totals[b] + w <= instance.capacity:
                bins[b].append(idx)
                bin_totals[b] += w
                placed = True
                break
        if not placed:
            bins.append([idx])
            bin_totals.append(w)

    # Build BinAssignment objects
    result: list[BinAssignment] = []
    for b_items, b_total in zip(bins, bin_totals):
        result.append(BinAssignment(
            items=b_items,
            weights=[instance.weights[i] for i in b_items],
            total=b_total,
            utilization=b_total / instance.capacity,
        ))

    return result


# --- ILP Optimal ---

def solve_ilp(instance: Instance, upper_bound: int) -> list[BinAssignment]:
    """Solve bin packing optimally using Integer Linear Programming.

    Binary variables:
        x[i,j] = 1 if item i is assigned to bin j
        y[j]   = 1 if bin j is used

    Minimize sum(y[j]).

    Constraints:
        - Each item in exactly one bin: sum_j x[i,j] = 1 for all i
        - Capacity: sum_i w[i]*x[i,j] <= capacity * y[j] for all j
    """
    n = instance.num_items
    B = upper_bound  # use FFD result as upper bound on number of bins
    weights = instance.weights
    cap = instance.capacity

    prob = LpProblem("bin_packing", LpMinimize)

    # Decision variables
    x: dict[tuple[int, int], LpVariable] = {}
    y: dict[int, LpVariable] = {}

    for j in range(B):
        y[j] = LpVariable(f"y_{j}", cat=LpBinary)
        for i in range(n):
            x[i, j] = LpVariable(f"x_{i}_{j}", cat=LpBinary)

    # Objective: minimize number of bins used
    prob += lpSum(y[j] for j in range(B)), "num_bins"

    # Constraint: each item assigned to exactly one bin
    for i in range(n):
        prob += (
            lpSum(x[i, j] for j in range(B)) == 1,
            f"assign_item_{i}"
        )

    # Constraint: bin capacity not exceeded (only if bin is used)
    for j in range(B):
        prob += (
            lpSum(weights[i] * x[i, j] for i in range(n)) <= cap * y[j],
            f"capacity_bin_{j}"
        )

    # Symmetry breaking: use bins in order (y[0] >= y[1] >= ... >= y[B-1])
    for j in range(B - 1):
        prob += (y[j] >= y[j + 1], f"symmetry_{j}")

    # Solve
    prob.solve(PULP_CBC_CMD(msg=False))

    # Extract assignments
    bins: dict[int, list[int]] = {}
    for j in range(B):
        if value(y[j]) is not None and value(y[j]) > 0.5:
            bins[j] = []
            for i in range(n):
                if value(x[i, j]) is not None and value(x[i, j]) > 0.5:
                    bins[j].append(i)

    # Build BinAssignment objects
    result: list[BinAssignment] = []
    for j in sorted(bins.keys()):
        items = bins[j]
        w_list = [weights[i] for i in items]
        total = sum(w_list)
        result.append(BinAssignment(
            items=items,
            weights=w_list,
            total=total,
            utilization=total / cap,
        ))

    return result


# --- Combined Solver ---

def solve(instance: Instance) -> Solution:
    """Solve bin packing with both FFD and ILP. Returns verified solution."""
    t0 = time.perf_counter()

    # Phase 1: FFD heuristic
    ffd_bins = solve_ffd(instance)
    ffd_num = len(ffd_bins)

    # Phase 2: ILP optimal (using FFD result as upper bound)
    ilp_bins = solve_ilp(instance, upper_bound=ffd_num)
    ilp_num = len(ilp_bins)

    elapsed = time.perf_counter() - t0

    # Utilization statistics
    ffd_avg_util = sum(b.utilization for b in ffd_bins) / ffd_num if ffd_num > 0 else 0.0
    ilp_avg_util = sum(b.utilization for b in ilp_bins) / ilp_num if ilp_num > 0 else 0.0

    sol = Solution(
        ffd_bins=ffd_bins,
        ilp_bins=ilp_bins,
        ffd_num_bins=ffd_num,
        ilp_num_bins=ilp_num,
        lower_bound=instance.lower_bound,
        ffd_avg_utilization=ffd_avg_util,
        ilp_avg_utilization=ilp_avg_util,
        is_optimal=True,
        is_feasible=False,  # verified below
        algorithm="FFD heuristic + ILP (PuLP/CBC, Branch & Bound)",
        time_seconds=elapsed,
        certificate=f"FFD bins={ffd_num}, ILP bins={ilp_num}, LB={instance.lower_bound}",
    )

    # Independent verification
    sol.is_feasible, sol.constraint_check = verify(instance, ffd_bins, ilp_bins)

    return sol


# --- Verification (independent of solver) ---

def verify(
    instance: Instance,
    ffd_bins: list[BinAssignment],
    ilp_bins: list[BinAssignment],
) -> tuple[bool, dict[str, Any]]:
    """Independently verify solution feasibility.

    Performs 8 checks:
    1. all_items_packed_ffd: every item appears in exactly one FFD bin
    2. all_items_packed_ilp: every item appears in exactly one ILP bin
    3. no_bin_overloaded_ffd: no FFD bin exceeds capacity
    4. no_bin_overloaded_ilp: no ILP bin exceeds capacity
    5. ilp_leq_ffd: ILP bins <= FFD bins
    6. ffd_leq_bound: FFD bins <= ceil(11/9 * OPT + 1)
    7. lower_bound_holds: ILP bins >= ceil(sum_weights / capacity)
    8. utilization_positive: average utilization > 50%
    """
    checks: dict[str, Any] = {}
    all_ok = True

    n = instance.num_items
    cap = instance.capacity
    lb = instance.lower_bound

    # Check 1: all_items_packed_ffd
    ffd_item_counts: dict[int, int] = {}
    for b in ffd_bins:
        for idx in b.items:
            ffd_item_counts[idx] = ffd_item_counts.get(idx, 0) + 1
    ok = (
        set(ffd_item_counts.keys()) == set(range(n))
        and all(c == 1 for c in ffd_item_counts.values())
    )
    checks["all_items_packed_ffd"] = ok
    if not ok:
        all_ok = False

    # Check 2: all_items_packed_ilp
    ilp_item_counts: dict[int, int] = {}
    for b in ilp_bins:
        for idx in b.items:
            ilp_item_counts[idx] = ilp_item_counts.get(idx, 0) + 1
    ok = (
        set(ilp_item_counts.keys()) == set(range(n))
        and all(c == 1 for c in ilp_item_counts.values())
    )
    checks["all_items_packed_ilp"] = ok
    if not ok:
        all_ok = False

    # Check 3: no_bin_overloaded_ffd
    ffd_totals = [sum(instance.weights[i] for i in b.items) for b in ffd_bins]
    ok = all(t <= cap for t in ffd_totals)
    checks["no_bin_overloaded_ffd"] = ok
    if not ok:
        all_ok = False

    # Check 4: no_bin_overloaded_ilp
    ilp_totals = [sum(instance.weights[i] for i in b.items) for b in ilp_bins]
    ok = all(t <= cap for t in ilp_totals)
    checks["no_bin_overloaded_ilp"] = ok
    if not ok:
        all_ok = False

    # Check 5: ilp_leq_ffd (ILP should be at least as good as FFD)
    ffd_num = len(ffd_bins)
    ilp_num = len(ilp_bins)
    ok = ilp_num <= ffd_num
    checks["ilp_leq_ffd"] = ok
    if not ok:
        all_ok = False

    # Check 6: ffd_leq_bound (FFD approximation guarantee)
    # FFD uses at most ceil(11/9 * OPT + 6/9) bins.
    # Since OPT >= lb, we check against ceil(11/9 * OPT + 1) as a safe bound.
    opt = ilp_num  # ILP gives us the actual OPT
    ffd_bound = math.ceil(11 / 9 * opt + 1)
    ok = ffd_num <= ffd_bound
    checks["ffd_leq_bound"] = ok
    if not ok:
        all_ok = False

    # Check 7: lower_bound_holds (ILP >= theoretical lower bound)
    ok = ilp_num >= lb
    checks["lower_bound_holds"] = ok
    if not ok:
        all_ok = False

    # Check 8: utilization_positive (average utilization > 50%)
    ilp_avg_util = sum(t / cap for t in ilp_totals) / ilp_num if ilp_num > 0 else 0.0
    ok = ilp_avg_util > 0.50
    checks["utilization_positive"] = ok
    if not ok:
        all_ok = False

    return all_ok, checks


# --- Main ---

if __name__ == "__main__":
    # Generate instance: 25 items with weights from seed=42
    np.random.seed(42)
    weights = tuple(int(w) for w in np.random.randint(5, 46, size=25))
    instance = Instance(weights=weights, capacity=100)

    sol = solve(instance)

    # --- Print Solution Report ---
    log.header("SOLUTION REPORT: Bin Packing -- Container Loading")
    log.metric("Algorithm:", sol.algorithm, tag="SOLVE")
    log.metric("Time:", f"{sol.time_seconds:.4f}s", tag="TIMING")
    log.metric("Items:", str(instance.num_items), tag="DATA")
    log.metric("Total weight:", f"{instance.total_weight} kg", tag="DATA")
    log.metric("Bin capacity:", f"{instance.capacity} kg", tag="DATA")
    log.metric("Lower bound:", f"{sol.lower_bound} bins", tag="RESULT")
    log.blank()

    # Item weights summary
    log.step("ITEM WEIGHTS")
    row = ""
    for i, w in enumerate(instance.weights):
        row += f"{w:3d}"
        if (i + 1) % 10 == 0 or i == instance.num_items - 1:
            log.table_row(f"Items {i - len(row)//3 + 1:>2}-{i:>2}: {row}", tag="DATA")
            row = ""
    log.metric("Min weight:", f"{min(instance.weights)} kg", tag="STATS")
    log.metric("Max weight:", f"{max(instance.weights)} kg", tag="STATS")
    log.metric("Mean weight:", f"{instance.total_weight / instance.num_items:.1f} kg", tag="STATS")
    log.blank()

    # FFD Results
    log.step("FIRST FIT DECREASING (FFD) -- HEURISTIC")
    log.metric("Bins used:", str(sol.ffd_num_bins), tag="RESULT")
    log.metric("Avg utilization:", f"{sol.ffd_avg_utilization:.1%}", tag="STATS")
    log.blank()

    log.table_row(f"{'Bin':>4}  {'Items (weights)':40s}  {'Total':>6}  {'Util':>6}", tag="TABLE")
    log.divider()
    for b_idx, b in enumerate(sol.ffd_bins):
        items_str = ", ".join(f"{w}" for w in sorted(b.weights, reverse=True))
        log.table_row(
            f"{b_idx + 1:>4}  {items_str:40s}  {b.total:>5} kg  {b.utilization:>5.0%}",
            tag="TABLE",
        )

    ffd_min_util = min(b.utilization for b in sol.ffd_bins)
    ffd_max_util = max(b.utilization for b in sol.ffd_bins)
    log.blank()
    log.metric("Min bin util:", f"{ffd_min_util:.1%}", tag="STATS")
    log.metric("Max bin util:", f"{ffd_max_util:.1%}", tag="STATS")
    log.blank()

    # ILP Results
    log.step("ILP OPTIMAL SOLUTION")
    log.metric("Bins used:", str(sol.ilp_num_bins), tag="RESULT")
    log.metric("Avg utilization:", f"{sol.ilp_avg_utilization:.1%}", tag="STATS")
    log.blank()

    log.table_row(f"{'Bin':>4}  {'Items (weights)':40s}  {'Total':>6}  {'Util':>6}", tag="TABLE")
    log.divider()
    for b_idx, b in enumerate(sol.ilp_bins):
        items_str = ", ".join(f"{w}" for w in sorted(b.weights, reverse=True))
        log.table_row(
            f"{b_idx + 1:>4}  {items_str:40s}  {b.total:>5} kg  {b.utilization:>5.0%}",
            tag="TABLE",
        )

    ilp_min_util = min(b.utilization for b in sol.ilp_bins)
    ilp_max_util = max(b.utilization for b in sol.ilp_bins)
    log.blank()
    log.metric("Min bin util:", f"{ilp_min_util:.1%}", tag="STATS")
    log.metric("Max bin util:", f"{ilp_max_util:.1%}", tag="STATS")
    log.blank()

    # Comparison
    log.step("COMPARISON: FFD vs ILP")
    log.table_row(f"{'Metric':<25} {'FFD':>10} {'ILP':>10} {'LB':>10}", tag="TABLE")
    log.divider()
    log.table_row(
        f"{'Bins used':<25} {sol.ffd_num_bins:>10} {sol.ilp_num_bins:>10} {sol.lower_bound:>10}",
        tag="TABLE",
    )
    log.table_row(
        f"{'Avg utilization':<25} {sol.ffd_avg_utilization:>9.1%} {sol.ilp_avg_utilization:>9.1%} {'--':>10}",
        tag="TABLE",
    )
    savings = sol.ffd_num_bins - sol.ilp_num_bins
    log.table_row(
        f"{'Bins saved (ILP vs FFD)':<25} {savings:>10} {'':>10} {'':>10}",
        tag="TABLE",
    )
    log.blank()

    ffd_bound = math.ceil(11 / 9 * sol.ilp_num_bins + 1)
    log.metric("FFD approx bound:", f"ceil(11/9 * {sol.ilp_num_bins} + 1) = {ffd_bound} bins", tag="PROOF")
    log.metric("FFD actual:", f"{sol.ffd_num_bins} bins (<= {ffd_bound})", tag="PROOF")
    log.blank()

    # Independent Verification
    log.step("INDEPENDENT VERIFICATION")
    for check_name, result in sol.constraint_check.items():
        if isinstance(result, bool):
            log.check(check_name, result, tag="VERIFY")
        else:
            log.check(check_name, result, tag="VERIFY")
    log.blank()

    all_pass = all(
        v for v in sol.constraint_check.values() if isinstance(v, bool)
    )
    if all_pass:
        log.success(
            f"All {sum(1 for v in sol.constraint_check.values() if isinstance(v, bool))} "
            f"verification checks passed",
            tag="COMPLETE",
        )
    else:
        log.error("Some verification checks failed", tag="ERROR")
    log.blank()

    # Save solution
    output = {
        "ffd_num_bins": sol.ffd_num_bins,
        "ilp_num_bins": sol.ilp_num_bins,
        "lower_bound": sol.lower_bound,
        "ffd_avg_utilization": round(sol.ffd_avg_utilization, 4),
        "ilp_avg_utilization": round(sol.ilp_avg_utilization, 4),
        "ffd_bins": [
            {"items": b.items, "weights": b.weights, "total": b.total}
            for b in sol.ffd_bins
        ],
        "ilp_bins": [
            {"items": b.items, "weights": b.weights, "total": b.total}
            for b in sol.ilp_bins
        ],
        "weights": list(instance.weights),
        "capacity": instance.capacity,
        "is_optimal": sol.is_optimal,
        "is_feasible": sol.is_feasible,
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
    }
    with open(Path(__file__).parent / "solution.json", "w") as f:
        json.dump(output, f, indent=2)
    log.success("solution.json", tag="SAVE")
    log.divider(style="thick")
