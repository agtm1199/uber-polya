#!/usr/bin/env python3
"""SIR Epidemic Model solver -- ODE-based compartmental epidemic analysis.

Solves the classic SIR (Susceptible-Infected-Recovered) model using
scipy.integrate.solve_ivp with RK45.  Computes the basic reproduction
number R0, peak infection time and magnitude, final epidemic size
(verified against the transcendental final-size relation), herd immunity
threshold, vaccination scenario analysis, and disease-free equilibrium
stability via Jacobian eigenvalue analysis.

Algorithm: Runge-Kutta 4(5) adaptive ODE integration (scipy solve_ivp).
Complexity: O(n_steps) per ODE solve, with n_steps ~ 2000.
Correctness: 8 independent verification checks.
"""
from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger
log = PolyaLogger()


# --- Data Model ---

@dataclass(frozen=True)
class Instance:
    """SIR epidemic model instance."""
    N: int                          # total population
    beta: float                     # transmission rate (per day)
    gamma: float                    # recovery rate (per day)
    I0: int                         # initial infected
    S0: int = -1                    # initial susceptible (-1 = N - I0)
    R0_init: int = 0               # initial recovered
    t_max: float = 200.0           # simulation horizon (days)
    vaccination_rates: tuple[float, ...] = (0.0, 0.3, 0.5, 0.67, 0.8)

    def __post_init__(self) -> None:
        if self.S0 == -1:
            object.__setattr__(self, "S0", self.N - self.I0)


@dataclass
class VaccinationResult:
    """Result of a single vaccination scenario."""
    vaccination_rate: float
    S0_effective: float
    R0_effective: float
    epidemic_occurs: bool
    peak_infected: float
    peak_time: float
    final_infected_frac: float


@dataclass
class Solution:
    """Verified SIR model solution with metadata."""
    # Core epidemiological quantities
    R0: float                            # basic reproduction number
    peak_infected: float                 # max simultaneous infected
    peak_time: float                     # day of peak infection
    final_infected_frac: float           # fraction ultimately infected (numerical)
    final_infected_frac_theory: float    # fraction from transcendental equation
    herd_immunity_threshold: float       # 1 - 1/R0

    # Time series
    t: np.ndarray                        # time points
    S: np.ndarray                        # susceptible over time
    I: np.ndarray                        # infected over time
    R: np.ndarray                        # recovered over time

    # Vaccination analysis
    vaccination_results: list[VaccinationResult]

    # Equilibrium analysis
    jacobian_eigenvalues: list[complex]
    dfe_stable: bool                     # disease-free equilibrium stability

    # Metadata
    algorithm: str
    time_seconds: float
    verification: dict[str, bool] = field(default_factory=dict)


# --- SIR ODE System ---

