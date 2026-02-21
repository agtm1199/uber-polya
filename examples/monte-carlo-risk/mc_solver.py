#!/usr/bin/env python3
"""Monte Carlo Project Risk Analysis solver.

Estimates project completion time under uncertainty using Monte Carlo
simulation with triangular duration distributions and dependency-aware
scheduling.

Phases 1-3 are sequential; phases 4-5 run in parallel after phase 3.
Total duration = Phase1 + Phase2 + Phase3 + max(Phase4, Phase5).

Analysis includes:
  1. Monte Carlo simulation (100,000 runs)
  2. Risk metrics: mean, CI, VaR95, CVaR95, P(finish <= deadline)
  3. Convergence analysis across sample sizes
  4. Sensitivity analysis via correlation
  5. Analytical cross-check using E[triangular] = (min+mode+max)/3

Verification: 10 independent checks on solution consistency.
"""
from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger

log = PolyaLogger()


# --- Data Model ---

@dataclass(frozen=True)
class Instance:
    """Monte Carlo project risk simulation instance.

    Each phase is a tuple: (name, min_days, mode_days, max_days, dependencies).
    Dependencies is a tuple of phase indices that must complete before this
    phase can start.
    """
    phases: tuple[tuple[str, float, float, float, tuple[int, ...]], ...]
    n_simulations: int = 100_000
    deadline: float = 50.0
    seed: int = 42


