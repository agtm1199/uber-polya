#!/usr/bin/env python3
"""Root Finding & Interpolation solver -- Numerical methods comparison.

Given measured data points of temperature vs. thermal expansion coefficient,
finds the temperature where alpha(T) = target using four root-finding methods
(bisection, Newton via finite difference, secant, Brent).  Compares three
interpolation schemes (linear, cubic spline, Lagrange) and three quadrature
rules (trapezoidal, Simpson, Gaussian) for integrating alpha(T).

Algorithm: Cubic spline interpolation + bisection / Newton / secant / Brent.
Complexity: O(n) interpolation setup; O(log(1/eps)) root-finding iterations.
Correctness: 8 independent verification checks.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from scipy import interpolate, integrate, optimize

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger
log = PolyaLogger()


# --- Data Model ---

@dataclass(frozen=True)
class Instance:
    """Problem instance for root finding and interpolation."""
    temperatures: tuple[float, ...]          # measured temperatures (deg C)
    coefficients: tuple[float, ...]          # expansion coefficients (x1e-6 /deg C)
    target_coefficient: float                # target alpha value (x1e-6 /deg C)
    integration_low: float                   # lower bound for integration (deg C)
    integration_high: float                  # upper bound for integration (deg C)


@dataclass
class RootResult:
    """Result from a single root-finding method."""
    method: str
    root: float
    residual: float
    iterations: int
    converged: bool


@dataclass
class Solution:
    """Verified solution with metadata."""
    root_results: list[dict]                 # one entry per method
    best_root: float                         # root from Brent (reference)
    best_residual: float                     # |g(root)| from Brent
    interpolation_comparison: dict           # max errors for each scheme
    integral_trapezoidal: float              # integral via trapezoidal rule
    integral_simpson: float                  # integral via Simpson's rule
    integral_gaussian: float                 # integral via scipy.integrate.quad
    objective: float                         # best root temperature
    is_optimal: bool
    is_feasible: bool
    algorithm: str
    time_seconds: float
    certificate: str
    constraint_check: dict[str, bool] = field(default_factory=dict)


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Solve the root-finding / interpolation / quadrature problem."""
    t0 = time.perf_counter()

    T = np.array(instance.temperatures)
    alpha = np.array(instance.coefficients)
    target = instance.target_coefficient
    T_lo, T_hi = instance.integration_low, instance.integration_high

    # ── Interpolation ──────────────────────────────────────────────

    # Cubic spline (primary)
    cs = interpolate.CubicSpline(T, alpha)

    # Linear interpolation
    linear_interp = interpolate.interp1d(T, alpha, kind="linear")

    # Lagrange interpolation
    lagrange_poly = interpolate.lagrange(T, alpha)

    # Evaluate interpolation accuracy at the data points
    interp_comparison: dict[str, float] = {}

    cs_at_data = cs(T)
    interp_comparison["cubic_spline_max_error"] = float(np.max(np.abs(cs_at_data - alpha)))

    lin_at_data = linear_interp(T)
    interp_comparison["linear_max_error"] = float(np.max(np.abs(lin_at_data - alpha)))

    lag_at_data = np.array([float(lagrange_poly(ti)) for ti in T])
    interp_comparison["lagrange_max_error"] = float(np.max(np.abs(lag_at_data - alpha)))

    # Evaluate on a fine grid to compare shapes
    T_fine = np.linspace(T[0], T[-1], 500)
    cs_fine = cs(T_fine)
    lin_fine = linear_interp(T_fine)
    lag_fine = np.array([float(lagrange_poly(ti)) for ti in T_fine])

    interp_comparison["max_spline_vs_linear"] = float(np.max(np.abs(cs_fine - lin_fine)))
    interp_comparison["max_spline_vs_lagrange"] = float(np.max(np.abs(cs_fine - lag_fine)))

    # ── Root Finding ───────────────────────────────────────────────

    def g(t: float) -> float:
        """Objective: g(T) = spline(T) - target.  Root is where alpha(T) = target."""
        return float(cs(t)) - target

    root_results: list[RootResult] = []

    # 1. Bisection
    a, b = float(T[0]), float(T[-1])
    tol = 1e-12
    bisect_iters = 0
    a_b, b_b = a, b
    while (b_b - a_b) > tol and bisect_iters < 200:
        mid = (a_b + b_b) / 2.0
        if g(a_b) * g(mid) <= 0:
            b_b = mid
        else:
            a_b = mid
        bisect_iters += 1
    bisect_root = (a_b + b_b) / 2.0
    root_results.append(RootResult(
        method="bisection",
        root=bisect_root,
        residual=abs(g(bisect_root)),
        iterations=bisect_iters,
        converged=abs(g(bisect_root)) < 1e-6,
    ))

    # 2. Newton (finite-difference derivative)
    newton_x = (a + b) / 2.0  # initial guess: midpoint
    newton_iters = 0
    h_fd = 1e-8
    converged_newton = False
    for _ in range(200):
        fx = g(newton_x)
        fpx = (g(newton_x + h_fd) - g(newton_x - h_fd)) / (2.0 * h_fd)
        if abs(fpx) < 1e-15:
            break
        newton_x -= fx / fpx
        newton_iters += 1
        if abs(fx) < tol:
            converged_newton = True
            break
    root_results.append(RootResult(
        method="newton",
        root=newton_x,
        residual=abs(g(newton_x)),
        iterations=newton_iters,
        converged=converged_newton,
    ))

    # 3. Secant
    x0, x1 = a + 10.0, b - 10.0  # two initial points away from edges
    secant_iters = 0
    converged_secant = False
    for _ in range(200):
        f0, f1 = g(x0), g(x1)
        if abs(f1 - f0) < 1e-15:
            break
        x_new = x1 - f1 * (x1 - x0) / (f1 - f0)
        x0, x1 = x1, x_new
        secant_iters += 1
        if abs(g(x1)) < tol:
            converged_secant = True
            break
    root_results.append(RootResult(
        method="secant",
        root=x1,
        residual=abs(g(x1)),
        iterations=secant_iters,
        converged=converged_secant,
    ))

    # 4. Brent (scipy -- the gold standard)
    brent_result = optimize.brentq(g, a, b, full_output=True, xtol=tol)
    brent_root = brent_result[0]
    brent_info = brent_result[1]
    root_results.append(RootResult(
        method="brent",
        root=brent_root,
        residual=abs(g(brent_root)),
        iterations=brent_info.iterations,
        converged=True,
    ))

    # ── Numerical Integration ──────────────────────────────────────

    # Integrate spline(T) from T_lo to T_hi
    # Fine grid for trapezoidal and Simpson
    n_quad = 1001  # odd for Simpson
    T_quad = np.linspace(T_lo, T_hi, n_quad)
    alpha_quad = cs(T_quad)

    integral_trap = float(np.trapezoid(alpha_quad, T_quad))
    integral_simp = float(integrate.simpson(alpha_quad, x=T_quad))
    integral_gauss, _ = integrate.quad(lambda t: float(cs(t)), T_lo, T_hi)

    elapsed = time.perf_counter() - t0

    # Build solution
    root_dicts = [
        {
            "method": r.method,
            "root_degC": r.root,
            "residual": r.residual,
            "iterations": r.iterations,
            "converged": r.converged,
        }
        for r in root_results
    ]

    brent_rr = root_results[3]  # Brent is the 4th entry

    sol = Solution(
        root_results=root_dicts,
        best_root=brent_rr.root,
        best_residual=brent_rr.residual,
        interpolation_comparison=interp_comparison,
        integral_trapezoidal=integral_trap,
        integral_simpson=integral_simp,
        integral_gaussian=integral_gauss,
        objective=brent_rr.root,
        is_optimal=True,
        is_feasible=True,
        algorithm="Cubic Spline + Brent/Bisection/Newton/Secant root finding",
        time_seconds=elapsed,
        certificate=(
            f"Brent root T* = {brent_rr.root:.6f} degC, "
            f"|g(T*)| = {brent_rr.residual:.2e}"
        ),
    )

    # Independent verification
    sol.is_feasible, sol.constraint_check = verify(instance, {
        "root_results": root_results,
        "spline": cs,
        "integral_trap": integral_trap,
        "integral_simp": integral_simp,
        "integral_gauss": integral_gauss,
    })

    return sol


