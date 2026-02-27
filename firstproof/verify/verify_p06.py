#!/usr/bin/env python3
"""
Verification script for Problem 6: Large epsilon-light vertex subsets.

Proof strategy: sparse-dense dichotomy.
  Case 1 (sparse): alpha(G) >= eps*n/8. Use independent set.
  Case 2 (dense): alpha(G) < eps*n/8. Use greedy spectral construction.

We verify:
1. Effective resistance properties (total leverage, vertex loads)
2. Independent sets are trivially eps-light
3. The combined approach (IS + greedy) achieves c = 1/8 universally
4. Quadratic form inequality for eps-light sets
"""
from __future__ import annotations

import numpy as np
from dataclasses import dataclass
import time

np.random.seed(2026)


@dataclass(frozen=True)
class GraphInstance:
    """An undirected graph represented by adjacency matrix."""
    n: int
    adj: np.ndarray
    name: str


@dataclass
class VerificationResult:
    graph_name: str
    n: int
    epsilon: float
    subset_size: int
    c_eff: float
    is_psd: bool
    min_eigenvalue: float
    method: str


def laplacian(adj: np.ndarray) -> np.ndarray:
    """Compute the Laplacian matrix L = D - A."""
    D = np.diag(adj.sum(axis=1))
    return D - adj


def check_epsilon_light(adj: np.ndarray, S: list[int], epsilon: float) -> tuple[bool, float]:
    """Check if S is epsilon-light: epsilon*L - L_S >= 0 (PSD)."""
    n = adj.shape[0]
    L = laplacian(adj)
    S_set = set(S)
    adj_S = np.zeros((n, n))
    for i in S_set:
        for j in S_set:
            adj_S[i, j] = adj[i, j]
    L_S = laplacian(adj_S)
    M = epsilon * L - L_S
    eigenvalues = np.linalg.eigvalsh(M)
    min_eig = float(eigenvalues[0])
    is_psd = min_eig >= -1e-10
    return is_psd, min_eig


def compute_vertex_loads(adj: np.ndarray) -> np.ndarray:
    """Compute vertex loads ell(v) = sum_{e incident to v} R_eff(e)."""
    n = adj.shape[0]
    L = laplacian(adj)
    eigenvalues, eigenvectors = np.linalg.eigh(L)
    Lplus = np.zeros((n, n))
    for i in range(n):
        if eigenvalues[i] > 1e-10:
            Lplus += (1.0 / eigenvalues[i]) * np.outer(eigenvectors[:, i], eigenvectors[:, i])
    loads = np.zeros(n)
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i, j] > 0:
                diff = np.zeros(n)
                diff[i] = 1.0
                diff[j] = -1.0
                r_eff = diff @ Lplus @ diff
                loads[i] += r_eff
                loads[j] += r_eff
    return loads


def find_independent_set(adj: np.ndarray) -> list[int]:
    """Find a greedy independent set (by degree ascending)."""
    n = adj.shape[0]
    degrees = adj.sum(axis=1)
    order = np.argsort(degrees)
    I = set()
    for v in order:
        if not any(adj[v, w] > 0 for w in I):
            I.add(int(v))
    return sorted(I)


def greedy_eps_light(adj: np.ndarray, epsilon: float, order: list[int] = None) -> list[int]:
    """Greedy spectral construction: add vertices checking PSD condition."""
    n = adj.shape[0]
    if order is None:
        order = list(range(n))
    S = []
    for v in order:
        S_trial = S + [int(v)]
        ok, _ = check_epsilon_light(adj, S_trial, epsilon)
        if ok:
            S = S_trial
    return S


def find_eps_light_combined(adj: np.ndarray, epsilon: float) -> tuple[list[int], str]:
    """Combined approach: max of IS and greedy."""
    n = adj.shape[0]

    # Method 1: Independent set
    I = find_independent_set(adj)

    # Method 2: Greedy with multiple random orderings
    best_greedy = []
    for trial in range(5):
        order = list(np.random.permutation(n))
        S = greedy_eps_light(adj, epsilon, order)
        if len(S) > len(best_greedy):
            best_greedy = S

    # Method 3: Greedy from load-sorted order
    loads = compute_vertex_loads(adj)
    load_order = list(np.argsort(loads))
    S_load = greedy_eps_light(adj, epsilon, load_order)
    if len(S_load) > len(best_greedy):
        best_greedy = S_load

    if len(I) >= len(best_greedy):
        return I, "independent_set"
    else:
        return best_greedy, "greedy"


