#!/usr/bin/env python3
"""Nash Equilibrium solver -- Coffee Shop Pricing Game.

Models two competing coffee shops choosing pricing strategies simultaneously
as a normal-form game. Finds all Nash equilibria (pure and mixed) via support
enumeration, checks for dominant strategies, computes best responses, and
analyzes minimax strategies.

Algorithm: Support enumeration (nashpy library).
Complexity: O(2^n * 2^m) worst case for n x m game; negligible for small games.
Correctness: Each equilibrium verified independently via no-profitable-deviation check.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import nashpy as nash

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger
log = PolyaLogger()


# --- Data Model ---

@dataclass(frozen=True)
class Instance:
    """Problem instance for a 2-player normal-form game."""
    payoff_A: np.ndarray          # payoff matrix for Player 1 (row player)
    payoff_B: np.ndarray          # payoff matrix for Player 2 (column player)
    row_labels: tuple[str, ...]   # strategy names for Player 1
    col_labels: tuple[str, ...]   # strategy names for Player 2
    player_names: tuple[str, str] = ("Shop 1", "Shop 2")
    game_name: str = "Coffee Shop Pricing"

    def __post_init__(self) -> None:
        assert self.payoff_A.shape == self.payoff_B.shape, "Payoff matrices must match"
        assert self.payoff_A.shape[0] == len(self.row_labels), "Row labels must match rows"
        assert self.payoff_A.shape[1] == len(self.col_labels), "Col labels must match cols"


@dataclass
class Equilibrium:
    """A single Nash equilibrium."""
    sigma_1: np.ndarray            # mixed strategy for Player 1
    sigma_2: np.ndarray            # mixed strategy for Player 2
    payoff_1: float                # expected payoff for Player 1
    payoff_2: float                # expected payoff for Player 2
    is_pure: bool                  # True if both strategies are pure
    support_1: list[str]           # strategies in Player 1's support
    support_2: list[str]           # strategies in Player 2's support


@dataclass
class Solution:
    """Verified solution with metadata."""
    equilibria: list[Equilibrium]
    num_equilibria: int
    dominant_strategies: dict[str, str | None]   # player -> dominant strategy or None
    best_responses: dict[str, dict[str, str]]    # player -> {opponent_strategy: best_response}
    minimax_value_1: float | None
    minimax_value_2: float | None
    minimax_strategy_1: np.ndarray | None
    minimax_strategy_2: np.ndarray | None
    is_zero_sum: bool
    algorithm: str
    time_seconds: float
    constraint_check: dict[str, Any] = field(default_factory=dict)


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Find all Nash equilibria and analyze the game."""
    t0 = time.perf_counter()

    A = instance.payoff_A
    B = instance.payoff_B
    n_rows, n_cols = A.shape

    # Create nashpy Game object
    game = nash.Game(A, B)

    # --- 1. Find all Nash equilibria via support enumeration ---
    equilibria: list[Equilibrium] = []
    for eq in game.support_enumeration():
        sigma_1, sigma_2 = eq
        # Ensure valid probability distributions (clamp tiny negatives from numerics)
        sigma_1 = np.maximum(sigma_1, 0.0)
        sigma_2 = np.maximum(sigma_2, 0.0)
        if sigma_1.sum() > 0:
            sigma_1 /= sigma_1.sum()
        if sigma_2.sum() > 0:
            sigma_2 /= sigma_2.sum()

        payoff_1 = float(sigma_1 @ A @ sigma_2)
        payoff_2 = float(sigma_1 @ B @ sigma_2)
        is_pure = (np.count_nonzero(sigma_1 > 1e-10) == 1 and
                   np.count_nonzero(sigma_2 > 1e-10) == 1)

        support_1 = [instance.row_labels[i] for i in range(n_rows) if sigma_1[i] > 1e-10]
        support_2 = [instance.col_labels[j] for j in range(n_cols) if sigma_2[j] > 1e-10]

        equilibria.append(Equilibrium(
            sigma_1=sigma_1,
            sigma_2=sigma_2,
            payoff_1=payoff_1,
            payoff_2=payoff_2,
            is_pure=is_pure,
            support_1=support_1,
            support_2=support_2,
        ))

    # --- 2. Check for dominant strategies ---
    dominant_strategies: dict[str, str | None] = {}

    # Player 1 (row player): strategy i dominates strategy j if A[i,k] > A[j,k] for all k
    dom_1 = _find_dominant_strategy(A, instance.row_labels)
    dominant_strategies[instance.player_names[0]] = dom_1

    # Player 2 (column player): transpose so columns become rows
    dom_2 = _find_dominant_strategy(B.T, instance.col_labels)
    dominant_strategies[instance.player_names[1]] = dom_2

    # --- 3. Best responses ---
    best_responses: dict[str, dict[str, str]] = {}

    # Player 1's best response to each of Player 2's pure strategies
    br_1: dict[str, str] = {}
    for j in range(n_cols):
        best_row = int(np.argmax(A[:, j]))
        br_1[instance.col_labels[j]] = instance.row_labels[best_row]
    best_responses[instance.player_names[0]] = br_1

    # Player 2's best response to each of Player 1's pure strategies
    br_2: dict[str, str] = {}
    for i in range(n_rows):
        best_col = int(np.argmax(B[i, :]))
        br_2[instance.row_labels[i]] = instance.col_labels[best_col]
    best_responses[instance.player_names[1]] = br_2

    # --- 4. Check zero-sum and compute minimax ---
    is_zero_sum = bool(np.allclose(A + B, 0))

    # Compute security levels (maximin values) for each player
    minimax_val_1, minimax_strat_1 = _compute_maximin(A, n_rows, n_cols)
    minimax_val_2, minimax_strat_2 = _compute_maximin(B.T, n_cols, n_rows)

    elapsed = time.perf_counter() - t0

    sol = Solution(
        equilibria=equilibria,
        num_equilibria=len(equilibria),
        dominant_strategies=dominant_strategies,
        best_responses=best_responses,
        minimax_value_1=minimax_val_1,
        minimax_value_2=minimax_val_2,
        minimax_strategy_1=minimax_strat_1,
        minimax_strategy_2=minimax_strat_2,
        is_zero_sum=is_zero_sum,
        algorithm="Support Enumeration (nashpy)",
        time_seconds=elapsed,
    )

    # Independent verification
    sol.constraint_check = verify(instance, sol)

    return sol


