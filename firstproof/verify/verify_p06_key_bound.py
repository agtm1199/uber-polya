#!/usr/bin/env python3
"""
Targeted verification of the KEY BOUND for Problem 6:

    ||sum_{e in E(S,S)} A_e|| <= max_{e in E(S,S)} ell_e

where A_e = L^{+/2} L_e L^{+/2} are the normalized edge matrices,
ell_e = tr(A_e) = R_eff(e) is the leverage score,
and the frame property sum_e A_e = Pi (projection onto range of L).

The bound follows from:
  y^T M y = sum_e ell_e (y^T a_hat_e)^2
          <= (max ell_e) * sum_{e in E(S,S)} (y^T a_hat_e)^2
          <= (max ell_e) * sum_{e in E} (y^T a_hat_e)^2
          = (max ell_e) * y^T Pi y
          = max ell_e     (for unit y in range(Pi))
"""
from __future__ import annotations

import numpy as np
from itertools import combinations
import time

np.random.seed(42)


def laplacian(adj: np.ndarray) -> np.ndarray:
    return np.diag(adj.sum(axis=1)) - adj


def compute_normalized_edge_matrices(adj: np.ndarray):
    """Compute A_e = L^{+/2} L_e L^{+/2} for all edges, and leverage scores."""
    n = adj.shape[0]
    L = laplacian(adj)
    eigenvalues, eigenvectors = np.linalg.eigh(L)

    # Compute L^{+/2}
    Lphalf = np.zeros((n, n))
    for i in range(n):
        if eigenvalues[i] > 1e-10:
            Lphalf += (1.0 / np.sqrt(eigenvalues[i])) * np.outer(eigenvectors[:, i], eigenvectors[:, i])

    # Pi = projection onto range of L
    Pi = np.zeros((n, n))
    for i in range(n):
        if eigenvalues[i] > 1e-10:
            Pi += np.outer(eigenvectors[:, i], eigenvectors[:, i])

    edges = []
    A_edges = []
    ell_edges = []

    for i in range(n):
        for j in range(i + 1, n):
            if adj[i, j] > 0:
                edges.append((i, j))
                # L_e = (e_i - e_j)(e_i - e_j)^T
                diff = np.zeros(n)
                diff[i] = 1.0
                diff[j] = -1.0
                L_e = np.outer(diff, diff)
                A_e = Lphalf @ L_e @ Lphalf
                A_edges.append(A_e)
                ell_edges.append(np.trace(A_e))

    return edges, A_edges, ell_edges, Pi


def test_key_bound(adj: np.ndarray, name: str):
    """Test: ||sum_{e in E(S,S)} A_e|| <= max_{e in E(S,S)} ell_e for various S."""
    n = adj.shape[0]
    edges, A_edges, ell_edges, Pi = compute_normalized_edge_matrices(adj)
    m = len(edges)

    # Verify frame property: sum A_e = Pi
    A_sum = sum(A_edges)
    frame_err = np.linalg.norm(A_sum - Pi, ord='fro')
    print(f"  {name}: n={n}, m={m}, frame error = {frame_err:.2e}")

    # Verify sum ell_e = n-1
    total_ell = sum(ell_edges)
    print(f"    sum ell_e = {total_ell:.6f}, n-1 = {n-1}")

    # Test the key bound for random subsets
    violations = 0
    total_tests = 0
    max_ratio = 0.0

    for trial in range(2000):
        # Random subset
        if n <= 12:
            s = np.random.randint(2, n)
        else:
            s = np.random.randint(2, min(n, 10))
        S = set(np.random.choice(n, s, replace=False))

        # Find edges in E(S,S)
        M = np.zeros((n, n))
        max_ell_S = 0.0
        edge_count = 0
        for idx, (u, v) in enumerate(edges):
            if u in S and v in S:
                M += A_edges[idx]
                max_ell_S = max(max_ell_S, ell_edges[idx])
                edge_count += 1

        if edge_count == 0:
            continue

        spectral_norm = np.linalg.eigvalsh(M)[-1]  # max eigenvalue (M is PSD)
        total_tests += 1

        if spectral_norm > max_ell_S + 1e-10:
            violations += 1
            ratio = spectral_norm / max_ell_S
            max_ratio = max(max_ratio, ratio)
            if violations <= 5:
                print(f"    VIOLATION: |S|={s}, edges={edge_count}, "
                      f"||M|| = {spectral_norm:.6f}, max_ell = {max_ell_S:.6f}, "
                      f"ratio = {ratio:.4f}")
        else:
            ratio = spectral_norm / max_ell_S if max_ell_S > 0 else 0
            max_ratio = max(max_ratio, ratio)

    if violations == 0:
        print(f"    KEY BOUND HOLDS: {total_tests} tests, max ratio ||M||/max_ell = {max_ratio:.6f}")
    else:
        print(f"    VIOLATIONS: {violations}/{total_tests}, max ratio = {max_ratio:.6f}")

    return violations == 0


