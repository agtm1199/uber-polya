#!/usr/bin/env python3
"""
Clean verification for Problem 6: Large epsilon-light vertex subsets.

The CLEAN proof strategy:
  For any graph G on n vertices and eps in (0,1]:
  1. Compute the independent set I in G with |I| >= n/(1+d_avg) by Turan bound.
  2. I is trivially eps-light (no edges, L_I = 0).
  3. |I| >= n/(1+d_avg).

  Question: when is n/(1+d_avg) >= c*eps*n, i.e. 1/(1+d_avg) >= c*eps?

  This requires d_avg <= 1/(c*eps) - 1.
  For graphs with d_avg > 1/(c*eps) - 1, we need a different argument.

  KEY INSIGHT: For ANY subset S of size s, the PSD condition eps*L - L_S >= 0
  is equivalent to: for all x, x^T L_S x <= eps * x^T L x.

  For a graph with largest Laplacian eigenvalue lambda_max and S of size s:
  ||L_S|| <= 2*(s-1) (since max degree in G_S is at most s-1)

  The condition eps*L - L_S >= 0 requires eps*lambda_i(L) >= lambda_i(L_S)
  for all i, which is NOT the same as eps*lambda_max(L) >= lambda_max(L_S).
  It requires the ordering to align.

  CORRECT APPROACH: Since L_S is the Laplacian of a SUBGRAPH of G (the
  induced subgraph on S), we have L_S <= L (in PSD order, because each
  edge is either kept or removed). Wait, NO! L and L_S are both Laplacians
  on V, but L_S only includes edges within S. The key: L - L_S = sum of
  L_e over edges NOT in E(S,S), which is PSD. So L_S <= L (PSD order).

  This means: 1*L - L_S >= 0 always, i.e. S is always 1-light.
  For eps < 1: need eps*L - L_S >= 0. Write L_S = sum_{e in E(S,S)} L_e.
  This is a subsum of L = sum_{e in E} L_e.

  The condition is: the subsum is at most eps fraction of the total sum.

  For an independent set I: E(I,I) = empty, L_I = 0, so eps*L >= 0. Always works.

  So the question reduces to: can we find a large independent set?
  alpha(G) >= n/(1+d_avg) >= n/(1+2m/n) = n^2/(n+2m).

  We need alpha(G) >= c*eps*n. This holds when n/(1+d_avg) >= c*eps*n,
  i.e. d_avg <= 1/(c*eps) - 1.

  For dense graphs with d_avg > 1/(c*eps) - 1: we need a non-trivial argument.
  But the claim requires ANY positive c.

  COMPLETE CLEAN PROOF:
  Case 1: alpha(G) >= eps*n/8. Take I. Done.
  Case 2: alpha(G) < eps*n/8. Then d_avg > 8/eps - 1 >= 7/eps.
  So m > 7n/(2*eps), which means the graph has many edges.

  In Case 2, we use a probabilistic argument:
  Take S by including each vertex independently with probability p = eps/4.
  E[|S|] = p*n = eps*n/4.
  E[L_S] = p^2 * L (since each edge e={u,v} is in E(S,S) with prob p^2).
  ||E[L_S]|| = p^2 * ||L|| = (eps/4)^2 * ||L||.

  For the PSD condition: we need ||L_S|| <= eps * lambda_min^+(L)
  (smallest positive Laplacian eigenvalue) AT WORST.
  Actually, we need eps*L - L_S >= 0, which means L^{-1/2}L_S L^{-1/2} <= eps*I
  on range(L). The expectation is p^2 * I, so ||E[..]|| = p^2 = eps^2/16 << eps.

  By matrix Bernstein (vertex independence version):
  Each vertex v contributes a random matrix X_v to L_S (the edges from v
  to other vertices in S). These are NOT independent since X_v depends
  on which other vertices are in S.

  Alternative: use matrix Chernoff for the edge indicators.
  The edges e = {u,v} are included with prob p^2 (product of two Bernoullis).
  These are NOT independent (share vertices).

  CLEANEST APPROACH: partition-based argument.
  Take a random k-partition of V into parts V_1,...,V_k.
  E[|V_i|] = n/k. E[edges within V_i] = m/k^2 (approx).
  By pigeonhole, some V_i has E(V_i,V_i) at most m/k edges in expectation.
  Set k = ceil(1/eps). Then V_i has size ~ eps*n and few internal edges.

  Actually: for a random 2-partition, each edge e={u,v} falls within V_1
  with prob 1/4. So E[|E(V_1,V_1)|] = m/4, E[|V_1|] = n/2.
  ||L_{V_1}|| ~ ||L||/4 in expectation, but we need <= eps*||L||.
  For 1/4 <= eps, we're fine. For eps < 1/4, use k = ceil(1/eps).

  Random k-coloring: each vertex gets a color from {1,...,k} uniformly.
  E[|V_1|] = n/k. Pr[edge e in E(V_1,V_1)] = 1/k^2.
  E[L_{V_1}] = (1/k^2) L. ||E[L_{V_1}]|| = ||L||/k^2.
  For eps*||L|| >= ||L||/k^2, need k^2 >= 1/eps, i.e. k >= 1/sqrt(eps).

  Set k = ceil(1/sqrt(eps)). Then |V_1| ~ sqrt(eps)*n.
  We need |V_1| >= c*eps*n, so sqrt(eps)*n >= c*eps*n, i.e.
  1/sqrt(eps) >= c, i.e. c <= sqrt(eps). This fails for small eps!

  ... This approach gives subsets of size sqrt(eps)*n, not eps*n.

  THE CORRECT APPROACH must exploit the PSD condition more carefully.
  Going back to the independent set in the heavy-edge graph:

  Define heavy edges: E_H = {e : ell_e > eps/2} where ell_e = R_eff(e).
  |E_H| < 2(n-1)/eps (since sum ell_e = n-1).
  d_avg(G_H) < 4/eps.
  Independent set in G_H: |I| >= n/(1+4/eps) = eps*n/(eps+4) >= eps*n/5.
  I has no heavy edges: all edges in E(I,I) have ell_e <= eps/2.

  NOW: I has |I| >= eps*n/5. But we need I to be eps-light.
  The condition: eps*L - L_I >= 0.
  Since L_I = sum_{e in E(I,I)} L_e and each ell_e <= eps/2,
  we know tr(L^{+/2} L_I L^{+/2}) = sum ell_e <= |E(I,I)| * eps/2.

  But trace is NOT enough to control the spectral norm.

  HOWEVER: we can subsample from I. Take a random subset T of I,
  including each vertex with prob p. E[|T|] = p*|I| >= p*eps*n/5.
  For edges in E(T,T): prob p^2 * (edge exists in E(I,I)).
  E[sum_{e in E(T,T)} ell_e] = p^2 * sum_{e in E(I,I)} ell_e <= p^2 * (n-1).

  On range(L): L^{+/2} L_T L^{+/2} = sum_{e in E(T,T)} A_e.
  E[sum] = p^2 * sum_{e in E(I,I)} A_e <= p^2 * Pi.
  ||E[sum]|| <= p^2.

  For p^2 <= eps: p <= sqrt(eps).
  E[|T|] >= sqrt(eps) * eps * n / 5 = eps^{3/2} * n / 5.

  This gives c = eps^{1/2}/5, which depends on eps. Not universal.

  FINAL INSIGHT: The Turan bound on the heavy-edge graph gives |I| >= eps*n/5,
  and the subsampling at rate p=sqrt(eps) gives |T| ~ eps^{3/2}*n/5.
  This is NOT c*eps*n for universal c.

  The correct approach must be MORE CLEVER. Let me test whether just taking
  I (the independent set in G_H) actually works as eps-light.
"""
from __future__ import annotations

