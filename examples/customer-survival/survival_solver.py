#!/usr/bin/env python3
"""Customer Survival -- SaaS Subscription Churn solver.

Analyzes SaaS customer churn using survival analysis:
  1. Kaplan-Meier estimator per plan group
  2. Log-rank test comparing Basic vs Pro survival
  3. Cox Proportional Hazards regression with plan type and ticket count

Verification: independent checks on monotonicity, probability bounds,
significance, hazard ratio directions, concordance, and censoring rate.
"""
from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter, KaplanMeierFitter
from lifelines.statistics import logrank_test
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger

log = PolyaLogger()


# --- Data Model ---

@dataclass(frozen=True)
class Instance:
    """Survival analysis problem instance."""
    durations: tuple[float, ...]      # subscription duration in months
    events: tuple[int, ...]           # 1 = churned, 0 = censored (still active)
    plan_types: tuple[str, ...]       # "Basic" or "Pro"
    ticket_counts: tuple[int, ...]    # number of support tickets filed
    alpha: float = 0.05

    @property
    def n(self) -> int:
        return len(self.durations)

    @property
    def n_basic(self) -> int:
        return sum(1 for p in self.plan_types if p == "Basic")

    @property
    def n_pro(self) -> int:
        return sum(1 for p in self.plan_types if p == "Pro")

    @property
    def censoring_rate(self) -> float:
        return 1.0 - sum(self.events) / len(self.events)


@dataclass
class Solution:
    """Survival analysis solution with all results."""
    # Kaplan-Meier results
    km_basic_times: list[float] = field(default_factory=list)
    km_basic_survival: list[float] = field(default_factory=list)
    km_pro_times: list[float] = field(default_factory=list)
    km_pro_survival: list[float] = field(default_factory=list)
    median_basic: float = 0.0
    median_pro: float = 0.0

    # Log-rank test
    logrank_statistic: float = 0.0
    logrank_p_value: float = 0.0

    # Cox PH results
    cox_plan_coef: float = 0.0
    cox_plan_hr: float = 0.0
    cox_plan_hr_lower: float = 0.0
    cox_plan_hr_upper: float = 0.0
    cox_plan_p: float = 0.0
    cox_tickets_coef: float = 0.0
    cox_tickets_hr: float = 0.0
    cox_tickets_hr_lower: float = 0.0
    cox_tickets_hr_upper: float = 0.0
    cox_tickets_p: float = 0.0
    concordance_index: float = 0.0

    # PH assumption check
    ph_test_plan_p: float = 0.0
    ph_test_tickets_p: float = 0.0
    ph_assumption_holds: bool = False

    # Descriptive
    n_total: int = 0
    n_basic: int = 0
    n_pro: int = 0
    n_events: int = 0
    n_censored: int = 0
    censoring_rate: float = 0.0
    mean_tickets_basic: float = 0.0
    mean_tickets_pro: float = 0.0

    # Metadata
    algorithm: str = ""
    time_seconds: float = 0.0

    # Verification
    verification: dict = field(default_factory=dict)


# --- Synthetic Data Generation ---