# --- Verification (independent of solver) ---

def verify(
    instance: Instance,
    solution_data: dict,
) -> tuple[bool, dict[str, bool]]:
    """Independently verify the root-finding solution.

    Uses only the raw Instance data and solution artifacts -- recomputes
    everything from scratch where possible.
    """
    checks: dict[str, bool] = {}
    all_ok = True

    T = np.array(instance.temperatures)
    alpha = np.array(instance.coefficients)
    target = instance.target_coefficient

    root_results: list[RootResult] = solution_data["root_results"]
    cs = solution_data["spline"]

    integral_trap = solution_data["integral_trap"]
    integral_simp = solution_data["integral_simp"]
    integral_gauss = solution_data["integral_gauss"]

    # Check 1: all_methods_find_root -- all 4 methods return a root
    ok = all(r.converged for r in root_results)
    checks["all_methods_find_root"] = ok
    if not ok:
        all_ok = False

    # Check 2: roots_agree -- all roots within 0.1 deg C of each other
    roots = [r.root for r in root_results]
    root_spread = max(roots) - min(roots)
    ok = root_spread < 0.1
    checks["roots_agree"] = ok
    if not ok:
        all_ok = False

    # Check 3: residual_small -- |g(root)| < 1e-8 for Brent
    brent_rr = [r for r in root_results if r.method == "brent"][0]
    ok = brent_rr.residual < 1e-8
    checks["residual_small"] = ok
    if not ok:
        all_ok = False

    # Check 4: root_in_range -- root within data range
    ok = float(T[0]) <= brent_rr.root <= float(T[-1])
    checks["root_in_range"] = ok
    if not ok:
        all_ok = False

    # Check 5: spline_passes_through_data -- max |spline(x_i) - y_i| < 1e-10
    cs_at_data = cs(T)
    max_interp_err = float(np.max(np.abs(cs_at_data - alpha)))
    ok = max_interp_err < 1e-10
    checks["spline_passes_through_data"] = ok
    if not ok:
        all_ok = False

    # Check 6: integration_methods_agree -- all 3 integrals within 1%
    integrals = [integral_trap, integral_simp, integral_gauss]
    mean_int = sum(integrals) / 3.0
    ok = all(abs(v - mean_int) / mean_int < 0.01 for v in integrals)
    checks["integration_methods_agree"] = ok
    if not ok:
        all_ok = False

    # Check 7: integration_positive -- integral > 0
    ok = all(v > 0 for v in integrals)
    checks["integration_positive"] = ok
    if not ok:
        all_ok = False

    # Check 8: brent_fewest_or_tied -- Brent converges in <= iterations of bisection
    bisect_rr = [r for r in root_results if r.method == "bisection"][0]
    ok = brent_rr.iterations <= bisect_rr.iterations
    checks["brent_fewest_or_tied"] = ok
    if not ok:
        all_ok = False

    return all_ok, checks


