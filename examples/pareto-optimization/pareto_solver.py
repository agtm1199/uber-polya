#!/usr/bin/env python3
"""Multi-objective Pareto optimization for product design trade-offs.

Uses the epsilon-constraint method to trace the Pareto frontier between
cost and durability for a 3-variable product design problem.  Identifies
the knee point (maximum curvature), computes utopia/nadir points, and
reports trade-off rates along the frontier.

Complexity: O(n_eps * T_nlp) where n_eps is the number of epsilon samples
            and T_nlp is the cost of one nonlinear program (scipy L-BFGS-B).
Correctness: Each point is a local optimum of a constrained sub-problem;
             Pareto filtering removes any dominated solutions.
"""
from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger

log = PolyaLogger()


# ---------------------------------------------------------------------------
# Data Model
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Instance:
    """Multi-objective optimization instance.

    Attributes:
        bounds: Sequence of (lo, hi) for each design variable.
        n_pareto: Number of epsilon levels used to trace the frontier.
    """
    bounds: tuple[tuple[float, float], ...]
    n_pareto: int

    @property
    def n_vars(self) -> int:
        return len(self.bounds)


@dataclass
class ParetoPoint:
    """A single point on (or near) the Pareto frontier."""
    x: np.ndarray        # design variables
    cost: float          # f1 value
    inv_durability: float  # f2 value (lower = more durable)


@dataclass
class Solution:
    """Verified multi-objective solution with metadata."""
    pareto_points: list[ParetoPoint]
    weighted_points: list[ParetoPoint]
    knee_point: ParetoPoint
    knee_index: int
    utopia: tuple[float, float]       # (best_cost, best_inv_dur)
    nadir: tuple[float, float]        # (worst_cost_on_front, worst_inv_dur_on_front)
    tradeoff_rates: list[float]       # marginal rates of substitution
    is_verified: bool
    algorithm: str
    time_seconds: float
    verification_checks: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Objective functions
# ---------------------------------------------------------------------------

def cost_function(x: np.ndarray) -> float:
    """Product cost as a function of design variables.

    f1(x) = 2 * thickness + 5 * alloy^2 + 3 * coating
    """
    thickness, alloy, coating = x[0], x[1], x[2]
    return 2.0 * thickness + 5.0 * alloy ** 2 + 3.0 * coating


def inv_durability_function(x: np.ndarray) -> float:
    """Inverse durability (lower is better / more durable).

    f2(x) = -ln(thickness) - 2 * alloy - 1.5 * coating^0.8
    """
    thickness, alloy, coating = x[0], x[1], x[2]
    return -np.log(thickness) - 2.0 * alloy - 1.5 * coating ** 0.8


# ---------------------------------------------------------------------------
# Solver helpers
# ---------------------------------------------------------------------------

def _random_x0(bounds: tuple[tuple[float, float], ...],
               rng: np.random.Generator) -> np.ndarray:
    """Generate a random feasible starting point."""
    return np.array([lo + rng.random() * (hi - lo) for lo, hi in bounds])


def _solve_single_objective(
    objective: Callable[[np.ndarray], float],
    bounds: tuple[tuple[float, float], ...],
    rng: np.random.Generator,
    n_restarts: int = 5,
) -> tuple[np.ndarray, float]:
    """Minimize a single objective with multi-start L-BFGS-B."""
    best_x: np.ndarray | None = None
    best_val = np.inf

    for _ in range(n_restarts):
        x0 = _random_x0(bounds, rng)
        res = minimize(objective, x0, method="L-BFGS-B", bounds=bounds)
        if res.success and res.fun < best_val:
            best_val = res.fun
            best_x = res.x.copy()

    assert best_x is not None, "All optimizer restarts failed"
    return best_x, best_val


