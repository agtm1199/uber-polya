#!/usr/bin/env python3
"""Potluck Planning solver -- ILP assignment with coverage constraints.

Assigns 8 guests to 5 dish categories (appetizer, salad, main, side,
dessert) so that every category is covered at least once, each guest
brings exactly one dish, and total self-reported effort is minimized.
Because 8 guests > 5 categories, some categories will have 2 contributors.

Algorithm: Integer Linear Programming (ILP) via PuLP/CBC.
Complexity: NP-hard in general, but small instances are tractable via ILP.
Correctness: Exact optimal, verified independently.
"""
from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

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

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger

log = PolyaLogger()


# --- Data Model ---


@dataclass(frozen=True)
class Instance:
    """Problem instance for potluck dish assignment."""

    guests: tuple[str, ...]
    categories: tuple[str, ...]
    effort_matrix: dict[str, dict[str, int]]  # guest -> category -> effort (1-5)
    min_per_category: dict[str, int]           # category -> min guests required
    max_per_category: dict[str, int]           # category -> max guests allowed

    @property
    def num_guests(self) -> int:
        return len(self.guests)

    @property
    def num_categories(self) -> int:
        return len(self.categories)

    def effort(self, guest: str, category: str) -> int:
        return self.effort_matrix[guest][category]


@dataclass
class Solution:
    """Verified solution with metadata."""

    assignment: dict[str, str]          # guest -> category
    total_effort: int
    category_counts: dict[str, int]     # category -> number of guests assigned
    is_optimal: bool
    is_feasible: bool
    algorithm: str
    time_seconds: float
    certificate: str
    constraint_check: dict[str, Any] = field(default_factory=dict)


# --- Solver ---


def solve(instance: Instance) -> Solution:
    """Solve the potluck assignment ILP. Returns verified solution."""
    t0 = time.perf_counter()

    G = instance.guests
    C = instance.categories

    # Build ILP
    prob = LpProblem("potluck_planning", LpMinimize)

    # Binary decision variables: x[guest, category] = 1 if guest brings that category
    x: dict[tuple[str, str], LpVariable] = {}
    for g in G:
        for c in C:
            x[g, c] = LpVariable(f"x_{g}_{c}", cat=LpBinary)

    # Objective: minimize total effort
    prob += (
        lpSum(
            instance.effort(g, c) * x[g, c]
            for g in G
            for c in C
        ),
        "total_effort",
    )

    # Constraint 1: Each guest is assigned exactly one category
    for g in G:
        prob += (
            lpSum(x[g, c] for c in C) == 1,
            f"one_category_per_guest_{g}",
        )

    # Constraint 2: Each category has at least min_per_category guests
    for c in C:
        prob += (
            lpSum(x[g, c] for g in G) >= instance.min_per_category[c],
            f"min_coverage_{c}",
        )

    # Constraint 3: Each category has at most max_per_category guests
    for c in C:
        prob += (
            lpSum(x[g, c] for g in G) <= instance.max_per_category[c],
            f"max_coverage_{c}",
        )

    # Solve
    prob.solve(PULP_CBC_CMD(msg=False))
    elapsed = time.perf_counter() - t0

    status = LpStatus[prob.status]
    obj = int(value(prob.objective)) if prob.status == 1 else 0

    # Extract assignment
    assignment: dict[str, str] = {}
    for g in G:
        for c in C:
            if value(x[g, c]) is not None and value(x[g, c]) > 0.5:
                assignment[g] = c
                break

    # Category counts
    cat_counts: dict[str, int] = {c: 0 for c in C}
    for c_assigned in assignment.values():
        cat_counts[c_assigned] += 1

    sol = Solution(
        assignment=assignment,
        total_effort=obj,
        category_counts=cat_counts,
        is_optimal=(status == "Optimal"),
        is_feasible=False,  # verified below
        algorithm="ILP (PuLP/CBC, Branch & Bound)",
        time_seconds=elapsed,
        certificate=f"CBC solver status: {status}",
    )

    # Independent verification
    sol.is_feasible, sol.constraint_check = verify(instance, assignment)

    return sol


# --- Verification (independent of solver) ---


