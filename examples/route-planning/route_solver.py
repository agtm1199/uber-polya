#!/usr/bin/env python3
"""Route Planning (TSP) solver using Held-Karp dynamic programming.

Finds the shortest Hamiltonian cycle through n cities (warehouse + delivery stops).
Complexity: O(n^2 * 2^n) time, O(n * 2^n) space.
Correctness: Exact optimal, verified independently.
"""
from __future__ import annotations

import time
import json
import itertools
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
    """Problem instance for TSP route planning."""
    locations: tuple[str, ...]
    dist_matrix: tuple[tuple[float, ...], ...]  # dist_matrix[i][j] = distance from i to j
    start: int  # index of the starting location (warehouse)

    @property
    def n(self) -> int:
        return len(self.locations)

    def dist(self, i: int, j: int) -> float:
        return self.dist_matrix[i][j]


@dataclass
class Solution:
    """Verified solution with metadata."""
    tour: list[int]             # ordered list of location indices (starts and ends at start)
    tour_names: list[str]       # ordered list of location names
    objective: float            # total tour distance
    is_optimal: bool
    is_feasible: bool
    algorithm: str
    time_seconds: float
    certificate: str
    heuristic_distance: float | None = None  # nearest-neighbor comparison
    constraint_check: dict[str, Any] = field(default_factory=dict)


# --- Solver: Held-Karp DP ---

def solve(instance: Instance) -> Solution:
    """Solve TSP exactly using Held-Karp dynamic programming."""
    t0 = time.perf_counter()

    n = instance.n
    start = instance.start
    dist = instance.dist

    # dp[S][i] = min distance to visit all cities in set S, ending at city i
    # S is a bitmask representing the set of visited cities
    INF = float("inf")

    # Initialize: dp[{start}][start] = 0
    dp = [[INF] * n for _ in range(1 << n)]
    parent = [[-1] * n for _ in range(1 << n)]

    dp[1 << start][start] = 0

    # Fill DP table
    for mask in range(1 << n):
        for u in range(n):
            if dp[mask][u] == INF:
                continue
            if not (mask & (1 << u)):
                continue
            for v in range(n):
                if mask & (1 << v):
                    continue  # already visited
                new_mask = mask | (1 << v)
                new_dist = dp[mask][u] + dist(u, v)
                if new_dist < dp[new_mask][v]:
                    dp[new_mask][v] = new_dist
                    parent[new_mask][v] = u

    # Find optimal last city before returning to start
    full_mask = (1 << n) - 1
    best_dist = INF
    best_last = -1
    for u in range(n):
        if u == start:
            continue
        total = dp[full_mask][u] + dist(u, start)
        if total < best_dist:
            best_dist = total
            best_last = u

    # Reconstruct tour
    tour = []
    mask = full_mask
    current = best_last
    while current != -1:
        tour.append(current)
        prev = parent[mask][current]
        mask = mask ^ (1 << current)
        current = prev
    tour.reverse()
    tour.append(start)  # return to start

    elapsed = time.perf_counter() - t0

    tour_names = [instance.locations[i] for i in tour]

    # Nearest-neighbor heuristic for comparison
    nn_dist = _nearest_neighbor(instance)

    sol = Solution(
        tour=tour,
        tour_names=tour_names,
        objective=best_dist,
        is_optimal=True,
        is_feasible=False,  # verified below
        algorithm=f"Held-Karp DP (exact, O(n^2 * 2^n), n={n})",
        time_seconds=elapsed,
        certificate="Exact algorithm: explores all 2^n subsets",
        heuristic_distance=nn_dist,
    )

    # Independent verification
    sol.is_feasible, sol.constraint_check = verify(instance, tour)

    return sol


def _nearest_neighbor(instance: Instance) -> float:
    """Nearest-neighbor heuristic for TSP (greedy baseline)."""
    n = instance.n
    start = instance.start
    visited = {start}
    current = start
    total_dist = 0.0

    for _ in range(n - 1):
        best_next = -1
        best_d = float("inf")
        for j in range(n):
            if j not in visited and instance.dist(current, j) < best_d:
                best_d = instance.dist(current, j)
                best_next = j
        visited.add(best_next)
        total_dist += best_d
        current = best_next

    total_dist += instance.dist(current, start)
    return total_dist


