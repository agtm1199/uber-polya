#!/usr/bin/env python3
"""A/B Test solver.

Solves a two-proportion comparison using:
  1. Two-proportion z-test (frequentist)
  2. Bayesian Beta-Binomial model
  3. Bootstrap confidence interval for the difference

Verification: Fisher's exact test + chi-squared cross-validation.
"""
from __future__ import annotations

import json
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
    """A/B test instance."""
    n_a: int           # visitors in group A (control)
    conv_a: int        # conversions in group A
    n_b: int           # visitors in group B (treatment)
    conv_b: int        # conversions in group B
    alpha: float = 0.05
    alternative: str = "two-sided"  # "two-sided", "larger", "smaller"
    prior_alpha: float = 1.0  # Beta prior parameter (1 = uniform)
    prior_beta: float = 1.0

    @property
    def rate_a(self) -> float:
        return self.conv_a / self.n_a

    @property
    def rate_b(self) -> float:
        return self.conv_b / self.n_b


@dataclass
class Solution:
    """Verified A/B test solution with metadata."""
    # Frequentist results
    z_statistic: float
    p_value: float
    rate_a: float
    rate_b: float
    absolute_lift: float
    relative_lift: float
    ci_diff: tuple[float, float]
    effect_size_h: float  # Cohen's h

    # Bayesian results
    prob_b_better: float
    expected_lift_bayesian: float
    bayesian_ci_lift: tuple[float, float]
    credible_interval_a: tuple[float, float]
    credible_interval_b: tuple[float, float]

    # Bootstrap results
    bootstrap_ci_diff: tuple[float, float]

    # Power analysis
    power: float
    n_per_group_for_80pct: int

    # Metadata
    is_significant: bool
    algorithm: str
    time_seconds: float
    recommendation: str

    # Verification
    verification: dict = field(default_factory=dict)

    # Sensitivity
    sensitivity: dict = field(default_factory=dict)


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Solve A/B test with frequentist + Bayesian + bootstrap analysis."""
    t0 = time.perf_counter()
    rng = np.random.default_rng(42)

    rate_a = instance.rate_a
    rate_b = instance.rate_b
    absolute_lift = rate_b - rate_a
    relative_lift = absolute_lift / rate_a if rate_a > 0 else float("inf")

    # --- 1. Two-proportion z-test ---
    from statsmodels.stats.proportion import proportions_ztest, proportion_confint

    z_stat, p_value = proportions_ztest(
        [instance.conv_b, instance.conv_a],
        [instance.n_b, instance.n_a],
        alternative=instance.alternative,
    )

    # CI for the difference in proportions (Wald method)
    se_diff = np.sqrt(
        rate_a * (1 - rate_a) / instance.n_a
        + rate_b * (1 - rate_b) / instance.n_b
    )
    z_crit = stats.norm.ppf(1 - instance.alpha / 2)
    ci_diff = (absolute_lift - z_crit * se_diff, absolute_lift + z_crit * se_diff)

    # Cohen's h effect size
    effect_size_h = 2 * (np.arcsin(np.sqrt(rate_b)) - np.arcsin(np.sqrt(rate_a)))

    is_significant = p_value < instance.alpha

    # --- 2. Bayesian Beta-Binomial ---
    post_a = stats.beta(
        instance.prior_alpha + instance.conv_a,
        instance.prior_beta + instance.n_a - instance.conv_a,
    )
    post_b = stats.beta(
        instance.prior_alpha + instance.conv_b,
        instance.prior_beta + instance.n_b - instance.conv_b,
    )

    n_mc = 100_000
    samples_a = post_a.rvs(n_mc, random_state=rng)
    samples_b = post_b.rvs(n_mc, random_state=rng)
    prob_b_better = float(np.mean(samples_b > samples_a))
    lift_samples = samples_b - samples_a
    expected_lift_bayesian = float(np.mean(lift_samples))
    bayesian_ci_lift = (
        float(np.percentile(lift_samples, 2.5)),
        float(np.percentile(lift_samples, 97.5)),
    )
    credible_interval_a = post_a.interval(1 - instance.alpha)
    credible_interval_b = post_b.interval(1 - instance.alpha)

    # --- 3. Bootstrap CI for difference ---
    n_boot = 10_000
    boot_diffs = []
    for _ in range(n_boot):
        boot_a = rng.binomial(instance.n_a, rate_a) / instance.n_a
        boot_b = rng.binomial(instance.n_b, rate_b) / instance.n_b
        boot_diffs.append(boot_b - boot_a)
    boot_diffs = np.array(boot_diffs)
    bootstrap_ci_diff = (
        float(np.percentile(boot_diffs, 2.5)),
        float(np.percentile(boot_diffs, 97.5)),
    )

    # --- 4. Power analysis ---
    from statsmodels.stats.power import NormalIndPower

    power_analysis = NormalIndPower()
    observed_power = power_analysis.solve_power(
        effect_size=abs(effect_size_h),
        nobs1=instance.n_a,
        alpha=instance.alpha,
        ratio=instance.n_b / instance.n_a,
    )

    if abs(effect_size_h) > 0.001:
        n_needed = power_analysis.solve_power(
            effect_size=abs(effect_size_h),
            alpha=instance.alpha,
            power=0.8,
            ratio=1.0,
        )
        n_per_group_80 = int(np.ceil(n_needed))
    else:
        n_per_group_80 = -1  # undefined for zero effect

    # --- Recommendation ---
    if is_significant and abs(effect_size_h) >= 0.2:
        recommendation = "SHIP: Statistically significant with meaningful effect size."
    elif is_significant and abs(effect_size_h) < 0.2:
        recommendation = "CAUTIOUS: Statistically significant but small effect. Consider practical impact."
    elif not is_significant and observed_power < 0.8:
        recommendation = "UNDERPOWERED: Not significant, but test lacked power. Collect more data."
    else:
        recommendation = "NO EFFECT: Not significant with adequate power. No meaningful difference."

    elapsed = time.perf_counter() - t0

    sol = Solution(
        z_statistic=float(z_stat),
        p_value=float(p_value),
        rate_a=rate_a,
        rate_b=rate_b,
        absolute_lift=absolute_lift,
        relative_lift=relative_lift,
        ci_diff=ci_diff,
        effect_size_h=float(effect_size_h),
        prob_b_better=prob_b_better,
        expected_lift_bayesian=expected_lift_bayesian,
        bayesian_ci_lift=bayesian_ci_lift,
        credible_interval_a=credible_interval_a,
        credible_interval_b=credible_interval_b,
        bootstrap_ci_diff=bootstrap_ci_diff,
        power=float(observed_power),
        n_per_group_for_80pct=n_per_group_80,
        is_significant=is_significant,
        algorithm="Two-proportion z-test + Bayesian Beta-Binomial + Bootstrap",
        time_seconds=elapsed,
        recommendation=recommendation,
    )

    # Independent verification
    sol.verification = verify(instance, sol)

    # Sensitivity analysis
    sol.sensitivity = sensitivity_analysis(instance)

    return sol


# --- Verification (independent of solver) ---

def verify(instance: Instance, sol: Solution) -> dict:
    """Independently verify using Fisher's exact + chi-squared."""
    checks: dict = {}

    # Check 1: Fisher's exact test (independent method)
    table = np.array([
        [instance.conv_a, instance.n_a - instance.conv_a],
        [instance.conv_b, instance.n_b - instance.conv_b],
    ])
    _, p_fisher = stats.fisher_exact(table, alternative=instance.alternative)
    checks["fisher_exact_p"] = float(p_fisher)
    checks["fisher_agrees"] = (p_fisher < instance.alpha) == sol.is_significant

    # Check 2: Chi-squared test (another independent method)
    chi2, p_chi2, _, _ = stats.chi2_contingency(table, correction=True)
    checks["chi2_statistic"] = float(chi2)
    checks["chi2_p"] = float(p_chi2)
    checks["chi2_agrees"] = (p_chi2 < instance.alpha) == sol.is_significant

    # Check 3: Recompute rates
    checks["rate_a_correct"] = abs(sol.rate_a - instance.conv_a / instance.n_a) < 1e-10
    checks["rate_b_correct"] = abs(sol.rate_b - instance.conv_b / instance.n_b) < 1e-10

    # Check 4: Bayesian sanity (prob_b_better should agree with direction of z-test)
    if sol.z_statistic > 0:
        checks["bayesian_direction_agrees"] = sol.prob_b_better > 0.5
    else:
        checks["bayesian_direction_agrees"] = sol.prob_b_better <= 0.5

    # Overall
    checks["all_methods_agree"] = all([
        checks["fisher_agrees"],
        checks["chi2_agrees"],
        checks["rate_a_correct"],
        checks["rate_b_correct"],
        checks["bayesian_direction_agrees"],
    ])

    return checks


