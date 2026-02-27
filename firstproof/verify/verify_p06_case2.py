#!/usr/bin/env python3
"""
Test Case 2 of Problem 6: graphs where alpha(G) < eps*n/8.

For these dense graphs, we need an alternative to the IS approach.

Key insight: for such graphs, the average degree is > 8/eps - 1.
By sum ell_e = n-1 and m edges: avg ell_e = (n-1)/m < 2eps/7.

So most (in fact all) edges have ell_e < 1 (always true for unweighted graphs).
Most edges have ell_e << eps.

CLAIM: For any graph, the greedy algorithm (process vertices, accept if PSD
condition holds) always finds S with |S| >= c*eps*n.

Let's verify this on dense graphs.
"""
from __future__ import annotations

import numpy as np
import time

np.random.seed(42)


def laplacian(adj):
    return np.diag(adj.sum(axis=1)) - adj


def check_eps_light(adj, S, epsilon):
    n = adj.shape[0]
    L = laplacian(adj)
    S_set = set(S)
    adj_S = np.zeros((n, n))
    for i in S_set:
        for j in S_set:
            adj_S[i, j] = adj[i, j]
    L_S = laplacian(adj_S)
    M = epsilon * L - L_S
    min_eig = np.linalg.eigvalsh(M)[0]
    return min_eig >= -1e-10, min_eig


def greedy_eps_light(adj, epsilon, order=None):
    """Greedy construction of eps-light set.
    Process vertices in given order, accept if PSD holds."""
    n = adj.shape[0]
    if order is None:
        order = list(range(n))
    S = []
    for v in order:
        S_trial = S + [int(v)]
        ok, _ = check_eps_light(adj, S_trial, epsilon)
        if ok:
            S = S_trial
    return S


def independence_number_greedy(adj):
    """Greedy IS in original graph."""
    n = adj.shape[0]
    degrees = adj.sum(axis=1)
    order = np.argsort(degrees)
    I = set()
    for v in order:
        if not any(adj[v, w] > 0 for w in I):
            I.add(int(v))
    return len(I)


def generate_complete(n):
    return np.ones((n, n)) - np.eye(n), f"K_{n}"

def generate_erdos_renyi(n, p):
    adj = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            if np.random.random() < p:
                adj[i, j] = 1
                adj[j, i] = 1
    return adj, f"ER({n},{p})"

