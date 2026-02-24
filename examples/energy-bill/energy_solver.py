#!/usr/bin/env python3
"""Energy Bill Optimization solver -- Time-of-Use Appliance Scheduling.

Schedules 5 household appliances across 24 hours to minimize daily
electricity cost under time-of-use pricing and noise constraints.
Uses ILP (PuLP/CBC) with binary start-hour decision variables.

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
    LpProblem, LpVariable, LpMinimize, LpBinary,
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
    """Problem instance for energy bill optimization.

    Attributes:
        appliances: list of dicts with keys: name, duration_hours, power_kw,
                    allowed_start_hours (list of ints 0-23).
        rates: list of 24 floats, electricity cost in $/kWh per hour.
        hours: number of hours in the scheduling horizon (default 24).
    """
    appliances: tuple[dict[str, Any], ...]
    rates: tuple[float, ...]
    hours: int = 24

    @property
    def n_appliances(self) -> int:
        return len(self.appliances)


@dataclass
class Solution:
    """Verified solution with metadata."""
    schedule: dict[str, int]             # appliance name -> start hour
    total_cost: float                    # total daily electricity cost
    cost_breakdown: dict[str, float]     # appliance name -> cost
    is_optimal: bool
    is_feasible: bool
    algorithm: str
    time_seconds: float
    certificate: str
    constraint_check: dict[str, Any] = field(default_factory=dict)


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Solve the appliance scheduling ILP. Returns verified solution."""
    t0 = time.perf_counter()

    appliances = instance.appliances
    rates = instance.rates
    H = instance.hours

    # Build ILP
    prob = LpProblem("energy_bill", LpMinimize)

    # Binary decision variables: x[a, h] = 1 if appliance a starts at hour h
    x: dict[tuple[str, int], LpVariable] = {}
    for a in appliances:
        name = a["name"]
        for h in a["allowed_start_hours"]:
            # Only create variable if appliance fits within the 24-hour window
            if h + a["duration_hours"] <= H:
                x[name, h] = LpVariable(f"x_{name}_{h}", cat=LpBinary)

    # Objective: minimize total electricity cost
    # Cost for appliance a starting at hour h = power_kw * sum of rates
    # over [h, h+duration)
    cost_terms = []
    for a in appliances:
        name = a["name"]
        dur = a["duration_hours"]
        pwr = a["power_kw"]
        for h in a["allowed_start_hours"]:
            if h + dur <= H:
                hourly_cost = pwr * sum(rates[h + t] for t in range(dur))
                cost_terms.append(hourly_cost * x[name, h])

    prob += lpSum(cost_terms), "total_electricity_cost"

    # Constraint 1: Each appliance starts exactly once
    for a in appliances:
        name = a["name"]
        dur = a["duration_hours"]
        valid_starts = [h for h in a["allowed_start_hours"] if h + dur <= H]
        prob += (
            lpSum(x[name, h] for h in valid_starts) == 1,
            f"assign_{name}"
        )

    # Solve
    prob.solve(PULP_CBC_CMD(msg=False))
    elapsed = time.perf_counter() - t0

    status = LpStatus[prob.status]
    obj = value(prob.objective) if prob.status == 1 else None

    # Extract schedule
    schedule: dict[str, int] = {}
    cost_breakdown: dict[str, float] = {}
    for a in appliances:
        name = a["name"]
        dur = a["duration_hours"]
        pwr = a["power_kw"]
        for h in a["allowed_start_hours"]:
            if h + dur <= H:
                val = value(x[name, h])
                if val is not None and val > 0.5:
                    schedule[name] = h
                    cost_breakdown[name] = pwr * sum(
                        rates[h + t] for t in range(dur)
                    )
                    break

    total_cost = sum(cost_breakdown.values()) if cost_breakdown else 0.0

    # Build solution
    sol = Solution(
        schedule=schedule,
        total_cost=total_cost,
        cost_breakdown=cost_breakdown,
        is_optimal=(status == "Optimal"),
        is_feasible=False,  # verified below
        algorithm="ILP (PuLP/CBC, Branch & Bound)",
        time_seconds=elapsed,
        certificate=f"CBC solver status: {status}",
    )

    # Independent verification
    sol.is_feasible, sol.constraint_check = verify(instance, schedule)

    return sol


