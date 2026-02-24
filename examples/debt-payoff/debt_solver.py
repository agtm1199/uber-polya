#!/usr/bin/env python3
"""Debt Payoff Optimization solver (Avalanche vs Snowball).

Simulates month-by-month debt repayment under two strategies to find
the allocation of extra payments that minimizes total interest paid.
Complexity: O(D * M) where D = number of debts, M = months to payoff.
Correctness: Simulation verified independently; avalanche is provably
optimal among greedy single-target strategies.
"""
from __future__ import annotations

import time
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger
log = PolyaLogger()


# --- Data Model ---

@dataclass(frozen=True)
class Instance:
    """Problem instance for debt payoff optimization."""
    debts: tuple[dict[str, Any], ...]   # each: name, balance, apr, min_payment
    extra_monthly_payment: float        # extra cash above all minimums combined

    @property
    def total_balance(self) -> float:
        return sum(d["balance"] for d in self.debts)

    @property
    def total_minimums(self) -> float:
        return sum(d["min_payment"] for d in self.debts)


@dataclass
class Solution:
    """Verified solution with metadata."""
    strategy_name: str
    monthly_schedule: list[dict[str, Any]]  # simplified month-by-month log
    total_interest_paid: float
    months_to_payoff: int
    is_optimal: bool
    is_feasible: bool
    algorithm: str
    time_seconds: float
    certificate: str


# --- Simulation Engine ---

def _simulate(
    instance: Instance,
    priority_key: str,
    priority_reverse: bool,
) -> Solution:
    """Run a month-by-month debt payoff simulation.

    Each month:
      1. Accrue interest on all debts (monthly_rate = apr / 12).
      2. Pay the minimum on every debt that has a remaining balance.
      3. Allocate extra payment (plus freed minimums from paid-off debts)
         to the highest-priority debt according to the chosen strategy.
      4. If a debt is paid off mid-allocation, redirect the surplus to
         the next priority debt.

    Args:
        instance: The debt payoff problem instance.
        priority_key: Dict key to sort debts by ("apr" or "balance").
        priority_reverse: True = highest first, False = lowest first.

    Returns:
        A Solution dataclass with full schedule and totals.
    """
    strategy_name = "avalanche" if priority_key == "apr" else "snowball"
    t0 = time.perf_counter()

    # Working copy of balances
    balances = {d["name"]: float(d["balance"]) for d in instance.debts}
    monthly_rates = {d["name"]: d["apr"] / 12.0 for d in instance.debts}
    min_payments = {d["name"]: float(d["min_payment"]) for d in instance.debts}

    # Build priority order (stable sort by key, then by name for ties)
    debt_order = sorted(
        instance.debts,
        key=lambda d: (d[priority_key], d["name"]),
        reverse=priority_reverse,
    )
    priority_names = [d["name"] for d in debt_order]

    total_interest = 0.0
    schedule: list[dict[str, Any]] = []
    month = 0
    max_months = 600  # safety cap: 50 years

    while any(b > 0.005 for b in balances.values()) and month < max_months:
        month += 1
        month_interest = 0.0
        month_payments: dict[str, float] = {name: 0.0 for name in balances}

        # Step 1: Accrue interest
        for name in balances:
            if balances[name] > 0:
                interest = balances[name] * monthly_rates[name]
                balances[name] += interest
                month_interest += interest

        total_interest += month_interest

        # Step 2: Pay minimums (or remaining balance if less than minimum)
        freed_minimums = 0.0
        for name in balances:
            if balances[name] > 0:
                payment = min(min_payments[name], balances[name])
                balances[name] -= payment
                month_payments[name] += payment
            else:
                # This debt is already paid off; its minimum is freed up
                freed_minimums += min_payments[name]

        # Step 3: Allocate extra + freed minimums to priority target(s)
        available = instance.extra_monthly_payment + freed_minimums

        for name in priority_names:
            if available <= 0:
                break
            if balances[name] > 0:
                payment = min(available, balances[name])
                balances[name] -= payment
                month_payments[name] += payment
                available -= payment

        # Round tiny residuals to zero
        for name in balances:
            if balances[name] < 0.005:
                balances[name] = 0.0

        # Record month snapshot (simplified for schedule)
        schedule.append({
            "month": month,
            "interest": round(month_interest, 2),
            "payments": {k: round(v, 2) for k, v in month_payments.items() if v > 0},
            "remaining_balances": {k: round(v, 2) for k, v in balances.items() if v > 0},
        })

    elapsed = time.perf_counter() - t0

    return Solution(
        strategy_name=strategy_name,
        monthly_schedule=schedule,
        total_interest_paid=round(total_interest, 2),
        months_to_payoff=month,
        is_optimal=False,       # set after comparison
        is_feasible=False,      # set after verification
        algorithm=f"Greedy {strategy_name} simulation (month-by-month)",
        time_seconds=elapsed,
        certificate=f"Simulated {month} months; total interest ${total_interest:,.2f}",
    )


