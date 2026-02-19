#!/usr/bin/env python3
"""A/B Test visualizations.

Generates two charts:
  1. Conversion rate comparison (bar chart with CI error bars + significance)
  2. Power curve (sample size vs. power for the observed effect)

Reads solution data from solution.json (output of ab_solver.py).
"""
from __future__ import annotations

import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats


def load_solution(path: str = "solution.json") -> dict:
    """Load solution data."""
    with open(path) as f:
        return json.load(f)


def plot_conversion_comparison(sol: dict, filename: str = "conversion_comparison.png") -> None:
    """Bar chart comparing conversion rates with confidence intervals."""
    inst = sol["instance"]
    freq = sol["frequentist"]
    bayes = sol["bayesian"]

    rate_a = inst["conv_a"] / inst["n_a"]
    rate_b = inst["conv_b"] / inst["n_b"]

    # Wilson CIs for individual proportions
    from statsmodels.stats.proportion import proportion_confint
    ci_a = proportion_confint(inst["conv_a"], inst["n_a"], alpha=inst["alpha"], method="wilson")
    ci_b = proportion_confint(inst["conv_b"], inst["n_b"], alpha=inst["alpha"], method="wilson")

    fig, ax = plt.subplots(figsize=(8, 5))

    groups = ["Control (A)", "Treatment (B)"]
    rates = [rate_a * 100, rate_b * 100]
    errors = [
        [(rate_a - ci_a[0]) * 100, (rate_b - ci_b[0]) * 100],
        [(ci_a[1] - rate_a) * 100, (ci_b[1] - rate_b) * 100],
    ]
    colors = ["#90caf9", "#1976d2"]

    bars = ax.bar(groups, rates, yerr=errors, capsize=10, color=colors,
                  edgecolor="white", linewidth=1.5, width=0.5,
                  error_kw={"linewidth": 2, "capthick": 1.5})

    # Annotate rates
    for bar, rate, n, conv in zip(bars, rates, [inst["n_a"], inst["n_b"]],
                                   [inst["conv_a"], inst["conv_b"]]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                "{:.2f}%\n({:,}/{:,})".format(rate, conv, n),
                ha="center", fontsize=10, fontweight="bold")

    # Significance bracket
    max_y = max(rates) + max(errors[1]) + 1.5
    p_val = freq["p_value"]
    if p_val < 0.001:
        sig_text = "p < 0.001 ***"
    elif p_val < 0.01:
        sig_text = "p = {:.4f} **".format(p_val)
    elif p_val < 0.05:
        sig_text = "p = {:.4f} *".format(p_val)
    else:
        sig_text = "p = {:.3f} (ns)".format(p_val)

    ax.annotate("", xy=(0, max_y), xytext=(1, max_y),
                arrowprops=dict(arrowstyle="-", color="black", lw=1.5))
    ax.text(0.5, max_y + 0.15, sig_text, ha="center", fontsize=10)

    # Bayesian annotation
    prob_text = "P(B > A) = {:.1%}".format(bayes["prob_b_better"])
    ax.text(0.98, 0.05, prob_text, transform=ax.transAxes, ha="right",
            fontsize=9, style="italic", color="#555555",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.5))

    ax.set_ylabel("Conversion Rate (%)", fontsize=11)
    ax.set_title("A/B Test: Conversion Rate Comparison", fontsize=14, fontweight="bold")
    ax.set_ylim(0, max_y + 1.0)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: "{:.1f}%".format(x)))

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    print("Saved: {}".format(filename))


def plot_power_curve(sol: dict, filename: str = "power_curve.png") -> None:
    """Power curve: sample size vs. statistical power for the observed effect."""
    inst = sol["instance"]
    power_data = sol.get("sensitivity", {}).get("power_curve", {})

    if not power_data:
        print("No power curve data available. Skipping.")
        return

    rate_a = inst["conv_a"] / inst["n_a"]
    rate_b = inst["conv_b"] / inst["n_b"]
    effect_h = 2 * (np.arcsin(np.sqrt(rate_b)) - np.arcsin(np.sqrt(rate_a)))

    ns = sorted(int(k) for k in power_data.keys())
    powers = [power_data[str(n)] for n in ns]

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(ns, powers, "o-", color="#1976d2", linewidth=2.5, markersize=8,
            markerfacecolor="white", markeredgewidth=2)

    # 80% power line
    ax.axhline(y=0.8, color="#d32f2f", linestyle="--", linewidth=1.5, alpha=0.7)
    ax.text(ns[-1] * 0.98, 0.82, "80% power target", ha="right", fontsize=9,
            color="#d32f2f", style="italic")

    # Mark current sample size
    current_n = inst["n_a"]
    current_power = sol["power"]["observed"]
    ax.plot(current_n, current_power, "D", color="#d32f2f", markersize=12, zorder=5)
    ax.annotate("Current\nn={:,}\npower={:.0%}".format(current_n, current_power),
                xy=(current_n, current_power),
                xytext=(current_n + ns[-1] * 0.08, current_power - 0.12),
                fontsize=9, ha="left",
                arrowprops=dict(arrowstyle="->", color="#d32f2f"),
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))

    # Mark n needed for 80% power
    n_80 = sol["power"]["n_for_80pct"]
    if 0 < n_80 <= ns[-1] * 1.5:
        ax.axvline(x=n_80, color="#4caf50", linestyle=":", linewidth=1.5, alpha=0.7)
        ax.text(n_80, 0.05, "n={:,}\nfor 80%".format(n_80), ha="center", fontsize=8,
                color="#4caf50", fontweight="bold")

    ax.set_xlabel("Sample Size per Group", fontsize=11)
    ax.set_ylabel("Statistical Power", fontsize=11)
    ax.set_title("Power Curve (Cohen's h = {:.3f})".format(abs(effect_h)),
                 fontsize=14, fontweight="bold")
    ax.set_ylim(0, 1.05)
    ax.set_xlim(0, ns[-1] * 1.1)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: "{:.0%}".format(x)))
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: "{:,.0f}".format(x)))

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    print("Saved: {}".format(filename))


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "solution.json"
    sol = load_solution(path)
    plot_conversion_comparison(sol)
    plot_power_curve(sol)