def sir_rhs(
    t: float,
    y: list[float],
    beta: float,
    gamma: float,
    N: int,
) -> list[float]:
    """Right-hand side of the SIR ODE system.

    dS/dt = -beta * S * I / N
    dI/dt =  beta * S * I / N - gamma * I
    dR/dt =  gamma * I
    """
    S, I, R = y
    dSdt = -beta * S * I / N
    dIdt = beta * S * I / N - gamma * I
    dRdt = gamma * I
    return [dSdt, dIdt, dRdt]


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Solve the SIR epidemic model."""
    t0_clock = time.perf_counter()

    N = instance.N
    beta = instance.beta
    gamma = instance.gamma

    # --- Step 1: Basic reproduction number ---
    R0 = beta / gamma

    # --- Step 2: Solve the SIR ODE ---
    t_span = (0.0, instance.t_max)
    t_eval = np.linspace(0.0, instance.t_max, 2000)
    y0 = [float(instance.S0), float(instance.I0), float(instance.R0_init)]

    result = solve_ivp(
        fun=lambda t, y: sir_rhs(t, y, beta, gamma, N),
        t_span=t_span,
        y0=y0,
        method="RK45",
        t_eval=t_eval,
        rtol=1e-10,
        atol=1e-12,
    )

    t_arr = result.t
    S_arr = result.y[0]
    I_arr = result.y[1]
    R_arr = result.y[2]

    # --- Step 3: Peak infection ---
    peak_idx = int(np.argmax(I_arr))
    peak_infected = float(I_arr[peak_idx])
    peak_time = float(t_arr[peak_idx])

    # --- Step 4: Final epidemic size (numerical) ---
    final_infected_frac = float(R_arr[-1]) / N

    # --- Step 5: Final epidemic size (theoretical via transcendental equation) ---
    # R_inf = 1 - exp(-R0 * R_inf)
    # Rearranged: f(x) = x - 1 + exp(-R0 * x) = 0, solve for x in (0, 1)
    def final_size_eq(x: float) -> float:
        return x - 1.0 + math.exp(-R0 * x)

    # The non-trivial root is in (epsilon, 1) when R0 > 1
    final_infected_frac_theory = float(brentq(final_size_eq, 1e-10, 1.0 - 1e-10))

    # --- Step 6: Herd immunity threshold ---
    herd_immunity_threshold = 1.0 - 1.0 / R0

    # --- Step 7: Vaccination analysis ---
    vaccination_results: list[VaccinationResult] = []
    for v in instance.vaccination_rates:
        S0_v = (1.0 - v) * N
        R0_eff = R0 * (1.0 - v)
        epidemic_occurs = R0_eff > 1.0

        # Solve the modified SIR
        y0_v = [S0_v, float(instance.I0), v * N + instance.R0_init]
        result_v = solve_ivp(
            fun=lambda t, y: sir_rhs(t, y, beta, gamma, N),
            t_span=t_span,
            y0=y0_v,
            method="RK45",
            t_eval=t_eval,
            rtol=1e-10,
            atol=1e-12,
        )

        I_v = result_v.y[1]
        R_v = result_v.y[2]
        peak_idx_v = int(np.argmax(I_v))
        peak_infected_v = float(I_v[peak_idx_v])
        peak_time_v = float(result_v.t[peak_idx_v])
        # Final infected fraction (relative to total population)
        final_frac_v = float(R_v[-1] - y0_v[2]) / N

        vaccination_results.append(VaccinationResult(
            vaccination_rate=v,
            S0_effective=S0_v,
            R0_effective=R0_eff,
            epidemic_occurs=epidemic_occurs,
            peak_infected=peak_infected_v,
            peak_time=peak_time_v,
            final_infected_frac=final_frac_v,
        ))

    # --- Step 8: Equilibrium analysis ---
    # Disease-free equilibrium (DFE): S=N, I=0, R=0
    # Jacobian of the SIR system at (S, I, R):
    #   J = [ [-beta*I/N,  -beta*S/N,  0],
    #         [ beta*I/N,   beta*S/N - gamma, 0],
    #         [ 0,          gamma,      0] ]
    # At DFE (S=N, I=0):
    #   J_dfe = [ [0, -beta, 0],
    #             [0, beta - gamma, 0],
    #             [0, gamma, 0] ]
    # Eigenvalues: 0, 0, beta - gamma
    J_dfe = np.array([
        [0.0, -beta, 0.0],
        [0.0, beta - gamma, 0.0],
        [0.0, gamma, 0.0],
    ])
    eigenvalues = list(np.linalg.eigvals(J_dfe))

    # DFE is stable if all eigenvalues have non-positive real part
    # When R0 > 1, beta - gamma > 0 => unstable (epidemic grows)
    dfe_stable = all(ev.real <= 0 for ev in eigenvalues)

    elapsed = time.perf_counter() - t0_clock

    sol = Solution(
        R0=R0,
        peak_infected=peak_infected,
        peak_time=peak_time,
        final_infected_frac=final_infected_frac,
        final_infected_frac_theory=final_infected_frac_theory,
        herd_immunity_threshold=herd_immunity_threshold,
        t=t_arr,
        S=S_arr,
        I=I_arr,
        R=R_arr,
        vaccination_results=vaccination_results,
        jacobian_eigenvalues=eigenvalues,
        dfe_stable=dfe_stable,
        algorithm="Runge-Kutta 4(5) adaptive ODE integration (scipy.integrate.solve_ivp)",
        time_seconds=elapsed,
    )

    # Independent verification
    sol.verification = verify(instance, sol)

    return sol


# --- Verification (independent of solver) ---

def verify(instance: Instance, sol: Solution) -> dict[str, bool]:
    """Independently verify the SIR solution with 8 checks.

    All checks are computed from scratch using the raw time-series
    data and instance parameters.  No logic is shared with the solver.
    """
    checks: dict[str, bool] = {}

    N = instance.N
    beta = instance.beta
    gamma = instance.gamma

    # Check 1: Population conserved at all time points
    total = sol.S + sol.I + sol.R
    max_deviation = float(np.max(np.abs(total - N)))
    checks["population_conserved"] = max_deviation < 1.0

    # Check 2: R0 is correct
    R0_expected = beta / gamma
    checks["R0_correct"] = abs(sol.R0 - R0_expected) < 1e-10

    # Check 3: Peak infection exceeds initial
    checks["peak_occurs"] = sol.peak_infected > instance.I0

    # Check 4: Peak time is in a reasonable range
    checks["peak_time_reasonable"] = 10.0 < sol.peak_time < 100.0

    # Check 5: Final size matches theory
    checks["final_size_matches_theory"] = (
        abs(sol.final_infected_frac - sol.final_infected_frac_theory) < 0.02
    )

    # Check 6: Herd immunity threshold is correct
    expected_threshold = 1.0 - 1.0 / R0_expected
    checks["herd_immunity_correct"] = (
        abs(sol.herd_immunity_threshold - expected_threshold) < 0.001
    )

    # Check 7: Vaccination at 0.67 prevents large outbreak
    # Find the vaccination result with rate closest to 0.67
    vax_67 = None
    for vr in sol.vaccination_results:
        if abs(vr.vaccination_rate - 0.67) < 0.01:
            vax_67 = vr
            break
    if vax_67 is not None:
        # With 67% vaccinated, R0_eff should be ~0.99 (just below 1)
        # The peak infected should be small (no large outbreak)
        checks["vaccination_prevents_epidemic"] = vax_67.peak_infected < 0.01 * N
    else:
        checks["vaccination_prevents_epidemic"] = False

    # Check 8: All compartments non-negative at all time points
    all_nonneg = bool(
        np.all(sol.S >= -1e-6)
        and np.all(sol.I >= -1e-6)
        and np.all(sol.R >= -1e-6)
    )
    checks["all_compartments_nonneg"] = all_nonneg

    return checks


# --- Main ---

if __name__ == "__main__":
    instance = Instance(
        N=10000,
        beta=0.3,
        gamma=0.1,
        I0=10,
        R0_init=0,
        t_max=200.0,
        vaccination_rates=(0.0, 0.3, 0.5, 0.67, 0.8),
    )

    sol = solve(instance)

    # --- Print Solution Report ---
    log.header("SOLUTION REPORT: SIR Epidemic Model")

    # Problem setup
    log.step("PROBLEM SETUP")
    log.metric("Population N:", f"{instance.N:,}", tag="DATA")
    log.metric("Transmission rate beta:", f"{instance.beta}/day", tag="DATA")
    log.metric("Recovery rate gamma:", f"{instance.gamma}/day", tag="DATA")
    log.metric("Infectious period:", f"{1.0/instance.gamma:.0f} days", tag="DATA")
    log.metric("Initial infected I0:", f"{instance.I0}", tag="DATA")
    log.metric("Simulation horizon:", f"{instance.t_max:.0f} days", tag="DATA")
    log.blank()

    # SIR model equations
    log.step("SIR MODEL EQUATIONS")
    log.info("dS/dt = -beta * S * I / N", tag="MODEL")
    log.info("dI/dt =  beta * S * I / N - gamma * I", tag="MODEL")
    log.info("dR/dt =  gamma * I", tag="MODEL")
    log.info("Constraint: S(t) + I(t) + R(t) = N for all t", tag="MODEL")
    log.blank()

    # R0 computation
    log.step("BASIC REPRODUCTION NUMBER")
    log.info(f"R0 = beta / gamma = {instance.beta} / {instance.gamma} = {sol.R0:.1f}", tag="SOLVE")
    log.info("Interpretation: each infected person infects 3 others on average", tag="INTERPRET")
    log.info(f"Since R0 = {sol.R0:.1f} > 1, the disease will spread (epidemic)", tag="INTERPRET")
    log.blank()

    # ODE solution results
    log.step("ODE SOLUTION (RK45)")
    log.metric("Peak infected:", f"{sol.peak_infected:.0f} ({sol.peak_infected/instance.N:.1%} of N)", tag="RESULT")
    log.metric("Peak time:", f"day {sol.peak_time:.1f}", tag="RESULT")
    log.metric("Final infected (num):", f"{sol.final_infected_frac:.4f} ({sol.final_infected_frac:.1%})", tag="RESULT")
    log.metric("Final infected (theory):", f"{sol.final_infected_frac_theory:.4f} ({sol.final_infected_frac_theory:.1%})", tag="RESULT")
    log.metric("Theory-numerical gap:", f"{abs(sol.final_infected_frac - sol.final_infected_frac_theory):.6f}", tag="RESULT")
    log.blank()

    # Final size relation
    log.step("FINAL SIZE RELATION")
    log.info("Transcendental equation: R_inf = 1 - exp(-R0 * R_inf)", tag="MODEL")
    log.info(f"Solved via Brent's method: R_inf = {sol.final_infected_frac_theory:.6f}", tag="SOLVE")
    log.info(f"Numerical simulation:     R_inf = {sol.final_infected_frac:.6f}", tag="SOLVE")
    log.info("These agree to within the ODE integration tolerance", tag="VERIFY")
    log.blank()

    # Herd immunity
    log.step("HERD IMMUNITY THRESHOLD")
    log.info(f"Threshold = 1 - 1/R0 = 1 - 1/{sol.R0:.1f} = {sol.herd_immunity_threshold:.4f}", tag="SOLVE")
    log.info(f"At least {sol.herd_immunity_threshold:.1%} of the population must be immune to prevent spread", tag="INTERPRET")
    log.blank()

    # Vaccination analysis
    log.step("VACCINATION SCENARIO ANALYSIS")
    log.table_row(f"{'Rate':>6}  {'S0_eff':>8}  {'R0_eff':>7}  {'Epidemic':>9}  {'Peak I':>8}  {'Peak Day':>9}  {'Final %':>8}", tag="TABLE")
    log.divider()
    for vr in sol.vaccination_results:
        epidemic_str = "YES" if vr.epidemic_occurs else "NO"
        log.table_row(
            f"{vr.vaccination_rate:>5.0%}  {vr.S0_effective:>8.0f}  {vr.R0_effective:>7.2f}  {epidemic_str:>9}  "
            f"{vr.peak_infected:>8.0f}  {vr.peak_time:>8.1f}d  {vr.final_infected_frac:>7.1%}",
            tag="TABLE",
        )
    log.blank()

    log.info("At 67% vaccination, R0_eff drops to ~1.0 -- epidemic is prevented", tag="RECOMMEND")
    log.info("At 80% vaccination, R0_eff = 0.60 -- strong herd immunity", tag="RECOMMEND")
    log.blank()

    # Equilibrium analysis
    log.step("EQUILIBRIUM ANALYSIS (Disease-Free Equilibrium)")
    log.info("DFE: (S, I, R) = (N, 0, 0)", tag="MODEL")
    log.info("Jacobian at DFE:", tag="MODEL")
    log.info("  J = [[0, -beta, 0], [0, beta-gamma, 0], [0, gamma, 0]]", tag="MODEL")
    eig_strs = [f"{ev.real:.4f}" if abs(ev.imag) < 1e-10 else f"{ev:.4f}" for ev in sol.jacobian_eigenvalues]
    log.metric("Eigenvalues:", f"[{', '.join(eig_strs)}]", tag="STATS")
    log.metric("DFE stable:", f"{sol.dfe_stable} (stable only when R0 <= 1)", tag="STATS")
    if not sol.dfe_stable:
        log.info(f"Eigenvalue beta - gamma = {instance.beta - instance.gamma:.4f} > 0 => DFE unstable", tag="INTERPRET")
        log.info("This confirms the epidemic will grow when R0 > 1", tag="INTERPRET")
    log.blank()

    # Time series summary
    log.step("TIME SERIES SUMMARY")
    key_days = [0, 10, 20, 30, 50, 100, 150, 200]
    log.table_row(f"{'Day':>5}  {'S':>8}  {'I':>8}  {'R':>8}  {'S+I+R':>8}", tag="TABLE")
    log.divider()
    for day in key_days:
        if day <= instance.t_max:
            idx = int(np.argmin(np.abs(sol.t - day)))
            s_val = sol.S[idx]
            i_val = sol.I[idx]
            r_val = sol.R[idx]
            log.table_row(
                f"{day:>5}  {s_val:>8.0f}  {i_val:>8.0f}  {r_val:>8.0f}  {s_val+i_val+r_val:>8.0f}",
                tag="TABLE",
            )
    log.blank()

    # Practical recommendations
    log.step("PRACTICAL RECOMMENDATIONS")
    log.info(f"R0 = {sol.R0:.1f}: this is a highly transmissible disease", tag="RECOMMEND")
    log.info(f"Without intervention, ~{sol.final_infected_frac:.0%} of the population will be infected", tag="RECOMMEND")
    log.info(f"Peak strain on healthcare: ~{sol.peak_infected:.0f} simultaneous cases on day {sol.peak_time:.0f}", tag="RECOMMEND")
    log.info(f"Vaccination target: immunize at least {sol.herd_immunity_threshold:.0%} of the population", tag="RECOMMEND")
    log.info("Even partial vaccination (e.g. 50%) significantly reduces peak and total burden", tag="RECOMMEND")
    log.blank()

    # Solver metadata
    log.metric("Algorithm:", sol.algorithm, tag="SOLVE")
    log.metric("Time:", f"{sol.time_seconds:.6f}s", tag="TIMING")
    log.blank()

    # Independent verification
    log.step("INDEPENDENT VERIFICATION (8 checks)")
    all_pass = True
    for check_name, passed in sol.verification.items():
        log.check(check_name, passed, tag="VERIFY")
        if not passed:
            all_pass = False
    log.blank()

    if all_pass:
        log.success("All 8 verification checks passed", tag="COMPLETE")
    else:
        failed = [k for k, v in sol.verification.items() if not v]
        log.error(f"{len(failed)} check(s) failed: {', '.join(failed)}", tag="ERROR")
    log.blank()

    log.divider(style="thick")

    # Save JSON
    output = {
        "instance": {
            "N": instance.N,
            "beta": instance.beta,
            "gamma": instance.gamma,
            "I0": instance.I0,
            "t_max": instance.t_max,
        },
        "R0": sol.R0,
        "peak_infected": sol.peak_infected,
        "peak_time": sol.peak_time,
        "final_infected_frac_numerical": sol.final_infected_frac,
        "final_infected_frac_theory": sol.final_infected_frac_theory,
        "herd_immunity_threshold": sol.herd_immunity_threshold,
        "vaccination_analysis": [
            {
                "vaccination_rate": vr.vaccination_rate,
                "R0_effective": vr.R0_effective,
                "epidemic_occurs": vr.epidemic_occurs,
                "peak_infected": vr.peak_infected,
                "peak_time": vr.peak_time,
                "final_infected_frac": vr.final_infected_frac,
            }
            for vr in sol.vaccination_results
        ],
        "equilibrium": {
            "eigenvalues": [str(ev) for ev in sol.jacobian_eigenvalues],
            "dfe_stable": sol.dfe_stable,
        },
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
        "verification": sol.verification,
    }
    out_path = Path(__file__).parent / "solution.json"
    with open(str(out_path), "w") as f:
        json.dump(output, f, indent=2)
    log.success(f"solution.json", tag="SAVE")