import numpy as np
import time

np.random.seed(42)


def laplacian(adj: np.ndarray) -> np.ndarray:
    return np.diag(adj.sum(axis=1)) - adj


def compute_leverage_scores(adj: np.ndarray) -> dict:
    n = adj.shape[0]
    L = laplacian(adj)
    eigenvalues, eigenvectors = np.linalg.eigh(L)
    Lplus = np.zeros((n, n))
    for i in range(n):
        if eigenvalues[i] > 1e-10:
            Lplus += (1.0 / eigenvalues[i]) * np.outer(eigenvectors[:, i], eigenvectors[:, i])
    scores = {}
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i, j] > 0:
                diff = np.zeros(n)
                diff[i] = 1.0
                diff[j] = -1.0
                scores[(i, j)] = diff @ Lplus @ diff
    return scores


def find_IS_in_heavy_graph(adj: np.ndarray, epsilon: float):
    """Find independent set in heavy-edge graph G_H.
    Heavy edges: ell_e > eps/2."""
    n = adj.shape[0]
    scores = compute_leverage_scores(adj)

    # Build heavy-edge adjacency
    heavy_adj = np.zeros((n, n))
    for (i, j), ell in scores.items():
        if ell > epsilon / 2:
            heavy_adj[i, j] = 1
            heavy_adj[j, i] = 1

    # Greedy independent set (by degree ascending in heavy graph)
    degrees = heavy_adj.sum(axis=1)
    order = np.argsort(degrees)
    I = set()
    for v in order:
        if not any(heavy_adj[v, w] > 0 for w in I):
            I.add(int(v))

    return list(I), scores


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


