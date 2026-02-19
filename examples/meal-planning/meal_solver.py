#!/usr/bin/env python3
"""Meal Planning solver -- Integer Linear Programming for diet optimization.

Plans 7 days of dinners minimizing grocery cost while meeting weekly
nutrition targets (protein, calories, fiber). Uses PuLP/CBC for ILP.

Algorithm: Integer Linear Programming (Branch & Bound via CBC).
Complexity: NP-hard in general, but small instances solve instantly.
Correctness: Exact optimal, verified independently.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

from pulp import (
    LpProblem, LpVariable, LpMinimize, LpInteger,
    LpStatus, value, lpSum, PULP_CBC_CMD
)

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger
log = PolyaLogger()


# --- Data Model ---

@dataclass(frozen=True)
class Meal:
    """A single meal option with cost and nutrition per serving."""
    name: str
    cost: float         # dollars per serving
    calories: int       # kcal per serving
    protein: float      # grams per serving
    fiber: float        # grams per serving


@dataclass(frozen=True)
class Instance:
    """Problem instance for weekly meal planning."""
    meals: tuple[Meal, ...]
    total_days: int
    min_protein: float     # grams per week
    max_calories: int      # kcal per week
    min_fiber: float       # grams per week

    @property
    def n_meals(self) -> int:
        return len(self.meals)


@dataclass
class Solution:
    """Verified solution with metadata."""
    plan: dict[str, int]          # meal_name -> count
    objective: float              # total cost
    is_optimal: bool
    is_feasible: bool
    algorithm: str
    time_seconds: float
    certificate: str
    nutrition_totals: dict[str, float] = field(default_factory=dict)
    constraint_check: dict[str, bool] = field(default_factory=dict)
    lp_relaxation: float | None = None


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Solve the meal planning ILP. Returns verified solution."""
    t0 = time.perf_counter()

    meals = instance.meals

    # Build ILP
    prob = LpProblem("meal_planning", LpMinimize)

    # Integer decision variables: how many times to serve each meal (0 to total_days)
    x = {
        m.name: LpVariable(f"x_{m.name.replace(' ', '_')}", lowBound=0,
                           upBound=instance.total_days, cat=LpInteger)
        for m in meals
    }

    # Objective: minimize total cost
    prob += lpSum(m.cost * x[m.name] for m in meals), "total_cost"

    # Constraint 1: Exactly total_days meals
    prob += (
        lpSum(x[m.name] for m in meals) == instance.total_days,
        "total_meals"
    )

    # Constraint 2: Minimum protein
    prob += (
        lpSum(m.protein * x[m.name] for m in meals) >= instance.min_protein,
        "min_protein"
    )

    # Constraint 3: Maximum calories
    prob += (
        lpSum(m.calories * x[m.name] for m in meals) <= instance.max_calories,
        "max_calories"
    )

    # Constraint 4: Minimum fiber
    prob += (
        lpSum(m.fiber * x[m.name] for m in meals) >= instance.min_fiber,
        "min_fiber"
    )

    # Solve
    prob.solve(PULP_CBC_CMD(msg=False))
    elapsed = time.perf_counter() - t0

    status = LpStatus[prob.status]
    obj = value(prob.objective) if prob.status == 1 else None

    # Extract plan
    plan: dict[str, int] = {}
    for m in meals:
        val = value(x[m.name])
        if val is not None and val > 0.5:
            plan[m.name] = int(round(val))

    # Compute nutrition totals
    meal_lookup = {m.name: m for m in meals}
    nutrition = {"calories": 0.0, "protein": 0.0, "fiber": 0.0, "cost": 0.0}
    for name, count in plan.items():
        m = meal_lookup[name]
        nutrition["calories"] += m.calories * count
        nutrition["protein"] += m.protein * count
        nutrition["fiber"] += m.fiber * count
        nutrition["cost"] += m.cost * count

    # Build solution
    sol = Solution(
        plan=plan,
        objective=obj,
        is_optimal=(status == "Optimal"),
        is_feasible=False,  # will verify independently
        algorithm="ILP (PuLP/CBC, Branch & Bound)",
        time_seconds=elapsed,
        certificate=f"CBC solver status: {status}",
        nutrition_totals=nutrition,
    )

    # Independent verification
    sol.is_feasible, sol.constraint_check = verify(instance, plan)

    # LP relaxation bound
    prob_lp = LpProblem("meal_planning_lp", LpMinimize)
    x_lp = {
        m.name: LpVariable(f"xlp_{m.name.replace(' ', '_')}", lowBound=0,
                           upBound=instance.total_days)
        for m in meals
    }
    prob_lp += lpSum(m.cost * x_lp[m.name] for m in meals)
    prob_lp += lpSum(x_lp[m.name] for m in meals) == instance.total_days
    prob_lp += lpSum(m.protein * x_lp[m.name] for m in meals) >= instance.min_protein
    prob_lp += lpSum(m.calories * x_lp[m.name] for m in meals) <= instance.max_calories
    prob_lp += lpSum(m.fiber * x_lp[m.name] for m in meals) >= instance.min_fiber
    prob_lp.solve(PULP_CBC_CMD(msg=False))
    sol.lp_relaxation = value(prob_lp.objective)

    return sol


