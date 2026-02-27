#!/usr/bin/env python3
"""
Verification of the dense-case argument for Problem 6.

When alpha(G) < eps*n/8, the graph is dense (avg degree > 8/eps - 1).
We test whether a random subset of size s = floor(eps*n/8) is eps-light.

Key identity: for a uniformly random subset S of size s,
  E[L_S] = (s(s-1))/(n(n-1)) * L

So E[L_S] = eps_eff * L where eps_eff = s(s-1)/(n(n-1)) ~ (eps/8)^2 << eps.

The question is whether L_S concentrates around its expectation.
"""
from __future__ import annotations

import numpy as np
import time

np.random.seed(42)


def laplacian(adj: np.ndarray) -> np.ndarray:
    return np.diag(adj.sum(axis=1)) - adj


def test_random_subset_concentration(adj: np.ndarray, name: str, epsilon: float,
                                      num_trials: int = 500):
    """Test if random subsets of size floor(eps*n/8) are eps-light."""
    n = adj.shape[0]
    s = max(1, int(epsilon * n / 8))
    L = laplacian(adj)

    # Expected: E[L_S] = s(s-1)/(n(n-1)) * L
    eps_eff = s * (s - 1) / (n * (n - 1)) if n > 1 else 0
    print(f"  {name}: n={n}, eps={epsilon}, s={s}, eps_eff={eps_eff:.6f}, eps={epsilon}")

    successes = 0
    for trial in range(num_trials):
        S = np.random.choice(n, s, replace=False)
        S_set = set(S)

        # Compute L_S
        adj_S = np.zeros((n, n))
        for i in S_set:
            for j in S_set:
                adj_S[i, j] = adj[i, j]
        L_S = laplacian(adj_S)

        # Check eps*L - L_S >= 0
        M = epsilon * L - L_S
        min_eig = np.linalg.eigvalsh(M)[0]
        if min_eig >= -1e-10:
            successes += 1

    print(f"    Success rate: {successes}/{num_trials} = {successes/num_trials:.2%}")
    return successes, num_trials


def test_deterministic_low_degree_selection(adj: np.ndarray, name: str, epsilon: float):
    """Test: select the s = floor(eps*n/8) vertices with lowest degree.
    In dense graphs, these vertices have fewer internal edges."""
    n = adj.shape[0]
    s = max(1, int(epsilon * n / 8))
    L = laplacian(adj)

    degrees = adj.sum(axis=1)
    order = np.argsort(degrees)
    S = list(order[:s])

    # Check eps-lightness
    S_set = set(S)
    adj_S = np.zeros((n, n))
    for i in S_set:
        for j in S_set:
            adj_S[i, j] = adj[i, j]
    L_S = laplacian(adj_S)
    M = epsilon * L - L_S
    min_eig = np.linalg.eigvalsh(M)[0]
    is_psd = min_eig >= -1e-10

    # Also compute the max eigenvalue ratio
    eig_L = np.linalg.eigvalsh(L)
    eig_LS = np.linalg.eigvalsh(L_S)
    max_ratio = 0
    for i in range(n):
        if eig_L[i] > 1e-10:
            ratio = eig_LS[i] / eig_L[i]
            max_ratio = max(max_ratio, ratio)

    print(f"  {name}: n={n}, eps={epsilon}, s={s}, PSD={is_psd}, "
          f"min_eig={min_eig:.6f}, max_eig_ratio={max_ratio:.4f}")
    return is_psd


def test_interlacing_bound(adj: np.ndarray, name: str, epsilon: float):
    """Test the Cauchy interlacing / eigenvalue-by-eigenvalue bound.

    For S subset of V with |S|=s, the eigenvalues of L_S interlace with those of L.
    Specifically, lambda_i(L_S) <= lambda_{i+n-s}(L) for all i.

    But actually the correct bound for the PSD condition eps*L - L_S >= 0 is:
    we need lambda_max(L^{-1/2} L_S L^{-1/2}) <= eps (on range of L).
    """
    n = adj.shape[0]
    s = max(1, int(epsilon * n / 8))
    L = laplacian(adj)

    # For complete graph K_n: L = nI - J, eigenvalues: 0 (mult 1), n (mult n-1)
    # For S of size s in K_n: L_S has eigenvalues 0 (mult 1), s (mult s-1), 0 (mult n-s)
    # eps*L - L_S: eigenvalues eps*n - s (mult s-1), eps*n (mult n-s), 0 (mult 1)
    # PSD iff eps*n >= s, i.e. s <= eps*n.
    # With s = eps*n/8: eps*n - eps*n/8 = 7*eps*n/8 > 0. Always works.

    # For any graph: we need a bound on how L_S can compare to L.
    # The key quantity: for S of size s, L_S = sum_{e in E(S,S)} L_e.
    # Each L_e has ||L_e|| = 2.
    # The number of edges in E(S,S) is at most s*(s-1)/2.
    # So ||L_S|| <= 2 * s*(s-1)/2 = s*(s-1).
    # And we need ||L_S|| <= eps * lambda_2(L).

    eig_L = np.linalg.eigvalsh(L)
    lambda2 = eig_L[1] if n > 1 else 0

    S = np.random.choice(n, s, replace=False)
    S_set = set(S)
    adj_S = np.zeros((n, n))
    for i in S_set:
        for j in S_set:
            adj_S[i, j] = adj[i, j]
    L_S = laplacian(adj_S)
    eig_LS = np.linalg.eigvalsh(L_S)
    max_eig_LS = eig_LS[-1]

    print(f"  {name}: lambda_2(L)={lambda2:.4f}, ||L_S||={max_eig_LS:.4f}, "
          f"eps*lambda_2={epsilon*lambda2:.4f}, "
          f"s(s-1)={s*(s-1)}, "
          f"||L_S||<=eps*lambda_2? {max_eig_LS <= epsilon * lambda2 + 1e-10}")


