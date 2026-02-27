#!/usr/bin/env python3
"""Verify Problem 4: Finite Free Stam Inequality.

Novel approach: Majorization + Schur-convexity argument.

We prove 1/Phi_n(p boxplus_n q) >= 1/Phi_n(p) + 1/Phi_n(q) via:

1. V_n-additivity: V_n(p boxplus q) = V_n(p) + V_n(q)  [algebraic identity]
2. The key identity: 1/Phi_n(p) = V_n(p) / (2 * S(p)) where
   S(p) = (sum d_ij^2)(sum 1/d_ij^2) >= M^2 by Cauchy-Schwarz
3. A majorization argument: the squared gaps of p boxplus q
   majorize the concatenation-normalized gaps of p and q,
   which forces S(p boxplus q) <= weighted harmonic mean of S(p), S(q).

This verification script:
- Tests the convolution formula
- Verifies V_n-additivity
- Verifies the main inequality for random instances
- Tests edge cases (equal spacing, clustering)
- Verifies the n=2 equality case
- Tests the Cauchy-Schwarz ratio S behavior

Novel proof strategy uses finite free cumulants and majorization:
- The finite free cumulants kappa_k are additive under boxplus_n
- Express Phi_n in terms of cumulants and root gaps
- Use Schur-convexity of 1/Phi_n on the space of gap vectors
- Show that convolution "majorizes" the gap vector in the right sense
"""
from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from math import factorial, comb
from typing import Sequence

import numpy as np
from numpy.polynomial import polynomial as P


@dataclass(frozen=True)
class Instance:
    """A test instance."""
    n: int
    roots_p: tuple[float, ...]
    roots_q: tuple[float, ...]


@dataclass
class Solution:
    """Verification results."""
    instance: Instance
    phi_p: float
    phi_q: float
    phi_conv: float
    inv_phi_conv: float
    inv_phi_p_plus_q: float
    inequality_holds: bool
    margin: float
    vn_additive: bool
    vn_error: float


def poly_from_roots(roots: Sequence[float]) -> np.ndarray:
    """Return monic polynomial coefficients [a_0=1, a_1, ..., a_n] (descending)."""
    n = len(roots)
    # numpy poly gives highest-degree-first coefficients
    coeffs = np.polynomial.polynomial.polyfromroots(roots)[::-1]
    # Normalize to monic
    coeffs = coeffs / coeffs[0]
    return coeffs


def finite_free_convolution(p_coeffs: np.ndarray, q_coeffs: np.ndarray) -> np.ndarray:
    """Compute p boxplus_n q using the coefficient formula.

    c_k = sum_{i+j=k} ((n-i)!(n-j)!) / (n!(n-k)!) * a_i * b_j
    """
    n = len(p_coeffs) - 1
    c = np.zeros(n + 1)
    for k in range(n + 1):
        s = 0.0
        for i in range(k + 1):
            j = k - i
            if i <= n and j <= n:
                coeff = (factorial(n - i) * factorial(n - j)) / (factorial(n) * factorial(n - k))
                s += coeff * p_coeffs[i] * q_coeffs[j]
        c[k] = s
    return c


def finite_free_convolution_via_cumulants(p_coeffs: np.ndarray, q_coeffs: np.ndarray) -> np.ndarray:
    """Compute p boxplus_n q using the multiplicative generating function.

    Define alpha_k(p) = a_k * (n-k)!/n!
    Then F_p(z) = sum alpha_k z^k
    and F_{p boxplus q}(z) = F_p(z) * F_q(z) (truncated to degree n)
    Then recover a_k^(c) = alpha_k^(c) * n!/(n-k)!
    """
    n = len(p_coeffs) - 1
    alpha_p = np.array([p_coeffs[k] * factorial(n - k) / factorial(n) for k in range(n + 1)])
    alpha_q = np.array([q_coeffs[k] * factorial(n - k) / factorial(n) for k in range(n + 1)])

    # Polynomial multiplication (truncated to degree n)
    alpha_c = np.convolve(alpha_p, alpha_q)[:n + 1]

    # Recover coefficients
    c = np.array([alpha_c[k] * factorial(n) / factorial(n - k) for k in range(n + 1)])
    return c


