# Vendor Selection -- Cloud Infrastructure

**Domain**: Decision Analysis (MCDA)
**Algorithm**: AHP (Analytic Hierarchy Process) + TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)
**Key Concepts**: Pairwise comparison, consistency ratio, ideal/anti-ideal solutions, sensitivity analysis

## Problem

A company needs to select a cloud infrastructure vendor from 5 candidates (CloudPeak, NimbusForge, SkyGrid, DataSphere, CoreVault) evaluated across 4 criteria:

- **Cost** (25%) -- monthly spend in thousands; lower is better
- **Performance** (30%) -- throughput benchmark score; higher is better
- **Security** (25%) -- compliance/audit score; higher is better
- **Support** (20%) -- SLA response quality score; higher is better

Criteria weights are derived from expert pairwise comparisons using AHP with eigenvalue consistency checking. Final vendor ranking uses TOPSIS with sensitivity analysis to test ranking robustness under weight perturbation.

## Files

| File | Description |
|------|-------------|
| `vendor_solver.py` | AHP weight derivation + TOPSIS ranking + sensitivity analysis + weighted sum comparison |

## Requirements

```bash
pip install numpy
```

## Quick Run

```bash
python3 vendor_solver.py
```

## Expected Output

- AHP-derived criteria weights with consistency ratio (CR < 0.10)
- TOPSIS scores and ranking for all 5 vendors
- Weighted sum ranking for cross-validation
- Sensitivity analysis showing ranking stability under +/-10% weight perturbations
- Independent verification of all computations

## Algorithm

1. **AHP weight derivation**: Construct a 4x4 pairwise comparison matrix from expert judgments. Compute the principal eigenvector (power method) and normalize to obtain criteria weights. Verify consistency via the consistency ratio (CR = CI / RI where CI = (lambda_max - n) / (n - 1) and RI is the random index for matrix size n).

2. **TOPSIS ranking**: Normalize the 5x4 performance matrix using vector normalization. Construct the weighted normalized matrix. Identify positive-ideal (best per criterion) and negative-ideal (worst per criterion) solutions. Compute Euclidean distances to both ideals. Rank by relative closeness: C_i = D_i^- / (D_i^+ + D_i^-).

3. **Sensitivity analysis**: Perturb each weight by +/-10% (redistributing the delta proportionally across other criteria). Re-run TOPSIS for each perturbation. Flag any ranking changes.

4. **Cross-validation**: Compute simple weighted sum scores and compare the ranking against TOPSIS to check consistency.

## Key Concepts

- **AHP (Analytic Hierarchy Process)** -- structured method for deriving criterion weights from pairwise expert comparisons with built-in consistency checking
- **TOPSIS** -- distance-based MCDA method that ranks alternatives by proximity to the ideal solution and distance from the anti-ideal
- **Consistency ratio** -- AHP diagnostic ensuring pairwise judgments are logically coherent (CR < 0.10 required)
- **Vector normalization** -- dividing each column by its Euclidean norm to make criteria comparable
- **Ideal/anti-ideal solutions** -- best and worst achievable performance vectors used as reference points
- **Sensitivity analysis** -- testing whether the top-ranked vendor changes under plausible weight shifts
- **Benefit vs. cost criteria** -- TOPSIS treats "higher is better" and "lower is better" criteria differently when identifying ideal points
