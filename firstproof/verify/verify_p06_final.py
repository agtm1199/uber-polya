#!/usr/bin/env python3
"""
FINAL verification for Problem 6: Large epsilon-light vertex subsets.

The correct proof strategy:

CASE 1: alpha(G) >= eps*n*c. Use independent set. L_S = 0. Done.

CASE 2: alpha(G) < eps*n*c. Graph is dense: d_avg > 1/(c*eps) - 1.
  Need to show: some set S of size >= c*eps*n is eps-light.

For Case 2, we exploit: in dense graphs, a RANDOM subset of moderate
size is eps-light with high probability.

KEY LEMMA FOR DENSE GRAPHS:
Let S be a uniformly random subset of V with |S| = s.
For each edge e = {u,v}, Pr[e in E(S,S)] = s(s-1)/(n(n-1)).
So E[L_S] = s(s-1)/(n(n-1)) * L.

For the PSD condition eps*L - L_S >= 0, we need the RANDOM matrix L_S
to not exceed eps*L.

Using matrix concentration (Tropp): the deviation ||L_S - E[L_S]||
can be bounded, and if E[L_S] is small enough relative to eps*L,
the PSD condition holds with positive probability.

But there's a simpler approach: use the greedy algorithm starting
from an independent set in G_H, but CAP the size at eps*n.

Actually, the simplest correct approach for Case 2:
Since d_avg > 1/(c*eps) - 1, there are at least n*d_avg/2 edges.
The leverage scores sum to n-1, so the average ell_e = (n-1)/m.
For m > n/(2c*eps), we get avg ell_e < 2c*eps.

So most edges are light. Build IS in G_H (heavy-edge graph with
threshold eps), but then TRUNCATE the IS to have at most eps*n vertices.

Wait - but the IS in G_H can be all of V when all ell_e < eps.
The issue is: we need the SUBSET to be eps-light, meaning
sum_{e in E(S,S)} L_e <= eps * sum_{e in E} L_e.

For K_n: any subset of size <= eps*n works.
The question: does this generalize?

THIS SCRIPT tests the following claim:
For any graph G and any S with |S| <= sqrt(eps) * n,
S is eps-light.

And the refined claim: for any S with |S| <= eps * n,
S is eps-light IF the graph has minimum degree >= C/eps for some constant C.
"""
from __future__ import annotations

import numpy as np
import time

np.random.seed(42)


def laplacian(adj: np.ndarray) -> np.ndarray:
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

def generate_path(n):
    adj = np.zeros((n, n))
    for i in range(n - 1):
        adj[i, i+1] = 1
        adj[i+1, i] = 1
    return adj, f"P_{n}"