def test_IS_lightness(adj, name, epsilon):
    """Test if the IS in heavy-edge graph is epsilon-light."""
    n = adj.shape[0]
    I, scores = find_IS_in_heavy_graph(adj, epsilon)

    is_psd, min_eig = check_eps_light(adj, I, epsilon)
    c_eff = (len(I) / n) / epsilon if epsilon > 0 else 0

    # Max leverage score in E(I,I)
    I_set = set(I)
    max_ell_I = 0
    num_edges_I = 0
    total_ell_I = 0
    for (u, v), ell in scores.items():
        if u in I_set and v in I_set:
            max_ell_I = max(max_ell_I, ell)
            num_edges_I += 1
            total_ell_I += ell

    print(f"  {name}: n={n}, eps={epsilon}, |I|={len(I)}, c_eff={c_eff:.4f}, "
          f"PSD={is_psd}, min_eig={min_eig:.6f}, "
          f"|E(I,I)|={num_edges_I}, max_ell={max_ell_I:.6f}, "
          f"total_ell={total_ell_I:.4f}")

    return is_psd, c_eff, len(I)


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


def main():
    t_start = time.perf_counter()
    print("=" * 80)
    print("PROBLEM 6: CLEAN PROOF VERIFICATION")
    print("=" * 80)

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
        generate_regular(12, 6),
        generate_regular(15, 4),
        generate_erdos_renyi(12, 0.3),
        generate_erdos_renyi(15, 0.5),
        generate_bipartite(5, 5),
        generate_bipartite(6, 8),
    ]

    print("\nPART 1: IS the independent set in G_H actually eps-light?")
    print("-" * 80)

    all_results = []
    for eps in [0.1, 0.2, 0.3, 0.5]:
        print(f"\n--- epsilon = {eps} ---")
        for adj, name in graphs:
            psd, c, size = test_IS_lightness(adj, name, eps)
            all_results.append((name, eps, psd, c, size))

    # Summary
    print("\n\nSUMMARY")
    print("=" * 60)
    violations = [(name, eps, psd, c, sz) for name, eps, psd, c, sz in all_results if not psd]
    if violations:
        print(f"VIOLATIONS: {len(violations)}")
        for name, eps, psd, c, sz in violations:
            print(f"  {name}, eps={eps}: NOT PSD")
    else:
        print("ALL TESTS PASSED: IS in heavy-edge graph is always eps-light!")

    min_c = min(c for _, _, _, c, _ in all_results if c > 0)
    print(f"Minimum c_eff: {min_c:.6f}")
    print(f"c >= 1/5 = {1/5:.6f}? {min_c >= 1/5 - 1e-6}")

    # Part 2: Test the pure independent set approach
    print("\n\nPART 2: PURE INDEPENDENT SET (IN ORIGINAL GRAPH)")
    print("-" * 60)
    print("If alpha(G) >= c*eps*n, just take the IS.")

    for adj, name in graphs:
        n = adj.shape[0]
        # Find IS in original graph
        degrees = adj.sum(axis=1)
        order = np.argsort(degrees)
        I = set()
        for v in order:
            if not any(adj[v, w] > 0 for w in I):
                I.add(int(v))
        alpha = len(I)
        d_avg = degrees.mean()
        turan = n / (1 + d_avg)
        print(f"  {name}: n={n}, alpha={alpha}, d_avg={d_avg:.1f}, "
              f"Turan_bound={turan:.1f}")

    elapsed = time.perf_counter() - t_start
    print(f"\nTotal time: {elapsed:.2f}s")
    print("=" * 80)


if __name__ == "__main__":
    main()