def solve(instance: Instance) -> Solution:
    """Solve using the avalanche strategy (highest interest rate first).

    The avalanche method is provably optimal among greedy single-target
    strategies because it minimizes the balance-weighted average interest
    rate at every step.
    """
    sol = _simulate(instance, priority_key="apr", priority_reverse=True)
    sol.is_optimal = True  # avalanche is optimal among greedy strategies
    ok, checks = verify(instance, sol)
    sol.is_feasible = ok
    sol.certificate += f" | verification: {'PASS' if ok else 'FAIL'}"
    return sol


def solve_snowball(instance: Instance) -> Solution:
    """Solve using the snowball strategy (lowest balance first).

    The snowball method pays off small debts first for psychological
    momentum, but typically costs more in total interest than avalanche.
    """
    sol = _simulate(instance, priority_key="balance", priority_reverse=False)
    sol.is_optimal = False
    ok, checks = verify(instance, sol)
    sol.is_feasible = ok
    sol.certificate += f" | verification: {'PASS' if ok else 'FAIL'}"
    return sol


# --- Verification (independent of solver logic) ---

def verify(
    instance: Instance,
    solution: Solution,
) -> tuple[bool, dict[str, Any]]:
    """Independently verify the debt payoff simulation.

    Checks:
      1. All debts reach zero balance by the final month.
      2. Minimum payments are always met (or balance is paid in full).
      3. No negative balances appear at any point.
      4. Total extra payment never exceeds the monthly budget.
      5. Total principal repaid equals original total balance (accounting
         for interest added and payments made).
    """
    checks: dict[str, Any] = {}
    all_ok = True

    schedule = solution.monthly_schedule
    debts_by_name = {d["name"]: d for d in instance.debts}
    min_pays = {d["name"]: d["min_payment"] for d in instance.debts}

    # Check 1: All debts reach zero
    final = schedule[-1] if schedule else {}
    remaining = final.get("remaining_balances", {})
    debts_at_zero = all(
        name not in remaining or remaining[name] < 0.01
        for name in debts_by_name
    )
    checks["all_debts_zero"] = debts_at_zero
    if not debts_at_zero:
        all_ok = False

    # Check 2: Minimums always met
    minimums_met = True
    for entry in schedule:
        payments = entry["payments"]
        rem = entry["remaining_balances"]
        for name, mp in min_pays.items():
            paid = payments.get(name, 0.0)
            still_owed = rem.get(name, 0.0)
            # Either paid at least the minimum, or paid off the entire balance
            if still_owed > 0.01 and paid < mp - 0.01:
                minimums_met = False
                break
    checks["minimums_always_met"] = minimums_met
    if not minimums_met:
        all_ok = False

    # Check 3: No negative balances
    no_negatives = True
    for entry in schedule:
        for bal in entry["remaining_balances"].values():
            if bal < -0.01:
                no_negatives = False
                break
    checks["no_negative_balances"] = no_negatives
    if not no_negatives:
        all_ok = False

    # Check 4: Extra payment never exceeds budget
    budget_ok = True
    for entry in schedule:
        total_paid = sum(entry["payments"].values())
        # Maximum possible payment = all minimums + extra
        max_allowed = instance.total_minimums + instance.extra_monthly_payment
        if total_paid > max_allowed + 0.01:
            budget_ok = False
            break
    checks["extra_within_budget"] = budget_ok
    if not budget_ok:
        all_ok = False

    # Check 5: Total payments ~ original balance + total interest
    total_payments = sum(
        sum(entry["payments"].values()) for entry in schedule
    )
    expected_total = instance.total_balance + solution.total_interest_paid
    payment_balance = abs(total_payments - expected_total) < 1.0
    checks["payments_balance_check"] = payment_balance
    checks["total_payments"] = round(total_payments, 2)
    checks["expected_total"] = round(expected_total, 2)
    if not payment_balance:
        all_ok = False

    return all_ok, checks