def test_independent_set_construction(adj: np.ndarray, epsilon: float, name: str):
    """Test the full independent-set construction for epsilon-lightness."""
    n = adj.shape[0]
    edges, A_edges, ell_edges, Pi = compute_normalized_edge_matrices(adj)

    # Find heavy edges (ell_e > epsilon)
    heavy_edges = [(u, v) for (u, v), ell in zip(edges, ell_edges) if ell > epsilon]

    # Build heavy-edge adjacency
    heavy_adj = np.zeros((n, n))
    for u, v in heavy_edges:
        heavy_adj[u, v] = 1
        heavy_adj[v, u] = 1

    # Greedy independent set (sorted by degree in heavy graph, ascending)
    degrees_H = heavy_adj.sum(axis=1).astype(int)
    order = np.argsort(degrees_H)
    I = set()
    for v in order:
        # Check if v has any neighbor in I (in the heavy-edge graph)
        has_neighbor = any(heavy_adj[v, w] > 0 for w in I)
        if not has_neighbor:
            I.add(v)

    S = list(I)

    # Check epsilon-lightness
    L = laplacian(adj)
    L_S_adj = np.zeros((n, n))
    for i in S:
        for j in S:
            L_S_adj[i, j] = adj[i, j]
    L_S = laplacian(L_S_adj)
    M = epsilon * L - L_S
    min_eig = np.linalg.eigvalsh(M)[0]
    is_psd = min_eig >= -1e-10

    c_eff = (len(S) / n) / epsilon if epsilon > 0 else 0

    # Also check via the key bound: all edges in E(S,S) should be light
    max_ell_in_S = 0.0
    for (u, v), ell in zip(edges, ell_edges):
        if u in set(S) and v in set(S):
            max_ell_in_S = max(max_ell_in_S, ell)

    print(f"  {name}, eps={epsilon}: |S|={len(S)}, c_eff={c_eff:.4f}, "
          f"PSD={is_psd}, min_eig={min_eig:.6f}, "
          f"max_ell_in_S={max_ell_in_S:.6f} (<= eps={epsilon}? "
          f"{'YES' if max_ell_in_S <= epsilon + 1e-10 else 'NO'})")

    return is_psd, c_eff


def generate_complete(n):
    return np.ones((n, n)) - np.eye(n), f"K_{n}"

def generate_cycle(n):
    adj = np.zeros((n, n))
    for i in range(n):
        adj[i, (i+1) % n] = 1
        adj[(i+1) % n, i] = 1
    return adj, f"C_{n}"

def generate_star(n):
    adj = np.zeros((n, n))
    for i in range(1, n):
        adj[0, i] = 1
        adj[i, 0] = 1
    return adj, f"Star_{n}"

def generate_regular(n, d):
    adj = np.zeros((n, n))
    for i in range(n):
        for k in range(1, d // 2 + 1):
            j = (i + k) % n
            adj[i, j] = 1
            adj[j, i] = 1
    return adj, f"Reg({n},{d})"

def generate_path(n):
    adj = np.zeros((n, n))
    for i in range(n - 1):
        adj[i, i+1] = 1
        adj[i+1, i] = 1
    return adj, f"P_{n}"


def main():
    t_start = time.perf_counter()
    print("=" * 80)
    print("PROBLEM 6: KEY BOUND VERIFICATION")
    print("||sum_{E(S,S)} A_e|| <= max_{E(S,S)} ell_e")
    print("=" * 80)
    print()

    # Part 1: Test the key bound
    print("PART 1: KEY BOUND ||M|| <= max_ell")
    print("-" * 60)

    graphs = [
        generate_complete(6),
        generate_complete(10),
        generate_complete(15),
        generate_cycle(8),
        generate_cycle(12),
        generate_cycle(20),
        generate_star(8),
        generate_star(12),
        generate_path(10),
        generate_path(15),
        generate_regular(10, 4),
        generate_regular(12, 6),
    ]

    all_passed = True
    for adj, name in graphs:
        passed = test_key_bound(adj, name)
        if not passed:
            all_passed = False

    print(f"\nAll key bound tests passed: {all_passed}")

    # Part 2: Test the full independent-set construction
    print()
    print("PART 2: INDEPENDENT SET CONSTRUCTION")
    print("-" * 60)

    all_psd = True
    min_c = float('inf')

    for adj, name in graphs:
        for eps in [0.1, 0.2, 0.3, 0.5]:
            is_psd, c_eff = test_independent_set_construction(adj, eps, name)
            if not is_psd:
                all_psd = False
            if c_eff > 0:
                min_c = min(min_c, c_eff)

    print(f"\nAll PSD checks passed: {all_psd}")
    print(f"Minimum c_eff: {min_c:.6f}")
    print(f"Target c = 1/3 = {1/3:.6f}")
    print(f"c_eff >= 1/3: {min_c >= 1/3 - 1e-10}")

    # Part 3: Detailed analysis for edge cases
    print()
    print("PART 3: EDGE CASE ANALYSIS")
    print("-" * 60)

    # For a star graph, the center has high leverage load
    adj, name = generate_star(10)
    edges, A_edges, ell_edges, Pi = compute_normalized_edge_matrices(adj)
    print(f"  Star_10 leverage scores: {[f'{l:.4f}' for l in ell_edges[:5]]}...")
    print(f"  Max ell_e = {max(ell_edges):.6f}")
    loads = np.zeros(10)
    for (u, v), ell in zip(edges, ell_edges):
        loads[u] += ell
        loads[v] += ell
    print(f"  Vertex loads: {np.round(loads, 4)}")

    # For a path, edges near the ends have high leverage
    adj, name = generate_path(10)
    edges, A_edges, ell_edges, Pi = compute_normalized_edge_matrices(adj)
    print(f"\n  P_10 leverage scores: {[f'{l:.4f}' for l in ell_edges]}")
    print(f"  Max ell_e = {max(ell_edges):.6f}")

    elapsed = time.perf_counter() - t_start
    print(f"\nTotal time: {elapsed:.2f}s")
    print("=" * 80)


if __name__ == "__main__":
    main()