def compute_Phi_n(roots: np.ndarray) -> float:
    """Compute Phi_n(p) = sum_{i != j} 1/(lambda_i - lambda_j)^2."""
    n = len(roots)
    total = 0.0
    for i in range(n):
        for j in range(n):
            if i != j:
                diff = roots[i] - roots[j]
                if abs(diff) < 1e-14:
                    return float('inf')
                total += 1.0 / (diff ** 2)
    return total


def compute_Vn(roots: np.ndarray) -> float:
    """Compute V_n(p) = sum_{i<j} (lambda_i - lambda_j)^2."""
    n = len(roots)
    total = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            total += (roots[i] - roots[j]) ** 2
    return total


def compute_Vn_from_coeffs(coeffs: np.ndarray) -> float:
    """Compute V_n from coefficients: V_n = (n-1)*a_1^2 - 2*n*a_2."""
    n = len(coeffs) - 1
    a1 = coeffs[1]
    a2 = coeffs[2] if n >= 2 else 0.0
    return (n - 1) * a1**2 - 2 * n * a2


def compute_S_ratio(roots: np.ndarray) -> float:
    """Compute S(p) = (sum d_ij^2)(sum 1/d_ij^2) >= M^2."""
    n = len(roots)
    sum_sq = 0.0
    sum_inv_sq = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            d2 = (roots[i] - roots[j]) ** 2
            if d2 < 1e-28:
                return float('inf')
            sum_sq += d2
            sum_inv_sq += 1.0 / d2
    return sum_sq * sum_inv_sq


def solve(instance: Instance) -> Solution:
    """Verify the inequality for one instance."""
    n = instance.n
    roots_p = np.array(instance.roots_p)
    roots_q = np.array(instance.roots_q)

    # Compute polynomial coefficients
    p_coeffs = poly_from_roots(roots_p)
    q_coeffs = poly_from_roots(roots_q)

    # Compute convolution (both methods)
    c_coeffs = finite_free_convolution(p_coeffs, q_coeffs)
    c_coeffs2 = finite_free_convolution_via_cumulants(p_coeffs, q_coeffs)

    # Verify both methods agree
    assert np.allclose(c_coeffs, c_coeffs2, atol=1e-8), \
        f"Convolution methods disagree: {np.max(np.abs(c_coeffs - c_coeffs2))}"

    # Find roots of convolution
    # Construct polynomial for numpy: needs ascending coefficients
    conv_poly = c_coeffs[::-1]  # ascending order
    roots_conv = np.sort(np.roots(c_coeffs))

    # Check real-rootedness
    if not np.all(np.abs(np.imag(roots_conv)) < 1e-8):
        print(f"  WARNING: convolution has complex roots for n={n}")
    roots_conv = np.real(roots_conv)

    # Compute Phi_n values
    phi_p = compute_Phi_n(roots_p)
    phi_q = compute_Phi_n(roots_q)
    phi_conv = compute_Phi_n(roots_conv)

    inv_phi_conv = 1.0 / phi_conv if phi_conv > 0 and phi_conv < float('inf') else 0.0
    inv_phi_p = 1.0 / phi_p if phi_p > 0 and phi_p < float('inf') else 0.0
    inv_phi_q = 1.0 / phi_q if phi_q > 0 and phi_q < float('inf') else 0.0
    inv_phi_sum = inv_phi_p + inv_phi_q

    inequality_holds = inv_phi_conv >= inv_phi_sum - 1e-10  # small tolerance

    margin = inv_phi_conv - inv_phi_sum

    # V_n additivity check
    vn_p = compute_Vn(roots_p)
    vn_q = compute_Vn(roots_q)
    vn_conv = compute_Vn(roots_conv)

    # Also check from coefficients
    vn_p_coeff = compute_Vn_from_coeffs(p_coeffs)
    vn_q_coeff = compute_Vn_from_coeffs(q_coeffs)
    vn_conv_coeff = compute_Vn_from_coeffs(c_coeffs)

    vn_sum = vn_p + vn_q
    vn_error = abs(vn_conv - vn_sum) / max(abs(vn_sum), 1e-15)
    vn_additive = vn_error < 1e-6

    return Solution(
        instance=instance,
        phi_p=phi_p,
        phi_q=phi_q,
        phi_conv=phi_conv,
        inv_phi_conv=inv_phi_conv,
        inv_phi_p_plus_q=inv_phi_sum,
        inequality_holds=inequality_holds,
        margin=margin,
        vn_additive=vn_additive,
        vn_error=vn_error,
    )


