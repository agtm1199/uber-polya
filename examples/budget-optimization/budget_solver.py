#!/usr/bin/env python3
"""Budget Optimization solver (0/1 Knapsack).

Selects projects to maximize total ROI under a budget constraint using ILP.
Complexity: NP-hard in general; tractable for small instances via ILP.
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
class Project:
    """A candidate project."""
    name: str
    cost: int       # cost in thousands of dollars
    roi_score: int  # expected ROI score (1-10)


@dataclass(frozen=True)
class Instance:
    """Problem instance for budget optimization."""
    projects: tuple[Project, ...]
    budget: int  # total budget in thousands of dollars

    @property
    def num_projects(self) -> int:
        return len(self.projects)


@dataclass
class Solution:
    """Verified solution with metadata."""
    selected: list[str]         # names of selected projects
    selection_mask: list[bool]  # True/False for each project
    objective: float            # total ROI score
    total_cost: int             # total cost of selected projects
    is_optimal: bool
    is_feasible: bool
    algorithm: str
    time_seconds: float
    certificate: str
    constraint_check: dict[str, Any] = field(default_factory=dict)


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Solve the 0/1 knapsack ILP. Returns verified solution."""
    t0 = time.perf_counter()

    projects = instance.projects
    budget = instance.budget

    # Build ILP
    prob = LpProblem("budget_optimization", LpMaximize)

    # Binary decision variables: x[i] = 1 if project i is selected
    x = {
        p.name: LpVariable(f"x_{p.name}", cat=LpBinary)
        for p in projects
    }

    # Objective: maximize total ROI score
    prob += lpSum(p.roi_score * x[p.name] for p in projects), "total_roi"

    # Constraint: total cost <= budget
    prob += (
        lpSum(p.cost * x[p.name] for p in projects) <= budget,
        "budget_constraint"
    )

    # Solve
    prob.solve(PULP_CBC_CMD(msg=False))
    elapsed = time.perf_counter() - t0

    status = LpStatus[prob.status]
    obj = value(prob.objective) if prob.status == 1 else 0.0

    # Extract selection
    selected = []
    selection_mask = []
    total_cost = 0
    for p in projects:
        is_selected = value(x[p.name]) is not None and value(x[p.name]) > 0.5
        selection_mask.append(is_selected)
        if is_selected:
            selected.append(p.name)
            total_cost += p.cost

    sol = Solution(
        selected=selected,
        selection_mask=selection_mask,
        objective=obj,
        total_cost=total_cost,
        is_optimal=(status == "Optimal"),
        is_feasible=False,  # verified below
        algorithm="0/1 Knapsack ILP (PuLP/CBC, Branch & Bound)",
        time_seconds=elapsed,
        certificate=f"CBC solver status: {status}",
    )

    # Independent verification
    sol.is_feasible, sol.constraint_check = verify(instance, selection_mask)

    return sol


# --- Verification (independent of solver) ---

def verify(
    instance: Instance,
    selection_mask: list[bool]
) -> tuple[bool, dict[str, Any]]:
    """Independently verify solution feasibility."""
    checks: dict[str, Any] = {}
    all_ok = True

    projects = instance.projects

    # Check 1: selection_mask has correct length
    ok = len(selection_mask) == len(projects)
    checks["mask_length_correct"] = ok
    if not ok:
        all_ok = False

    # Check 2: Budget constraint
    total_cost = sum(p.cost for p, sel in zip(projects, selection_mask) if sel)
    ok = total_cost <= instance.budget
    checks["budget_satisfied"] = ok
    checks["total_cost"] = total_cost
    checks["budget_remaining"] = instance.budget - total_cost
    if not ok:
        all_ok = False

    # Check 3: Recompute objective
    total_roi = sum(p.roi_score for p, sel in zip(projects, selection_mask) if sel)
    checks["objective_recomputed"] = total_roi

    # Check 4: All selected projects exist
    selected_names = {p.name for p, sel in zip(projects, selection_mask) if sel}
    valid_names = {p.name for p in projects}
    ok = selected_names.issubset(valid_names)
    checks["all_projects_valid"] = ok
    if not ok:
        all_ok = False

    return all_ok, checks


# --- Main ---

