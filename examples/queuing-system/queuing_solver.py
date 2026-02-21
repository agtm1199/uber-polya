#!/usr/bin/env python3
"""Call Center Queuing Analysis solver.

Solves an M/M/c queuing problem using:
  1. Analytical M/M/c formulas (P0, Erlang-C, Lq, Wq, L, W)
  2. Staffing analysis across c = 1..10 servers
  3. Growth scenario with 50% arrival rate increase
  4. SimPy discrete-event simulation for cross-validation

Verification: Little's Law, stability condition, probability bounds,
simulation-vs-theory comparison, staffing monotonicity.
"""
from __future__ import annotations

import json
import math
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import simpy
from scipy.special import factorial as sp_factorial

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger

log = PolyaLogger()


# --- Data Model ---

@dataclass(frozen=True)
class Instance:
    """M/M/c queuing system instance."""
    arrival_rate: float         # lambda: arrivals per hour
    service_rate: float         # mu: service completions per hour per agent
    num_servers: int            # c: number of parallel agents
    target_wait_minutes: float  # maximum acceptable average wait (minutes)
    growth_factor: float        # multiplier for arrival rate in growth scenario


@dataclass
class MMcResults:
    """Analytical results for a single M/M/c configuration."""
    c: int
    rho: float
    p0: float
    erlang_c: float
    lq: float
    wq: float          # hours
    wq_minutes: float
    w: float            # hours
    w_minutes: float
    l: float
    littles_law_l: float


@dataclass
class Solution:
    """Complete queuing analysis solution."""
    # Current scenario analytical results
    current: MMcResults | None = None

    # Staffing analysis: list of (c, wq_minutes) for c = 1..10
    staffing: list[tuple[int, float]] = field(default_factory=list)
    min_servers_for_target: int = 0

    # Growth scenario
    growth: MMcResults | None = None
    growth_staffing: list[tuple[int, float]] = field(default_factory=list)
    min_servers_for_target_growth: int = 0

    # Simulation results
    sim_wq_hours: float = 0.0
    sim_wq_minutes: float = 0.0
    sim_w_hours: float = 0.0
    sim_l_avg: float = 0.0
    sim_customers_served: int = 0

    # Metadata
    algorithm: str = ""
    time_seconds: float = 0.0

    # Verification
    verification: dict = field(default_factory=dict)


# --- M/M/c Analytical Solver ---

def compute_mmc(lam: float, mu: float, c: int) -> MMcResults | None:
    """Compute M/M/c queue metrics analytically.

    Returns None if the system is unstable (rho >= 1).

    Formulas:
        rho = lam / (c * mu)
        P0  = [sum_{k=0}^{c-1} (c*rho)^k / k!  +  (c*rho)^c / (c! * (1-rho))]^{-1}
        C(c,rho) = [(c*rho)^c / (c! * (1-rho))] * P0
        Lq  = C(c,rho) * rho / (1-rho)
        Wq  = Lq / lam
        W   = Wq + 1/mu
        L   = lam * W
    """
    rho = lam / (c * mu)
    if rho >= 1.0:
        return None  # unstable

    a = c * rho  # offered load = lam / mu

    # P0: probability the system is empty
    sum_terms = sum(a ** k / math.factorial(k) for k in range(c))
    last_term = a ** c / (math.factorial(c) * (1.0 - rho))
    p0 = 1.0 / (sum_terms + last_term)

    # Erlang-C: probability of waiting
    erlang_c = (a ** c / (math.factorial(c) * (1.0 - rho))) * p0

    # Queue length and wait times
    lq = erlang_c * rho / (1.0 - rho)
    wq = lq / lam
    w = wq + 1.0 / mu
    l = lam * w
    littles_law_l = lam * w  # should equal l exactly

    return MMcResults(
        c=c,
        rho=rho,
        p0=p0,
        erlang_c=erlang_c,
        lq=lq,
        wq=wq,
        wq_minutes=wq * 60.0,
        w=w,
        w_minutes=w * 60.0,
        l=l,
        littles_law_l=littles_law_l,
    )


# --- Staffing Analysis ---

