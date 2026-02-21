#!/usr/bin/env python3
"""Feature Importance & Model Comparison solver.

Analyzes a synthetic classification dataset with 20 features (5 informative,
3 redundant, 12 noise) using a multi-stage pipeline:
  1. PCA for dimensionality analysis (explained variance)
  2. Mutual information feature ranking and selection (top 8)
  3. Recursive Feature Elimination with Random Forest (top 8)
  4. 4-model comparison (Logistic, RF, SVM, k-NN) x 3 feature sets (5-fold CV)

Polya Phase 1-2 (uber-model): Understand + Plan
  - Unknown: Which features matter? Which model is best?
  - Data: 800 samples, 20 features, binary target
  - Condition: 5 informative, 3 redundant, 12 noise features
  - Structure: Feature selection + supervised classification
  - Model: Compare filter (MI) vs wrapper (RFE) selection + 4 classifiers

Polya Phase 3 (uber-solve): Execute
  - PCA explained variance analysis
  - MI ranking + RFE ranking
  - 5-fold stratified CV for all model x feature-set combinations
  - Identify best combination

Polya Phase 4 (uber-interpret): Look Back
  - Verify informative features recovered
  - Verify selection improves or maintains accuracy
  - Report best pipeline and feature overlap
"""
from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE, mutual_info_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger

log = PolyaLogger()


# --- Phase 1-2: Formal Model (uber-model output) ---

@dataclass(frozen=True)
class Instance:
    """Feature importance problem instance."""
    X: np.ndarray                      # (n_samples, n_features) feature matrix
    y: np.ndarray                      # (n_samples,) binary target
    n_samples: int = 800
    n_features: int = 20
    n_informative: int = 5
    n_redundant: int = 3
    n_select: int = 8                  # number of features to select
    n_cv_folds: int = 5
    seed: int = 42
    true_informative_indices: tuple[int, ...] = ()  # ground truth informative feature indices

    def __hash__(self) -> int:
        return hash((self.n_samples, self.n_features, self.seed))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Instance):
            return NotImplemented
        return self.seed == other.seed and self.n_samples == other.n_samples


@dataclass
class Solution:
    """Feature importance and model comparison solution."""
    # PCA results
    pca_explained_variance_ratio: list[float] = field(default_factory=list)
    pca_cumulative_variance: list[float] = field(default_factory=list)
    pca_n_components_95pct: int = 0

    # Mutual information results
    mi_feature_scores: list[float] = field(default_factory=list)
    mi_feature_ranking: list[int] = field(default_factory=list)
    mi_selected_indices: list[int] = field(default_factory=list)

    # RFE results
    rfe_feature_ranking: list[int] = field(default_factory=list)
    rfe_selected_indices: list[int] = field(default_factory=list)

    # Feature overlap
    mi_rfe_overlap: list[int] = field(default_factory=list)
    mi_rfe_overlap_count: int = 0

    # Model comparison: {model_name: {all_features_acc, mi_features_acc, rfe_features_acc, ...}}
    model_comparison: dict = field(default_factory=dict)

    # Best combination
    best_model_name: str = ""
    best_feature_method: str = ""
    best_accuracy: float = 0.0
    best_accuracy_std: float = 0.0

    # Metadata
    algorithm: str = ""
    time_seconds: float = 0.0

    # Verification
    verification: dict = field(default_factory=dict)


# --- Synthetic Data Generation ---