# ---- Graph generators ----

def generate_complete(n: int) -> GraphInstance:
    adj = np.ones((n, n)) - np.eye(n)
    return GraphInstance(n=n, adj=adj, name=f"K_{n}")

def generate_cycle(n: int) -> GraphInstance:
    adj = np.zeros((n, n))
    for i in range(n):
        adj[i, (i + 1) % n] = 1
        adj[(i + 1) % n, i] = 1
    return GraphInstance(n=n, adj=adj, name=f"C_{n}")

def generate_star(n: int) -> GraphInstance:
    adj = np.zeros((n, n))
    for i in range(1, n):
        adj[0, i] = 1
        adj[i, 0] = 1
    return GraphInstance(n=n, adj=adj, name=f"Star_{n}")

def generate_path(n: int) -> GraphInstance:
    adj = np.zeros((n, n))
    for i in range(n - 1):
        adj[i, i + 1] = 1
        adj[i + 1, i] = 1
    return GraphInstance(n=n, adj=adj, name=f"P_{n}")

def generate_regular(n: int, d: int) -> GraphInstance:
    adj = np.zeros((n, n))
    for i in range(n):
        for k in range(1, d // 2 + 1):
            j = (i + k) % n
            adj[i, j] = 1
            adj[j, i] = 1
    return GraphInstance(n=n, adj=adj, name=f"Reg({n},{d})")

def generate_erdos_renyi(n: int, p: float, name: str = "") -> GraphInstance:
    adj = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            if np.random.random() < p:
                adj[i, j] = 1
                adj[j, i] = 1
    return GraphInstance(n=n, adj=adj, name=name or f"ER({n},{p:.1f})")

def generate_bipartite(n1: int, n2: int) -> GraphInstance:
    n = n1 + n2
    adj = np.zeros((n, n))
    for i in range(n1):
        for j in range(n1, n):
            adj[i, j] = 1
            adj[j, i] = 1
    return GraphInstance(n=n, adj=adj, name=f"K_{n1},{n2}")


def main() -> None:
    t_start = time.perf_counter()
    print("=" * 80)
    print("PROBLEM 6 VERIFICATION: Large epsilon-light vertex subsets")
    print("Proof strategy: sparse-dense dichotomy with IS + greedy")
    print("=" * 80)
    print()

    # ---- PART 1: Verify effective resistance properties ----
    print("PART 1: EFFECTIVE RESISTANCE PROPERTIES")
    print("-" * 60)

    for G in [generate_complete(6), generate_cycle(8), generate_star(6)]:
        loads = compute_vertex_loads(G.adj)
        total = loads.sum()
        print(f"  {G.name}: total vertex load = {total:.4f}, "
              f"expected 2(n-1) = {2*(G.n - 1)}, "
              f"match = {abs(total - 2*(G.n - 1)) < 0.01}")
        print(f"    avg load = {total/G.n:.4f}, loads = {np.round(loads, 3)}")

    print()

    # ---- PART 2: Test on various graph families ----
    print("PART 2: EPSILON-LIGHT SUBSET CONSTRUCTION")
    print("-" * 80)

    graphs = [
        generate_complete(8),
        generate_complete(12),
        generate_complete(20),
        generate_cycle(10),
        generate_cycle(15),
        generate_cycle(20),
        generate_star(8),
        generate_star(12),
        generate_path(10),
        generate_path(15),
        generate_regular(10, 4),
        generate_regular(15, 4),
        generate_regular(15, 6),
        generate_erdos_renyi(12, 0.3, "ER(12,0.3)"),
        generate_erdos_renyi(12, 0.5, "ER(12,0.5)"),
        generate_erdos_renyi(15, 0.3, "ER(15,0.3)"),
        generate_bipartite(5, 5),
        generate_bipartite(6, 8),
    ]

    epsilons = [0.1, 0.2, 0.3, 0.5]

    results: list[VerificationResult] = []

    print(f"{'Graph':<14} {'eps':>5} {'|S|':>5} {'|V|':>5} "
          f"{'c_eff':>8} {'PSD':>4} {'Method':<15}")
    print("-" * 80)

    for G in graphs:
        for eps in epsilons:
            S, method = find_eps_light_combined(G.adj, eps)

            if S:
                is_psd, min_eig = check_epsilon_light(G.adj, S, eps)
                c_eff = (len(S) / G.n) / eps
            else:
                is_psd, min_eig = True, 0.0
                c_eff = 0.0

            print(f"{G.name:<14} {eps:>5.1f} {len(S):>5d} {G.n:>5d} "
                  f"{c_eff:>8.4f} {'Y' if is_psd else 'N':>4} {method:<15}")

            results.append(VerificationResult(
                graph_name=G.name,
                n=G.n,
                epsilon=eps,
                subset_size=len(S),
                c_eff=c_eff,
                is_psd=is_psd,
                min_eigenvalue=min_eig,
                method=method,
            ))

    # ---- PART 3: Summary statistics ----
    print()
    print("PART 3: SUMMARY")
    print("-" * 60)

    valid = [r for r in results if r.subset_size > 0]
    if valid:
        min_c = min(r.c_eff for r in valid)
        all_psd = all(r.is_psd for r in valid)
        target_c = 1 / 8
        all_above_target = all(r.c_eff >= target_c - 1e-10 for r in valid)
        print(f"  Total test cases: {len(results)}")
        print(f"  Non-empty subsets found: {len(valid)}")
        print(f"  All PSD conditions verified: {all_psd}")
        print(f"  Minimum c_eff achieved: {min_c:.6f}")
        print(f"  Target c = 1/8 = {target_c:.6f}")
        print(f"  c_eff >= 1/8 in all cases: {all_above_target}")
        print()

        # Break down by graph family
        families = {}
        for r in valid:
            family = r.graph_name.split("_")[0].split("(")[0]
            if family not in families:
                families[family] = []
            families[family].append(r.c_eff)

        print("  By graph family:")
        for fam, cs in sorted(families.items()):
            print(f"    {fam:<12}: min c_eff = {min(cs):.4f}, "
                  f"avg c_eff = {sum(cs)/len(cs):.4f}, "
                  f"count = {len(cs)}")
    else:
        print("  WARNING: No valid subsets found!")

    # ---- PART 4: Verify the edge-energy interpretation ----
    print()
    print("PART 4: EDGE ENERGY VERIFICATION")
    print("-" * 60)
    print("  Verifying: for epsilon-light S, x^T L_S x <= eps * x^T L x for all x")
    print()

    for G in [generate_complete(8), generate_cycle(10), generate_regular(10, 4)]:
        eps = 0.3
        S, _ = find_eps_light_combined(G.adj, eps)
        if not S:
            continue
        L = laplacian(G.adj)
        S_set = set(S)
        adj_S = np.zeros((G.n, G.n))
        for i in S_set:
            for j in S_set:
                adj_S[i, j] = G.adj[i, j]
        L_S = laplacian(adj_S)

        # Test on random vectors
        passed = True
        max_ratio = 0.0
        for _ in range(1000):
            x = np.random.randn(G.n)
            x -= x.mean()  # Project out constant
            energy_full = x @ L @ x
            energy_S = x @ L_S @ x
            if energy_full > 1e-12:
                ratio = energy_S / energy_full
                max_ratio = max(max_ratio, ratio)
                if ratio > eps + 1e-10:
                    passed = False

        print(f"  {G.name}: |S| = {len(S)}, eps = {eps}, "
              f"max ratio = {max_ratio:.6f}, "
              f"passed = {passed}")

    elapsed = time.perf_counter() - t_start
    print()
    print("=" * 80)
    print(f"VERIFICATION COMPLETE. Time: {elapsed:.2f}s")
    print("=" * 80)


if __name__ == "__main__":
    main()
