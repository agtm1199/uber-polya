#!/usr/bin/env python3
"""Vendor Selection solver -- AHP weight derivation + TOPSIS ranking.

Selects the best cloud infrastructure vendor from 5 candidates across 4 criteria
using the Analytic Hierarchy Process (AHP) for weight derivation from pairwise
comparisons, and TOPSIS for final ranking. Includes sensitivity analysis and
weighted-sum cross-validation.

Algorithm: AHP (eigenvalue method) + TOPSIS (ideal-point distance).
Complexity: O(n^2 * k) for n alternatives and k criteria (dominated by matrix ops).
Correctness: Consistency-checked weights, independently verified ranking.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger
log = PolyaLogger()


# --- Data Model ---

@dataclass(frozen=True)
class Instance:
    """Problem instance for vendor selection via AHP + TOPSIS."""
    vendor_names: tuple[str, ...]
    criteria_names: tuple[str, ...]
    is_benefit: tuple[bool, ...]           # True = higher is better, False = lower is better
    pairwise_matrix: np.ndarray            # k x k AHP pairwise comparison matrix
    performance_matrix: np.ndarray         # n x k performance scores (vendors x criteria)

    def __post_init__(self) -> None:
        n = len(self.vendor_names)
        k = len(self.criteria_names)
        assert self.pairwise_matrix.shape == (k, k), "Pairwise matrix must be k x k"
        assert self.performance_matrix.shape == (n, k), "Performance matrix must be n x k"
        assert len(self.is_benefit) == k, "Benefit flags must match criteria count"


@dataclass
class Solution:
    """Verified solution with metadata."""
    ahp_weights: np.ndarray                # k criteria weights from AHP
    lambda_max: float                      # principal eigenvalue
    consistency_index: float               # CI = (lambda_max - n) / (n - 1)
    consistency_ratio: float               # CR = CI / RI
    topsis_scores: np.ndarray              # n closeness coefficients
    topsis_ranking: list[tuple[str, float]]  # [(vendor, score)] sorted descending
    ideal_positive: np.ndarray             # k best values per criterion
    ideal_negative: np.ndarray             # k worst values per criterion
    dist_positive: np.ndarray              # n distances to positive ideal
    dist_negative: np.ndarray              # n distances to negative ideal
    weighted_sum_scores: np.ndarray        # n weighted sum scores for comparison
    weighted_sum_ranking: list[tuple[str, float]]
    sensitivity_results: list[dict[str, Any]]
    objective: float                       # top TOPSIS score
    is_optimal: bool
    is_feasible: bool
    algorithm: str
    time_seconds: float
    certificate: str
    constraint_check: dict[str, Any] = field(default_factory=dict)


# --- AHP: Random Index table (Saaty) ---

AHP_RANDOM_INDEX: dict[int, float] = {
    1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
    6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49,
}


# --- AHP Weight Derivation ---

def ahp_weights(pairwise: np.ndarray) -> tuple[np.ndarray, float, float, float]:
    """Derive criteria weights from AHP pairwise comparison matrix.

    Uses the power method to approximate the principal eigenvector.

    Returns:
        weights: normalized eigenvector (sums to 1)
        lambda_max: principal eigenvalue
        ci: consistency index
        cr: consistency ratio
    """
    n = pairwise.shape[0]

    # Power method: iterate A*v, normalize, repeat
    v = np.ones(n) / n
    for _ in range(100):
        v_new = pairwise @ v
        v_new = v_new / v_new.sum()
        if np.allclose(v, v_new, atol=1e-10):
            break
        v = v_new

    weights = v_new

    # Principal eigenvalue: lambda_max = sum of (A*w)_i / w_i, averaged
    aw = pairwise @ weights
    lambda_max = float(np.mean(aw / weights))

    # Consistency index and ratio
    ci = (lambda_max - n) / (n - 1) if n > 1 else 0.0
    ri = AHP_RANDOM_INDEX.get(n, 1.49)
    cr = ci / ri if ri > 0 else 0.0

    return weights, lambda_max, ci, cr


# --- TOPSIS Ranking ---

def topsis_rank(
    performance: np.ndarray,
    weights: np.ndarray,
    is_benefit: tuple[bool, ...],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Compute TOPSIS scores.

    Returns:
        scores: closeness coefficients for each alternative
        ideal_pos: positive ideal solution
        ideal_neg: negative ideal solution
        dist_pos: distances to positive ideal
        dist_neg: distances to negative ideal
    """
    n, k = performance.shape

    # Step 1: Vector normalization (divide each column by its Euclidean norm)
    norms = np.sqrt((performance ** 2).sum(axis=0))
    # Guard against zero columns
    norms = np.where(norms == 0, 1.0, norms)
    normalized = performance / norms

    # Step 2: Weighted normalized matrix
    weighted = normalized * weights

    # Step 3: Identify ideal and anti-ideal
    ideal_pos = np.zeros(k)
    ideal_neg = np.zeros(k)
    for j in range(k):
        col = weighted[:, j]
        if is_benefit[j]:
            ideal_pos[j] = col.max()
            ideal_neg[j] = col.min()
        else:
            ideal_pos[j] = col.min()
            ideal_neg[j] = col.max()

    # Step 4: Euclidean distances
    dist_pos = np.sqrt(((weighted - ideal_pos) ** 2).sum(axis=1))
    dist_neg = np.sqrt(((weighted - ideal_neg) ** 2).sum(axis=1))

    # Step 5: Closeness coefficient
    scores = dist_neg / (dist_pos + dist_neg)

    return scores, ideal_pos, ideal_neg, dist_pos, dist_neg