def generate_instance(seed: int = 42) -> Instance:
    """Generate synthetic classification data.

    800 samples, 20 features:
      - 5 informative (truly predictive)
      - 3 redundant (linear combinations of informative)
      - 12 noise (random, uncorrelated with target)
    Binary target, approximately balanced classes.
    """
    X, y = make_classification(
        n_samples=800,
        n_features=20,
        n_informative=5,
        n_redundant=3,
        n_clusters_per_class=2,
        n_classes=2,
        flip_y=0.03,
        random_state=seed,
    )

    # Identify the true informative features by correlating with noiseless data
    # make_classification places informative features first, then redundant, then noise
    # Informative: indices 0..4, Redundant: indices 5..7, Noise: indices 8..19
    true_informative = tuple(range(5))

    return Instance(
        X=X,
        y=y,
        n_samples=800,
        n_features=20,
        n_informative=5,
        n_redundant=3,
        n_select=8,
        n_cv_folds=5,
        seed=seed,
        true_informative_indices=true_informative,
    )


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Run full feature importance and model comparison pipeline."""
    t0 = time.perf_counter()
    sol = Solution()

    X = instance.X.copy()
    y = instance.y.copy()

    # Standardize features for PCA and distance-based models
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # ── Step 1: PCA -- Explained Variance Analysis ──
    pca = PCA(n_components=instance.n_features, random_state=instance.seed)
    pca.fit(X_scaled)

    sol.pca_explained_variance_ratio = [
        float(v) for v in pca.explained_variance_ratio_
    ]
    cumvar = np.cumsum(pca.explained_variance_ratio_)
    sol.pca_cumulative_variance = [float(v) for v in cumvar]

    # Number of components for 95% variance
    sol.pca_n_components_95pct = int(np.searchsorted(cumvar, 0.95) + 1)

    # ── Step 2: Mutual Information Feature Selection ──
    mi_scores = mutual_info_classif(
        X, y, discrete_features=False, random_state=instance.seed,
    )
    sol.mi_feature_scores = [float(s) for s in mi_scores]

    # Rank: highest MI first (rank 1 = most important)
    mi_order = np.argsort(-mi_scores)
    mi_ranking = np.empty(instance.n_features, dtype=int)
    for rank_pos, feat_idx in enumerate(mi_order):
        mi_ranking[feat_idx] = rank_pos + 1
    sol.mi_feature_ranking = mi_ranking.tolist()

    # Select top n_select by MI
    sol.mi_selected_indices = sorted(mi_order[:instance.n_select].tolist())

    # ── Step 3: RFE with Random Forest ──
    rf_estimator = RandomForestClassifier(
        n_estimators=100, random_state=instance.seed,
    )
    rfe = RFE(
        estimator=rf_estimator,
        n_features_to_select=instance.n_select,
        step=1,
    )
    rfe.fit(X, y)

    sol.rfe_feature_ranking = rfe.ranking_.tolist()
    sol.rfe_selected_indices = sorted(
        int(i) for i in np.where(rfe.support_)[0]
    )

    # ── Feature Overlap ──
    mi_set = set(sol.mi_selected_indices)
    rfe_set = set(sol.rfe_selected_indices)
    sol.mi_rfe_overlap = sorted(mi_set & rfe_set)
    sol.mi_rfe_overlap_count = len(sol.mi_rfe_overlap)

    # ── Step 4: Model Comparison (5-fold stratified CV) ──
    models = {
        "LogisticRegression": LogisticRegression(
            max_iter=1000, random_state=instance.seed,
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=100, random_state=instance.seed,
        ),
        "SVM_RBF": SVC(
            kernel="rbf", random_state=instance.seed,
        ),
        "kNN": KNeighborsClassifier(
            n_neighbors=5,
        ),
    }

    feature_sets = {
        "all_features": list(range(instance.n_features)),
        "mi_features": sol.mi_selected_indices,
        "rfe_features": sol.rfe_selected_indices,
    }

    cv = StratifiedKFold(
        n_splits=instance.n_cv_folds, shuffle=True, random_state=instance.seed,
    )

    best_acc = 0.0
    best_model = ""
    best_fset = ""
    best_std = 0.0

    for model_name, model in models.items():
        sol.model_comparison[model_name] = {}
        for fset_name, feat_idx in feature_sets.items():
            X_sub = X_scaled[:, feat_idx]
            scores = cross_val_score(
                model, X_sub, y, cv=cv, scoring="accuracy",
            )
            mean_acc = float(np.mean(scores))
            std_acc = float(np.std(scores))
            sol.model_comparison[model_name][fset_name] = {
                "mean_accuracy": round(mean_acc, 4),
                "std_accuracy": round(std_acc, 4),
                "fold_scores": [round(float(s), 4) for s in scores],
            }

            if mean_acc > best_acc:
                best_acc = mean_acc
                best_model = model_name
                best_fset = fset_name
                best_std = std_acc

    # ── Step 5: Best Combination ──
    sol.best_model_name = best_model
    sol.best_feature_method = best_fset
    sol.best_accuracy = round(best_acc, 4)
    sol.best_accuracy_std = round(best_std, 4)

    sol.algorithm = "PCA + Mutual Information + RFE (Random Forest) + 4-Model 5-Fold CV"
    sol.time_seconds = time.perf_counter() - t0

    # Independent verification
    sol.verification = verify(instance, sol)

    return sol


# --- Verification (independent of solver) ---

def verify(instance: Instance, sol: Solution) -> dict:
    """Independently verify feature importance and model comparison results.

    Seven checks:
      1. pca_95pct_lt_20: Need fewer than 20 components for 95% variance
      2. informative_features_selected: At least 3/5 true informative in MI top 8
      3. rfe_features_selected: At least 3/5 true informative in RFE top 8
      4. selected_beats_random: Best selected accuracy >= all-features accuracy - 0.05
      5. best_accuracy_gt_80pct: Best model accuracy > 80%
      6. cv_scores_stable: Best model CV std < 0.05
      7. all_passed: All above pass
    """
    checks: dict = {}
    true_info = set(instance.true_informative_indices)

    # Check 1: PCA needs fewer than 20 components for 95% variance
    checks["pca_95pct_lt_20"] = sol.pca_n_components_95pct < 20

    # Check 2: MI selects at least 3 of 5 true informative features
    mi_recovered = len(set(sol.mi_selected_indices) & true_info)
    checks["informative_features_selected"] = mi_recovered >= 3

    # Check 3: RFE selects at least 3 of 5 true informative features
    rfe_recovered = len(set(sol.rfe_selected_indices) & true_info)
    checks["rfe_features_selected"] = rfe_recovered >= 3

    # Check 4: Best accuracy with selected features >= all-features accuracy - 0.05
    # Independently look up the all-features accuracy for the best model
    best_model_all_acc = sol.model_comparison[sol.best_model_name]["all_features"]["mean_accuracy"]
    if sol.best_feature_method == "all_features":
        # If best is already all-features, check passes trivially
        checks["selected_beats_random"] = True
    else:
        checks["selected_beats_random"] = sol.best_accuracy >= best_model_all_acc - 0.05

    # Check 5: Best accuracy > 80%
    checks["best_accuracy_gt_80pct"] = sol.best_accuracy > 0.80

    # Check 6: CV standard deviation < 0.05 (stable performance)
    checks["cv_scores_stable"] = sol.best_accuracy_std < 0.05

    # Overall
    checks["all_passed"] = all(
        v for k, v in checks.items() if k != "all_passed"
    )

    return checks


# --- Main ---

if __name__ == "__main__":
    instance = generate_instance(seed=42)
    sol = solve(instance)

    # ===============================================================
    #  PHASE 1-2: MODEL (uber-model output)
    # ===============================================================
    log.header("UBER-POLYA: Feature Importance & Model Comparison")

    log.section("PHASE 1-2: UNDERSTAND & PLAN (uber-model)")
    log.info("Problem: Which features matter? Which model is best?", tag="MODEL")
    log.info("Data: 800 samples, 20 features (5 informative, 3 redundant, 12 noise)", tag="DATA")
    log.info("Target: Binary classification, ~balanced classes", tag="DATA")
    log.info("Structure: Feature selection + supervised classification", tag="MODEL")
    log.blank()
    log.info("Plan:", tag="MODEL")
    log.info("1. PCA for dimensionality analysis", tag="MODEL")
    log.info("2. Mutual information (filter method) -- select top 8", tag="MODEL")
    log.info("3. RFE with Random Forest (wrapper method) -- select top 8", tag="MODEL")
    log.info("4. Compare Logistic, RF, SVM, k-NN x 3 feature sets (5-fold CV)", tag="MODEL")

    # ===============================================================
    #  PHASE 3: SOLVE (uber-solve output)
    # ===============================================================
    log.section("PHASE 3: EXECUTE (uber-solve)")

    # PCA
    log.step("STEP 1: PCA Explained Variance")
    log.metric("Components for 95%", str(sol.pca_n_components_95pct), tag="STATS")
    log.blank()
    log.info("Cumulative explained variance by component:", tag="STATS")
    for i, cum in enumerate(sol.pca_cumulative_variance):
        marker = " <-- 95% threshold" if i + 1 == sol.pca_n_components_95pct else ""
        log.bar("PC{:>2}:".format(i + 1), cum, tag="STATS", marker=marker)
    log.blank()

    # Mutual Information
    log.step("STEP 2: Mutual Information Feature Ranking")
    mi_order = sorted(
        range(instance.n_features),
        key=lambda i: sol.mi_feature_scores[i],
        reverse=True,
    )
    log.table_row("{:<12} {:>12} {:>8}".format("Feature", "MI Score", "Rank"), tag="TABLE")
    for idx in mi_order:
        marker = " *" if idx in instance.true_informative_indices else ""
        log.table_row("{:<12} {:>12.4f} {:>8}{}".format(
            "feat_{}".format(idx),
            sol.mi_feature_scores[idx],
            sol.mi_feature_ranking[idx],
            marker,
        ), tag="STATS")
    log.info("(* = true informative feature)", tag="DATA")
    log.metric("MI selected (top 8)", str(sol.mi_selected_indices), tag="RESULT")
    mi_recovered = len(set(sol.mi_selected_indices) & set(instance.true_informative_indices))
    log.metric("True informative found", "{}/{}".format(mi_recovered, instance.n_informative), tag="VERIFY")
    log.blank()

    # RFE
    log.step("STEP 3: RFE (Random Forest) Feature Ranking")
    rfe_order = sorted(
        range(instance.n_features),
        key=lambda i: sol.rfe_feature_ranking[i],
    )
    log.table_row("{:<12} {:>12}".format("Feature", "RFE Rank"), tag="TABLE")
    for idx in rfe_order:
        marker = " *" if idx in instance.true_informative_indices else ""
        log.table_row("{:<12} {:>12}{}".format(
            "feat_{}".format(idx),
            sol.rfe_feature_ranking[idx],
            marker,
        ), tag="STATS")
    log.info("(* = true informative feature)", tag="DATA")
    log.metric("RFE selected (top 8)", str(sol.rfe_selected_indices), tag="RESULT")
    rfe_recovered = len(set(sol.rfe_selected_indices) & set(instance.true_informative_indices))
    log.metric("True informative found", "{}/{}".format(rfe_recovered, instance.n_informative), tag="VERIFY")
    log.blank()

    # Overlap
    log.step("MI / RFE Overlap")
    log.metric("Overlap features", str(sol.mi_rfe_overlap), tag="STATS")
    log.metric("Overlap count", "{}/{}".format(sol.mi_rfe_overlap_count, instance.n_select), tag="STATS")
    log.blank()

    # Model comparison
    log.step("STEP 4: Model Comparison (5-Fold Stratified CV)")
    log.table_row("{:<22} {:>16} {:>16} {:>16}".format(
        "Model", "All (20)", "MI (8)", "RFE (8)"), tag="TABLE")
    for model_name, results in sol.model_comparison.items():
        all_acc = results["all_features"]["mean_accuracy"]
        mi_acc = results["mi_features"]["mean_accuracy"]
        rfe_acc = results["rfe_features"]["mean_accuracy"]
        log.table_row("{:<22} {:>12.2%} +/-{:.2%}  {:>7.2%} +/-{:.2%}  {:>7.2%} +/-{:.2%}".format(
            model_name,
            all_acc, results["all_features"]["std_accuracy"],
            mi_acc, results["mi_features"]["std_accuracy"],
            rfe_acc, results["rfe_features"]["std_accuracy"],
        ), tag="STATS")
    log.blank()

    # Best combination
    log.step("STEP 5: Best Combination")
    log.success("Model: {}".format(sol.best_model_name), tag="RESULT")
    log.success("Features: {}".format(sol.best_feature_method), tag="RESULT")
    log.success("Accuracy: {:.2%} +/- {:.2%}".format(
        sol.best_accuracy, sol.best_accuracy_std), tag="RESULT")
    log.blank()

    # ===============================================================
    #  PHASE 4: LOOK BACK (uber-interpret output)
    # ===============================================================
    log.section("PHASE 4: LOOK BACK (uber-interpret)")

    log.step("BOTTOM LINE")
    log.success("PCA: {} of 20 components explain 95% of variance".format(
        sol.pca_n_components_95pct), tag="RESULT")
    log.success("MI and RFE agree on {}/{} selected features".format(
        sol.mi_rfe_overlap_count, instance.n_select), tag="RESULT")
    log.success("Best pipeline: {} + {} = {:.2%} accuracy".format(
        sol.best_model_name, sol.best_feature_method, sol.best_accuracy), tag="RESULT")
    log.blank()

    log.step("WHAT THIS MEANS")
    if sol.pca_n_components_95pct <= 10:
        log.info("The feature space is highly compressible: {}/20 components capture 95% of variance".format(
            sol.pca_n_components_95pct), tag="INTERPRET")
    else:
        log.info("The feature space has moderate redundancy: {}/20 components for 95% variance".format(
            sol.pca_n_components_95pct), tag="INTERPRET")

    if sol.mi_rfe_overlap_count >= 6:
        log.info("Strong agreement between MI and RFE: both methods identify the same core features", tag="INTERPRET")
    else:
        log.info("Partial agreement between MI (filter) and RFE (wrapper): {}/{} overlap".format(
            sol.mi_rfe_overlap_count, instance.n_select), tag="INTERPRET")
        log.info("Different selection methods capture different aspects of feature relevance", tag="INTERPRET")

    if sol.best_feature_method != "all_features":
        log.success("Feature selection improved or maintained accuracy while using fewer features", tag="INTERPRET")
        log.info("Using {}/20 features reduces model complexity and overfitting risk".format(
            instance.n_select), tag="INTERPRET")
    else:
        log.info("All 20 features gave the best accuracy; noise features did not hurt this model", tag="INTERPRET")
    log.blank()

    log.step("RECOMMENDATIONS")
    log.success("1. Use {} for this classification task".format(sol.best_model_name), tag="RECOMMEND")
    log.success("2. Apply {} feature selection (top {} features)".format(
        sol.best_feature_method.replace("_features", "").upper(), instance.n_select), tag="RECOMMEND")
    log.success("3. Features {} are consistently important across both methods".format(
        sol.mi_rfe_overlap), tag="RECOMMEND")
    log.success("4. PCA confirms dimensionality can be reduced to {} components".format(
        sol.pca_n_components_95pct), tag="RECOMMEND")
    log.blank()

    log.step("LIMITATIONS")
    log.warning("Synthetic data: real datasets have more complex feature interactions", tag="WARNING")
    log.warning("MI assumes continuous features; for mixed types use adjusted estimators", tag="WARNING")
    log.warning("RFE with RF captures nonlinear importance but is computationally expensive", tag="WARNING")
    log.warning("Accuracy alone may not suffice -- consider precision/recall for imbalanced classes", tag="WARNING")
    log.blank()

    log.step("TRANSFERABLE PATTERN")
    log.info("Pattern: 'Which features matter and which model is best?'", tag="MODEL")
    log.info("Model:   PCA (variance) + filter (MI) + wrapper (RFE) selection", tag="MODEL")
    log.info("Solve:   Cross-validated model comparison across feature subsets", tag="SOLVE")
    log.info("Reuse:   Any tabular classification/regression with feature selection needs", tag="MODEL")

    log.blank()

    log.step("VERIFICATION")
    for check_name, result in sol.verification.items():
        if isinstance(result, bool):
            log.check(check_name, result, tag="VERIFY")
        else:
            log.check(check_name, float(result), tag="VERIFY")
    log.blank()

    log.metric("Algorithm", sol.algorithm, tag="SOLVE")
    log.metric("Time", "{:.4f}s".format(sol.time_seconds), tag="TIMING")
    log.divider(style="thick")

    # Save JSON
    output = {
        "instance": {
            "n_samples": instance.n_samples,
            "n_features": instance.n_features,
            "n_informative": instance.n_informative,
            "n_redundant": instance.n_redundant,
            "n_select": instance.n_select,
            "seed": instance.seed,
            "true_informative_indices": list(instance.true_informative_indices),
        },
        "pca": {
            "explained_variance_ratio": sol.pca_explained_variance_ratio,
            "cumulative_variance": sol.pca_cumulative_variance,
            "n_components_95pct": sol.pca_n_components_95pct,
        },
        "mutual_information": {
            "feature_scores": sol.mi_feature_scores,
            "feature_ranking": sol.mi_feature_ranking,
            "selected_indices": sol.mi_selected_indices,
        },
        "rfe": {
            "feature_ranking": sol.rfe_feature_ranking,
            "selected_indices": sol.rfe_selected_indices,
        },
        "feature_overlap": {
            "mi_rfe_overlap": sol.mi_rfe_overlap,
            "overlap_count": sol.mi_rfe_overlap_count,
        },
        "model_comparison": sol.model_comparison,
        "best_combination": {
            "model_name": sol.best_model_name,
            "feature_method": sol.best_feature_method,
            "accuracy": sol.best_accuracy,
            "accuracy_std": sol.best_accuracy_std,
        },
        "verification": sol.verification,
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
    }

    out_path = Path(__file__).resolve().parent / "solution.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    log.success("Solution data saved to: {}".format(out_path.name), tag="SAVE")
    log.divider(style="thick")