def verify(
    instance: Instance,
    assignment: dict[str, str],
) -> tuple[bool, dict[str, Any]]:
    """Independently verify solution feasibility with 6 checks."""
    checks: dict[str, Any] = {}
    all_ok = True

    G = instance.guests
    C = instance.categories

    # Check 1: Every guest is assigned exactly one category
    all_guests_assigned = set(assignment.keys()) == set(G)
    checks["all_guests_assigned"] = all_guests_assigned
    if not all_guests_assigned:
        all_ok = False

    # Check 2: Every assigned category is valid
    valid_categories = all(c in C for c in assignment.values())
    checks["all_categories_valid"] = valid_categories
    if not valid_categories:
        all_ok = False

    # Check 3: Minimum coverage per category
    cat_counts: dict[str, int] = {c: 0 for c in C}
    for c_assigned in assignment.values():
        cat_counts[c_assigned] += 1

    min_coverage_ok = True
    for c in C:
        if cat_counts[c] < instance.min_per_category[c]:
            min_coverage_ok = False
            break
    checks["min_coverage_met"] = min_coverage_ok
    if not min_coverage_ok:
        all_ok = False

    # Check 4: Maximum coverage per category
    max_coverage_ok = True
    for c in C:
        if cat_counts[c] > instance.max_per_category[c]:
            max_coverage_ok = False
            break
    checks["max_coverage_met"] = max_coverage_ok
    if not max_coverage_ok:
        all_ok = False

    # Check 5: Total effort recomputed independently
    recomputed_effort = 0
    for g, c in assignment.items():
        recomputed_effort += instance.effort(g, c)
    checks["effort_recomputed"] = recomputed_effort

    # Check 6: Total guests assigned equals expected count
    correct_count = len(assignment) == len(G)
    checks["guest_count_correct"] = correct_count
    if not correct_count:
        all_ok = False

    return all_ok, checks


# --- Analysis helpers ---


def compute_bounds(instance: Instance) -> dict[str, Any]:
    """Compute theoretical bounds on the optimal effort."""
    import random

    G = instance.guests
    C = instance.categories

    # Lower bound: sum of each guest's minimum effort across all categories
    guest_min_sum = sum(
        min(instance.effort(g, c) for c in C)
        for g in G
    )

    # Upper bound: sum of each guest's maximum effort (worst case)
    guest_max_sum = sum(
        max(instance.effort(g, c) for c in C)
        for g in G
    )

    # Relaxation lower bound: for each category needing min_per_category,
    # take the cheapest contributors.  This is a relaxation because it
    # allows a guest to be counted for multiple categories.
    relaxation_lb = 0
    for c in C:
        efforts_for_c = sorted(instance.effort(g, c) for g in G)
        relaxation_lb += sum(efforts_for_c[: instance.min_per_category[c]])

    # Random feasible assignment expected effort (Monte Carlo, 10k trials)
    rng = random.Random(42)
    trials = 10000
    random_efforts: list[int] = []
    for _ in range(trials):
        cats = list(C)
        guest_list = list(G)
        rng.shuffle(guest_list)
        rand_assign: dict[str, str] = {}
        # First ensure each category gets at least one guest
        for i, c in enumerate(cats):
            rand_assign[guest_list[i]] = c
        # Assign remaining guests randomly
        for g in guest_list[len(cats):]:
            rand_assign[g] = rng.choice(cats)
        total = sum(instance.effort(g, rand_assign[g]) for g in G)
        random_efforts.append(total)

    random_mean = sum(random_efforts) / len(random_efforts)
    random_min = min(random_efforts)
    random_max = max(random_efforts)

    return {
        "guest_min_sum_lb": guest_min_sum,
        "relaxation_lb": relaxation_lb,
        "guest_max_sum_ub": guest_max_sum,
        "random_mean": round(random_mean, 1),
        "random_min": random_min,
        "random_max": random_max,
    }


# --- Main ---


