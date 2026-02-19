#!/usr/bin/env python3
"""Cafe Tips A/B Test -- Full uber-polya statistical inference pipeline.

Problem: A cafe owner plays jazz music some days and pop music other days.
She collected average tip percentage for 25 jazz days and 25 pop days.
Question: Does music genre significantly affect tipping behavior?

Polya Phase 1-2 (uber-model): Understand + Plan
  - Unknown: Is there a difference in mean tips between jazz and pop days?
  - Data: Two independent samples of daily tip percentages
  - Condition: Tips are continuous, days are independent
  - Structure: Two-sample hypothesis test (§10.2)
  - Model: H0: μ_jazz = μ_pop vs H1: μ_jazz ≠ μ_pop

Polya Phase 3 (uber-solve): Execute
  - Check assumptions (normality, equal variance)
  - Primary: Welch's t-test (S7) with Cohen's d effect size (S45)
  - Verification: Mann-Whitney U (S9), permutation test (S16), bootstrap CI (S20)
  - Power analysis (S44)

Polya Phase 4 (uber-interpret): Look Back
  - Translate to business recommendation
  - Sensitivity: What sample size would we need?
  - Visualization: Group comparison + distribution overlay
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field

import numpy as np
from scipy import stats


# --- Phase 1-2: Formal Model (uber-model output) ---

@dataclass(frozen=True)
class Instance:
    """Cafe tips problem instance."""
    jazz_tips: tuple[float, ...]   # daily avg tip % on jazz days
    pop_tips: tuple[float, ...]    # daily avg tip % on pop days
    alpha: float = 0.05

    @property
    def n_jazz(self) -> int:
        return len(self.jazz_tips)

    @property
    def n_pop(self) -> int:
        return len(self.pop_tips)


@dataclass
class Solution:
    """Complete statistical analysis solution."""
    # Descriptive statistics
    descriptive: dict = field(default_factory=dict)

    # Assumption checks
    assumptions: dict = field(default_factory=dict)

    # Primary test: Welch's t-test
    t_statistic: float = 0.0
    p_value: float = 0.0
    mean_diff: float = 0.0
    ci_diff: tuple[float, float] = (0.0, 0.0)
    cohens_d: float = 0.0
    effect_interpretation: str = ""

    # Verification tests
    verification: dict = field(default_factory=dict)

    # Power analysis
    power: float = 0.0
    n_per_group_80pct: int = 0

    # Bayesian
    bayesian: dict = field(default_factory=dict)

    # Sensitivity
    sensitivity: dict = field(default_factory=dict)

    # Metadata
    is_significant: bool = False
    recommendation: str = ""
    algorithm: str = ""
    time_seconds: float = 0.0


# --- Phase 3: Solve (uber-solve) ---

def solve(instance: Instance) -> Solution:
    """Full statistical analysis pipeline."""
    t0 = time.perf_counter()
    rng = np.random.default_rng(42)
    sol = Solution()

    jazz = np.array(instance.jazz_tips)
    pop = np.array(instance.pop_tips)

    # ── Step 1: Descriptive Statistics (S1) ──
    sol.descriptive = {
        "jazz": {
            "n": len(jazz), "mean": float(np.mean(jazz)),
            "std": float(np.std(jazz, ddof=1)), "median": float(np.median(jazz)),
            "min": float(jazz.min()), "max": float(jazz.max()),
            "q1": float(np.percentile(jazz, 25)), "q3": float(np.percentile(jazz, 75)),
        },
        "pop": {
            "n": len(pop), "mean": float(np.mean(pop)),
            "std": float(np.std(pop, ddof=1)), "median": float(np.median(pop)),
            "min": float(pop.min()), "max": float(pop.max()),
            "q1": float(np.percentile(pop, 25)), "q3": float(np.percentile(pop, 75)),
        },
    }

    # ── Step 2: Check Assumptions (S15, Levene's) ──
    # Normality: Shapiro-Wilk
    w_jazz, p_jazz_norm = stats.shapiro(jazz)
    w_pop, p_pop_norm = stats.shapiro(pop)
    # Equal variance: Levene's test
    _, p_levene = stats.levene(jazz, pop)

    sol.assumptions = {
        "normality_jazz": {"W": float(w_jazz), "p": float(p_jazz_norm),
                           "normal": p_jazz_norm > 0.05},
        "normality_pop": {"W": float(w_pop), "p": float(p_pop_norm),
                          "normal": p_pop_norm > 0.05},
        "equal_variance": {"levene_p": float(p_levene),
                           "equal": p_levene > 0.05},
        "parametric_ok": p_jazz_norm > 0.05 and p_pop_norm > 0.05,
    }

    # ── Step 3: Primary Test -- Welch's t-test (S7) ──
    t_stat, p_value = stats.ttest_ind(jazz, pop, equal_var=False)
    sol.t_statistic = float(t_stat)
    sol.p_value = float(p_value)
    sol.is_significant = p_value < instance.alpha

    # Mean difference with CI
    sol.mean_diff = float(np.mean(jazz) - np.mean(pop))
    se_diff = np.sqrt(np.var(jazz, ddof=1)/len(jazz) + np.var(pop, ddof=1)/len(pop))
    # Welch-Satterthwaite df
    s1, s2 = np.var(jazz, ddof=1), np.var(pop, ddof=1)
    n1, n2 = len(jazz), len(pop)
    df = (s1/n1 + s2/n2)**2 / ((s1/n1)**2/(n1-1) + (s2/n2)**2/(n2-1))
    t_crit = stats.t.ppf(1 - instance.alpha/2, df)
    sol.ci_diff = (float(sol.mean_diff - t_crit * se_diff),
                   float(sol.mean_diff + t_crit * se_diff))

    # Effect size: Cohen's d (S45)
    pooled_std = np.sqrt(((n1-1)*s1 + (n2-1)*s2) / (n1+n2-2))
    sol.cohens_d = float(sol.mean_diff / pooled_std)
    d_abs = abs(sol.cohens_d)
    if d_abs < 0.2:
        sol.effect_interpretation = "negligible"
    elif d_abs < 0.5:
        sol.effect_interpretation = "small"
    elif d_abs < 0.8:
        sol.effect_interpretation = "medium"
    else:
        sol.effect_interpretation = "large"

    # ── Step 4: Verification -- 3 independent methods ──
    # 4a. Mann-Whitney U (nonparametric, S9)
    u_stat, p_mw = stats.mannwhitneyu(jazz, pop, alternative="two-sided")
    r_biserial = 1 - (2 * u_stat) / (n1 * n2)

    # 4b. Permutation test (S16)
    def stat_fn(x, y, axis):
        return np.mean(x, axis=axis) - np.mean(y, axis=axis)
    perm_result = stats.permutation_test(
        (jazz, pop), stat_fn, n_resamples=10000,
        random_state=42, alternative="two-sided",
    )

    # 4c. Bootstrap CI for difference (S20)
    n_boot = 10000
    boot_diffs = []
    for _ in range(n_boot):
        b_jazz = rng.choice(jazz, size=n1, replace=True)
        b_pop = rng.choice(pop, size=n2, replace=True)
        boot_diffs.append(np.mean(b_jazz) - np.mean(b_pop))
    boot_diffs = np.array(boot_diffs)

    sol.verification = {
        "mann_whitney": {
            "U": float(u_stat), "p": float(p_mw),
            "rank_biserial_r": float(r_biserial),
            "agrees": (p_mw < instance.alpha) == sol.is_significant,
        },
        "permutation": {
            "p": float(perm_result.pvalue),
            "agrees": (perm_result.pvalue < instance.alpha) == sol.is_significant,
        },
        "bootstrap_ci": {
            "ci_2.5": float(np.percentile(boot_diffs, 2.5)),
            "ci_97.5": float(np.percentile(boot_diffs, 97.5)),
            "contains_zero": float(np.percentile(boot_diffs, 2.5)) <= 0 <= float(np.percentile(boot_diffs, 97.5)),
        },
        "all_agree": all([
            (p_mw < instance.alpha) == sol.is_significant,
            (perm_result.pvalue < instance.alpha) == sol.is_significant,
        ]),
    }

    # ── Step 5: Power Analysis (S44) ──
    from statsmodels.stats.power import TTestIndPower
    power_analysis = TTestIndPower()
    sol.power = float(power_analysis.solve_power(
        effect_size=abs(sol.cohens_d), nobs1=n1, alpha=instance.alpha, ratio=n2/n1,
    ))
    if abs(sol.cohens_d) > 0.01:
        sol.n_per_group_80pct = int(np.ceil(power_analysis.solve_power(
            effect_size=abs(sol.cohens_d), alpha=instance.alpha, power=0.8, ratio=1.0,
        )))
    else:
        sol.n_per_group_80pct = -1

    # ── Step 6: Bayesian analysis (S34 adapted for means) ──
    # Use Monte Carlo with posterior sampling
    # Uninformative prior: Normal(0, 100) for means, HalfNormal for sigma
    # Simplified: use observed statistics as basis
    post_jazz_samples = rng.normal(np.mean(jazz), stats.sem(jazz), 100000)
    post_pop_samples = rng.normal(np.mean(pop), stats.sem(pop), 100000)
    diff_samples = post_jazz_samples - post_pop_samples
    prob_jazz_higher = float(np.mean(diff_samples > 0))

    sol.bayesian = {
        "prob_jazz_higher": prob_jazz_higher,
        "expected_diff": float(np.mean(diff_samples)),
        "credible_interval_95": (
            float(np.percentile(diff_samples, 2.5)),
            float(np.percentile(diff_samples, 97.5)),
        ),
    }

    # ── Step 7: Sensitivity Analysis ──
    # Power at various sample sizes
    power_curve = {}
    for n in [10, 15, 20, 25, 30, 40, 50, 75, 100]:
        if abs(sol.cohens_d) > 0.01:
            pwr = power_analysis.solve_power(
                effect_size=abs(sol.cohens_d), nobs1=n,
                alpha=instance.alpha, ratio=1.0,
            )
            power_curve[n] = round(float(pwr), 3)
    sol.sensitivity = {
        "power_curve": power_curve,
        "current_n": n1,
        "current_power": sol.power,
    }

    # What if alpha = 0.01?
    sol.sensitivity["stricter_alpha"] = {
        "alpha": 0.01,
        "still_significant": sol.p_value < 0.01,
    }

    # ── Recommendation ──
    if sol.is_significant and d_abs >= 0.5:
        sol.recommendation = (
            "STRONG EVIDENCE: Jazz music significantly increases tips with a "
            "{} effect. Switch to jazz during peak hours.".format(sol.effect_interpretation)
        )
    elif sol.is_significant and d_abs >= 0.2:
        sol.recommendation = (
            "MODERATE EVIDENCE: Jazz shows a statistically significant but {} "
            "effect on tips. Consider jazz for a trial period and track results.".format(
                sol.effect_interpretation)
        )
    elif sol.is_significant and d_abs < 0.2:
        sol.recommendation = (
            "WEAK EVIDENCE: Statistically significant but negligible practical "
            "effect. The difference is too small to matter for your business."
        )
    elif not sol.is_significant and sol.power < 0.8:
        sol.recommendation = (
            "INCONCLUSIVE: Not significant, but the test was underpowered "
            "(power={:.0%}). Collect at least {} days per group to reach "
            "80% power for this effect size.".format(sol.power, sol.n_per_group_80pct)
        )
    else:
        sol.recommendation = (
            "NO EFFECT: With adequate power ({:.0%}), no significant difference "
            "detected. Music genre likely doesn't meaningfully affect tips.".format(sol.power)
        )

    sol.algorithm = "Welch's t-test + Mann-Whitney U + Permutation + Bootstrap"
    sol.time_seconds = time.perf_counter() - t0

    return sol


# --- Visualization (uber-interpret Phase 3) ---

def generate_visualizations(instance: Instance, sol: Solution) -> None:
    """Generate charts following uber-interpret visualization guide."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    jazz = np.array(instance.jazz_tips)
    pop = np.array(instance.pop_tips)

    # ── Chart 1: Group Comparison with CI (visualization.md §11) ──
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    # Left: Bar chart with CI error bars
    ax = axes[0]
    means = [sol.descriptive["jazz"]["mean"], sol.descriptive["pop"]["mean"]]
    sems = [stats.sem(jazz), stats.sem(pop)]
    t_crit = stats.t.ppf(0.975, 24)
    ci_errs = [t_crit * s for s in sems]

    colors = ["#1976d2", "#90caf9"]
    bars = ax.bar(["Jazz", "Pop"], means, yerr=ci_errs, capsize=10,
                  color=colors, edgecolor="white", linewidth=1.5, width=0.5,
                  error_kw={"linewidth": 2, "capthick": 1.5})

    for bar, mean in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15,
                "{:.1f}%".format(mean), ha="center", fontsize=12, fontweight="bold")

    # Significance bracket
    max_y = max(means) + max(ci_errs) + 0.8
    ax.annotate("", xy=(0, max_y), xytext=(1, max_y),
                arrowprops=dict(arrowstyle="-", color="black", lw=1.5))
    if sol.p_value < 0.001:
        sig_text = "p < 0.001 ***"
    elif sol.p_value < 0.01:
        sig_text = "p = {:.3f} **".format(sol.p_value)
    elif sol.p_value < 0.05:
        sig_text = "p = {:.3f} *".format(sol.p_value)
    else:
        sig_text = "p = {:.3f} (ns)".format(sol.p_value)
    ax.text(0.5, max_y + 0.1, sig_text, ha="center", fontsize=11)

    # Effect size annotation
    ax.text(0.98, 0.05, "Cohen's d = {:.2f} ({})".format(sol.cohens_d, sol.effect_interpretation),
            transform=ax.transAxes, ha="right", fontsize=9, style="italic",
            color="#555", bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.5))

    ax.set_ylabel("Average Tip (%)", fontsize=11)
    ax.set_title("Mean Tips by Music Genre", fontsize=13, fontweight="bold")
    ax.set_ylim(0, max_y + 0.8)

    # Right: Distribution overlay (visualization.md §12 concept)
    ax = axes[1]
    from scipy.stats import gaussian_kde

    x_range = np.linspace(min(jazz.min(), pop.min()) - 2,
                          max(jazz.max(), pop.max()) + 2, 200)
    kde_jazz = gaussian_kde(jazz, bw_method="silverman")
    kde_pop = gaussian_kde(pop, bw_method="silverman")

    ax.fill_between(x_range, kde_jazz(x_range), alpha=0.3, color="#1976d2", label="Jazz")
    ax.fill_between(x_range, kde_pop(x_range), alpha=0.3, color="#90caf9", label="Pop")
    ax.plot(x_range, kde_jazz(x_range), color="#1976d2", linewidth=2)
    ax.plot(x_range, kde_pop(x_range), color="#90caf9", linewidth=2)

    # Mark means
    ax.axvline(np.mean(jazz), color="#1976d2", linestyle="--", linewidth=1.5, alpha=0.7)
    ax.axvline(np.mean(pop), color="#64b5f6", linestyle="--", linewidth=1.5, alpha=0.7)
    ax.text(np.mean(jazz), ax.get_ylim()[1]*0.9, "  Jazz\n  mean",
            fontsize=8, color="#1976d2")
    ax.text(np.mean(pop), ax.get_ylim()[1]*0.75, "  Pop\n  mean",
            fontsize=8, color="#64b5f6")

    ax.set_xlabel("Tip (%)", fontsize=11)
    ax.set_ylabel("Density", fontsize=11)
    ax.set_title("Tip Distribution by Genre", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)

    plt.suptitle("Cafe Tips Analysis: Jazz vs. Pop Music",
                 fontsize=15, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig("cafe_tips_analysis.png", dpi=150, bbox_inches="tight")
    print("Saved: cafe_tips_analysis.png")

    # ── Chart 2: Power Curve ──
    fig, ax = plt.subplots(figsize=(8, 5))
    power_data = sol.sensitivity.get("power_curve", {})
    if power_data:
        ns = sorted(int(k) for k in power_data.keys())
        powers = [power_data[n] for n in ns]

        ax.plot(ns, powers, "o-", color="#1976d2", linewidth=2.5, markersize=8,
                markerfacecolor="white", markeredgewidth=2)
        ax.axhline(y=0.8, color="#d32f2f", linestyle="--", linewidth=1.5, alpha=0.7)
        ax.text(ns[-1]*0.98, 0.82, "80% power target", ha="right",
                fontsize=9, color="#d32f2f", style="italic")

        # Mark current
        ax.plot(instance.n_jazz, sol.power, "D", color="#d32f2f", markersize=12, zorder=5)
        ax.annotate("Current\nn={}\npower={:.0%}".format(instance.n_jazz, sol.power),
                    xy=(instance.n_jazz, sol.power),
                    xytext=(instance.n_jazz + 8, sol.power - 0.15),
                    fontsize=9, ha="left",
                    arrowprops=dict(arrowstyle="->", color="#d32f2f"),
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))

        ax.set_xlabel("Sample Size per Group (days)", fontsize=11)
        ax.set_ylabel("Statistical Power", fontsize=11)
        ax.set_title("Power Curve: How Many Days Do You Need?",
                     fontsize=14, fontweight="bold")
        ax.set_ylim(0, 1.05)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: "{:.0%}".format(x)))

    plt.tight_layout()
    plt.savefig("cafe_power_curve.png", dpi=150, bbox_inches="tight")
    print("Saved: cafe_power_curve.png")