def _find_dominant_strategy(
    payoff_matrix: np.ndarray, labels: tuple[str, ...]
) -> str | None:
    """Find a strictly dominant strategy for the row player, if one exists.

    Strategy i strictly dominates strategy j if payoff_matrix[i, k] > payoff_matrix[j, k]
    for all k.
    """
    n = payoff_matrix.shape[0]
    for i in range(n):
        dominates_all = True
        for j in range(n):
            if i == j:
                continue
            if not np.all(payoff_matrix[i, :] > payoff_matrix[j, :]):
                dominates_all = False
                break
        if dominates_all:
            return labels[i]
    return None


def _find_weakly_dominated(
    payoff_matrix: np.ndarray, labels: tuple[str, ...]
) -> list[tuple[str, str]]:
    """Find all weakly dominated strategies for the row player.

    Returns list of (dominated, dominator) pairs.
    Strategy i weakly dominates j if payoff_matrix[i,k] >= payoff_matrix[j,k] for all k
    and strict inequality for at least one k.
    """
    n = payoff_matrix.shape[0]
    dominated: list[tuple[str, str]] = []
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if (np.all(payoff_matrix[i, :] >= payoff_matrix[j, :])
                    and np.any(payoff_matrix[i, :] > payoff_matrix[j, :])):
                dominated.append((labels[j], labels[i]))
    return dominated


def _compute_maximin(
    payoff: np.ndarray, n_own: int, n_opp: int
) -> tuple[float, np.ndarray]:
    """Compute maximin value and strategy via linear programming.

    Finds max v subject to: sum_i sigma[i] * payoff[i, j] >= v for all j,
    sum_i sigma[i] = 1, sigma[i] >= 0.
    """
    from scipy.optimize import linprog

    # Minimize -v (equivalently maximize v):
    #   variables: [sigma_0, ..., sigma_{n-1}, v]
    #   Inequality: -payoff^T @ sigma + v*1 <= 0 for each opponent pure strategy
    #   Equality: sum(sigma) = 1

    c = np.zeros(n_own + 1)
    c[-1] = -1.0  # minimize -v

    A_ub = np.zeros((n_opp, n_own + 1))
    A_ub[:, :n_own] = -payoff.T
    A_ub[:, -1] = 1.0
    b_ub = np.zeros(n_opp)

    A_eq = np.zeros((1, n_own + 1))
    A_eq[0, :n_own] = 1.0
    b_eq = np.array([1.0])

    bounds = [(0, None)] * n_own + [(None, None)]

    result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds,
                     method="highs")

    if result.success:
        sigma = result.x[:n_own]
        v = result.x[-1]
        return float(v), sigma
    else:
        # Fallback: pure strategy maximin
        min_payoffs = payoff.min(axis=1)
        best = int(np.argmax(min_payoffs))
        sigma = np.zeros(n_own)
        sigma[best] = 1.0
        return float(min_payoffs[best]), sigma


# --- Verification (independent of solver) ---

