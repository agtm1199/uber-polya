#!/usr/bin/env python3
"""Traffic Flow Analysis solver using linear algebra.

Models a 4-intersection one-way street network as a linear system Ax = b
derived from conservation of flow (flow in = flow out at every node),
plus one traffic sensor reading.  The system has 5 equations and 5 unknowns
but rank 4, so it is underdetermined with nullity 1.  We compute the
minimum-norm particular solution via numpy.linalg.lstsq and characterize
the full solution family through null space analysis.

Complexity: O(m * n^2) for lstsq on an m x n system -- trivial here.
Correctness: Verified independently by re-checking conservation at each node.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger
log = PolyaLogger()


# --- Data Model ---

@dataclass(frozen=True)
class Instance:
    """Traffic flow network instance.

    Attributes:
        node_names: labels for each intersection
        internal_labels: labels for each unknown internal road flow
        A: coefficient matrix (m x n) from flow conservation equations
        b: right-hand-side vector (m,) of known external flows
        descriptions: human-readable description of each equation
    """
    node_names: tuple[str, ...]
    internal_labels: tuple[str, ...]
    A: np.ndarray          # (m, n) conservation coefficient matrix
    b: np.ndarray          # (m,) known external net flows
    descriptions: tuple[str, ...]  # one per equation

    @property
    def m(self) -> int:
        """Number of equations (nodes)."""
        return self.A.shape[0]

    @property
    def n(self) -> int:
        """Number of unknowns (internal road segments)."""
        return self.A.shape[1]


@dataclass
class Solution:
    """Verified solution with metadata."""
    x_particular: np.ndarray       # minimum-norm particular solution
    null_basis: np.ndarray         # (n, nullity) null space basis columns
    rank: int
    nullity: int
    is_feasible: bool
    algorithm: str
    time_seconds: float
    residual: float                # ||Ax - b||
    constraint_check: dict[str, bool] = field(default_factory=dict)


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Solve the traffic flow conservation system Ax = b.

    Uses numpy.linalg.lstsq which returns the minimum-norm solution
    when the system is underdetermined (rank < n).  Also computes
    the null space via SVD to characterize the full solution family.
    """
    t0 = time.perf_counter()

    A = instance.A
    b = instance.b
    m, n = A.shape

    # --- Rank analysis via SVD ---
    U, sigma, Vt = np.linalg.svd(A, full_matrices=True)
    tol = max(m, n) * np.max(sigma) * np.finfo(float).eps
    rank = int(np.sum(sigma > tol))
    nullity = n - rank

    # --- Null space basis (columns of V corresponding to zero singular values) ---
    null_basis = Vt[rank:].T  # shape (n, nullity)

    # --- Minimum-norm particular solution ---
    x_particular, residuals, rank_lstsq, sv = np.linalg.lstsq(A, b, rcond=None)

    # Compute residual norm
    residual = float(np.linalg.norm(A @ x_particular - b))

    elapsed = time.perf_counter() - t0

    sol = Solution(
        x_particular=x_particular,
        null_basis=null_basis,
        rank=rank,
        nullity=nullity,
        is_feasible=False,  # verified below
        algorithm="numpy.linalg.lstsq (SVD-based minimum-norm)",
        time_seconds=elapsed,
        residual=residual,
    )

    # Independent verification
    sol.is_feasible, sol.constraint_check = verify(instance, x_particular)

    return sol


# --- Verification (independent of solver) ---

def verify(
    instance: Instance,
    x: np.ndarray,
    tol: float = 1e-8,
) -> tuple[bool, dict[str, bool]]:
    """Independently verify that flow conservation holds at every node.

    Recomputes Ax and checks each row against b.  Does NOT share any
    logic with the solver.
    """
    checks: dict[str, bool] = {}
    all_ok = True

    Ax = instance.A @ x

    for i, desc in enumerate(instance.descriptions):
        residual_i = abs(Ax[i] - instance.b[i])
        ok = residual_i < tol
        checks[f"node_{instance.node_names[i]}_conservation ({desc})"] = ok
        if not ok:
            all_ok = False

    # Global residual check
    global_residual = float(np.linalg.norm(Ax - instance.b))
    checks["global_residual_norm < tol"] = global_residual < tol
    if global_residual >= tol:
        all_ok = False

    # Check that x values are non-negative (physical: traffic flows >= 0)
    all_nonneg = bool(np.all(x >= -tol))
    checks["all_flows_nonneg"] = all_nonneg
    if not all_nonneg:
        # Not a hard failure for the linear system, but physically meaningful
        pass

    return all_ok, checks


