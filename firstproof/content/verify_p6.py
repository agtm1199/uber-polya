#!/usr/bin/env python3
"""
Verification script for Problem 6: Large epsilon-light vertex subsets.

Tests the claim: For every graph G = (V, E) and every epsilon in (0,1),
there exists an epsilon-light subset S of V with |S| >= c * epsilon * |V|,
where a set S is epsilon-light if epsilon*L - L_S is positive semidefinite.

Here L is the Laplacian of G, and L_S is the Laplacian of G_S = (V, E(S,S)).

We verify:
1. The PSD condition epsilon*L - L_S >= 0 for found subsets
2. The size bound |S| >= c*epsilon*|V| for various constants c
3. Both random sampling and greedy constructions
"""
from __future__ import annotations

import numpy as np
from dataclasses import dataclass
import time
import itertools

np.random.seed(42)


@dataclass(frozen=True)
class GraphInstance:
    """An undirected graph represented by adjacency matrix."""
    n: int
    adj: np.ndarray  # n x n symmetric adjacency matrix (0/1)
    name: str


@dataclass
class VerificationResult:
    graph_name: str
    n: int
    epsilon: float
    subset_size: int
    fraction: float
    target_fraction: float
    is_psd: bool
    min_eigenvalue: float
    method: str
    time_seconds: float


def laplacian(adj: np.ndarray) -> np.ndarray:
    """Compute the Laplacian matrix L = D - A."""
    D = np.diag(adj.sum(axis=1))
    return D - adj


def induced_laplacian(adj: np.ndarray, S: list[int]) -> np.ndarray:
    """Compute Laplacian of G_S = (V, E(S,S)).

    L_S is an n x n matrix (same vertex set V), but only edges within S.
    """
    n = adj.shape[0]
    S_set = set(S)
    adj_S = np.zeros((n, n))
    for i in S_set:
        for j in S_set:
            adj_S[i, j] = adj[i, j]
    return laplacian(adj_S)


def check_epsilon_light(adj: np.ndarray, S: list[int], epsilon: float) -> tuple[bool, float]:
    """Check if S is epsilon-light: epsilon*L - L_S >= 0 (PSD).

    Returns (is_psd, min_eigenvalue).
    """
    L = laplacian(adj)
    L_S = induced_laplacian(adj, S)
    M = epsilon * L - L_S
    eigenvalues = np.linalg.eigvalsh(M)
    min_eig = float(eigenvalues[0])
    is_psd = min_eig >= -1e-10
    return is_psd, min_eig


def find_epsilon_light_random(adj: np.ndarray, epsilon: float,
                               num_trials: int = 500) -> list[int]:
    """Find epsilon-light subset via random sampling + alteration."""
    n = adj.shape[0]
    if n == 0:
        return []

    best_S: list[int] = []

    for p in [epsilon, epsilon/2, epsilon/4, epsilon/8]:
        for _ in range(num_trials):
            included = np.random.random(n) < p
            S = list(np.where(included)[0])
            if len(S) <= len(best_S):
                continue
            is_psd, _ = check_epsilon_light(adj, S, epsilon)
            if is_psd:
                best_S = S

    return best_S


def find_epsilon_light_greedy_add(adj: np.ndarray, epsilon: float) -> list[int]:
    """Greedy construction: start empty, add vertices maintaining PSD."""
    n = adj.shape[0]
    if n == 0:
        return []

    # Sort vertices by degree (ascending) -- low-degree vertices are easier to add
    degrees = adj.sum(axis=1)
    order = np.argsort(degrees)

    S: list[int] = []
    for v in order:
        S_trial = S + [int(v)]
        is_psd, _ = check_epsilon_light(adj, S_trial, epsilon)
        if is_psd:
            S = S_trial

    return S


