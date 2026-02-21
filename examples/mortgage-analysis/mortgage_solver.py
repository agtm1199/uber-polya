#!/usr/bin/env python3
"""Mortgage Comparison Analysis solver -- Financial mathematics.

Compares three mortgage options for a $320,000 loan:
  1. 30-year fixed at 6.5%
  2. 15-year fixed at 5.8%
  3. Refinance: 30-year at 6.5% for 5 years, then 25-year at 5.2% + $6k closing

Computes full amortization schedules, total costs, and refinance break-even.

Algorithm: Annuity PMT formula + amortization schedules + break-even search.
Complexity: O(n) per schedule where n = number of monthly payments.
Correctness: Independent verify() checks schedule sums and final balances.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger
log = PolyaLogger()


# --- Data Model ---

@dataclass(frozen=True)
class MortgageOption:
    """A single mortgage option."""
    name: str
    annual_rate: float          # APR as decimal (e.g. 0.065)
    term_years: int             # loan term in years
    loan_amount: float          # principal
    closing_costs: float = 0.0  # upfront costs added to total

    @property
    def monthly_rate(self) -> float:
        return self.annual_rate / 12.0

    @property
    def n_payments(self) -> int:
        return self.term_years * 12


@dataclass(frozen=True)
class Instance:
    """Problem instance: compare multiple mortgage options."""
    loan_amount: float
    options: list[MortgageOption]
    home_price: float = 0.0
    down_payment: float = 0.0


@dataclass
class AmortizationEntry:
    """Single month in an amortization schedule."""
    month: int
    payment: float
    principal: float
    interest: float
    balance: float


@dataclass
class OptionResult:
    """Computed results for one mortgage option."""
    name: str
    monthly_payment: float
    total_interest: float
    total_paid: float           # principal + interest + closing costs
    schedule: list[AmortizationEntry]


@dataclass
class Solution:
    """Verified solution with metadata."""
    comparisons: list[OptionResult]
    refinance_breakeven_months: int | None    # months after refi to recoup costs
    refinance_net_savings: float              # total savings of refi vs staying
    cheapest_option: str
    objective: float            # total cost of cheapest option
    is_optimal: bool
    is_feasible: bool
    algorithm: str
    time_seconds: float
    certificate: str
    constraint_check: dict[str, bool] = field(default_factory=dict)


# --- Financial Helpers ---

def compute_monthly_payment(principal: float, monthly_rate: float,
                            n_payments: int) -> float:
    """Compute fixed monthly payment using the annuity formula.

    PMT = L * r * (1 + r)^n / ((1 + r)^n - 1)
    """
    if monthly_rate == 0.0:
        return principal / n_payments
    r = monthly_rate
    factor = (1 + r) ** n_payments
    return principal * r * factor / (factor - 1)


def build_amortization_schedule(principal: float, monthly_rate: float,
                                n_payments: int,
                                monthly_payment: float) -> list[AmortizationEntry]:
    """Build a full month-by-month amortization schedule."""
    schedule: list[AmortizationEntry] = []
    balance = principal

    for month in range(1, n_payments + 1):
        interest = balance * monthly_rate
        # Last payment: adjust to clear balance exactly
        if month == n_payments:
            principal_part = balance
            payment = principal_part + interest
        else:
            principal_part = monthly_payment - interest
            payment = monthly_payment

        balance -= principal_part

        schedule.append(AmortizationEntry(
            month=month,
            payment=round(payment, 2),
            principal=round(principal_part, 2),
            interest=round(interest, 2),
            balance=round(max(balance, 0.0), 2),
        ))

    return schedule


def compute_option(option: MortgageOption) -> OptionResult:
    """Compute the full amortization and totals for one mortgage option."""
    pmt = compute_monthly_payment(
        option.loan_amount, option.monthly_rate, option.n_payments,
    )
    schedule = build_amortization_schedule(
        option.loan_amount, option.monthly_rate, option.n_payments, pmt,
    )

    total_interest = sum(e.interest for e in schedule)
    total_paid = sum(e.payment for e in schedule) + option.closing_costs

    return OptionResult(
        name=option.name,
        monthly_payment=round(pmt, 2),
        total_interest=round(total_interest, 2),
        total_paid=round(total_paid, 2),
        schedule=schedule,
    )


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Solve the mortgage comparison problem."""
    t0 = time.perf_counter()

    comparisons: list[OptionResult] = []
    for opt in instance.options:
        comparisons.append(compute_option(opt))

    # --- Refinance break-even analysis ---
    # Compare option 3 (refinance) against option 1 (original 30-year)
    # after the refinance point (month 61 onward).
    refinance_breakeven_months: int | None = None
    refinance_net_savings: float = 0.0

    # Find the 30-year and refinance results by name
    result_30yr = next((c for c in comparisons if "30-year" in c.name.lower()), None)
    result_refi = next((c for c in comparisons if "refinance" in c.name.lower()), None)

    if result_30yr is not None and result_refi is not None:
        # The refinance option includes 5 years of original payments + closing
        # costs + 25 years of new payments. Compare cumulative cost month by
        # month after the refinance event (month 61).
        #
        # For the 30-year loan, months 61..360 are the remaining payments.
        # For the refinance, months 61 onward are the new 25-year schedule
        # plus the $6,000 closing cost incurred at month 60.
        refi_option = next(o for o in instance.options if "refinance" in o.name.lower())
        closing_costs = refi_option.closing_costs

        # Monthly payment difference: staying vs refinancing
        old_monthly = result_30yr.monthly_payment
        # The refinance schedule's first 60 months use old_monthly, then switch.
        # We need the new monthly payment (months 61+).
        # In our model, the refinance OptionResult has a blended schedule.
        # Extract the new payment from month 61 of the refinance schedule.
        new_monthly = result_refi.schedule[60].payment if len(result_refi.schedule) > 60 else 0.0

        # Break-even: cumulative savings vs closing costs
        monthly_savings = old_monthly - new_monthly
        cumulative_savings = 0.0
        if monthly_savings > 0:
            for month_offset in range(1, 300 + 1):  # up to 25 years
                cumulative_savings += monthly_savings
                if cumulative_savings >= closing_costs:
                    refinance_breakeven_months = month_offset
                    break

        # Net savings over full remaining life (25 years = 300 months)
        # Total remaining on 30-year (months 61-360): 300 payments
        remaining_30yr = sum(e.payment for e in result_30yr.schedule[60:])
        # Total on refinance (months 61-360): 300 payments from new schedule
        remaining_refi = sum(e.payment for e in result_refi.schedule[60:]) + closing_costs
        refinance_net_savings = round(remaining_30yr - remaining_refi, 2)

    # Determine cheapest option
    cheapest = min(comparisons, key=lambda c: c.total_paid)

    elapsed = time.perf_counter() - t0

    sol = Solution(
        comparisons=comparisons,
        refinance_breakeven_months=refinance_breakeven_months,
        refinance_net_savings=refinance_net_savings,
        cheapest_option=cheapest.name,
        objective=cheapest.total_paid,
        is_optimal=True,
        is_feasible=True,
        algorithm="Annuity PMT + Amortization Schedule + Break-Even Search",
        time_seconds=elapsed,
        certificate="Closed-form PMT verified by amortization schedule summation",
    )

    # Independent verification
    sol.is_feasible, sol.constraint_check = verify(instance, comparisons)

    return sol