# --- Sensitivity Analysis ---

def sensitivity_analysis(instance: Instance) -> dict:
    """What-if scenarios for the A/B test."""
    from statsmodels.stats.proportion import proportions_ztest
    from statsmodels.stats.power import NormalIndPower

    results = {}
    rate_a = instance.rate_a
    rate_b = instance.rate_b
    effect_h = 2 * (np.arcsin(np.sqrt(rate_b)) - np.arcsin(np.sqrt(rate_a)))

    # Scenario 1: What if sample size doubles?
    _, p_2x = proportions_ztest(
        [instance.conv_b * 2, instance.conv_a * 2],
        [instance.n_b * 2, instance.n_a * 2],
    )
    power_2x = NormalIndPower().solve_power(
        effect_size=abs(effect_h), nobs1=instance.n_a * 2,
        alpha=instance.alpha, ratio=1.0,
    )
    results["double_sample_size"] = {
        "p_value": float(p_2x),
        "power": float(power_2x),
        "significant": bool(p_2x < instance.alpha),
    }

    # Scenario 2: What if the effect is half as large?
    half_rate_b = rate_a + (rate_b - rate_a) / 2
    half_h = 2 * (np.arcsin(np.sqrt(half_rate_b)) - np.arcsin(np.sqrt(rate_a)))
    if abs(half_h) > 0.001:
        n_half = NormalIndPower().solve_power(
            effect_size=abs(half_h), alpha=instance.alpha, power=0.8, ratio=1.0,
        )
        results["half_effect"] = {
            "hypothetical_rate_b": float(half_rate_b),
            "n_per_group_needed": int(np.ceil(n_half)),
        }

    # Scenario 3: Power at various sample sizes
    power_curve = {}
    for n in [100, 250, 500, 1000, 2000, 5000, 10000]:
        if abs(effect_h) > 0.001:
            pwr = NormalIndPower().solve_power(
                effect_size=abs(effect_h), nobs1=n, alpha=instance.alpha, ratio=1.0,
            )
            power_curve[n] = round(float(pwr), 3)
    results["power_curve"] = power_curve

    return results


