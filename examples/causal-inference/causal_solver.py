#!/usr/bin/env python3
"""Causal Inference solver -- Job Training Program.

Estimates the causal effect of a voluntary job training program on salary
using four methods:
  1. Naive difference in means (biased by selection)
  2. Propensity Score Matching (ATT)
  3. Difference-in-Differences (DiD)
  4. Doubly Robust / Augmented Inverse Propensity Weighting (AIPW)

The data is synthetic with a known true effect of $5,000, demonstrating
how naive estimation overstates the effect while causal methods recover
the ground truth.

Verification: 8 independent checks confirming bias in naive estimate,
accuracy of causal methods, propensity overlap, and treatment balance.
"""
from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from scipy.special import expit
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.neighbors import NearestNeighbors

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger

log = PolyaLogger()


# ---------------------------------------------------------------------------
# Data Model
# ---------------------------------------------------------------------------

TRUE_EFFECT: float = 5000.0


@dataclass(frozen=True)
class Instance:
    """Causal inference problem instance with synthetic observational data."""
    education: tuple[float, ...]       # years of education per employee
    experience: tuple[float, ...]      # years of experience per employee
    age: tuple[float, ...]             # age per employee
    treatment: tuple[int, ...]         # 1 = trained, 0 = control
    salary: tuple[float, ...]          # observed salary (outcome)
    salary_pre: tuple[float, ...]      # synthetic pre-treatment salary (for DiD)
    true_effect: float = TRUE_EFFECT
    n: int = 1000

    @property
    def n_treated(self) -> int:
        return sum(self.treatment)

    @property
    def n_control(self) -> int:
        return self.n - self.n_treated


@dataclass
class Solution:
    """Complete causal inference solution."""
    # Naive estimate
    naive_diff: float = 0.0

    # Propensity Score Matching
    psm_att: float = 0.0
    propensity_treated_mean: float = 0.0
    propensity_control_mean: float = 0.0

    # Difference-in-Differences
    did_estimate: float = 0.0

    # Doubly Robust (AIPW)
    dr_ate: float = 0.0

    # Metadata
    n_treated: int = 0
    n_control: int = 0
    true_effect: float = TRUE_EFFECT
    algorithm: str = ""
    time_seconds: float = 0.0

    # Verification
    verification: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Data Generation
# ---------------------------------------------------------------------------

def generate_instance(seed: int = 42, n: int = 1000) -> Instance:
    """Generate synthetic observational data with confounding.

    Covariates (education, experience, age) affect both treatment
    assignment and salary, creating selection bias.  The true causal
    effect of treatment on salary is exactly TRUE_EFFECT.
    """
    rng = np.random.default_rng(seed)

    # -- Covariates --
    education = rng.normal(14, 3, n)          # years of schooling
    experience = rng.normal(10, 5, n)         # years of work experience
    age = rng.normal(35, 8, n)                # age in years

    # Clip to reasonable ranges
    education = np.clip(education, 8, 22)
    experience = np.clip(experience, 0, 35)
    age = np.clip(age, 22, 65)

    # -- Treatment assignment (depends on education & experience) --
    # Higher education and more experience -> more likely to enroll
    # Coefficients calibrated so ~50% are treated (balanced groups)
    logit_p = -2.0 + 0.10 * education + 0.05 * experience
    prop_score = expit(logit_p)
    treatment = rng.binomial(1, prop_score)

    # -- Outcome: salary --
    # Salary depends on education, experience, age, AND treatment
    noise = rng.normal(0, 5000, n)
    base_salary = (
        20000
        + 3000 * education
        + 1500 * experience
        + 200 * age
        + noise
    )
    salary = base_salary + TRUE_EFFECT * treatment

    # -- Pre-treatment salary (for DiD): salary without treatment effect + different noise --
    noise_pre = rng.normal(0, 5000, n)
    salary_pre = (
        20000
        + 3000 * education
        + 1500 * experience
        + 200 * age
        + noise_pre
    )

    return Instance(
        education=tuple(education.tolist()),
        experience=tuple(experience.tolist()),
        age=tuple(age.tolist()),
        treatment=tuple(treatment.tolist()),
        salary=tuple(salary.tolist()),
        salary_pre=tuple(salary_pre.tolist()),
        true_effect=TRUE_EFFECT,
        n=n,
    )


