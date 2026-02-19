#!/usr/bin/env python3
"""Visualizations for portfolio optimization solution.

Generates:
1. Efficient frontier (risk-return trade-off curve)
2. Portfolio allocation stacked area chart across the frontier
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger

log = PolyaLogger()


def ensure_installed(package: str) -> None:
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])


ensure_installed("matplotlib")
ensure_installed("numpy")
ensure_installed("cvxpy")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import cvxpy as cp


def compute_frontier_with_weights():
    """Recompute frontier with full weight data for visualization."""
    asset_names = ["Tech", "Healthcare", "Energy", "Bonds", "Real Estate"]
    mu = np.array([0.12, 0.09, 0.08, 0.05, 0.07])
    Sigma = np.array([
        [0.0400, 0.0120, 0.0100, 0.0005, 0.0080],
        [0.0120, 0.0225, 0.0090, 0.0010, 0.0060],
        [0.0100, 0.0090, 0.0289, 0.0008, 0.0070],
        [0.0005, 0.0010, 0.0008, 0.0036, 0.0015],
        [0.0080, 0.0060, 0.0070, 0.0015, 0.0196],
    ])

    n = len(asset_names)
    risks, returns, weights_list = [], [], []

    for gamma in np.logspace(-2, 2, 50):
        x = cp.Variable(n)
        prob = cp.Problem(
            cp.Maximize(mu @ x - gamma * cp.quad_form(x, Sigma)),
            [cp.sum(x) == 1, x >= 0],
        )
        prob.solve()
        if prob.status == "optimal":
            w = x.value
            risks.append(float(np.sqrt(w @ Sigma @ w)) * 100)
            returns.append(float(mu @ w) * 100)
            weights_list.append(w * 100)

    return risks, returns, weights_list, asset_names


def plot_efficient_frontier(risks, returns, asset_names):
    """Chart 1: Efficient frontier curve with key portfolios annotated."""
    colors = {
        "primary": "#1976d2",
        "danger": "#d32f2f",
        "success": "#4caf50",
        "warning": "#ff9800",
    }

    fig, ax = plt.subplots(figsize=(10, 7))

    # Plot frontier
    ax.plot(risks, returns, "-", color=colors["primary"], linewidth=2.5, label="Efficient Frontier")
    ax.scatter(risks, returns, c=colors["primary"], s=20, zorder=3)

    # Annotate key points
    min_risk_idx = np.argmin(risks)
    max_ret_idx = np.argmax(returns)

    ax.scatter(risks[min_risk_idx], returns[min_risk_idx],
               c=colors["success"], s=150, zorder=5, edgecolors="black", linewidth=1.5)
    ax.annotate("Min Variance\n{:.1f}% risk, {:.1f}% return".format(
        risks[min_risk_idx], returns[min_risk_idx]),
        xy=(risks[min_risk_idx], returns[min_risk_idx]),
        xytext=(risks[min_risk_idx] + 1.5, returns[min_risk_idx] - 0.5),
        arrowprops=dict(arrowstyle="->", color="gray"), fontsize=9)

    ax.scatter(risks[max_ret_idx], returns[max_ret_idx],
               c=colors["danger"], s=150, zorder=5, edgecolors="black", linewidth=1.5)
    ax.annotate("Max Return\n{:.1f}% risk, {:.1f}% return".format(
        risks[max_ret_idx], returns[max_ret_idx]),
        xy=(risks[max_ret_idx], returns[max_ret_idx]),
        xytext=(risks[max_ret_idx] - 5, returns[max_ret_idx] + 0.3),
        arrowprops=dict(arrowstyle="->", color="gray"), fontsize=9)

    # Balanced portfolio (near middle)
    mid_idx = len(risks) // 2
    ax.scatter(risks[mid_idx], returns[mid_idx],
               c=colors["warning"], s=150, zorder=5, edgecolors="black", linewidth=1.5)
    ax.annotate("Balanced\n{:.1f}% risk, {:.1f}% return".format(
        risks[mid_idx], returns[mid_idx]),
        xy=(risks[mid_idx], returns[mid_idx]),
        xytext=(risks[mid_idx] + 1.5, returns[mid_idx] + 0.3),
        arrowprops=dict(arrowstyle="->", color="gray"), fontsize=9)

    ax.set_xlabel("Risk (Annual Std Dev %)", fontsize=11)
    ax.set_ylabel("Expected Return (%)", fontsize=11)
    ax.set_title("Efficient Frontier: Risk-Return Trade-off", fontsize=14, fontweight="bold")
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("viz_efficient_frontier.png", dpi=150, bbox_inches="tight")
    log.success("viz_efficient_frontier.png", tag="SAVE")
    plt.close()


def plot_allocation_area(risks, weights_list, asset_names):
    """Chart 2: Stacked area chart showing allocation shift across the frontier."""
    categorical = ["#1976d2", "#d32f2f", "#4caf50", "#ff9800", "#9c27b0"]

    weights_array = np.array(weights_list)  # (n_points, n_assets)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.stackplot(
        risks, weights_array.T,
        labels=asset_names, colors=categorical, alpha=0.85,
    )
    ax.set_xlabel("Risk (Annual Std Dev %)", fontsize=11)
    ax.set_ylabel("Allocation (%)", fontsize=11)
    ax.set_title("Portfolio Allocation Across the Efficient Frontier",
                 fontsize=14, fontweight="bold")
    ax.legend(loc="upper left", fontsize=9)
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig("viz_allocation_area.png", dpi=150, bbox_inches="tight")
    log.success("viz_allocation_area.png", tag="SAVE")
    plt.close()


if __name__ == "__main__":
    risks, returns, weights_list, asset_names = compute_frontier_with_weights()
    plot_efficient_frontier(risks, returns, asset_names)
    plot_allocation_area(risks, weights_list, asset_names)