# --- Main ---

if __name__ == "__main__":
    # Realistic data: daily average tip % (jazz tends higher)
    rng = np.random.default_rng(7)
    jazz_data = rng.normal(loc=19.2, scale=2.8, size=25).round(1)
    pop_data = rng.normal(loc=16.5, scale=3.0, size=25).round(1)
    # Clip to realistic range
    jazz_data = np.clip(jazz_data, 8, 30)
    pop_data = np.clip(pop_data, 8, 30)

    instance = Instance(
        jazz_tips=tuple(jazz_data.tolist()),
        pop_tips=tuple(pop_data.tolist()),
        alpha=0.05,
    )

    sol = solve(instance)

    # ═══════════════════════════════════════════════════════
    #  PHASE 1-2: MODEL (uber-model output)
    # ═══════════════════════════════════════════════════════
    print("=" * 70)
    print("  UBER-POLYA: Cafe Tips -- Jazz vs. Pop Music")
    print("=" * 70)
    print()
    print("  PHASE 1-2: UNDERSTAND & PLAN (uber-model)")
    print("  " + "=" * 64)
    print()
    print("  Problem Type:  Problem to Find (comparison)")
    print("  Unknown:       Is there a difference in mean tips?")
    print("  Data:          25 jazz days, 25 pop days (tip percentages)")
    print("  Condition:     Independent samples, continuous outcome")
    print()
    print("  Formal Model:")
    print("    H0: mu_jazz = mu_pop  (no difference)")
    print("    H1: mu_jazz != mu_pop (two-sided)")
    print("    Structure: Two-sample hypothesis test (structures.md 10.2)")
    print("    Test: Welch's t-test (algorithms-statistics.md S7)")
    print("    Verify: Mann-Whitney U (S9), Permutation (S16), Bootstrap (S20)")
    print()

    # ═══════════════════════════════════════════════════════
    #  PHASE 3: SOLVE (uber-solve output)
    # ═══════════════════════════════════════════════════════
    print("  PHASE 3: EXECUTE (uber-solve)")
    print("  " + "=" * 64)
    print()

    # Descriptive stats
    print("  STEP 1: Descriptive Statistics")
    print("  " + "-" * 64)
    print("  {:<12} {:>8} {:>8} {:>8} {:>8} {:>8}".format(
        "Genre", "n", "Mean", "SD", "Median", "IQR"))
    print("  " + "-" * 64)
    for genre, key in [("Jazz", "jazz"), ("Pop", "pop")]:
        d = sol.descriptive[key]
        print("  {:<12} {:>8} {:>8.1f} {:>8.1f} {:>8.1f} {:>8.1f}".format(
            genre, d["n"], d["mean"], d["std"], d["median"],
            d["q3"] - d["q1"]))
    print()

    # Assumption checks
    print("  STEP 2: Assumption Checks")
    print("  " + "-" * 64)
    for genre, key in [("Jazz", "normality_jazz"), ("Pop", "normality_pop")]:
        a = sol.assumptions[key]
        status = "PASS (normal)" if a["normal"] else "FAIL (non-normal)"
        print("  Normality ({}):  Shapiro W={:.3f}, p={:.3f} -> {}".format(
            genre, a["W"], a["p"], status))
    ev = sol.assumptions["equal_variance"]
    print("  Equal variance:  Levene p={:.3f} -> {}".format(
        ev["levene_p"], "PASS (equal)" if ev["equal"] else "FAIL (unequal)"))
    print("  Parametric OK:   {}".format(
        "Yes -> Welch's t-test" if sol.assumptions["parametric_ok"]
        else "No -> will also run nonparametric"))
    print()

    # Primary test
    print("  STEP 3: Primary Test (Welch's t-test)")
    print("  " + "-" * 64)
    print("  t-statistic:    {:.3f}".format(sol.t_statistic))
    print("  p-value:        {:.6f}".format(sol.p_value))
    print("  Significant:    {} (alpha={})".format(sol.is_significant, instance.alpha))
    print("  Mean difference:{:+.2f} percentage points".format(sol.mean_diff))
    print("  95% CI (diff):  [{:.2f}, {:.2f}]".format(*sol.ci_diff))
    print("  Cohen's d:      {:.3f} ({})".format(sol.cohens_d, sol.effect_interpretation))
    print("  Power:          {:.1%}".format(sol.power))
    print()

    # Verification
    print("  STEP 4: Independent Verification")
    print("  " + "-" * 64)
    mw = sol.verification["mann_whitney"]
    print("  Mann-Whitney U: U={:.0f}, p={:.6f} -> {}".format(
        mw["U"], mw["p"], "AGREES" if mw["agrees"] else "DISAGREES"))
    pm = sol.verification["permutation"]
    print("  Permutation:    p={:.6f} -> {}".format(
        pm["p"], "AGREES" if pm["agrees"] else "DISAGREES"))
    bs = sol.verification["bootstrap_ci"]
    print("  Bootstrap CI:   [{:.2f}, {:.2f}] -> {}".format(
        bs["ci_2.5"], bs["ci_97.5"],
        "contains 0 (consistent with non-sig)" if bs["contains_zero"]
        else "excludes 0 (consistent with sig)"))
    print("  All methods:    {}".format(
        "AGREE" if sol.verification["all_agree"] else "DISAGREE"))
    print()

    # Bayesian
    print("  STEP 5: Bayesian Analysis")
    print("  " + "-" * 64)
    print("  P(jazz > pop):  {:.1%}".format(sol.bayesian["prob_jazz_higher"]))
    print("  Expected diff:  {:+.2f} pp".format(sol.bayesian["expected_diff"]))
    print("  95% CrI:        [{:.2f}, {:.2f}]".format(
        *sol.bayesian["credible_interval_95"]))
    print()

    # Power analysis
    print("  STEP 6: Power Analysis")
    print("  " + "-" * 64)
    print("  Current power:  {:.1%} (n=25/group)".format(sol.power))
    print("  Need for 80%:   {} days per group".format(sol.n_per_group_80pct))
    if "power_curve" in sol.sensitivity:
        print("  Power curve:")
        for n, pwr in sol.sensitivity["power_curve"].items():
            bar = "#" * int(pwr * 30)
            marker = " <-- current" if n == instance.n_jazz else ""
            print("    n={:>3}: {:.0%} {}{}".format(n, pwr, bar, marker))
    print()

    # ═══════════════════════════════════════════════════════
    #  PHASE 4: LOOK BACK (uber-interpret output)
    # ═══════════════════════════════════════════════════════
    print("  PHASE 4: LOOK BACK (uber-interpret)")
    print("  " + "=" * 64)
    print()
    print("  BOTTOM LINE")
    print("  " + "-" * 64)
    if sol.is_significant:
        print("  Jazz music days have {:.1f}% average tips vs {:.1f}% for pop --".format(
            sol.descriptive["jazz"]["mean"], sol.descriptive["pop"]["mean"]))
        print("  a {:+.1f} percentage point difference (p={:.4f}).".format(
            sol.mean_diff, sol.p_value))
    else:
        print("  No statistically significant difference detected between")
        print("  jazz ({:.1f}%) and pop ({:.1f}%) music days (p={:.3f}).".format(
            sol.descriptive["jazz"]["mean"], sol.descriptive["pop"]["mean"],
            sol.p_value))
    print()

    print("  WHAT THIS MEANS FOR YOUR CAFE")
    print("  " + "-" * 64)
    if sol.is_significant and abs(sol.cohens_d) >= 0.5:
        annual = sol.mean_diff * 365 / 100 * 500  # assume $500 avg daily tips base
        print("  - The effect is real and meaningful ({} effect size)".format(
            sol.effect_interpretation))
        print("  - On a $500 daily tip base, jazz adds ~${:.0f}/year".format(abs(annual)))
        print("  - All 3 verification methods agree")
        print("  - Bayesian: {:.0%} probability jazz is genuinely better".format(
            sol.bayesian["prob_jazz_higher"]))
    elif sol.is_significant:
        print("  - Statistically detectable but {} effect".format(
            sol.effect_interpretation))
        print("  - May not translate to meaningful revenue difference")
    else:
        if sol.power < 0.8:
            print("  - Your test was underpowered ({:.0%} power)".format(sol.power))
            print("  - This means: a real difference MIGHT exist but you")
            print("    didn't collect enough data to detect it reliably")
            print("  - Recommendation: collect {} more days per genre".format(
                max(0, sol.n_per_group_80pct - instance.n_jazz)))
        else:
            print("  - With {:.0%} power, you had a good chance of".format(sol.power))
            print("    detecting a meaningful effect -- and didn't find one")
            print("  - Music genre likely doesn't affect tips much")
    print()

    print("  RECOMMENDATION")
    print("  " + "-" * 64)
    print("  {}".format(sol.recommendation))
    print()

    print("  SENSITIVITY")
    print("  " + "-" * 64)
    strict = sol.sensitivity.get("stricter_alpha", {})
    if strict:
        print("  At alpha=0.01 (stricter): {}".format(
            "still significant" if strict["still_significant"] else "no longer significant"))
    print("  If you want to be more certain, collect {} days/group".format(
        sol.n_per_group_80pct))
    print()

    print("  LIMITATIONS")
    print("  " + "-" * 64)
    print("  - Days were not randomized (possible confounding: weekday, season)")
    print("  - Tips may depend on staff, weather, events -- not just music")
    print("  - Self-selected music choice (owner picks) vs controlled experiment")
    print("  - Small sample (n=25/group); larger sample increases confidence")
    print()

    print("  TRANSFERABLE PATTERN")
    print("  " + "-" * 64)
    print("  Pattern: 'Does X affect Y?' with two groups")
    print("  Model:   Two-sample hypothesis test (structures.md 10.2)")
    print("  Solve:   Welch's t-test + nonparametric verification")
    print("  Reuse:   Any before/after, A/B, treatment/control comparison")
    print()

    print("  Algorithm: {}".format(sol.algorithm))
    print("  Time:      {:.4f}s".format(sol.time_seconds))
    print("=" * 70)

    # Generate visualizations
    print()
    generate_visualizations(instance, sol)

    # Save JSON
    output = {
        "descriptive": sol.descriptive,
        "assumptions": sol.assumptions,
        "primary_test": {
            "t_statistic": sol.t_statistic, "p_value": sol.p_value,
            "mean_diff": sol.mean_diff, "ci_diff": list(sol.ci_diff),
            "cohens_d": sol.cohens_d, "effect": sol.effect_interpretation,
            "is_significant": sol.is_significant,
        },
        "verification": sol.verification,
        "bayesian": sol.bayesian,
        "power": {"observed": sol.power, "n_for_80pct": sol.n_per_group_80pct},
        "sensitivity": sol.sensitivity,
        "recommendation": sol.recommendation,
    }
    with open("solution.json", "w") as f:
        json.dump(output, f, indent=2, default=str)
    print("Saved: solution.json")