def verify(instance: Instance, sol: Solution) -> dict[str, Any]:
    """Independently verify all equilibria and solution properties.

    Does NOT reuse any solver logic. Recomputes everything from the payoff matrices.
    """
    checks: dict[str, Any] = {}
    A = instance.payoff_A
    B = instance.payoff_B
    n_rows, n_cols = A.shape
    all_ok = True

    # Check 1: Each equilibrium is a valid Nash equilibrium (no profitable deviation)
    for idx, eq in enumerate(sol.equilibria):
        prefix = f"eq{idx}"

        # 1a. Probabilities sum to 1
        sum_1 = float(eq.sigma_1.sum())
        sum_2 = float(eq.sigma_2.sum())
        ok_sum_1 = abs(sum_1 - 1.0) < 1e-8
        ok_sum_2 = abs(sum_2 - 1.0) < 1e-8
        checks[f"{prefix}_probs_sum_1_p1"] = ok_sum_1
        checks[f"{prefix}_probs_sum_1_p2"] = ok_sum_2
        if not (ok_sum_1 and ok_sum_2):
            all_ok = False

        # 1b. All probabilities non-negative
        ok_nonneg_1 = bool(np.all(eq.sigma_1 >= -1e-10))
        ok_nonneg_2 = bool(np.all(eq.sigma_2 >= -1e-10))
        checks[f"{prefix}_nonneg_p1"] = ok_nonneg_1
        checks[f"{prefix}_nonneg_p2"] = ok_nonneg_2
        if not (ok_nonneg_1 and ok_nonneg_2):
            all_ok = False

        # 1c. Recompute expected payoffs independently
        ep1 = float(eq.sigma_1 @ A @ eq.sigma_2)
        ep2 = float(eq.sigma_1 @ B @ eq.sigma_2)
        ok_pay_1 = abs(ep1 - eq.payoff_1) < 1e-8
        ok_pay_2 = abs(ep2 - eq.payoff_2) < 1e-8
        checks[f"{prefix}_payoff_p1_correct"] = ok_pay_1
        checks[f"{prefix}_payoff_p2_correct"] = ok_pay_2
        if not (ok_pay_1 and ok_pay_2):
            all_ok = False

        # 1d. No profitable deviation for Player 1
        max_dev_1 = 0.0
        for i in range(n_rows):
            payoff_if_deviate = float(A[i, :] @ eq.sigma_2)
            deviation_gain = payoff_if_deviate - ep1
            max_dev_1 = max(max_dev_1, deviation_gain)
        ok_no_dev_1 = max_dev_1 < 1e-6
        checks[f"{prefix}_no_profitable_deviation_p1"] = ok_no_dev_1
        checks[f"{prefix}_max_deviation_gain_p1"] = round(max_dev_1, 8)
        if not ok_no_dev_1:
            all_ok = False

        # 1e. No profitable deviation for Player 2
        max_dev_2 = 0.0
        for j in range(n_cols):
            payoff_if_deviate = float(eq.sigma_1 @ B[:, j])
            deviation_gain = payoff_if_deviate - ep2
            max_dev_2 = max(max_dev_2, deviation_gain)
        ok_no_dev_2 = max_dev_2 < 1e-6
        checks[f"{prefix}_no_profitable_deviation_p2"] = ok_no_dev_2
        checks[f"{prefix}_max_deviation_gain_p2"] = round(max_dev_2, 8)
        if not ok_no_dev_2:
            all_ok = False

        # 1f. Indifference condition: strategies in the support yield same expected payoff
        payoffs_per_row = A @ eq.sigma_2
        support_payoffs_1 = [payoffs_per_row[i] for i in range(n_rows)
                             if eq.sigma_1[i] > 1e-10]
        if len(support_payoffs_1) > 1:
            ok_indiff_1 = bool(np.max(support_payoffs_1) - np.min(support_payoffs_1) < 1e-6)
        else:
            ok_indiff_1 = True
        checks[f"{prefix}_indifference_condition_p1"] = ok_indiff_1
        if not ok_indiff_1:
            all_ok = False

        payoffs_per_col = eq.sigma_1 @ B
        support_payoffs_2 = [payoffs_per_col[j] for j in range(n_cols)
                             if eq.sigma_2[j] > 1e-10]
        if len(support_payoffs_2) > 1:
            ok_indiff_2 = bool(np.max(support_payoffs_2) - np.min(support_payoffs_2) < 1e-6)
        else:
            ok_indiff_2 = True
        checks[f"{prefix}_indifference_condition_p2"] = ok_indiff_2
        if not ok_indiff_2:
            all_ok = False

    # Check 2: At least one equilibrium found (Nash's theorem guarantees existence)
    checks["num_equilibria_positive"] = sol.num_equilibria > 0
    if sol.num_equilibria == 0:
        all_ok = False

    # Check 3: Cross-validate with vertex enumeration for small games
    if n_rows <= 4 and n_cols <= 4:
        game_check = nash.Game(A, B)
        vertex_eqs = list(game_check.vertex_enumeration())
        checks["vertex_enum_count"] = len(vertex_eqs)
        # Support enumeration should find at least as many as vertex enumeration
        checks["support_enum_found_all"] = sol.num_equilibria >= len(vertex_eqs)

    # Check 4: Zero-sum classification is correct
    checks["zero_sum_correct"] = bool(np.allclose(A + B, 0)) == sol.is_zero_sum

    checks["all_checks_pass"] = all_ok
    return checks