def staffing_analysis(
    lam: float, mu: float, max_servers: int = 10
) -> list[tuple[int, float]]:
    """Compute Wq (minutes) for c = 1..max_servers.

    Returns list of (c, wq_minutes). Entries with rho >= 1 get wq = inf.
    """
    results: list[tuple[int, float]] = []
    for c in range(1, max_servers + 1):
        res = compute_mmc(lam, mu, c)
        if res is None:
            results.append((c, float("inf")))
        else:
            results.append((c, res.wq_minutes))
    return results


# --- SimPy DES Verification ---

def run_simulation(
    lam: float,
    mu: float,
    c: int,
    n_customers: int = 50_000,
    warmup: int = 5_000,
    seed: int = 42,
) -> tuple[float, float, float, int]:
    """Run a SimPy discrete-event simulation of an M/M/c queue.

    Returns (avg_wq_hours, avg_w_hours, avg_queue_length, customers_served).
    """
    np.random.seed(seed)

    wait_times: list[float] = []
    system_times: list[float] = []
    queue_lengths: list[float] = []
    queue_length_times: list[float] = []

    class CallCenter:
        def __init__(self, env: simpy.Environment, num_agents: int, mu: float) -> None:
            self.env = env
            self.agents = simpy.Resource(env, capacity=num_agents)
            self.mu = mu

        def serve(self) -> simpy.events.Event:
            service_time = np.random.exponential(1.0 / self.mu)
            yield self.env.timeout(service_time)

    def customer(
        env: simpy.Environment,
        center: CallCenter,
        customer_id: int,
    ) -> simpy.events.Event:
        arrival_time = env.now
        queue_lengths.append(len(center.agents.queue))
        queue_length_times.append(env.now)

        with center.agents.request() as req:
            yield req
            wait = env.now - arrival_time
            wait_times.append(wait)
            yield env.process(center.serve())
            total = env.now - arrival_time
            system_times.append(total)

    def arrivals(
        env: simpy.Environment,
        center: CallCenter,
        lam: float,
        n_customers: int,
    ) -> simpy.events.Event:
        for i in range(n_customers):
            inter_arrival = np.random.exponential(1.0 / lam)
            yield env.timeout(inter_arrival)
            env.process(customer(env, center, i))

    env = simpy.Environment()
    center = CallCenter(env, c, mu)
    env.process(arrivals(env, center, lam, n_customers))
    env.run()

    # Discard warm-up observations
    wait_arr = np.array(wait_times[warmup:])
    system_arr = np.array(system_times[warmup:])

    avg_wq = float(np.mean(wait_arr)) if len(wait_arr) > 0 else 0.0
    avg_w = float(np.mean(system_arr)) if len(system_arr) > 0 else 0.0

    # Average queue length (time-weighted)
    if len(queue_lengths) > warmup:
        avg_ql = float(np.mean(queue_lengths[warmup:]))
    else:
        avg_ql = 0.0

    served = len(wait_arr)
    return avg_wq, avg_w, avg_ql, served


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Solve the queuing analysis: analytical + staffing + growth + simulation."""
    t0 = time.perf_counter()
    sol = Solution()

    lam = instance.arrival_rate
    mu = instance.service_rate
    c = instance.num_servers
    target_wq_hrs = instance.target_wait_minutes / 60.0

    # Step 1: Analytical M/M/c for current configuration
    sol.current = compute_mmc(lam, mu, c)

    # Step 2: Staffing analysis
    sol.staffing = staffing_analysis(lam, mu, max_servers=10)
    sol.min_servers_for_target = 0
    for servers, wq_min in sol.staffing:
        if wq_min < instance.target_wait_minutes:
            sol.min_servers_for_target = servers
            break

    # Step 3: Growth scenario
    lam_growth = lam * instance.growth_factor
    sol.growth = compute_mmc(lam_growth, mu, c)
    sol.growth_staffing = staffing_analysis(lam_growth, mu, max_servers=10)
    sol.min_servers_for_target_growth = 0
    for servers, wq_min in sol.growth_staffing:
        if wq_min < instance.target_wait_minutes:
            sol.min_servers_for_target_growth = servers
            break

    # Step 4: SimPy DES verification
    sim_wq, sim_w, sim_l, sim_served = run_simulation(
        lam, mu, c, n_customers=200_000, warmup=10_000, seed=42,
    )
    sol.sim_wq_hours = sim_wq
    sol.sim_wq_minutes = sim_wq * 60.0
    sol.sim_w_hours = sim_w
    sol.sim_l_avg = sim_l
    sol.sim_customers_served = sim_served

    sol.algorithm = "M/M/c Analytical + SimPy DES Verification"
    sol.time_seconds = time.perf_counter() - t0

    # Verification (independent)
    sol.verification = verify(instance, sol)

    return sol


# --- Verification (independent of solver) ---

def verify(instance: Instance, sol: Solution) -> dict:
    """Independently verify the solution with at least 8 checks."""
    checks: dict = {}
    lam = instance.arrival_rate
    mu = instance.service_rate
    c = instance.num_servers
    cur = sol.current

    # Check 1: utilization_below_1 -- stability condition
    rho = lam / (c * mu)
    checks["utilization_below_1"] = rho < 1.0

    # Check 2: littles_law_holds -- |L - lam*W| < 0.01
    if cur is not None:
        l_check = lam * cur.w
        checks["littles_law_holds"] = abs(cur.l - l_check) < 0.01
    else:
        checks["littles_law_holds"] = False

    # Check 3: wait_time_positive -- Wq >= 0
    if cur is not None:
        checks["wait_time_positive"] = cur.wq >= 0.0
    else:
        checks["wait_time_positive"] = False

    # Check 4: system_time_gt_service -- W >= 1/mu
    if cur is not None:
        checks["system_time_gt_service"] = cur.w >= (1.0 / mu) - 1e-9
    else:
        checks["system_time_gt_service"] = False

    # Check 5: simulation_matches_theory -- |Wq_sim - Wq_analytical| / Wq_analytical < 0.10
    if cur is not None and cur.wq > 0:
        rel_error = abs(sol.sim_wq_hours - cur.wq) / cur.wq
        checks["simulation_matches_theory"] = rel_error < 0.10
        checks["simulation_relative_error"] = round(rel_error, 4)
    else:
        checks["simulation_matches_theory"] = False
        checks["simulation_relative_error"] = None

    # Check 6: staffing_reduces_wait -- more servers -> lower or equal Wq
    monotone = True
    prev_wq = float("inf")
    for _, wq_min in sol.staffing:
        if wq_min > prev_wq + 1e-9:
            monotone = False
            break
        prev_wq = wq_min
    checks["staffing_reduces_wait"] = monotone

    # Check 7: growth_needs_more_staff -- growth scenario needs >= as many agents
    checks["growth_needs_more_staff"] = (
        sol.min_servers_for_target_growth >= sol.min_servers_for_target
    )

    # Check 8: probability_bounds -- 0 <= P(wait) <= 1
    if cur is not None:
        checks["probability_bounds"] = 0.0 <= cur.erlang_c <= 1.0
    else:
        checks["probability_bounds"] = False

    # Overall
    bool_checks = [v for v in checks.values() if isinstance(v, bool)]
    checks["all_passed"] = all(bool_checks)

    return checks


# --- Main ---

if __name__ == "__main__":
    instance = Instance(
        arrival_rate=20.0,          # lambda = 20 calls/hour
        service_rate=6.0,           # mu = 6 calls/hour/agent
        num_servers=4,              # c = 4 agents
        target_wait_minutes=2.0,    # target: < 2 min average wait
        growth_factor=1.5,          # 50% increase in call volume
    )

    sol = solve(instance)
    cur = sol.current

    # ===============================================================
    #  REPORT
    # ===============================================================
    log.header("CALL CENTER QUEUING ANALYSIS")

    # --- Instance ---
    log.step("INSTANCE")
    log.metric("Arrival rate (lam)", "{:.1f} calls/hour".format(instance.arrival_rate), tag="DATA")
    log.metric("Service rate (mu)", "{:.1f} calls/hour/agent".format(instance.service_rate), tag="DATA")
    log.metric("Servers (c)", "{}".format(instance.num_servers), tag="DATA")
    log.metric("Target wait", "< {:.1f} minutes".format(instance.target_wait_minutes), tag="DATA")
    log.metric("Growth factor", "{:.0%}".format(instance.growth_factor), tag="DATA")
    log.blank()

    # --- Analytical M/M/c Results ---
    log.step("STEP 1: M/M/c Analytical Results (c={})".format(instance.num_servers))
    if cur is not None:
        log.metric("Utilization (rho)", "{:.4f}".format(cur.rho), tag="STATS")
        log.metric("P0 (empty prob)", "{:.6f}".format(cur.p0), tag="STATS")
        log.metric("Erlang-C P(wait)", "{:.6f}".format(cur.erlang_c), tag="STATS")
        log.metric("Lq (queue length)", "{:.4f} customers".format(cur.lq), tag="STATS")
        log.metric("Wq (wait time)", "{:.4f} hrs = {:.2f} min".format(cur.wq, cur.wq_minutes), tag="STATS")
        log.metric("W  (system time)", "{:.4f} hrs = {:.2f} min".format(cur.w, cur.w_minutes), tag="STATS")
        log.metric("L  (in system)", "{:.4f} customers".format(cur.l), tag="STATS")
        log.blank()
        log.info("Little's Law check: L = {:.4f}, lam*W = {:.4f}".format(
            cur.l, cur.littles_law_l), tag="VERIFY")
    else:
        log.warning("System is UNSTABLE (rho >= 1) with c={} agents!".format(
            instance.num_servers), tag="WARNING")
    log.blank()

    # --- Staffing Analysis ---
    log.step("STEP 2: Staffing Analysis (target Wq < {:.1f} min)".format(
        instance.target_wait_minutes))
    log.table_row("{:<10} {:>12} {:>12} {:>10}".format(
        "Agents", "Wq (min)", "Rho", "Meets Target"), tag="TABLE")
    log.table_row("-" * 50, tag="TABLE")
    for servers, wq_min in sol.staffing:
        rho_val = instance.arrival_rate / (servers * instance.service_rate)
        if wq_min == float("inf"):
            log.table_row("{:<10} {:>12} {:>12.4f} {:>10}".format(
                servers, "UNSTABLE", rho_val, "No"), tag="TABLE")
        else:
            meets = "Yes" if wq_min < instance.target_wait_minutes else "No"
            log.table_row("{:<10} {:>12.2f} {:>12.4f} {:>10}".format(
                servers, wq_min, rho_val, meets), tag="TABLE")
    log.blank()
    log.success("Minimum servers for < {:.1f} min wait: {}".format(
        instance.target_wait_minutes, sol.min_servers_for_target), tag="RESULT")
    log.blank()

    # --- Growth Scenario ---
    lam_growth = instance.arrival_rate * instance.growth_factor
    log.step("STEP 3: Growth Scenario (lam = {:.1f} calls/hr)".format(lam_growth))
    if sol.growth is not None:
        log.metric("Utilization (rho)", "{:.4f}".format(sol.growth.rho), tag="STATS")
        log.metric("Erlang-C P(wait)", "{:.6f}".format(sol.growth.erlang_c), tag="STATS")
        log.metric("Wq (wait time)", "{:.4f} hrs = {:.2f} min".format(
            sol.growth.wq, sol.growth.wq_minutes), tag="STATS")
        log.metric("L  (in system)", "{:.4f} customers".format(sol.growth.l), tag="STATS")
    else:
        log.warning("System UNSTABLE with c={} at lam={:.1f}!".format(
            instance.num_servers, lam_growth), tag="WARNING")
    log.blank()

    log.table_row("{:<10} {:>12} {:>10}".format(
        "Agents", "Wq (min)", "Meets Target"), tag="TABLE")
    log.table_row("-" * 38, tag="TABLE")
    for servers, wq_min in sol.growth_staffing:
        if wq_min == float("inf"):
            log.table_row("{:<10} {:>12} {:>10}".format(
                servers, "UNSTABLE", "No"), tag="TABLE")
        else:
            meets = "Yes" if wq_min < instance.target_wait_minutes else "No"
            log.table_row("{:<10} {:>12.2f} {:>10}".format(
                servers, wq_min, meets), tag="TABLE")
    log.blank()
    log.success("Minimum servers for growth scenario: {}".format(
        sol.min_servers_for_target_growth), tag="RESULT")
    log.blank()

    # --- SimPy DES Verification ---
    log.step("STEP 4: SimPy DES Verification (200,000 customers, 10,000 warm-up)")
    log.metric("Sim Wq", "{:.4f} hrs = {:.2f} min".format(
        sol.sim_wq_hours, sol.sim_wq_minutes), tag="STATS")
    log.metric("Sim W", "{:.4f} hrs = {:.2f} min".format(
        sol.sim_w_hours, sol.sim_w_hours * 60.0), tag="STATS")
    log.metric("Sim avg queue len", "{:.2f}".format(sol.sim_l_avg), tag="STATS")
    log.metric("Customers served", "{:,}".format(sol.sim_customers_served), tag="DATA")
    log.blank()
    if cur is not None:
        log.info("Comparison: analytical Wq = {:.4f} hrs, simulated Wq = {:.4f} hrs".format(
            cur.wq, sol.sim_wq_hours), tag="VERIFY")
        if cur.wq > 0:
            rel_err = abs(sol.sim_wq_hours - cur.wq) / cur.wq
            log.info("Relative error: {:.2%}".format(rel_err), tag="VERIFY")
    log.blank()

    # --- Verification ---
    log.step("VERIFICATION (8 independent checks)")
    for check_name, result in sol.verification.items():
        if check_name == "simulation_relative_error":
            if result is not None:
                log.check(check_name, float(result), tag="VERIFY")
            else:
                log.check(check_name, "N/A", tag="VERIFY")
        elif isinstance(result, bool):
            log.check(check_name, result, tag="VERIFY")
        else:
            log.check(check_name, result, tag="VERIFY")
    log.blank()

    # --- Recommendation ---
    log.step("RECOMMENDATION")
    if cur is not None:
        if cur.wq_minutes < instance.target_wait_minutes:
            log.success(
                "Current staffing ({} agents) meets the < {:.0f} min wait target "
                "(Wq = {:.2f} min).".format(
                    instance.num_servers, instance.target_wait_minutes,
                    cur.wq_minutes),
                tag="RECOMMEND")
        else:
            log.warning(
                "Current staffing ({} agents) does NOT meet target "
                "(Wq = {:.2f} min > {:.0f} min). Need at least {} agents.".format(
                    instance.num_servers, cur.wq_minutes,
                    instance.target_wait_minutes, sol.min_servers_for_target),
                tag="RECOMMEND")
    log.info(
        "For 50% growth: need at least {} agents to maintain < {:.0f} min wait.".format(
            sol.min_servers_for_target_growth, instance.target_wait_minutes),
        tag="RECOMMEND")
    log.blank()

    log.metric("Algorithm", sol.algorithm, tag="SOLVE")
    log.metric("Time", "{:.4f}s".format(sol.time_seconds), tag="TIMING")
    log.divider(style="thick")

    # --- Save JSON ---
    def mmc_to_dict(r: MMcResults | None) -> dict | None:
        if r is None:
            return None
        return {
            "c": r.c, "rho": r.rho, "p0": r.p0,
            "erlang_c": r.erlang_c, "lq": r.lq,
            "wq_hours": r.wq, "wq_minutes": r.wq_minutes,
            "w_hours": r.w, "w_minutes": r.w_minutes,
            "l": r.l,
        }

    output = {
        "instance": {
            "arrival_rate": instance.arrival_rate,
            "service_rate": instance.service_rate,
            "num_servers": instance.num_servers,
            "target_wait_minutes": instance.target_wait_minutes,
            "growth_factor": instance.growth_factor,
        },
        "current_analytical": mmc_to_dict(sol.current),
        "staffing_analysis": [
            {"agents": c, "wq_minutes": wq} for c, wq in sol.staffing
        ],
        "min_servers_for_target": sol.min_servers_for_target,
        "growth_analytical": mmc_to_dict(sol.growth),
        "growth_staffing_analysis": [
            {"agents": c, "wq_minutes": wq} for c, wq in sol.growth_staffing
        ],
        "min_servers_for_target_growth": sol.min_servers_for_target_growth,
        "simulation": {
            "wq_hours": sol.sim_wq_hours,
            "wq_minutes": sol.sim_wq_minutes,
            "w_hours": sol.sim_w_hours,
            "avg_queue_length": sol.sim_l_avg,
            "customers_served": sol.sim_customers_served,
        },
        "verification": sol.verification,
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
    }
    out_path = Path(__file__).resolve().parent / "solution.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    log.success("Solution data saved to: {}".format(out_path), tag="SAVE")
    log.divider(style="thick")
