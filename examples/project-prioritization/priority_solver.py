#!/usr/bin/env python3
"""Project Prioritization solver using Multi-Criteria Decision Analysis (MCDA).

Ranks software features by weighted composite score across multiple criteria.
Supports criterion inversion (lower-is-better), min-max normalization,
and sensitivity analysis on weights.

Complexity: O(n * k) for n features and k criteria.
Correctness: Deterministic weighted scoring, verified independently.
"""
from __future__ import annotations

import time
import json
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
class Criterion:
    """A scoring criterion."""
    name: str
    weight: float
    lower_is_better: bool = False  # if True, invert scores before weighting


@dataclass(frozen=True)
class Instance:
    """Problem instance for project prioritization."""
    features: tuple[str, ...]
    criteria: tuple[Criterion, ...]
    scores: dict[str, dict[str, float]]  # feature -> {criterion_name: raw_score}

    @property
    def n_features(self) -> int:
        return len(self.features)

    @property
    def n_criteria(self) -> int:
        return len(self.criteria)


@dataclass
class Solution:
    """Verified solution with metadata."""
    ranking: list[tuple[str, float]]  # [(feature, composite_score), ...] sorted descending
    normalized_scores: dict[str, dict[str, float]]  # feature -> {criterion: normalized_score}
    weighted_scores: dict[str, dict[str, float]]     # feature -> {criterion: weighted_score}
    objective: float  # top-ranked feature's composite score
    is_optimal: bool
    is_feasible: bool
    algorithm: str
    time_seconds: float
    certificate: str
    constraint_check: dict[str, Any] = field(default_factory=dict)


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Compute MCDA ranking with weighted scoring."""
    t0 = time.perf_counter()

    features = instance.features
    criteria = instance.criteria
    scores = instance.scores
    n = instance.n_features
    k = instance.n_criteria

    # Build raw score matrix (n x k)
    raw = np.zeros((n, k))
    for i, feat in enumerate(features):
        for j, crit in enumerate(criteria):
            raw[i, j] = scores[feat][crit.name]

    # Min-max normalization per criterion to [0, 1]
    normalized = np.zeros_like(raw)
    for j, crit in enumerate(criteria):
        col = raw[:, j]
        col_min = col.min()
        col_max = col.max()
        if col_max - col_min > 0:
            normalized[:, j] = (col - col_min) / (col_max - col_min)
        else:
            normalized[:, j] = 1.0  # all same score -> all get 1.0

        # Invert if lower is better (e.g., development effort)
        if crit.lower_is_better:
            normalized[:, j] = 1.0 - normalized[:, j]

    # Apply weights
    weights = np.array([c.weight for c in criteria])
    weighted = normalized * weights  # element-wise: (n x k) * (k,)

    # Composite scores
    composite = weighted.sum(axis=1)

    # Build output data structures
    normalized_scores: dict[str, dict[str, float]] = {}
    weighted_scores: dict[str, dict[str, float]] = {}
    for i, feat in enumerate(features):
        normalized_scores[feat] = {}
        weighted_scores[feat] = {}
        for j, crit in enumerate(criteria):
            normalized_scores[feat][crit.name] = round(float(normalized[i, j]), 4)
            weighted_scores[feat][crit.name] = round(float(weighted[i, j]), 4)

    # Ranking (descending by composite score)
    ranking_indices = np.argsort(-composite)
    ranking = [(features[i], round(float(composite[i]), 4)) for i in ranking_indices]

    elapsed = time.perf_counter() - t0

    sol = Solution(
        ranking=ranking,
        normalized_scores=normalized_scores,
        weighted_scores=weighted_scores,
        objective=ranking[0][1],
        is_optimal=True,  # deterministic computation
        is_feasible=False,  # verified below
        algorithm="MCDA weighted linear scoring with min-max normalization",
        time_seconds=elapsed,
        certificate="Deterministic: unique ranking for given weights and scores",
    )

    # Independent verification
    sol.is_feasible, sol.constraint_check = verify(instance, ranking, normalized_scores, weighted_scores)

    return sol


# --- Verification (independent of solver) ---

def verify(
    instance: Instance,
    ranking: list[tuple[str, float]],
    normalized_scores: dict[str, dict[str, float]],
    weighted_scores: dict[str, dict[str, float]],
) -> tuple[bool, dict[str, Any]]:
    """Independently verify the MCDA computation."""
    checks: dict[str, Any] = {}
    all_ok = True

    features = instance.features
    criteria = instance.criteria
    scores = instance.scores

    # Check 1: All features present in ranking
    ranked_features = {f for f, _ in ranking}
    ok = ranked_features == set(features)
    checks["all_features_ranked"] = ok
    if not ok:
        all_ok = False

    # Check 2: Weights sum to 1.0
    weight_sum = sum(c.weight for c in criteria)
    ok = abs(weight_sum - 1.0) < 1e-6
    checks["weights_sum_to_one"] = ok
    checks["weight_sum"] = round(weight_sum, 6)
    if not ok:
        all_ok = False

    # Check 3: Normalized scores in [0, 1]
    all_in_range = True
    for feat in features:
        for crit in criteria:
            val = normalized_scores[feat][crit.name]
            if val < -1e-6 or val > 1.0 + 1e-6:
                all_in_range = False
    checks["normalized_in_range"] = all_in_range
    if not all_in_range:
        all_ok = False

    # Check 4: Recompute composite scores independently
    recompute_ok = True
    for feat, reported_score in ranking:
        recomputed = sum(
            weighted_scores[feat][crit.name] for crit in criteria
        )
        if abs(recomputed - reported_score) > 1e-3:
            recompute_ok = False
    checks["composite_scores_match"] = recompute_ok
    if not recompute_ok:
        all_ok = False

    # Check 5: Ranking is sorted descending
    scores_list = [s for _, s in ranking]
    ok = all(scores_list[i] >= scores_list[i + 1] for i in range(len(scores_list) - 1))
    checks["ranking_sorted_descending"] = ok
    if not ok:
        all_ok = False

    # Check 6: Verify weighted = normalized * weight for each entry
    weighted_ok = True
    for feat in features:
        for crit in criteria:
            expected = normalized_scores[feat][crit.name] * crit.weight
            actual = weighted_scores[feat][crit.name]
            if abs(expected - actual) > 1e-3:
                weighted_ok = False
    checks["weighted_equals_norm_times_weight"] = weighted_ok
    if not weighted_ok:
        all_ok = False

    return all_ok, checks


# --- Main ---

if __name__ == "__main__":
    # Build instance: 8 features scored on 4 criteria
    criteria = (
        Criterion("user_impact",        weight=0.40, lower_is_better=False),
        Criterion("dev_effort",         weight=0.25, lower_is_better=True),
        Criterion("strategic_alignment", weight=0.20, lower_is_better=False),
        Criterion("revenue_potential",   weight=0.15, lower_is_better=False),
    )

    features = (
        "Search Revamp",
        "Mobile Push Notifications",
        "Dashboard Analytics",
        "API Rate Limiting",
        "User Onboarding Flow",
        "Payment Integration",
        "Dark Mode",
        "Bulk Export",
    )

    # Raw scores (1-10) for each feature on each criterion
    scores = {
        "Search Revamp":            {"user_impact": 9, "dev_effort": 7, "strategic_alignment": 8, "revenue_potential": 6},
        "Mobile Push Notifications": {"user_impact": 8, "dev_effort": 4, "strategic_alignment": 7, "revenue_potential": 5},
        "Dashboard Analytics":       {"user_impact": 7, "dev_effort": 6, "strategic_alignment": 9, "revenue_potential": 8},
        "API Rate Limiting":         {"user_impact": 4, "dev_effort": 3, "strategic_alignment": 6, "revenue_potential": 3},
        "User Onboarding Flow":      {"user_impact": 9, "dev_effort": 5, "strategic_alignment": 8, "revenue_potential": 9},
        "Payment Integration":       {"user_impact": 6, "dev_effort": 8, "strategic_alignment": 7, "revenue_potential": 10},
        "Dark Mode":                 {"user_impact": 5, "dev_effort": 2, "strategic_alignment": 3, "revenue_potential": 2},
        "Bulk Export":               {"user_impact": 3, "dev_effort": 3, "strategic_alignment": 4, "revenue_potential": 4},
    }

    instance = Instance(features=features, criteria=criteria, scores=scores)
    sol = solve(instance)

    # --- Print Solution Report ---
    log.header("SOLUTION REPORT: Project Prioritization (MCDA)")
    log.metric("Features:", str(instance.n_features), tag="RESULT")
    log.metric("Criteria:", str(instance.n_criteria), tag="RESULT")
    log.metric("Algorithm:", sol.algorithm, tag="SOLVE")
    log.metric("Time:", f"{sol.time_seconds:.6f}s", tag="TIMING")
    log.blank()

    # Criteria weights
    log.step("CRITERIA WEIGHTS")
    for crit in criteria:
        direction = "(lower is better)" if crit.lower_is_better else "(higher is better)"
        log.table_row(
            f"{crit.name:<25} weight={crit.weight:.2f}  {direction}",
            tag="TABLE"
        )
    log.blank()

    # Raw scores
    log.step("RAW SCORES")
    header = f"{'Feature':<28}"
    for crit in criteria:
        short = crit.name[:10]
        header += f" {short:>10}"
    log.table_row(header, tag="TABLE")
    log.divider()

    for feat in features:
        row = f"{feat:<28}"
        for crit in criteria:
            row += f" {scores[feat][crit.name]:>10}"
        log.table_row(row, tag="TABLE")
    log.blank()

    # Normalized scores
    log.step("NORMALIZED SCORES (0-1, effort inverted)")
    header = f"{'Feature':<28}"
    for crit in criteria:
        short = crit.name[:10]
        header += f" {short:>10}"
    log.table_row(header, tag="TABLE")
    log.divider()

    for feat in features:
        row = f"{feat:<28}"
        for crit in criteria:
            val = sol.normalized_scores[feat][crit.name]
            row += f" {val:>10.3f}"
        log.table_row(row, tag="TABLE")
    log.blank()

    # Weighted scores
    log.step("WEIGHTED SCORES")
    header = f"{'Feature':<28}"
    for crit in criteria:
        short = crit.name[:10]
        header += f" {short:>10}"
    header += f" {'TOTAL':>10}"
    log.table_row(header, tag="TABLE")
    log.divider()

    for feat in features:
        row = f"{feat:<28}"
        total = 0.0
        for crit in criteria:
            val = sol.weighted_scores[feat][crit.name]
            row += f" {val:>10.4f}"
            total += val
        row += f" {total:>10.4f}"
        log.table_row(row, tag="TABLE")
    log.blank()

    # Final ranking
    log.step("FINAL RANKING")
    log.table_row(f"{'Rank':>4}  {'Feature':<28} {'Score':>8}", tag="TABLE")
    log.divider()

    for rank, (feat, score) in enumerate(sol.ranking, 1):
        marker = " <-- TOP PRIORITY" if rank == 1 else ""
        log.table_row(f"{rank:>4}. {feat:<28} {score:>8.4f}{marker}", tag="TABLE")
    log.blank()

    # Sensitivity analysis: how robust is the ranking?
    log.step("SENSITIVITY ANALYSIS: Weight Perturbations")
    log.info("Testing if top-ranked feature changes when each weight shifts by +/- 0.1", tag="DATA")
    log.blank()

    base_top = sol.ranking[0][0]
    perturbations = [
        ("user_impact +0.1",        [0.50, 0.20, 0.17, 0.13]),
        ("user_impact -0.1",        [0.30, 0.30, 0.23, 0.17]),
        ("dev_effort +0.1",         [0.35, 0.35, 0.17, 0.13]),
        ("dev_effort -0.1",         [0.45, 0.15, 0.23, 0.17]),
        ("strategic_alignment +0.1", [0.35, 0.22, 0.30, 0.13]),
        ("strategic_alignment -0.1", [0.45, 0.28, 0.10, 0.17]),
        ("revenue_potential +0.1",   [0.35, 0.22, 0.18, 0.25]),
        ("revenue_potential -0.1",   [0.45, 0.28, 0.22, 0.05]),
    ]

    for label, new_weights in perturbations:
        alt_criteria = tuple(
            Criterion(c.name, w, c.lower_is_better)
            for c, w in zip(criteria, new_weights)
        )
        alt_instance = Instance(features=features, criteria=alt_criteria, scores=scores)
        alt_sol = solve(alt_instance)
        alt_top = alt_sol.ranking[0][0]
        changed = "CHANGED" if alt_top != base_top else "stable"
        log.table_row(
            f"  {label:<30} -> top: {alt_top:<28} [{changed}]",
            tag="SENSITIVITY"
        )
    log.blank()

    # Pairwise comparison of top 3
    log.step("TOP 3 HEAD-TO-HEAD COMPARISON")
    top3 = [feat for feat, _ in sol.ranking[:3]]
    for i in range(len(top3)):
        for j in range(i + 1, len(top3)):
            f1, f2 = top3[i], top3[j]
            log.info(f"{f1} vs {f2}:", tag="DATA")
            for crit in criteria:
                v1 = sol.weighted_scores[f1][crit.name]
                v2 = sol.weighted_scores[f2][crit.name]
                winner = f1 if v1 > v2 else (f2 if v2 > v1 else "TIE")
                log.table_row(
                    f"  {crit.name:<25} {v1:.4f} vs {v2:.4f}  -> {winner}",
                    tag="TABLE"
                )
            log.blank()

    # Independent verification
    log.step("INDEPENDENT VERIFICATION")
    for check_name, result in sol.constraint_check.items():
        if isinstance(result, bool):
            log.check(check_name, result, tag="VERIFY")
        else:
            log.check(check_name, result, tag="VERIFY")
    log.blank()

    # Save solution
    output = {
        "ranking": [{"feature": f, "score": s} for f, s in sol.ranking],
        "objective": sol.objective,
        "is_optimal": sol.is_optimal,
        "is_feasible": sol.is_feasible,
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
    }
    with open(Path(__file__).parent / "solution.json", "w") as f:
        json.dump(output, f, indent=2)
    log.success("solution.json", tag="SAVE")
    log.divider(style="thick")