# --- Instances ---

def make_2x2_instance() -> Instance:
    """2x2 Coffee Shop Pricing Game (Anti-coordination / Chicken variant).

    Strategies: Discount, Hold
    Payoffs in $1000s/month profit.

    Story:
    - Both Discount: destructive price war, thin margins ($2k each)
    - Both Hold: comfortable market sharing ($4k each)
    - One Discounts, other Holds: discounter captures customers ($5k),
      holder loses traffic ($3k)

    Game structure (anti-coordination):
    - Each shop prefers to do the opposite of the competitor
    - If competitor discounts -> hold prices (avoid price war)
    - If competitor holds -> discount (steal market share)
    - Result: 2 pure NE + 1 mixed NE

    Hand-verified equilibria:
    - Pure NE 1: (Discount, Hold) with payoffs ($5k, $3k)
    - Pure NE 2: (Hold, Discount) with payoffs ($3k, $5k)
    - Mixed NE:  each plays (1/2, 1/2) with expected payoffs ($3.5k, $3.5k)
    """
    #                    Discount  Hold
    A = np.array([
        [2.0,           5.0],    # Shop 1 plays Discount
        [3.0,           4.0],    # Shop 1 plays Hold
    ])
    B = np.array([
        [2.0,           3.0],    # Shop 2 when Shop 1 Discounts
        [5.0,           4.0],    # Shop 2 when Shop 1 Holds
    ])
    return Instance(
        payoff_A=A,
        payoff_B=B,
        row_labels=("Discount", "Hold"),
        col_labels=("Discount", "Hold"),
        player_names=("Shop 1", "Shop 2"),
        game_name="2x2 Coffee Shop Pricing (Anti-coordination)",
    )


def make_3x3_instance() -> Instance:
    """3x3 Coffee Shop Pricing Game with Loyalty Program option.

    Strategies: Discount, Hold, Loyalty
    Payoffs in $1000s/month profit.

    Story (circular dominance, like Rock-Paper-Scissors with cooperative diagonal):
    - Discount beats Hold: discounter captures price-sensitive switchers ($6k),
      holder loses walk-in traffic ($1k)
    - Hold beats Loyalty: holder saves costs while loyalty program is expensive
      and slow to convert new customers ($7k holder, $2k loyalty)
    - Loyalty beats Discount: loyalty retains committed regulars who ignore
      competitor promos ($5k loyalty, $2k discounter)
    - Same strategy: moderate payoffs from shared market segment

    This is a symmetric game (B = A^T) with circular best-response structure:
    - Best response to Discount is Loyalty
    - Best response to Hold is Discount
    - Best response to Loyalty is Hold
    - No pure-strategy Nash equilibrium exists
    - Unique fully-mixed Nash equilibrium at (3/7, 1/3, 5/21) for each player

    Hand-verified:
    - Mixed NE: p_discount=3/7, p_hold=1/3, p_loyalty=5/21
    - Expected payoff at NE: 79/21 ~ $3.762k/month each
    """
    #                    Discount   Hold     Loyalty
    A = np.array([
        [3.0,           6.0,       2.0],    # Shop 1 plays Discount
        [1.0,           5.0,       7.0],    # Shop 1 plays Hold
        [5.0,           2.0,       4.0],    # Shop 1 plays Loyalty
    ])
    # Symmetric game: B = A^T
    B = A.T.copy()
    return Instance(
        payoff_A=A,
        payoff_B=B,
        row_labels=("Discount", "Hold", "Loyalty"),
        col_labels=("Discount", "Hold", "Loyalty"),
        player_names=("Shop 1", "Shop 2"),
        game_name="3x3 Coffee Shop Pricing (Circular Dominance with Loyalty)",
    )


# --- Display Helpers ---

def print_payoff_matrix(instance: Instance) -> None:
    """Print the bimatrix game in a readable format."""
    A = instance.payoff_A
    B = instance.payoff_B
    n_rows, n_cols = A.shape

    col_header = "".join(f"{instance.col_labels[j]:>18}" for j in range(n_cols))
    log.info(f"  {instance.player_names[1]:>18} {col_header}", tag="DATA")
    log.info(f"  {instance.player_names[0]}", tag="DATA")
    log.divider()

    for i in range(n_rows):
        cells = ""
        for j in range(n_cols):
            cells += f"  ({A[i,j]:5.1f}, {B[i,j]:5.1f}) "
        log.table_row(f"{instance.row_labels[i]:>12}  {cells}", tag="TABLE")


