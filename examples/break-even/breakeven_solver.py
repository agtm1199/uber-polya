#!/usr/bin/env python3
"""Break-Even Analysis solver -- Symbolic and numerical business analysis.

Finds the break-even quantity where Revenue = Cost for a new product,
then performs sensitivity analysis on price and variable cost changes.
Uses SymPy for symbolic derivation and NumPy for numerical sweeps.

Algorithm: Closed-form symbolic solution + numerical sensitivity.
Complexity: O(1) for break-even, O(n) for sensitivity sweeps.
Correctness: Exact symbolic solution, verified independently.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import sympy as sp

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger
log = PolyaLogger()


# --- Data Model ---

@dataclass(frozen=True)
class Instance:
    """Problem instance for break-even analysis."""
    fixed_cost: float       # fixed costs ($)
    variable_cost: float    # variable cost per unit ($)
    selling_price: float    # selling price per unit ($)
    product_name: str = "New Product"

    @property
    def contribution_margin(self) -> float:
        return self.selling_price - self.variable_cost


@dataclass
class Solution:
    """Verified solution with metadata."""
    breakeven_quantity: int        # units (ceiling)
    breakeven_exact: float        # exact fractional quantity
    breakeven_revenue: float      # revenue at break-even
    contribution_margin: float    # price - variable cost per unit
    symbolic_formula: str         # symbolic expression
    objective: float              # breakeven quantity (the main result)
    is_optimal: bool
    is_feasible: bool
    algorithm: str
    time_seconds: float
    certificate: str
    sensitivity: dict = field(default_factory=dict)
    profit_table: list = field(default_factory=list)
    constraint_check: dict[str, bool] = field(default_factory=dict)


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Solve the break-even problem symbolically and numerically."""
    t0 = time.perf_counter()

    # Symbolic derivation
    Q, F, P, V = sp.symbols("Q F P V", positive=True)

    revenue = P * Q
    cost = F + V * Q
    profit = revenue - cost

    # Solve Revenue = Cost for Q
    breakeven_expr = sp.solve(sp.Eq(revenue, cost), Q)[0]
    # breakeven_expr = F / (P - V)

    # Evaluate numerically
    subs = {F: instance.fixed_cost, P: instance.selling_price, V: instance.variable_cost}
    be_exact = float(breakeven_expr.subs(subs))
    be_quantity = int(np.ceil(be_exact))  # must sell whole units
    be_revenue = instance.selling_price * be_quantity
    contribution = instance.contribution_margin

    # Profit table at various quantities
    profit_table = []
    for q in [0, 250, 500, 750, 1000, be_quantity, 1250, 1500, 2000, 2500]:
        rev = instance.selling_price * q
        cost_val = instance.fixed_cost + instance.variable_cost * q
        prof = rev - cost_val
        profit_table.append({
            "quantity": q,
            "revenue": round(rev, 2),
            "cost": round(cost_val, 2),
            "profit": round(prof, 2),
        })
    # Sort and deduplicate
    profit_table = sorted(profit_table, key=lambda x: x["quantity"])
    seen = set()
    unique_table = []
    for row in profit_table:
        if row["quantity"] not in seen:
            seen.add(row["quantity"])
            unique_table.append(row)
    profit_table = unique_table

    # Sensitivity analysis
    sensitivity = {}

    # 1. Price sensitivity: what if price drops 5%, 10%, 15%, 20%?
    price_sens = []
    for pct in [-20, -15, -10, -5, 0, 5, 10, 15, 20]:
        new_price = instance.selling_price * (1 + pct / 100)
        new_cm = new_price - instance.variable_cost
        if new_cm > 0:
            new_be = instance.fixed_cost / new_cm
            price_sens.append({
                "price_change_pct": pct,
                "new_price": round(new_price, 2),
                "new_breakeven": int(np.ceil(new_be)),
                "contribution_margin": round(new_cm, 2),
            })
        else:
            price_sens.append({
                "price_change_pct": pct,
                "new_price": round(new_price, 2),
                "new_breakeven": None,
                "contribution_margin": round(new_cm, 2),
                "note": "INFEASIBLE: price <= variable cost",
            })
    sensitivity["price_changes"] = price_sens

    # 2. Variable cost sensitivity: what if VC increases 5%, 10%, 15%, 20%?
    vc_sens = []
    for pct in [-20, -10, 0, 10, 20, 30, 50]:
        new_vc = instance.variable_cost * (1 + pct / 100)
        new_cm = instance.selling_price - new_vc
        if new_cm > 0:
            new_be = instance.fixed_cost / new_cm
            vc_sens.append({
                "vc_change_pct": pct,
                "new_vc": round(new_vc, 2),
                "new_breakeven": int(np.ceil(new_be)),
                "contribution_margin": round(new_cm, 2),
            })
        else:
            vc_sens.append({
                "vc_change_pct": pct,
                "new_vc": round(new_vc, 2),
                "new_breakeven": None,
                "contribution_margin": round(new_cm, 2),
                "note": "INFEASIBLE: variable cost >= price",
            })
    sensitivity["variable_cost_changes"] = vc_sens

    # 3. Combined: price drop 10% AND vc increase 20%
    worst_price = instance.selling_price * 0.90
    worst_vc = instance.variable_cost * 1.20
    worst_cm = worst_price - worst_vc
    if worst_cm > 0:
        worst_be = int(np.ceil(instance.fixed_cost / worst_cm))
        sensitivity["worst_case"] = {
            "scenario": "Price -10% AND Variable Cost +20%",
            "price": round(worst_price, 2),
            "variable_cost": round(worst_vc, 2),
            "contribution_margin": round(worst_cm, 2),
            "breakeven": worst_be,
        }
    else:
        sensitivity["worst_case"] = {
            "scenario": "Price -10% AND Variable Cost +20%",
            "note": "INFEASIBLE",
        }

    # 4. Fixed cost sensitivity
    fc_sens = []
    for fc_mult in [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]:
        new_fc = instance.fixed_cost * fc_mult
        new_be = int(np.ceil(new_fc / contribution))
        fc_sens.append({
            "fixed_cost": round(new_fc, 2),
            "multiplier": fc_mult,
            "breakeven": new_be,
        })
    sensitivity["fixed_cost_changes"] = fc_sens

    elapsed = time.perf_counter() - t0

    sol = Solution(
        breakeven_quantity=be_quantity,
        breakeven_exact=be_exact,
        breakeven_revenue=be_revenue,
        contribution_margin=contribution,
        symbolic_formula=f"Q* = F / (P - V) = {sp.pretty(breakeven_expr)}",
        objective=be_exact,
        is_optimal=True,
        is_feasible=(contribution > 0),
        algorithm="Symbolic (SymPy) + Numerical (NumPy) Break-Even Analysis",
        time_seconds=elapsed,
        certificate=f"Closed-form: Q* = {instance.fixed_cost} / ({instance.selling_price} - {instance.variable_cost}) = {be_exact:.4f}",
        sensitivity=sensitivity,
        profit_table=profit_table,
    )

    # Independent verification
    sol.is_feasible, sol.constraint_check = verify(instance, {
        "breakeven_quantity": be_quantity,
        "breakeven_exact": be_exact,
        "contribution_margin": contribution,
    })

    return sol