# --- Weighted Sum Method (for cross-validation) ---

def weighted_sum_rank(
    performance: np.ndarray,
    weights: np.ndarray,
    is_benefit: tuple[bool, ...],
) -> np.ndarray:
    """Compute weighted sum scores using min-max normalization.

    Returns scores for each alternative (higher is better).
    """
    n, k = performance.shape
    normalized = np.zeros_like(performance, dtype=float)

    for j in range(k):
        col = performance[:, j]
        col_min, col_max = col.min(), col.max()
        if col_max - col_min > 0:
            if is_benefit[j]:
                normalized[:, j] = (col - col_min) / (col_max - col_min)
            else:
                normalized[:, j] = (col_max - col) / (col_max - col_min)
        else:
            normalized[:, j] = 1.0

    scores = (normalized * weights).sum(axis=1)
    return scores


# --- Sensitivity Analysis ---

def sensitivity_analysis(
    performance: np.ndarray,
    base_weights: np.ndarray,
    is_benefit: tuple[bool, ...],
    vendor_names: tuple[str, ...],
    criteria_names: tuple[str, ...],
    delta: float = 0.10,
) -> list[dict[str, Any]]:
    """Vary each weight by +/- delta and check if TOPSIS ranking changes.

    The delta is redistributed proportionally among other criteria so weights
    still sum to 1.
    """
    k = len(base_weights)
    base_scores, _, _, _, _ = topsis_rank(performance, base_weights, is_benefit)
    base_order = list(np.argsort(-base_scores))

    results: list[dict[str, Any]] = []

    for j in range(k):
        for sign, label in [(+1, "+"), (-1, "-")]:
            perturbed = base_weights.copy()
            shift = sign * delta

            # Clamp the perturbed weight to [0.01, 0.99]
            new_wj = np.clip(perturbed[j] + shift, 0.01, 0.99)
            actual_shift = new_wj - perturbed[j]
            perturbed[j] = new_wj

            # Redistribute the shift proportionally among other criteria
            others_sum = perturbed[:j].sum() + perturbed[j+1:].sum()
            if others_sum > 0:
                for i in range(k):
                    if i != j:
                        perturbed[i] -= actual_shift * (perturbed[i] / others_sum)

            # Renormalize to handle floating point drift
            perturbed = perturbed / perturbed.sum()

            new_scores, _, _, _, _ = topsis_rank(performance, perturbed, is_benefit)
            new_order = list(np.argsort(-new_scores))

            top_changed = new_order[0] != base_order[0]
            any_order_change = new_order != base_order

            results.append({
                "criterion": criteria_names[j],
                "direction": label,
                "delta": delta,
                "perturbed_weights": perturbed.tolist(),
                "new_ranking": [vendor_names[i] for i in new_order],
                "new_scores": new_scores.tolist(),
                "top_changed": top_changed,
                "any_change": bool(any(a != b for a, b in zip(new_order, base_order))),
            })

    return results


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Run full AHP + TOPSIS pipeline."""
    t0 = time.perf_counter()

    # Phase 1: AHP weight derivation
    weights, lambda_max, ci, cr = ahp_weights(instance.pairwise_matrix)

    # Phase 2: TOPSIS ranking
    topsis_sc, ideal_pos, ideal_neg, dist_pos, dist_neg = topsis_rank(
        instance.performance_matrix, weights, instance.is_benefit,
    )

    # Phase 3: Weighted sum for cross-validation
    ws_scores = weighted_sum_rank(
        instance.performance_matrix, weights, instance.is_benefit,
    )

    # Phase 4: Sensitivity analysis
    sens = sensitivity_analysis(
        instance.performance_matrix, weights, instance.is_benefit,
        instance.vendor_names, instance.criteria_names,
    )

    # Build rankings
    topsis_order = np.argsort(-topsis_sc)
    topsis_ranking = [
        (instance.vendor_names[i], round(float(topsis_sc[i]), 6))
        for i in topsis_order
    ]

    ws_order = np.argsort(-ws_scores)
    ws_ranking = [
        (instance.vendor_names[i], round(float(ws_scores[i]), 6))
        for i in ws_order
    ]

    elapsed = time.perf_counter() - t0

    sol = Solution(
        ahp_weights=weights,
        lambda_max=lambda_max,
        consistency_index=ci,
        consistency_ratio=cr,
        topsis_scores=topsis_sc,
        topsis_ranking=topsis_ranking,
        ideal_positive=ideal_pos,
        ideal_negative=ideal_neg,
        dist_positive=dist_pos,
        dist_negative=dist_neg,
        weighted_sum_scores=ws_scores,
        weighted_sum_ranking=ws_ranking,
        sensitivity_results=sens,
        objective=topsis_ranking[0][1],
        is_optimal=True,
        is_feasible=False,  # set by verify
        algorithm="AHP (eigenvalue method) + TOPSIS (ideal-point distance)",
        time_seconds=elapsed,
        certificate=f"AHP CR={cr:.4f} < 0.10; TOPSIS top vendor: {topsis_ranking[0][0]}",
    )

    # Independent verification
    sol.is_feasible, sol.constraint_check = verify(instance, sol)

    return sol


# --- Verification (independent of solver) ---

def verify(instance: Instance, sol: Solution) -> tuple[bool, dict[str, Any]]:
    """Independently verify the AHP + TOPSIS computation.

    Recomputes everything from scratch without reusing solver internals.
    """
    checks: dict[str, Any] = {}
    all_ok = True

    n = len(instance.vendor_names)
    k = len(instance.criteria_names)
    perf = instance.performance_matrix

    # --- AHP Checks ---

    # Check 1: AHP weights sum to 1
    w_sum = float(sol.ahp_weights.sum())
    ok = abs(w_sum - 1.0) < 1e-6
    checks["ahp_weights_sum_to_one"] = ok
    checks["ahp_weight_sum_value"] = round(w_sum, 8)
    if not ok:
        all_ok = False

    # Check 2: Consistency ratio below threshold
    ok = sol.consistency_ratio < 0.10
    checks["ahp_cr_below_threshold"] = ok
    checks["ahp_cr_value"] = round(sol.consistency_ratio, 6)
    if not ok:
        all_ok = False

    # Check 3: Recompute eigenvalue independently
    # lambda_max = mean of (A*w)_i / w_i
    aw = instance.pairwise_matrix @ sol.ahp_weights
    recomputed_lambda = float(np.mean(aw / sol.ahp_weights))
    ok = abs(recomputed_lambda - sol.lambda_max) < 1e-6
    checks["ahp_eigenvalue_recomputed_matches"] = ok
    checks["ahp_eigenvalue_recomputed"] = round(recomputed_lambda, 6)
    checks["ahp_eigenvalue_reported"] = round(sol.lambda_max, 6)
    if not ok:
        all_ok = False

    # Check 4: Pairwise matrix reciprocity (a_ij * a_ji = 1)
    reciprocal_ok = True
    for i in range(k):
        for j in range(k):
            prod = instance.pairwise_matrix[i, j] * instance.pairwise_matrix[j, i]
            if abs(prod - 1.0) > 1e-6:
                reciprocal_ok = False
    checks["ahp_pairwise_reciprocal"] = reciprocal_ok
    if not reciprocal_ok:
        all_ok = False

    # --- TOPSIS Checks ---

    # Check 5: Recompute ideal and anti-ideal from scratch
    norms = np.sqrt((perf ** 2).sum(axis=0))
    norms = np.where(norms == 0, 1.0, norms)
    norm_matrix = perf / norms
    weighted_matrix = norm_matrix * sol.ahp_weights

    recomp_ideal_pos = np.zeros(k)
    recomp_ideal_neg = np.zeros(k)
    for j in range(k):
        col = weighted_matrix[:, j]
        if instance.is_benefit[j]:
            recomp_ideal_pos[j] = col.max()
            recomp_ideal_neg[j] = col.min()
        else:
            recomp_ideal_pos[j] = col.min()
            recomp_ideal_neg[j] = col.max()

    ok = np.allclose(recomp_ideal_pos, sol.ideal_positive, atol=1e-6)
    checks["topsis_ideal_positive_correct"] = bool(ok)
    if not ok:
        all_ok = False

    ok = np.allclose(recomp_ideal_neg, sol.ideal_negative, atol=1e-6)
    checks["topsis_ideal_negative_correct"] = bool(ok)
    if not ok:
        all_ok = False

    # Check 6: Recompute TOPSIS scores from scratch
    recomp_dist_pos = np.sqrt(((weighted_matrix - recomp_ideal_pos) ** 2).sum(axis=1))
    recomp_dist_neg = np.sqrt(((weighted_matrix - recomp_ideal_neg) ** 2).sum(axis=1))
    recomp_scores = recomp_dist_neg / (recomp_dist_pos + recomp_dist_neg)

    ok = np.allclose(recomp_scores, sol.topsis_scores, atol=1e-6)
    checks["topsis_scores_recomputed_match"] = bool(ok)
    if not ok:
        all_ok = False

    # Check 7: No vendor dominates another on ALL criteria (trade-offs exist)
    dominance_found = False
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            # Check if vendor i dominates vendor j on every criterion
            dominates = True
            for c in range(k):
                if instance.is_benefit[c]:
                    if perf[i, c] <= perf[j, c]:
                        dominates = False
                        break
                else:
                    if perf[i, c] >= perf[j, c]:
                        dominates = False
                        break
            if dominates:
                dominance_found = True
                break
        if dominance_found:
            break
    checks["no_full_dominance_tradeoffs_exist"] = not dominance_found
    if dominance_found:
        all_ok = False

    # Check 8: Sensitivity thresholds are valid (all perturbed weights sum to 1)
    sens_weights_ok = True
    for entry in sol.sensitivity_results:
        pw = np.array(entry["perturbed_weights"])
        if abs(pw.sum() - 1.0) > 1e-4 or (pw < 0).any():
            sens_weights_ok = False
    checks["sensitivity_weights_valid"] = sens_weights_ok
    if not sens_weights_ok:
        all_ok = False

    # Check 9: TOPSIS scores in [0, 1]
    ok = bool((sol.topsis_scores >= -1e-6).all() and (sol.topsis_scores <= 1.0 + 1e-6).all())
    checks["topsis_scores_in_unit_range"] = ok
    if not ok:
        all_ok = False

    # Check 10: Rankings are sorted descending
    topsis_vals = [s for _, s in sol.topsis_ranking]
    ok = all(topsis_vals[i] >= topsis_vals[i + 1] - 1e-9 for i in range(len(topsis_vals) - 1))
    checks["topsis_ranking_sorted"] = ok
    if not ok:
        all_ok = False

    return all_ok, checks


# --- Main ---

if __name__ == "__main__":
    # ========================================================================
    # Problem Setup: 5 cloud vendors, 4 criteria
    # ========================================================================

    vendor_names = (
        "CloudPeak",     # AWS-like: broad, premium pricing
        "NimbusForge",   # Azure-like: strong enterprise security
        "SkyGrid",       # GCP-like: high performance, moderate cost
        "DataSphere",    # DigitalOcean-like: low cost, simpler offerings
        "CoreVault",     # Linode-like: good support, competitive pricing
    )

    criteria_names = ("Cost", "Performance", "Security", "Support")

    # Cost is a cost criterion (lower is better); the rest are benefit criteria
    is_benefit = (False, True, True, True)

    # AHP Pairwise Comparison Matrix (criteria vs criteria)
    # Scale: 1 = equal, 3 = moderate, 5 = strong, 7 = very strong, 9 = extreme
    # Judgments reflect target weights ~(25%, 30%, 25%, 20%):
    #   Cost vs Performance:  Performance slightly more important (1/2)
    #   Cost vs Security:     Equal importance (1)
    #   Cost vs Support:      Cost slightly more important (3/2)
    #   Performance vs Security: Performance slightly more important (3/2)
    #   Performance vs Support:  Performance moderately more important (2)
    #   Security vs Support:  Security slightly more important (3/2)
    pairwise = np.array([
        # Cost   Perf   Sec    Supp
        [1,      2/3,   1,     3/2 ],   # Cost
        [3/2,    1,     3/2,   2   ],   # Performance
        [1,      2/3,   1,     3/2 ],   # Security
        [2/3,    1/2,   2/3,   1   ],   # Support
    ], dtype=float)

    # Performance Matrix: 5 vendors x 4 criteria
    # Cost: monthly spend in $thousands (lower is better)
    # Performance: benchmark throughput score 0-100 (higher is better)
    # Security: compliance/audit score 0-100 (higher is better)
    # Support: SLA quality score 0-100 (higher is better)
    performance = np.array([
        # Cost($K)  Perf   Security  Support
        [18.5,      92,    88,       78],    # CloudPeak: premium, excellent perf
        [16.0,      85,    95,       82],    # NimbusForge: strong security, good support
        [14.0,      94,    82,       70],    # SkyGrid: best perf, lower security
        [ 8.5,      72,    70,       65],    # DataSphere: cheapest, decent
        [11.0,      78,    80,       90],    # CoreVault: best support, competitive
    ], dtype=float)

    instance = Instance(
        vendor_names=vendor_names,
        criteria_names=criteria_names,
        is_benefit=is_benefit,
        pairwise_matrix=pairwise,
        performance_matrix=performance,
    )

    sol = solve(instance)

    # ========================================================================
    # Solution Report
    # ========================================================================

    log.header("SOLUTION REPORT: Vendor Selection (AHP + TOPSIS)")

    log.step("PROBLEM SETUP")
    log.metric("Vendors:", str(len(vendor_names)), tag="DATA")
    log.metric("Criteria:", str(len(criteria_names)), tag="DATA")
    for i, name in enumerate(criteria_names):
        kind = "benefit (higher=better)" if is_benefit[i] else "cost (lower=better)"
        log.info(f"  {name:<15} [{kind}]", tag="DATA")
    log.blank()

    log.metric("Algorithm:", sol.algorithm, tag="SOLVE")
    log.metric("Time:", f"{sol.time_seconds:.6f}s", tag="TIMING")
    log.blank()

    # --- AHP Results ---
    log.step("PHASE 1: AHP WEIGHT DERIVATION")

    log.info("Pairwise Comparison Matrix (Saaty scale 1-9):", tag="MODEL")
    header = f"{'':>14}"
    for name in criteria_names:
        header += f" {name:>10}"
    log.table_row(header, tag="TABLE")
    log.divider()
    for i, name in enumerate(criteria_names):
        row = f"{name:>14}"
        for j in range(len(criteria_names)):
            val = pairwise[i, j]
            # Display as fraction if close to a simple ratio, else as decimal
            if abs(val - round(val)) < 1e-6:
                row += f" {val:>10.0f}"
            elif abs(val - 1.5) < 1e-6:
                row += f" {'3/2':>10}"
            elif abs(val - 2/3) < 1e-6:
                row += f" {'2/3':>10}"
            elif val < 1 and abs(1/val - round(1/val)) < 1e-6:
                row += f" {f'1/{1/val:.0f}':>10}"
            else:
                row += f" {val:>10.2f}"
        log.table_row(row, tag="TABLE")
    log.blank()

    log.info("Derived Criteria Weights:", tag="RESULT")
    for i, name in enumerate(criteria_names):
        pct = sol.ahp_weights[i] * 100
        log.bar(f"{name:<14}", sol.ahp_weights[i], max_width=30, tag="RESULT")
    log.blank()

    log.metric("Lambda max:", f"{sol.lambda_max:.6f}", tag="STATS")
    log.metric("Consistency Index:", f"{sol.consistency_index:.6f}", tag="STATS")
    log.metric("Consistency Ratio:", f"{sol.consistency_ratio:.6f}", tag="STATS")
    cr_status = "PASS (< 0.10)" if sol.consistency_ratio < 0.10 else "FAIL (>= 0.10)"
    log.metric("CR Check:", cr_status, tag="VERIFY")
    log.blank()

    # --- Performance Matrix ---
    log.step("PHASE 2: PERFORMANCE MATRIX")
    header = f"{'Vendor':<14}"
    for name in criteria_names:
        header += f" {name:>12}"
    log.table_row(header, tag="TABLE")
    log.divider()
    for i, vendor in enumerate(vendor_names):
        row = f"{vendor:<14}"
        for j, name in enumerate(criteria_names):
            val = performance[i, j]
            if name == "Cost":
                row += f" ${val:>10.1f}K"
            else:
                row += f" {val:>12.0f}"
        log.table_row(row, tag="TABLE")
    log.blank()

    # --- TOPSIS Results ---
    log.step("PHASE 3: TOPSIS RANKING")

    log.info("Ideal Positive Solution (best per criterion):", tag="MODEL")
    for j, name in enumerate(criteria_names):
        val = sol.ideal_positive[j]
        log.info(f"  {name:<14} {val:.6f}", tag="MODEL")
    log.blank()

    log.info("Ideal Negative Solution (worst per criterion):", tag="MODEL")
    for j, name in enumerate(criteria_names):
        val = sol.ideal_negative[j]
        log.info(f"  {name:<14} {val:.6f}", tag="MODEL")
    log.blank()

    log.info("Distances and Closeness Coefficients:", tag="RESULT")
    log.table_row(
        f"{'Vendor':<14} {'D+':<12} {'D-':<12} {'Score':<10} {'Rank':<6}",
        tag="TABLE",
    )
    log.divider()

    # Sort by TOPSIS score for display
    order = np.argsort(-sol.topsis_scores)
    for rank, idx in enumerate(order, 1):
        vendor = vendor_names[idx]
        marker = " <-- BEST" if rank == 1 else ""
        log.table_row(
            f"{vendor:<14} {sol.dist_positive[idx]:<12.6f} "
            f"{sol.dist_negative[idx]:<12.6f} "
            f"{sol.topsis_scores[idx]:<10.6f} #{rank}{marker}",
            tag="RESULT" if rank == 1 else "TABLE",
        )
    log.blank()

    # --- Weighted Sum Cross-Validation ---
    log.step("PHASE 4: WEIGHTED SUM CROSS-VALIDATION")
    log.table_row(
        f"{'Rank':<6} {'Vendor':<14} {'TOPSIS Score':<14} {'WS Score':<14}",
        tag="TABLE",
    )
    log.divider()
    for rank, (vendor, t_score) in enumerate(sol.topsis_ranking, 1):
        # Find WS score for same vendor
        ws_score = next(s for v, s in sol.weighted_sum_ranking if v == vendor)
        log.table_row(
            f"#{rank:<5} {vendor:<14} {t_score:<14.6f} {ws_score:<14.6f}",
            tag="TABLE",
        )
    log.blank()

    topsis_top = sol.topsis_ranking[0][0]
    ws_top = sol.weighted_sum_ranking[0][0]
    if topsis_top == ws_top:
        log.success(
            f"Both methods agree: {topsis_top} is the top vendor",
            tag="VERIFY",
        )
    else:
        log.warning(
            f"Methods disagree: TOPSIS={topsis_top}, Weighted Sum={ws_top}",
            tag="WARNING",
        )
    log.blank()

    # --- Sensitivity Analysis ---
    log.step("PHASE 5: SENSITIVITY ANALYSIS (weight +/-10%)")

    any_top_changed = False
    log.table_row(
        f"{'Perturbation':<22} {'Top Vendor':<16} {'Top Changed?':<14} {'Any Change?':<12}",
        tag="TABLE",
    )
    log.divider()
    for entry in sol.sensitivity_results:
        label = f"{entry['criterion']} {entry['direction']}{entry['delta']:.0%}"
        top_v = entry["new_ranking"][0]
        top_ch = "YES" if entry["top_changed"] else "no"
        any_ch = "YES" if entry["any_change"] else "no"
        tag = "WARNING" if entry["top_changed"] else "SENSITIVITY"
        log.table_row(
            f"{label:<22} {top_v:<16} {top_ch:<14} {any_ch:<12}",
            tag=tag,
        )
        if entry["top_changed"]:
            any_top_changed = True
    log.blank()

    if any_top_changed:
        log.warning(
            "Ranking is SENSITIVE: top vendor changes under some perturbations",
            tag="SENSITIVITY",
        )
    else:
        log.success(
            "Ranking is ROBUST: top vendor is stable across all +/-10% perturbations",
            tag="SENSITIVITY",
        )
    log.blank()

    # --- Business Interpretation ---
    log.step("BUSINESS INTERPRETATION")
    best_vendor = sol.topsis_ranking[0][0]
    best_score = sol.topsis_ranking[0][1]
    second_vendor = sol.topsis_ranking[1][0]
    second_score = sol.topsis_ranking[1][1]
    gap = best_score - second_score

    log.info(f"Recommended vendor: {best_vendor} (TOPSIS score: {best_score:.4f})", tag="RECOMMEND")
    log.info(f"Runner-up: {second_vendor} (TOPSIS score: {second_score:.4f})", tag="RECOMMEND")
    log.info(f"Score gap: {gap:.4f} ({gap / best_score * 100:.1f}% of top score)", tag="RECOMMEND")
    log.blank()

    if gap < 0.05:
        log.warning("Score gap is small -- consider negotiation leverage with both vendors", tag="INTERPRET")
    else:
        log.info("Score gap is meaningful -- clear winner identified", tag="INTERPRET")
    log.blank()

    # Show top vendor's profile
    best_idx = list(vendor_names).index(best_vendor)
    log.info(f"{best_vendor} profile:", tag="DATA")
    for j, name in enumerate(criteria_names):
        val = performance[best_idx, j]
        if name == "Cost":
            log.info(f"  {name:<14} ${val:.1f}K/month", tag="DATA")
        else:
            log.info(f"  {name:<14} {val:.0f}/100", tag="DATA")
    log.blank()

    # --- Independent Verification ---
    log.step("INDEPENDENT VERIFICATION")
    for check_name, result in sol.constraint_check.items():
        if isinstance(result, bool):
            log.check(check_name, result, tag="VERIFY")
        else:
            log.check(check_name, result, tag="VERIFY")
    log.blank()

    log.divider(style="thick")

    # --- Save JSON ---
    output = {
        "recommended_vendor": sol.topsis_ranking[0][0],
        "topsis_ranking": [
            {"vendor": v, "score": round(s, 6)} for v, s in sol.topsis_ranking
        ],
        "weighted_sum_ranking": [
            {"vendor": v, "score": round(s, 6)} for v, s in sol.weighted_sum_ranking
        ],
        "ahp_weights": {
            name: round(float(sol.ahp_weights[i]), 6)
            for i, name in enumerate(criteria_names)
        },
        "consistency_ratio": round(sol.consistency_ratio, 6),
        "lambda_max": round(sol.lambda_max, 6),
        "sensitivity": {
            "any_top_change": any_top_changed,
            "perturbation_count": len(sol.sensitivity_results),
        },
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
        "is_feasible": sol.is_feasible,
    }
    with open(Path(__file__).parent / "solution.json", "w") as f:
        json.dump(output, f, indent=2)
    log.success("solution.json", tag="SAVE")