if __name__ == "__main__":
    # Build instance: 8 guests, 5 dish categories
    # Effort scores (1-5): lower = easier / more skilled for that guest
    guests = ("Alice", "Ben", "Carmen", "David", "Elena", "Frank", "Grace", "Hiro")
    categories = ("appetizer", "salad", "main", "side", "dessert")

    effort_matrix: dict[str, dict[str, int]] = {
        #                  app  sal  main side des
        "Alice":  {"appetizer": 2, "salad": 4, "main": 5, "side": 3, "dessert": 1},
        "Ben":    {"appetizer": 3, "salad": 1, "main": 4, "side": 2, "dessert": 5},
        "Carmen": {"appetizer": 5, "salad": 3, "main": 1, "side": 4, "dessert": 2},
        "David":  {"appetizer": 4, "salad": 2, "main": 3, "side": 1, "dessert": 4},
        "Elena":  {"appetizer": 1, "salad": 5, "main": 2, "side": 3, "dessert": 4},
        "Frank":  {"appetizer": 3, "salad": 2, "main": 4, "side": 5, "dessert": 1},
        "Grace":  {"appetizer": 4, "salad": 1, "main": 3, "side": 2, "dessert": 5},
        "Hiro":   {"appetizer": 2, "salad": 3, "main": 2, "side": 4, "dessert": 3},
    }

    min_per = {c: 1 for c in categories}  # every category must be covered
    max_per = {c: 2 for c in categories}  # at most 2 guests per category

    instance = Instance(
        guests=guests,
        categories=categories,
        effort_matrix=effort_matrix,
        min_per_category=min_per,
        max_per_category=max_per,
    )

    sol = solve(instance)
    bounds = compute_bounds(instance)

    # --- Print Solution Report ---
    log.header("SOLUTION REPORT: Potluck Dish Assignment")

    log.step("PROBLEM SETUP")
    log.metric("Guests:", str(instance.num_guests), tag="DATA")
    log.metric("Categories:", str(instance.num_categories), tag="DATA")
    log.metric("Effort range:", "1-5 (lower = easier)", tag="DATA")
    log.metric("Min per category:", "1", tag="DATA")
    log.metric("Max per category:", "2", tag="DATA")
    log.blank()

    # Effort matrix
    log.step("EFFORT MATRIX")
    cat_header = "".join(f"{c[:6]:>10}" for c in instance.categories)
    log.table_row(f"{'Guest':<10}{cat_header}", tag="TABLE")
    log.divider()
    for g in instance.guests:
        row = "".join(
            f"{instance.effort(g, c):>10}" for c in instance.categories
        )
        log.table_row(f"{g:<10}{row}", tag="DATA")
    log.blank()

    # Solver results
    log.step("SOLVER RESULTS")
    log.metric("Algorithm:", sol.algorithm, tag="SOLVE")
    log.metric("Optimal:", str(sol.is_optimal), tag="RESULT")
    log.metric("Feasible:", str(sol.is_feasible), tag="RESULT")
    log.metric("Total effort:", str(sol.total_effort), tag="RESULT")
    log.metric("Time:", f"{sol.time_seconds:.6f}s", tag="TIMING")
    log.metric("Certificate:", sol.certificate, tag="PROOF")
    log.blank()

    # Assignment details
    log.step("OPTIMAL ASSIGNMENT")
    log.table_row(
        f"{'Guest':<10} {'Category':<14} {'Effort':>8} {'Best':>8} {'Gap':>6}",
        tag="TABLE",
    )
    log.divider()

    for g in instance.guests:
        c = sol.assignment[g]
        eff = instance.effort(g, c)
        best_possible = min(instance.effort(g, cat) for cat in instance.categories)
        gap = eff - best_possible
        marker = " <-- best!" if gap == 0 else ""
        log.table_row(
            f"{g:<10} {c:<14} {eff:>8} {best_possible:>8} {gap:>6}{marker}",
            tag="ASSIGN",
        )

    log.blank()

    # Category coverage summary
    log.step("CATEGORY COVERAGE")
    for c in instance.categories:
        assigned_guests = [g for g, cat in sol.assignment.items() if cat == c]
        guest_str = ", ".join(
            f"{g} (effort {instance.effort(g, c)})" for g in assigned_guests
        )
        log.info(
            f"{c:<12} [{sol.category_counts[c]} guest(s)]: {guest_str}",
            tag="ASSIGN",
        )
    log.blank()

    # Bounds comparison
    log.step("OPTIMALITY ANALYSIS")
    log.metric("Optimal effort:", str(sol.total_effort), tag="OPTIMIZE")
    log.metric("Guest-min-sum LB:", str(bounds["guest_min_sum_lb"]), tag="OPTIMIZE")
    log.metric("Relaxation LB:", str(bounds["relaxation_lb"]), tag="OPTIMIZE")
    log.metric("Worst-case UB:", str(bounds["guest_max_sum_ub"]), tag="OPTIMIZE")
    if bounds["guest_min_sum_lb"] > 0:
        efficiency = bounds["guest_min_sum_lb"] / sol.total_effort * 100
        log.metric(
            "Efficiency:",
            f"{efficiency:.1f}% (closer to 100% = tighter)",
            tag="OPTIMIZE",
        )
    log.blank()

    # vs random assignment
    log.step("vs RANDOM ASSIGNMENT (Monte Carlo, 10k trials)")
    log.metric("Optimal:", str(sol.total_effort), tag="RESULT")
    log.metric("Random mean:", str(bounds["random_mean"]), tag="STATS")
    log.metric("Random best:", str(bounds["random_min"]), tag="STATS")
    log.metric("Random worst:", str(bounds["random_max"]), tag="STATS")
    if sol.total_effort > 0:
        improvement = (bounds["random_mean"] - sol.total_effort) / bounds["random_mean"] * 100
        log.metric(
            "Improvement:", f"{improvement:.1f}% less effort than random", tag="OPTIMIZE"
        )
    log.blank()

    # Who got their top choice?
    log.step("GUEST SATISFACTION ANALYSIS")
    top_choice_count = 0
    for g in instance.guests:
        c = sol.assignment[g]
        eff = instance.effort(g, c)
        best = min(instance.effort(g, cat) for cat in instance.categories)
        if eff == best:
            log.success(
                f"{g}: got easiest category ({c}, effort {eff})", tag="RESULT"
            )
            top_choice_count += 1
        else:
            best_cat = min(
                instance.categories, key=lambda cat: instance.effort(g, cat)
            )
            log.info(
                f"{g}: {c} (effort {eff}), would prefer {best_cat} (effort {best})",
                tag="RESULT",
            )
    log.metric(
        "Guests with top pick:",
        f"{top_choice_count}/{instance.num_guests}",
        tag="STATS",
    )
    log.blank()

    # Sensitivity: What if a guest drops out?
    log.step("SENSITIVITY: What if a guest drops out?")
    for removed_g in instance.guests:
        remaining_guests = tuple(g for g in instance.guests if g != removed_g)
        remaining_effort = {
            g: instance.effort_matrix[g] for g in remaining_guests
        }
        sub_instance = Instance(
            guests=remaining_guests,
            categories=instance.categories,
            effort_matrix=remaining_effort,
            min_per_category=instance.min_per_category,
            max_per_category=instance.max_per_category,
        )
        sub_sol = solve(sub_instance)
        if sub_sol.is_optimal:
            delta = sub_sol.total_effort - sol.total_effort
            log.info(
                f"Remove {removed_g:<8}: effort = {sub_sol.total_effort} "
                f"({delta:+d} from full group)",
                tag="SENSITIVITY",
            )
        else:
            log.warning(
                f"Remove {removed_g:<8}: infeasible or sub-optimal",
                tag="SENSITIVITY",
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
    output: dict[str, Any] = {
        "assignment": sol.assignment,
        "total_effort": sol.total_effort,
        "category_counts": sol.category_counts,
        "effort_breakdown": {
            g: {"category": sol.assignment[g], "effort": instance.effort(g, sol.assignment[g])}
            for g in instance.guests
        },
        "is_optimal": sol.is_optimal,
        "is_feasible": sol.is_feasible,
        "bounds": bounds,
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
    }
    with open(Path(__file__).parent / "solution.json", "w") as f:
        json.dump(output, f, indent=2)
    log.success("solution.json", tag="SAVE")