# --- Verification (independent of solver) ---

def verify(instance: Instance, solution_data: dict) -> tuple[bool, dict[str, bool]]:
    """Independently verify break-even solution."""
    checks: dict[str, bool] = {}
    all_ok = True

    be_qty = solution_data["breakeven_quantity"]
    be_exact = solution_data["breakeven_exact"]
    cm = solution_data["contribution_margin"]

    # Check 1: Contribution margin is positive
    ok = cm > 0
    checks["positive_contribution_margin"] = ok
    if not ok:
        all_ok = False

    # Check 2: Recompute break-even from scratch
    recomputed = instance.fixed_cost / (instance.selling_price - instance.variable_cost)
    ok = abs(recomputed - be_exact) < 1e-10
    checks["breakeven_recomputed_matches"] = ok
    checks["breakeven_recomputed_value"] = round(recomputed, 4)
    if not ok:
        all_ok = False

    # Check 3: At break-even quantity, profit >= 0
    revenue_at_be = instance.selling_price * be_qty
    cost_at_be = instance.fixed_cost + instance.variable_cost * be_qty
    profit_at_be = revenue_at_be - cost_at_be
    ok = profit_at_be >= 0
    checks["profit_at_breakeven_nonnegative"] = ok
    checks["profit_at_breakeven"] = round(profit_at_be, 2)
    if not ok:
        all_ok = False

    # Check 4: One unit below break-even, profit < 0
    if be_qty > 0:
        revenue_below = instance.selling_price * (be_qty - 1)
        cost_below = instance.fixed_cost + instance.variable_cost * (be_qty - 1)
        profit_below = revenue_below - cost_below
        ok = profit_below < 0
        checks["profit_below_breakeven_negative"] = ok
        checks["profit_one_below"] = round(profit_below, 2)
        if not ok:
            all_ok = False

    # Check 5: Revenue = Cost at exact break-even
    rev_exact = instance.selling_price * be_exact
    cost_exact = instance.fixed_cost + instance.variable_cost * be_exact
    ok = abs(rev_exact - cost_exact) < 1e-6
    checks["revenue_equals_cost_at_exact"] = ok
    if not ok:
        all_ok = False

    return all_ok, checks