# --- Verification (independent of solver) ---

def verify(
    instance: Instance,
    tour: list[int],
) -> tuple[bool, dict[str, Any]]:
    """Independently verify solution feasibility."""
    checks: dict[str, Any] = {}
    all_ok = True

    n = instance.n
    start = instance.start

    # Check 1: Tour starts at the starting location
    ok = tour[0] == start
    checks["starts_at_warehouse"] = ok
    if not ok:
        all_ok = False

    # Check 2: Tour ends at the starting location
    ok = tour[-1] == start
    checks["returns_to_warehouse"] = ok
    if not ok:
        all_ok = False

    # Check 3: Tour visits every location exactly once (except start which appears twice)
    interior = tour[:-1]  # exclude the final return to start
    ok = set(interior) == set(range(n)) and len(interior) == n
    checks["visits_all_locations"] = ok
    if not ok:
        all_ok = False

    # Check 4: No repeated locations (except start)
    ok = len(set(interior)) == len(interior)
    checks["no_repeated_visits"] = ok
    if not ok:
        all_ok = False

    # Check 5: Recompute total distance
    total = 0.0
    for i in range(len(tour) - 1):
        total += instance.dist(tour[i], tour[i + 1])
    checks["distance_recomputed"] = round(total, 2)

    return all_ok, checks


# --- Main ---