@dataclass
class Solution:
    """Monte Carlo risk analysis solution with all results."""
    # Core statistics
    mean_duration: float = 0.0
    std_duration: float = 0.0
    median_duration: float = 0.0
    ci_low: float = 0.0
    ci_high: float = 0.0

    # Risk metrics
    prob_finish_by_deadline: float = 0.0
    var95: float = 0.0
    cvar95: float = 0.0
    deadline: float = 0.0

    # Convergence analysis
    convergence_ns: list[int] = field(default_factory=list)
    convergence_means: list[float] = field(default_factory=list)

    # Sensitivity analysis
    phase_names: list[str] = field(default_factory=list)
    phase_correlations: list[float] = field(default_factory=list)
    critical_risk_driver: str = ""

    # Analytical cross-check
    analytical_mean: float = 0.0

    # Raw durations (not serialized to JSON -- too large)
    all_durations: np.ndarray = field(default_factory=lambda: np.array([]))

    # Per-phase sampled durations for sensitivity (n_simulations x n_phases)
    phase_durations: np.ndarray = field(default_factory=lambda: np.array([]))

    # Metadata
    algorithm: str = ""
    time_seconds: float = 0.0
    n_simulations: int = 0

    # Verification
    verification: dict = field(default_factory=dict)


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Run Monte Carlo simulation for project risk analysis."""
    t0 = time.perf_counter()
    np.random.seed(instance.seed)

    sol = Solution()
    sol.deadline = instance.deadline
    sol.n_simulations = instance.n_simulations

    n_phases = len(instance.phases)
    n_sim = instance.n_simulations

    # --- 1. Monte Carlo Simulation ---
    # Sample all phase durations at once: shape (n_sim, n_phases)
    phase_samples = np.zeros((n_sim, n_phases))
    for j, (name, lo, mode, hi, deps) in enumerate(instance.phases):
        phase_samples[:, j] = np.random.triangular(lo, mode, hi, size=n_sim)

    # Compute total project duration respecting dependencies.
    # For each simulation, compute finish times using topological order.
    # Phase finish time = phase start time + phase duration.
    # Phase start time = max(finish times of all dependencies), or 0 if none.
    finish_times = np.zeros((n_sim, n_phases))
    for j, (name, lo, mode, hi, deps) in enumerate(instance.phases):
        if len(deps) == 0:
            start = np.zeros(n_sim)
        else:
            start = np.max(finish_times[:, list(deps)], axis=1)
        finish_times[:, j] = start + phase_samples[:, j]

    # Total project duration = max finish time across all phases
    total_durations = np.max(finish_times, axis=1)

    sol.all_durations = total_durations
    sol.phase_durations = phase_samples

    # --- 2. Core Statistics ---
    sol.mean_duration = float(np.mean(total_durations))
    sol.std_duration = float(np.std(total_durations, ddof=1))
    sol.median_duration = float(np.median(total_durations))

    # 95% CI for the mean using CLT: mean +/- 1.96 * SE
    se = sol.std_duration / float(np.sqrt(n_sim))
    sol.ci_low = float(sol.mean_duration - 1.96 * se)
    sol.ci_high = float(sol.mean_duration + 1.96 * se)

    # --- 3. Risk Metrics ---
    sol.prob_finish_by_deadline = float(np.mean(total_durations <= instance.deadline))
    sol.var95 = float(np.percentile(total_durations, 95))

    # CVaR95: expected duration in the tail beyond VaR95
    tail_mask = total_durations >= sol.var95
    sol.cvar95 = float(np.mean(total_durations[tail_mask]))

    # --- 4. Convergence Analysis ---
    checkpoints = [100, 500, 1_000, 5_000, 10_000, 50_000, 100_000]
    # Filter to valid checkpoints (<= n_sim)
    checkpoints = [n for n in checkpoints if n <= n_sim]
    sol.convergence_ns = checkpoints
    sol.convergence_means = [float(np.mean(total_durations[:n])) for n in checkpoints]

    # --- 5. Sensitivity Analysis ---
    # Correlation between each phase's sampled duration and total project duration
    sol.phase_names = [p[0] for p in instance.phases]
    sol.phase_correlations = []
    for j in range(n_phases):
        corr, _ = stats.pearsonr(phase_samples[:, j], total_durations)
        sol.phase_correlations.append(float(corr))

    max_corr_idx = int(np.argmax(sol.phase_correlations))
    sol.critical_risk_driver = sol.phase_names[max_corr_idx]

    # --- 6. Analytical Cross-Check ---
    # E[triangular(a, c, b)] = (a + c + b) / 3 for each phase.
    # Compute expected critical path analytically.
    phase_means = [(lo + mode + hi) / 3.0 for (_, lo, mode, hi, _) in instance.phases]

    # Compute analytical finish times (deterministic with expected durations)
    analytical_finish = [0.0] * n_phases
    for j, (name, lo, mode, hi, deps) in enumerate(instance.phases):
        if len(deps) == 0:
            start = 0.0
        else:
            start = max(analytical_finish[d] for d in deps)
        analytical_finish[j] = start + phase_means[j]

    sol.analytical_mean = max(analytical_finish)

    # Metadata
    sol.algorithm = "Monte Carlo simulation with triangular distributions"
    sol.time_seconds = time.perf_counter() - t0

    # Verification
    sol.verification = verify(instance, sol)

    return sol


# --- Verification (independent of solver) ---

def verify(instance: Instance, sol: Solution) -> dict:
    """Independently verify Monte Carlo solution correctness.

    Ten checks that do not share logic with the solver:
      1. mean_reasonable: 25 < mean < 50
      2. std_positive: std > 0
      3. ci_contains_mean: CI_low < mean < CI_high
      4. var95_gt_mean: VaR95 > mean
      5. cvar95_ge_var95: CVaR95 >= VaR95
      6. prob_deadline_between_0_1: 0 < P(<=50) < 1
      7. convergence_stabilizes: |last - second_last| < 0.5
      8. analytical_close: |mean_MC - mean_analytical| < 1.0
      9. sensitivity_sums_reasonable: all correlations in (0, 1)
     10. simulation_count_correct: len(durations) == N
    """
    checks: dict = {}

    # 1. Mean is in a reasonable range for this problem
    checks["mean_reasonable"] = bool(25.0 < sol.mean_duration < 50.0)

    # 2. Standard deviation is positive
    checks["std_positive"] = bool(sol.std_duration > 0.0)

    # 3. Confidence interval contains the mean
    checks["ci_contains_mean"] = bool(sol.ci_low < sol.mean_duration < sol.ci_high)

    # 4. VaR95 exceeds the mean (right tail is above average)
    checks["var95_gt_mean"] = bool(sol.var95 > sol.mean_duration)

    # 5. CVaR95 >= VaR95 (conditional tail mean is at least as large as the threshold)
    checks["cvar95_ge_var95"] = bool(sol.cvar95 >= sol.var95)

    # 6. Probability of finishing by deadline is strictly between 0 and 1
    checks["prob_deadline_between_0_1"] = bool(0.0 < sol.prob_finish_by_deadline < 1.0)

    # 7. Convergence stabilizes: last two checkpoints differ by < 0.5 days
    if len(sol.convergence_means) >= 2:
        last_diff = abs(sol.convergence_means[-1] - sol.convergence_means[-2])
        checks["convergence_stabilizes"] = bool(last_diff < 0.5)
    else:
        checks["convergence_stabilizes"] = False

    # 8. MC mean is close to analytical expected value (within 1 day)
    checks["analytical_close"] = bool(abs(sol.mean_duration - sol.analytical_mean) < 1.0)

    # 9. All sensitivity correlations are between 0 and 1 (positive correlations expected)
    checks["sensitivity_sums_reasonable"] = bool(all(
        0.0 < c < 1.0 for c in sol.phase_correlations
    ))

    # 10. Simulation count matches requested count
    checks["simulation_count_correct"] = bool(len(sol.all_durations) == instance.n_simulations)

    # Overall
    checks["all_passed"] = all(
        v for v in checks.values() if isinstance(v, bool)
    )

    return checks


# --- Main ---

if __name__ == "__main__":
    # Define the 5-phase project instance
    instance = Instance(
        phases=(
            ("Phase 1",  5.0,  8.0, 14.0, ()),        # no dependencies
            ("Phase 2",  3.0,  5.0, 10.0, (0,)),      # depends on Phase 1
            ("Phase 3",  7.0, 10.0, 18.0, (1,)),      # depends on Phase 2
            ("Phase 4",  4.0,  6.0, 12.0, (2,)),      # depends on Phase 3
            ("Phase 5",  6.0,  9.0, 15.0, (2,)),      # depends on Phase 3
        ),
        n_simulations=100_000,
        deadline=50.0,
        seed=42,
    )

    sol = solve(instance)

    # --- Print Solution Report ---
    log.header("MONTE CARLO PROJECT RISK ANALYSIS")

    log.section("PHASE 1-2: UNDERSTAND & PLAN (uber-model)")
    log.info("Problem: Estimate project duration under uncertain phase times", tag="MODEL")
    log.info("Structure: Dependency graph with triangular distributions", tag="MODEL")
    log.info("Method: Monte Carlo simulation (N={:,})".format(sol.n_simulations), tag="SOLVE")
    log.blank()

    log.step("INSTANCE")
    log.metric("Phases", str(len(instance.phases)), tag="DATA")
    for name, lo, mode, hi, deps in instance.phases:
        dep_str = ", ".join("Phase {}".format(d + 1) for d in deps) if deps else "None"
        log.metric(name, "Tri({}, {}, {})  deps=[{}]".format(lo, mode, hi, dep_str), tag="DATA")
    log.metric("Deadline", "{:.0f} days".format(instance.deadline), tag="DATA")
    log.metric("Simulations", "{:,}".format(instance.n_simulations), tag="DATA")
    log.metric("Seed", str(instance.seed), tag="DATA")
    log.blank()

    log.section("PHASE 3: EXECUTE (uber-solve)")

    log.step("STEP 1: Duration Statistics")
    log.metric("Mean duration", "{:.2f} days".format(sol.mean_duration), tag="STATS")
    log.metric("Std deviation", "{:.2f} days".format(sol.std_duration), tag="STATS")
    log.metric("Median duration", "{:.2f} days".format(sol.median_duration), tag="STATS")
    log.metric("95% CI (mean)", "[{:.2f}, {:.2f}] days".format(sol.ci_low, sol.ci_high), tag="STATS")
    log.blank()

    log.step("STEP 2: Risk Metrics")
    log.metric("P(finish <= {} d)".format(int(sol.deadline)),
               "{:.2%}".format(sol.prob_finish_by_deadline), tag="STATS")
    log.metric("VaR95 (95th pctl)", "{:.2f} days".format(sol.var95), tag="STATS")
    log.metric("CVaR95 (tail mean)", "{:.2f} days".format(sol.cvar95), tag="STATS")
    log.blank()

    log.step("STEP 3: Convergence Analysis")
    for n, m in zip(sol.convergence_ns, sol.convergence_means):
        log.metric("N={:>7,}".format(n), "mean = {:.3f} days".format(m), tag="STATS")
    if len(sol.convergence_means) >= 2:
        delta = abs(sol.convergence_means[-1] - sol.convergence_means[-2])
        log.info("Final convergence delta: {:.4f} days".format(delta), tag="VERIFY")
    log.blank()

    log.step("STEP 4: Sensitivity Analysis (correlation with total duration)")
    for name, corr in sorted(zip(sol.phase_names, sol.phase_correlations),
                              key=lambda x: -x[1]):
        log.bar(
            "{:10s} r={:.3f}".format(name, corr),
            corr,
            max_width=30,
            tag="SENSITIVITY",
            marker="  <-- critical" if name == sol.critical_risk_driver else "",
        )
    log.info("Critical risk driver: {}".format(sol.critical_risk_driver), tag="RESULT")
    log.blank()

    log.step("STEP 5: Analytical Cross-Check")
    log.metric("Analytical E[T]", "{:.2f} days".format(sol.analytical_mean), tag="STATS")
    log.metric("MC mean", "{:.2f} days".format(sol.mean_duration), tag="STATS")
    log.metric("Difference", "{:.3f} days".format(
        abs(sol.mean_duration - sol.analytical_mean)), tag="VERIFY")
    log.blank()

    log.section("PHASE 4: LOOK BACK (uber-interpret)")

    log.step("BOTTOM LINE")
    log.success("Expected project duration: {:.1f} days (95% CI: [{:.1f}, {:.1f}])".format(
        sol.mean_duration, sol.ci_low, sol.ci_high), tag="RESULT")
    log.success("Probability of finishing within {:.0f} days: {:.1%}".format(
        sol.deadline, sol.prob_finish_by_deadline), tag="RESULT")
    log.success("Worst-case (VaR95): {:.1f} days".format(sol.var95), tag="RESULT")
    log.success("Tail risk (CVaR95): {:.1f} days".format(sol.cvar95), tag="RESULT")
    log.success("Critical risk driver: {} (r={:.3f})".format(
        sol.critical_risk_driver,
        max(sol.phase_correlations)), tag="RESULT")
    log.blank()

    log.step("RECOMMENDATIONS")
    log.success("1. Plan for ~{:.0f} days with buffer to {:.0f} days (VaR95)".format(
        sol.mean_duration, sol.var95), tag="RECOMMEND")
    log.success("2. Focus risk mitigation on {} (highest variance contribution)".format(
        sol.critical_risk_driver), tag="RECOMMEND")
    log.success("3. P(on-time) = {:.0%} -- {:.0%} confidence of meeting {:.0f}-day deadline".format(
        sol.prob_finish_by_deadline, sol.prob_finish_by_deadline, sol.deadline), tag="RECOMMEND")
    log.success("4. If deadline is hard, consider crashing the critical risk driver phase", tag="RECOMMEND")
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
    log.divider(style="thick")

    # Save JSON (exclude large arrays)
    output = {
        "instance": {
            "phases": [
                {
                    "name": name,
                    "min": lo,
                    "mode": mode,
                    "max": hi,
                    "dependencies": list(deps),
                }
                for name, lo, mode, hi, deps in instance.phases
            ],
            "n_simulations": instance.n_simulations,
            "deadline": instance.deadline,
            "seed": instance.seed,
        },
        "statistics": {
            "mean_duration": sol.mean_duration,
            "std_duration": sol.std_duration,
            "median_duration": sol.median_duration,
            "ci_95_low": sol.ci_low,
            "ci_95_high": sol.ci_high,
        },
        "risk_metrics": {
            "prob_finish_by_deadline": sol.prob_finish_by_deadline,
            "var95": sol.var95,
            "cvar95": sol.cvar95,
            "deadline": sol.deadline,
        },
        "convergence": {
            "sample_sizes": sol.convergence_ns,
            "running_means": sol.convergence_means,
        },
        "sensitivity": {
            "phase_names": sol.phase_names,
            "correlations": sol.phase_correlations,
            "critical_risk_driver": sol.critical_risk_driver,
        },
        "analytical_crosscheck": {
            "analytical_mean": sol.analytical_mean,
            "mc_mean": sol.mean_duration,
            "difference": abs(sol.mean_duration - sol.analytical_mean),
        },
        "verification": sol.verification,
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
    }

    out_path = Path(__file__).resolve().parent / "solution.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    log.success("Solution data saved to: {}".format(out_path.name), tag="SAVE")
    log.divider(style="thick")
