#!/usr/bin/env python3
"""Portfolio optimization solver using Markowitz mean-variance model.

Solves the convex quadratic program:
    maximize    mu^T x - gamma * x^T Sigma x
    subject to  sum(x) = 1, x >= 0

Complexity: Polynomial (interior point for convex QP).
Correctness: Guaranteed global optimum (convex problem).
"""
from __future__ import annotations

import subprocess
import sys
import time
from dataclasses import dataclass

import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger
log = PolyaLogger()


def ensure_installed(package: str, import_name: str | None = None) -> None:
    """Install package if not available."""
    try:
        __import__(import_name or package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])


ensure_installed("cvxpy")
import cvxpy as cp  # noqa: E402


# --- Data Model ---

@dataclass(frozen=True)
class Instance:
    """Portfolio optimization instance."""
    asset_names: list[str]
    expected_returns: np.ndarray  # mu: (n,) vector of expected annual returns
    covariance: np.ndarray        # Sigma: (n, n) covariance matrix
    risk_aversion: float          # gamma: risk aversion parameter

    @property
    def n(self) -> int:
        return len(self.asset_names)


@dataclass
class Solution:
    """Verified portfolio solution with metadata."""
    weights: np.ndarray           # optimal allocation (sums to 1)
    expected_return: float        # mu^T x
    risk: float                   # sqrt(x^T Sigma x) -- portfolio std dev
    objective: float              # mu^T x - gamma * x^T Sigma x
    is_optimal: bool
    is_feasible: bool
    algorithm: str
    time_seconds: float
    certificate: str | None
    solver_status: str