if __name__ == "__main__":
    # Build instance: warehouse + 8 delivery stops
    # Distance matrix (symmetric, in km)
    locations = (
        "Warehouse",      # 0
        "Downtown",       # 1
        "Airport",        # 2
        "University",     # 3
        "Hospital",       # 4
        "Mall",           # 5
        "Stadium",        # 6
        "Park",           # 7
        "Industrial Zone", # 8
    )

    # Realistic asymmetric-ish distance matrix (km)
    # Made symmetric for simplicity
    D = [
        #  WH   DT   AP   UN   HO   MA   ST   PK   IZ
        [  0,  12,  29,  22,  13,  21,  25,   9,  15],  # Warehouse
        [ 12,   0,  18,  14,   8,  10,  19,  15,  20],  # Downtown
        [ 29,  18,   0,  24,  26,  22,  30,  28,  17],  # Airport
        [ 22,  14,  24,   0,  11,  16,  12,  20,  27],  # University
        [ 13,   8,  26,  11,   0,  14,  17,  10,  23],  # Hospital
        [ 21,  10,  22,  16,  14,   0,  15,  18,  19],  # Mall
        [ 25,  19,  30,  12,  17,  15,   0,  22,  26],  # Stadium
        [  9,  15,  28,  20,  10,  18,  22,   0,  16],  # Park
        [ 15,  20,  17,  27,  23,  19,  26,  16,   0],  # Industrial Zone
    ]

    dist_matrix = tuple(tuple(row) for row in D)

    instance = Instance(
        locations=locations,
        dist_matrix=dist_matrix,
        start=0,
    )

    sol = solve(instance)

    # --- Print Solution Report ---
    log.header("SOLUTION REPORT: Route Planning (TSP)")
    log.metric("Status:", "Optimal" if sol.is_optimal else "Sub-optimal", tag="RESULT")
    log.metric("Feasible:", str(sol.is_feasible), tag="RESULT")
    log.metric("Tour distance:", f"{sol.objective:.1f} km", tag="RESULT")
    log.metric("Locations:", f"{instance.n}", tag="RESULT")
    log.metric("Algorithm:", sol.algorithm, tag="SOLVE")
    log.metric("Time:", f"{sol.time_seconds:.4f}s", tag="TIMING")
    log.blank()

    # Optimal tour
    log.step("OPTIMAL TOUR")
    total_check = 0.0
    for i in range(len(sol.tour) - 1):
        u, v = sol.tour[i], sol.tour[i + 1]
        d = instance.dist(u, v)
        total_check += d
        log.table_row(
            f"  {i+1:>2}. {instance.locations[u]:<20} -> {instance.locations[v]:<20} {d:>6.1f} km",
            tag="TABLE"
        )
    log.table_row(f"     {'TOTAL':>20}    {'':20} {total_check:>6.1f} km", tag="RESULT")
    log.blank()

    # Tour as simple list
    log.step("TOUR SEQUENCE")
    tour_str = " -> ".join(sol.tour_names)
    log.info(tour_str, tag="DATA")
    log.blank()

    # Comparison with nearest-neighbor heuristic
    log.step("HEURISTIC COMPARISON")
    log.metric("Held-Karp (optimal):", f"{sol.objective:.1f} km", tag="OPTIMIZE")
    log.metric("Nearest-neighbor:", f"{sol.heuristic_distance:.1f} km", tag="OPTIMIZE")
    gap = (sol.heuristic_distance - sol.objective) / sol.objective * 100
    log.metric("NN suboptimality:", f"{gap:.1f}%", tag="OPTIMIZE")
    log.blank()

    # Distance matrix summary
    log.step("DISTANCE MATRIX")
    header = f"{'':>15}"
    for loc in locations:
        header += f" {loc[:4]:>5}"
    log.table_row(header, tag="TABLE")
    log.divider()

    for i, loc_i in enumerate(locations):
        row = f"{loc_i:>15}"
        for j, loc_j in enumerate(locations):
            row += f" {D[i][j]:>5}"
        log.table_row(row, tag="TABLE")
    log.blank()

    # Leg distance distribution
    log.step("LEG DISTANCE ANALYSIS")
    leg_distances = []
    for i in range(len(sol.tour) - 1):
        leg_distances.append(instance.dist(sol.tour[i], sol.tour[i + 1]))

    log.metric("Shortest leg:", f"{min(leg_distances):.1f} km", tag="STATS")
    log.metric("Longest leg:", f"{max(leg_distances):.1f} km", tag="STATS")
    log.metric("Average leg:", f"{np.mean(leg_distances):.1f} km", tag="STATS")
    log.metric("Std dev:", f"{np.std(leg_distances):.1f} km", tag="STATS")
    log.blank()

    # Independent verification
    log.step("INDEPENDENT VERIFICATION")
    for check_name, result in sol.constraint_check.items():
        if isinstance(result, bool):
            log.check(check_name, result, tag="VERIFY")
        else:
            log.check(check_name, result, tag="VERIFY")
    log.blank()

    # Brute-force cross-check for confidence (only if n is small enough)
    if instance.n <= 10:
        log.step("BRUTE-FORCE CROSS-CHECK")
        t0_bf = time.perf_counter()
        cities = [i for i in range(instance.n) if i != instance.start]
        best_bf = float("inf")
        best_perm = None
        count = 0
        for perm in itertools.permutations(cities):
            dist_total = instance.dist(instance.start, perm[0])
            for i in range(len(perm) - 1):
                dist_total += instance.dist(perm[i], perm[i + 1])
            dist_total += instance.dist(perm[-1], instance.start)
            count += 1
            if dist_total < best_bf:
                best_bf = dist_total
                best_perm = perm
        elapsed_bf = time.perf_counter() - t0_bf

        log.metric("Brute-force distance:", f"{best_bf:.1f} km", tag="VERIFY")
        log.metric("Held-Karp distance:", f"{sol.objective:.1f} km", tag="VERIFY")
        log.check("brute_force_matches_dp", abs(best_bf - sol.objective) < 0.01)
        log.metric("Permutations checked:", f"{count:,}", tag="STATS")
        log.metric("Brute-force time:", f"{elapsed_bf:.4f}s", tag="TIMING")
        log.blank()

    # Save solution
    output = {
        "tour": sol.tour,
        "tour_names": sol.tour_names,
        "objective": sol.objective,
        "heuristic_distance": sol.heuristic_distance,
        "is_optimal": sol.is_optimal,
        "is_feasible": sol.is_feasible,
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
    }
    with open(Path(__file__).parent / "solution.json", "w") as f:
        json.dump(output, f, indent=2)
    log.success("solution.json", tag="SAVE")
    log.divider(style="thick")