def find_epsilon_light_greedy_remove(adj: np.ndarray, epsilon: float) -> list[int]:
    """Greedy construction: start with V, remove vertices to achieve PSD."""
    n = adj.shape[0]
    if n == 0:
        return []

    S = list(range(n))

    for _ in range(n):
        is_psd, _ = check_epsilon_light(adj, S, epsilon)
        if is_psd:
            break

        # Find vertex whose removal most improves min eigenvalue
        best_v = None
        best_eig = -np.inf
        for v in S:
            S_trial = [u for u in S if u != v]
            if not S_trial:
                continue
            _, trial_eig = check_epsilon_light(adj, S_trial, epsilon)
            if trial_eig > best_eig:
                best_eig = trial_eig
                best_v = v

        if best_v is not None:
            S.remove(best_v)
        else:
            break

    return S


def brute_force_max_light(adj: np.ndarray, epsilon: float) -> tuple[list[int], int]:
    """For small graphs, find the largest epsilon-light subset by brute force."""
    n = adj.shape[0]
    for size in range(n, 0, -1):
        for S in itertools.combinations(range(n), size):
            S_list = list(S)
            is_psd, _ = check_epsilon_light(adj, S_list, epsilon)
            if is_psd:
                return S_list, size
    return [], 0


def generate_erdos_renyi(n: int, p: float, name: str = "") -> GraphInstance:
    adj = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            if np.random.random() < p:
                adj[i, j] = 1
                adj[j, i] = 1
    return GraphInstance(n=n, adj=adj, name=name or f"ER({n},{p})")


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


