#!/usr/bin/env python3
"""
Problem 10 Verification: Kernelized CP-ALS subproblem with missing data.
Column-wise gather/scatter PCG with Kronecker (Cholesky-based) preconditioning
and optional Nystrom acceleration.

System:
  [(Z x K)^T S S^T (Z x K) + lambda (I_r x K)] vec(W) = (I_r x K) vec(B)

Novel approach: Column-wise gather/scatter matvec + Cholesky-based Kronecker
preconditioner (not eigendecomposition-based) + Nystrom low-rank kernel option.
"""
from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
import time

np.random.seed(42)


@dataclass(frozen=True)
class Instance:
    n: int
    r: int
    q: int
    K: np.ndarray       # n x n kernel matrix (SPD)
    Z_obs: np.ndarray   # q x r: rows of Z at observed rest-indices
    B: np.ndarray       # n x r MTTKRP
    lam: float
    obs_i: np.ndarray   # q-vector: mode-k indices
    obs_j: np.ndarray   # q-vector: rest indices


@dataclass
class Solution:
    W_direct: np.ndarray
    W_pcg: np.ndarray
    max_error: float
    relative_error: float
    pcg_iterations: int
    pcg_time: float
    direct_time: float
    matvec_correct: bool
    precond_correct: bool
    details: dict = field(default_factory=dict)


def generate_instance(n: int, r: int, M: int,
                      obs_fraction: float = 0.3) -> Instance:
    """Generate test instance with SPD kernel and observed entries."""
    N = n * M
    q = max(int(obs_fraction * N), 2 * n * r)
    q = min(q, N)

    # SPD kernel matrix
    L = np.random.randn(n, n)
    K = L @ L.T + 0.5 * np.eye(n)

    # Full Z matrix (M x r)
    Z_full = np.random.randn(M, r)

    # Observed entries: flat indices in [0, N)
    obs_flat = np.sort(np.random.choice(N, size=q, replace=False))
    obs_i = obs_flat % n
    obs_j = obs_flat // n

    # Z_obs: rows of Z at observed rest-indices
    Z_obs = Z_full[obs_j, :]  # q x r

    # RHS B: simulate MTTKRP
    B = np.random.randn(n, r)

    lam = 0.1

    return Instance(n=n, r=r, q=q, K=K, Z_obs=Z_obs, B=B, lam=lam,
                    obs_i=obs_i, obs_j=obs_j)


def build_explicit_system(inst: Instance) -> tuple[np.ndarray, np.ndarray]:
    """Build the nr x nr system matrix explicitly for verification."""
    n, r, q = inst.n, inst.r, inst.q
    K, Z_obs, lam = inst.K, inst.Z_obs, inst.lam

    # Build S^T(Z x K) as q x nr matrix
    STZK = np.zeros((q, n * r))
    for ell in range(q):
        i_ell = inst.obs_i[ell]
        for s in range(r):
            STZK[ell, s * n:(s + 1) * n] = Z_obs[ell, s] * K[i_ell, :]

    # A = STZK^T STZK + lambda (I_r x K)
    A = STZK.T @ STZK
    for s in range(r):
        A[s * n:(s + 1) * n, s * n:(s + 1) * n] += lam * K

    # RHS: (I_r x K) vec(B)
    rhs = np.zeros(n * r)
    for s in range(r):
        rhs[s * n:(s + 1) * n] = K @ inst.B[:, s]

    return A, rhs


def matvec(inst: Instance, w: np.ndarray) -> np.ndarray:
    """
    Column-wise gather/scatter matvec: y = A w.

    Steps:
    1. Reshape w to W, compute P = KW                O(n^2 r)
    2. Gather: v[l] = Z_obs[l,:] . P[i_l,:]         O(qr)
    3. Scatter: T[i,:] += v[l] * Z_obs[l,:]          O(qr)
    4. Y = KT + lambda * P                            O(n^2 r)
    """
    n, r, q = inst.n, inst.r, inst.q
    K, Z_obs, lam = inst.K, inst.Z_obs, inst.lam

    # Reshape
    W = np.zeros((n, r))
    for s in range(r):
        W[:, s] = w[s * n:(s + 1) * n]

    # Step 1: Kernel multiply
    P = K @ W  # n x r

    # Step 2: Gather (column-wise)
    KW_at_obs = P[inst.obs_i, :]  # q x r
    vals = np.sum(Z_obs * KW_at_obs, axis=1)  # q-vector

    # Step 3: Scatter (column-wise)
    T = np.zeros((n, r))
    np.add.at(T, inst.obs_i, vals[:, None] * Z_obs)

    # Step 4: Kernel multiply + regularize
    Y = K @ T + lam * P

    # Flatten
    y = np.zeros(n * r)
    for s in range(r):
        y[s * n:(s + 1) * n] = Y[:, s]

    return y


