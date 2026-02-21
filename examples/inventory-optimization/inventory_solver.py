#!/usr/bin/env python3
"""Inventory optimization solver.

Solves three classical inventory problems:
  1. Economic Order Quantity (EOQ) -- deterministic demand
  2. Reorder Point with safety stock -- stochastic lead-time demand
  3. Newsvendor model -- single-period perishable goods

Verification: independent formula checks + Monte Carlo simulation.
"""
from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass, field

import numpy as np
from scipy import stats

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger
log = PolyaLogger()


# --- Data Model ---

@dataclass(frozen=True)
class Instance:
    """Inventory optimization instance."""
    demand_rate: float          # annual demand (units/year)
    order_cost: float           # fixed cost per order ($)
    holding_cost: float         # holding cost per unit per year ($/unit/year)
    lead_time_weeks: float      # deterministic lead time (weeks)
    weekly_demand_mean: float   # mean weekly demand (units)
    weekly_demand_std: float    # std dev of weekly demand (units)
    service_level: float        # target cycle service level (probability)
    unit_cost: float            # purchase cost per unit for newsvendor ($)
    selling_price: float        # selling price per unit for newsvendor ($)
    salvage_value: float        # salvage value per unsold unit for newsvendor ($)


@dataclass
class Solution:
    """Verified inventory optimization solution."""
    # EOQ results
    eoq: float
    eoq_total_cost: float
    eoq_ordering_cost: float
    eoq_holding_cost: float
    orders_per_year: float
    cycle_time_days: float

    # Reorder point results
    reorder_point: float
    safety_stock: float
    z_score: float
    mean_demand_during_lt: float
    std_demand_during_lt: float

    # Newsvendor results
    critical_ratio: float
    newsvendor_q: float
    newsvendor_expected_profit: float
    newsvendor_expected_leftover: float
    newsvendor_expected_shortage: float

    # Sensitivity analysis
    sensitivity: dict = field(default_factory=dict)

    # Monte Carlo simulation
    simulation: dict = field(default_factory=dict)

    # Verification
    verification: dict = field(default_factory=dict)

    # Metadata
    algorithm: str = ""
    time_seconds: float = 0.0


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Solve EOQ + reorder point + newsvendor with sensitivity and simulation."""
    t0 = time.perf_counter()

    # --- 1. EOQ ---
    D = instance.demand_rate
    K = instance.order_cost
    h = instance.holding_cost

    eoq = math.sqrt(2 * D * K / h)
    eoq_ordering_cost = D / eoq * K
    eoq_holding_cost = eoq / 2 * h
    eoq_total_cost = eoq_ordering_cost + eoq_holding_cost
    orders_per_year = D / eoq
    cycle_time_days = 365.0 / orders_per_year

    # --- 2. Reorder Point & Safety Stock ---
    lt = instance.lead_time_weeks
    mu_weekly = instance.weekly_demand_mean
    sigma_weekly = instance.weekly_demand_std

    mean_demand_during_lt = mu_weekly * lt
    std_demand_during_lt = sigma_weekly * math.sqrt(lt)

    z_score = stats.norm.ppf(instance.service_level)
    safety_stock = z_score * std_demand_during_lt
    reorder_point = mean_demand_during_lt + safety_stock

    # --- 3. Newsvendor ---
    Cu = instance.selling_price - instance.unit_cost   # cost of underage
    Co = instance.unit_cost - instance.salvage_value    # cost of overage
    critical_ratio = Cu / (Cu + Co)

    # Demand during the single period is weekly demand (Normal approximation)
    newsvendor_q = stats.norm.ppf(critical_ratio,
                                  loc=mu_weekly,
                                  scale=sigma_weekly)

    # Expected profit, leftover, shortage via integration
    mu = mu_weekly
    sigma = sigma_weekly
    z_nv = (newsvendor_q - mu) / sigma

    # E[leftover] = E[max(Q - D, 0)]
    expected_leftover = (newsvendor_q - mu) * stats.norm.cdf(z_nv) + \
                        sigma * stats.norm.pdf(z_nv)

    # E[shortage] = E[max(D - Q, 0)]
    expected_shortage = (mu - newsvendor_q) * (1 - stats.norm.cdf(z_nv)) + \
                        sigma * stats.norm.pdf(z_nv)

    # Expected profit = Cu * E[min(Q,D)] - Co * E[leftover]
    # E[sales] = mu - E[shortage] = Q - E[leftover]
    expected_sales = newsvendor_q - expected_leftover
    newsvendor_expected_profit = (instance.selling_price * expected_sales
                                  - instance.unit_cost * newsvendor_q
                                  + instance.salvage_value * expected_leftover)

    elapsed = time.perf_counter() - t0

    sol = Solution(
        eoq=eoq,
        eoq_total_cost=eoq_total_cost,
        eoq_ordering_cost=eoq_ordering_cost,
        eoq_holding_cost=eoq_holding_cost,
        orders_per_year=orders_per_year,
        cycle_time_days=cycle_time_days,
        reorder_point=reorder_point,
        safety_stock=safety_stock,
        z_score=z_score,
        mean_demand_during_lt=mean_demand_during_lt,
        std_demand_during_lt=std_demand_during_lt,
        critical_ratio=critical_ratio,
        newsvendor_q=newsvendor_q,
        newsvendor_expected_profit=newsvendor_expected_profit,
        newsvendor_expected_leftover=expected_leftover,
        newsvendor_expected_shortage=expected_shortage,
        algorithm="EOQ + (s,Q) reorder point + Newsvendor",
    )

    # Sensitivity analysis
    sol.sensitivity = sensitivity_analysis(instance)

    # Monte Carlo simulation
    sol.simulation = monte_carlo_simulation(instance, eoq, reorder_point)

    # Independent verification
    sol.verification = verify(instance, sol)

    sol.time_seconds = time.perf_counter() - t0
    return sol


# --- Sensitivity Analysis ---

def sensitivity_analysis(instance: Instance) -> dict:
    """Vary key parameters and observe how EOQ, total cost, and safety stock change."""
    D = instance.demand_rate
    K = instance.order_cost
    h = instance.holding_cost
    results: dict = {}

    # --- Demand variation: +/- 20% ---
    demand_sensitivity = []
    for factor in [0.80, 0.90, 1.00, 1.10, 1.20]:
        d = D * factor
        q = math.sqrt(2 * d * K / h)
        tc = 2 * math.sqrt(d * K * h / 2)  # = sqrt(2*D*K*h)
        demand_sensitivity.append({
            "demand": d,
            "eoq": round(q, 1),
            "total_cost": round(tc, 2),
        })
    results["demand_variation"] = demand_sensitivity

    # --- Holding cost variation: +/- 50% ---
    holding_sensitivity = []
    for factor in [0.50, 0.75, 1.00, 1.25, 1.50]:
        hc = h * factor
        q = math.sqrt(2 * D * K / hc)
        tc = math.sqrt(2 * D * K * hc)
        holding_sensitivity.append({
            "holding_cost": hc,
            "eoq": round(q, 1),
            "total_cost": round(tc, 2),
        })
    results["holding_cost_variation"] = holding_sensitivity

    # --- Order cost variation: +/- 50% ---
    order_sensitivity = []
    for factor in [0.50, 0.75, 1.00, 1.25, 1.50]:
        oc = K * factor
        q = math.sqrt(2 * D * oc / h)
        tc = math.sqrt(2 * D * oc * h)
        order_sensitivity.append({
            "order_cost": oc,
            "eoq": round(q, 1),
            "total_cost": round(tc, 2),
        })
    results["order_cost_variation"] = order_sensitivity

    # --- Service level variation: 0.85 to 0.99 ---
    sigma_lt = instance.weekly_demand_std * math.sqrt(instance.lead_time_weeks)
    service_sensitivity = []
    for sl in [0.85, 0.90, 0.93, 0.95, 0.97, 0.99]:
        z = stats.norm.ppf(sl)
        ss = z * sigma_lt
        service_sensitivity.append({
            "service_level": sl,
            "z_score": round(z, 3),
            "safety_stock": round(ss, 1),
        })
    results["service_level_variation"] = service_sensitivity

    return results


# --- Monte Carlo Simulation ---

def monte_carlo_simulation(instance: Instance, eoq: float,
                           reorder_point: float,
                           n_cycles: int = 10_000) -> dict:
    """Simulate (Q, ROP) inventory policy over many order cycles.

    Each cycle:
      1. Start with inventory = Q + safety_stock (just received an order).
      2. Demand during lead time is drawn from Normal(mu_LT, sigma_LT).
      3. If demand <= inventory at reorder point trigger, no stockout.
      4. Track fill rate as fraction of cycles without stockout.
    """
    np.random.seed(42)

    mu_lt = instance.weekly_demand_mean * instance.lead_time_weeks
    sigma_lt = instance.weekly_demand_std * math.sqrt(instance.lead_time_weeks)

    # Simulate demand during lead time for each cycle
    demands_during_lt = np.random.normal(mu_lt, sigma_lt, n_cycles)
    demands_during_lt = np.maximum(demands_during_lt, 0)  # demand cannot be negative

    # In a (Q, ROP) policy, a reorder is triggered when inventory hits ROP.
    # The inventory on hand when the order arrives is approximately:
    # ROP - demand_during_lead_time.  Stockout if demand_during_lt > ROP.
    stockouts = demands_during_lt > reorder_point
    fill_rate = 1.0 - np.mean(stockouts)

    # Also simulate newsvendor single-period outcomes
    nv_demands = np.random.normal(instance.weekly_demand_mean,
                                  instance.weekly_demand_std,
                                  n_cycles)
    nv_demands = np.maximum(nv_demands, 0)

    Cu = instance.selling_price - instance.unit_cost
    Co = instance.unit_cost - instance.salvage_value
    cr = Cu / (Cu + Co)
    nv_q = stats.norm.ppf(cr, loc=instance.weekly_demand_mean,
                          scale=instance.weekly_demand_std)

    nv_sales = np.minimum(nv_q, nv_demands)
    nv_leftover = np.maximum(nv_q - nv_demands, 0)
    nv_profit = (instance.selling_price * nv_sales
                 - instance.unit_cost * nv_q
                 + instance.salvage_value * nv_leftover)

    return {
        "n_cycles": n_cycles,
        "simulated_fill_rate": float(fill_rate),
        "target_service_level": instance.service_level,
        "fill_rate_error": float(abs(fill_rate - instance.service_level)),
        "simulated_nv_mean_profit": float(np.mean(nv_profit)),
        "simulated_nv_std_profit": float(np.std(nv_profit)),
    }


# --- Verification (independent of solver) ---

def verify(instance: Instance, sol: Solution) -> dict:
    """Independently verify solution with at least 8 checks."""
    checks: dict = {}

    D = instance.demand_rate
    K = instance.order_cost
    h = instance.holding_cost

    # Check 1: EOQ is positive
    checks["eoq_positive"] = sol.eoq > 0

    # Check 2: EOQ formula is correct
    expected_eoq = math.sqrt(2 * D * K / h)
    checks["eoq_formula_correct"] = abs(sol.eoq - expected_eoq) < 0.01

    # Check 3: At EOQ, ordering cost approximately equals holding cost
    checks["total_cost_at_eoq"] = abs(sol.eoq_ordering_cost - sol.eoq_holding_cost) < 0.01

    # Check 4: ROP > mean demand during lead time
    checks["rop_gt_mean_demand"] = bool(sol.reorder_point > sol.mean_demand_during_lt)

    # Check 5: Safety stock is positive
    checks["safety_stock_positive"] = bool(sol.safety_stock > 0)

    # Check 6: Newsvendor Q is in plausible range
    checks["newsvendor_in_range"] = bool(100 < sol.newsvendor_q < 500)

    # Check 7: Critical ratio formula is correct
    Cu = instance.selling_price - instance.unit_cost
    Co = instance.unit_cost - instance.salvage_value
    expected_cr = Cu / (Cu + Co)
    checks["critical_ratio_correct"] = abs(sol.critical_ratio - expected_cr) < 1e-10

    # Check 8: Simulated fill rate is within 3% of target service level
    sim_fill = sol.simulation.get("simulated_fill_rate", 0.0)
    checks["simulation_service_level"] = abs(sim_fill - instance.service_level) < 0.03

    # Overall
    checks["all_passed"] = all(
        v for k, v in checks.items() if k != "all_passed" and isinstance(v, bool)
    )

    return checks


# --- Main ---

if __name__ == "__main__":
    instance = Instance(
        demand_rate=10_000,
        order_cost=50.0,
        holding_cost=2.0,
        lead_time_weeks=1.0,
        weekly_demand_mean=192.0,
        weekly_demand_std=40.0,
        service_level=0.95,
        unit_cost=10.0,
        selling_price=25.0,
        salvage_value=3.0,
    )

    sol = solve(instance)

    # --- Print Solution Report ---
    log.header("INVENTORY OPTIMIZATION SOLUTION REPORT")

    log.step("INSTANCE")
    log.metric("Demand rate", "{:,.0f} units/year".format(instance.demand_rate), tag="DATA")
    log.metric("Order cost", "${:.2f}/order".format(instance.order_cost), tag="DATA")
    log.metric("Holding cost", "${:.2f}/unit/year".format(instance.holding_cost), tag="DATA")
    log.metric("Lead time", "{:.0f} week(s)".format(instance.lead_time_weeks), tag="DATA")
    log.metric("Weekly demand", "mean={:.0f}, std={:.0f}".format(
        instance.weekly_demand_mean, instance.weekly_demand_std), tag="DATA")
    log.metric("Service level", "{:.0%}".format(instance.service_level), tag="DATA")
    log.metric("Newsvendor costs", "cost=${:.0f}, price=${:.0f}, salvage=${:.0f}".format(
        instance.unit_cost, instance.selling_price, instance.salvage_value), tag="DATA")
    log.blank()

    log.step("EOQ ANALYSIS")
    log.metric("EOQ (Q*)", "{:.1f} units".format(sol.eoq), tag="RESULT")
    log.metric("Total cost", "${:,.2f}/year".format(sol.eoq_total_cost), tag="RESULT")
    log.metric("Ordering cost", "${:,.2f}/year".format(sol.eoq_ordering_cost), tag="STATS")
    log.metric("Holding cost", "${:,.2f}/year".format(sol.eoq_holding_cost), tag="STATS")
    log.metric("Orders/year", "{:.1f}".format(sol.orders_per_year), tag="STATS")
    log.metric("Cycle time", "{:.1f} days".format(sol.cycle_time_days), tag="STATS")
    log.blank()

    log.step("REORDER POINT & SAFETY STOCK")
    log.metric("Z-score", "{:.4f} (for {:.0%} SL)".format(
        sol.z_score, instance.service_level), tag="STATS")
    log.metric("Mean demand (LT)", "{:.1f} units".format(sol.mean_demand_during_lt), tag="STATS")
    log.metric("Std demand (LT)", "{:.1f} units".format(sol.std_demand_during_lt), tag="STATS")
    log.metric("Safety stock", "{:.1f} units".format(sol.safety_stock), tag="RESULT")
    log.metric("Reorder point", "{:.1f} units".format(sol.reorder_point), tag="RESULT")
    log.blank()

    log.step("NEWSVENDOR MODEL")
    log.metric("Cu (underage)", "${:.2f}".format(
        instance.selling_price - instance.unit_cost), tag="STATS")
    log.metric("Co (overage)", "${:.2f}".format(
        instance.unit_cost - instance.salvage_value), tag="STATS")
    log.metric("Critical ratio", "{:.4f}".format(sol.critical_ratio), tag="RESULT")
    log.metric("Optimal Q", "{:.1f} units".format(sol.newsvendor_q), tag="RESULT")
    log.metric("Expected profit", "${:,.2f}".format(sol.newsvendor_expected_profit), tag="RESULT")
    log.metric("Expected leftover", "{:.1f} units".format(sol.newsvendor_expected_leftover), tag="STATS")
    log.metric("Expected shortage", "{:.1f} units".format(sol.newsvendor_expected_shortage), tag="STATS")
    log.blank()

    log.step("SENSITIVITY ANALYSIS -- EOQ vs Demand")
    for entry in sol.sensitivity["demand_variation"]:
        pct = entry["demand"] / instance.demand_rate
        log.metric("D={:,.0f}".format(entry["demand"]),
                   "EOQ={:.1f}, TC=${:,.2f}".format(entry["eoq"], entry["total_cost"]),
                   tag="SENSITIVITY")
    log.blank()

    log.step("SENSITIVITY ANALYSIS -- EOQ vs Holding Cost")
    for entry in sol.sensitivity["holding_cost_variation"]:
        log.metric("h=${:.2f}".format(entry["holding_cost"]),
                   "EOQ={:.1f}, TC=${:,.2f}".format(entry["eoq"], entry["total_cost"]),
                   tag="SENSITIVITY")
    log.blank()

    log.step("SENSITIVITY ANALYSIS -- EOQ vs Order Cost")
    for entry in sol.sensitivity["order_cost_variation"]:
        log.metric("K=${:.2f}".format(entry["order_cost"]),
                   "EOQ={:.1f}, TC=${:,.2f}".format(entry["eoq"], entry["total_cost"]),
                   tag="SENSITIVITY")
    log.blank()

    log.step("SENSITIVITY ANALYSIS -- Safety Stock vs Service Level")
    for entry in sol.sensitivity["service_level_variation"]:
        log.bar("SL={:.0%}:".format(entry["service_level"]),
                entry["service_level"],
                tag="POWER",
                marker="  SS={:.1f}".format(entry["safety_stock"]))
    log.blank()

    log.step("MONTE CARLO SIMULATION (10,000 cycles)")
    log.metric("Simulated fill rate", "{:.2%}".format(
        sol.simulation["simulated_fill_rate"]), tag="TEST")
    log.metric("Target service level", "{:.2%}".format(
        sol.simulation["target_service_level"]), tag="TEST")
    log.metric("Fill rate error", "{:.4f}".format(
        sol.simulation["fill_rate_error"]), tag="TEST")
    log.metric("NV mean profit", "${:,.2f}".format(
        sol.simulation["simulated_nv_mean_profit"]), tag="TEST")
    log.metric("NV profit std", "${:,.2f}".format(
        sol.simulation["simulated_nv_std_profit"]), tag="TEST")
    log.blank()

    log.step("VERIFICATION")
    for check_name, result in sol.verification.items():
        if isinstance(result, bool):
            log.check(check_name, result, tag="VERIFY")
        else:
            log.check(check_name, float(result), tag="VERIFY")
    log.blank()

    log.metric("Algorithm", sol.algorithm, tag="SOLVE")
    log.metric("Time", "{:.4f}s".format(sol.time_seconds), tag="TIMING")
    log.blank()

    # Output JSON
    output = {
        "instance": {
            "demand_rate": instance.demand_rate,
            "order_cost": instance.order_cost,
            "holding_cost": instance.holding_cost,
            "lead_time_weeks": instance.lead_time_weeks,
            "weekly_demand_mean": instance.weekly_demand_mean,
            "weekly_demand_std": instance.weekly_demand_std,
            "service_level": instance.service_level,
            "unit_cost": instance.unit_cost,
            "selling_price": instance.selling_price,
            "salvage_value": instance.salvage_value,
        },
        "eoq": {
            "quantity": sol.eoq,
            "total_cost": sol.eoq_total_cost,
            "ordering_cost": sol.eoq_ordering_cost,
            "holding_cost": sol.eoq_holding_cost,
            "orders_per_year": sol.orders_per_year,
            "cycle_time_days": sol.cycle_time_days,
        },
        "reorder_point": {
            "rop": sol.reorder_point,
            "safety_stock": sol.safety_stock,
            "z_score": sol.z_score,
            "mean_demand_lt": sol.mean_demand_during_lt,
            "std_demand_lt": sol.std_demand_during_lt,
        },
        "newsvendor": {
            "critical_ratio": sol.critical_ratio,
            "optimal_q": sol.newsvendor_q,
            "expected_profit": sol.newsvendor_expected_profit,
            "expected_leftover": sol.newsvendor_expected_leftover,
            "expected_shortage": sol.newsvendor_expected_shortage,
        },
        "sensitivity": sol.sensitivity,
        "simulation": sol.simulation,
        "verification": sol.verification,
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
    }

    out_path = Path(__file__).resolve().parent / "solution.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    log.success("Solution data saved to: {}".format(out_path), tag="SAVE")
    log.divider(style="thick")