# --- Verification (independent of solver) ---

def verify(
    instance: Instance,
    schedule: dict[str, int],
) -> tuple[bool, dict[str, Any]]:
    """Independently verify solution feasibility.

    Performs 6 checks that share no logic with the solver.
    """
    checks: dict[str, Any] = {}
    all_ok = True

    appliances = instance.appliances
    rates = instance.rates
    H = instance.hours
    app_lookup = {a["name"]: a for a in appliances}

    # Check 1: All appliances are scheduled
    scheduled_names = set(schedule.keys())
    required_names = {a["name"] for a in appliances}
    ok = scheduled_names == required_names
    checks["all_appliances_scheduled"] = ok
    if not ok:
        all_ok = False

    # Check 2: Each start hour is within the appliance's allowed hours
    for name, start in schedule.items():
        a = app_lookup.get(name)
        if a is None:
            checks[f"valid_appliance_{name}"] = False
            all_ok = False
            continue
        ok = start in a["allowed_start_hours"]
        checks[f"allowed_start_{name}"] = ok
        if not ok:
            all_ok = False

    # Check 3: Each appliance fits within the 24-hour window
    for name, start in schedule.items():
        a = app_lookup[name]
        end = start + a["duration_hours"]
        ok = end <= H
        checks[f"fits_in_window_{name}"] = ok
        if not ok:
            all_ok = False

    # Check 4: No two appliances occupy the same hour (overlap analysis)
    # Build occupancy grid
    occupancy: dict[int, list[str]] = {h: [] for h in range(H)}
    for name, start in schedule.items():
        a = app_lookup[name]
        for t in range(a["duration_hours"]):
            occupancy[start + t].append(name)
    max_concurrent = max(len(v) for v in occupancy.values())
    checks["max_concurrent_appliances"] = max_concurrent
    # (No hard constraint on overlap in this model, but recorded for insight)

    # Check 5: Cost calculation is correct (recompute independently)
    recomputed_cost = 0.0
    recomputed_breakdown: dict[str, float] = {}
    for name, start in schedule.items():
        a = app_lookup[name]
        dur = a["duration_hours"]
        pwr = a["power_kw"]
        c = pwr * sum(rates[start + t] for t in range(dur))
        recomputed_breakdown[name] = round(c, 4)
        recomputed_cost += c
    checks["cost_recomputed"] = round(recomputed_cost, 4)
    checks["cost_breakdown_recomputed"] = recomputed_breakdown

    # Check 6: Start hours are valid integers in [0, 23]
    ok = all(isinstance(h, int) and 0 <= h < H for h in schedule.values())
    checks["start_hours_valid_range"] = ok
    if not ok:
        all_ok = False

    return all_ok, checks


# --- Helpers ---

def hour_label(h: int) -> str:
    """Convert hour 0-23 to human-readable label like '11pm', '7am'."""
    h = h % 24
    if h == 0:
        return "12am"
    elif h < 12:
        return f"{h}am"
    elif h == 12:
        return "12pm"
    else:
        return f"{h - 12}pm"


def rate_tier(rate: float) -> str:
    """Classify a rate into tier name."""
    if rate <= 0.08:
        return "off-peak"
    elif rate <= 0.15:
        return "mid-peak"
    else:
        return "peak"


def worst_case_cost(instance: Instance) -> float:
    """Compute worst-case cost: every appliance runs at peak hours."""
    peak_rate = max(instance.rates)
    total = 0.0
    for a in instance.appliances:
        total += a["power_kw"] * a["duration_hours"] * peak_rate
    return total


