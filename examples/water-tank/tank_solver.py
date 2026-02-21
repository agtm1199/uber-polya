#!/usr/bin/env python3
"""Water Tank Optimization solver -- Calculus-based design optimization.

Finds the dimensions of an open-top cylindrical tank that holds a given
volume using the least material (minimum surface area).  Uses SymPy for
symbolic differentiation, critical-point analysis, and the second
derivative test.  Also solves the closed-top variant for comparison and
computes material savings versus a cube of equal volume.

Algorithm: Symbolic differentiation + critical point analysis (SymPy).
Complexity: O(1) -- closed-form solution.
Correctness: Second derivative test + independent numerical verification.
"""
from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass, field
from pathlib import Path

import sympy as sp

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger
log = PolyaLogger()


# --- Data Model ---

@dataclass(frozen=True)
class Instance:
    """Problem instance for water tank optimization."""
    volume_liters: float        # required volume in liters
    open_top: bool = True       # True = no lid, False = closed cylinder

    @property
    def volume_m3(self) -> float:
        """Volume in cubic metres (1 L = 0.001 m^3)."""
        return self.volume_liters / 1000.0


@dataclass
class Solution:
    """Verified solution with metadata."""
    radius: float                   # optimal radius (m)
    height: float                   # optimal height (m)
    surface_area: float             # minimized surface area (m^2)
    material_savings_vs_cube: float # percentage saved compared to cube
    radius_symbolic: str            # symbolic expression for r*
    height_symbolic: str            # symbolic expression for h*
    surface_symbolic: str           # symbolic expression for S*
    second_derivative: str          # d^2S/dr^2 at r* (must be > 0)
    closed_top_radius: float        # optimal r for closed variant (m)
    closed_top_height: float        # optimal h for closed variant (m)
    closed_top_area: float          # minimized area for closed variant (m^2)
    objective: float                # surface area (the quantity minimized)
    is_optimal: bool
    is_feasible: bool
    algorithm: str
    time_seconds: float
    certificate: str
    constraint_check: dict[str, bool] = field(default_factory=dict)


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Solve the tank optimization problem symbolically."""
    t0 = time.perf_counter()

    V_val = instance.volume_m3

    # Symbolic variables
    r, h, V = sp.symbols("r h V", positive=True)

    # --- Open-top cylinder ---
    # Surface area: base + lateral wall (no lid)
    S_open = sp.pi * r**2 + 2 * sp.pi * r * h

    # Volume constraint: pi * r^2 * h = V
    h_expr = V / (sp.pi * r**2)

    # Substitute h into S to get S(r)
    S_r_open = S_open.subs(h, h_expr)
    S_r_open = sp.simplify(S_r_open)

    # Differentiate and solve dS/dr = 0
    dS_dr_open = sp.diff(S_r_open, r)
    critical_open = sp.solve(dS_dr_open, r)
    # Take the positive real root
    r_opt_open = critical_open[0]

    # Second derivative test
    d2S_dr2_open = sp.diff(S_r_open, r, 2)
    d2S_at_opt_open = sp.simplify(d2S_dr2_open.subs(r, r_opt_open))

    # Optimal height
    h_opt_open = sp.simplify(h_expr.subs(r, r_opt_open))

    # Optimal surface area
    S_opt_open = sp.simplify(S_r_open.subs(r, r_opt_open))

    # Numerical evaluation for open-top
    r_num_open = float(r_opt_open.subs(V, V_val))
    h_num_open = float(h_opt_open.subs(V, V_val))
    S_num_open = float(S_opt_open.subs(V, V_val))
    d2S_num_open = float(d2S_at_opt_open.subs(V, V_val))

    # --- Closed-top cylinder ---
    S_closed = 2 * sp.pi * r**2 + 2 * sp.pi * r * h
    S_r_closed = S_closed.subs(h, h_expr)
    S_r_closed = sp.simplify(S_r_closed)

    dS_dr_closed = sp.diff(S_r_closed, r)
    critical_closed = sp.solve(dS_dr_closed, r)
    r_opt_closed = critical_closed[0]

    h_opt_closed = sp.simplify(h_expr.subs(r, r_opt_closed))
    S_opt_closed = sp.simplify(S_r_closed.subs(r, r_opt_closed))

    r_num_closed = float(r_opt_closed.subs(V, V_val))
    h_num_closed = float(h_opt_closed.subs(V, V_val))
    S_num_closed = float(S_opt_closed.subs(V, V_val))

    # --- Cube comparison ---
    # Cube with same volume: side = V^(1/3), open-top area = 5 * side^2
    cube_side = V_val ** (1 / 3)
    cube_area_open = 5 * cube_side**2   # 5 faces (no lid)
    cube_area_closed = 6 * cube_side**2  # 6 faces

    if instance.open_top:
        savings = (cube_area_open - S_num_open) / cube_area_open * 100
    else:
        savings = (cube_area_closed - S_num_closed) / cube_area_closed * 100

    elapsed = time.perf_counter() - t0

    sol = Solution(
        radius=r_num_open,
        height=h_num_open,
        surface_area=S_num_open,
        material_savings_vs_cube=savings,
        radius_symbolic=str(sp.simplify(r_opt_open)),
        height_symbolic=str(sp.simplify(h_opt_open)),
        surface_symbolic=str(sp.simplify(S_opt_open)),
        second_derivative=str(d2S_at_opt_open),
        closed_top_radius=r_num_closed,
        closed_top_height=h_num_closed,
        closed_top_area=S_num_closed,
        objective=S_num_open if instance.open_top else S_num_closed,
        is_optimal=True,
        is_feasible=True,
        algorithm="Symbolic Differentiation + Critical Point Analysis (SymPy)",
        time_seconds=elapsed,
        certificate=(
            f"d^2S/dr^2 at r* = {d2S_num_open:.4f} > 0 (confirmed minimum)"
        ),
    )

    # Independent verification
    sol.is_feasible, sol.constraint_check = verify(instance, {
        "radius": r_num_open,
        "height": h_num_open,
        "surface_area": S_num_open,
        "d2S_at_opt": d2S_num_open,
        "closed_radius": r_num_closed,
        "closed_height": h_num_closed,
        "closed_area": S_num_closed,
    })

    return sol


# --- Verification (independent of solver) ---

def verify(
    instance: Instance,
    solution_data: dict,
) -> tuple[bool, dict[str, bool]]:
    """Independently verify the tank optimization solution.

    Recomputes everything from scratch using plain math -- no SymPy,
    no shared variables with the solver.
    """
    checks: dict[str, bool] = {}
    all_ok = True
    V = instance.volume_m3

    r = solution_data["radius"]
    h = solution_data["height"]
    S = solution_data["surface_area"]
    d2S = solution_data["d2S_at_opt"]

    # Check 1: Volume constraint satisfied
    vol_computed = math.pi * r**2 * h
    ok = abs(vol_computed - V) / V < 1e-8
    checks["volume_constraint_satisfied"] = ok
    if not ok:
        all_ok = False

    # Check 2: Surface area matches recomputation (open-top)
    S_recomputed = math.pi * r**2 + 2 * math.pi * r * h
    ok = abs(S_recomputed - S) / S < 1e-8
    checks["surface_area_recomputed_matches"] = ok
    if not ok:
        all_ok = False

    # Check 3: Second derivative is positive (confirms minimum)
    ok = d2S > 0
    checks["second_derivative_positive"] = ok
    if not ok:
        all_ok = False

    # Check 4: dS/dr ~ 0 at optimal r (first-order condition)
    # S(r) = pi*r^2 + 2*V/r  (after substituting h = V/(pi*r^2))
    dS_dr = 2 * math.pi * r - 2 * V / r**2
    ok = abs(dS_dr) < 1e-8
    checks["first_order_condition_dSdr_zero"] = ok
    if not ok:
        all_ok = False

    # Check 5: h/r ratio for open-top should be ~1.0
    ratio_open = h / r
    ok = abs(ratio_open - 1.0) < 1e-6
    checks["open_top_h_equals_r"] = ok
    if not ok:
        all_ok = False

    # Check 6: Closed-top variant checks
    rc = solution_data["closed_radius"]
    hc = solution_data["closed_height"]
    Sc = solution_data["closed_area"]

    vol_closed = math.pi * rc**2 * hc
    ok = abs(vol_closed - V) / V < 1e-8
    checks["closed_volume_constraint"] = ok
    if not ok:
        all_ok = False

    S_closed_recomputed = 2 * math.pi * rc**2 + 2 * math.pi * rc * hc
    ok = abs(S_closed_recomputed - Sc) / Sc < 1e-8
    checks["closed_surface_area_recomputed"] = ok
    if not ok:
        all_ok = False

    # h/r ratio for closed-top should be ~2.0
    ratio_closed = hc / rc
    ok = abs(ratio_closed - 2.0) < 1e-6
    checks["closed_top_h_equals_2r"] = ok
    if not ok:
        all_ok = False

    # Check 7: Perturbation test -- slightly larger and smaller r give worse S
    for delta in [0.001, -0.001]:
        r_pert = r + delta
        h_pert = V / (math.pi * r_pert**2)
        S_pert = math.pi * r_pert**2 + 2 * math.pi * r_pert * h_pert
        ok = S_pert > S
        tag = f"perturbation_r{'+' if delta > 0 else ''}{delta}_gives_worse_S"
        checks[tag] = ok
        if not ok:
            all_ok = False

    return all_ok, checks


# --- Main ---

if __name__ == "__main__":
    # Build instance: 1000-litre open-top cylindrical tank
    instance = Instance(
        volume_liters=1000.0,
        open_top=True,
    )

    sol = solve(instance)

    # --- Print Solution Report ---
    log.header("SOLUTION REPORT: Water Tank Optimization")

    log.step("PROBLEM SETUP")
    log.metric("Tank type:", "Open-top cylinder (no lid)", tag="DATA")
    log.metric("Required volume:", f"{instance.volume_liters:.0f} L ({instance.volume_m3:.3f} m^3)", tag="DATA")
    log.metric("Objective:", "Minimize surface area (material)", tag="DATA")
    log.metric("Constraint:", "pi * r^2 * h = V", tag="DATA")
    log.blank()

    # Symbolic derivation
    log.step("SYMBOLIC DERIVATION (Open-Top)")
    log.info("Surface area:   S(r, h) = pi*r^2 + 2*pi*r*h", tag="MODEL")
    log.info("Volume constraint: V = pi*r^2*h  =>  h = V / (pi*r^2)", tag="MODEL")
    log.info("Substituting:   S(r) = pi*r^2 + 2*V/r", tag="MODEL")
    log.blank()
    log.info("dS/dr = 2*pi*r - 2*V/r^2 = 0", tag="SOLVE")
    log.info(f"Optimal radius:  r* = {sol.radius_symbolic}", tag="SOLVE")
    log.info(f"Optimal height:  h* = {sol.height_symbolic}", tag="SOLVE")
    log.info(f"Minimum area:    S* = {sol.surface_symbolic}", tag="SOLVE")
    log.blank()
    log.info(f"Second derivative at r*: d^2S/dr^2 = {sol.second_derivative}", tag="VERIFY")
    log.info(f"  => {sol.certificate}", tag="VERIFY")
    log.blank()

    # Numerical results -- open-top
    log.step("NUMERICAL RESULTS (Open-Top, V = 1000 L)")
    log.metric("Optimal radius:", f"{sol.radius:.6f} m ({sol.radius * 100:.2f} cm)", tag="RESULT")
    log.metric("Optimal height:", f"{sol.height:.6f} m ({sol.height * 100:.2f} cm)", tag="RESULT")
    log.metric("h / r ratio:", f"{sol.height / sol.radius:.6f} (expected: 1.0)", tag="RESULT")
    log.metric("Surface area:", f"{sol.surface_area:.6f} m^2 ({sol.surface_area * 1e4:.2f} cm^2)", tag="RESULT")
    log.metric("Diameter:", f"{2 * sol.radius:.6f} m ({2 * sol.radius * 100:.2f} cm)", tag="RESULT")
    log.blank()

    # Closed-top comparison
    log.step("CLOSED-TOP COMPARISON")
    log.info("Closed-top: S(r, h) = 2*pi*r^2 + 2*pi*r*h", tag="MODEL")
    log.metric("Optimal radius:", f"{sol.closed_top_radius:.6f} m ({sol.closed_top_radius * 100:.2f} cm)", tag="RESULT")
    log.metric("Optimal height:", f"{sol.closed_top_height:.6f} m ({sol.closed_top_height * 100:.2f} cm)", tag="RESULT")
    log.metric("h / r ratio:", f"{sol.closed_top_height / sol.closed_top_radius:.6f} (expected: 2.0)", tag="RESULT")
    log.metric("Surface area:", f"{sol.closed_top_area:.6f} m^2", tag="RESULT")
    extra = sol.closed_top_area - sol.surface_area
    log.metric("Extra material:", f"{extra:.6f} m^2 (adding the lid)", tag="SENSITIVITY")
    log.blank()

    # Cube comparison
    log.step("COMPARISON: Cylinder vs Cube")
    V_m3 = instance.volume_m3
    cube_side = V_m3 ** (1 / 3)
    cube_area_open = 5 * cube_side**2
    cube_area_closed = 6 * cube_side**2
    log.metric("Cube side length:", f"{cube_side:.6f} m", tag="DATA")
    log.metric("Cube area (open):", f"{cube_area_open:.6f} m^2 (5 faces)", tag="DATA")
    log.metric("Cylinder area:", f"{sol.surface_area:.6f} m^2 (open-top)", tag="RESULT")
    log.metric("Material savings:", f"{sol.material_savings_vs_cube:.2f}% vs open cube", tag="RESULT")
    log.blank()

    # Lagrange multiplier interpretation
    log.step("LAGRANGE MULTIPLIER INTERPRETATION")
    log.info("The same problem can be formulated as:", tag="MODEL")
    log.info("  min S(r,h) = pi*r^2 + 2*pi*r*h", tag="MODEL")
    log.info("  s.t. g(r,h) = pi*r^2*h - V = 0", tag="MODEL")
    log.info("Lagrangian: L = S - lambda * g", tag="MODEL")
    log.info("At the optimum, lambda = dS*/dV -- the marginal material", tag="INTERPRET")
    log.info("cost of adding one more unit of volume.", tag="INTERPRET")
    # Compute lambda numerically:  dS*/dV ~ [S(V+dV) - S(V-dV)] / (2*dV)
    dV = 1e-6
    r_plus = ((V_m3 + dV) / math.pi) ** (1 / 3)
    S_plus = math.pi * r_plus**2 + 2 * (V_m3 + dV) / r_plus
    r_minus = ((V_m3 - dV) / math.pi) ** (1 / 3)
    S_minus = math.pi * r_minus**2 + 2 * (V_m3 - dV) / r_minus
    lam = (S_plus - S_minus) / (2 * dV)
    log.metric("lambda (numerical):", f"{lam:.6f} m^2 / m^3 = m^-1", tag="RESULT")
    log.info(f"Adding 1 L of capacity costs ~{lam * 0.001:.6f} m^2 of material", tag="RECOMMEND")
    log.blank()

    # Practical recommendations
    log.step("PRACTICAL RECOMMENDATIONS")
    log.info(f"Build a cylinder with diameter {2 * sol.radius * 100:.1f} cm and height {sol.height * 100:.1f} cm", tag="RECOMMEND")
    log.info(f"This uses {sol.surface_area:.4f} m^2 of sheet metal", tag="RECOMMEND")
    log.info(f"A cube of the same volume would need {cube_area_open:.4f} m^2 ({sol.material_savings_vs_cube:.1f}% more)", tag="RECOMMEND")
    log.info("The geometric insight: for an open-top cylinder, h = r at the optimum", tag="RECOMMEND")
    log.info("For a closed-top cylinder, h = 2r at the optimum", tag="RECOMMEND")
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

    log.divider(style="thick")

    # Save JSON
    output = {
        "volume_liters": instance.volume_liters,
        "volume_m3": instance.volume_m3,
        "open_top": {
            "radius_m": sol.radius,
            "height_m": sol.height,
            "surface_area_m2": sol.surface_area,
            "h_over_r": sol.height / sol.radius,
            "radius_symbolic": sol.radius_symbolic,
            "height_symbolic": sol.height_symbolic,
            "surface_symbolic": sol.surface_symbolic,
        },
        "closed_top": {
            "radius_m": sol.closed_top_radius,
            "height_m": sol.closed_top_height,
            "surface_area_m2": sol.closed_top_area,
            "h_over_r": sol.closed_top_height / sol.closed_top_radius,
        },
        "cube_comparison": {
            "side_m": cube_side,
            "area_open_m2": cube_area_open,
            "material_savings_pct": sol.material_savings_vs_cube,
        },
        "lagrange_multiplier": lam,
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
        "verification": sol.constraint_check,
    }
    with open(str(Path(__file__).parent / "solution.json"), "w") as f:
        json.dump(output, f, indent=2)
    log.success("solution.json", tag="SAVE")
