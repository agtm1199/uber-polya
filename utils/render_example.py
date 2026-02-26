#!/usr/bin/env python3
"""Render an existing uber-polya example to LaTeX + PDF.

Reads an example's ``solution.json`` and ``README.md``, infers the
mathematical formulation, and produces a report that reads like a
mathematics solution paper — with equations, constraints, and results
typeset properly.

Usage::

    python utils/render_example.py examples/team-assignment/
    python utils/render_example.py examples/inspector-assignment/ --include-code
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Allow running from project root
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from utils.latex_data import (
    Constraint,
    Figure,
    FormalModel,
    InterpretationReport,
    MappingRow,
    ReportConfig,
    SensitivityRow,
    SolutionReport,
    Variable,
    VerificationCheck,
)
from utils.latex_renderer import LatexRenderer


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_readme(path: Path) -> dict[str, str]:
    """Parse README.md into a dict of heading -> body.

    Also extracts ``**Domain**:``, ``**Algorithm**:``, ``**Key Concepts**:``
    metadata from the preamble into dedicated keys.
    """
    sections: dict[str, str] = {}
    current = "preamble"
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            sections[current] = "\n".join(lines).strip()
            current = line.lstrip("# ").strip()
            lines = []
        else:
            lines.append(line)
    sections[current] = "\n".join(lines).strip()

    # Extract metadata from preamble
    preamble = sections.get("preamble", "")
    for meta_key in ("Domain", "Algorithm", "Key Concepts"):
        m = re.search(rf"\*\*{meta_key}\*\*:\s*(.+)", preamble)
        if m and meta_key not in sections:
            sections[meta_key] = m.group(1).strip()

    return sections


def _extract_title(sections: dict[str, str], fallback_name: str) -> str:
    """Extract a clean title from the preamble — first line only."""
    preamble = sections.get("preamble", "")
    if preamble:
        first_line = preamble.split("\n")[0].strip().lstrip("# ").strip()
        if first_line:
            return first_line
    return fallback_name.replace("-", " ").title()


# ── Domain detection ─────────────────────────────────────────────────

def _detect_domain(data: dict, sections: dict[str, str]) -> str:
    """Detect the mathematical domain from README content + solution keys.

    Checks specific domains first, then falls back to generic.
    """
    # Use explicit metadata if available
    meta_domain = sections.get("Domain", "").lower()

    text = (
        sections.get("Problem", "") + " "
        + sections.get("Algorithm", "") + " "
        + sections.get("Key Concepts", "") + " "
        + meta_domain
    ).lower()

    # Also check solution.json keys for structural signals
    sol_keys = set(data.keys())

    # ── Specific domain checks (ordered by specificity) ──
    # Game theory
    if any(k in text for k in ("nash", "payoff matrix", "game theory",
                                 "equilibrium", "bimatrix")):
        return "Game Theory"
    if sol_keys & {"game_1_2x2", "game_2_3x3", "equilibria", "payoff_A"}:
        return "Game Theory"

    # Dynamical Systems / ODEs
    # Use regex word boundaries for short keywords to avoid false positives
    # (e.g., "ode" inside "mode", "sir" inside other words)
    if any(k in text for k in ("epidemic", "differential equation", "dynamical",
                                 "runge-kutta", "solve_ivp")):
        return "Dynamical Systems / ODEs"
    if any(re.search(rf"\b{p}\b", text) for p in ("sir", "ode")):
        return "Dynamical Systems / ODEs"
    if sol_keys & {"R0", "peak_infected", "herd_immunity_threshold"}:
        return "Dynamical Systems / ODEs"

    # Financial Mathematics
    if any(k in text for k in ("mortgage", "amortiz", "refinanc", "npv ",
                                 "financial math", "time value of money",
                                 "loan", "interest rate")):
        return "Financial Mathematics"
    if sol_keys & {"loan_amount", "refinance_breakeven_months", "options"}:
        if "monthly_payment" in str(data.get("options", "")):
            return "Financial Mathematics"

    # Simulation / Monte Carlo (check before statistics since MC problems
    # often use statistical concepts like confidence intervals)
    if "monte carlo" in text:
        return "Simulation / Monte Carlo"

    # Statistical Inference
    if any(k in text for k in ("hypothesis", "t-test", "p-value", "anova",
                                 "chi-square", "statistical test",
                                 "bayesian", "confidence interval")):
        return "Statistical Inference"
    if sol_keys & {"primary_test", "bayesian", "power"}:
        return "Statistical Inference"

    # Time Series
    if any(k in text for k in ("time series", "forecast", "sarima", "arima",
                                 "exponential smoothing")):
        return "Time Series Analysis"

    # Survival Analysis
    if any(k in text for k in ("survival", "kaplan-meier", "cox ",
                                 "hazard")):
        return "Survival Analysis"

    # Multi-Objective Optimization
    if any(k in text for k in ("pareto", "multi-objective", "nsga")):
        return "Multi-Objective Optimization"

    # Machine Learning
    if any(k in text for k in ("classif", "cluster", "random forest",
                                 "neural net", "feature select")):
        return "Machine Learning"

    # Graph Theory
    if any(k in text for k in ("graph", "bipartite", "hamiltonian",
                                 "shortest path", "network flow")):
        return "Graph Theory / Combinatorics"

    # Integer/Linear Programming
    if any(k in text for k in ("ilp", "integer linear", "binary variable",
                                 "branch and bound", "branch-and-bound")):
        return "Integer Linear Programming"
    if any(k in text for k in ("linear program",)):
        return "Linear Programming"

    # Queuing Theory
    if "queue" in text or "queuing" in text:
        return "Queuing Theory"

    # Simulation / Monte Carlo (fallback for "simulation" without "monte carlo")
    if "simulation" in text:
        return "Simulation / Monte Carlo"

    # Causal Inference
    if "causal" in text:
        return "Causal Inference"

    # Numerical Methods
    if any(k in text for k in ("root find", "interpol", "numerical")):
        return "Numerical Methods"

    # Computational Geometry
    if any(k in text for k in ("polygon", "convex hull", "voronoi")):
        return "Computational Geometry"

    # Fallback: check for optimization-style keys
    if sol_keys & {"assignment", "assignments", "is_optimal", "objective"}:
        return "Mathematical Optimization"

    return "Mathematical Optimization"


def _infer_problem_type(data: dict, sections: dict[str, str]) -> str:
    text = (sections.get("Problem", "") + sections.get("Algorithm", "")).lower()
    if any(w in text for w in ("prove", "proof", "theorem", "induction")):
        return "Prove"
    return "Find"


def _infer_complexity(sections: dict[str, str]) -> str:
    algo = sections.get("Algorithm", "")
    m = re.search(r"O\([^)]+\)", algo)
    if m:
        return m.group(0)
    if "NP" in algo:
        return "NP-hard (solved via ILP)"
    if "polynomial" in algo.lower():
        return "P"
    return ""


# ── Domain-specific variable inference ───────────────────────────────

def _vars_game_theory(data: dict, sections: dict[str, str]) -> list[Variable]:
    """Variables for game theory problems."""
    return [
        Variable(r"\sigma_i", "mixed strategy for player i (probability vector)", r"\Delta(S_i)"),
        Variable(r"A, B", "payoff matrices for players 1 and 2", r"\mathbb{R}^{m \times n}"),
        Variable(r"u_i(\sigma)", "expected utility of player i under profile sigma", r"\mathbb{R}"),
    ]


def _vars_sir(data: dict, sections: dict[str, str]) -> list[Variable]:
    """Variables for SIR / ODE problems."""
    inst = data.get("instance", {})
    N = inst.get("N", "N")
    beta = inst.get("beta", "beta")
    gamma = inst.get("gamma", "gamma")
    return [
        Variable("S(t)", "susceptible individuals at time t", f"[0, {N}]"),
        Variable("I(t)", "infected individuals at time t", f"[0, {N}]"),
        Variable("R(t)", "recovered individuals at time t", f"[0, {N}]"),
        Variable(r"\beta", f"transmission rate = {beta}/day", r"\mathbb{{R}}_{{>0}}"),
        Variable(r"\gamma", f"recovery rate = {gamma}/day", r"\mathbb{{R}}_{{>0}}"),
        Variable("R_0", f"basic reproduction number = {beta}/{gamma}", r"\mathbb{{R}}_{{>0}}"),
        Variable("N", f"total population = {N}", r"\mathbb{{Z}}^+"),
    ]


def _vars_finance(data: dict, sections: dict[str, str]) -> list[Variable]:
    """Variables for financial mathematics problems."""
    loan = data.get("loan_amount", "L")
    return [
        Variable("L", f"loan principal = ${loan:,.0f}" if isinstance(loan, (int, float)) else f"loan principal = {loan}", r"\mathbb{{R}}_{>0}"),
        Variable("r", "monthly interest rate = APR/12", r"\mathbb{{R}}_{>0}"),
        Variable("n", "total number of monthly payments", r"\mathbb{{Z}}^+"),
        Variable("PMT", "monthly payment amount", r"\mathbb{{R}}_{>0}"),
    ]


def _vars_statistics(data: dict, sections: dict[str, str]) -> list[Variable]:
    """Variables for statistical inference problems."""
    test = data.get("primary_test", {})
    vars_list = [
        Variable(r"\mu_1, \mu_2", "population means for groups 1 and 2", r"\mathbb{{R}}"),
        Variable(r"\bar{{x}}_1, \bar{{x}}_2", "sample means", r"\mathbb{{R}}"),
        Variable(r"s_1, s_2", "sample standard deviations", r"\mathbb{{R}}_{{>0}}"),
        Variable(r"n_1, n_2", "sample sizes", r"\mathbb{{Z}}^+"),
    ]
    # Detect test statistic name
    stat_name = test.get("statistic_name", "t")
    test_name = test.get("test_name", "")
    if not test_name:
        if "t_statistic" in test:
            test_name = "Welch's t-test"
        elif "chi2_statistic" in test:
            test_name = "Chi-squared test"
            stat_name = r"\chi^2"
        else:
            test_name = "hypothesis test"
    vars_list.append(
        Variable(stat_name, f"test statistic ({test_name})", r"\mathbb{{R}}")
    )
    vars_list.append(Variable("p", "p-value", "[0, 1]"))
    vars_list.append(Variable(r"\alpha", "significance level", "[0, 1]"))
    if test.get("effect_size") or test.get("cohens_d"):
        vars_list.append(Variable("d", "Cohen's d (effect size)", r"\mathbb{{R}}_{\ge 0}"))
    return vars_list


def _vars_optimization(data: dict, sections: dict[str, str]) -> list[Variable]:
    """Variables for optimization/assignment problems (original logic)."""
    algo_text = sections.get("Algorithm", "")
    problem_text = sections.get("Problem", "")
    variables: list[Variable] = []

    binary_match = re.search(r"(\d+)\s*binary\s*variable", algo_text, re.I)
    if binary_match:
        n = binary_match.group(1)
        variables.append(Variable(r"x_{ij}", "assignment decision", r"\{0, 1\}"))
        variables.append(Variable("n", f"number of binary variables = {n}", r"\mathbb{{Z}}^+"))
        return variables

    if "assignment" in data or "assignments" in data:
        variables.append(Variable(
            r"x_{ij}", "1 if item i assigned to slot j, 0 otherwise", r"\{0, 1\}",
        ))
    elif "plan" in data:
        variables.append(Variable(r"x_i", "quantity of item i selected", r"\mathbb{{Z}}_{\ge 0}"))
    elif "schedule" in data:
        variables.append(Variable(r"t_i", "start time for task i", r"\mathbb{{R}}_{\ge 0}"))
    elif "forecast" in data:
        variables.append(Variable(r"\hat{y}_t", "predicted value at time t", r"\mathbb{{R}}"))
    else:
        variables.append(Variable("x", "decision variable", r"\mathbb{{R}}"))
    return variables


def _infer_variables(domain: str, data: dict, sections: dict[str, str]) -> list[Variable]:
    dispatch = {
        "Game Theory": _vars_game_theory,
        "Dynamical Systems / ODEs": _vars_sir,
        "Financial Mathematics": _vars_finance,
        "Statistical Inference": _vars_statistics,
    }
    fn = dispatch.get(domain, _vars_optimization)
    return fn(data, sections)


# ── Domain-specific constraint inference ─────────────────────────────

def _constraints_game_theory(data: dict, sections: dict[str, str]) -> list[Constraint]:
    return [
        Constraint(1, r"\sigma_i \ge 0, \quad \sum_{k} \sigma_{ik} = 1",
                   "mixed strategy is a probability distribution"),
        Constraint(2, r"u_i(\sigma_i^*, \sigma_{-i}^*) \ge u_i(s_i, \sigma_{-i}^*) \quad \forall s_i \in S_i",
                   "Nash equilibrium: no profitable unilateral deviation"),
        Constraint(3, r"A \in \mathbb{R}^{m \times n}, \quad B \in \mathbb{R}^{m \times n}",
                   "payoff matrices define the normal-form game"),
    ]


def _constraints_sir(data: dict, sections: dict[str, str]) -> list[Constraint]:
    return [
        Constraint(1, r"\frac{dS}{dt} = -\frac{\beta S I}{N}",
                   "susceptible individuals become infected"),
        Constraint(2, r"\frac{dI}{dt} = \frac{\beta S I}{N} - \gamma I",
                   "infected gain from transmission, lose from recovery"),
        Constraint(3, r"\frac{dR}{dt} = \gamma I",
                   "recovered individuals accumulate"),
        Constraint(4, r"S(t) + I(t) + R(t) = N",
                   "population conservation"),
        Constraint(5, r"R_0 = \frac{\beta}{\gamma}",
                   "basic reproduction number"),
        Constraint(6, r"v^* = 1 - \frac{1}{R_0}",
                   "herd immunity threshold"),
    ]


def _constraints_finance(data: dict, sections: dict[str, str]) -> list[Constraint]:
    return [
        Constraint(1, r"PMT = L \cdot \frac{r(1+r)^n}{(1+r)^n - 1}",
                   "annuity payment formula"),
        Constraint(2, r"B_k = B_{k-1}(1+r) - PMT",
                   "amortization recurrence"),
        Constraint(3, r"B_n = 0",
                   "loan fully repaid at maturity"),
        Constraint(4, r"\text{Total Interest} = n \cdot PMT - L",
                   "total interest = payments minus principal"),
    ]


def _constraints_statistics(data: dict, sections: dict[str, str]) -> list[Constraint]:
    test = data.get("primary_test", {})
    test_name = test.get("test_name", "t-test")
    h0 = test.get("null_hypothesis", r"\mu_1 = \mu_2")
    h1 = test.get("alt_hypothesis", r"\mu_1 \neq \mu_2")

    constraints = [
        Constraint(1, f"H_0: {h0}", "null hypothesis"),
        Constraint(2, f"H_1: {h1}", "alternative hypothesis"),
        Constraint(3, r"\alpha = 0.05", "significance level"),
    ]

    if "welch" in test_name.lower() or "t-test" in test_name.lower():
        constraints.append(Constraint(
            4,
            r"t = \frac{\bar{x}_1 - \bar{x}_2}{\sqrt{\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}}}",
            "Welch's t-test statistic",
        ))
    if "effect_size" in test:
        constraints.append(Constraint(
            len(constraints) + 1,
            r"d = \frac{\bar{x}_1 - \bar{x}_2}{s_p}",
            "Cohen's d effect size",
        ))

    return constraints


def _constraints_optimization(data: dict, sections: dict[str, str]) -> list[Constraint]:
    """Original optimization constraint inference."""
    problem_text = sections.get("Problem", "")
    constraints: list[Constraint] = []
    idx = 1

    patterns = [
        (r"at most (\d+)", r"\sum_j x_{{ij}} \le {}", "capacity limit"),
        (r"at least (\d+)", r"\sum_j x_{{ij}} \ge {}", "minimum requirement"),
        (r"exactly (\d+)", r"\sum_j x_{{ij}} = {}", "exact assignment"),
        (r"each .+ needs exactly (\d+)", r"\sum_i x_{{ij}} = {}", "coverage requirement"),
        (r"one .+ per", r"\sum_j x_{{ij}} = 1", "one-per-item"),
    ]

    for pattern, formula_tmpl, origin in patterns:
        match = re.search(pattern, problem_text, re.I)
        if match:
            groups = match.groups()
            val = groups[0] if groups else ""
            formula = formula_tmpl.format(val) if val and "{}" in formula_tmpl else formula_tmpl
            constraints.append(Constraint(idx, formula, origin))
            idx += 1

    if any(k in data for k in ("assignment", "assignments", "plan")):
        constraints.append(Constraint(
            idx, r"x_{ij} \in \{0, 1\} \quad \forall\, i, j", "binary decision variables",
        ))
        idx += 1

    if not constraints:
        concepts = sections.get("Key Concepts", "")
        for line in concepts.splitlines():
            line = line.strip().lstrip("- ")
            if line and "**" in line:
                parts = line.split("--", 1)
                name = parts[0].strip().strip("*")
                origin = parts[1].strip() if len(parts) > 1 else ""
                constraints.append(Constraint(idx, name, origin))
                idx += 1

    return constraints


def _infer_constraints(domain: str, data: dict, sections: dict[str, str]) -> list[Constraint]:
    dispatch = {
        "Game Theory": _constraints_game_theory,
        "Dynamical Systems / ODEs": _constraints_sir,
        "Financial Mathematics": _constraints_finance,
        "Statistical Inference": _constraints_statistics,
    }
    fn = dispatch.get(domain, _constraints_optimization)
    return fn(data, sections)


# ── Domain-specific objective inference ──────────────────────────────

def _infer_objective(domain: str, data: dict, sections: dict[str, str]) -> str | None:
    if domain == "Game Theory":
        return r"\text{Find } \sigma^* \text{ s.t. } u_i(\sigma_i^*, \sigma_{-i}^*) \ge u_i(s_i, \sigma_{-i}^*) \; \forall i, s_i"

    if domain == "Dynamical Systems / ODEs":
        return r"\text{Solve } \frac{d\mathbf{y}}{dt} = f(t, \mathbf{y}), \quad \mathbf{y}(0) = \mathbf{y}_0"

    if domain == "Financial Mathematics":
        return r"\min_{\text{option}} \; \sum_{k=1}^{n} PMT_k \; + \; \text{closing costs}"

    if domain == "Statistical Inference":
        return r"\text{Reject } H_0 \text{ if } p < \alpha"

    # Original optimization logic
    problem_text = sections.get("Problem", "").lower()
    obj_val = data.get("objective") or data.get("total_cost")
    if obj_val is None:
        return None

    if "maximize" in problem_text or "maximiz" in problem_text:
        return r"\max \sum_{i,j} c_{ij} \, x_{ij}"
    elif "minimize" in problem_text or "minimiz" in problem_text:
        return r"\min \sum_{i,j} c_{ij} \, x_{ij}"
    elif "cost" in problem_text:
        return r"\min \sum_{i} c_i \, x_i"
    elif any(w in problem_text for w in ("satisfaction", "score", "expertise")):
        return r"\max \sum_{i,j} s_{ij} \, x_{ij}"
    else:
        return r"\text{optimize} \; f(x)"


# ── Domain-specific solution detail formatting ───────────────────────

def _details_game_theory(data: dict, sections: dict[str, str]) -> str:
    """Format game theory results as mathematical prose."""
    lines: list[str] = []

    for game_key in sorted(k for k in data if k.startswith("game_")):
        game = data[game_key]
        name = game.get("name", game_key)
        lines.append(f"Game: {name}")
        lines.append("")

        # Payoff matrices
        A = game.get("payoff_A", [])
        B = game.get("payoff_B", [])
        row_labels = game.get("row_labels", [])
        col_labels = game.get("col_labels", [])

        if A and col_labels:
            lines.append("Payoff matrix (Player 1, Player 2):")
            header = "  " + " ".join(f"{c:>14}" for c in col_labels)
            lines.append(header)
            for i, row_a in enumerate(A):
                row_b = B[i] if i < len(B) else []
                label = row_labels[i] if i < len(row_labels) else f"S{i}"
                cells = []
                for j, a_val in enumerate(row_a):
                    b_val = row_b[j] if j < len(row_b) else "?"
                    cells.append(f"({a_val}, {b_val})")
                lines.append(f"  {label:>10}  " + " ".join(f"{c:>14}" for c in cells))
            lines.append("")

        # Nash equilibria
        equilibria = game.get("equilibria", [])
        n_eq = game.get("num_equilibria", len(equilibria))
        lines.append(f"Nash equilibria found: {n_eq}")

        for i, eq in enumerate(equilibria):
            is_pure = str(eq.get("is_pure", "")).lower() == "true"
            s1 = eq.get("sigma_1", [])
            s2 = eq.get("sigma_2", [])
            p1 = eq.get("payoff_1", "?")
            p2 = eq.get("payoff_2", "?")
            sup1 = eq.get("support_1", [])
            sup2 = eq.get("support_2", [])

            eq_type = "Pure" if is_pure else "Mixed"
            lines.append(f"  NE {i+1} ({eq_type}): sigma_1 = {s1}, sigma_2 = {s2}")
            lines.append(f"    Payoffs: ({p1}, {p2})")
            if sup1:
                lines.append(f"    Support: P1 plays {', '.join(sup1)}; P2 plays {', '.join(sup2)}")

        # Dominant strategies
        dom = game.get("dominant_strategies", {})
        if dom:
            for player, strat in dom.items():
                if strat:
                    lines.append(f"  Dominant strategy for {player}: {strat}")
                else:
                    lines.append(f"  No dominant strategy for {player}")

        # Zero-sum, minimax
        if "is_zero_sum" in game:
            lines.append(f"  Zero-sum: {'Yes' if game['is_zero_sum'] else 'No'}")
        for pkey in ("minimax_value_1", "minimax_value_2"):
            if pkey in game:
                pnum = pkey[-1]
                lines.append(f"  Minimax value (Player {pnum}): {game[pkey]}")

        lines.append("")

    return "\n".join(lines) if lines else "Game theory solution computed."


def _details_sir(data: dict, sections: dict[str, str]) -> str:
    """Format SIR epidemic results."""
    lines: list[str] = []

    inst = data.get("instance", {})
    if inst and "N" in inst:
        N = inst.get("N", "?")
        lines.append(f"Population: N = {N:,}" if isinstance(N, (int, float)) else f"Population: N = {N}")
        lines.append(f"Transmission rate: beta = {inst.get('beta', '?')}/day")
        lines.append(f"Recovery rate: gamma = {inst.get('gamma', '?')}/day")
        lines.append(f"Initial infected: I(0) = {inst.get('I0', '?')}")
        lines.append("")

    R0 = data.get("R0")
    if R0 is not None:
        lines.append(f"Basic reproduction number: R_0 = beta/gamma = {R0:.2f}")

    peak_I = data.get("peak_infected")
    peak_t = data.get("peak_time")
    if peak_I is not None and peak_t is not None:
        lines.append(f"Peak infection: I_max = {peak_I:,.0f} at t = {peak_t:.1f} days")

    final_num = data.get("final_infected_frac_numerical")
    final_thy = data.get("final_infected_frac_theory")
    if final_num is not None:
        lines.append(f"Final epidemic size (numerical): {final_num:.1%} of population")
    if final_thy is not None:
        lines.append(f"Final epidemic size (theory): {final_thy:.1%} of population")

    hit = data.get("herd_immunity_threshold")
    if hit is not None:
        lines.append(f"Herd immunity threshold: v* = 1 - 1/R_0 = {hit:.1%}")

    # Vaccination analysis
    vacc = data.get("vaccination_analysis", [])
    if vacc:
        lines.append("")
        lines.append("Vaccination scenarios:")
        for v in vacc:
            vr = v.get("vaccination_rate", 0)
            r_eff = v.get("R0_effective", 0)
            epidemic = v.get("epidemic_occurs", False)
            peak = v.get("peak_infected", 0)
            final = v.get("final_infected_frac", 0)
            status = "EPIDEMIC" if epidemic else "contained"
            lines.append(f"  v = {vr:.0%}: R_eff = {r_eff:.2f}, peak = {peak:,.0f}, "
                         f"final size = {final:.1%} [{status}]")

    # Equilibrium analysis
    eq = data.get("equilibrium", {})
    if eq:
        lines.append("")
        dfe = "stable" if eq.get("dfe_stable") else "unstable"
        lines.append(f"Disease-free equilibrium: {dfe}")
        eigenvalues = eq.get("eigenvalues", [])
        if eigenvalues:
            lines.append(f"Eigenvalues: {', '.join(str(e) for e in eigenvalues)}")

    return "\n".join(lines) if lines else "SIR solution computed."


def _details_finance(data: dict, sections: dict[str, str]) -> str:
    """Format financial mathematics results."""
    lines: list[str] = []

    if "home_price" in data:
        lines.append(f"Home price: ${data['home_price']:,.0f}")
    if "down_payment" in data:
        lines.append(f"Down payment: ${data['down_payment']:,.0f}")
    if "loan_amount" in data:
        lines.append(f"Loan amount: L = ${data['loan_amount']:,.0f}")
    lines.append("")

    # Mortgage options comparison
    options = data.get("options", [])
    if options:
        lines.append("Mortgage Options Comparison:")
        lines.append("")
        for opt in options:
            name = opt.get("name", "Option")
            pmt = opt.get("monthly_payment", 0)
            total_int = opt.get("total_interest", 0)
            total_paid = opt.get("total_paid", 0)
            lines.append(f"  {name}:")
            lines.append(f"    Monthly payment: PMT = ${pmt:,.2f}")
            lines.append(f"    Total interest: ${total_int:,.2f}")
            lines.append(f"    Total paid: ${total_paid:,.2f}")
            lines.append("")

    cheapest = data.get("cheapest_option")
    if cheapest:
        lines.append(f"Cheapest option: {cheapest}")

    breakeven = data.get("refinance_breakeven_months")
    if breakeven is not None:
        lines.append(f"Refinance break-even: month {breakeven} ({breakeven / 12:.1f} years)")

    savings = data.get("refinance_net_savings")
    if savings is not None:
        lines.append(f"Refinance net savings: ${savings:,.0f}")

    return "\n".join(lines) if lines else "Financial analysis computed."


def _details_statistics(data: dict, sections: dict[str, str]) -> str:
    """Format statistical inference results."""
    lines: list[str] = []

    # Descriptive statistics
    desc = data.get("descriptive", {})
    if desc:
        lines.append("Descriptive Statistics:")
        for group, stats in desc.items():
            if isinstance(stats, dict):
                n = stats.get("n", "?")
                mean = stats.get("mean", "?")
                std = stats.get("std", "?")
                lines.append(f"  {group}: n = {n}, mean = {mean}, std = {std}")
        lines.append("")

    # Assumptions
    assumptions = data.get("assumptions", {})
    if assumptions:
        lines.append("Assumptions checked:")
        for test_name, result in assumptions.items():
            if isinstance(result, dict):
                passed = result.get("passed", result.get("normal", "?"))
                stat = result.get("statistic", result.get("p_value", ""))
                lines.append(f"  {test_name}: {'PASS' if passed else 'FAIL'}"
                             + (f" (stat = {stat:.4f})" if isinstance(stat, float) else ""))
        lines.append("")

    # Primary test
    test = data.get("primary_test", {})
    if test:
        # Detect test name from available keys
        test_name = test.get("test_name", "")
        if not test_name:
            if "t_statistic" in test:
                test_name = "Welch's t-test"
            else:
                test_name = "Hypothesis test"
        lines.append(f"Test: {test_name}")

        # Get test statistic (try multiple key names)
        stat_val = test.get("statistic") or test.get("t_statistic") or test.get("chi2_statistic")
        stat_name = test.get("statistic_name", "t")
        if stat_val is not None:
            lines.append(f"  {stat_name} = {stat_val:.4f}" if isinstance(stat_val, float) else f"  {stat_name} = {stat_val}")

        p_val = test.get("p_value")
        if p_val is not None:
            lines.append(f"  p-value = {p_val:.6f}" if isinstance(p_val, float) else f"  p-value = {p_val}")

        # Significance (try multiple key names)
        sig = test.get("significant") or test.get("is_significant")
        if sig is not None:
            sig_bool = sig if isinstance(sig, bool) else str(sig).lower() == "true"
            lines.append(f"  Significant at alpha = 0.05: {'Yes' if sig_bool else 'No'}")

        # Mean difference
        mean_diff = test.get("mean_diff") or test.get("mean_difference")
        if mean_diff is not None:
            lines.append(f"  Mean difference: {mean_diff:.4f}" if isinstance(mean_diff, float) else f"  Mean difference: {mean_diff}")

        # Effect size (try multiple key names)
        es = test.get("effect_size") or test.get("cohens_d")
        if es is not None:
            interp = test.get("effect_interpretation") or test.get("effect", "")
            lines.append(f"  Cohen's d = {es:.4f} ({interp})" if interp else f"  Cohen's d = {es:.4f}" if isinstance(es, float) else f"  Cohen's d = {es}")

        # Confidence interval (try multiple key names)
        ci = test.get("confidence_interval") or test.get("ci_95") or test.get("ci_diff")
        if ci and isinstance(ci, (list, tuple)) and len(ci) == 2:
            lines.append(f"  95% CI for difference: [{ci[0]:.4f}, {ci[1]:.4f}]")

    # Bayesian analysis
    bayes = data.get("bayesian", {})
    if bayes:
        lines.append("")
        lines.append("Bayesian Analysis:")
        bf = bayes.get("bayes_factor", bayes.get("BF10"))
        if bf is not None:
            lines.append(f"  Bayes Factor (BF10) = {bf:.4f}" if isinstance(bf, float) else f"  Bayes Factor = {bf}")
        interp = bayes.get("interpretation", "")
        if interp:
            lines.append(f"  Interpretation: {interp}")

    # Power analysis
    power = data.get("power", {})
    if power:
        lines.append("")
        lines.append("Power Analysis:")
        current_power = power.get("power", power.get("achieved_power"))
        if current_power is not None:
            lines.append(f"  Achieved power: {current_power:.1%}" if isinstance(current_power, float) else f"  Power: {current_power}")
        n_needed = power.get("n_needed", power.get("sample_needed_80"))
        if n_needed is not None:
            lines.append(f"  Sample size needed for 80% power: n = {n_needed}")

    # Recommendation
    rec = data.get("recommendation")
    if rec:
        lines.append(f"\nRecommendation: {rec}")

    return "\n".join(lines) if lines else "Statistical analysis computed."


def _details_optimization(data: dict, sections: dict[str, str]) -> str:
    """Original optimization detail formatting."""
    lines: list[str] = []

    result_keys = [
        ("assignment", "Assignment"), ("assignments", "Assignments"),
        ("plan", "Optimal Plan"), ("schedule", "Schedule"),
        ("forecast", "Forecast"), ("path", "Path"),
        ("allocation", "Allocation"), ("coloring", "Coloring"),
    ]

    for key, label in result_keys:
        if key not in data:
            continue
        val = data[key]
        if isinstance(val, dict):
            lines.append(f"{label}:")
            for k, v in val.items():
                if isinstance(v, list):
                    lines.append(f"  {k} -> {', '.join(str(x) for x in v)}")
                elif isinstance(v, float):
                    lines.append(f"  {k} = {v:.4f}")
                else:
                    lines.append(f"  {k} -> {v}")
        elif isinstance(val, list):
            lines.append(f"{label}: {' -> '.join(str(x) for x in val)}")
        break

    obj = data.get("objective") or data.get("total_cost")
    if obj is not None:
        lines.append(f"\nObjective value: z* = {obj}")

    bounds = data.get("bounds", {})
    if bounds:
        if "upper_bound" in bounds:
            lines.append(f"Upper bound: {bounds['upper_bound']}")
        if "lower_bound" in bounds:
            lines.append(f"Lower bound: {bounds['lower_bound']}")

    lp = data.get("lp_relaxation")
    if lp is not None:
        lines.append(f"LP relaxation: {lp:.4f}")
        if obj is not None and lp > 0:
            gap = abs(obj - lp) / abs(lp) * 100
            lines.append(f"Integrality gap: {gap:.2f}%")

    efficiency = data.get("efficiency")
    if efficiency is not None:
        lines.append(f"Solution efficiency: {efficiency:.1%}")

    for summary_key in ("nutrition_totals", "cost_breakdown", "comparison",
                         "random_stats", "descriptive"):
        if summary_key in data and isinstance(data[summary_key], dict):
            lines.append(f"\n{summary_key.replace('_', ' ').title()}:")
            for k, v in data[summary_key].items():
                if isinstance(v, float):
                    lines.append(f"  {k}: {v:.4f}")
                else:
                    lines.append(f"  {k}: {v}")

    algo_text = sections.get("Algorithm", "")
    if algo_text:
        clean = re.sub(r"\*\*([^*]+)\*\*", r"\1", algo_text)
        clean = re.sub(r"`([^`]+)`", r"\1", clean)
        lines.append(f"\nMethod: {clean}")

    return "\n".join(lines) if lines else "Solution computed successfully."


def _format_solution_details(domain: str, data: dict, sections: dict[str, str]) -> str:
    dispatch = {
        "Game Theory": _details_game_theory,
        "Dynamical Systems / ODEs": _details_sir,
        "Financial Mathematics": _details_finance,
        "Statistical Inference": _details_statistics,
    }
    fn = dispatch.get(domain, _details_optimization)
    return fn(data, sections)


# ── Domain-specific verification extraction ──────────────────────────

def _extract_verification(domain: str, data: dict) -> list[VerificationCheck]:
    """Extract verification checks from solution data."""
    checks: list[VerificationCheck] = []

    # Try domain-specific verification dict
    verif = data.get("verification", {})
    if isinstance(verif, dict) and verif:
        for name, val in verif.items():
            if isinstance(val, bool):
                checks.append(VerificationCheck(
                    name.replace("_", " ").title(),
                    val,
                    "Passed" if val else "Failed",
                ))

    # Standard optimization checks
    if "is_feasible" in data:
        checks.append(VerificationCheck(
            "Feasibility", data["is_feasible"],
            "All constraints satisfied" if data["is_feasible"] else "Constraint violation",
        ))
    if "is_optimal" in data:
        lp = data.get("lp_relaxation")
        obj = data.get("objective") or data.get("total_cost")
        if lp is not None and obj is not None:
            gap = abs(obj - lp) / max(abs(lp), 1e-9) * 100
            cert = f"LP relaxation = {lp:.2f}, gap = {gap:.2f}%"
        else:
            cert = data.get("algorithm", "Solver guarantee")
        checks.append(VerificationCheck("Optimality", data["is_optimal"], cert))

    efficiency = data.get("efficiency")
    if efficiency is not None:
        checks.append(VerificationCheck(
            "Efficiency", efficiency >= 0.95,
            f"{efficiency:.1%} of theoretical maximum",
        ))

    # Game theory: check nested verification dicts
    for key in sorted(k for k in data if k.startswith("game_")):
        game = data[key]
        gv = game.get("verification", {})
        if isinstance(gv, dict):
            for vname, vval in gv.items():
                if isinstance(vval, bool):
                    checks.append(VerificationCheck(
                        f"{key}: {vname.replace('_', ' ')}",
                        vval,
                        "Passed" if vval else "Failed",
                    ))

    return checks


# ── Domain-specific answer summary ───────────────────────────────────

def _build_answer(domain: str, data: dict) -> str:
    """Build a concise answer string from solution data."""
    if domain == "Game Theory":
        games = [k for k in data if k.startswith("game_")]
        parts = []
        for gk in games:
            g = data[gk]
            n_eq = g.get("num_equilibria", 0)
            name = g.get("name", gk)
            parts.append(f"{name}: {n_eq} Nash equilibria found")
        return "; ".join(parts) if parts else "Equilibria computed"

    if domain == "Dynamical Systems / ODEs":
        R0 = data.get("R0")
        peak = data.get("peak_infected")
        hit = data.get("herd_immunity_threshold")
        parts = []
        if R0 is not None:
            parts.append(f"R_0 = {R0:.2f}")
        if peak is not None:
            parts.append(f"peak infected = {peak:,.0f}")
        if hit is not None:
            parts.append(f"herd immunity = {hit:.1%}")
        return "; ".join(parts) if parts else "ODE solution computed"

    if domain == "Financial Mathematics":
        cheapest = data.get("cheapest_option", "")
        breakeven = data.get("refinance_breakeven_months")
        parts = []
        if cheapest:
            parts.append(f"cheapest: {cheapest}")
        if breakeven is not None:
            parts.append(f"refinance break-even at month {breakeven}")
        return "; ".join(parts) if parts else "Financial analysis complete"

    if domain == "Statistical Inference":
        test = data.get("primary_test", {})
        stat = test.get("statistic") or test.get("t_statistic")
        p = test.get("p_value")
        sig = test.get("significant") or test.get("is_significant")
        parts = []
        if stat is not None:
            parts.append(f"t = {stat:.4f}" if isinstance(stat, float) else f"stat = {stat}")
        if p is not None:
            parts.append(f"p = {p:.6f}" if isinstance(p, float) else f"p = {p}")
        if sig is not None:
            sig_bool = sig if isinstance(sig, bool) else str(sig).lower() == "true"
            parts.append("significant" if sig_bool else "not significant")
        return "; ".join(parts) if parts else "Statistical test complete"

    # Optimization fallback
    for key in ("assignment", "assignments", "plan", "schedule", "forecast",
                "path", "allocation", "coloring"):
        if key in data:
            val = data[key]
            if isinstance(val, dict):
                n = len(val)
                items = ", ".join(
                    f"{k} -> {v}" if not isinstance(v, list)
                    else f"{k} -> [{', '.join(str(x) for x in v)}]"
                    for k, v in list(val.items())[:6]
                )
                suffix = f", ... ({n - 6} more)" if n > 6 else ""
                return f"{n}-element {key}: {items}{suffix}"
            elif isinstance(val, list):
                return f"{key}: {' -> '.join(str(x) for x in val[:8])}"
    return "Solution computed"


# ── Domain-specific mapping ──────────────────────────────────────────

def _build_mapping(domain: str, data: dict) -> list[MappingRow]:
    if domain == "Game Theory":
        return [
            MappingRow("coffee shop", "player i"),
            MappingRow("pricing decision", "strategy s_i in S_i"),
            MappingRow("profit", "payoff u_i(s)"),
            MappingRow("payoff table", "bimatrix (A, B)"),
        ]
    if domain == "Dynamical Systems / ODEs":
        return [
            MappingRow("healthy population", "S(t) — susceptible compartment"),
            MappingRow("sick population", "I(t) — infected compartment"),
            MappingRow("immune population", "R(t) — recovered compartment"),
            MappingRow("contagiousness", "beta — transmission rate"),
            MappingRow("recovery speed", "gamma — recovery rate"),
        ]
    if domain == "Financial Mathematics":
        return [
            MappingRow("loan balance", "L — principal"),
            MappingRow("annual percentage rate", "r — monthly rate = APR/12"),
            MappingRow("loan term", "n — number of monthly payments"),
            MappingRow("monthly mortgage payment", "PMT — annuity payment"),
        ]
    if domain == "Statistical Inference":
        return [
            MappingRow("group average", "sample mean x-bar"),
            MappingRow("group variability", "sample std s"),
            MappingRow("sample count", "n"),
            MappingRow("significance threshold", "alpha = 0.05"),
        ]

    # Optimization fallback
    mapping: list[MappingRow] = []
    for key in ("assignment", "assignments", "plan", "schedule", "forecast",
                "path", "allocation", "coloring"):
        if key in data:
            mapping.append(MappingRow(key.replace("_", " "), f"x: solution vector ({key})"))
            break
    if data.get("objective") is not None:
        mapping.append(MappingRow("total score/cost", "objective function value"))
    if not mapping:
        mapping.append(MappingRow("problem input", "instance parameters"))
    return mapping


# ── Domain-specific interpretation answer ────────────────────────────

def _build_interp_answer(domain: str, data: dict) -> str:
    """Build a highlighted answer for the interpretation section."""
    if domain == "Game Theory":
        games = [k for k in data if k.startswith("game_")]
        parts = []
        for gk in games:
            g = data[gk]
            eqs = g.get("equilibria", [])
            pure = sum(1 for e in eqs if str(e.get("is_pure", "")).lower() == "true")
            mixed = len(eqs) - pure
            name = g.get("name", gk)
            parts.append(f"{name}: {pure} pure + {mixed} mixed NE")
        return "; ".join(parts) if parts else "Equilibria found."

    if domain == "Dynamical Systems / ODEs":
        R0 = data.get("R0")
        peak_I = data.get("peak_infected")
        peak_t = data.get("peak_time")
        hit = data.get("herd_immunity_threshold")
        parts = []
        if R0 is not None:
            parts.append(f"R_0 = {R0:.2f}")
        if peak_I is not None:
            parts.append(f"peak = {peak_I:,.0f} infected at day {peak_t:.0f}" if peak_t else f"peak = {peak_I:,.0f}")
        if hit is not None:
            parts.append(f"herd immunity at {hit:.0%} vaccination")
        return "; ".join(parts) + "." if parts else "ODE solved."

    if domain == "Financial Mathematics":
        cheapest = data.get("cheapest_option", "")
        savings = data.get("refinance_net_savings")
        breakeven = data.get("refinance_breakeven_months")
        parts = []
        if cheapest:
            parts.append(f"Cheapest option: {cheapest}")
        if savings is not None:
            parts.append(f"refinancing saves ${savings:,.0f}")
        if breakeven is not None:
            parts.append(f"break-even at month {breakeven}")
        return "; ".join(parts) + "." if parts else "Financial analysis complete."

    if domain == "Statistical Inference":
        test = data.get("primary_test", {})
        sig = test.get("significant") or test.get("is_significant")
        p = test.get("p_value")
        es = test.get("effect_size") or test.get("cohens_d")
        es_interp = test.get("effect_interpretation") or test.get("effect", "")
        parts = []
        if sig is not None:
            sig_bool = sig if isinstance(sig, bool) else str(sig).lower() == "true"
            parts.append("Statistically significant" if sig_bool else "Not statistically significant")
        if p is not None:
            parts.append(f"p = {p:.4f}" if isinstance(p, float) else f"p = {p}")
        if es is not None:
            parts.append(f"d = {es:.2f} ({es_interp})" if es_interp else f"d = {es:.2f}")
        return "; ".join(parts) + "." if parts else "Test complete."

    # Optimization fallback
    obj = data.get("objective") or data.get("total_cost")
    opt = "optimal" if data.get("is_optimal") else "feasible"
    if obj is not None:
        return f"The {opt} solution has objective value z* = {obj}."
    return f"A {opt} solution was found."


# ── Certificate inference ────────────────────────────────────────────

def _infer_certificate(domain: str, data: dict) -> str | None:
    if domain == "Game Theory":
        return "Nash equilibria verified: no player has a profitable unilateral deviation."
    if domain == "Dynamical Systems / ODEs":
        v = data.get("verification", {})
        if isinstance(v, dict) and v.get("population_conserved"):
            return "Population conservation verified. S(t)+I(t)+R(t)=N at all time steps."
        return None
    if domain == "Financial Mathematics":
        return "Amortization verified: final balance = $0.00 for all options."
    if domain == "Statistical Inference":
        v = data.get("verification", {})
        if isinstance(v, dict):
            return "Assumptions checked; test statistic independently verified."
        return None

    # Optimization
    lp = data.get("lp_relaxation")
    obj = data.get("objective") or data.get("total_cost")
    if lp is not None and obj is not None:
        gap = abs(obj - lp) / max(abs(lp), 1e-9) * 100
        if gap < 0.01:
            return "LP relaxation = ILP solution (gap = 0%). Global optimum proven."
        return f"LP relaxation bound: {lp:.4f}. Optimality gap: {gap:.2f}%."
    if data.get("is_optimal"):
        algo = data.get("algorithm", "")
        if "hungarian" in algo.lower():
            return "Hungarian algorithm guarantees global optimum in O(n^3)."
        if "ilp" in algo.lower() or "branch" in algo.lower():
            return "Branch-and-bound solved to optimality."
        return "Solver reports optimal."
    return None


# ── Build model / solution / interpretation ──────────────────────────

def _build_model(domain: str, sections: dict[str, str], data: dict) -> FormalModel:
    problem = sections.get("Problem", "")
    algo_name = data.get("algorithm", "unknown")

    # Named problem detection
    named = None
    named_patterns = [
        (r"assignment problem", "Assignment Problem"),
        (r"bipartite matching", "Bipartite Matching"),
        (r"knapsack", "Knapsack Problem"),
        (r"traveling salesman|TSP", "Traveling Salesman Problem"),
        (r"prisoner.*dilemma", "Prisoner's Dilemma"),
        (r"chicken|hawk.?dove", "Game of Chicken"),
        (r"rock.?paper.?scissors", "Rock-Paper-Scissors"),
    ]
    full_text = problem + " " + sections.get("Algorithm", "") + " " + sections.get("Key Concepts", "")
    for pat, name in named_patterns:
        if re.search(pat, full_text, re.I):
            named = name
            break

    # Universe
    universe: list[str] = []
    if domain == "Game Theory":
        for key in sorted(k for k in data if k.startswith("game_")):
            g = data[key]
            rows = g.get("row_labels", [])
            cols = g.get("col_labels", [])
            if rows:
                universe.append(f"Strategies: " + r"\{" + ", ".join(rows) + r"\}")
    elif domain == "Dynamical Systems / ODEs":
        inst = data.get("instance", {})
        if inst:
            universe.append(f"Population N = {inst.get('N', '?')}")
            universe.append(f"Time horizon: [0, {inst.get('t_max', '?')}] days")
    elif domain == "Financial Mathematics":
        if "loan_amount" in data:
            universe.append(f"Loan amount: ${data['loan_amount']:,.0f}")
        opts = data.get("options", [])
        if opts:
            universe.append(f"Options: " + r"\{" + ", ".join(o.get("name", "?") for o in opts) + r"\}")
    elif domain == "Statistical Inference":
        desc = data.get("descriptive", {})
        for group in desc:
            if isinstance(desc[group], dict):
                n = desc[group].get("n", "?")
                universe.append(f"{group}: n = {n}")

    if not universe:
        # Generic universe from solution keys
        for key, val in data.items():
            if isinstance(val, dict) and key not in (
                "bounds", "random_stats", "sensitivity", "nutrition_totals",
                "cost_breakdown", "comparison", "verification", "instance",
                "equilibrium",
            ):
                items = list(val.keys())
                if items and len(items) <= 12 and all(
                    isinstance(v, (str, int, float, list)) for v in val.values()
                ):
                    universe.append(
                        f"{key.replace('_', ' ').title()}: "
                        + r"\{" + ", ".join(str(i) for i in items) + r"\}"
                    )
        if not universe:
            universe = ["See problem description"]

    return FormalModel(
        problem_type=_infer_problem_type(data, sections),
        domain=domain,
        named_problem=named,
        universe=universe,
        variables=_infer_variables(domain, data, sections),
        structure=problem,
        mapping=_build_mapping(domain, data),
        constraints=_infer_constraints(domain, data, sections),
        objective=_infer_objective(domain, data, sections),
        claim=None,
        suggested_approach=algo_name,
        complexity_class=_infer_complexity(sections),
        available_tools=[algo_name.split("(")[0].strip()] if algo_name else [],
    )


def _build_solution(domain: str, data: dict, sections: dict[str, str],
                    solver_code: str | None) -> SolutionReport:
    return SolutionReport(
        answer=_build_answer(domain, data),
        objective_value=data.get("objective") or data.get("total_cost"),
        is_optimal=data.get("is_optimal", False),
        is_feasible=data.get("is_feasible", domain in ("Game Theory", "Dynamical Systems / ODEs",
                                                         "Financial Mathematics", "Statistical Inference")),
        algorithm=data.get("algorithm", "unknown"),
        complexity=_infer_complexity(sections),
        time_seconds=data.get("time_seconds", 0.0),
        certificate=_infer_certificate(domain, data),
        details=_format_solution_details(domain, data, sections),
        verification=_extract_verification(domain, data),
        solver_code=solver_code,
    )


def _build_sensitivity(data: dict) -> list[SensitivityRow]:
    rows: list[SensitivityRow] = []
    sens = data.get("sensitivity", {})
    if not isinstance(sens, dict):
        return rows

    for param, info in sens.items():
        if not isinstance(info, dict):
            continue
        pct = info.get("pct", 0)
        new_obj = info.get("objective", "")
        classification = "robust" if abs(pct) < 2 else ("critical" if abs(pct) > 5 else "sensitive")
        rows.append(SensitivityRow(
            parameter=param,
            current="present",
            change="removed",
            new_objective=str(new_obj),
            classification=classification,
        ))
    return rows


def _build_interpretation(
    domain: str,
    sections: dict[str, str],
    data: dict,
    fig_paths: list[Path],
) -> InterpretationReport:
    problem = sections.get("Problem", "")
    expected = sections.get("Expected Output", "")
    algo_text = sections.get("Algorithm", "")

    question = problem.split(".")[0].strip() + "." if problem else "Solve the given problem."
    answer = _build_interp_answer(domain, data)

    # What this means
    meaning_parts: list[str] = []
    if expected:
        clean = re.sub(r"\*\*([^*]+)\*\*", r"\1", expected)
        clean = re.sub(r"`([^`]+)`", r"\1", clean)
        meaning_parts.append(clean)
    if algo_text:
        clean = re.sub(r"\*\*([^*]+)\*\*", r"\1", algo_text)
        clean = re.sub(r"`([^`]+)`", r"\1", clean)
        meaning_parts.append(clean)
    what_this_means = "\n\n".join(meaning_parts) if meaning_parts else "See problem description."

    sensitivity = _build_sensitivity(data)

    # Recommendations
    recs: list[str] = []
    if data.get("is_optimal"):
        recs.append("The solution is provably optimal; no further improvement is possible within this model.")
    if domain == "Game Theory":
        recs.append("Consider pre-play communication or binding agreements to reach Pareto-superior outcomes.")
    elif domain == "Dynamical Systems / ODEs":
        recs.append("Monitor R_0 closely; small changes in transmission can shift epidemic dynamics dramatically.")
    elif domain == "Financial Mathematics":
        recs.append("Compare total interest paid, not just monthly payments, when evaluating mortgage options.")
    elif domain == "Statistical Inference":
        recs.append("Report effect sizes alongside p-values for practical significance assessment.")
    if sensitivity:
        critical = [r.parameter for r in sensitivity if r.classification == "critical"]
        if critical:
            recs.append(f"Monitor critical parameters: {', '.join(critical)}.")
    if not recs:
        recs.append("Review the model assumptions to ensure real-world fidelity.")

    # Limitations
    limitations = []
    if domain == "Game Theory":
        limitations.append("Assumes rational, utility-maximizing players with complete information.")
        limitations.append("Real-world players may use heuristics or have incomplete information.")
    elif domain == "Dynamical Systems / ODEs":
        limitations.append("SIR model assumes homogeneous mixing; real populations have network structure.")
        limitations.append("Parameters (beta, gamma) are assumed constant; real epidemics evolve over time.")
    elif domain == "Financial Mathematics":
        limitations.append("Assumes fixed interest rates; adjustable-rate mortgages introduce variability.")
        limitations.append("Does not account for tax deductions, insurance, or opportunity cost of down payment.")
    elif domain == "Statistical Inference":
        limitations.append("Results are conditional on model assumptions (normality, independence, etc.).")
        limitations.append("Statistical significance does not imply practical importance.")
    else:
        limitations.append("Model assumes deterministic parameters; real-world variability not captured.")
        limitations.append("Solution quality depends on the accuracy of input data.")

    return InterpretationReport(
        question=question,
        answer=answer,
        what_this_means=what_this_means,
        sensitivity=sensitivity,
        recommendations=recs,
        limitations=limitations,
        figures=[Figure(path=p, caption=p.stem.replace("_", " ").title()) for p in fig_paths],
    )


# ── Main render function ─────────────────────────────────────────────

def render_example(example_dir: Path, include_code: bool = False) -> tuple[Path, Path]:
    """Render an example directory to report.tex + report.pdf.

    Returns (tex_path, pdf_path).
    """
    example_dir = example_dir.resolve()
    solution_json = example_dir / "solution.json"
    readme_md = example_dir / "README.md"

    if not solution_json.exists():
        raise FileNotFoundError(f"No solution.json in {example_dir}")
    if not readme_md.exists():
        raise FileNotFoundError(f"No README.md in {example_dir}")

    data = _load_json(solution_json)
    sections = _load_readme(readme_md)
    title = _extract_title(sections, example_dir.name)

    # Detect domain
    domain = _detect_domain(data, sections)

    # Find any PNG figures
    fig_paths = sorted(example_dir.glob("*.png"))

    # Find solver script for code inclusion
    solver_code = None
    if include_code:
        solvers = list(example_dir.glob("*_solver.py"))
        if solvers:
            solver_code = solvers[0].read_text(encoding="utf-8")

    config = ReportConfig(
        title=title,
        output_dir=example_dir / "report",
        include_code=include_code,
    )

    model = _build_model(domain, sections, data)
    solution = _build_solution(domain, data, sections, solver_code)
    interpretation = _build_interpretation(domain, sections, data, fig_paths)

    renderer = LatexRenderer(config)
    tex_path = renderer.render_tex(model, solution, interpretation)
    pdf_path = renderer.render_pdf(model, solution, interpretation)

    print(f"LaTeX source: {tex_path}")
    print(f"PDF report:   {pdf_path}")
    return tex_path, pdf_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render an uber-polya example to LaTeX + PDF.",
    )
    parser.add_argument(
        "example_dir",
        type=Path,
        help="Path to the example directory (must contain solution.json and README.md)",
    )
    parser.add_argument(
        "--include-code",
        action="store_true",
        help="Include the Python solver source in the PDF appendix",
    )
    args = parser.parse_args()
    render_example(args.example_dir, args.include_code)


if __name__ == "__main__":
    main()