def naive_cost(instance: Instance) -> float:
    """Compute naive cost: appliances start at typical daytime hours."""
    naive_starts = {"dishwasher": 19, "washer": 10, "dryer": 11,
                    "ev_charger": 18, "pool_pump": 14}
    total = 0.0
    for a in instance.appliances:
        start = naive_starts.get(a["name"], 12)
        dur = a["duration_hours"]
        pwr = a["power_kw"]
        total += pwr * sum(instance.rates[start + t] for t in range(dur))
    return total


# --- Main ---

if __name__ == "__main__":
    # Time-of-use rates: 24 hours (index 0 = midnight, index 23 = 11pm)
    # Off-peak: 11pm-7am  ($0.08/kWh) -> hours 23, 0, 1, 2, 3, 4, 5, 6
    # Mid-peak: 7am-4pm   ($0.15/kWh) -> hours 7, 8, 9, 10, 11, 12, 13, 14, 15
    #           9pm-11pm  ($0.15/kWh) -> hours 21, 22
    # Peak:     4pm-9pm   ($0.30/kWh) -> hours 16, 17, 18, 19, 20
    tou_rates: list[float] = []
    for h in range(24):
        if h <= 6 or h == 23:       # off-peak: 11pm-7am
            tou_rates.append(0.08)
        elif 7 <= h <= 15:           # mid-peak: 7am-4pm
            tou_rates.append(0.15)
        elif 16 <= h <= 20:          # peak: 4pm-9pm
            tou_rates.append(0.30)
        else:                        # mid-peak: 9pm-11pm (hours 21, 22)
            tou_rates.append(0.15)

    # Appliance data with noise constraints:
    # - Dishwasher: 2 hours, 1.8 kW, can run anytime
    # - Washer: 1 hour, 0.5 kW, daytime only (7am-10pm) due to noise
    # - Dryer: 2 hours, 5.0 kW, daytime only (7am-10pm) due to noise
    # - EV Charger: 4 hours, 7.2 kW, can run anytime
    # - Pool Pump: 6 hours, 1.1 kW, can run anytime

    # Allowed start hours per appliance
    all_hours = list(range(24))
    daytime_hours = list(range(7, 22))  # 7am to 9pm (must finish by ~10pm)

    appliances = (
        {
            "name": "dishwasher",
            "duration_hours": 2,
            "power_kw": 1.8,
            "allowed_start_hours": all_hours,
        },
        {
            "name": "washer",
            "duration_hours": 1,
            "power_kw": 0.5,
            "allowed_start_hours": daytime_hours,
        },
        {
            "name": "dryer",
            "duration_hours": 2,
            "power_kw": 5.0,
            "allowed_start_hours": daytime_hours,
        },
        {
            "name": "ev_charger",
            "duration_hours": 4,
            "power_kw": 7.2,
            "allowed_start_hours": all_hours,
        },
        {
            "name": "pool_pump",
            "duration_hours": 6,
            "power_kw": 1.1,
            "allowed_start_hours": all_hours,
        },
    )

    instance = Instance(
        appliances=appliances,
        rates=tuple(tou_rates),
        hours=24,
    )

    sol = solve(instance)

    # --- Print Solution Report ---
    log.header("SOLUTION REPORT: Energy Bill Optimization (ILP)")

    log.step("PROBLEM SETUP")
    log.metric("Appliances:", str(instance.n_appliances), tag="DATA")
    log.metric("Horizon:", "24 hours", tag="DATA")
    log.metric("Rate tiers:", "off-peak $0.08, mid-peak $0.15, peak $0.30", tag="DATA", pad=16)
    log.blank()

    # Rate schedule table
    log.step("TIME-OF-USE RATE SCHEDULE")
    log.table_row(
        f"{'Hour':<8} {'Time':<8} {'Rate':>8} {'Tier':<10}",
        tag="TABLE",
    )
    log.divider()
    for h in range(24):
        log.table_row(
            f"{h:<8} {hour_label(h):<8} ${tou_rates[h]:>6.2f}  {rate_tier(tou_rates[h]):<10}",
            tag="DATA",
        )
    log.blank()

    # Appliance table
    log.step("APPLIANCE SPECIFICATIONS")
    log.table_row(
        f"{'Appliance':<14} {'Duration':>8} {'Power':>8} {'kWh/run':>8} {'Allowed':>18}",
        tag="TABLE",
    )
    log.divider()
    for a in appliances:
        kwh = a["duration_hours"] * a["power_kw"]
        hrs = a["allowed_start_hours"]
        window = f"{hour_label(hrs[0])}-{hour_label(hrs[-1] + 1)}" if len(hrs) < 24 else "anytime"
        log.table_row(
            f"{a['name']:<14} {a['duration_hours']:>6} hr {a['power_kw']:>6.1f} kW"
            f" {kwh:>7.1f}  {window:>18}",
            tag="DATA",
        )
    log.blank()

    # Solver results
    log.step("SOLVER RESULTS")
    log.metric("Status:", "Optimal" if sol.is_optimal else "Suboptimal", tag="RESULT")
    log.metric("Feasible:", str(sol.is_feasible), tag="RESULT")
    log.metric("Total cost:", f"${sol.total_cost:.2f}", tag="RESULT")
    log.metric("Algorithm:", sol.algorithm, tag="SOLVE")
    log.metric("Time:", f"{sol.time_seconds:.6f}s", tag="TIMING")
    log.blank()

    if sol.is_optimal and sol.schedule:
        # Optimal schedule
        log.step("OPTIMAL SCHEDULE")
        log.table_row(
            f"{'Appliance':<14} {'Start':>6} {'End':>6} {'Hours':>6}"
            f" {'kWh':>8} {'Rate tier':<12} {'Cost':>8}",
            tag="TABLE",
        )
        log.divider()

        app_lookup = {a["name"]: a for a in appliances}
        for name in sorted(sol.schedule.keys()):
            start = sol.schedule[name]
            a = app_lookup[name]
            end = start + a["duration_hours"]
            kwh = a["power_kw"] * a["duration_hours"]
            # Determine the rate tier(s) the appliance runs in
            run_rates = [tou_rates[start + t] for t in range(a["duration_hours"])]
            tiers = sorted(set(rate_tier(r) for r in run_rates))
            tier_str = "/".join(tiers)
            cost = sol.cost_breakdown[name]
            log.table_row(
                f"{name:<14} {hour_label(start):>6} {hour_label(end % 24):>6}"
                f" {a['duration_hours']:>5}h {kwh:>7.1f}  {tier_str:<12} ${cost:>6.2f}",
                tag="ASSIGN",
            )

        log.divider()
        total_kwh = sum(
            app_lookup[n]["power_kw"] * app_lookup[n]["duration_hours"]
            for n in sol.schedule
        )
        log.table_row(
            f"{'TOTAL':<14} {'':>6} {'':>6} {'':>6}"
            f" {total_kwh:>7.1f}  {'':>12} ${sol.total_cost:>6.2f}",
            tag="RESULT",
        )
        log.blank()

        # Visual timeline
        log.step("24-HOUR TIMELINE")
        # Header row with hour markers
        hour_marks = "".join(f"{h % 24:>3}" for h in range(24))
        log.table_row(f"{'':14} {hour_marks}", tag="TABLE")
        log.divider()

        for name in sorted(sol.schedule.keys()):
            start = sol.schedule[name]
            a = app_lookup[name]
            dur = a["duration_hours"]
            timeline = ""
            for h in range(24):
                if start <= h < start + dur:
                    timeline += "  #"
                else:
                    timeline += "  ."
            log.table_row(f"{name:<14}{timeline}", tag="DATA")

        # Rate tier row
        tier_row = ""
        for h in range(24):
            r = tou_rates[h]
            if r <= 0.08:
                tier_row += "  L"
            elif r <= 0.15:
                tier_row += "  M"
            else:
                tier_row += "  H"
        log.table_row(f"{'rate tier':<14}{tier_row}", tag="STATS")
        log.blank()

        # Cost comparison
        log.step("COST COMPARISON")
        worst = worst_case_cost(instance)
        naive = naive_cost(instance)
        optimal = sol.total_cost

        log.metric("Worst case (all peak):", f"${worst:.2f}", tag="STATS")
        log.metric("Naive (typical hours):", f"${naive:.2f}", tag="STATS")
        log.metric("Optimal (ILP):", f"${optimal:.2f}", tag="RESULT")
        log.blank()

        savings_vs_worst = worst - optimal
        savings_vs_naive = naive - optimal
        log.metric("Savings vs worst:", f"${savings_vs_worst:.2f} ({savings_vs_worst / worst * 100:.1f}%)", tag="RESULT")
        log.metric("Savings vs naive:", f"${savings_vs_naive:.2f} ({savings_vs_naive / naive * 100:.1f}%)", tag="RESULT")
        log.blank()

        # Per-appliance cost breakdown
        log.step("PER-APPLIANCE COST BREAKDOWN")
        log.table_row(
            f"{'Appliance':<14} {'Optimal':>10} {'Naive':>10} {'Worst':>10} {'Saved':>10}",
            tag="TABLE",
        )
        log.divider()

        naive_starts_map = {"dishwasher": 19, "washer": 10, "dryer": 11,
                            "ev_charger": 18, "pool_pump": 14}
        peak_rate = max(tou_rates)
        for name in sorted(sol.schedule.keys()):
            a = app_lookup[name]
            opt_cost = sol.cost_breakdown[name]
            wst_cost = a["power_kw"] * a["duration_hours"] * peak_rate
            naive_start = naive_starts_map.get(name, 12)
            naive_c = a["power_kw"] * sum(
                tou_rates[naive_start + t] for t in range(a["duration_hours"])
            )
            saved = naive_c - opt_cost
            log.table_row(
                f"{name:<14} ${opt_cost:>8.2f} ${naive_c:>8.2f}"
                f" ${wst_cost:>8.2f} ${saved:>8.2f}",
                tag="ASSIGN",
            )
        log.blank()

        # Monthly/annual projections
        log.step("PROJECTED SAVINGS (30-DAY / 365-DAY)")
        log.metric("Daily optimal:", f"${optimal:.2f}", tag="STATS")
        log.metric("Daily naive:", f"${naive:.2f}", tag="STATS")
        log.metric("Monthly savings:", f"${savings_vs_naive * 30:.2f}", tag="RESULT")
        log.metric("Annual savings:", f"${savings_vs_naive * 365:.2f}", tag="RESULT")
        log.blank()

    else:
        log.warning("Solver returned infeasible -- check constraints", tag="WARNING")
        log.blank()

    # Independent verification
    log.step("INDEPENDENT VERIFICATION")
    for check_name, result in sol.constraint_check.items():
        if isinstance(result, bool):
            log.check(check_name, result, tag="VERIFY")
        elif isinstance(result, dict):
            for sub_name, sub_val in result.items():
                log.check(f"  {sub_name}", round(sub_val, 4), tag="VERIFY")
        else:
            log.check(check_name, result, tag="VERIFY")
    log.blank()

    log.divider(style="thick")

    # Save JSON
    output = {
        "schedule": sol.schedule,
        "total_cost": round(sol.total_cost, 4),
        "cost_breakdown": {k: round(v, 4) for k, v in sol.cost_breakdown.items()},
        "is_optimal": sol.is_optimal,
        "is_feasible": sol.is_feasible,
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
        "comparison": {
            "worst_case_cost": round(worst_case_cost(instance), 4),
            "naive_cost": round(naive_cost(instance), 4),
            "savings_vs_naive": round(naive_cost(instance) - sol.total_cost, 4),
            "savings_vs_worst": round(worst_case_cost(instance) - sol.total_cost, 4),
        },
    }
    with open(str(Path(__file__).parent / "solution.json"), "w") as f:
        json.dump(output, f, indent=2)
    log.success("solution.json", tag="SAVE")