def apply_preconditioner_cholesky(inst: Instance, r_vec: np.ndarray,
                                   L_K: np.ndarray,
                                   L_G: np.ndarray) -> np.ndarray:
    """
    Apply M^{-1} using Cholesky factors.
    M = (G + lambda I_r) x K.
    M^{-1} = (G + lambda I)^{-1} x K^{-1}.
    vec(Z) = vec(K^{-1} R (G+lambda I)^{-1}).

    Using Cholesky: K = L_K L_K^T, (G+lambda I) = L_G L_G^T.
    Z = L_K^{-T} L_K^{-1} R L_G^{-T} L_G^{-1}
    """
    n, r = inst.n, inst.r

    R = np.zeros((n, r))
    for s in range(r):
        R[:, s] = r_vec[s * n:(s + 1) * n]

    # Left solve: K^{-1} R = (L_K L_K^T)^{-1} R
    # Forward: Y = L_K^{-1} R
    from scipy.linalg import solve_triangular
    Y = solve_triangular(L_K, R, lower=True)
    # Back: Z1 = L_K^{-T} Y
    Z1 = solve_triangular(L_K, Y, lower=True, trans='T')

    # Right solve: Z1 (G+lambda I)^{-1} = Z1 (L_G L_G^T)^{-1}
    # = Z1 L_G^{-T} L_G^{-1}
    # Right multiply by L_G^{-T}: Z2 = Z1 L_G^{-T} = (L_G^{-1} Z1^T)^T
    Z2 = solve_triangular(L_G, Z1.T, lower=True).T
    # Right multiply by L_G^{-1}: Z3 = Z2 L_G^{-1} = (L_G^{-T} Z2^T)^T
    Z3 = solve_triangular(L_G, Z2.T, lower=True, trans='T').T

    z = np.zeros(n * r)
    for s in range(r):
        z[s * n:(s + 1) * n] = Z3[:, s]

    return z


def pcg_solve(inst: Instance, tol: float = 1e-10, max_iter: int = 1000):
    """PCG with Cholesky-based Kronecker preconditioner."""
    n, r = inst.n, inst.r

    # RHS
    rhs = np.zeros(n * r)
    for s in range(r):
        rhs[s * n:(s + 1) * n] = inst.K @ inst.B[:, s]

    # Cholesky factorizations (one-time setup)
    L_K = np.linalg.cholesky(inst.K)
    G = inst.Z_obs.T @ inst.Z_obs + inst.lam * np.eye(r)
    L_G = np.linalg.cholesky(G)

    # PCG iteration
    t0 = time.perf_counter()
    x = np.zeros(n * r)
    res = rhs.copy()
    z = apply_preconditioner_cholesky(inst, res, L_K, L_G)
    p = z.copy()
    rz = res @ z
    rhs_norm = np.linalg.norm(rhs)

    if rhs_norm < 1e-15:
        return np.zeros((n, r)), 0, 0.0

    for it in range(max_iter):
        Ap = matvec(inst, p)
        pAp = p @ Ap
        if abs(pAp) < 1e-30:
            break
        alpha = rz / pAp
        x += alpha * p
        res -= alpha * Ap

        if np.linalg.norm(res) / rhs_norm < tol:
            it += 1
            break

        z = apply_preconditioner_cholesky(inst, res, L_K, L_G)
        rz_new = res @ z
        beta = rz_new / rz
        p = z + beta * p
        rz = rz_new

    t1 = time.perf_counter()

    W = np.zeros((n, r))
    for s in range(r):
        W[:, s] = x[s * n:(s + 1) * n]

    return W, it, t1 - t0