# --- Main ---

if __name__ == "__main__":
    # Example: Website checkout flow A/B test
    instance = Instance(
        n_a=1500,       # 1500 visitors saw the old checkout (control)
        conv_a=60,      # 60 completed purchase
        n_b=1500,       # 1500 visitors saw the new checkout (treatment)
        conv_b=85,      # 85 completed purchase
        alpha=0.05,
        alternative="two-sided",
    )

    sol = solve(instance)

    # --- Print Solution Report ---
    log.header("A/B TEST SOLUTION REPORT")

    log.step("INSTANCE")
    log.metric("Control (A)", "{:,} visitors, {:,} conversions ({:.2%})".format(
        instance.n_a, instance.conv_a, instance.rate_a), tag="DATA")
    log.metric("Treatment (B)", "{:,} visitors, {:,} conversions ({:.2%})".format(
        instance.n_b, instance.conv_b, instance.rate_b), tag="DATA")
    log.blank()

    log.step("FREQUENTIST ANALYSIS")
    log.metric("Z-statistic", "{:.3f}".format(sol.z_statistic), tag="STATS")
    log.metric("P-value", "{:.6f}".format(sol.p_value), tag="STATS")
    log.metric("Significant", "{} (alpha={})".format(sol.is_significant, instance.alpha), tag="HYPOTHESIS")
    log.metric("Absolute lift", "{:+.2%}".format(sol.absolute_lift), tag="STATS")
    log.metric("Relative lift", "{:+.1%}".format(sol.relative_lift), tag="STATS")
    log.metric("95% CI (diff)", "[{:.4f}, {:.4f}]".format(*sol.ci_diff), tag="STATS")
    log.metric("Cohen's h", "{:.3f} ({})".format(
        sol.effect_size_h,
        "small" if abs(sol.effect_size_h) < 0.3 else "medium" if abs(sol.effect_size_h) < 0.5 else "large"
    ), tag="STATS")
    log.metric("Power", "{:.1%}".format(sol.power), tag="POWER")
    log.blank()

    log.step("BAYESIAN ANALYSIS")
    log.metric("P(B > A)", "{:.1%}".format(sol.prob_b_better), tag="BAYESIAN")
    log.metric("Expected lift", "{:+.4f}".format(sol.expected_lift_bayesian), tag="BAYESIAN")
    log.metric("95% CrI (lift)", "[{:.4f}, {:.4f}]".format(*sol.bayesian_ci_lift), tag="BAYESIAN")
    log.metric("CrI A", "[{:.4f}, {:.4f}]".format(*sol.credible_interval_a), tag="BAYESIAN")
    log.metric("CrI B", "[{:.4f}, {:.4f}]".format(*sol.credible_interval_b), tag="BAYESIAN")
    log.blank()

    log.step("BOOTSTRAP ANALYSIS")
    log.metric("95% CI (diff)", "[{:.4f}, {:.4f}]".format(*sol.bootstrap_ci_diff), tag="STATS")
    log.blank()

    log.step("POWER ANALYSIS")
    log.metric("Observed power", "{:.1%}".format(sol.power), tag="POWER")
    log.metric("N per group for 80% power", "{:,}".format(sol.n_per_group_for_80pct), tag="POWER")
    log.blank()

    log.step("RECOMMENDATION")
    log.info(sol.recommendation, tag="RECOMMEND")
    log.blank()

    log.step("VERIFICATION (independent methods)")
    for check_name, result in sol.verification.items():
        if isinstance(result, bool):
            log.check(check_name, result, tag="VERIFY")
        else:
            log.check(check_name, float(result), tag="VERIFY")
    log.blank()

    log.step("SENSITIVITY ANALYSIS")
    if "double_sample_size" in sol.sensitivity:
        s = sol.sensitivity["double_sample_size"]
        log.metric("Double sample size", "p={:.6f}, power={:.1%}, sig={}".format(
            s["p_value"], s["power"], s["significant"]), tag="SENSITIVITY")
    if "half_effect" in sol.sensitivity:
        s = sol.sensitivity["half_effect"]
        log.metric("Half effect size", "need {:,}/group for 80% power".format(
            s["n_per_group_needed"]), tag="SENSITIVITY")
    if "power_curve" in sol.sensitivity:
        log.info("Power curve:", tag="POWER")
        for n, pwr in sol.sensitivity["power_curve"].items():
            log.bar("n={:>6,}:".format(n), pwr, tag="POWER")
    log.blank()

    log.metric("Algorithm", sol.algorithm, tag="SOLVE")
    log.metric("Time", "{:.4f}s".format(sol.time_seconds), tag="TIMING")
    log.blank()

    # Output JSON
    output = {
        "instance": {
            "n_a": instance.n_a, "conv_a": instance.conv_a,
            "n_b": instance.n_b, "conv_b": instance.conv_b,
            "alpha": instance.alpha,
        },
        "frequentist": {
            "z_statistic": sol.z_statistic, "p_value": sol.p_value,
            "ci_diff": list(sol.ci_diff), "cohens_h": sol.effect_size_h,
            "is_significant": sol.is_significant,
        },
        "bayesian": {
            "prob_b_better": sol.prob_b_better,
            "expected_lift": sol.expected_lift_bayesian,
            "credible_interval_lift": list(sol.bayesian_ci_lift),
        },
        "bootstrap": {"ci_diff": list(sol.bootstrap_ci_diff)},
        "power": {"observed": sol.power, "n_for_80pct": sol.n_per_group_for_80pct},
        "recommendation": sol.recommendation,
        "verification": sol.verification,
        "sensitivity": sol.sensitivity,
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
    }
    with open("solution.json", "w") as f:
        json.dump(output, f, indent=2, default=str)
    log.success("Solution data saved to: solution.json", tag="SAVE")
    log.divider(style="thick")