# --- Verification (independent of solver) ---

def verify(instance: Instance, plan: dict[str, int]) -> tuple[bool, dict[str, bool]]:
    """Independently verify solution feasibility."""
    checks: dict[str, bool] = {}
    all_ok = True

    meal_lookup = {m.name: m for m in instance.meals}

    # Check 1: Total meals = total_days
    total_servings = sum(plan.values())
    ok = total_servings == instance.total_days
    checks["total_meals_correct"] = ok
    checks["total_meals_count"] = total_servings
    if not ok:
        all_ok = False

    # Check 2: All meal names valid
    valid_names = all(name in meal_lookup for name in plan.keys())
    checks["all_meals_valid"] = valid_names
    if not valid_names:
        all_ok = False

    # Check 3: Counts in valid range
    counts_valid = all(0 <= c <= instance.total_days for c in plan.values())
    checks["counts_in_range"] = counts_valid
    if not counts_valid:
        all_ok = False

    # Recompute nutrition
    total_cal = sum(meal_lookup[n].calories * c for n, c in plan.items())
    total_pro = sum(meal_lookup[n].protein * c for n, c in plan.items())
    total_fib = sum(meal_lookup[n].fiber * c for n, c in plan.items())
    total_cost = sum(meal_lookup[n].cost * c for n, c in plan.items())

    # Check 4: Protein constraint
    ok = total_pro >= instance.min_protein
    checks["min_protein_met"] = ok
    checks["total_protein_g"] = round(total_pro, 1)
    if not ok:
        all_ok = False

    # Check 5: Calorie constraint
    ok = total_cal <= instance.max_calories
    checks["max_calories_met"] = ok
    checks["total_calories_kcal"] = total_cal
    if not ok:
        all_ok = False

    # Check 6: Fiber constraint
    ok = total_fib >= instance.min_fiber
    checks["min_fiber_met"] = ok
    checks["total_fiber_g"] = round(total_fib, 1)
    if not ok:
        all_ok = False

    # Recomputed objective
    checks["objective_recomputed"] = round(total_cost, 2)

    return all_ok, checks


# --- Main ---