@dataclass
class EfficientFrontier:
    """Collection of Pareto-optimal portfolios."""
    risks: list[float]
    returns: list[float]
    weights: list[np.ndarray]
    gammas: list[float]


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Solve the Markowitz portfolio optimization."""
    t0 = time.perf_counter()

    n = instance.n
    mu = instance.expected_returns
    Sigma = instance.covariance
    gamma = instance.risk_aversion

    # Decision variable: portfolio weights
    x = cp.Variable(n)

    # Objective: maximize return - gamma * risk
    # Equivalent to: minimize gamma * x^T Sigma x - mu^T x
    portfolio_return = mu @ x
    portfolio_risk = cp.quad_form(x, Sigma)
    objective = cp.Maximize(portfolio_return - gamma * portfolio_risk)

    # Constraints
    constraints = [
        cp.sum(x) == 1,  # fully invested
        x >= 0,          # no short selling
    ]

    prob = cp.Problem(objective, constraints)
    prob.solve()

    elapsed = time.perf_counter() - t0

    weights = x.value
    exp_ret = float(mu @ weights)
    risk_val = float(np.sqrt(weights @ Sigma @ weights))

    feasible = verify(instance, weights)

    return Solution(
        weights=weights,
        expected_return=exp_ret,
        risk=risk_val,
        objective=float(prob.value),
        is_optimal=(prob.status == "optimal"),
        is_feasible=feasible,
        algorithm="Markowitz QP via cvxpy (interior point)",
        time_seconds=elapsed,
        certificate="Convex QP -- global optimum guaranteed by strong duality",
        solver_status=prob.status,
    )


def solve_efficient_frontier(instance: Instance, n_points: int = 50) -> EfficientFrontier:
    """Sweep risk aversion to trace the efficient frontier."""
    risks, returns, all_weights, gammas = [], [], [], []

    for gamma in np.logspace(-2, 2, n_points):
        inst = Instance(
            asset_names=instance.asset_names,
            expected_returns=instance.expected_returns,
            covariance=instance.covariance,
            risk_aversion=gamma,
        )
        sol = solve(inst)
        if sol.is_optimal and sol.is_feasible:
            risks.append(sol.risk)
            returns.append(sol.expected_return)
            all_weights.append(sol.weights.copy())
            gammas.append(gamma)

    return EfficientFrontier(
        risks=risks, returns=returns, weights=all_weights, gammas=gammas
    )


# --- Verification ---

def verify(instance: Instance, weights: np.ndarray) -> bool:
    """Independently verify solution feasibility."""
    tol = 1e-6

    # Check weights sum to 1
    if abs(np.sum(weights) - 1.0) > tol:
        log.error(f"weights sum to {np.sum(weights):.6f}, expected 1.0", tag="VERIFY")
        return False

    # Check no short selling
    if np.any(weights < -tol):
        log.error(f"negative weight found: min = {np.min(weights):.6f}", tag="VERIFY")
        return False

    # Check covariance matrix is positive semidefinite
    eigenvalues = np.linalg.eigvalsh(instance.covariance)
    if np.any(eigenvalues < -tol):
        log.error(f"covariance matrix not PSD: min eigenvalue = {np.min(eigenvalues):.6f}", tag="VERIFY")
        return False

    return True


# --- Main ---

if __name__ == "__main__":
    # Problem data: 5 assets with realistic parameters
    asset_names = ["Tech", "Healthcare", "Energy", "Bonds", "Real Estate"]

    # Expected annual returns (%)
    mu = np.array([0.12, 0.09, 0.08, 0.05, 0.07])

    # Covariance matrix (annualized)
    # Constructed to be realistic: higher correlation within equities, low with bonds
    Sigma = np.array([
        [0.0400, 0.0120, 0.0100, 0.0005, 0.0080],  # Tech
        [0.0120, 0.0225, 0.0090, 0.0010, 0.0060],  # Healthcare
        [0.0100, 0.0090, 0.0289, 0.0008, 0.0070],  # Energy
        [0.0005, 0.0010, 0.0008, 0.0036, 0.0015],  # Bonds
        [0.0080, 0.0060, 0.0070, 0.0015, 0.0196],  # Real Estate
    ])

    log.header("Portfolio Optimization")
    log.info(f"Assets: {', '.join(asset_names)}", tag="DATA")

    # Solve for different risk aversion levels
    for gamma, label in [(10.0, "Conservative (gamma=10)"),
                          (1.0, "Balanced (gamma=1)"),
                          (0.1, "Aggressive (gamma=0.1)")]:
        instance = Instance(
            asset_names=asset_names,
            expected_returns=mu,
            covariance=Sigma,
            risk_aversion=gamma,
        )
        sol = solve(instance)

        log.step(label)
        for name, w in zip(asset_names, sol.weights):
            log.table_row(f"{name:15s} {w * 100:6.1f}%", tag="TABLE")
        log.metric("Expected return", f"{sol.expected_return * 100:.2f}%", tag="RESULT")
        log.metric("Risk (std dev)", f"{sol.risk * 100:.2f}%", tag="RESULT")
        log.metric("Optimal", str(sol.is_optimal), tag="VERIFY")
        log.metric("Feasible", str(sol.is_feasible), tag="VERIFY")
        log.metric("Time", f"{sol.time_seconds:.4f}s", tag="TIMING")

    # Compute efficient frontier
    log.info("Computing efficient frontier (50 points)...", tag="FRONTIER")
    instance = Instance(
        asset_names=asset_names,
        expected_returns=mu,
        covariance=Sigma,
        risk_aversion=1.0,  # placeholder, overridden in sweep
    )
    ef = solve_efficient_frontier(instance)
    log.info(f"{len(ef.risks)} Pareto-optimal portfolios computed", tag="FRONTIER")
    log.info(f"Risk range: {min(ef.risks) * 100:.2f}% -- {max(ef.risks) * 100:.2f}%", tag="FRONTIER")
    log.info(f"Return range: {min(ef.returns) * 100:.2f}% -- {max(ef.returns) * 100:.2f}%", tag="FRONTIER")

    # Save frontier data for visualization
    import json
    frontier_data = {
        "risks": [float(r) for r in ef.risks],
        "returns": [float(r) for r in ef.returns],
        "asset_names": asset_names,
    }
    with open("efficient_frontier.json", "w") as f:
        json.dump(frontier_data, f, indent=2)
    log.success("efficient_frontier.json", tag="SAVE")