def print_equilibrium(eq: Equilibrium, instance: Instance, idx: int) -> None:
    """Print a single equilibrium in detail."""
    eq_type = "Pure" if eq.is_pure else "Mixed"
    log.info(f"Equilibrium #{idx + 1} ({eq_type} Strategy NE)", tag="RESULT")

    # Player 1 strategy
    parts_1 = []
    for k, lbl in enumerate(instance.row_labels):
        prob = eq.sigma_1[k]
        if prob > 1e-10:
            # Show as fraction if close to a nice fraction
            frac_str = _to_fraction_str(prob)
            parts_1.append(f"{lbl}: {frac_str}")
    log.metric(f"{instance.player_names[0]}:", "  ".join(parts_1), tag="RESULT", pad=12)

    # Player 2 strategy
    parts_2 = []
    for k, lbl in enumerate(instance.col_labels):
        prob = eq.sigma_2[k]
        if prob > 1e-10:
            frac_str = _to_fraction_str(prob)
            parts_2.append(f"{lbl}: {frac_str}")
    log.metric(f"{instance.player_names[1]}:", "  ".join(parts_2), tag="RESULT", pad=12)

    log.metric("Payoff:", f"{instance.player_names[0]}=${eq.payoff_1:.3f}k, "
               f"{instance.player_names[1]}=${eq.payoff_2:.3f}k", tag="RESULT", pad=12)
    log.metric("Support:", f"P1={eq.support_1}, P2={eq.support_2}", tag="DATA", pad=12)


def _to_fraction_str(value: float) -> str:
    """Convert a float to a nice fraction string if possible, else decimal."""
    from fractions import Fraction
    frac = Fraction(value).limit_denominator(100)
    if abs(float(frac) - value) < 1e-6:
        if frac.denominator == 1:
            return f"{frac.numerator}"
        return f"{frac.numerator}/{frac.denominator} ({value:.4f})"
    return f"{value:.4f}"


# --- Main ---