# --- Verification (independent of solver) ---

def verify(instance: Instance, comparisons: list[OptionResult]) -> tuple[bool, dict[str, bool]]:
    """Independently verify that amortization schedules are correct.

    Handles both simple fixed-rate loans and two-phase refinance schedules.
    Rounding tolerance is generous because individual entries are rounded to
    cents, and drift accumulates over hundreds of payments.
    """
    checks: dict[str, bool] = {}
    all_ok = True

    # Rounding tolerance: $0.50 per 100 payments is conservative
    PRINCIPAL_TOL = 1.0   # dollars -- principal sum vs loan amount
    INTEREST_TOL = 2.0    # dollars -- recomputed interest vs reported
    BALANCE_TOL = 0.02    # dollars -- final balance should be ~0
    PMT_TOL = 0.02        # dollars -- payment vs formula

    for comp in comparisons:
        option = next(o for o in instance.options if o.name == comp.name)
        prefix = comp.name.replace(" ", "_").lower()

        # Check 1: Total principal paid equals loan amount
        total_principal = sum(e.principal for e in comp.schedule)
        ok = abs(total_principal - option.loan_amount) < PRINCIPAL_TOL
        checks[f"{prefix}_principal_sums_to_loan"] = ok
        if not ok:
            all_ok = False

        # Check 2: Final balance is zero (or effectively zero)
        final_balance = comp.schedule[-1].balance
        ok = abs(final_balance) < BALANCE_TOL
        checks[f"{prefix}_final_balance_zero"] = ok
        if not ok:
            all_ok = False

        # Check 3: Every month, interest = balance_prev * monthly_rate
        # For refinance options (two-phase), determine the rate per month.
        is_refinance = "refinance" in comp.name.lower()
        if is_refinance:
            # Phase A: first 60 months at the original 30-year rate (6.5%)
            # Phase B: months 61+ at the refinance rate (5.2%)
            # These rates are encoded in the problem, not in the dummy option.
            # Recover them from the schedule itself: interest / prev_balance.
            rate_phase_a = 0.065 / 12  # original rate
            rate_phase_b = 0.052 / 12  # refinance rate

        recomputed_interest = 0.0
        balance = option.loan_amount
        for entry in comp.schedule:
            if is_refinance:
                monthly_rate = rate_phase_a if entry.month <= 60 else rate_phase_b
            else:
                monthly_rate = option.monthly_rate
            expected_interest = round(balance * monthly_rate, 2)
            recomputed_interest += expected_interest
            balance -= entry.principal
        ok = abs(recomputed_interest - comp.total_interest) < INTEREST_TOL
        checks[f"{prefix}_interest_recomputed_matches"] = ok
        if not ok:
            all_ok = False

        # Check 4: Monthly payment matches annuity formula (non-refinance only)
        if not is_refinance:
            expected_pmt = compute_monthly_payment(
                option.loan_amount, option.monthly_rate, option.n_payments,
            )
            ok = abs(expected_pmt - comp.monthly_payment) < PMT_TOL
            checks[f"{prefix}_pmt_matches_formula"] = ok
            if not ok:
                all_ok = False

        # Check 5: total_paid = total_interest + loan_amount + closing_costs
        expected_total = comp.total_interest + option.loan_amount + option.closing_costs
        ok = abs(expected_total - comp.total_paid) < INTEREST_TOL
        checks[f"{prefix}_total_paid_consistent"] = ok
        if not ok:
            all_ok = False

    return all_ok, checks