def _solve_epsilon_constrained(
    epsilon: float,
    bounds: tuple[tuple[float, float], ...],
    rng: np.random.Generator,
    n_restarts: int = 5,
    penalty_weight: float = 1000.0,
) -> tuple[np.ndarray, float, float] | None:
    """Minimize cost subject to inv_durability <= epsilon.

    Uses a penalty formulation:
        min  cost(x) + penalty_weight * max(0, inv_durability(x) - epsilon)^2

    Returns (x, cost, inv_dur) or None if all restarts fail.
    """

    def penalized(x: np.ndarray) -> float:
        c = cost_function(x)
        d = inv_durability_function(x)
        violation = max(0.0, d - epsilon)
        return c + penalty_weight * violation ** 2

    best_x: np.ndarray | None = None
    best_val = np.inf

    for _ in range(n_restarts):
        x0 = _random_x0(bounds, rng)
        res = minimize(penalized, x0, method="L-BFGS-B", bounds=bounds)
        if res.success and res.fun < best_val:
            best_val = res.fun
            best_x = res.x.copy()

    if best_x is None:
        return None

    c = cost_function(best_x)
    d = inv_durability_function(best_x)

    # Only accept if constraint is approximately satisfied
    if d > epsilon + 0.1:
        return None

    return best_x, c, d


def _solve_weighted_sum(
    w1: float,
    bounds: tuple[tuple[float, float], ...],
    rng: np.random.Generator,
    n_restarts: int = 5,
) -> tuple[np.ndarray, float, float]:
    """Minimize w1 * cost + (1 - w1) * inv_durability."""
    w2 = 1.0 - w1

    def scalarized(x: np.ndarray) -> float:
        return w1 * cost_function(x) + w2 * inv_durability_function(x)

    best_x: np.ndarray | None = None
    best_val = np.inf

    for _ in range(n_restarts):
        x0 = _random_x0(bounds, rng)
        res = minimize(scalarized, x0, method="L-BFGS-B", bounds=bounds)
        if res.success and res.fun < best_val:
            best_val = res.fun
            best_x = res.x.copy()

    assert best_x is not None, "All weighted-sum restarts failed"
    c = cost_function(best_x)
    d = inv_durability_function(best_x)
    return best_x, c, d


# ---------------------------------------------------------------------------
# Pareto filter
# ---------------------------------------------------------------------------

def _deduplicate(points: list[ParetoPoint], tol: float = 1e-6) -> list[ParetoPoint]:
    """Remove near-duplicate points (within tol in both objectives)."""
    if not points:
        return points
    unique: list[ParetoPoint] = [points[0]]
    for p in points[1:]:
        if not any(abs(p.cost - u.cost) < tol and abs(p.inv_durability - u.inv_durability) < tol
                   for u in unique):
            unique.append(p)
    return unique


def pareto_filter(points: list[ParetoPoint]) -> list[ParetoPoint]:
    """Remove dominated and duplicate points.  Keep only non-dominated (Pareto-optimal) ones.

    A point p dominates q if p.cost <= q.cost AND p.inv_durability <= q.inv_durability
    with at least one strict inequality.
    """
    # First deduplicate to avoid trivial ties
    points = _deduplicate(points)

    n = len(points)
    is_dominated = [False] * n

    for i in range(n):
        if is_dominated[i]:
            continue
        for j in range(n):
            if i == j or is_dominated[j]:
                continue
            # Does j dominate i?
            if (points[j].cost <= points[i].cost
                    and points[j].inv_durability <= points[i].inv_durability
                    and (points[j].cost < points[i].cost
                         or points[j].inv_durability < points[i].inv_durability)):
                is_dominated[i] = True
                break

    filtered = [p for p, dom in zip(points, is_dominated) if not dom]
    # Sort by cost ascending for a clean frontier
    filtered.sort(key=lambda p: p.cost)
    return filtered


# ---------------------------------------------------------------------------
# Knee point detection
# ---------------------------------------------------------------------------

def find_knee_point(front: list[ParetoPoint]) -> tuple[int, ParetoPoint]:
    """Find the knee point as the point of maximum curvature.

    For each interior point i, compute the angle formed by the vectors
    (i-1 -> i) and (i -> i+1).  The knee is where this angle is smallest
    (sharpest bend).

    Returns (index, ParetoPoint).
    """
    if len(front) <= 2:
        idx = len(front) // 2
        return idx, front[idx]

    costs = np.array([p.cost for p in front])
    durs = np.array([p.inv_durability for p in front])

    # Normalize to [0,1] for fair angle comparison
    c_range = costs.max() - costs.min()
    d_range = durs.max() - durs.min()
    if c_range < 1e-12:
        c_range = 1.0
    if d_range < 1e-12:
        d_range = 1.0

    cn = (costs - costs.min()) / c_range
    dn = (durs - durs.min()) / d_range

    best_idx = 1
    min_angle = np.inf

    for i in range(1, len(front) - 1):
        v1 = np.array([cn[i] - cn[i - 1], dn[i] - dn[i - 1]])
        v2 = np.array([cn[i + 1] - cn[i], dn[i + 1] - dn[i]])

        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 < 1e-12 or norm2 < 1e-12:
            continue

        cos_angle = np.clip(np.dot(v1, v2) / (norm1 * norm2), -1.0, 1.0)
        angle = np.arccos(cos_angle)

        if angle < min_angle:
            min_angle = angle
            best_idx = i

    return best_idx, front[best_idx]


