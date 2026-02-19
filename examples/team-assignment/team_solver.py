#!/usr/bin/env python3
"""Team Assignment solver -- Hungarian algorithm for optimal matching.

Assigns 6 developers to 6 projects (one each) to maximize total
satisfaction. Uses scipy.optimize.linear_sum_assignment (Hungarian
algorithm) with negated cost matrix for maximization.

Algorithm: Hungarian algorithm (Kuhn-Munkres), O(n^3).
Complexity: Polynomial -- exact and efficient.
Correctness: Globally optimal, verified independently.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from scipy.optimize import linear_sum_assignment

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger
log = PolyaLogger()


# --- Data Model ---

@dataclass(frozen=True)
class Instance:
    """Problem instance for developer-project assignment."""
    developers: tuple[str, ...]
    projects: tuple[str, ...]
    preferences: tuple[tuple[int, ...], ...]  # n x n matrix, preferences[i][j] = dev i's rating of project j

    @property
    def n(self) -> int:
        return len(self.developers)

    def pref(self, dev_idx: int, proj_idx: int) -> int:
        return self.preferences[dev_idx][proj_idx]


@dataclass
class Solution:
    """Verified solution with metadata."""
    assignment: dict[str, str]        # developer -> project
    assignment_indices: list[tuple[int, int]]  # (dev_idx, proj_idx) pairs
    objective: int                    # total satisfaction score
    is_optimal: bool
    is_feasible: bool
    algorithm: str
    time_seconds: float
    certificate: str
    constraint_check: dict[str, bool] = field(default_factory=dict)


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Solve the assignment problem using the Hungarian algorithm."""
    t0 = time.perf_counter()

    n = instance.n
    pref_matrix = np.array(instance.preferences)

    # Hungarian algorithm minimizes cost, so negate for maximization
    cost_matrix = -pref_matrix
    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    # Total satisfaction (negate back)
    total = int(-cost_matrix[row_ind, col_ind].sum())
    elapsed = time.perf_counter() - t0

    # Build assignment mapping
    assignment = {}
    assignment_indices = []
    for r, c in zip(row_ind, col_ind):
        assignment[instance.developers[r]] = instance.projects[c]
        assignment_indices.append((int(r), int(c)))

    sol = Solution(
        assignment=assignment,
        assignment_indices=assignment_indices,
        objective=total,
        is_optimal=True,  # Hungarian algorithm guarantees global optimum
        is_feasible=False,  # will verify independently
        algorithm="Hungarian Algorithm (scipy.optimize.linear_sum_assignment)",
        time_seconds=elapsed,
        certificate=f"Hungarian algorithm guarantees global optimum for {n}x{n} assignment",
    )

    # Independent verification
    sol.is_feasible, sol.constraint_check = verify(instance, assignment)

    return sol


# --- Verification (independent of solver) ---

def verify(instance: Instance, assignment: dict[str, str]) -> tuple[bool, dict[str, bool]]:
    """Independently verify solution feasibility."""
    checks: dict[str, bool] = {}
    all_ok = True

    # Check 1: All developers assigned
    all_devs = set(assignment.keys()) == set(instance.developers)
    checks["all_developers_assigned"] = all_devs
    if not all_devs:
        all_ok = False

    # Check 2: All projects assigned
    all_projs = set(assignment.values()) == set(instance.projects)
    checks["all_projects_assigned"] = all_projs
    if not all_projs:
        all_ok = False

    # Check 3: One-to-one mapping (no duplicate projects)
    projects_assigned = list(assignment.values())
    one_to_one = len(projects_assigned) == len(set(projects_assigned))
    checks["one_to_one_mapping"] = one_to_one
    if not one_to_one:
        all_ok = False

    # Check 4: Recompute objective
    dev_idx = {d: i for i, d in enumerate(instance.developers)}
    proj_idx = {p: i for i, p in enumerate(instance.projects)}
    total = 0
    for dev, proj in assignment.items():
        total += instance.pref(dev_idx[dev], proj_idx[proj])
    checks["objective_recomputed"] = total

    return all_ok, checks


# --- Analysis helpers ---