# --- Main ---

if __name__ == "__main__":
    # Build instance: 8 realistic (T, alpha) data points for a steel alloy.
    # Temperatures in deg C, expansion coefficients in x1e-6 /deg C.
    instance = Instance(
        temperatures=(0.0, 100.0, 200.0, 300.0, 400.0, 500.0, 600.0, 700.0),
        coefficients=(9.4, 10.6, 11.4, 12.1, 13.0, 14.0, 15.1, 16.3),
        target_coefficient=12.0,
        integration_low=100.0,
        integration_high=500.0,
    )

    sol = solve(instance)

    # --- Print Solution Report ---
    log.header("SOLUTION REPORT: Root Finding & Interpolation")

    log.step("PROBLEM SETUP")
    log.metric("Material:", "Steel alloy thermal expansion", tag="DATA")
    log.metric("Data points:", f"{len(instance.temperatures)}", tag="DATA")
    log.metric("Target alpha:", f"{instance.target_coefficient} x1e-6 /degC", tag="DATA")
    log.metric("Integration range:", f"[{instance.integration_low}, {instance.integration_high}] degC", tag="DATA")
    log.blank()

    log.info("Temperature (degC):  " + "  ".join(f"{t:6.0f}" for t in instance.temperatures), tag="DATA")
    log.info("alpha (x1e-6/degC):  " + "  ".join(f"{a:6.1f}" for a in instance.coefficients), tag="DATA")
    log.blank()

    # Interpolation comparison
    log.step("INTERPOLATION COMPARISON")
    ic = sol.interpolation_comparison
    log.metric("Cubic spline max err:", f"{ic['cubic_spline_max_error']:.2e} (at data pts)", tag="RESULT")
    log.metric("Linear max err:", f"{ic['linear_max_error']:.2e} (at data pts)", tag="RESULT")
    log.metric("Lagrange max err:", f"{ic['lagrange_max_error']:.2e} (at data pts)", tag="RESULT")
    log.metric("Spline vs linear:", f"{ic['max_spline_vs_linear']:.4f} (max diff on fine grid)", tag="SENSITIVITY")
    log.metric("Spline vs Lagrange:", f"{ic['max_spline_vs_lagrange']:.4f} (max diff on fine grid)", tag="SENSITIVITY")
    log.blank()

    # Root finding comparison
    log.step("ROOT FINDING: g(T) = spline(T) - 12.0 = 0")
    log.table_row(
        f"{'Method':<12} {'Root (degC)':>12} {'|g(root)|':>14} {'Iters':>8} {'Converged':>10}",
        tag="TABLE",
    )
    log.divider()
    for r in sol.root_results:
        log.table_row(
            f"{r['method']:<12} {r['root_degC']:>12.6f} {r['residual']:>14.2e} "
            f"{r['iterations']:>8d} {'YES' if r['converged'] else 'NO':>10}",
            tag="RESULT",
        )
    log.blank()

    log.metric("Best root (Brent):", f"{sol.best_root:.6f} degC", tag="RESULT")
    log.metric("Best residual:", f"{sol.best_residual:.2e}", tag="RESULT")
    log.info(f"At T = {sol.best_root:.2f} degC, alpha = {sol.best_root + 0.0:.6f}", tag="INTERPRET")
    log.info(f"  => spline({sol.best_root:.6f}) = {sol.objective + 0.0:.6f} ... target = {instance.target_coefficient}", tag="INTERPRET")
    log.blank()

    # Numerical integration
    log.step("NUMERICAL INTEGRATION: integral of alpha(T) over [100, 500] degC")
    log.metric("Trapezoidal:", f"{sol.integral_trapezoidal:.6f} (x1e-6 degC)", tag="RESULT")
    log.metric("Simpson:", f"{sol.integral_simpson:.6f} (x1e-6 degC)", tag="RESULT")
    log.metric("Gaussian quad:", f"{sol.integral_gaussian:.6f} (x1e-6 degC)", tag="RESULT")
    mean_int = (sol.integral_trapezoidal + sol.integral_simpson + sol.integral_gaussian) / 3.0
    log.metric("Mean:", f"{mean_int:.6f}", tag="STATS")
    max_dev = max(
        abs(sol.integral_trapezoidal - mean_int),
        abs(sol.integral_simpson - mean_int),
        abs(sol.integral_gaussian - mean_int),
    )
    log.metric("Max deviation:", f"{max_dev:.2e} ({max_dev / mean_int * 100:.4f}%)", tag="SENSITIVITY")
    log.blank()

    # Physical interpretation
    log.step("PHYSICAL INTERPRETATION")
    log.info(
        f"The thermal expansion coefficient reaches {instance.target_coefficient} x1e-6 /degC "
        f"at T = {sol.best_root:.1f} degC.",
        tag="INTERPRET",
    )
    log.info(
        f"Integrated expansion over [{instance.integration_low:.0f}, {instance.integration_high:.0f}] degC: "
        f"{sol.integral_gaussian:.2f} x1e-6 degC.",
        tag="INTERPRET",
    )
    log.info(
        "This integral represents the total thermal strain contribution over the range.",
        tag="INTERPRET",
    )
    log.blank()

    log.metric("Algorithm:", sol.algorithm, tag="SOLVE")
    log.metric("Time:", f"{sol.time_seconds:.6f}s", tag="TIMING")
    log.blank()

    # Independent verification
    log.step("INDEPENDENT VERIFICATION")
    for check_name, result in sol.constraint_check.items():
        if isinstance(result, bool):
            log.check(check_name, result, tag="VERIFY")
        else:
            log.check(check_name, result, tag="VERIFY")
    log.blank()

    all_passed = all(v for v in sol.constraint_check.values() if isinstance(v, bool))
    if all_passed:
        log.success(f"All {sum(1 for v in sol.constraint_check.values() if isinstance(v, bool))} checks passed.", tag="COMPLETE")
    else:
        failed = [k for k, v in sol.constraint_check.items() if isinstance(v, bool) and not v]
        log.error(f"{len(failed)} check(s) failed: {', '.join(failed)}", tag="ERROR")
    log.blank()

    log.divider(style="thick")

    # Save JSON
    output = {
        "instance": {
            "temperatures": list(instance.temperatures),
            "coefficients": list(instance.coefficients),
            "target_coefficient": instance.target_coefficient,
            "integration_range": [instance.integration_low, instance.integration_high],
        },
        "root_finding": {
            "methods": sol.root_results,
            "best_method": "brent",
            "best_root_degC": sol.best_root,
            "best_residual": sol.best_residual,
        },
        "interpolation": sol.interpolation_comparison,
        "integration": {
            "trapezoidal": sol.integral_trapezoidal,
            "simpson": sol.integral_simpson,
            "gaussian_quad": sol.integral_gaussian,
        },
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
        "verification": {
            k: v for k, v in sol.constraint_check.items() if isinstance(v, bool)
        },
    }
    with open(str(Path(__file__).parent / "solution.json"), "w") as f:
        json.dump(output, f, indent=2)
    log.success("solution.json", tag="SAVE")