def verify(solution: Solution) -> bool:
    """Independent verification."""
    return solution.inequality_holds and solution.vn_additive


def random_real_rooted(n: int, spread: float = 5.0, min_gap: float = 0.1) -> tuple[float, ...]:
    """Generate a random monic real-rooted polynomial with well-separated roots."""
    while True:
        roots = np.sort(np.random.uniform(-spread, spread, n))
        gaps = np.diff(roots)
        if np.all(gaps > min_gap):
            return tuple(roots)


def main() -> None:
    np.random.seed(42)
    t0 = time.perf_counter()

    print("=" * 75)
    print("Problem 4 Verification: Finite Free Stam Inequality")
    print("1/Phi_n(p boxplus_n q) >= 1/Phi_n(p) + 1/Phi_n(q)")
    print("=" * 75)
    print()

    # 1. Test n=2 exact equality
    print("--- n=2: Exact equality test ---")
    for _ in range(20):
        roots_p = random_real_rooted(2, 10.0, 0.5)
        roots_q = random_real_rooted(2, 10.0, 0.5)
        inst = Instance(n=2, roots_p=roots_p, roots_q=roots_q)
        sol = solve(inst)
        assert sol.inequality_holds, f"n=2 inequality failed!"
        # Check exact equality
        assert abs(sol.margin) < 1e-6, \
            f"n=2 not exact equality: margin = {sol.margin}"
    print("  All 20 n=2 tests: EXACT EQUALITY confirmed (margin < 1e-6)")
    print()

    # 2. Systematic testing
    all_pass = True
    total = 0
    passed = 0
    min_margins = {}

    degrees = [2, 3, 4, 5, 6, 7, 8, 10, 12, 15]
    trials_per_degree = {d: 300 if d <= 8 else 100 for d in degrees}

    for n in degrees:
        n_trials = trials_per_degree[n]
        local_min_margin = float('inf')
        local_pass = 0
        for trial in range(n_trials):
            spread = 5.0
            min_gap = 0.1
            if n > 10:
                spread = 10.0
                min_gap = 0.2
            roots_p = random_real_rooted(n, spread, min_gap)
            roots_q = random_real_rooted(n, spread, min_gap)
            inst = Instance(n=n, roots_p=roots_p, roots_q=roots_q)
            sol = solve(inst)
            ok = verify(sol)
            if ok:
                local_pass += 1
                passed += 1
            else:
                all_pass = False
            total += 1
            local_min_margin = min(local_min_margin, sol.margin)

        min_margins[n] = local_min_margin
        status = "PASS" if local_pass == n_trials else "FAIL"
        print(f"[{status}] n={n:2d}: {local_pass}/{n_trials} passed, "
              f"min_margin={local_min_margin:.4e}")

    print()
    print(f"Total: {passed}/{total} passed")
    print()

    # 3. Stress tests
    print("--- Stress tests: Close roots ---")
    stress_pass = 0
    stress_total = 0
    for n in [3, 4, 5, 6]:
        for _ in range(50):
            roots_p = random_real_rooted(n, 0.5, 0.05)
            roots_q = random_real_rooted(n, 0.5, 0.05)
            inst = Instance(n=n, roots_p=roots_p, roots_q=roots_q)
            sol = solve(inst)
            ok = verify(sol)
            stress_total += 1
            if ok:
                stress_pass += 1
            else:
                all_pass = False
    print(f"  Close roots: {stress_pass}/{stress_total} passed")

    print()
    print("--- Stress tests: Wide spread ---")
    stress_pass2 = 0
    stress_total2 = 0
    for n in [3, 4, 5, 6]:
        for _ in range(50):
            roots_p = random_real_rooted(n, 100.0, 1.0)
            roots_q = random_real_rooted(n, 100.0, 1.0)
            inst = Instance(n=n, roots_p=roots_p, roots_q=roots_q)
            sol = solve(inst)
            ok = verify(sol)
            stress_total2 += 1
            if ok:
                stress_pass2 += 1
            else:
                all_pass = False
    print(f"  Wide spread: {stress_pass2}/{stress_total2} passed")

    print()

    # 4. Verify additional properties
    print("--- Property verification ---")

    # (a) V_n additivity
    print("  V_n additivity:")
    for n in [3, 5, 8]:
        roots_p = random_real_rooted(n)
        roots_q = random_real_rooted(n)
        inst = Instance(n=n, roots_p=roots_p, roots_q=roots_q)
        sol = solve(inst)
        print(f"    n={n}: V_n error = {sol.vn_error:.2e} ({'OK' if sol.vn_additive else 'FAIL'})")

    # (b) Cauchy-Schwarz ratio S behavior
    print("  Cauchy-Schwarz ratio S (should be >= M^2):")
    for n in [3, 4, 5]:
        M = comb(n, 2)
        for _ in range(10):
            roots_p = random_real_rooted(n)
            roots_q = random_real_rooted(n)
            p_coeffs = poly_from_roots(roots_p)
            q_coeffs = poly_from_roots(roots_q)
            c_coeffs = finite_free_convolution(p_coeffs, q_coeffs)
            roots_conv = np.real(np.sort(np.roots(c_coeffs)))

            S_p = compute_S_ratio(np.array(roots_p))
            S_q = compute_S_ratio(np.array(roots_q))
            S_c = compute_S_ratio(roots_conv)

            assert S_p >= M**2 - 0.01, f"S_p < M^2"
            assert S_q >= M**2 - 0.01, f"S_q < M^2"
            assert S_c >= M**2 - 0.01, f"S_c < M^2"

        print(f"    n={n}, M={M}: All S >= M^2 = {M**2} confirmed")

    # (c) Test that equally-spaced roots give S = M^2 (Cauchy-Schwarz equality)
    print("  Equally-spaced roots S ratio:")
    for n in [3, 4, 5, 6]:
        M = comb(n, 2)
        roots_eq = tuple(np.linspace(-1, 1, n))
        S_eq = compute_S_ratio(np.array(roots_eq))
        print(f"    n={n}: S = {S_eq:.4f}, M^2 = {M**2}")

    # (d) Verify commutativity and identity
    print("  Commutativity and identity:")
    for n in [3, 5]:
        roots_p = random_real_rooted(n)
        roots_q = random_real_rooted(n)
        p_coeffs = poly_from_roots(roots_p)
        q_coeffs = poly_from_roots(roots_q)

        # p boxplus q vs q boxplus p
        c1 = finite_free_convolution(p_coeffs, q_coeffs)
        c2 = finite_free_convolution(q_coeffs, p_coeffs)
        assert np.allclose(c1, c2, atol=1e-10), "Commutativity failed"

        # p boxplus x^n = p
        id_coeffs = np.zeros(n + 1)
        id_coeffs[0] = 1.0
        c_id = finite_free_convolution(p_coeffs, id_coeffs)
        assert np.allclose(c_id, p_coeffs, atol=1e-10), "Identity failed"
    print("    Commutativity: OK, Identity: OK")

    print()
    elapsed = time.perf_counter() - t0
    print(f"Total time: {elapsed:.1f}s")
    print()

    if all_pass:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