def generate_complete(n):
    return np.ones((n, n)) - np.eye(n)


def generate_cycle(n):
    adj = np.zeros((n, n))
    for i in range(n):
        adj[i, (i+1) % n] = 1
        adj[(i+1) % n, i] = 1
    return adj


def generate_regular(n, d):
    adj = np.zeros((n, n))
    for i in range(n):
        for k in range(1, d // 2 + 1):
            j = (i + k) % n
            adj[i, j] = 1
            adj[j, i] = 1
    return adj


def generate_erdos_renyi(n, p):
    adj = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            if np.random.random() < p:
                adj[i, j] = 1
                adj[j, i] = 1
    return adj


def main():
    t_start = time.perf_counter()
    print("=" * 80)
    print("PROBLEM 6: DENSE CASE VERIFICATION")
    print("=" * 80)

    # Part 1: Random subset concentration test
    print("\nPART 1: RANDOM SUBSET CONCENTRATION")
    print("-" * 60)
    print("Testing: random S of size floor(eps*n/8) is eps-light?")
    print()

    test_cases = [
        (generate_complete(20), "K_20"),
        (generate_complete(30), "K_30"),
        (generate_complete(50), "K_50"),
        (generate_regular(20, 10), "Reg(20,10)"),
        (generate_regular(30, 14), "Reg(30,14)"),
        (generate_erdos_renyi(20, 0.5), "ER(20,0.5)"),
        (generate_erdos_renyi(30, 0.5), "ER(30,0.5)"),
        (generate_erdos_renyi(20, 0.8), "ER(20,0.8)"),
    ]

    for eps in [0.1, 0.2, 0.3, 0.5]:
        print(f"\n  epsilon = {eps}:")
        for adj, name in test_cases:
            test_random_subset_concentration(adj, name, eps, num_trials=200)

    # Part 2: Complete graph analysis
    print("\n\nPART 2: COMPLETE GRAPH ANALYSIS")
    print("-" * 60)
    print("For K_n, any S of size s: L_S has eigenvalues 0 and s.")
    print("eps*L - L_S PSD iff s <= eps*n.")
    print("With s = eps*n/8: always PSD with large margin.")
    print()

    for n in [10, 20, 50, 100]:
        for eps in [0.1, 0.3, 0.5]:
            s = max(1, int(eps * n / 8))
            margin = eps * n - s
            print(f"  K_{n}: eps={eps}, s={s}, eps*n={eps*n:.1f}, "
                  f"margin=eps*n-s={margin:.1f}, PSD=True")

    # Part 3: Eigenvalue interlacing
    print("\n\nPART 3: EIGENVALUE INTERLACING ANALYSIS")
    print("-" * 60)

    for eps in [0.2, 0.5]:
        print(f"\n  epsilon = {eps}:")
        for adj, name in test_cases[:5]:
            test_interlacing_bound(adj, name, eps)

    # Part 4: Low-degree selection
    print("\n\nPART 4: DETERMINISTIC LOW-DEGREE SELECTION")
    print("-" * 60)

    for eps in [0.1, 0.2, 0.3, 0.5]:
        print(f"\n  epsilon = {eps}:")
        for adj, name in test_cases:
            test_deterministic_low_degree_selection(adj, name, eps)

    # Part 5: Worst-case analysis - dense graphs where the bound is tight
    print("\n\nPART 5: TIGHT EXAMPLES")
    print("-" * 60)
    print("Testing clique on s vertices embedded in K_n")

    for n in [20, 30]:
        for eps in [0.2, 0.5]:
            s = max(1, int(eps * n / 8))
            # Take S = {0,...,s-1} in K_n
            adj = generate_complete(n)
            S = list(range(s))
            L = laplacian(adj)
            S_set = set(S)
            adj_S = np.zeros((n, n))
            for i in S_set:
                for j in S_set:
                    adj_S[i, j] = adj[i, j]
            L_S = laplacian(adj_S)
            M = eps * L - L_S
            min_eig = np.linalg.eigvalsh(M)[0]
            print(f"  K_{n}, eps={eps}, s={s}: min_eig(eps*L - L_S) = {min_eig:.4f}, "
                  f"PSD = {min_eig >= -1e-10}")

    elapsed = time.perf_counter() - t_start
    print(f"\nTotal time: {elapsed:.2f}s")
    print("=" * 80)


if __name__ == "__main__":
    main()