# --- Main ---

if __name__ == "__main__":
    # Build instance
    instance = Instance(
        fixed_cost=25000.0,
        variable_cost=12.0,
        selling_price=35.0,
        product_name="SmartWidget Pro",
    )

    sol = solve(instance)

    # --- Print Solution Report ---
    log.header("SOLUTION REPORT: Break-Even Analysis")

    log.step("PROBLEM SETUP")
    log.metric("Product:", instance.product_name, tag="DATA")
    log.metric("Fixed costs:", f"${instance.fixed_cost:,.2f}", tag="DATA")
    log.metric("Variable cost/unit:", f"${instance.variable_cost:.2f}", tag="DATA")
    log.metric("Selling price/unit:", f"${instance.selling_price:.2f}", tag="DATA")
    log.metric("Contribution margin:", f"${sol.contribution_margin:.2f}/unit", tag="DATA")
    log.blank()

    # Symbolic result
    log.step("SYMBOLIC DERIVATION")
    log.info("Revenue(Q) = P * Q = $35.00 * Q", tag="MODEL")
    log.info("Cost(Q)    = F + V * Q = $25,000 + $12.00 * Q", tag="MODEL")
    log.info("Profit(Q)  = Revenue - Cost = (P - V) * Q - F", tag="MODEL")
    log.blank()
    log.info("Set Revenue = Cost and solve for Q:", tag="SOLVE")
    log.info(f"  {sol.symbolic_formula}", tag="SOLVE")
    log.blank()

    log.step("BREAK-EVEN RESULT")
    log.metric("Exact break-even:", f"{sol.breakeven_exact:.4f} units", tag="RESULT")
    log.metric("Rounded (ceiling):", f"{sol.breakeven_quantity} units", tag="RESULT")
    log.metric("Break-even revenue:", f"${sol.breakeven_revenue:,.2f}", tag="RESULT")
    log.metric("Algorithm:", sol.algorithm, tag="SOLVE")
    log.metric("Time:", f"{sol.time_seconds:.6f}s", tag="TIMING")
    log.blank()

    # Profit table
    log.step("PROFIT TABLE")
    log.table_row(
        f"{'Quantity':>10} {'Revenue':>12} {'Cost':>12} {'Profit':>12} {'Status':>10}",
        tag="TABLE",
    )
    log.divider()
    for row in sol.profit_table:
        q = row["quantity"]
        status = "BREAK-EVEN" if q == sol.breakeven_quantity else ("PROFIT" if row["profit"] > 0 else "LOSS")
        log.table_row(
            f"{q:>10,} ${row['revenue']:>11,.2f} ${row['cost']:>11,.2f} "
            f"${row['profit']:>11,.2f} {status:>10}",
            tag="RESULT" if row["profit"] >= 0 else "DATA",
        )
    log.blank()

    # Sensitivity: Price changes
    log.step("SENSITIVITY: Price Changes")
    log.table_row(
        f"{'Change':>8} {'New Price':>10} {'Margin':>8} {'Break-Even':>12} {'vs Base':>10}",
        tag="TABLE",
    )
    log.divider()
    for s in sol.sensitivity["price_changes"]:
        pct = s["price_change_pct"]
        if s["new_breakeven"] is not None:
            delta = s["new_breakeven"] - sol.breakeven_quantity
            delta_str = f"{delta:+d}" if delta != 0 else "---"
            log.table_row(
                f"{pct:>+7}% ${s['new_price']:>9.2f} ${s['contribution_margin']:>7.2f} "
                f"{s['new_breakeven']:>11,} {delta_str:>10}",
                tag="SENSITIVITY" if pct != 0 else "RESULT",
            )
        else:
            log.table_row(
                f"{pct:>+7}% ${s['new_price']:>9.2f} ${s['contribution_margin']:>7.2f} "
                f"{'INFEASIBLE':>11} {'N/A':>10}",
                tag="WARNING",
            )
    log.blank()

    # Sensitivity: Variable cost changes
    log.step("SENSITIVITY: Variable Cost Changes")
    log.table_row(
        f"{'Change':>8} {'New VC':>10} {'Margin':>8} {'Break-Even':>12} {'vs Base':>10}",
        tag="TABLE",
    )
    log.divider()
    for s in sol.sensitivity["variable_cost_changes"]:
        pct = s["vc_change_pct"]
        if s["new_breakeven"] is not None:
            delta = s["new_breakeven"] - sol.breakeven_quantity
            delta_str = f"{delta:+d}" if delta != 0 else "---"
            log.table_row(
                f"{pct:>+7}% ${s['new_vc']:>9.2f} ${s['contribution_margin']:>7.2f} "
                f"{s['new_breakeven']:>11,} {delta_str:>10}",
                tag="SENSITIVITY" if pct != 0 else "RESULT",
            )
        else:
            log.table_row(
                f"{pct:>+7}% ${s['new_vc']:>9.2f} ${s['contribution_margin']:>7.2f} "
                f"{'INFEASIBLE':>11} {'N/A':>10}",
                tag="WARNING",
            )
    log.blank()

    # Worst case scenario
    log.step("WORST CASE: Price -10% AND Variable Cost +20%")
    wc = sol.sensitivity["worst_case"]
    if "note" not in wc:
        log.metric("Adjusted price:", f"${wc['price']:.2f}", tag="SENSITIVITY")
        log.metric("Adjusted VC:", f"${wc['variable_cost']:.2f}", tag="SENSITIVITY")
        log.metric("New margin:", f"${wc['contribution_margin']:.2f}", tag="SENSITIVITY")
        log.metric("New break-even:", f"{wc['breakeven']:,} units", tag="SENSITIVITY")
        delta = wc["breakeven"] - sol.breakeven_quantity
        log.metric("Change from base:", f"{delta:+,} units ({delta / sol.breakeven_quantity * 100:+.1f}%)", tag="SENSITIVITY")
    else:
        log.warning("INFEASIBLE: contribution margin <= 0 under worst case", tag="WARNING")
    log.blank()

    # Fixed cost sensitivity
    log.step("SENSITIVITY: Fixed Cost Changes")
    for s in sol.sensitivity["fixed_cost_changes"]:
        mult_label = f"{s['multiplier']:.0%}" if s['multiplier'] != 1.0 else "BASE"
        log.info(
            f"Fixed = ${s['fixed_cost']:>10,.2f} ({mult_label:>5}): "
            f"break-even = {s['breakeven']:>6,} units",
            tag="SENSITIVITY",
        )
    log.blank()

    # Business recommendations
    log.step("BUSINESS RECOMMENDATIONS")
    log.info(f"You need to sell at least {sol.breakeven_quantity:,} units to cover costs", tag="RECOMMEND")
    log.info(f"Each unit beyond break-even generates ${sol.contribution_margin:.2f} profit", tag="RECOMMEND")

    # Profit at target volumes
    for target_units in [1500, 2000, 3000]:
        profit = (instance.selling_price - instance.variable_cost) * target_units - instance.fixed_cost
        margin_pct = profit / (instance.selling_price * target_units) * 100
        log.info(
            f"At {target_units:,} units: profit = ${profit:,.2f} ({margin_pct:.1f}% margin)",
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
        "product": instance.product_name,
        "breakeven_quantity": sol.breakeven_quantity,
        "breakeven_exact": sol.breakeven_exact,
        "breakeven_revenue": sol.breakeven_revenue,
        "contribution_margin": sol.contribution_margin,
        "symbolic_formula": sol.symbolic_formula,
        "is_feasible": sol.is_feasible,
        "profit_table": sol.profit_table,
        "sensitivity": sol.sensitivity,
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
    }
    with open(str(Path(__file__).parent / "solution.json"), "w") as f:
        json.dump(output, f, indent=2)
    log.success("solution.json", tag="SAVE")