# --- Problem Setup ---

def build_instance() -> Instance:
    """Build the 4-intersection traffic flow instance.

    Network topology::

              500 (in)
                |
                v
          +---- A ----+
          |   / |      |
      x4  ^  /  | x1   |
          | x5  v      |
          |  \\  B ---> 600 (out)
          |   \\ |
          |    \\| x2
          |     v
      300 --> C
          |     |
          |     | x3
          |     v
     200 <--- D

    Internal flows:
        x1: A -> B,  x2: B -> C,  x3: C -> D,  x4: D -> A,  x5: A -> C

    External flows (balanced: 800 in = 800 out):
        A: 500 cars/hr in from north
        B: 600 cars/hr out to east
        C: 300 cars/hr in from south
        D: 200 cars/hr out to west

    Conservation equations (flow in = flow out at each node):
        A: 500 + x4 = x1 + x5   =>  x1 - x4 + x5 = 500    ... (1)
        B: x1 = x2 + 600        =>  x1 - x2 = 600          ... (2)
        C: x2 + x5 + 300 = x3   => -x2 + x3 - x5 = 300    ... (3)
        D: x3 = x4 + 200        =>  x3 - x4 = 200          ... (4)

    For a connected 4-node graph, the incidence matrix has rank = nodes - 1 = 3,
    so only 3 of the 4 conservation equations are independent (nullity = 2).

    To reduce the degrees of freedom to 1, we add a traffic sensor reading:
        x2 = 200 (traffic counter on B -> C road)            ... (5)

    Final system: 5 equations, 5 unknowns, rank 4, nullity 1.
    """
    # Columns: x1, x2, x3, x4, x5
    A = np.array([
        [ 1,  0,  0, -1,  1],   # Eq 1: node A conservation
        [ 1, -1,  0,  0,  0],   # Eq 2: node B conservation
        [ 0, -1,  1,  0, -1],   # Eq 3: node C conservation
        [ 0,  0,  1, -1,  0],   # Eq 4: node D conservation
        [ 0,  1,  0,  0,  0],   # Eq 5: sensor on B->C road
    ], dtype=float)

    b = np.array([500.0, 600.0, 300.0, 200.0, 200.0])

    return Instance(
        node_names=("A", "B", "C", "D", "sensor_BC"),
        internal_labels=("x1: A->B", "x2: B->C", "x3: C->D",
                         "x4: D->A", "x5: A->C"),
        A=A,
        b=b,
        descriptions=(
            "node A: 500 + x4 = x1 + x5",
            "node B: x1 = x2 + 600",
            "node C: x2 + x5 + 300 = x3",
            "node D: x3 = x4 + 200",
            "sensor: x2 = 200",
        ),
    )


# --- Main ---