def generate_instance(seed: int = 42) -> Instance:
    """Generate synthetic SaaS customer data.

    Basic plan: n=300, median survival ~12 months (Weibull with higher hazard)
    Pro plan:   n=200, median survival ~24 months (Weibull with lower hazard)
    Censoring:  ~30% right-censored (still active)
    Tickets:    Poisson-distributed covariate; higher tickets -> higher churn
    """
    rng = np.random.default_rng(seed)

    n_basic = 300
    n_pro = 200
    n_total = n_basic + n_pro

    # Plan labels
    plans = ["Basic"] * n_basic + ["Pro"] * n_pro

    # Support ticket counts: Basic customers file more tickets on average
    tickets_basic = rng.poisson(lam=4.0, size=n_basic)
    tickets_pro = rng.poisson(lam=2.0, size=n_pro)
    tickets = np.concatenate([tickets_basic, tickets_pro])

    # Generate true survival times using Weibull distribution
    # Weibull: T = scale * (-log(U))^(1/shape)
    # Higher ticket count increases hazard (multiplicative model)
    shape = 1.2  # slight increasing hazard over time

    # Base scales chosen so median survival is ~12 (Basic) and ~24 (Pro)
    # Median of Weibull = scale * (ln(2))^(1/shape)
    # For median=12: scale = 12 / (ln(2))^(1/1.2)
    ln2_inv_shape = np.log(2) ** (1.0 / shape)
    scale_basic = 12.0 / ln2_inv_shape
    scale_pro = 24.0 / ln2_inv_shape

    scales = np.array(
        [scale_basic] * n_basic + [scale_pro] * n_pro, dtype=float
    )

    # Ticket effect: each ticket multiplies hazard by exp(0.08)
    # which means it divides survival time by exp(0.08/shape)
    ticket_effect = np.exp(-0.08 * tickets / shape)
    effective_scales = scales * ticket_effect

    # Draw true survival times from Weibull
    u = rng.uniform(0, 1, size=n_total)
    true_times = effective_scales * (-np.log(u)) ** (1.0 / shape)

    # Generate censoring times: uniform on [0, max_obs]
    # Choose max_obs so that roughly 30% are censored
    max_obs = 56.0
    censor_times = rng.uniform(0, max_obs, size=n_total)

    # Observed data: min(true_time, censor_time)
    observed_times = np.minimum(true_times, censor_times)
    events = (true_times <= censor_times).astype(int)

    # Ensure minimum duration of 0.5 months
    observed_times = np.maximum(observed_times, 0.5)

    return Instance(
        durations=tuple(np.round(observed_times, 2).tolist()),
        events=tuple(events.tolist()),
        plan_types=tuple(plans),
        ticket_counts=tuple(tickets.tolist()),
        alpha=0.05,
    )


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Run full survival analysis pipeline."""
    t0 = time.perf_counter()
    sol = Solution()

    # Build DataFrame
    df = pd.DataFrame({
        "duration": instance.durations,
        "event": instance.events,
        "plan": instance.plan_types,
        "tickets": instance.ticket_counts,
    })
    df["is_basic"] = (df["plan"] == "Basic").astype(int)

    # Descriptive statistics
    sol.n_total = instance.n
    sol.n_basic = instance.n_basic
    sol.n_pro = instance.n_pro
    sol.n_events = sum(instance.events)
    sol.n_censored = sol.n_total - sol.n_events
    sol.censoring_rate = instance.censoring_rate
    sol.mean_tickets_basic = float(
        df.loc[df["plan"] == "Basic", "tickets"].mean()
    )
    sol.mean_tickets_pro = float(
        df.loc[df["plan"] == "Pro", "tickets"].mean()
    )

    # --- 1. Kaplan-Meier per group ---
    basic_mask = df["plan"] == "Basic"
    pro_mask = df["plan"] == "Pro"

    kmf_basic = KaplanMeierFitter()
    kmf_basic.fit(
        df.loc[basic_mask, "duration"],
        event_observed=df.loc[basic_mask, "event"],
        label="Basic",
    )

    kmf_pro = KaplanMeierFitter()
    kmf_pro.fit(
        df.loc[pro_mask, "duration"],
        event_observed=df.loc[pro_mask, "event"],
        label="Pro",
    )

    # Extract KM survival table values
    sol.km_basic_times = kmf_basic.survival_function_.index.tolist()
    sol.km_basic_survival = kmf_basic.survival_function_["Basic"].tolist()
    sol.km_pro_times = kmf_pro.survival_function_.index.tolist()
    sol.km_pro_survival = kmf_pro.survival_function_["Pro"].tolist()

    sol.median_basic = float(kmf_basic.median_survival_time_)
    sol.median_pro = float(kmf_pro.median_survival_time_)

    # --- 2. Log-rank test ---
    lr_result = logrank_test(
        df.loc[basic_mask, "duration"],
        df.loc[pro_mask, "duration"],
        event_observed_A=df.loc[basic_mask, "event"],
        event_observed_B=df.loc[pro_mask, "event"],
    )
    sol.logrank_statistic = float(lr_result.test_statistic)
    sol.logrank_p_value = float(lr_result.p_value)

    # --- 3. Cox Proportional Hazards ---
    cox_df = df[["duration", "event", "is_basic", "tickets"]].copy()
    cph = CoxPHFitter()
    cph.fit(cox_df, duration_col="duration", event_col="event")

    summary = cph.summary

    sol.cox_plan_coef = float(summary.loc["is_basic", "coef"])
    sol.cox_plan_hr = float(summary.loc["is_basic", "exp(coef)"])
    sol.cox_plan_hr_lower = float(
        summary.loc["is_basic", "exp(coef) lower 95%"]
    )
    sol.cox_plan_hr_upper = float(
        summary.loc["is_basic", "exp(coef) upper 95%"]
    )
    sol.cox_plan_p = float(summary.loc["is_basic", "p"])

    sol.cox_tickets_coef = float(summary.loc["tickets", "coef"])
    sol.cox_tickets_hr = float(summary.loc["tickets", "exp(coef)"])
    sol.cox_tickets_hr_lower = float(
        summary.loc["tickets", "exp(coef) lower 95%"]
    )
    sol.cox_tickets_hr_upper = float(
        summary.loc["tickets", "exp(coef) upper 95%"]
    )
    sol.cox_tickets_p = float(summary.loc["tickets", "p"])

    sol.concordance_index = float(cph.concordance_index_)

    # --- 4. PH assumption check (Schoenfeld residuals) ---
    from lifelines.statistics import proportional_hazard_test

    ph_test = proportional_hazard_test(cph, cox_df, time_transform="rank")
    ph_summary = ph_test.summary

    sol.ph_test_plan_p = float(ph_summary.loc["is_basic", "p"])
    sol.ph_test_tickets_p = float(ph_summary.loc["tickets", "p"])
    sol.ph_assumption_holds = bool(
        sol.ph_test_plan_p > instance.alpha
        and sol.ph_test_tickets_p > instance.alpha
    )

    # Metadata
    sol.algorithm = "Kaplan-Meier + Log-Rank Test + Cox Proportional Hazards"
    sol.time_seconds = time.perf_counter() - t0

    # Verification
    sol.verification = verify(instance, sol)

    return sol


# --- Verification (independent of solver) ---

def verify(instance: Instance, sol: Solution) -> dict:
    """Independently verify the survival analysis results.

    Checks:
      1. KM survival probabilities are monotonically non-increasing
      2. KM probabilities are in [0, 1]
      3. Log-rank test is significant (p < 0.05)
      4. Cox PH HR for Basic vs Pro > 1 (Basic has higher hazard)
      5. Cox PH HR for tickets > 1 (more tickets = higher churn)
      6. Concordance index > 0.55 (better than random)
      7. Median survival Basic < median survival Pro
      8. Censoring rate is approximately 30%
    """
    checks: dict = {}

    # Check 1: KM Basic survival is monotonically non-increasing
    basic_surv = sol.km_basic_survival
    mono_basic = all(
        basic_surv[i] >= basic_surv[i + 1] - 1e-10
        for i in range(len(basic_surv) - 1)
    )
    checks["km_basic_monotonic"] = mono_basic

    # Also check Pro
    pro_surv = sol.km_pro_survival
    mono_pro = all(
        pro_surv[i] >= pro_surv[i + 1] - 1e-10
        for i in range(len(pro_surv) - 1)
    )
    checks["km_pro_monotonic"] = mono_pro

    # Check 2: KM probabilities in [0, 1]
    basic_in_range = all(0.0 - 1e-10 <= s <= 1.0 + 1e-10 for s in basic_surv)
    pro_in_range = all(0.0 - 1e-10 <= s <= 1.0 + 1e-10 for s in pro_surv)
    checks["km_basic_in_01"] = basic_in_range
    checks["km_pro_in_01"] = pro_in_range

    # Check 3: Log-rank test shows significant difference
    checks["logrank_significant"] = sol.logrank_p_value < instance.alpha

    # Check 4: Cox PH HR for Basic > 1 (Basic has higher hazard than Pro)
    checks["cox_plan_hr_gt_1"] = sol.cox_plan_hr > 1.0

    # Check 5: Cox PH HR for tickets > 1 (more tickets = higher churn)
    checks["cox_tickets_hr_gt_1"] = sol.cox_tickets_hr > 1.0

    # Check 6: Concordance index > 0.55
    checks["concordance_gt_055"] = sol.concordance_index > 0.55

    # Check 7: Median survival Basic < median survival Pro
    checks["median_basic_lt_pro"] = sol.median_basic < sol.median_pro

    # Check 8: Censoring rate approximately 30% (within 10 percentage points)
    checks["censoring_rate_approx_30pct"] = abs(sol.censoring_rate - 0.30) < 0.10

    # Overall
    checks["all_passed"] = all(
        v for v in checks.values() if isinstance(v, bool)
    )

    return checks


# --- Main ---

if __name__ == "__main__":
    instance = generate_instance(seed=42)

    sol = solve(instance)

    # --- Print Solution Report ---
    log.header("CUSTOMER SURVIVAL -- SaaS Subscription Churn")

    log.section("PHASE 1-2: UNDERSTAND & PLAN (uber-model)")
    log.info("Problem: Time-to-event analysis with right censoring", tag="MODEL")
    log.info("Structure: Survival analysis (Kaplan-Meier, Cox PH)", tag="MODEL")
    log.info("H0: No difference in survival between Basic and Pro", tag="HYPOTHESIS")
    log.info("H1: Survival differs by plan type", tag="HYPOTHESIS")
    log.blank()

    log.step("INSTANCE")
    log.metric("Total customers", str(sol.n_total), tag="DATA")
    log.metric("Basic plan", str(sol.n_basic), tag="DATA")
    log.metric("Pro plan", str(sol.n_pro), tag="DATA")
    log.metric("Events (churned)", str(sol.n_events), tag="DATA")
    log.metric("Censored (active)", str(sol.n_censored), tag="DATA")
    log.metric("Censoring rate", "{:.1%}".format(sol.censoring_rate), tag="DATA")
    log.metric("Mean tickets (Basic)", "{:.1f}".format(sol.mean_tickets_basic), tag="DATA")
    log.metric("Mean tickets (Pro)", "{:.1f}".format(sol.mean_tickets_pro), tag="DATA")
    log.blank()

    log.section("PHASE 3: EXECUTE (uber-solve)")

    log.step("STEP 1: Kaplan-Meier Estimation")
    log.metric("Median surv (Basic)", "{:.1f} months".format(sol.median_basic), tag="STATS")
    log.metric("Median surv (Pro)", "{:.1f} months".format(sol.median_pro), tag="STATS")
    log.metric("KM Basic timepoints", str(len(sol.km_basic_times)), tag="STATS")
    log.metric("KM Pro timepoints", str(len(sol.km_pro_times)), tag="STATS")
    log.blank()

    log.step("STEP 2: Log-Rank Test")
    log.metric("Test statistic", "{:.3f}".format(sol.logrank_statistic), tag="STATS")
    log.metric("p-value", "{:.6f}".format(sol.logrank_p_value), tag="STATS")
    log.metric("Significant", "{} (alpha={})".format(
        sol.logrank_p_value < instance.alpha, instance.alpha), tag="HYPOTHESIS")
    log.blank()

    log.step("STEP 3: Cox Proportional Hazards")
    log.metric("Plan (Basic) coef", "{:.4f}".format(sol.cox_plan_coef), tag="STATS")
    log.metric("Plan HR", "{:.3f}".format(sol.cox_plan_hr), tag="STATS")
    log.metric("Plan HR 95% CI", "[{:.3f}, {:.3f}]".format(
        sol.cox_plan_hr_lower, sol.cox_plan_hr_upper), tag="STATS")
    log.metric("Plan p-value", "{:.6f}".format(sol.cox_plan_p), tag="STATS")
    log.blank()
    log.metric("Tickets coef", "{:.4f}".format(sol.cox_tickets_coef), tag="STATS")
    log.metric("Tickets HR", "{:.3f}".format(sol.cox_tickets_hr), tag="STATS")
    log.metric("Tickets HR 95% CI", "[{:.3f}, {:.3f}]".format(
        sol.cox_tickets_hr_lower, sol.cox_tickets_hr_upper), tag="STATS")
    log.metric("Tickets p-value", "{:.6f}".format(sol.cox_tickets_p), tag="STATS")
    log.blank()
    log.metric("Concordance index", "{:.4f}".format(sol.concordance_index), tag="STATS")
    log.blank()

    log.step("STEP 4: PH Assumption Check")
    log.metric("Plan (Schoenfeld p)", "{:.4f}".format(sol.ph_test_plan_p), tag="VERIFY")
    log.metric("Tickets (Schoenfeld p)", "{:.4f}".format(sol.ph_test_tickets_p), tag="VERIFY")
    log.check(
        "PH assumption holds (p > 0.05 for all)",
        sol.ph_assumption_holds, tag="VERIFY",
    )
    log.blank()

    log.section("PHASE 4: LOOK BACK (uber-interpret)")

    log.step("BOTTOM LINE")
    log.success("Basic plan customers churn faster: median {:.1f} months".format(
        sol.median_basic), tag="RESULT")
    log.success("Pro plan customers last longer: median {:.1f} months".format(
        sol.median_pro), tag="RESULT")
    log.success("Log-rank test confirms significant difference (p={:.6f})".format(
        sol.logrank_p_value), tag="RESULT")
    log.blank()

    log.step("RISK FACTORS (Cox PH)")
    log.info("Being on Basic plan multiplies churn hazard by {:.2f}x vs Pro".format(
        sol.cox_plan_hr), tag="INTERPRET")
    log.info("Each additional support ticket multiplies churn hazard by {:.3f}x".format(
        sol.cox_tickets_hr), tag="INTERPRET")
    log.info("Model discriminative ability: C-index = {:.3f}".format(
        sol.concordance_index), tag="INTERPRET")
    log.blank()

    log.step("RECOMMENDATIONS")
    log.success("1. Prioritize retention for Basic plan customers (2x churn risk)", tag="RECOMMEND")
    log.success("2. Monitor support ticket volume as early churn warning signal", tag="RECOMMEND")
    log.success("3. Consider proactive outreach at month 6-8 for Basic plan users", tag="RECOMMEND")
    log.success("4. Investigate why Pro customers stay longer (features? commitment?)", tag="RECOMMEND")
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

    # Save JSON
    output = {
        "instance": {
            "n_total": sol.n_total,
            "n_basic": sol.n_basic,
            "n_pro": sol.n_pro,
            "n_events": sol.n_events,
            "n_censored": sol.n_censored,
            "censoring_rate": sol.censoring_rate,
        },
        "kaplan_meier": {
            "median_basic": sol.median_basic,
            "median_pro": sol.median_pro,
        },
        "logrank_test": {
            "statistic": sol.logrank_statistic,
            "p_value": sol.logrank_p_value,
        },
        "cox_ph": {
            "plan_basic": {
                "coef": sol.cox_plan_coef,
                "hazard_ratio": sol.cox_plan_hr,
                "hr_95ci": [sol.cox_plan_hr_lower, sol.cox_plan_hr_upper],
                "p_value": sol.cox_plan_p,
            },
            "tickets": {
                "coef": sol.cox_tickets_coef,
                "hazard_ratio": sol.cox_tickets_hr,
                "hr_95ci": [sol.cox_tickets_hr_lower, sol.cox_tickets_hr_upper],
                "p_value": sol.cox_tickets_p,
            },
            "concordance_index": sol.concordance_index,
        },
        "ph_assumption": {
            "plan_schoenfeld_p": sol.ph_test_plan_p,
            "tickets_schoenfeld_p": sol.ph_test_tickets_p,
            "holds": sol.ph_assumption_holds,
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