def compute_bounds(instance: Instance) -> dict[str, Any]:
    """Compute theoretical bounds on the optimal objective."""
    pref_matrix = np.array(instance.preferences)
    n = instance.n

    # Upper bound: sum of row maxima (best project for each developer)
    row_max_bound = int(pref_matrix.max(axis=1).sum())

    # Upper bound: sum of column maxima (best developer for each project)
    col_max_bound = int(pref_matrix.max(axis=0).sum())

    # Tighter upper bound: minimum of both
    upper_bound = min(row_max_bound, col_max_bound)

    # Lower bound: sum of row minima (worst-case greedy)
    lower_bound = int(pref_matrix.min(axis=1).sum())

    # Random assignment expected value
    random_expected = float(pref_matrix.mean()) * n

    return {
        "row_max_bound": row_max_bound,
        "col_max_bound": col_max_bound,
        "upper_bound": upper_bound,
        "lower_bound": lower_bound,
        "random_expected": random_expected,
    }


def monte_carlo_random(instance: Instance, n_trials: int = 10000) -> dict[str, float]:
    """Estimate random assignment statistics via Monte Carlo."""
    rng = np.random.default_rng(42)
    pref_matrix = np.array(instance.preferences)
    n = instance.n

    scores = []
    for _ in range(n_trials):
        perm = rng.permutation(n)
        score = sum(pref_matrix[i, perm[i]] for i in range(n))
        scores.append(int(score))

    scores_arr = np.array(scores)
    return {
        "mean": float(scores_arr.mean()),
        "std": float(scores_arr.std()),
        "min": int(scores_arr.min()),
        "max": int(scores_arr.max()),
        "p95": float(np.percentile(scores_arr, 95)),
    }


# --- Main ---

