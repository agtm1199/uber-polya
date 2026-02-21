"""Solver smoke tests -- run each example solver and verify it exits cleanly.

Each solver has a self-contained __main__ block that creates an instance,
calls solve(), runs independent verification, and prints results.
A zero exit code means the solver ran without errors.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"

# Map: (example_dir_name, solver_filename)
# Every solver with a __main__ block that can run standalone.
SOLVERS = [
    ("ab-testing", "ab_solver.py"),
    ("anomaly-detection", "anomaly_solver.py"),
    ("bin-packing", "bin_solver.py"),
    ("break-even", "breakeven_solver.py"),
    ("budget-optimization", "budget_solver.py"),
    ("cafe-tips", "cafe_solver.py"),
    ("causal-inference", "causal_solver.py"),
    ("classification", "classification_solver.py"),
    ("clustering", "clustering_solver.py"),
    ("customer-survival", "survival_solver.py"),
    ("epidemic-sir", "sir_solver.py"),
    ("event-seating", "seating_solver.py"),
    ("fair-rent", "rent_solver.py"),
    ("feature-importance", "feature_solver.py"),
    ("inspector-assignment", "inspector_solver.py"),
    ("inventory-optimization", "inventory_solver.py"),
    ("land-survey", "survey_solver.py"),
    ("meal-planning", "meal_solver.py"),
    ("milking-cows", "milk2.py"),
    ("monte-carlo-risk", "mc_solver.py"),
    ("mortgage-analysis", "mortgage_solver.py"),
    ("nash-equilibrium", "nash_solver.py"),
    ("pareto-optimization", "pareto_solver.py"),
    ("portfolio-optimization", "portfolio_solver.py"),
    ("project-prioritization", "priority_solver.py"),
    ("queuing-system", "queuing_solver.py"),
    ("root-finding", "root_solver.py"),
    ("route-planning", "route_solver.py"),
    ("sales-forecast", "sales_forecast_solver.py"),
    ("shift-scheduling", "shift_solver.py"),
    ("study-schedule", "study_solver.py"),
    ("team-assignment", "team_solver.py"),
    ("tournament-hamiltonian", "tournament_proof.py"),
    ("traffic-flow", "traffic_solver.py"),
    ("vendor-selection", "vendor_solver.py"),
    ("water-tank", "tank_solver.py"),
]


@pytest.mark.parametrize("example_dir,solver_file", SOLVERS, ids=[s[0] for s in SOLVERS])
def test_solver_runs(example_dir: str, solver_file: str):
    """Run the solver and assert it exits with code 0."""
    solver_path = EXAMPLES / example_dir / solver_file
    assert solver_path.exists(), f"Solver not found: {solver_path}"

    result = subprocess.run(
        [sys.executable, str(solver_path)],
        cwd=str(solver_path.parent),
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, (
        f"Solver {example_dir}/{solver_file} failed with exit code {result.returncode}\n"
        f"STDERR:\n{result.stderr[-2000:]}"
    )


def _check_passed(value) -> bool:
    """Check if a verification value represents a pass.

    Handles multiple patterns found across solvers:
      - True (bool)
      - "True" (string)
      - {"passed": True, ...} (nested dict with metadata)
      - float/int (metric values -- skip, not a pass/fail check)
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"
    if isinstance(value, dict) and "passed" in value:
        return _check_passed(value["passed"])
    # Numeric values (metrics) are not pass/fail checks -- skip them
    return True


# Solvers that write solution.json with a verification dict.
# Format: (example_dir, solver_file, json_key)
SOLVERS_WITH_VERIFICATION = [
    ("ab-testing", "ab_solver.py", "verification"),
    ("anomaly-detection", "anomaly_solver.py", "verification"),
    ("causal-inference", "causal_solver.py", "verification"),
    ("classification", "classification_solver.py", "verification"),
    ("clustering", "clustering_solver.py", "verification"),
    ("customer-survival", "survival_solver.py", "verification"),
    ("epidemic-sir", "sir_solver.py", "verification"),
    ("feature-importance", "feature_solver.py", "verification"),
    ("inventory-optimization", "inventory_solver.py", "verification"),
    ("monte-carlo-risk", "mc_solver.py", "verification"),
    ("queuing-system", "queuing_solver.py", "verification"),
    ("root-finding", "root_solver.py", "verification"),
    ("sales-forecast", "sales_forecast_solver.py", "verification"),
]


@pytest.mark.parametrize(
    "example_dir,solver_file,verify_key",
    SOLVERS_WITH_VERIFICATION,
    ids=[s[0] for s in SOLVERS_WITH_VERIFICATION],
)
def test_solver_verification_passes(example_dir: str, solver_file: str, verify_key: str):
    """Run the solver, parse solution.json, and assert all verification checks pass."""
    solver_path = EXAMPLES / example_dir / solver_file
    solution_path = solver_path.parent / "solution.json"

    # Run solver
    result = subprocess.run(
        [sys.executable, str(solver_path)],
        cwd=str(solver_path.parent),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Solver failed: {result.stderr[-1000:]}"

    # Parse solution.json
    assert solution_path.exists(), f"No solution.json produced by {example_dir}"
    with open(solution_path) as f:
        solution = json.load(f)

    assert verify_key in solution, (
        f"Key '{verify_key}' not found in solution.json. Keys: {list(solution.keys())}"
    )

    checks = solution[verify_key]
    assert isinstance(checks, dict), f"Expected dict, got {type(checks)}"

    failed = {k: v for k, v in checks.items() if not _check_passed(v)}
    assert not failed, (
        f"Verification checks failed for {example_dir}: {failed}"
    )


# Solvers that write solution.json with is_feasible/is_optimal flags
SOLVERS_WITH_FEASIBILITY = [
    ("bin-packing", "bin_solver.py"),
    ("budget-optimization", "budget_solver.py"),
    ("event-seating", "seating_solver.py"),
]


@pytest.mark.parametrize(
    "example_dir,solver_file",
    SOLVERS_WITH_FEASIBILITY,
    ids=[s[0] for s in SOLVERS_WITH_FEASIBILITY],
)
def test_solver_feasible_and_optimal(example_dir: str, solver_file: str):
    """Run the solver and assert solution.json reports feasible and optimal."""
    solver_path = EXAMPLES / example_dir / solver_file
    solution_path = solver_path.parent / "solution.json"

    result = subprocess.run(
        [sys.executable, str(solver_path)],
        cwd=str(solver_path.parent),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Solver failed: {result.stderr[-1000:]}"

    assert solution_path.exists(), f"No solution.json produced by {example_dir}"
    with open(solution_path) as f:
        solution = json.load(f)

    assert solution.get("is_feasible") is True, (
        f"{example_dir} solution is not feasible"
    )
    assert solution.get("is_optimal") is True, (
        f"{example_dir} solution is not optimal"
    )