# ---------------------------------------------------------------------------
# Trade-off rates
# ---------------------------------------------------------------------------

def compute_tradeoff_rates(front: list[ParetoPoint]) -> list[float]:
    """Compute marginal rate of substitution between consecutive Pareto points.

    MRS_i = (f2_{i+1} - f2_i) / (f1_{i+1} - f1_i)

    Since the front is sorted by increasing cost (f1) and decreasing inv_dur (f2),
    the MRS values should be negative (objectives truly conflict).
    """
    rates: list[float] = []
    for i in range(len(front) - 1):
        dc = front[i + 1].cost - front[i].cost
        dd = front[i + 1].inv_durability - front[i].inv_durability
        if abs(dc) < 1e-12:
            rates.append(float("-inf"))
        else:
            rates.append(dd / dc)
    return rates


# ---------------------------------------------------------------------------
# Solver
# ---------------------------------------------------------------------------

def solve(instance: Instance) -> Solution:
    """Solve the multi-objective problem and return a verified Solution."""
    t0 = time.perf_counter()
    rng = np.random.default_rng(seed=42)
    bounds = instance.bounds

    # ------------------------------------------------------------------
    # Step 1: Individual optima to find objective ranges
    # ------------------------------------------------------------------
    x_best_cost, best_cost = _solve_single_objective(
        cost_function, bounds, rng
    )
    x_best_dur, best_inv_dur = _solve_single_objective(
        inv_durability_function, bounds, rng
    )

    utopia = (best_cost, best_inv_dur)

    # Evaluate the "other" objective at each individual optimum
    cost_at_dur_opt = cost_function(x_best_dur)
    inv_dur_at_cost_opt = inv_durability_function(x_best_cost)

    # Range for epsilon sweep (over inv_durability constraint)
    eps_lo = best_inv_dur
    eps_hi = inv_dur_at_cost_opt

    # ------------------------------------------------------------------
    # Step 2: Epsilon-constraint sweep
    # ------------------------------------------------------------------
    epsilons = np.linspace(eps_lo, eps_hi, instance.n_pareto)
    raw_points: list[ParetoPoint] = []

    # Include the individual optima as anchor points
    raw_points.append(ParetoPoint(
        x=x_best_cost.copy(),
        cost=best_cost,
        inv_durability=inv_dur_at_cost_opt,
    ))
    raw_points.append(ParetoPoint(
        x=x_best_dur.copy(),
        cost=cost_at_dur_opt,
        inv_durability=best_inv_dur,
    ))

    for eps in epsilons:
        result = _solve_epsilon_constrained(eps, bounds, rng)
        if result is not None:
            x_sol, c_sol, d_sol = result
            raw_points.append(ParetoPoint(
                x=x_sol.copy(), cost=c_sol, inv_durability=d_sol
            ))

    # ------------------------------------------------------------------
    # Step 3: Pareto filter
    # ------------------------------------------------------------------
    pareto_front = pareto_filter(raw_points)

    # ------------------------------------------------------------------
    # Step 4: Weighted-sum solutions for comparison
    # ------------------------------------------------------------------
    weighted_raw: list[ParetoPoint] = []
    for w1 in np.linspace(0.01, 0.99, 20):
        x_w, c_w, d_w = _solve_weighted_sum(w1, bounds, rng)
        weighted_raw.append(ParetoPoint(x=x_w.copy(), cost=c_w, inv_durability=d_w))

    weighted_front = pareto_filter(weighted_raw)

    # ------------------------------------------------------------------
    # Step 5: Knee point
    # ------------------------------------------------------------------
    knee_idx, knee = find_knee_point(pareto_front)

    # ------------------------------------------------------------------
    # Step 6: Nadir point
    # ------------------------------------------------------------------
    nadir = (
        max(p.cost for p in pareto_front),
        max(p.inv_durability for p in pareto_front),
    )

    # ------------------------------------------------------------------
    # Step 7: Trade-off rates
    # ------------------------------------------------------------------
    tradeoff_rates = compute_tradeoff_rates(pareto_front)

    elapsed = time.perf_counter() - t0

    sol = Solution(
        pareto_points=pareto_front,
        weighted_points=weighted_front,
        knee_point=knee,
        knee_index=knee_idx,
        utopia=utopia,
        nadir=nadir,
        tradeoff_rates=tradeoff_rates,
        is_verified=False,  # will be set by verify()
        algorithm="Epsilon-constraint + Pareto filter (scipy L-BFGS-B)",
        time_seconds=elapsed,
    )

    # ------------------------------------------------------------------
    # Step 8: Independent verification
    # ------------------------------------------------------------------
    sol.is_verified, sol.verification_checks = verify(instance, sol)

    return sol