# --- Main ---

if __name__ == "__main__":
    # Build instance: 4 realistic debts
    instance = Instance(
        debts=(
            {"name": "Credit Card",  "balance": 6200.0,  "apr": 0.2299, "min_payment": 120.0},
            {"name": "Car Loan",     "balance": 12000.0, "apr": 0.065,  "min_payment": 250.0},
            {"name": "Student Loan", "balance": 25000.0, "apr": 0.045,  "min_payment": 280.0},
            {"name": "Personal Loan","balance": 3500.0,  "apr": 0.15,   "min_payment": 75.0},
        ),
        extra_monthly_payment=500.0,
    )

    # -- Header --
    log.header("DEBT PAYOFF OPTIMIZATION")

    log.section("PROBLEM INSTANCE")
    log.metric("Total debt:",      f"${instance.total_balance:,.2f}", tag="DATA")
    log.metric("Total minimums:",  f"${instance.total_minimums:,.2f}/mo", tag="DATA")
    log.metric("Extra payment:",   f"${instance.extra_monthly_payment:,.2f}/mo", tag="DATA")
    log.metric("Total monthly:",   f"${instance.total_minimums + instance.extra_monthly_payment:,.2f}/mo", tag="DATA")
    log.blank()

    log.step("DEBT DETAILS")
    log.table_row(
        f"{'Debt':<16} {'Balance':>10} {'APR':>8} {'Min Pay':>10}",
        tag="TABLE",
    )
    log.divider()
    for d in instance.debts:
        log.table_row(
            f"{d['name']:<16} ${d['balance']:>9,.2f} {d['apr']*100:>7.2f}% ${d['min_payment']:>8,.2f}",
            tag="TABLE",
        )
    log.blank()

    # -- Solve with both strategies --
    log.section("STRATEGY COMPARISON")

    avalanche = solve(instance)
    snowball = solve_snowball(instance)

    interest_saved = snowball.total_interest_paid - avalanche.total_interest_paid
    months_saved = snowball.months_to_payoff - avalanche.months_to_payoff

    # Avalanche results
    log.step("AVALANCHE (Highest Rate First)")
    log.info(
        "Priority: Credit Card (22.99%) > Personal Loan (15.0%)"
        " > Car Loan (6.5%) > Student Loan (4.5%)",
        tag="MODEL",
    )
    log.metric("Total interest:", f"${avalanche.total_interest_paid:,.2f}", tag="RESULT")
    log.metric("Months to payoff:", f"{avalanche.months_to_payoff}", tag="RESULT")
    log.metric("Total paid:",
               f"${instance.total_balance + avalanche.total_interest_paid:,.2f}", tag="RESULT")
    log.metric("Algorithm:", avalanche.algorithm, tag="SOLVE")
    log.metric("Time:", f"{avalanche.time_seconds:.4f}s", tag="TIMING")
    log.blank()

    # Snowball results
    log.step("SNOWBALL (Lowest Balance First)")
    log.info(
        "Priority: Personal Loan ($3,500) > Credit Card ($6,200)"
        " > Car Loan ($12,000) > Student Loan ($25,000)",
        tag="MODEL",
    )
    log.metric("Total interest:", f"${snowball.total_interest_paid:,.2f}", tag="RESULT")
    log.metric("Months to payoff:", f"{snowball.months_to_payoff}", tag="RESULT")
    log.metric("Total paid:",
               f"${instance.total_balance + snowball.total_interest_paid:,.2f}", tag="RESULT")
    log.metric("Algorithm:", snowball.algorithm, tag="SOLVE")
    log.metric("Time:", f"{snowball.time_seconds:.4f}s", tag="TIMING")
    log.blank()

    # Head-to-head comparison
    log.step("HEAD-TO-HEAD COMPARISON")
    log.table_row(
        f"{'Metric':<25} {'Avalanche':>14} {'Snowball':>14} {'Difference':>14}",
        tag="TABLE",
    )
    log.divider()
    log.table_row(
        f"{'Total interest':<25} "
        f"${avalanche.total_interest_paid:>12,.2f} "
        f"${snowball.total_interest_paid:>12,.2f} "
        f"${interest_saved:>12,.2f}",
        tag="TABLE",
    )
    log.table_row(
        f"{'Months to payoff':<25} "
        f"{avalanche.months_to_payoff:>14} "
        f"{snowball.months_to_payoff:>14} "
        f"{months_saved:>14}",
        tag="TABLE",
    )
    total_aval = instance.total_balance + avalanche.total_interest_paid
    total_snow = instance.total_balance + snowball.total_interest_paid
    log.table_row(
        f"{'Total paid':<25} "
        f"${total_aval:>12,.2f} "
        f"${total_snow:>12,.2f} "
        f"${total_snow - total_aval:>12,.2f}",
        tag="TABLE",
    )
    log.blank()

    if interest_saved > 0:
        log.success(
            f"Avalanche saves ${interest_saved:,.2f} in interest"
            f" and {months_saved} month(s) vs snowball",
            tag="RECOMMEND",
        )
    else:
        log.info(
            "Both strategies produce similar results for this instance",
            tag="RECOMMEND",
        )
    log.blank()

    # -- Payoff timeline --
    log.step("PAYOFF TIMELINE (Avalanche)")
    debts_paid_off: dict[str, int] = {}
    for entry in avalanche.monthly_schedule:
        for d in instance.debts:
            name = d["name"]
            if name not in debts_paid_off and name not in entry["remaining_balances"]:
                debts_paid_off[name] = entry["month"]

    for name, mo in sorted(debts_paid_off.items(), key=lambda x: x[1]):
        pct = mo / avalanche.months_to_payoff
        log.bar(f"{name:<16} month {mo:>3}", pct, tag="RESULT")
    log.blank()

    # -- Verification --
    log.section("INDEPENDENT VERIFICATION")

    log.step("Avalanche Verification")
    ok_a, checks_a = verify(instance, avalanche)
    for check_name, result in checks_a.items():
        if isinstance(result, bool):
            log.check(check_name, result, tag="VERIFY")
        else:
            log.check(check_name, result, tag="VERIFY")
    log.blank()

    log.step("Snowball Verification")
    ok_s, checks_s = verify(instance, snowball)
    for check_name, result in checks_s.items():
        if isinstance(result, bool):
            log.check(check_name, result, tag="VERIFY")
        else:
            log.check(check_name, result, tag="VERIFY")
    log.blank()

    # -- Save solution --
    output = {
        "problem": {
            "debts": [dict(d) for d in instance.debts],
            "extra_monthly_payment": instance.extra_monthly_payment,
            "total_balance": instance.total_balance,
            "total_minimums": instance.total_minimums,
        },
        "avalanche": {
            "strategy": avalanche.strategy_name,
            "total_interest_paid": avalanche.total_interest_paid,
            "months_to_payoff": avalanche.months_to_payoff,
            "total_paid": round(instance.total_balance + avalanche.total_interest_paid, 2),
            "is_optimal": avalanche.is_optimal,
            "is_feasible": avalanche.is_feasible,
            "algorithm": avalanche.algorithm,
            "time_seconds": avalanche.time_seconds,
            "payoff_order": [
                {"debt": name, "month": mo}
                for name, mo in sorted(debts_paid_off.items(), key=lambda x: x[1])
            ],
        },
        "snowball": {
            "strategy": snowball.strategy_name,
            "total_interest_paid": snowball.total_interest_paid,
            "months_to_payoff": snowball.months_to_payoff,
            "total_paid": round(instance.total_balance + snowball.total_interest_paid, 2),
            "is_optimal": snowball.is_optimal,
            "is_feasible": snowball.is_feasible,
            "algorithm": snowball.algorithm,
            "time_seconds": snowball.time_seconds,
        },
        "comparison": {
            "interest_saved_by_avalanche": round(interest_saved, 2),
            "months_saved_by_avalanche": months_saved,
            "recommended_strategy": "avalanche",
        },
    }
    with open(Path(__file__).parent / "solution.json", "w") as f:
        json.dump(output, f, indent=2)
    log.success("solution.json", tag="SAVE")
    log.divider(style="thick")