def generate_regular(n, d):
    adj = np.zeros((n, n))
    for i in range(n):
        for k in range(1, d // 2 + 1):
            j = (i + k) % n
            adj[i, j] = 1
            adj[j, i] = 1
    return adj, f"Reg({n},{d})"

def generate_erdos_renyi(n, p):
    adj = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            if np.random.random() < p:
                adj[i, j] = 1
                adj[j, i] = 1
    return adj, f"ER({n},{p:.1f})"

def generate_bipartite(n1, n2):
    n = n1 + n2
    adj = np.zeros((n, n))
    for i in range(n1):
        for j in range(n1, n):
            adj[i, j] = 1
            adj[j, i] = 1
    return adj, f"K_{n1},{n2}"


def test_sqrt_eps_claim(adj, name, epsilon, num_trials=100):
    """Test: is ANY random set of size floor(sqrt(eps)*n) eps-light?"""
    n = adj.shape[0]
    s = max(1, int(np.sqrt(epsilon) * n))
    successes = 0
    for _ in range(num_trials):
        S = list(np.random.choice(n, s, replace=False))
        ok, _ = check_eps_light(adj, S, epsilon)
        if ok:
            successes += 1
    c_eff = (s / n) / epsilon
    print(f"  {name}: n={n}, eps={epsilon}, s(sqrt)={s}, c_eff={c_eff:.4f}, "
          f"success={successes}/{num_trials}")
    return successes == num_trials


def test_eps_claim(adj, name, epsilon, num_trials=100):
    """Test: is ANY random set of size floor(eps*n) eps-light?"""
    n = adj.shape[0]
    s = max(1, int(epsilon * n))
    successes = 0
    for _ in range(num_trials):
        S = list(np.random.choice(n, s, replace=False))
        ok, _ = check_eps_light(adj, S, epsilon)
        if ok:
            successes += 1
    c_eff = (s / n) / epsilon
    print(f"  {name}: n={n}, eps={epsilon}, s(eps*n)={s}, c_eff={c_eff:.4f}, "
          f"success={successes}/{num_trials}")
    return successes == num_trials


def find_max_eps_light_size(adj, epsilon, num_trials=50):
    """Find the maximum size of an eps-light random set."""
    n = adj.shape[0]
    max_psd_size = 0
    for _ in range(num_trials):
        # Random permutation
        perm = np.random.permutation(n)
        # Greedy: add vertices in random order, check PSD
        S = []
        for v in perm:
            S_trial = S + [int(v)]
            ok, _ = check_eps_light(adj, S_trial, epsilon)
            if ok:
                S = S_trial
        max_psd_size = max(max_psd_size, len(S))
    return max_psd_size


def main():
    t_start = time.perf_counter()
    print("=" * 80)
    print("PROBLEM 6: FINAL VERIFICATION")
    print("=" * 80)

    graphs = [
        generate_complete(10),
        generate_complete(20),
        generate_complete(30),
        generate_cycle(10),
        generate_cycle(20),
        generate_star(8),
        generate_star(15),
        generate_path(10),
        generate_path(20),
        generate_regular(10, 4),
        generate_regular(15, 6),
        generate_regular(20, 8),
        generate_erdos_renyi(15, 0.3),
        generate_erdos_renyi(15, 0.7),
        generate_bipartite(5, 5),
        generate_bipartite(8, 8),
    ]

    # PART 1: For each graph, find the MAX eps-light set size
    print("\nPART 1: MAXIMUM eps-light set sizes (greedy from random orders)")
    print("-" * 80)
    print(f"{'Graph':<16} {'eps':>5} {'max|S|':>7} {'n':>5} {'c_eff':>8} {'|S|/n':>8}")
    print("-" * 80)

    for adj, name in graphs:
        n = adj.shape[0]
        for eps in [0.1, 0.3, 0.5]:
            max_s = find_max_eps_light_size(adj, eps, num_trials=20)
            c_eff = (max_s / n) / eps if eps > 0 else 0
            print(f"{name:<16} {eps:>5.1f} {max_s:>7d} {n:>5d} {c_eff:>8.4f} {max_s/n:>8.4f}")

    # PART 2: Test if random subset of size floor(eps*n) always works
    print("\n\nPART 2: RANDOM SUBSET OF SIZE floor(eps*n)")
    print("-" * 80)
    print("If this always works, then c = 1 and the proof is trivial!")

    for adj, name in graphs:
        for eps in [0.1, 0.3, 0.5]:
            test_eps_claim(adj, name, eps, num_trials=50)

    # PART 3: Test the sqrt(eps) claim
    print("\n\nPART 3: RANDOM SUBSET OF SIZE floor(sqrt(eps)*n)")
    print("-" * 80)

    for adj, name in graphs:
        for eps in [0.1, 0.3, 0.5]:
            test_sqrt_eps_claim(adj, name, eps, num_trials=50)

    # PART 4: For K_n, the answer is known analytically
    print("\n\nPART 4: COMPLETE GRAPH ANALYSIS")
    print("-" * 60)
    print("For K_n: S of size s is eps-light iff s <= eps*n.")
    print("So max |S| = floor(eps*n), c_eff = floor(eps*n)/(eps*n) ~ 1.")

    for n in [10, 20, 50, 100]:
        adj = np.ones((n, n)) - np.eye(n)
        for eps in [0.1, 0.3, 0.5]:
            s = int(eps * n)
            # Analytical check for K_n
            # L_{K_n} = nI - J, eigenvalues: 0 (x1), n (xn-1)
            # L_S: eigenvalues 0 (x n-s+1), s (x s-1) when S induces K_s
            # eps*L - L_S: eigenvalues eps*n - s (x s-1), eps*n (x n-s), 0 (x1)
            margin = eps * n - s
            print(f"  K_{n}: eps={eps}, s={s}, eps*n={eps*n:.0f}, "
                  f"margin={margin:.0f}, c=s/(eps*n)={s/(eps*n):.4f}")

    # PART 5: Comparison of approaches for the definitive proof
    print("\n\nPART 5: DEFINITIVE PROOF APPROACH")
    print("-" * 60)
    print("For each graph, compare:")
    print("  (a) IS in original G: trivially eps-light")
    print("  (b) Random subset of size floor(eps*n): sometimes eps-light")
    print("  (c) Greedy from IS in heavy-edge graph, capped at eps*n")

    for adj, name in graphs:
        n = adj.shape[0]
        degrees = adj.sum(axis=1)
        d_avg = degrees.mean()

        # (a) IS in G
        order = np.argsort(degrees)
        I = set()
        for v in order:
            if not any(adj[v, w] > 0 for w in I):
                I.add(int(v))
        alpha = len(I)

        for eps in [0.3]:
            target = max(1, int(eps * n / 8))
            # Which approach gives >= target?
            # (a) IS
            a_ok = alpha >= target
            # (b) Random subset of eps*n
            s_rand = int(eps * n)
            S_rand = list(np.random.choice(n, min(s_rand, n), replace=False))
            b_ok_psd, _ = check_eps_light(adj, S_rand, eps)
            b_ok = b_ok_psd and len(S_rand) >= target
            # (c) Greedy
            max_greedy = find_max_eps_light_size(adj, eps, num_trials=5)
            c_ok = max_greedy >= target

            print(f"  {name}: n={n}, eps={eps}, target={target}, "
                  f"alpha={alpha}({'OK' if a_ok else 'FAIL'}), "
                  f"|S_rand|={len(S_rand)}/PSD={b_ok_psd}({'OK' if b_ok else 'FAIL'}), "
                  f"greedy_max={max_greedy}({'OK' if c_ok else 'FAIL'})")

    elapsed = time.perf_counter() - t_start
    print(f"\nTotal time: {elapsed:.2f}s")
    print("=" * 80)


if __name__ == "__main__":
    main()