def generate_regular(n, d):
    adj = np.zeros((n, n))
    for i in range(n):
        for k in range(1, d // 2 + 1):
            j = (i + k) % n
            adj[i, j] = 1
            adj[j, i] = 1
    return adj, f"Reg({n},{d})"

def generate_bipartite(n1, n2):
    n = n1 + n2
    adj = np.zeros((n, n))
    for i in range(n1):
        for j in range(n1, n):
            adj[i, j] = 1
            adj[j, i] = 1
    return adj, f"K_{n1},{n2}"

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

def generate_path(n):
    adj = np.zeros((n, n))
    for i in range(n - 1):
        adj[i, i+1] = 1
        adj[i+1, i] = 1
    return adj, f"P_{n}"


def main():
    t_start = time.perf_counter()
    print("=" * 80)
    print("PROBLEM 6: CASE 2 (DENSE GRAPHS) AND FULL VERIFICATION")
    print("=" * 80)

    # Comprehensive test: for every graph, try greedy with random orderings
    # and check that |S| >= c*eps*n for universal c.

    all_graphs = [
        generate_complete(8),
        generate_complete(15),
        generate_complete(25),
        generate_complete(40),
        generate_cycle(10),
        generate_cycle(20),
        generate_cycle(30),
        generate_star(8),
        generate_star(15),
        generate_star(25),
        generate_path(10),
        generate_path(20),
        generate_regular(10, 4),
        generate_regular(15, 6),
        generate_regular(20, 8),
        generate_regular(20, 12),
        generate_erdos_renyi(15, 0.3),
        generate_erdos_renyi(15, 0.5),
        generate_erdos_renyi(15, 0.8),
        generate_erdos_renyi(20, 0.5),
        generate_erdos_renyi(25, 0.5),
        generate_bipartite(5, 5),
        generate_bipartite(8, 8),
        generate_bipartite(10, 10),
    ]

    epsilons = [0.05, 0.1, 0.2, 0.3, 0.5, 0.8]

    print(f"\n{'Graph':<16} {'eps':>5} {'n':>4} {'alpha':>6} {'greedy':>7} "
          f"{'target':>7} {'c_eff':>8} {'alpha_ok':>9} {'greedy_ok':>10}")
    print("-" * 90)

    min_c_eff_greedy = float('inf')
    min_c_eff_alpha = float('inf')
    all_pass = True

    for adj, name in all_graphs:
        n = adj.shape[0]
        alpha = independence_number_greedy(adj)
        d_avg = adj.sum() / n

        for eps in epsilons:
            target = eps * n / 8  # Want c = 1/8

            # Greedy with 5 random orderings, take best
            best_greedy = 0
            for trial in range(5):
                order = list(np.random.permutation(n))
                S = greedy_eps_light(adj, eps, order)
                best_greedy = max(best_greedy, len(S))

            c_eff_greedy = (best_greedy / n) / eps if eps > 0 and n > 0 else 0
            c_eff_alpha = (alpha / n) / eps if eps > 0 and n > 0 else 0

            alpha_ok = alpha >= target
            greedy_ok = best_greedy >= target
            combined_ok = alpha_ok or greedy_ok

            # Use max of alpha and greedy
            best_overall = max(alpha, best_greedy)
            c_eff_best = (best_overall / n) / eps

            if not combined_ok:
                all_pass = False

            if c_eff_greedy < min_c_eff_greedy and best_greedy > 0:
                min_c_eff_greedy = c_eff_greedy
            if alpha > 0 and c_eff_alpha < min_c_eff_alpha:
                min_c_eff_alpha = c_eff_alpha

            # Print only interesting cases (where target > 1 or failure)
            if target > 0.5 or not combined_ok:
                flag = "" if combined_ok else " FAIL!"
                print(f"{name:<16} {eps:>5.2f} {n:>4d} {alpha:>6d} {best_greedy:>7d} "
                      f"{target:>7.1f} {c_eff_best:>8.4f} "
                      f"{'Y' if alpha_ok else 'N':>9} "
                      f"{'Y' if greedy_ok else 'N':>10}{flag}")

    print()
    print(f"ALL TESTS PASS (c=1/8): {all_pass}")
    print(f"Min c_eff (greedy): {min_c_eff_greedy:.6f}")
    print(f"Min c_eff (alpha): {min_c_eff_alpha:.6f}")

    # Detailed analysis of K_n (Case 2 representative)
    print("\n\nDETAILED K_n ANALYSIS")
    print("-" * 60)
    print("K_n: alpha=1, d_avg=n-1. Case 2 when eps*n/8 > 1, i.e. n > 8/eps.")
    print("For K_n, greedy finds S of size floor(eps*n).")
    print()

    for n in [10, 20, 30, 50]:
        adj, name = generate_complete(n)
        for eps in [0.1, 0.3, 0.5]:
            target = eps * n / 8
            S = greedy_eps_light(adj, eps)
            c_eff = (len(S) / n) / eps
            print(f"  K_{n}: eps={eps}, |S|={len(S)}, target={target:.1f}, "
                  f"c_eff={c_eff:.4f}, floor(eps*n)={int(eps*n)}")

    # The COMBINED approach: max(alpha, greedy_size)
    print("\n\nCOMBINED APPROACH: max(IS, greedy)")
    print("-" * 60)

    worst_c = float('inf')
    for adj, name in all_graphs:
        n = adj.shape[0]
        alpha = independence_number_greedy(adj)
        for eps in epsilons:
            best_greedy = 0
            for trial in range(5):
                order = list(np.random.permutation(n))
                S = greedy_eps_light(adj, eps, order)
                best_greedy = max(best_greedy, len(S))

            best = max(alpha, best_greedy)
            c = (best / n) / eps
            if c < worst_c:
                worst_c = c
                worst_case = (name, n, eps, alpha, best_greedy)

    print(f"Worst c_eff = {worst_c:.6f}")
    name, n, eps, alpha, greedy = worst_case
    print(f"  Achieved by: {name}, n={n}, eps={eps}, alpha={alpha}, greedy={greedy}")
    print(f"  c >= 1/8 = {1/8:.6f}? {worst_c >= 1/8 - 1e-6}")

    elapsed = time.perf_counter() - t_start
    print(f"\nTotal time: {elapsed:.2f}s")
    print("=" * 80)


if __name__ == "__main__":
    main()