if __name__ == "__main__":
    # =====================================================================
    #  GAME 1: 2x2 Anti-coordination game
    # =====================================================================
    instance_2x2 = make_2x2_instance()
    sol_2x2 = solve(instance_2x2)

    log.header(f"GAME 1: {instance_2x2.game_name}")

    log.step("PAYOFF MATRICES (in $1000s/month)")
    log.info("Format: (Shop 1 payoff, Shop 2 payoff)", tag="DATA")
    log.blank()
    print_payoff_matrix(instance_2x2)
    log.blank()

    log.step("DOMINANT STRATEGY ANALYSIS")
    for player, dom in sol_2x2.dominant_strategies.items():
        if dom:
            log.info(f"{player} has a strictly dominant strategy: {dom}", tag="RESULT")
        else:
            log.info(f"{player} has no strictly dominant strategy", tag="DATA")
    log.blank()

    log.step("BEST RESPONSES")
    for player, br in sol_2x2.best_responses.items():
        for opp_strat, best in br.items():
            log.info(f"{player} best response to '{opp_strat}': {best}", tag="DATA")

    # Show the anti-coordination structure explicitly
    log.blank()
    log.info("Anti-coordination structure: each shop wants to do", tag="INTERPRET")
    log.info("the OPPOSITE of its competitor.", tag="INTERPRET")
    log.blank()

    log.step(f"NASH EQUILIBRIA ({sol_2x2.num_equilibria} found)")
    for idx, eq in enumerate(sol_2x2.equilibria):
        print_equilibrium(eq, instance_2x2, idx)
        log.blank()

    log.step("MINIMAX / SECURITY LEVELS")
    if sol_2x2.minimax_value_1 is not None:
        log.metric(f"{instance_2x2.player_names[0]} security level:",
                   f"${sol_2x2.minimax_value_1:.2f}k/month", tag="RESULT", pad=28)
        if sol_2x2.minimax_strategy_1 is not None:
            parts = [f"{instance_2x2.row_labels[k]}: {sol_2x2.minimax_strategy_1[k]:.4f}"
                     for k in range(len(instance_2x2.row_labels))
                     if sol_2x2.minimax_strategy_1[k] > 1e-10]
            log.metric("  Maximin strategy:", "  ".join(parts), tag="DATA", pad=28)

    if sol_2x2.minimax_value_2 is not None:
        log.metric(f"{instance_2x2.player_names[1]} security level:",
                   f"${sol_2x2.minimax_value_2:.2f}k/month", tag="RESULT", pad=28)
        if sol_2x2.minimax_strategy_2 is not None:
            parts = [f"{instance_2x2.col_labels[k]}: {sol_2x2.minimax_strategy_2[k]:.4f}"
                     for k in range(len(instance_2x2.col_labels))
                     if sol_2x2.minimax_strategy_2[k] > 1e-10]
            log.metric("  Maximin strategy:", "  ".join(parts), tag="DATA", pad=28)

    log.metric("Zero-sum game?", str(sol_2x2.is_zero_sum), tag="DATA", pad=28)
    log.blank()

    log.step("STRATEGIC INTERPRETATION")
    log.info("This is an Anti-coordination Game (Chicken / Hawk-Dove variant):", tag="INTERPRET")
    log.info("  - No player has a dominant strategy", tag="INTERPRET")
    log.info("  - Best response depends on what the competitor does:", tag="INTERPRET")
    log.info("    If competitor discounts -> hold prices (avoid price war)", tag="INTERPRET")
    log.info("    If competitor holds -> discount (capture market share)", tag="INTERPRET")
    log.info("  - Two pure NE where shops differentiate (one discounts, one holds)", tag="INTERPRET")
    log.info("  - One mixed NE where both randomize 50/50", tag="INTERPRET")
    log.info("  - The mixed NE payoff ($3.50k each) is worse than (Hold, Hold) = $4k", tag="INTERPRET")
    log.info("  - Coordination on who discounts is the key strategic challenge", tag="INTERPRET")
    log.blank()
    log.info("Business recommendations:", tag="RECOMMEND")
    log.info("  - Communicate or signal to avoid the destructive (Discount, Discount)", tag="RECOMMEND")
    log.info("  - If uncertain about competitor, the mixed strategy hedges risk", tag="RECOMMEND")
    log.info("  - Consider alternating promotions (repeated game cooperation)", tag="RECOMMEND")
    log.info("  - Adding a Loyalty option (Game 2) may provide a new dimension", tag="RECOMMEND")
    log.blank()

    log.step("VERIFICATION")
    for check_name, result in sol_2x2.constraint_check.items():
        if isinstance(result, bool):
            log.check(check_name, result, tag="VERIFY")
        else:
            log.check(check_name, result, tag="VERIFY")
    log.blank()

    log.metric("Algorithm:", sol_2x2.algorithm, tag="SOLVE", pad=12)
    log.metric("Time:", f"{sol_2x2.time_seconds:.6f}s", tag="TIMING", pad=12)
    log.divider(style="thick")

    # =====================================================================
    #  GAME 2: 3x3 with Loyalty Program (circular dominance)
    # =====================================================================
    instance_3x3 = make_3x3_instance()
    sol_3x3 = solve(instance_3x3)

    log.header(f"GAME 2: {instance_3x3.game_name}")

    log.step("PAYOFF MATRICES (in $1000s/month)")
    log.info("Format: (Shop 1 payoff, Shop 2 payoff)", tag="DATA")
    log.info("Symmetric game: B = A^T (both shops face identical incentives)", tag="DATA")
    log.blank()
    print_payoff_matrix(instance_3x3)
    log.blank()

    log.step("DOMINANT STRATEGY ANALYSIS")
    for player, dom in sol_3x3.dominant_strategies.items():
        if dom:
            log.info(f"{player} has a strictly dominant strategy: {dom}", tag="RESULT")
        else:
            log.info(f"{player} has no strictly dominant strategy", tag="DATA")
    log.blank()

    # Weak dominance analysis
    log.step("WEAK DOMINANCE CHECK")
    weak_dom_1 = _find_weakly_dominated(instance_3x3.payoff_A, instance_3x3.row_labels)
    weak_dom_2 = _find_weakly_dominated(instance_3x3.payoff_B.T, instance_3x3.col_labels)
    if weak_dom_1:
        for dominated, dominator in weak_dom_1:
            log.info(f"Shop 1: {dominator} weakly dominates {dominated}", tag="RESULT")
    else:
        log.info("Shop 1: no weakly dominated strategies", tag="DATA")
    if weak_dom_2:
        for dominated, dominator in weak_dom_2:
            log.info(f"Shop 2: {dominator} weakly dominates {dominated}", tag="RESULT")
    else:
        log.info("Shop 2: no weakly dominated strategies", tag="DATA")
    log.blank()

    log.step("BEST RESPONSES (showing circular structure)")
    for player, br in sol_3x3.best_responses.items():
        for opp_strat, best in br.items():
            log.info(f"{player} best response to '{opp_strat}': {best}", tag="DATA")
    log.blank()
    log.info("Circular pattern: Discount -> Loyalty -> Hold -> Discount", tag="INTERPRET")
    log.info("(Like Rock-Paper-Scissors: no pure-strategy NE can exist)", tag="INTERPRET")
    log.blank()

    log.step(f"NASH EQUILIBRIA ({sol_3x3.num_equilibria} found)")
    for idx, eq in enumerate(sol_3x3.equilibria):
        print_equilibrium(eq, instance_3x3, idx)
        log.blank()

    # Show hand-calculation for the mixed NE
    log.step("MIXED EQUILIBRIUM DERIVATION")
    log.info("For P1 to be indifferent, P2 plays (q1, q2, q3):", tag="MODEL")
    log.info("  E[Discount] = 3q1 + 6q2 + 2q3", tag="MODEL")
    log.info("  E[Hold]     = 1q1 + 5q2 + 7q3", tag="MODEL")
    log.info("  E[Loyalty]  = 5q1 + 2q2 + 4q3", tag="MODEL")
    log.info("Setting all equal, substituting q3 = 1 - q1 - q2:", tag="SOLVE")
    log.info("  E[D]=E[L]: -2q1 + 4q2 - 2q3 = 0 => 6q2 = 2 => q2 = 1/3", tag="SOLVE")
    log.info("  E[D]=E[H]: 2q1 + q2 - 5q3 = 0 => 7q1 + 6q2 = 5 => q1 = 3/7", tag="SOLVE")
    log.info("  q3 = 1 - 3/7 - 1/3 = 5/21", tag="SOLVE")
    log.info("  By symmetry (B = A^T), P1 uses the same mixing: p = q", tag="RESULT")
    log.info("  Expected payoff: 79/21 = 3.762k each", tag="RESULT")
    log.blank()

    log.step("MINIMAX / SECURITY LEVELS")
    if sol_3x3.minimax_value_1 is not None:
        log.metric(f"{instance_3x3.player_names[0]} security level:",
                   f"${sol_3x3.minimax_value_1:.3f}k/month", tag="RESULT", pad=28)
        if sol_3x3.minimax_strategy_1 is not None:
            parts = [f"{instance_3x3.row_labels[k]}: "
                     f"{_to_fraction_str(sol_3x3.minimax_strategy_1[k])}"
                     for k in range(len(instance_3x3.row_labels))
                     if sol_3x3.minimax_strategy_1[k] > 1e-10]
            log.metric("  Maximin strategy:", "  ".join(parts), tag="DATA", pad=28)

    if sol_3x3.minimax_value_2 is not None:
        log.metric(f"{instance_3x3.player_names[1]} security level:",
                   f"${sol_3x3.minimax_value_2:.3f}k/month", tag="RESULT", pad=28)
        if sol_3x3.minimax_strategy_2 is not None:
            parts = [f"{instance_3x3.col_labels[k]}: "
                     f"{_to_fraction_str(sol_3x3.minimax_strategy_2[k])}"
                     for k in range(len(instance_3x3.col_labels))
                     if sol_3x3.minimax_strategy_2[k] > 1e-10]
            log.metric("  Maximin strategy:", "  ".join(parts), tag="DATA", pad=28)

    log.metric("Zero-sum game?", str(sol_3x3.is_zero_sum), tag="DATA", pad=28)
    log.blank()

    # Pareto efficiency analysis
    log.step("PARETO EFFICIENCY ANALYSIS")
    A3 = instance_3x3.payoff_A
    B3 = instance_3x3.payoff_B
    outcomes: list[tuple[int, int, float, float]] = []
    for i in range(A3.shape[0]):
        for j in range(A3.shape[1]):
            outcomes.append((i, j, float(A3[i, j]), float(B3[i, j])))

    pareto_optimal: list[tuple[int, int, float, float]] = []
    for o in outcomes:
        dominated = False
        for p in outcomes:
            if (p[2] >= o[2] and p[3] >= o[3]) and (p[2] > o[2] or p[3] > o[3]):
                dominated = True
                break
        if not dominated:
            pareto_optimal.append(o)

    log.info("Pareto-optimal outcomes:", tag="RESULT")
    for i, j, pa, pb in pareto_optimal:
        log.info(f"  ({instance_3x3.row_labels[i]}, {instance_3x3.col_labels[j]}): "
                 f"${pa:.1f}k, ${pb:.1f}k", tag="RESULT")
    log.blank()

    # Check if NE payoffs are Pareto-dominated
    for idx, eq in enumerate(sol_3x3.equilibria):
        ep1, ep2 = eq.payoff_1, eq.payoff_2
        dominated_by_any = any(pa >= ep1 + 1e-6 and pb >= ep2 + 1e-6
                               for _, _, pa, pb in outcomes)
        log.info(f"NE #{idx + 1} (expected ${ep1:.3f}k, ${ep2:.3f}k) "
                 f"Pareto-dominated? {dominated_by_any}", tag="CHECK")
    log.blank()

    log.step("STRATEGIC INTERPRETATION")
    log.info("Adding a Loyalty Program creates circular dominance:", tag="INTERPRET")
    log.info("  - Discount beats Hold (steal price-sensitive customers)", tag="INTERPRET")
    log.info("  - Hold beats Loyalty (save costs vs expensive program)", tag="INTERPRET")
    log.info("  - Loyalty beats Discount (retain loyal regulars)", tag="INTERPRET")
    log.info("  - No pure-strategy NE exists -- every pure strategy is exploitable", tag="INTERPRET")
    log.info("  - The unique mixed NE requires randomizing over all three strategies", tag="INTERPRET")
    log.info("  - Expected NE payoff (~$3.76k) is lower than (Hold,Hold)=$5k", tag="INTERPRET")
    log.info("    or (Loyalty,Loyalty)=$4k -- the 'fog of war' costs both shops", tag="INTERPRET")
    log.blank()
    log.info("Business recommendations:", tag="RECOMMEND")
    log.info("  - In a one-shot game, play the mixed strategy to be unpredictable", tag="RECOMMEND")
    log.info("  - In a repeated setting, coordinate on (Hold, Hold) for $5k each", tag="RECOMMEND")
    log.info("  - (Loyalty, Loyalty) at $4k is a reasonable compromise if trust is limited", tag="RECOMMEND")
    log.info("  - Avoid being predictable -- a pattern-recognizing competitor will exploit it", tag="RECOMMEND")
    log.info("  - Contrast with Game 1: the 3-strategy game has no differentiation equilibrium", tag="RECOMMEND")
    log.blank()

    log.step("VERIFICATION")
    for check_name, result in sol_3x3.constraint_check.items():
        if isinstance(result, bool):
            log.check(check_name, result, tag="VERIFY")
        else:
            log.check(check_name, result, tag="VERIFY")
    log.blank()

    log.metric("Algorithm:", sol_3x3.algorithm, tag="SOLVE", pad=12)
    log.metric("Time:", f"{sol_3x3.time_seconds:.6f}s", tag="TIMING", pad=12)
    log.divider(style="thick")

    # --- Save JSON ---
    def eq_to_dict(eq: Equilibrium) -> dict:
        return {
            "sigma_1": eq.sigma_1.tolist(),
            "sigma_2": eq.sigma_2.tolist(),
            "payoff_1": eq.payoff_1,
            "payoff_2": eq.payoff_2,
            "is_pure": eq.is_pure,
            "support_1": eq.support_1,
            "support_2": eq.support_2,
        }

    output = {
        "game_1_2x2": {
            "name": instance_2x2.game_name,
            "payoff_A": instance_2x2.payoff_A.tolist(),
            "payoff_B": instance_2x2.payoff_B.tolist(),
            "row_labels": list(instance_2x2.row_labels),
            "col_labels": list(instance_2x2.col_labels),
            "equilibria": [eq_to_dict(eq) for eq in sol_2x2.equilibria],
            "num_equilibria": sol_2x2.num_equilibria,
            "dominant_strategies": sol_2x2.dominant_strategies,
            "is_zero_sum": sol_2x2.is_zero_sum,
            "minimax_value_1": sol_2x2.minimax_value_1,
            "minimax_value_2": sol_2x2.minimax_value_2,
            "verification": {k: v for k, v in sol_2x2.constraint_check.items()
                             if not isinstance(v, np.ndarray)},
            "algorithm": sol_2x2.algorithm,
            "time_seconds": sol_2x2.time_seconds,
        },
        "game_2_3x3": {
            "name": instance_3x3.game_name,
            "payoff_A": instance_3x3.payoff_A.tolist(),
            "payoff_B": instance_3x3.payoff_B.tolist(),
            "row_labels": list(instance_3x3.row_labels),
            "col_labels": list(instance_3x3.col_labels),
            "equilibria": [eq_to_dict(eq) for eq in sol_3x3.equilibria],
            "num_equilibria": sol_3x3.num_equilibria,
            "dominant_strategies": sol_3x3.dominant_strategies,
            "is_zero_sum": sol_3x3.is_zero_sum,
            "minimax_value_1": sol_3x3.minimax_value_1,
            "minimax_value_2": sol_3x3.minimax_value_2,
            "verification": {k: v for k, v in sol_3x3.constraint_check.items()
                             if not isinstance(v, np.ndarray)},
            "algorithm": sol_3x3.algorithm,
            "time_seconds": sol_3x3.time_seconds,
        },
    }
    output_path = Path(__file__).parent / "solution.json"
    with open(str(output_path), "w") as f:
        json.dump(output, f, indent=2, default=str)
    log.success(f"Solution data saved to: {output_path.name}", tag="SAVE")