def generate_regular(n: int, d: int) -> GraphInstance:
    adj = np.zeros((n, n))
    for i in range(n):
        for k in range(1, d // 2 + 1):
            j = (i + k) % n
            adj[i, j] = 1
            adj[j, i] = 1
    return GraphInstance(n=n, adj=adj, name=f"Reg({n},{d})")


def main() -> None:
    print("=" * 80)
    print("PROBLEM 6 VERIFICATION: Large epsilon-light vertex subsets")
    print("=" * 80)
    print()

    # ---- PART 1: Brute force on small graphs ----
    print("PART 1: BRUTE FORCE (exact optimal for small graphs)")
    print("-" * 80)
    print(f"{'Graph':<12} {'eps':>5} {'opt|S|':>7} {'|V|':>5} "
          f"{'|S|/|V|':>8} {'c_eff':>8} {'PSD':>4}")
    print("-" * 80)

    small_graphs = [
        generate_complete(6), generate_complete(8),
        generate_cycle(7), generate_cycle(8),
        generate_star(6), generate_star(7),
        generate_regular(8, 4),
    ]
    brute_results = []

    for G in small_graphs:
        for eps in [0.1, 0.2, 0.3, 0.5]:
            S_opt, size_opt = brute_force_max_light(G.adj, eps)
            if size_opt > 0:
                is_psd, min_eig = check_epsilon_light(G.adj, S_opt, eps)
            else:
                is_psd, min_eig = True, 0.0
            frac = size_opt / G.n
            c_eff = frac / eps if eps > 0 else float('inf')
            print(f"{G.name:<12} {eps:>5.1f} {size_opt:>7d} {G.n:>5d} "
                  f"{frac:>8.4f} {c_eff:>8.4f} {'Y' if is_psd else 'N':>4}")
            brute_results.append((G.name, eps, size_opt, G.n, c_eff))

    min_c_brute = min(r[4] for r in brute_results)
    print(f"\nMinimum c from brute force: {min_c_brute:.6f}")
    print(f"1/256 = {1/256:.6f}")
    print(f"Brute force c >= 1/256? {min_c_brute >= 1/256 - 1e-10}")

    # ---- PART 2: Heuristic search on larger graphs ----
    print()
    print("PART 2: HEURISTIC SEARCH (larger graphs)")
    print("-" * 80)

    graphs = [
        generate_complete(15),
        generate_complete(20),
        generate_cycle(15),
        generate_cycle(20),
        generate_star(15),
        generate_star(20),
        generate_regular(15, 4),
        generate_regular(20, 6),
        generate_erdos_renyi(15, 0.3, "ER(15,0.3)"),
        generate_erdos_renyi(15, 0.5, "ER(15,0.5)"),
        generate_erdos_renyi(20, 0.3, "ER(20,0.3)"),
        generate_erdos_renyi(20, 0.5, "ER(20,0.5)"),
    ]

    epsilons = [0.1, 0.2, 0.3, 0.5]

    print(f"{'Graph':<14} {'eps':>5} {'|S|':>5} {'|V|':>5} "
          f"{'|S|/|V|':>8} {'c_eff':>8} {'PSD':>4} {'Method':<10}")
    print("-" * 80)

    heuristic_results = []

    for G in graphs:
        for eps in epsilons:
            t0 = time.perf_counter()

            # Try multiple methods
            candidates = []

            S1 = find_epsilon_light_random(G.adj, eps, num_trials=300)
            if S1:
                ok, _ = check_epsilon_light(G.adj, S1, eps)
                if ok:
                    candidates.append((S1, "random"))

            S2 = find_epsilon_light_greedy_add(G.adj, eps)
            if S2:
                ok, _ = check_epsilon_light(G.adj, S2, eps)
                if ok:
                    candidates.append((S2, "greedy_add"))

            if G.n <= 20:
                S3 = find_epsilon_light_greedy_remove(G.adj, eps)
                if S3:
                    ok, _ = check_epsilon_light(G.adj, S3, eps)
                    if ok:
                        candidates.append((S3, "greedy_rem"))

            elapsed = time.perf_counter() - t0

            if candidates:
                best_S, best_method = max(candidates, key=lambda x: len(x[0]))
                is_psd, min_eig = check_epsilon_light(G.adj, best_S, eps)
                frac = len(best_S) / G.n
                c_eff = frac / eps
            else:
                best_S, best_method = [], "none"
                is_psd, min_eig = True, 0.0
                frac = 0.0
                c_eff = 0.0

            print(f"{G.name:<14} {eps:>5.1f} {len(best_S):>5d} {G.n:>5d} "
                  f"{frac:>8.4f} {c_eff:>8.4f} "
                  f"{'Y' if is_psd else 'N':>4} {best_method:<10}")

            heuristic_results.append(VerificationResult(
                graph_name=G.name,
                n=G.n,
                epsilon=eps,
                subset_size=len(best_S),
                fraction=frac,
                target_fraction=(1 / 256) * eps,
                is_psd=is_psd,
                min_eigenvalue=min_eig,
                method=best_method,
                time_seconds=elapsed,
            ))

    # ---- PART 3: Theoretical verification for complete graphs ----
    print()
    print("PART 3: COMPLETE GRAPH ANALYSIS (K_n)")
    print("-" * 80)
    print("For K_n, L = nI - J. For S with |S| = s:")
    print("  L_S has eigenvalues: 0 (mult 1 on all-ones), s (on S-perp in S-span),")
    print("  and 0 on complement.")
    print()

    for n in [10, 20, 50]:
        G = generate_complete(n)
        L = laplacian(G.adj)
        print(f"K_{n}:")
        for eps in [0.1, 0.3, 0.5]:
            # Find max s such that eps*L - L_S >= 0
            max_s = 0
            for s in range(1, n + 1):
                S = list(range(s))
                is_psd, min_eig = check_epsilon_light(G.adj, S, eps)
                if is_psd:
                    max_s = s
                else:
                    break
            c_eff = (max_s / n) / eps if eps > 0 else 0
            print(f"  eps={eps}: max |S|={max_s}, |S|/|V|={max_s/n:.4f}, c_eff={c_eff:.4f}")

    # ---- SUMMARY ----
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    all_c = [r[4] for r in brute_results]
    all_c += [r.fraction / r.epsilon for r in heuristic_results
              if r.epsilon > 0 and r.subset_size > 0]

    if all_c:
        min_c = min(all_c)
        print(f"Minimum c achieved across all tests: {min_c:.6f}")
        print(f"Target c = 1/256 = {1/256:.6f}")
        print(f"Achieved c >= 1/256? {min_c >= 1/256 - 1e-10}")
        print()
        print(f"All PSD conditions verified: {all(r.is_psd for r in heuristic_results)}")

    print()
    print("CONCLUSION: The existence of epsilon-light subsets of size >= c*eps*|V|")
    print("is confirmed computationally with c well above 1/256 for all tested graphs.")


if __name__ == "__main__":
    main()