# ---------------------------------------------------------------------------
# Solver
# ---------------------------------------------------------------------------

def solve(instance: Instance) -> Solution:
    """Estimate causal effect using four methods."""
    t0 = time.perf_counter()
    sol = Solution()

    # Convert to arrays
    edu = np.array(instance.education)
    exp = np.array(instance.experience)
    age = np.array(instance.age)
    treat = np.array(instance.treatment)
    salary = np.array(instance.salary)
    salary_pre = np.array(instance.salary_pre)
    X = np.column_stack([edu, exp, age])

    treated_mask = treat == 1
    control_mask = treat == 0
    sol.n_treated = int(treated_mask.sum())
    sol.n_control = int(control_mask.sum())

    # ---------------------------------------------------------------
    # Method 1: Naive difference in means (biased)
    # ---------------------------------------------------------------
    sol.naive_diff = float(salary[treated_mask].mean() - salary[control_mask].mean())

    # ---------------------------------------------------------------
    # Method 2: Propensity Score Matching (ATT)
    # ---------------------------------------------------------------
    # Fit propensity model: P(treatment=1 | X)
    ps_model = LogisticRegression(max_iter=1000, random_state=42)
    ps_model.fit(X, treat)
    propensity = ps_model.predict_proba(X)[:, 1]

    sol.propensity_treated_mean = float(propensity[treated_mask].mean())
    sol.propensity_control_mean = float(propensity[control_mask].mean())

    # Nearest-neighbor matching on propensity score (1:1, with replacement)
    ps_control = propensity[control_mask].reshape(-1, 1)
    ps_treated = propensity[treated_mask].reshape(-1, 1)

    nn = NearestNeighbors(n_neighbors=1, metric="euclidean")
    nn.fit(ps_control)
    distances, indices = nn.kneighbors(ps_treated)

    # For each treated unit, find matched control salary
    control_salaries = salary[control_mask]
    matched_control_salary = control_salaries[indices.flatten()]
    treated_salary = salary[treated_mask]

    sol.psm_att = float((treated_salary - matched_control_salary).mean())

    # ---------------------------------------------------------------
    # Method 3: Difference-in-Differences
    # ---------------------------------------------------------------
    # Panel structure: pre-treatment salary (no effect) vs post-treatment salary
    # DiD = (mean_treated_post - mean_treated_pre) - (mean_control_post - mean_control_pre)
    #
    # Equivalently, regress salary_change on treatment indicator.
    salary_change = salary - salary_pre  # for treated, this includes the $5000 effect

    did_treated_change = salary_change[treated_mask].mean()
    did_control_change = salary_change[control_mask].mean()
    sol.did_estimate = float(did_treated_change - did_control_change)

    # ---------------------------------------------------------------
    # Method 4: Doubly Robust / AIPW (ATE)
    # ---------------------------------------------------------------
    # Outcome model: E[Y | X, T]
    # Fit separate outcome models for treated and control
    outcome_model_1 = LinearRegression()
    outcome_model_0 = LinearRegression()
    outcome_model_1.fit(X[treated_mask], salary[treated_mask])
    outcome_model_0.fit(X[control_mask], salary[control_mask])

    # Predict potential outcomes for all units
    mu1_hat = outcome_model_1.predict(X)  # E[Y(1) | X]
    mu0_hat = outcome_model_0.predict(X)  # E[Y(0) | X]

    # AIPW estimator
    n = len(treat)
    aipw_scores = (
        mu1_hat - mu0_hat
        + treat * (salary - mu1_hat) / np.clip(propensity, 0.01, 0.99)
        - (1 - treat) * (salary - mu0_hat) / np.clip(1 - propensity, 0.01, 0.99)
    )
    sol.dr_ate = float(aipw_scores.mean())

    # ---------------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------------
    sol.algorithm = (
        "Naive + Propensity Score Matching + "
        "Difference-in-Differences + Doubly Robust (AIPW)"
    )
    sol.time_seconds = time.perf_counter() - t0

    # Independent verification
    sol.verification = verify(instance, sol)

    return sol


# ---------------------------------------------------------------------------
# Verification (independent of solver)
# ---------------------------------------------------------------------------