if __name__ == "__main__":
    # Build instance: 10 candidate projects
    projects = (
        Project("Mobile App Redesign",     cost=80,  roi_score=8),
        Project("AI Chatbot",              cost=120, roi_score=9),
        Project("Data Pipeline Upgrade",   cost=60,  roi_score=6),
        Project("Customer Portal",         cost=100, roi_score=7),
        Project("Security Audit",          cost=30,  roi_score=5),
        Project("Cloud Migration",         cost=150, roi_score=10),
        Project("Analytics Dashboard",     cost=45,  roi_score=6),
        Project("API Gateway",             cost=70,  roi_score=7),
        Project("DevOps Automation",       cost=55,  roi_score=8),
        Project("Marketing Platform",      cost=90,  roi_score=4),
    )

    instance = Instance(projects=projects, budget=500)

    sol = solve(instance)

    # --- Print Solution Report ---
    log.header("SOLUTION REPORT: Budget Optimization")
    log.metric("Status:", "Optimal" if sol.is_optimal else "Sub-optimal", tag="RESULT")
    log.metric("Feasible:", str(sol.is_feasible), tag="RESULT")
    log.metric("Total ROI score:", f"{sol.objective:.0f}", tag="RESULT")
    log.metric("Total cost:", f"${sol.total_cost}K / ${instance.budget}K", tag="RESULT")
    log.metric("Budget used:", f"{sol.total_cost / instance.budget * 100:.1f}%", tag="RESULT")
    log.metric("Algorithm:", sol.algorithm, tag="SOLVE")
    log.metric("Time:", f"{sol.time_seconds:.4f}s", tag="TIMING")
    log.blank()

    # Project selection table
    log.step("PROJECT SELECTION")
    log.table_row(
        f"{'Project':<25} {'Cost':>6} {'ROI':>5} {'Selected':>10}",
        tag="TABLE"
    )
    log.divider()

    for p, sel in zip(instance.projects, sol.selection_mask):
        marker = "YES" if sel else "---"
        log.table_row(
            f"{p.name:<25} ${p.cost:>4}K {p.roi_score:>5} {marker:>10}",
            tag="TABLE"
        )

    log.blank()

    # Selected projects detail
    log.step("SELECTED PROJECTS")
    running_cost = 0
    for p, sel in zip(instance.projects, sol.selection_mask):
        if sel:
            running_cost += p.cost
            log.info(
                f"{p.name} (${p.cost}K, ROI={p.roi_score})",
                tag="ASSIGN"
            )
    log.metric("Projects selected:", f"{len(sol.selected)} of {instance.num_projects}", tag="STATS")
    log.blank()

    # Efficiency analysis
    log.step("EFFICIENCY ANALYSIS")
    for p in sorted(instance.projects, key=lambda p: p.roi_score / p.cost, reverse=True):
        efficiency = p.roi_score / p.cost * 100
        selected = p.name in sol.selected
        marker = " <-- selected" if selected else ""
        log.table_row(
            f"{p.name:<25} ROI/cost={efficiency:5.2f}  (${p.cost}K, ROI={p.roi_score}){marker}",
            tag="OPTIMIZE"
        )
    log.blank()

    # What could NOT fit
    log.step("EXCLUDED PROJECTS")
    excluded = [p for p, sel in zip(instance.projects, sol.selection_mask) if not sel]
    for p in excluded:
        log.info(f"{p.name}: ${p.cost}K, ROI={p.roi_score}", tag="DATA")
    budget_remaining = instance.budget - sol.total_cost
    log.metric("Budget remaining:", f"${budget_remaining}K", tag="STATS")
    log.blank()

    # Sensitivity: what if budget changes?
    log.step("SENSITIVITY: Budget Variations")
    for budget_mult, label in [(0.6, "$300K"), (0.8, "$400K"), (1.0, "$500K"),
                                (1.2, "$600K"), (1.5, "$750K")]:
        alt_budget = int(instance.budget * budget_mult)
        alt_instance = Instance(projects=projects, budget=alt_budget)
        alt_sol = solve(alt_instance)
        log.info(
            f"Budget ${alt_budget}K: ROI={alt_sol.objective:.0f}, "
            f"cost=${alt_sol.total_cost}K, "
            f"projects={len(alt_sol.selected)}",
            tag="SENSITIVITY"
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

    # Save solution
    output = {
        "selected": sol.selected,
        "objective": sol.objective,
        "total_cost": sol.total_cost,
        "budget": instance.budget,
        "is_optimal": sol.is_optimal,
        "is_feasible": sol.is_feasible,
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
    }
    with open(Path(__file__).parent / "solution.json", "w") as f:
        json.dump(output, f, indent=2)
    log.success("solution.json", tag="SAVE")
    log.divider(style="thick")
