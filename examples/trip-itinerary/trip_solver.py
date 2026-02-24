#!/usr/bin/env python3
"""Trip Itinerary solver -- 0/1 Knapsack with two capacity constraints.

Plans a one-day city trip selecting attractions to maximize total enjoyment
score, subject to an 8-hour time budget and a $100 money budget.
Uses PuLP/CBC for exact ILP solution with binary selection variables.

Algorithm: Integer Linear Programming (Branch & Bound via CBC).
Complexity: NP-hard in general; tractable for small instances via ILP.
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
    LpBinary,
    LpMaximize,
    LpProblem,
    LpStatus,
    LpVariable,
    PULP_CBC_CMD,
    lpSum,
    value,
)

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger

log = PolyaLogger()


# --- Data Model ---


@dataclass(frozen=True)
class Instance:
    """Problem instance for one-day trip itinerary planning.

    Each attraction is a dict with keys: name, enjoyment, duration_min, cost.
    """

    attractions: list[dict[str, Any]]  # name, enjoyment, duration_min, cost
    time_budget_min: int               # total available minutes
    money_budget: float                # total available dollars

    @property
    def num_attractions(self) -> int:
        return len(self.attractions)


@dataclass
class Solution:
    """Verified solution with metadata."""

    selected: list[str]       # names of selected attractions
    total_enjoyment: int      # sum of enjoyment scores
    total_time: int           # sum of durations in minutes
    total_cost: float         # sum of entry costs
    is_optimal: bool
    is_feasible: bool
    algorithm: str
    time_seconds: float
    certificate: str
    constraint_check: dict[str, Any] = field(default_factory=dict)


# --- Solver ---


def solve(instance: Instance) -> Solution:
    """Solve the two-constraint 0/1 knapsack ILP. Returns verified solution."""
    t0 = time.perf_counter()

    attractions = instance.attractions

    # Build ILP
    prob = LpProblem("trip_itinerary", LpMaximize)

    # Binary decision variables: x[i] = 1 if attraction i is visited
    x = {
        a["name"]: LpVariable(f"x_{a['name'].replace(' ', '_')}", cat=LpBinary)
        for a in attractions
    }

    # Objective: maximize total enjoyment score
    prob += (
        lpSum(a["enjoyment"] * x[a["name"]] for a in attractions),
        "total_enjoyment",
    )

    # Constraint 1: total duration <= time budget
    prob += (
        lpSum(a["duration_min"] * x[a["name"]] for a in attractions)
        <= instance.time_budget_min,
        "time_budget",
    )

    # Constraint 2: total cost <= money budget
    prob += (
        lpSum(a["cost"] * x[a["name"]] for a in attractions)
        <= instance.money_budget,
        "money_budget",
    )

    # Solve
    prob.solve(PULP_CBC_CMD(msg=False))
    elapsed = time.perf_counter() - t0

    status = LpStatus[prob.status]
    obj = value(prob.objective) if prob.status == 1 else 0.0

    # Extract selection
    selected: list[str] = []
    total_time = 0
    total_cost = 0.0
    for a in attractions:
        val = value(x[a["name"]])
        if val is not None and val > 0.5:
            selected.append(a["name"])
            total_time += a["duration_min"]
            total_cost += a["cost"]

    sol = Solution(
        selected=selected,
        total_enjoyment=int(obj) if obj is not None else 0,
        total_time=total_time,
        total_cost=total_cost,
        is_optimal=(status == "Optimal"),
        is_feasible=False,  # verified below
        algorithm="0/1 Knapsack ILP (PuLP/CBC, Branch & Bound)",
        time_seconds=elapsed,
        certificate=f"CBC solver status: {status}",
    )

    # Independent verification
    sol.is_feasible, sol.constraint_check = verify(instance, selected)

    return sol


# --- Verification (independent of solver) ---


def verify(
    instance: Instance, selected: list[str]
) -> tuple[bool, dict[str, Any]]:
    """Independently verify solution feasibility.

    Performs 5 checks without sharing any logic with the solver.
    """
    checks: dict[str, Any] = {}
    all_ok = True

    catalog = {a["name"]: a for a in instance.attractions}

    # Check 1: All selected attractions exist in the catalog
    valid_names = all(name in catalog for name in selected)
    checks["all_selected_exist_in_catalog"] = valid_names
    if not valid_names:
        all_ok = False

    # Check 2: No duplicate selections
    no_dupes = len(selected) == len(set(selected))
    checks["no_duplicate_selections"] = no_dupes
    if not no_dupes:
        all_ok = False

    # Check 3: Time budget constraint
    total_time = sum(catalog[name]["duration_min"] for name in selected if name in catalog)
    ok = total_time <= instance.time_budget_min
    checks["time_budget_satisfied"] = ok
    checks["total_time_min"] = total_time
    checks["time_remaining_min"] = instance.time_budget_min - total_time
    if not ok:
        all_ok = False

    # Check 4: Money budget constraint
    total_cost = sum(catalog[name]["cost"] for name in selected if name in catalog)
    ok = total_cost <= instance.money_budget
    checks["money_budget_satisfied"] = ok
    checks["total_cost"] = total_cost
    checks["money_remaining"] = round(instance.money_budget - total_cost, 2)
    if not ok:
        all_ok = False

    # Check 5: Recompute enjoyment score
    total_enjoyment = sum(catalog[name]["enjoyment"] for name in selected if name in catalog)
    checks["enjoyment_recomputed"] = total_enjoyment

    return all_ok, checks


# --- Main ---

if __name__ == "__main__":
    # Build instance: 10 realistic city attractions
    instance = Instance(
        attractions=[
            {"name": "City Museum",       "enjoyment": 8,  "duration_min": 120, "cost": 25.00},
            {"name": "Central Park",      "enjoyment": 7,  "duration_min":  60, "cost":  0.00},
            {"name": "Observation Tower", "enjoyment": 9,  "duration_min":  45, "cost": 35.00},
            {"name": "Street Market",     "enjoyment": 6,  "duration_min":  90, "cost":  5.00},
            {"name": "Art Gallery",       "enjoyment": 7,  "duration_min":  75, "cost": 15.00},
            {"name": "City Zoo",          "enjoyment": 8,  "duration_min": 150, "cost": 22.00},
            {"name": "Aquarium",          "enjoyment": 9,  "duration_min": 100, "cost": 30.00},
            {"name": "Historic Theater",  "enjoyment": 5,  "duration_min":  90, "cost": 40.00},
            {"name": "River Boat Tour",   "enjoyment": 8,  "duration_min":  60, "cost": 20.00},
            {"name": "Food Tour",         "enjoyment": 9,  "duration_min":  90, "cost": 45.00},
        ],
        time_budget_min=480,   # 8 hours
        money_budget=100.00,   # $100
    )

    sol = solve(instance)

    # --- Print Solution Report ---
    log.header("SOLUTION REPORT: Trip Itinerary (0/1 Knapsack ILP)")

    log.step("PROBLEM SETUP")
    log.metric("Attractions:", str(instance.num_attractions), tag="DATA")
    log.metric("Time budget:", f"{instance.time_budget_min} min ({instance.time_budget_min // 60}h)", tag="DATA")
    log.metric("Money budget:", f"${instance.money_budget:.2f}", tag="DATA")
    log.blank()

    # Attraction catalog
    log.step("ATTRACTION CATALOG")
    log.table_row(
        f"{'Attraction':<20} {'Enjoy':>6} {'Dur(min)':>9} {'Cost':>8}",
        tag="TABLE",
    )
    log.divider()
    for a in instance.attractions:
        log.table_row(
            f"{a['name']:<20} {a['enjoyment']:>6} {a['duration_min']:>9} ${a['cost']:>6.2f}",
            tag="DATA",
        )
    log.blank()

    # Solver results
    log.step("SOLVER RESULTS")
    log.metric("Status:", "Optimal" if sol.is_optimal else "Sub-optimal", tag="RESULT")
    log.metric("Feasible:", str(sol.is_feasible), tag="RESULT")
    log.metric("Total enjoyment:", str(sol.total_enjoyment), tag="RESULT")
    log.metric("Total time:", f"{sol.total_time} min ({sol.total_time // 60}h {sol.total_time % 60}m)", tag="RESULT")
    log.metric("Total cost:", f"${sol.total_cost:.2f}", tag="RESULT")
    log.metric("Algorithm:", sol.algorithm, tag="SOLVE")
    log.metric("Time:", f"{sol.time_seconds:.6f}s", tag="TIMING")
    log.blank()

    if sol.is_optimal and sol.selected:
        # Selected attractions detail
        log.step("OPTIMAL ITINERARY")
        catalog = {a["name"]: a for a in instance.attractions}
        log.table_row(
            f"{'Attraction':<20} {'Enjoy':>6} {'Dur(min)':>9} {'Cost':>8}",
            tag="TABLE",
        )
        log.divider()

        cumulative_time = 0
        for name in sol.selected:
            a = catalog[name]
            cumulative_time += a["duration_min"]
            log.table_row(
                f"{name:<20} {a['enjoyment']:>6} {a['duration_min']:>9} ${a['cost']:>6.2f}",
                tag="ASSIGN",
            )

        log.divider()
        log.table_row(
            f"{'TOTAL':<20} {sol.total_enjoyment:>6} {sol.total_time:>9} ${sol.total_cost:>6.2f}",
            tag="RESULT",
        )
        log.blank()

        # Budget utilization
        log.step("BUDGET UTILIZATION")
        time_pct = sol.total_time / instance.time_budget_min
        money_pct = sol.total_cost / instance.money_budget
        log.bar(
            f"Time  ({sol.total_time}/{instance.time_budget_min} min):",
            time_pct,
            tag="OPTIMIZE",
        )
        log.bar(
            f"Money (${sol.total_cost:.0f}/${instance.money_budget:.0f}):    ",
            money_pct,
            tag="OPTIMIZE",
        )
        log.metric("Time remaining:", f"{instance.time_budget_min - sol.total_time} min", tag="STATS")
        log.metric("Money remaining:", f"${instance.money_budget - sol.total_cost:.2f}", tag="STATS")
        log.blank()

        # Efficiency analysis
        log.step("EFFICIENCY: Enjoyment per Hour & per Dollar")
        sorted_attractions = sorted(
            instance.attractions,
            key=lambda a: a["enjoyment"] / max(a["duration_min"], 1),
            reverse=True,
        )
        for a in sorted_attractions:
            eff_time = a["enjoyment"] / a["duration_min"] * 60 if a["duration_min"] > 0 else float("inf")
            eff_cost = a["enjoyment"] / a["cost"] if a["cost"] > 0 else float("inf")
            is_selected = a["name"] in sol.selected
            marker = " <-- selected" if is_selected else ""
            eff_cost_str = f"{eff_cost:.2f}" if eff_cost != float("inf") else "FREE"
            log.table_row(
                f"{a['name']:<20} {eff_time:>5.2f}/hr  {eff_cost_str:>6}/$ {marker}",
                tag="OPTIMIZE",
            )
        log.blank()

        # Excluded attractions
        log.step("EXCLUDED ATTRACTIONS")
        excluded = [a for a in instance.attractions if a["name"] not in sol.selected]
        for a in excluded:
            log.info(
                f"{a['name']}: {a['duration_min']}min, ${a['cost']:.2f}, enjoy={a['enjoyment']}",
                tag="DATA",
            )
        log.blank()

        # Sensitivity: what if budget changes?
        log.step("SENSITIVITY: Budget Variations")
        for time_mult, money_mult, label in [
            (0.75, 1.0, "6h / $100"),
            (1.0, 0.75, "8h / $75"),
            (1.0, 1.0, "8h / $100"),
            (1.25, 1.0, "10h / $100"),
            (1.0, 1.5, "8h / $150"),
        ]:
            alt_instance = Instance(
                attractions=instance.attractions,
                time_budget_min=int(instance.time_budget_min * time_mult),
                money_budget=instance.money_budget * money_mult,
            )
            alt_sol = solve(alt_instance)
            delta = alt_sol.total_enjoyment - sol.total_enjoyment
            log.info(
                f"{label}: enjoy={alt_sol.total_enjoyment} (delta {delta:+d}), "
                f"time={alt_sol.total_time}min, cost=${alt_sol.total_cost:.2f}, "
                f"picks={len(alt_sol.selected)}",
                tag="SENSITIVITY",
            )
        log.blank()
    else:
        log.warning("Solver returned infeasible -- skipping detailed report", tag="WARNING")
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
        "selected": sol.selected,
        "total_enjoyment": sol.total_enjoyment,
        "total_time_min": sol.total_time,
        "total_cost": sol.total_cost,
        "time_budget_min": instance.time_budget_min,
        "money_budget": instance.money_budget,
        "is_optimal": sol.is_optimal,
        "is_feasible": sol.is_feasible,
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
    }
    with open(Path(__file__).parent / "solution.json", "w") as f:
        json.dump(output, f, indent=2)
    log.success("solution.json", tag="SAVE")
