#!/usr/bin/env python3
"""Verify the gap majorization bound for Problem 4.

Key claim (Lemma: Gap majorization under convolution):
  sum_{i<j} 1/c_{ij} <= sum_{i<j} 1/(a_{ij} + b_{ij})

where:
  a_{ij} = (lambda_j - lambda_i)^2  (squared gaps of p)
  b_{ij} = (mu_j - mu_i)^2          (squared gaps of q)
  c_{ij} = (rho_j - rho_i)^2        (squared gaps of p boxplus q)

This is the crucial novel claim that bridges the V_n-additivity
and harmonic mean superadditivity to give the full Stam inequality.
"""
from __future__ import annotations

import sys
from math import factorial
import numpy as np


def poly_from_roots(roots):
    coeffs = np.polynomial.polynomial.polyfromroots(roots)[::-1]
    return coeffs / coeffs[0]


def finite_free_convolution(p_coeffs, q_coeffs):
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


def random_real_rooted(n, spread=5.0, min_gap=0.1):
    while True:
        roots = np.sort(np.random.uniform(-spread, spread, n))
        if np.all(np.diff(roots) > min_gap):
            return roots


def test_gap_majorization(n, roots_p, roots_q):
    """Test the gap majorization bound for one instance."""
    p_coeffs = poly_from_roots(roots_p)
    q_coeffs = poly_from_roots(roots_q)
    c_coeffs = finite_free_convolution(p_coeffs, q_coeffs)

    roots_conv = np.sort(np.real(np.roots(c_coeffs)))

    # Compute squared gaps
    M = n * (n - 1) // 2
    a_vals = []  # squared gaps of p
    b_vals = []  # squared gaps of q
    c_vals = []  # squared gaps of conv

    for i in range(n):
        for j in range(i + 1, n):
            a_vals.append((roots_p[j] - roots_p[i])**2)
            b_vals.append((roots_q[j] - roots_q[i])**2)
            c_vals.append((roots_conv[j] - roots_conv[i])**2)

    a_vals = np.array(a_vals)
    b_vals = np.array(b_vals)
    c_vals = np.array(c_vals)

    # Check sum equality (V_n additivity)
    sum_c = np.sum(c_vals)
    sum_ab = np.sum(a_vals) + np.sum(b_vals)

    # Gap majorization: sum 1/c_m <= sum 1/(a_m + b_m)
    inv_c = np.sum(1.0 / c_vals)
    inv_ab = np.sum(1.0 / (a_vals + b_vals))

    gap_major_ok = inv_c <= inv_ab + 1e-8

    # Also verify the full Stam inequality
    phi_p = 2.0 * np.sum(1.0 / a_vals)
    phi_q = 2.0 * np.sum(1.0 / b_vals)
    phi_c = 2.0 * np.sum(1.0 / c_vals)

    stam_lhs = 1.0 / phi_c
    stam_rhs = 1.0 / phi_p + 1.0 / phi_q
    stam_ok = stam_lhs >= stam_rhs - 1e-10

    # Also verify superadditivity of HM for these specific sequences
    hm_ab = M / np.sum(1.0 / (a_vals + b_vals))
    hm_a = M / np.sum(1.0 / a_vals)
    hm_b = M / np.sum(1.0 / b_vals)
    hm_super_ok = hm_ab >= hm_a + hm_b - 1e-10

    return {
        'n': n,
        'vn_error': abs(sum_c - sum_ab) / max(sum_ab, 1e-15),
        'gap_major_ok': gap_major_ok,
        'gap_major_margin': inv_ab - inv_c,
        'hm_super_ok': hm_super_ok,
        'hm_super_margin': hm_ab - (hm_a + hm_b),
        'stam_ok': stam_ok,
        'stam_margin': stam_lhs - stam_rhs,
    }


def main():
    np.random.seed(42)

    print("=" * 75)
    print("Gap Majorization Bound Verification")
    print("sum 1/c_m <= sum 1/(a_m + b_m)")
    print("=" * 75)
    print()

    all_pass = True
    total = 0
    gap_pass = 0
    hm_pass = 0
    stam_pass = 0

    for n in [2, 3, 4, 5, 6, 7, 8, 10, 12, 15]:
        n_trials = 300 if n <= 8 else 100
        local_gap_pass = 0
        local_hm_pass = 0
        local_stam_pass = 0
        min_gap_margin = float('inf')
        min_hm_margin = float('inf')
        min_stam_margin = float('inf')

        for _ in range(n_trials):
            spread = 5.0 if n <= 10 else 10.0
            min_gap_val = 0.1 if n <= 10 else 0.2
            roots_p = random_real_rooted(n, spread, min_gap_val)
            roots_q = random_real_rooted(n, spread, min_gap_val)

            result = test_gap_majorization(n, roots_p, roots_q)
            total += 1

            if result['gap_major_ok']:
                local_gap_pass += 1
                gap_pass += 1
            else:
                all_pass = False

            if result['hm_super_ok']:
                local_hm_pass += 1
                hm_pass += 1

            if result['stam_ok']:
                local_stam_pass += 1
                stam_pass += 1

            min_gap_margin = min(min_gap_margin, result['gap_major_margin'])
            min_hm_margin = min(min_hm_margin, result['hm_super_margin'])
            min_stam_margin = min(min_stam_margin, result['stam_margin'])

        print(f"n={n:2d}: gap_major={local_gap_pass}/{n_trials} "
              f"(min_margin={min_gap_margin:.4e}), "
              f"HM_super={local_hm_pass}/{n_trials} "
              f"(min_margin={min_hm_margin:.4e}), "
              f"Stam={local_stam_pass}/{n_trials} "
              f"(min_margin={min_stam_margin:.4e})")

    print()
    print(f"Gap majorization: {gap_pass}/{total}")
    print(f"HM superadditive: {hm_pass}/{total}")
    print(f"Stam inequality:  {stam_pass}/{total}")
    print()

    if all_pass:
        print("ALL GAP MAJORIZATION TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
