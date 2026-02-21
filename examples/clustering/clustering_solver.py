#!/usr/bin/env python3
"""Customer segmentation via clustering.

Solves a customer segmentation problem using three complementary methods:
  1. K-Means (k=3) with elbow analysis
  2. DBSCAN with k-distance heuristic for eps selection
  3. Gaussian Mixture Model (GMM, 3 components)

Verification: silhouette thresholds, cluster count checks, BIC convergence,
cluster size reasonableness, profile distinguishability.
"""
from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.metrics import silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger

log = PolyaLogger()


# --- Data Model ---

FEATURES = ["annual_spending", "purchase_frequency", "avg_order_value",
            "days_since_last_purchase"]


@dataclass(frozen=True)
class Instance:
    """Customer segmentation instance."""
    data: pd.DataFrame          # raw customer feature matrix
    n_customers: int            # number of customers
    n_features: int             # number of features
    feature_names: tuple[str, ...]  # column names
    seed: int = 42


@dataclass
class Solution:
    """Clustering solution with multi-method comparison."""
    # Elbow analysis
    elbow_inertias: list[float] = field(default_factory=list)

    # K-Means results
    kmeans_labels: list[int] = field(default_factory=list)
    kmeans_centroids: list[list[float]] = field(default_factory=list)
    kmeans_silhouette: float = 0.0
    kmeans_inertia: float = 0.0

    # DBSCAN results
    dbscan_labels: list[int] = field(default_factory=list)
    dbscan_n_clusters: int = 0
    dbscan_n_noise: int = 0
    dbscan_silhouette: float = 0.0
    dbscan_eps: float = 0.0

    # GMM results
    gmm_labels: list[int] = field(default_factory=list)
    gmm_bic: float = 0.0
    gmm_aic: float = 0.0
    gmm_silhouette: float = 0.0

    # Comparison
    best_method: str = ""

    # Cluster profiles (best method): {cluster_id: {feature: mean_value}}
    cluster_profiles: dict = field(default_factory=dict)

    # Metadata
    algorithm: str = ""
    time_seconds: float = 0.0

    # Verification
    verification: dict = field(default_factory=dict)


# --- Data Generation ---