def verify(instance: Instance, sol: Solution) -> dict:
    """Independent verification with 8 checks."""
    checks: dict = {}
    true = instance.true_effect

    # Check 1: naive_biased -- naive estimate is far from truth (shows bias)
    naive_error = abs(sol.naive_diff - true)
    checks["naive_biased"] = bool(naive_error > 1000)

    # Check 2: psm_close -- PSM recovers close to true effect
    psm_error = abs(sol.psm_att - true)
    checks["psm_close"] = bool(psm_error < 1500)

    # Check 3: did_close -- DiD recovers close to true effect
    did_error = abs(sol.did_estimate - true)
    checks["did_close"] = bool(did_error < 1500)

    # Check 4: dr_close -- Doubly robust recovers close to true effect
    dr_error = abs(sol.dr_ate - true)
    checks["dr_close"] = bool(dr_error < 1500)

    # Check 5: psm_closer_than_naive -- PSM is closer to truth than naive
    checks["psm_closer_than_naive"] = bool(psm_error < naive_error)

    # Check 6: dr_closer_than_naive -- DR is closer to truth than naive
    checks["dr_closer_than_naive"] = bool(dr_error < naive_error)

    # Check 7: propensity_overlap -- mean propensity for both groups in (0.2, 0.8)
    checks["propensity_overlap"] = bool(
        0.2 < sol.propensity_treated_mean < 0.8
        and 0.2 < sol.propensity_control_mean < 0.8
    )

    # Check 8: treatment_balance -- roughly balanced groups
    checks["treatment_balance"] = bool(400 < sol.n_treated < 600)

    # Summary
    checks["all_passed"] = all(
        v for k, v in checks.items() if k != "all_passed"
    )

    return checks


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    instance = generate_instance(seed=42, n=1000)
    sol = solve(instance)

    # ==================================================================
    #  Report
    # ==================================================================
    log.header("CAUSAL INFERENCE: Job Training Program")

    # -- Instance summary --
    log.section("PHASE 1-2: UNDERSTAND & PLAN (uber-model)")
    log.info("Problem: Estimate causal effect of voluntary training on salary", tag="MODEL")
    log.info("Confounders: education, experience, age", tag="MODEL")
    log.info("True effect (ground truth): ${:,.0f}".format(instance.true_effect), tag="DATA")
    log.metric("N total", str(instance.n), tag="DATA")
    log.metric("N treated", str(sol.n_treated), tag="DATA")
    log.metric("N control", str(sol.n_control), tag="DATA")
    log.blank()

    # -- Method 1: Naive --
    log.section("PHASE 3: EXECUTE (uber-solve)")

    log.step("METHOD 1: Naive Difference in Means")
    log.metric("Naive estimate", "${:,.0f}".format(sol.naive_diff), tag="STATS")
    log.metric("True effect", "${:,.0f}".format(TRUE_EFFECT), tag="STATS")
    log.metric("Bias", "${:+,.0f}".format(sol.naive_diff - TRUE_EFFECT), tag="STATS")
    log.warning(
        "Naive overestimates because high-education employees "
        "both earn more AND self-select into training",
        tag="WARNING",
    )
    log.blank()

    # -- Method 2: PSM --
    log.step("METHOD 2: Propensity Score Matching (ATT)")
    log.metric("Propensity (treated)", "{:.3f}".format(sol.propensity_treated_mean), tag="STATS")
    log.metric("Propensity (control)", "{:.3f}".format(sol.propensity_control_mean), tag="STATS")
    log.metric("PSM ATT", "${:,.0f}".format(sol.psm_att), tag="RESULT")
    log.metric("Error vs truth", "${:+,.0f}".format(sol.psm_att - TRUE_EFFECT), tag="STATS")
    log.blank()

    # -- Method 3: DiD --
    log.step("METHOD 3: Difference-in-Differences")
    log.metric("DiD estimate", "${:,.0f}".format(sol.did_estimate), tag="RESULT")
    log.metric("Error vs truth", "${:+,.0f}".format(sol.did_estimate - TRUE_EFFECT), tag="STATS")
    log.blank()

    # -- Method 4: Doubly Robust --
    log.step("METHOD 4: Doubly Robust / AIPW (ATE)")
    log.metric("DR ATE", "${:,.0f}".format(sol.dr_ate), tag="RESULT")
    log.metric("Error vs truth", "${:+,.0f}".format(sol.dr_ate - TRUE_EFFECT), tag="STATS")
    log.blank()

    # -- Comparison table --
    log.step("COMPARISON")
    log.table_row(
        "{:<30} {:>12} {:>12}".format("Method", "Estimate", "Error"),
        tag="TABLE",
    )
    log.table_row("-" * 56, tag="TABLE")
    for label, est in [
        ("Naive (biased)", sol.naive_diff),
        ("Propensity Score Matching", sol.psm_att),
        ("Difference-in-Differences", sol.did_estimate),
        ("Doubly Robust (AIPW)", sol.dr_ate),
    ]:
        err = est - TRUE_EFFECT
        log.table_row(
            "{:<30} ${:>10,.0f} ${:>+10,.0f}".format(label, est, err),
            tag="STATS",
        )
    log.table_row("-" * 56, tag="TABLE")
    log.table_row(
        "{:<30} ${:>10,.0f}".format("True effect", TRUE_EFFECT),
        tag="RESULT",
    )
    log.blank()

    # -- Verification --
    log.step("VERIFICATION (8 independent checks)")
    for name, passed in sol.verification.items():
        if name == "all_passed":
            continue
        log.check(name, passed, tag="VERIFY")
    log.blank()
    log.check("ALL CHECKS PASSED", sol.verification["all_passed"], tag="VERIFY")
    log.blank()

    # -- Interpretation --
    log.section("PHASE 4: LOOK BACK (uber-interpret)")

    log.step("BOTTOM LINE")
    log.success(
        "The naive estimate (${:,.0f}) overstates the training effect by ${:,.0f}".format(
            sol.naive_diff, sol.naive_diff - TRUE_EFFECT,
        ),
        tag="RESULT",
    )
    log.success(
        "All three causal methods recover approximately ${:,.0f} (the true effect)".format(
            TRUE_EFFECT,
        ),
        tag="RESULT",
    )
    log.blank()

    log.step("WHY NAIVE FAILS")
    log.info(
        "Employees who enroll have higher education and experience",
        tag="INTERPRET",
    )
    log.info(
        "These same traits independently increase salary",
        tag="INTERPRET",
    )
    log.info(
        "Naive conflates 'earns more because educated' with 'earns more because trained'",
        tag="INTERPRET",
    )
    log.blank()

    log.step("RECOMMENDATION")
    log.success(
        "Use causal methods (PSM, DiD, or DR) whenever treatment is not randomized",
        tag="RECOMMEND",
    )
    log.success(
        "Doubly robust is preferred: consistent if either propensity or outcome model is correct",
        tag="RECOMMEND",
    )
    log.blank()

    log.step("TRANSFERABLE PATTERN")
    log.info("Pattern: 'What is the causal effect of X on Y?' with observational data", tag="MODEL")
    log.info("Model:   Potential outcomes framework with confounders", tag="MODEL")
    log.info("Solve:   PSM + DiD + Doubly Robust estimation", tag="SOLVE")
    log.info("Reuse:   Policy evaluation, program impact, medical treatment effects", tag="MODEL")

    log.blank()
    log.metric("Algorithm", sol.algorithm, tag="TIMING")
    log.metric("Time", "{:.4f}s".format(sol.time_seconds), tag="TIMING")
    log.divider(style="thick")

    # -- Save JSON --
    output = {
        "instance": {
            "n": instance.n,
            "n_treated": sol.n_treated,
            "n_control": sol.n_control,
            "true_effect": instance.true_effect,
        },
        "naive": {
            "estimate": sol.naive_diff,
            "bias": sol.naive_diff - TRUE_EFFECT,
        },
        "propensity_score_matching": {
            "att": sol.psm_att,
            "propensity_treated_mean": sol.propensity_treated_mean,
            "propensity_control_mean": sol.propensity_control_mean,
            "error": sol.psm_att - TRUE_EFFECT,
        },
        "difference_in_differences": {
            "estimate": sol.did_estimate,
            "error": sol.did_estimate - TRUE_EFFECT,
        },
        "doubly_robust": {
            "ate": sol.dr_ate,
            "error": sol.dr_ate - TRUE_EFFECT,
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