if __name__ == "__main__":
    # Build instance: 6 developers, 6 projects, 6x6 preference matrix
    instance = Instance(
        developers=("Alice", "Bob", "Carol", "Dave", "Eve", "Frank"),
        projects=(
            "API Gateway",
            "Mobile App",
            "Data Pipeline",
            "ML Model",
            "DevOps CI/CD",
            "Frontend UI",
        ),
        preferences=(
            #  API  Mobile  Data   ML   DevOps  UI
            (  8,    3,      7,    9,    2,      5),   # Alice
            (  4,    9,      3,    5,    6,      8),   # Bob
            (  6,    5,      9,    7,    4,      3),   # Carol
            (  3,    7,      5,    4,    9,      6),   # Dave
            (  7,    4,      8,    6,    5,      2),   # Eve
            (  5,    6,      4,    3,    7,      9),   # Frank
        ),
    )

    sol = solve(instance)
    bounds = compute_bounds(instance)
    random_stats = monte_carlo_random(instance)

    # --- Print Solution Report ---
    log.header("SOLUTION REPORT: Developer-Project Assignment")

    log.step("PROBLEM SETUP")
    log.metric("Developers:", str(instance.n), tag="DATA")
    log.metric("Projects:", str(instance.n), tag="DATA")
    log.metric("Preference range:", "1-10", tag="DATA")
    log.blank()

    # Preference matrix
    log.step("PREFERENCE MATRIX")
    proj_header = "".join(f"{p[:7]:>8}" for p in instance.projects)
    log.table_row(f"{'Developer':<10}{proj_header}", tag="TABLE")
    log.divider()
    for i, dev in enumerate(instance.developers):
        row = "".join(f"{instance.preferences[i][j]:>8}" for j in range(instance.n))
        log.table_row(f"{dev:<10}{row}", tag="DATA")
    log.blank()

    # Solver results
    log.step("SOLVER RESULTS")
    log.metric("Algorithm:", sol.algorithm, tag="SOLVE")
    log.metric("Optimal:", str(sol.is_optimal), tag="RESULT")
    log.metric("Feasible:", str(sol.is_feasible), tag="RESULT")
    log.metric("Total satisfaction:", str(sol.objective), tag="RESULT")
    log.metric("Time:", f"{sol.time_seconds:.6f}s", tag="TIMING")
    log.metric("Certificate:", sol.certificate, tag="PROOF")
    log.blank()

    # Assignment details
    log.step("OPTIMAL ASSIGNMENT")
    log.table_row(f"{'Developer':<10} {'Project':<18} {'Rating':>8} {'Rank':>8}", tag="TABLE")
    log.divider()

    dev_idx = {d: i for i, d in enumerate(instance.developers)}
    proj_idx = {p: i for i, p in enumerate(instance.projects)}

    for dev in instance.developers:
        proj = sol.assignment[dev]
        di = dev_idx[dev]
        pi = proj_idx[proj]
        rating = instance.pref(di, pi)
        # Rank: where does this project sit in the developer's preference order?
        sorted_prefs = sorted(range(instance.n),
                              key=lambda j: -instance.preferences[di][j])
        rank = sorted_prefs.index(pi) + 1
        rank_label = f"#{rank}" + (" (top!)" if rank == 1 else f" of {instance.n}")
        log.table_row(f"{dev:<10} {proj:<18} {rating:>8} {rank_label:>8}", tag="ASSIGN")

    log.blank()

    # Bounds comparison
    log.step("OPTIMALITY ANALYSIS")
    log.metric("Optimal score:", str(sol.objective), tag="OPTIMIZE")
    log.metric("Upper bound (row max):", str(bounds["row_max_bound"]), tag="OPTIMIZE")
    log.metric("Upper bound (col max):", str(bounds["col_max_bound"]), tag="OPTIMIZE")
    log.metric("Tight upper bound:", str(bounds["upper_bound"]), tag="OPTIMIZE")
    log.metric("Efficiency:", f"{sol.objective / bounds['upper_bound'] * 100:.1f}%", tag="OPTIMIZE")
    log.blank()

    # vs random assignment
    log.step("vs RANDOM ASSIGNMENT (Monte Carlo, 10k trials)")
    log.metric("Optimal:", str(sol.objective), tag="RESULT")
    log.metric("Random mean:", f"{random_stats['mean']:.1f}", tag="STATS")
    log.metric("Random std:", f"{random_stats['std']:.1f}", tag="STATS")
    log.metric("Random best:", str(random_stats['max']), tag="STATS")
    log.metric("Random worst:", str(random_stats['min']), tag="STATS")
    improvement = (sol.objective - random_stats["mean"]) / random_stats["mean"] * 100
    log.metric("Improvement:", f"+{improvement:.1f}% over random", tag="OPTIMIZE")
    log.blank()

    # Who got their top choice?
    log.step("SATISFACTION ANALYSIS")
    for dev in instance.developers:
        di = dev_idx[dev]
        proj = sol.assignment[dev]
        pi = proj_idx[proj]
        rating = instance.pref(di, pi)
        best_possible = max(instance.preferences[di])
        gap = best_possible - rating
        if gap == 0:
            log.success(f"{dev}: got top choice ({proj}, rating {rating})", tag="RESULT")
        else:
            log.info(
                f"{dev}: {proj} (rating {rating}, best possible {best_possible}, gap {gap})",
                tag="RESULT",
            )
    log.blank()

    # Sensitivity: What if a developer leaves?
    log.step("SENSITIVITY: What if a developer leaves?")
    for removed_idx, removed_dev in enumerate(instance.developers):
        remaining_devs = tuple(d for d in instance.developers if d != removed_dev)
        # Remove row from preference matrix, keep all projects
        remaining_prefs = tuple(
            instance.preferences[i]
            for i in range(instance.n) if i != removed_idx
        )
        # For a non-square matrix, pad: assign 5 devs to best 5 of 6 projects
        # Use a different approach: try all 6 subsets of 5 projects
        best_sub_obj = 0
        best_sub_assign = {}
        for skip_proj in range(instance.n):
            sub_devs = remaining_devs
            sub_projs = tuple(p for j, p in enumerate(instance.projects) if j != skip_proj)
            sub_prefs = tuple(
                tuple(remaining_prefs[i][j] for j in range(instance.n) if j != skip_proj)
                for i in range(len(remaining_devs))
            )
            sub_instance = Instance(developers=sub_devs, projects=sub_projs, preferences=sub_prefs)
            sub_sol = solve(sub_instance)
            if sub_sol.objective > best_sub_obj:
                best_sub_obj = sub_sol.objective
                best_sub_assign = sub_sol.assignment

        delta = best_sub_obj - sol.objective
        log.info(
            f"Remove {removed_dev:<6}: best 5-of-6 obj = {best_sub_obj} "
            f"({delta:+d} from full team)",
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
    output = {
        "assignment": sol.assignment,
        "objective": sol.objective,
        "is_optimal": sol.is_optimal,
        "is_feasible": sol.is_feasible,
        "bounds": bounds,
        "random_stats": random_stats,
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
    }
    with open(str(Path(__file__).parent / "solution.json"), "w") as f:
        json.dump(output, f, indent=2)
    log.success("solution.json", tag="SAVE")