if __name__ == "__main__":
    instance = build_instance()
    sol = solve(instance)

    # --- Print Solution Report ---
    log.header("SOLUTION REPORT: Traffic Flow Analysis")

    # Problem summary
    log.step("PROBLEM SETUP")
    log.info("4 intersections (A, B, C, D) with 5 internal road segments", tag="DATA")
    log.info("External flows: 500 in (A), 600 out (B), 300 in (C), 200 out (D)", tag="DATA")
    log.info("Sensor reading: x2 = 200 (traffic counter on B->C)", tag="DATA")
    log.info(f"System size: {instance.m} equations, {instance.n} unknowns", tag="DATA")
    log.blank()

    # Equations
    log.step("CONSERVATION EQUATIONS")
    for i, desc in enumerate(instance.descriptions):
        log.table_row(f"Eq {i+1}:  {desc}", tag="TABLE")
    log.blank()

    # Coefficient matrix
    log.step("COEFFICIENT MATRIX A AND RHS b")
    col_labels = "  ".join(f"{lbl.split(':')[0]:>4}" for lbl in instance.internal_labels)
    log.table_row(f"       {col_labels}    |  b", tag="TABLE")
    log.divider()
    for i in range(instance.m):
        row_str = "  ".join(f"{instance.A[i, j]:4.0f}" for j in range(instance.n))
        log.table_row(f"Eq {i+1}:  {row_str}    | {instance.b[i]:6.0f}", tag="TABLE")
    log.blank()

    # Rank analysis
    log.step("RANK ANALYSIS")
    log.metric("Rank of A:", str(sol.rank), tag="STATS")
    log.metric("Nullity:", str(sol.nullity), tag="STATS")
    log.metric("Equations:", str(instance.m), tag="STATS")
    log.metric("Unknowns:", str(instance.n), tag="STATS")

    if sol.nullity > 0:
        log.info(
            f"System is underdetermined: {sol.nullity} free parameter(s)",
            tag="STATS",
        )
        log.info("Infinite solutions exist; lstsq returns minimum-norm particular solution", tag="STATS")
    elif sol.nullity == 0:
        log.info("System has a unique solution", tag="STATS")
    log.blank()

    # Null space basis
    if sol.nullity > 0:
        log.step("NULL SPACE BASIS")
        log.info(
            f"Any vector of the form x_particular + t1*v1 + t2*v2 + ... is also a solution",
            tag="STATS",
        )
        for k in range(sol.nullity):
            vec = sol.null_basis[:, k]
            components = ", ".join(
                f"{lbl.split(':')[0]}={vec[j]:+.4f}"
                for j, lbl in enumerate(instance.internal_labels)
            )
            log.table_row(f"v{k+1} = [{components}]", tag="TABLE")
        log.blank()

    # Particular solution
    log.step("PARTICULAR SOLUTION (minimum-norm)")
    for j, lbl in enumerate(instance.internal_labels):
        log.metric(
            f"{lbl}:",
            f"{sol.x_particular[j]:.2f} cars/hr",
            tag="RESULT",
        )
    log.blank()

    # Solution metadata
    log.step("SOLVER METADATA")
    log.metric("Algorithm:", sol.algorithm, tag="SOLVE")
    log.metric("Time:", f"{sol.time_seconds:.6f}s", tag="TIMING")
    log.metric("Residual ||Ax-b||:", f"{sol.residual:.2e}", tag="RESULT")
    log.blank()

    # Independent verification
    log.step("INDEPENDENT VERIFICATION")
    for check_name, result in sol.constraint_check.items():
        log.check(check_name, result, tag="VERIFY")
    log.blank()

    # Physical interpretation
    log.step("INTERPRETATION")
    x = sol.x_particular
    labels = instance.internal_labels

    # Find busiest and quietest roads
    idx_max = int(np.argmax(x))
    idx_min = int(np.argmin(x))
    log.info(f"Busiest segment:  {labels[idx_max]} = {x[idx_max]:.0f} cars/hr", tag="RECOMMEND")
    log.info(f"Quietest segment: {labels[idx_min]} = {x[idx_min]:.0f} cars/hr", tag="RECOMMEND")

    if sol.nullity > 0:
        log.info(
            f"Note: {sol.nullity} degree(s) of freedom remain. "
            "Additional sensor readings would pin down a unique solution.",
            tag="RECOMMEND",
        )

    # Negative flow check
    neg_flows = [(labels[j], x[j]) for j in range(len(x)) if x[j] < -1e-8]
    if neg_flows:
        log.warning("Some flows are negative (may indicate wrong assumed direction):", tag="WARNING")
        for lbl, val in neg_flows:
            log.warning(f"  {lbl} = {val:.2f}", tag="WARNING")
    else:
        log.success("All flows are non-negative (physically consistent)", tag="VERIFY")

    log.blank()
    log.divider(style="thick")