def generate_instance(seed: int = 42) -> Instance:
    """Generate synthetic customer purchasing data with 3 natural clusters.

    Cluster 1 (High Value):  ~150 customers -- high spending, high frequency,
                             high avg order value, low recency.
    Cluster 2 (Moderate):    ~200 customers -- medium spending, medium frequency,
                             medium avg order value, medium recency.
    Cluster 3 (At Risk):     ~150 customers -- low spending, low frequency,
                             low avg order value, high recency.
    """
    rng = np.random.default_rng(seed)

    # Cluster 1: High Value (~150 customers)
    n1 = 150
    c1_spending = rng.normal(12000, 2000, n1)
    c1_frequency = rng.normal(48, 8, n1)
    c1_order_val = rng.normal(250, 40, n1)
    c1_recency = rng.normal(10, 5, n1)

    # Cluster 2: Moderate (~200 customers)
    n2 = 200
    c2_spending = rng.normal(5000, 1500, n2)
    c2_frequency = rng.normal(20, 6, n2)
    c2_order_val = rng.normal(150, 30, n2)
    c2_recency = rng.normal(45, 15, n2)

    # Cluster 3: At Risk (~150 customers)
    n3 = 150
    c3_spending = rng.normal(1500, 800, n3)
    c3_frequency = rng.normal(5, 3, n3)
    c3_order_val = rng.normal(80, 25, n3)
    c3_recency = rng.normal(120, 30, n3)

    # Concatenate and ensure non-negative values
    spending = np.concatenate([c1_spending, c2_spending, c3_spending])
    frequency = np.concatenate([c1_frequency, c2_frequency, c3_frequency])
    order_val = np.concatenate([c1_order_val, c2_order_val, c3_order_val])
    recency = np.concatenate([c1_recency, c2_recency, c3_recency])

    spending = np.maximum(spending, 50.0)
    frequency = np.maximum(frequency, 1.0)
    order_val = np.maximum(order_val, 10.0)
    recency = np.maximum(recency, 1.0)

    df = pd.DataFrame({
        "annual_spending": spending,
        "purchase_frequency": frequency,
        "avg_order_value": order_val,
        "days_since_last_purchase": recency,
    })

    return Instance(
        data=df,
        n_customers=len(df),
        n_features=len(FEATURES),
        feature_names=tuple(FEATURES),
        seed=seed,
    )


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Run full clustering pipeline: scale, elbow, K-Means, DBSCAN, GMM."""
    t0 = time.perf_counter()

    X_raw = instance.data[list(instance.feature_names)].values
    scaler = StandardScaler()
    X = scaler.fit_transform(X_raw)

    # --- 1. Elbow analysis (K-Means for k=2..8) ---
    elbow_inertias: list[float] = []
    for k in range(2, 9):
        km = KMeans(n_clusters=k, random_state=instance.seed, n_init=10)
        km.fit(X)
        elbow_inertias.append(float(km.inertia_))

    # --- 2. K-Means (k=3) ---
    km3 = KMeans(n_clusters=3, random_state=instance.seed, n_init=10)
    km3_labels = km3.fit_predict(X)
    km3_centroids = km3.cluster_centers_.tolist()
    km3_sil = float(silhouette_score(X, km3_labels))
    km3_inertia = float(km3.inertia_)

    # --- 3. DBSCAN (eps via k-distance heuristic) ---
    k_neighbors = 5
    nn = NearestNeighbors(n_neighbors=k_neighbors)
    nn.fit(X)
    distances, _ = nn.kneighbors(X)
    k_dists = np.sort(distances[:, k_neighbors - 1])

    # Find the knee using the maximum-distance-to-line method on the sorted
    # k-distance curve.  Draw a line from the first to the last point; the
    # knee is where the perpendicular distance to that line is greatest.
    n_pts = len(k_dists)
    line_start = np.array([0.0, k_dists[0]])
    line_end = np.array([float(n_pts - 1), k_dists[-1]])
    line_vec = line_end - line_start
    line_len = np.linalg.norm(line_vec)
    line_unit = line_vec / line_len

    perp_dists = np.empty(n_pts)
    for pi in range(n_pts):
        point = np.array([float(pi), k_dists[pi]])
        vec = point - line_start
        proj = np.dot(vec, line_unit)
        perp_dists[pi] = np.sqrt(max(np.dot(vec, vec) - proj * proj, 0.0))

    knee_idx = int(np.argmax(perp_dists))
    eps_value = float(k_dists[knee_idx])
    # Ensure eps is reasonable (not too small, not too large)
    eps_value = max(eps_value, 0.3)

    db = DBSCAN(eps=eps_value, min_samples=k_neighbors)
    db_labels = db.fit_predict(X)
    db_n_clusters = len(set(db_labels)) - (1 if -1 in db_labels else 0)
    db_n_noise = int(np.sum(db_labels == -1))

    # Silhouette only defined when >= 2 clusters and not all noise
    if db_n_clusters >= 2 and db_n_noise < len(db_labels):
        mask = db_labels != -1
        if len(set(db_labels[mask])) >= 2:
            db_sil = float(silhouette_score(X[mask], db_labels[mask]))
        else:
            db_sil = -1.0
    else:
        db_sil = -1.0

    # --- 4. GMM (n_components=3) ---
    gmm = GaussianMixture(n_components=3, random_state=instance.seed,
                          covariance_type="full", max_iter=200)
    gmm_labels = gmm.fit_predict(X)
    gmm_bic = float(gmm.bic(X))
    gmm_aic = float(gmm.aic(X))
    gmm_sil = float(silhouette_score(X, gmm_labels))

    # --- 5. Compare methods by silhouette score ---
    scores = {
        "K-Means": km3_sil,
        "DBSCAN": db_sil,
        "GMM": gmm_sil,
    }
    best_method = max(scores, key=lambda m: scores[m])

    # --- 6. Cluster profiles (best method, in original feature space) ---
    best_labels_map = {
        "K-Means": km3_labels,
        "DBSCAN": db_labels,
        "GMM": gmm_labels,
    }
    best_labels = best_labels_map[best_method]
    profiles: dict[str, dict[str, float]] = {}
    for cid in sorted(set(best_labels)):
        if cid == -1:
            continue  # skip DBSCAN noise
        mask = best_labels == cid
        cluster_data = instance.data[list(instance.feature_names)].values[mask]
        means = {feat: float(np.mean(cluster_data[:, i]))
                 for i, feat in enumerate(instance.feature_names)}
        profiles[str(cid)] = means

    elapsed = time.perf_counter() - t0

    sol = Solution(
        elbow_inertias=elbow_inertias,
        kmeans_labels=km3_labels.tolist(),
        kmeans_centroids=km3_centroids,
        kmeans_silhouette=km3_sil,
        kmeans_inertia=km3_inertia,
        dbscan_labels=db_labels.tolist(),
        dbscan_n_clusters=db_n_clusters,
        dbscan_n_noise=db_n_noise,
        dbscan_silhouette=db_sil,
        dbscan_eps=eps_value,
        gmm_labels=gmm_labels.tolist(),
        gmm_bic=gmm_bic,
        gmm_aic=gmm_aic,
        gmm_silhouette=gmm_sil,
        best_method=best_method,
        cluster_profiles=profiles,
        algorithm="K-Means + DBSCAN + GMM",
        time_seconds=elapsed,
    )

    # Independent verification
    sol.verification = verify(instance, sol)

    return sol


# --- Verification (independent of solver) ---

def verify(instance: Instance, sol: Solution) -> dict:
    """Independently verify clustering quality.

    Seven checks:
      1. K-Means silhouette > 0.4
      2. K-Means found exactly 3 clusters
      3. DBSCAN found between 2 and 5 clusters
      4. GMM BIC is finite (model converged)
      5. No cluster has fewer than 20 points (best method)
      6. At least one feature has different means across clusters
         (max_mean - min_mean > 1.0 in standardized space)
      7. All above pass
    """
    checks: dict = {}

    # Re-scale data independently for check 6
    X_raw = instance.data[list(instance.feature_names)].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    # Check 1: K-Means silhouette > 0.4
    # Recompute independently: fit a fresh K-Means and compute silhouette
    km_verify = KMeans(n_clusters=3, random_state=instance.seed, n_init=10)
    km_verify_labels = km_verify.fit_predict(X_scaled)
    km_verify_sil = float(silhouette_score(X_scaled, km_verify_labels))
    checks["kmeans_silhouette_gt_04"] = km_verify_sil > 0.4

    # Check 2: K-Means found exactly 3 clusters (since we set k=3)
    n_unique_km = len(set(km_verify_labels))
    checks["kmeans_found_3_clusters"] = n_unique_km == 3

    # Check 3: DBSCAN found between 2 and 5 clusters
    # Recompute DBSCAN independently with the same eps
    db_verify = DBSCAN(eps=sol.dbscan_eps, min_samples=5)
    db_verify_labels = db_verify.fit_predict(X_scaled)
    db_verify_n_clusters = len(set(db_verify_labels)) - (
        1 if -1 in db_verify_labels else 0)
    checks["dbscan_found_2_to_5_clusters"] = 2 <= db_verify_n_clusters <= 5

    # Check 4: GMM BIC is finite (model converged)
    checks["gmm_bic_finite"] = bool(np.isfinite(sol.gmm_bic))

    # Check 5: No cluster has fewer than 20 points (best method)
    best_labels = np.array(sol.kmeans_labels if sol.best_method == "K-Means"
                           else sol.dbscan_labels if sol.best_method == "DBSCAN"
                           else sol.gmm_labels)
    cluster_ids = set(best_labels)
    cluster_ids.discard(-1)  # exclude DBSCAN noise
    min_cluster_size = min(
        int(np.sum(best_labels == cid)) for cid in cluster_ids
    ) if cluster_ids else 0
    checks["cluster_sizes_reasonable"] = min_cluster_size >= 20

    # Check 6: At least one feature has different means across clusters
    # (max_mean - min_mean > 1.0 in standardized space)
    distinguishable = False
    for feat_idx in range(instance.n_features):
        cluster_means = []
        for cid in sorted(cluster_ids):
            mask = best_labels == cid
            cluster_means.append(float(np.mean(X_scaled[mask, feat_idx])))
        if cluster_means:
            spread = max(cluster_means) - min(cluster_means)
            if spread > 1.0:
                distinguishable = True
                break
    checks["profiles_distinguishable"] = distinguishable

    # Check 7: All above pass
    checks["all_passed"] = all(
        v for k, v in checks.items() if k != "all_passed"
    )

    return checks


# --- Main ---

if __name__ == "__main__":
    instance = generate_instance(seed=42)
    sol = solve(instance)

    # === Phase 1: Instance Report ===
    log.header("CUSTOMER SEGMENTATION VIA CLUSTERING")

    log.section("PHASE 1: INSTANCE")
    log.metric("Customers", str(instance.n_customers), tag="DATA")
    log.metric("Features", ", ".join(instance.feature_names), tag="DATA")
    log.metric("Seed", str(instance.seed), tag="DATA")
    log.blank()

    # Summary statistics
    log.step("Feature Summary (raw)")
    for feat in instance.feature_names:
        vals = instance.data[feat]
        log.metric(feat,
                   "mean={:.1f}  std={:.1f}  min={:.1f}  max={:.1f}".format(
                       vals.mean(), vals.std(), vals.min(), vals.max()),
                   tag="STATS")
    log.blank()

    # === Phase 2: Solve ===
    log.section("PHASE 2: SOLVE")

    log.step("Elbow Analysis (k=2..8)")
    for k_idx, inertia in enumerate(sol.elbow_inertias, start=2):
        marker = " <-- chosen" if k_idx == 3 else ""
        log.metric("k={}".format(k_idx), "inertia={:.1f}{}".format(
            inertia, marker), tag="SOLVE")
    log.blank()

    log.step("K-Means (k=3)")
    log.metric("Silhouette", "{:.4f}".format(sol.kmeans_silhouette), tag="STATS")
    log.metric("Inertia", "{:.1f}".format(sol.kmeans_inertia), tag="STATS")
    for i, centroid in enumerate(sol.kmeans_centroids):
        log.metric("Centroid {}".format(i),
                   "[" + ", ".join("{:.3f}".format(c) for c in centroid) + "]",
                   tag="RESULT")
    km_counts = np.bincount(sol.kmeans_labels)
    log.metric("Cluster sizes", ", ".join(str(c) for c in km_counts), tag="RESULT")
    log.blank()

    log.step("DBSCAN (eps={:.3f})".format(sol.dbscan_eps))
    log.metric("Clusters found", str(sol.dbscan_n_clusters), tag="RESULT")
    log.metric("Noise points", str(sol.dbscan_n_noise), tag="RESULT")
    log.metric("Silhouette", "{:.4f}".format(sol.dbscan_silhouette)
               if sol.dbscan_silhouette > -1.0 else "N/A (< 2 clusters)",
               tag="STATS")
    log.blank()

    log.step("GMM (n_components=3)")
    log.metric("Silhouette", "{:.4f}".format(sol.gmm_silhouette), tag="STATS")
    log.metric("BIC", "{:.1f}".format(sol.gmm_bic), tag="STATS")
    log.metric("AIC", "{:.1f}".format(sol.gmm_aic), tag="STATS")
    log.blank()

    # === Phase 3: Interpret ===
    log.section("PHASE 3: INTERPRET")

    log.step("Method Comparison (silhouette score)")
    methods = [
        ("K-Means", sol.kmeans_silhouette),
        ("DBSCAN", sol.dbscan_silhouette),
        ("GMM", sol.gmm_silhouette),
    ]
    for name, sil in methods:
        marker = " <-- best" if name == sol.best_method else ""
        if sil > -1.0:
            log.bar("{:<10}".format(name), max(sil, 0.0), tag="RESULT",
                    marker=" {:.4f}{}".format(sil, marker))
        else:
            log.metric(name, "N/A{}".format(marker), tag="RESULT")
    log.metric("Best method", sol.best_method, tag="RECOMMEND")
    log.blank()

    log.step("Cluster Profiles ({})".format(sol.best_method))
    header_fmt = "{:<12}" + "".join("{:>24}" for _ in instance.feature_names)
    log.table_row(header_fmt.format("Cluster", *instance.feature_names),
                  tag="TABLE")
    log.table_row("-" * (12 + 24 * len(instance.feature_names)), tag="TABLE")
    for cid, profile in sorted(sol.cluster_profiles.items()):
        vals = [profile[f] for f in instance.feature_names]
        row = "{:<12}".format("Cluster " + cid)
        row += "".join("{:>24.1f}".format(v) for v in vals)
        log.table_row(row, tag="TABLE")
    log.blank()

    # === Phase 4: Verify ===
    log.section("PHASE 4: VERIFY")
    for name, passed in sol.verification.items():
        log.check(name, passed, tag="VERIFY")
    log.blank()

    log.metric("Algorithm", sol.algorithm, tag="SOLVE")
    log.metric("Time", "{:.4f}s".format(sol.time_seconds), tag="TIMING")
    log.divider(style="thick")

    # Save JSON
    output = {
        "instance": {
            "n_customers": instance.n_customers,
            "n_features": instance.n_features,
            "feature_names": list(instance.feature_names),
            "seed": instance.seed,
        },
        "elbow_analysis": {
            "k_range": list(range(2, 9)),
            "inertias": sol.elbow_inertias,
        },
        "kmeans": {
            "k": 3,
            "labels": sol.kmeans_labels,
            "centroids": sol.kmeans_centroids,
            "silhouette": sol.kmeans_silhouette,
            "inertia": sol.kmeans_inertia,
        },
        "dbscan": {
            "eps": sol.dbscan_eps,
            "labels": sol.dbscan_labels,
            "n_clusters": sol.dbscan_n_clusters,
            "n_noise": sol.dbscan_n_noise,
            "silhouette": sol.dbscan_silhouette,
        },
        "gmm": {
            "n_components": 3,
            "labels": sol.gmm_labels,
            "bic": sol.gmm_bic,
            "aic": sol.gmm_aic,
            "silhouette": sol.gmm_silhouette,
        },
        "best_method": sol.best_method,
        "cluster_profiles": sol.cluster_profiles,
        "verification": sol.verification,
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
    }
    with open(Path(__file__).resolve().parent / "solution.json", "w") as f:
        json.dump(output, f, indent=2, default=str)
    log.success("Solution data saved to: solution.json", tag="SAVE")
    log.divider(style="thick")