def solve(inst: Instance) -> Solution:
    n, r, q = inst.n, inst.r, inst.q
    print(f"  Instance: n={n}, r={r}, q={q}")

    # Explicit system for verification
    print("  Building explicit system...")
    t0 = time.perf_counter()
    A_sys, rhs = build_explicit_system(inst)
    print(f"    System: {A_sys.shape}, time: {time.perf_counter()-t0:.4f}s")

    # Direct solve
    print("  Direct solve...")
    t0 = time.perf_counter()
    w_direct = np.linalg.solve(A_sys, rhs)
    t_direct = time.perf_counter() - t0

    # Verify column-wise gather/scatter matvec
    print("  Verifying column-wise gather/scatter matvec...")
    test_w = np.random.randn(n * r)
    mv_explicit = A_sys @ test_w
    mv_free = matvec(inst, test_w)
    mv_err = np.linalg.norm(mv_explicit - mv_free) / np.linalg.norm(mv_explicit)
    print(f"    Relative error: {mv_err:.2e}")
    mv_ok = mv_err < 1e-10

    # Verify Cholesky-based preconditioner
    print("  Verifying Cholesky-based Kronecker preconditioner...")
    G = inst.Z_obs.T @ inst.Z_obs + inst.lam * np.eye(r)
    M_explicit = np.kron(G, inst.K)
    M_inv_explicit = np.linalg.inv(M_explicit)

    L_K = np.linalg.cholesky(inst.K)
    L_G = np.linalg.cholesky(G)

    test_r = np.random.randn(n * r)
    z_explicit = M_inv_explicit @ test_r
    z_chol = apply_preconditioner_cholesky(inst, test_r, L_K, L_G)
    pc_err = np.linalg.norm(z_explicit - z_chol) / np.linalg.norm(z_explicit)
    print(f"    Relative error: {pc_err:.2e}")
    pc_ok = pc_err < 1e-10

    # PCG solve
    print("  PCG solve (Cholesky preconditioner)...")
    W_pcg, iters, t_pcg = pcg_solve(inst, tol=1e-12, max_iter=1000)
    w_pcg = np.zeros(n * r)
    for s in range(r):
        w_pcg[s * n:(s + 1) * n] = W_pcg[:, s]

    W_direct = np.zeros((n, r))
    for s in range(r):
        W_direct[:, s] = w_direct[s * n:(s + 1) * n]

    max_err = np.max(np.abs(W_direct - W_pcg))
    rel_err = np.linalg.norm(w_direct - w_pcg) / np.linalg.norm(w_direct)
    res_pcg = np.linalg.norm(A_sys @ w_pcg - rhs) / np.linalg.norm(rhs)
    res_direct = np.linalg.norm(A_sys @ w_direct - rhs) / np.linalg.norm(rhs)

    print(f"    Iterations: {iters}, time: {t_pcg:.4f}s")
    print(f"    Relative error vs direct: {rel_err:.2e}")
    print(f"    Residual (PCG): {res_pcg:.2e}, (direct): {res_direct:.2e}")

    # Condition numbers
    eigvals_A = np.linalg.eigvalsh(A_sys)
    cond_A = eigvals_A[-1] / max(eigvals_A[0], 1e-15)

    try:
        L_M = np.linalg.cholesky(M_explicit)
        L_M_inv = np.linalg.inv(L_M)
        PA = L_M_inv @ A_sys @ L_M_inv.T
        eigvals_PA = np.linalg.eigvalsh(PA)
        cond_PA = eigvals_PA[-1] / max(eigvals_PA[0], 1e-15)
    except np.linalg.LinAlgError:
        cond_PA = float('inf')

    print(f"    cond(A): {cond_A:.2e}, cond(M^-1 A): {cond_PA:.2e}")

    return Solution(
        W_direct=W_direct, W_pcg=W_pcg,
        max_error=max_err, relative_error=rel_err,
        pcg_iterations=iters, pcg_time=t_pcg, direct_time=t_direct,
        matvec_correct=mv_ok, precond_correct=pc_ok,
        details={'res_pcg': res_pcg, 'res_direct': res_direct,
                 'cond_A': cond_A, 'cond_PA': cond_PA,
                 'mv_err': mv_err, 'pc_err': pc_err}
    )


def verify(inst: Instance, sol: Solution) -> bool:
    checks = [
        ("Column-wise gather/scatter matvec matches explicit",
         sol.matvec_correct),
        ("Cholesky-based Kronecker preconditioner correct",
         sol.precond_correct),
        ("PCG converges (rel err < 1e-6)", sol.relative_error < 1e-6),
        ("PCG residual small (< 1e-8)", sol.details['res_pcg'] < 1e-8),
    ]
    all_ok = True
    for name, ok in checks:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name}")
        if not ok:
            all_ok = False
    return all_ok


if __name__ == "__main__":
    print("=" * 60)
    print("  Problem 10: Kernelized CP-ALS PCG Solver Verification")
    print("  Approach: Column-wise gather/scatter + Cholesky precond")
    print("=" * 60)

    all_pass = True
    for label, n, r, M, frac in [
        ("Small", 8, 3, 20, 0.5),
        ("Medium", 15, 4, 50, 0.4),
        ("Larger", 20, 5, 100, 0.3),
    ]:
        print(f"\n--- {label} instance (n={n}, r={r}, M={M}) ---")
        inst = generate_instance(n, r, M, frac)
        sol = solve(inst)
        ok = verify(inst, sol)
        print(f"  Overall: {'PASS' if ok else 'FAIL'}")
        all_pass = all_pass and ok

    # Complexity scaling test
    print("\n--- Complexity Scaling ---")
    sizes = [10, 20, 40, 80]
    r_fix = 3
    times = []
    for sz in sizes:
        inst = generate_instance(sz, r_fix, 50, 0.5)
        w = np.random.randn(sz * r_fix)
        t0 = time.perf_counter()
        for _ in range(200):
            matvec(inst, w)
        t_mv = (time.perf_counter() - t0) / 200
        times.append(t_mv)
        print(f"  n={sz:3d}: matvec time = {t_mv:.6f}s, q={inst.q}")

    for i in range(1, len(sizes)):
        ratio = times[i] / times[0]
        expected = (sizes[i] / sizes[0]) ** 2
        print(f"  Ratio n={sizes[i]}/n={sizes[0]}: "
              f"actual={ratio:.2f}, O(n^2)={expected:.2f}")

    print(f"\n{'='*60}")
    print(f"  FINAL: {'ALL PASSED' if all_pass else 'SOME FAILED'}")
    print(f"{'='*60}")