# ---------------------------------------------------------------------------
# Independent verification (shares NO logic with solver)
# ---------------------------------------------------------------------------

def verify(instance: Instance, sol: Solution) -> tuple[bool, dict[str, Any]]:
    """Independently verify the Pareto solution.

    Checks:
        1. All Pareto points are non-dominated
        2. No dominated points remain in the Pareto set
        3. All solutions satisfy variable bounds
        4. Objectives are correctly recomputed from design variables
        5. Knee point is on the Pareto front
        6. Utopia point is infeasible (no single solution achieves it)
        7. Trade-off rates are negative (objectives truly conflict)
    """
    checks: dict[str, Any] = {}
    all_ok = True
    tol = 1e-6
    front = sol.pareto_points

    # ------------------------------------------------------------------
    # Check 1 & 2: All points are non-dominated (no point dominates another)
    # ------------------------------------------------------------------
    non_dom_ok = True
    for i, pi in enumerate(front):
        for j, pj in enumerate(front):
            if i == j:
                continue
            # Does pj dominate pi?
            if (pj.cost <= pi.cost + tol
                    and pj.inv_durability <= pi.inv_durability + tol
                    and (pj.cost < pi.cost - tol
                         or pj.inv_durability < pi.inv_durability - tol)):
                non_dom_ok = False
                break
        if not non_dom_ok:
            break

    checks["all_points_non_dominated"] = non_dom_ok
    if not non_dom_ok:
        all_ok = False

    # ------------------------------------------------------------------
    # Check 3: All solutions satisfy variable bounds
    # ------------------------------------------------------------------
    bounds_ok = True
    for p in front:
        for k, (lo, hi) in enumerate(instance.bounds):
            if p.x[k] < lo - tol or p.x[k] > hi + tol:
                bounds_ok = False
                break
        if not bounds_ok:
            break

    checks["all_within_bounds"] = bounds_ok
    if not bounds_ok:
        all_ok = False

    # ------------------------------------------------------------------
    # Check 4: Objectives recomputed correctly from design variables
    # ------------------------------------------------------------------
    obj_ok = True
    max_cost_err = 0.0
    max_dur_err = 0.0
    for p in front:
        # Recompute cost independently
        t, a, c = p.x[0], p.x[1], p.x[2]
        recomp_cost = 2.0 * t + 5.0 * a ** 2 + 3.0 * c
        recomp_dur = -np.log(t) - 2.0 * a - 1.5 * c ** 0.8

        cost_err = abs(recomp_cost - p.cost)
        dur_err = abs(recomp_dur - p.inv_durability)
        max_cost_err = max(max_cost_err, cost_err)
        max_dur_err = max(max_dur_err, dur_err)

        if cost_err > tol or dur_err > tol:
            obj_ok = False

    checks["objectives_recomputed_correctly"] = obj_ok
    checks["max_cost_recomputation_error"] = float(max_cost_err)
    checks["max_durability_recomputation_error"] = float(max_dur_err)
    if not obj_ok:
        all_ok = False

    # ------------------------------------------------------------------
    # Check 5: Knee point is on the Pareto front
    # ------------------------------------------------------------------
    knee = sol.knee_point
    knee_on_front = any(
        abs(p.cost - knee.cost) < tol and abs(p.inv_durability - knee.inv_durability) < tol
        for p in front
    )
    checks["knee_on_pareto_front"] = knee_on_front
    if not knee_on_front:
        all_ok = False

    # ------------------------------------------------------------------
    # Check 6: Utopia point is infeasible (no single Pareto solution achieves it)
    # ------------------------------------------------------------------
    u_cost, u_dur = sol.utopia
    utopia_infeasible = not any(
        p.cost <= u_cost + tol and p.inv_durability <= u_dur + tol
        for p in front
    )
    checks["utopia_infeasible"] = utopia_infeasible
    if not utopia_infeasible:
        all_ok = False

    # ------------------------------------------------------------------
    # Check 7: Trade-off rates are negative (objectives truly conflict)
    # ------------------------------------------------------------------
    rates = sol.tradeoff_rates
    if len(rates) > 0:
        neg_count = sum(1 for r in rates if r < 0)
        rates_negative = neg_count == len(rates)
        checks["tradeoff_rates_all_negative"] = rates_negative
        checks["tradeoff_negative_fraction"] = f"{neg_count}/{len(rates)}"
        if not rates_negative:
            all_ok = False
    else:
        checks["tradeoff_rates_all_negative"] = True
        checks["tradeoff_negative_fraction"] = "0/0 (trivial)"

    return all_ok, checks


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Build instance
    instance = Instance(
        bounds=(
            (1.0, 10.0),  # material thickness (mm)
            (1.0, 5.0),   # alloy grade (index)
            (0.5, 3.0),   # coating level (index)
        ),
        n_pareto=50,
    )

    sol = solve(instance)

    # ── Solution Report ───────────────────────────────────────────────
    log.header("Pareto Optimization: Product Design Trade-offs")

    log.metric("Algorithm:", sol.algorithm, tag="SOLVE")
    log.metric("Time:", f"{sol.time_seconds:.4f}s", tag="TIMING")
    log.metric("Pareto points:", str(len(sol.pareto_points)), tag="RESULT")
    log.metric("Weighted-sum pts:", str(len(sol.weighted_points)), tag="RESULT")
    log.blank()

    # ── Utopia and Nadir ──────────────────────────────────────────────
    log.step("UTOPIA & NADIR POINTS")
    log.metric("Utopia (cost):", f"{sol.utopia[0]:.4f}", tag="RESULT")
    log.metric("Utopia (inv_dur):", f"{sol.utopia[1]:.4f}", tag="RESULT")
    log.metric("Nadir  (cost):", f"{sol.nadir[0]:.4f}", tag="RESULT")
    log.metric("Nadir  (inv_dur):", f"{sol.nadir[1]:.4f}", tag="RESULT")
    log.blank()

    # ── Pareto Frontier Table ─────────────────────────────────────────
    log.step("PARETO FRONTIER")
    log.table_row(
        f"{'#':>3}  {'Cost':>10}  {'Inv Dur':>10}  "
        f"{'Thickness':>10}  {'Alloy':>8}  {'Coating':>8}",
        tag="TABLE",
    )
    log.divider()

    for i, p in enumerate(sol.pareto_points):
        marker = "  <-- knee" if i == sol.knee_index else ""
        log.table_row(
            f"{i:>3}  {p.cost:>10.4f}  {p.inv_durability:>10.4f}  "
            f"{p.x[0]:>10.4f}  {p.x[1]:>8.4f}  {p.x[2]:>8.4f}{marker}",
            tag="TABLE",
        )

    log.blank()

    # ── Knee Point Detail ─────────────────────────────────────────────
    log.step("KNEE POINT (Best Compromise)")
    kp = sol.knee_point
    log.metric("Cost:", f"{kp.cost:.4f}", tag="RESULT")
    log.metric("Inv durability:", f"{kp.inv_durability:.4f}", tag="RESULT")
    log.metric("Thickness:", f"{kp.x[0]:.4f} mm", tag="DATA")
    log.metric("Alloy grade:", f"{kp.x[1]:.4f}", tag="DATA")
    log.metric("Coating level:", f"{kp.x[2]:.4f}", tag="DATA")
    log.metric("Frontier index:", f"{sol.knee_index} / {len(sol.pareto_points) - 1}", tag="DATA")
    log.blank()

    # ── Trade-off Rates ───────────────────────────────────────────────
    log.step("TRADE-OFF RATES (Marginal Rate of Substitution)")
    log.table_row(
        f"{'Segment':>8}  {'delta_cost':>12}  {'delta_dur':>12}  {'MRS':>12}",
        tag="TABLE",
    )
    log.divider()

    front = sol.pareto_points
    for i, rate in enumerate(sol.tradeoff_rates):
        dc = front[i + 1].cost - front[i].cost
        dd = front[i + 1].inv_durability - front[i].inv_durability
        log.table_row(
            f"{i:>3}->{i+1:<3}  {dc:>12.4f}  {dd:>12.4f}  {rate:>12.4f}",
            tag="TABLE",
        )

    log.blank()

    # ── Weighted-Sum Comparison ───────────────────────────────────────
    log.step("WEIGHTED-SUM PARETO POINTS (for comparison)")
    log.table_row(
        f"{'#':>3}  {'Cost':>10}  {'Inv Dur':>10}",
        tag="TABLE",
    )
    log.divider()

    for i, p in enumerate(sol.weighted_points):
        log.table_row(
            f"{i:>3}  {p.cost:>10.4f}  {p.inv_durability:>10.4f}",
            tag="TABLE",
        )

    log.blank()

    # ── Independent Verification ──────────────────────────────────────
    log.step("INDEPENDENT VERIFICATION")
    for check_name, result in sol.verification_checks.items():
        if isinstance(result, bool):
            log.check(check_name, result, tag="VERIFY")
        else:
            log.check(check_name, result, tag="VERIFY")

    log.blank()

    overall = "ALL CHECKS PASSED" if sol.is_verified else "SOME CHECKS FAILED"
    if sol.is_verified:
        log.success(overall, tag="VERIFY")
    else:
        log.error(overall, tag="VERIFY")
    log.blank()

    # ── Interpretation ────────────────────────────────────────────────
    log.step("INTERPRETATION")
    log.info(
        f"The Pareto frontier contains {len(sol.pareto_points)} non-dominated designs.",
        tag="INTERPRET",
    )
    log.info(
        f"Cost ranges from {sol.utopia[0]:.2f} (min-cost design) to "
        f"{sol.nadir[0]:.2f} (most durable design).",
        tag="INTERPRET",
    )
    log.info(
        f"Inverse durability ranges from {sol.utopia[1]:.2f} (most durable) to "
        f"{sol.nadir[1]:.2f} (cheapest design).",
        tag="INTERPRET",
    )
    log.info(
        f"The knee point at index {sol.knee_index} offers the best compromise: "
        f"cost={kp.cost:.2f}, inv_dur={kp.inv_durability:.2f}.",
        tag="INTERPRET",
    )

    if sol.tradeoff_rates:
        finite_rates = [r for r in sol.tradeoff_rates if np.isfinite(r)]
        if finite_rates:
            avg_rate = np.mean(finite_rates)
            log.info(
                f"Average MRS = {avg_rate:.4f}: each unit increase in cost yields "
                f"~{abs(avg_rate):.4f} units of durability improvement on average.",
                tag="INTERPRET",
            )

    log.info(
        "Recommendation: start with the knee-point design and adjust based "
        "on whether the business prioritizes cost savings or product longevity.",
        tag="RECOMMEND",
    )
    log.blank()

    # ── Save solution ─────────────────────────────────────────────────
    output = {
        "n_pareto_points": len(sol.pareto_points),
        "n_weighted_points": len(sol.weighted_points),
        "knee_point": {
            "cost": float(kp.cost),
            "inv_durability": float(kp.inv_durability),
            "thickness": float(kp.x[0]),
            "alloy_grade": float(kp.x[1]),
            "coating_level": float(kp.x[2]),
            "frontier_index": sol.knee_index,
        },
        "utopia": {"cost": float(sol.utopia[0]), "inv_durability": float(sol.utopia[1])},
        "nadir": {"cost": float(sol.nadir[0]), "inv_durability": float(sol.nadir[1])},
        "pareto_front": [
            {"cost": float(p.cost), "inv_durability": float(p.inv_durability)}
            for p in sol.pareto_points
        ],
        "tradeoff_rates": [float(r) for r in sol.tradeoff_rates],
        "is_verified": sol.is_verified,
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
    }
    out_path = Path(__file__).parent / "solution.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    log.success(str(out_path.name), tag="SAVE")
    log.divider(style="thick")