# --- Main ---

if __name__ == "__main__":
    # --- Build instance ---
    home_price = 400_000.0
    down_payment = 80_000.0
    loan_amount = home_price - down_payment  # $320,000

    # Option 1: 30-year fixed at 6.5%
    opt1 = MortgageOption(
        name="30-Year Fixed 6.5%",
        annual_rate=0.065,
        term_years=30,
        loan_amount=loan_amount,
    )

    # Option 2: 15-year fixed at 5.8%
    opt2 = MortgageOption(
        name="15-Year Fixed 5.8%",
        annual_rate=0.058,
        term_years=15,
        loan_amount=loan_amount,
    )

    # Option 3: Refinance -- 30-year at 6.5% for 5 years, then refi remaining
    # balance to 25-year at 5.2% with $6,000 closing costs.
    # We model this as a single combined schedule for total-cost comparison.
    # First, compute the remaining balance after 60 months on the 30-year.
    pmt_30yr = compute_monthly_payment(loan_amount, 0.065 / 12, 360)
    schedule_first_5yr = build_amortization_schedule(
        loan_amount, 0.065 / 12, 360, pmt_30yr,
    )[:60]
    remaining_balance = loan_amount - sum(e.principal for e in schedule_first_5yr)

    opt3 = MortgageOption(
        name="Refinance 30yr->25yr at 5.2%",
        annual_rate=0.0,  # blended -- we handle manually below
        term_years=30,    # total span: 5 + 25 = 30 years
        loan_amount=loan_amount,
        closing_costs=6_000.0,
    )

    # For option 3 we build a custom combined schedule rather than using
    # compute_option directly, since it has two phases.
    # Phase A: first 60 months at 6.5%
    phase_a = schedule_first_5yr

    # Phase B: remaining balance at 5.2% for 25 years (300 months)
    new_rate = 0.052 / 12
    new_term = 300
    pmt_refi = compute_monthly_payment(remaining_balance, new_rate, new_term)
    phase_b_raw = build_amortization_schedule(
        remaining_balance, new_rate, new_term, pmt_refi,
    )
    # Re-number phase B months to continue from 61
    phase_b: list[AmortizationEntry] = []
    for entry in phase_b_raw:
        phase_b.append(AmortizationEntry(
            month=60 + entry.month,
            payment=entry.payment,
            principal=entry.principal,
            interest=entry.interest,
            balance=entry.balance,
        ))

    combined_schedule = phase_a + phase_b
    total_interest_refi = sum(e.interest for e in combined_schedule)
    total_paid_refi = sum(e.payment for e in combined_schedule) + opt3.closing_costs

    refi_result = OptionResult(
        name=opt3.name,
        monthly_payment=round(pmt_refi, 2),  # the post-refinance payment
        total_interest=round(total_interest_refi, 2),
        total_paid=round(total_paid_refi, 2),
        schedule=combined_schedule,
    )

    # Build instance with options 1 and 2 (option 3 is custom)
    instance = Instance(
        loan_amount=loan_amount,
        options=[opt1, opt2, opt3],
        home_price=home_price,
        down_payment=down_payment,
    )

    # Solve options 1 and 2 normally
    t0 = time.perf_counter()

    result_1 = compute_option(opt1)
    result_2 = compute_option(opt2)

    comparisons = [result_1, result_2, refi_result]

    # Break-even analysis: option 3 vs option 1 after month 60
    closing_costs = opt3.closing_costs
    old_monthly = result_1.monthly_payment
    new_monthly = refi_result.monthly_payment
    monthly_savings = old_monthly - new_monthly

    refinance_breakeven_months: int | None = None
    if monthly_savings > 0:
        cumulative = 0.0
        for m in range(1, 301):
            cumulative += monthly_savings
            if cumulative >= closing_costs:
                refinance_breakeven_months = m
                break

    # Net savings over remaining 25 years
    remaining_30yr_cost = sum(e.payment for e in result_1.schedule[60:])
    remaining_refi_cost = sum(e.payment for e in refi_result.schedule[60:]) + closing_costs
    refinance_net_savings = round(remaining_30yr_cost - remaining_refi_cost, 2)

    cheapest = min(comparisons, key=lambda c: c.total_paid)
    elapsed = time.perf_counter() - t0

    # Verify
    is_feasible, constraint_check = verify(instance, comparisons)

    sol = Solution(
        comparisons=comparisons,
        refinance_breakeven_months=refinance_breakeven_months,
        refinance_net_savings=refinance_net_savings,
        cheapest_option=cheapest.name,
        objective=cheapest.total_paid,
        is_optimal=True,
        is_feasible=is_feasible,
        algorithm="Annuity PMT + Amortization Schedule + Break-Even Search",
        time_seconds=elapsed,
        certificate="Closed-form PMT verified by amortization schedule summation",
        constraint_check=constraint_check,
    )

    # --- Print Solution Report ---
    log.header("SOLUTION REPORT: Mortgage Comparison Analysis")

    log.step("PROBLEM SETUP")
    log.metric("Home price:", f"${home_price:,.2f}", tag="DATA")
    log.metric("Down payment:", f"${down_payment:,.2f}", tag="DATA")
    log.metric("Loan amount:", f"${loan_amount:,.2f}", tag="DATA")
    log.blank()

    # Summary table
    log.step("OPTION COMPARISON")
    log.table_row(
        f"{'Option':<35} {'Monthly PMT':>12} {'Total Interest':>16} {'Total Paid':>14}",
        tag="TABLE",
    )
    log.divider()
    for comp in comparisons:
        tag = "RESULT" if comp.name == cheapest.name else "DATA"
        label = comp.name
        if comp.name == cheapest.name:
            label += " *"
        log.table_row(
            f"{label:<35} ${comp.monthly_payment:>11,.2f} "
            f"${comp.total_interest:>15,.2f} ${comp.total_paid:>13,.2f}",
            tag=tag,
        )
    log.blank()

    # Detailed per-option breakdown
    for comp in comparisons:
        log.step(f"DETAIL: {comp.name}")
        opt = next(o for o in instance.options if o.name == comp.name)
        if "refinance" in comp.name.lower():
            log.metric("Phase A rate:", "6.50% (months 1-60)", tag="DATA")
            log.metric("Phase B rate:", "5.20% (months 61-360)", tag="DATA")
            log.metric("Closing costs:", f"${opt.closing_costs:,.2f}", tag="DATA")
            log.metric("Post-refi PMT:", f"${comp.monthly_payment:,.2f}/mo", tag="RESULT")
        else:
            log.metric("Annual rate:", f"{opt.annual_rate * 100:.1f}%", tag="DATA")
            log.metric("Term:", f"{opt.term_years} years ({opt.n_payments} payments)", tag="DATA")
            log.metric("Monthly payment:", f"${comp.monthly_payment:,.2f}", tag="RESULT")

        log.metric("Total interest:", f"${comp.total_interest:,.2f}", tag="RESULT")
        log.metric("Total paid:", f"${comp.total_paid:,.2f}", tag="RESULT")

        # Show schedule snapshot: first 3, year-5, year-10, year-15, last 3
        log.blank()
        log.table_row(
            f"{'Month':>6} {'Payment':>10} {'Principal':>10} {'Interest':>10} {'Balance':>14}",
            tag="TABLE",
        )
        log.divider()
        n = len(comp.schedule)
        snapshot_months = set()
        snapshot_months.update(range(0, min(3, n)))
        for yr in [5, 10, 15, 20, 25]:
            idx = yr * 12 - 1
            if 0 <= idx < n:
                snapshot_months.add(idx)
        snapshot_months.update(range(max(0, n - 3), n))

        prev_idx = -1
        for idx in sorted(snapshot_months):
            if prev_idx >= 0 and idx - prev_idx > 1:
                log.table_row(f"{'...':>6}", tag="DATA")
            e = comp.schedule[idx]
            log.table_row(
                f"{e.month:>6} ${e.payment:>9,.2f} ${e.principal:>9,.2f} "
                f"${e.interest:>9,.2f} ${e.balance:>13,.2f}",
                tag="TABLE",
            )
            prev_idx = idx
        log.blank()

    # Refinance break-even
    log.step("REFINANCE BREAK-EVEN ANALYSIS")
    log.metric("Original 30yr PMT:", f"${old_monthly:,.2f}/mo", tag="DATA")
    log.metric("Post-refi PMT:", f"${new_monthly:,.2f}/mo", tag="DATA")
    log.metric("Monthly savings:", f"${monthly_savings:,.2f}/mo", tag="RESULT")
    log.metric("Closing costs:", f"${closing_costs:,.2f}", tag="DATA")
    if refinance_breakeven_months is not None:
        years = refinance_breakeven_months // 12
        months = refinance_breakeven_months % 12
        log.metric("Break-even:",
                    f"{refinance_breakeven_months} months ({years}y {months}m after refi)",
                    tag="RESULT")
    else:
        log.warning("Refinancing never breaks even", tag="WARNING")
    log.metric("Net savings (refi vs stay):", f"${refinance_net_savings:,.2f}", tag="RESULT")
    log.blank()

    # Interest savings comparison
    log.step("INTEREST SAVINGS vs 30-YEAR BASELINE")
    baseline_interest = result_1.total_interest
    for comp in comparisons:
        diff = baseline_interest - comp.total_interest
        pct = diff / baseline_interest * 100 if baseline_interest > 0 else 0
        if diff > 0:
            log.metric(f"{comp.name}:", f"saves ${diff:,.2f} ({pct:.1f}%)", tag="RESULT")
        elif diff == 0:
            log.metric(f"{comp.name}:", "baseline", tag="DATA")
        else:
            log.metric(f"{comp.name}:", f"costs ${-diff:,.2f} more ({-pct:.1f}%)", tag="WARNING")
    log.blank()

    # Recommendations
    log.step("RECOMMENDATIONS")
    log.info(f"Lowest total cost: {cheapest.name} at ${cheapest.total_paid:,.2f}", tag="RECOMMEND")
    if result_2.total_paid < result_1.total_paid:
        extra_monthly = result_2.monthly_payment - result_1.monthly_payment
        log.info(
            f"15-year saves ${result_1.total_paid - result_2.total_paid:,.2f} total, "
            f"but costs ${extra_monthly:,.2f}/mo more",
            tag="RECOMMEND",
        )
    if refinance_net_savings > 0:
        log.info(
            f"Refinancing saves ${refinance_net_savings:,.2f} over remaining life "
            f"(break-even in {refinance_breakeven_months} months)",
            tag="RECOMMEND",
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

    log.metric("Algorithm:", sol.algorithm, tag="SOLVE")
    log.metric("Time:", f"{sol.time_seconds:.6f}s", tag="TIMING")
    log.divider(style="thick")

    # Save JSON
    output: dict[str, Any] = {
        "home_price": home_price,
        "down_payment": down_payment,
        "loan_amount": loan_amount,
        "cheapest_option": sol.cheapest_option,
        "refinance_breakeven_months": sol.refinance_breakeven_months,
        "refinance_net_savings": sol.refinance_net_savings,
        "options": [],
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
    }
    for comp in comparisons:
        output["options"].append({
            "name": comp.name,
            "monthly_payment": comp.monthly_payment,
            "total_interest": comp.total_interest,
            "total_paid": comp.total_paid,
        })
    with open(str(Path(__file__).parent / "solution.json"), "w") as f:
        json.dump(output, f, indent=2)
    log.success("solution.json", tag="SAVE")