if __name__ == "__main__":
    # Build instance: 10 meals with realistic data
    instance = Instance(
        meals=(
            Meal("Grilled Chicken",   cost=5.50,  calories=550,  protein=45.0, fiber=3.0),
            Meal("Pasta Primavera",   cost=4.00,  calories=650,  protein=18.0, fiber=8.0),
            Meal("Salmon Fillet",     cost=11.00, calories=480,  protein=52.0, fiber=1.0),
            Meal("Bean Chili",        cost=3.50,  calories=420,  protein=28.0, fiber=16.0),
            Meal("Steak & Veggies",   cost=12.00, calories=700,  protein=55.0, fiber=5.0),
            Meal("Tofu Stir Fry",     cost=4.50,  calories=380,  protein=22.0, fiber=7.0),
            Meal("Lentil Soup",       cost=3.00,  calories=350,  protein=24.0, fiber=18.0),
            Meal("Turkey Burger",     cost=6.00,  calories=520,  protein=38.0, fiber=4.0),
            Meal("Veggie Wrap",       cost=4.50,  calories=400,  protein=15.0, fiber=10.0),
            Meal("Shrimp Tacos",      cost=8.00,  calories=450,  protein=35.0, fiber=6.0),
        ),
        total_days=7,
        min_protein=350.0,    # grams per week
        max_calories=14000,   # kcal per week
        min_fiber=140.0,      # grams per week
    )

    sol = solve(instance)

    # --- Print Solution Report ---
    log.header("SOLUTION REPORT: Weekly Meal Planning (ILP)")

    log.step("PROBLEM SETUP")
    log.metric("Meals available:", str(instance.n_meals), tag="DATA")
    log.metric("Days to plan:", str(instance.total_days), tag="DATA")
    log.metric("Min protein:", f"{instance.min_protein}g/week", tag="DATA")
    log.metric("Max calories:", f"{instance.max_calories} kcal/week", tag="DATA")
    log.metric("Min fiber:", f"{instance.min_fiber}g/week", tag="DATA")
    log.blank()

    # Menu table
    log.step("AVAILABLE MEALS")
    log.table_row(
        f"{'Meal':<22} {'Cost':>6} {'Cal':>6} {'Prot':>6} {'Fiber':>6}",
        tag="TABLE",
    )
    log.divider()
    for m in instance.meals:
        log.table_row(
            f"{m.name:<22} ${m.cost:>5.2f} {m.calories:>5}  {m.protein:>5.1f}g {m.fiber:>5.1f}g",
            tag="DATA",
        )
    log.blank()

    # Solver results
    log.step("SOLVER RESULTS")
    log.metric("Status:", "Optimal" if sol.is_optimal else "Suboptimal", tag="RESULT")
    log.metric("Feasible:", str(sol.is_feasible), tag="RESULT")
    log.metric("Total cost:", f"${sol.objective:.2f}", tag="RESULT")
    log.metric("LP Relaxation:", f"${sol.lp_relaxation:.2f}", tag="RESULT")
    integrality_gap = sol.objective - sol.lp_relaxation if sol.lp_relaxation else 0
    log.metric("Integrality gap:", f"${integrality_gap:.2f}", tag="RESULT")
    log.metric("Algorithm:", sol.algorithm, tag="SOLVE")
    log.metric("Time:", f"{sol.time_seconds:.6f}s", tag="TIMING")
    log.blank()

    # Optimal plan
    log.step("OPTIMAL MEAL PLAN")
    log.table_row(
        f"{'Meal':<22} {'Count':>6} {'Cost':>8} {'Cal':>7} {'Prot':>7} {'Fiber':>7}",
        tag="TABLE",
    )
    log.divider()

    meal_lookup = {m.name: m for m in instance.meals}
    for name, count in sorted(sol.plan.items(), key=lambda x: -x[1]):
        m = meal_lookup[name]
        log.table_row(
            f"{name:<22} {count:>5}x  ${m.cost * count:>6.2f} "
            f"{m.calories * count:>6} {m.protein * count:>6.1f}g {m.fiber * count:>6.1f}g",
            tag="ASSIGN",
        )

    log.divider()
    n = sol.nutrition_totals
    log.table_row(
        f"{'WEEKLY TOTAL':<22} {sum(sol.plan.values()):>5}   ${n['cost']:>6.2f} "
        f"{n['calories']:>6.0f} {n['protein']:>6.1f}g {n['fiber']:>6.1f}g",
        tag="RESULT",
    )
    log.blank()

    # Constraint satisfaction
    log.step("NUTRITION TARGETS vs ACTUAL")
    log.table_row(f"{'Nutrient':<15} {'Target':>15} {'Actual':>12} {'Status':>10}", tag="TABLE")
    log.divider()
    log.table_row(
        f"{'Protein':<15} {'>= ' + str(instance.min_protein) + 'g':>15} "
        f"{n['protein']:>10.1f}g  {'PASS' if n['protein'] >= instance.min_protein else 'FAIL':>6}",
        tag="CHECK",
    )
    log.table_row(
        f"{'Calories':<15} {'<= ' + str(instance.max_calories):>15} "
        f"{n['calories']:>10.0f}   {'PASS' if n['calories'] <= instance.max_calories else 'FAIL':>6}",
        tag="CHECK",
    )
    log.table_row(
        f"{'Fiber':<15} {'>= ' + str(instance.min_fiber) + 'g':>15} "
        f"{n['fiber']:>10.1f}g  {'PASS' if n['fiber'] >= instance.min_fiber else 'FAIL':>6}",
        tag="CHECK",
    )
    log.blank()

    # Cost per day and per nutrient
    log.step("COST EFFICIENCY")
    log.metric("Cost per day:", f"${n['cost'] / instance.total_days:.2f}", tag="STATS")
    log.metric("Cost per g protein:", f"${n['cost'] / n['protein']:.3f}", tag="STATS")
    log.metric("Cost per g fiber:", f"${n['cost'] / n['fiber']:.3f}", tag="STATS")
    log.metric("Cal per dollar:", f"{n['calories'] / n['cost']:.0f} kcal/$", tag="STATS")
    log.blank()

    # Sensitivity: What if nutrition targets change?
    log.step("SENSITIVITY: Varying Protein Target")
    for protein_target in [300, 350, 400, 450, 500]:
        modified = Instance(
            meals=instance.meals,
            total_days=instance.total_days,
            min_protein=protein_target,
            max_calories=instance.max_calories,
            min_fiber=instance.min_fiber,
        )
        msol = solve(modified)
        if msol.is_optimal:
            log.info(
                f"Protein >= {protein_target}g: cost = ${msol.objective:.2f} "
                f"(delta ${msol.objective - sol.objective:+.2f})",
                tag="SENSITIVITY",
            )
        else:
            log.warning(f"Protein >= {protein_target}g: INFEASIBLE", tag="SENSITIVITY")
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
        "plan": sol.plan,
        "objective": sol.objective,
        "is_optimal": sol.is_optimal,
        "is_feasible": sol.is_feasible,
        "nutrition_totals": sol.nutrition_totals,
        "lp_relaxation": sol.lp_relaxation,
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
    }
    with open(str(Path(__file__).parent / "solution.json"), "w") as f:
        json.dump(output, f, indent=2)
    log.success("solution.json", tag="SAVE")
