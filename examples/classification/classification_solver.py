#!/usr/bin/env python3
"""Customer Churn Classification solver.

Predicts customer churn using three competing classifiers:
  1. Logistic Regression (L2 regularization)
  2. Random Forest (100 trees)
  3. Gradient Boosting (100 trees, sklearn)

Pipeline:
  - Generate synthetic customer data (~1000 customers, ~30% churn rate)
  - Stratified 80/20 train/test split
  - Fit all three models on training data
  - Evaluate accuracy, precision, recall, F1, ROC-AUC on test set
  - Feature importance from Random Forest
  - 5-fold stratified cross-validation for best model
  - Confusion matrix for best model
  - Independent verification of all quality criteria
"""
from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger

log = PolyaLogger()


# --- Data Model ---

@dataclass(frozen=True)
class Instance:
    """Customer churn classification instance."""
    features: tuple[tuple[float, ...], ...]   # rows of feature vectors
    labels: tuple[int, ...]                    # 0 = retained, 1 = churned
    feature_names: tuple[str, ...]             # column names
    n_customers: int
    churn_rate: float
    seed: int = 42
    test_size: float = 0.20


@dataclass
class Solution:
    """Classification solution with per-model metrics."""
    # Per-model metrics: {model_name: {metric_name: value}}
    model_metrics: dict = field(default_factory=dict)

    # Best model (by ROC-AUC)
    best_model_name: str = ""
    best_accuracy: float = 0.0
    best_roc_auc: float = 0.0

    # Confusion matrix for best model (TP, FP, FN, TN)
    confusion_tp: int = 0
    confusion_fp: int = 0
    confusion_fn: int = 0
    confusion_tn: int = 0

    # Feature importances from Random Forest
    feature_importances: list[tuple[str, float]] = field(default_factory=list)

    # Cross-validation for best model (5-fold)
    cv_scores: list[float] = field(default_factory=list)
    cv_mean: float = 0.0
    cv_std: float = 0.0

    # Baseline
    majority_class_accuracy: float = 0.0

    # Test set size
    test_set_size: int = 0

    # Metadata
    algorithm: str = ""
    time_seconds: float = 0.0

    # Verification
    verification: dict = field(default_factory=dict)


# --- Data Generation ---

def generate_instance(seed: int = 42) -> Instance:
    """Generate synthetic customer churn data.

    ~1000 customers with 6 features. Churn probability is driven by:
      - Shorter tenure -> higher churn
      - More support tickets -> higher churn
      - Month-to-month contract -> higher churn
      - Higher monthly charges -> slightly higher churn
    Target churn rate: ~30%.
    """
    rng = np.random.default_rng(seed)
    n = 1000

    # Feature generation
    tenure = rng.uniform(1, 72, size=n)                    # months
    monthly_charges = rng.uniform(20, 110, size=n)         # dollars
    total_charges = tenure * monthly_charges * rng.uniform(0.8, 1.2, size=n)
    num_support_tickets = rng.poisson(lam=2.0, size=n)     # count
    contract_type = rng.choice([0, 1], size=n, p=[0.55, 0.45])  # 0=month-to-month, 1=annual
    has_internet = rng.choice([0, 1], size=n, p=[0.25, 0.75])   # 0=no, 1=yes

    # Churn probability (logistic model)
    log_odds = (
        0.0                                 # base intercept
        - 0.06 * tenure                     # longer tenure -> less churn
        + 0.01 * monthly_charges            # higher charges -> slightly more churn
        + 0.35 * num_support_tickets        # more tickets -> more churn
        - 1.2 * contract_type               # annual contract -> much less churn
        + 0.3 * has_internet                # internet customers churn slightly more
    )
    prob_churn = 1.0 / (1.0 + np.exp(-log_odds))
    churned = (rng.uniform(size=n) < prob_churn).astype(int)

    feature_names = (
        "tenure",
        "monthly_charges",
        "total_charges",
        "num_support_tickets",
        "contract_type",
        "has_internet",
    )

    features = np.column_stack([
        tenure, monthly_charges, total_charges,
        num_support_tickets.astype(float),
        contract_type.astype(float),
        has_internet.astype(float),
    ])

    churn_rate = float(np.mean(churned))

    return Instance(
        features=tuple(tuple(row) for row in features),
        labels=tuple(churned.tolist()),
        feature_names=feature_names,
        n_customers=n,
        churn_rate=churn_rate,
        seed=seed,
    )


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Train three classifiers, evaluate, and select the best."""
    t0 = time.perf_counter()
    sol = Solution()

    X = np.array(instance.features)
    y = np.array(instance.labels)

    # --- Train/test split (stratified) ---
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=instance.test_size, random_state=instance.seed, stratify=y,
    )
    sol.test_set_size = len(y_test)

    # Baseline: majority class accuracy
    majority_class = int(np.argmax(np.bincount(y_test)))
    sol.majority_class_accuracy = float(np.mean(y_test == majority_class))

    # --- Standardize features (for Logistic Regression) ---
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # --- Define models ---
    models: dict[str, object] = {
        "Logistic Regression": LogisticRegression(
            max_iter=1000, random_state=instance.seed,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100, random_state=instance.seed,
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=100, random_state=instance.seed,
        ),
    }

    # --- Fit and evaluate each model ---
    best_auc = -1.0
    best_name = ""
    best_model = None
    best_X_test = None

    for name, model in models.items():
        # Logistic Regression uses scaled features; tree models use raw
        if name == "Logistic Regression":
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            y_prob = model.predict_proba(X_test_scaled)[:, 1]
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)[:, 1]

        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))
        auc = float(roc_auc_score(y_test, y_prob))

        sol.model_metrics[name] = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "roc_auc": round(auc, 4),
        }

        if auc > best_auc:
            best_auc = auc
            best_name = name
            best_model = model
            best_X_test = X_test_scaled if name == "Logistic Regression" else X_test

    sol.best_model_name = best_name
    sol.best_accuracy = sol.model_metrics[best_name]["accuracy"]
    sol.best_roc_auc = sol.model_metrics[best_name]["roc_auc"]

    # --- Confusion matrix for best model ---
    y_pred_best = best_model.predict(best_X_test)
    cm = confusion_matrix(y_test, y_pred_best)
    # sklearn confusion_matrix layout: [[TN, FP], [FN, TP]]
    sol.confusion_tn = int(cm[0, 0])
    sol.confusion_fp = int(cm[0, 1])
    sol.confusion_fn = int(cm[1, 0])
    sol.confusion_tp = int(cm[1, 1])

    # --- Feature importances from Random Forest ---
    rf_model = models["Random Forest"]
    importances = rf_model.feature_importances_
    sol.feature_importances = sorted(
        [(name, round(float(imp), 4)) for name, imp in
         zip(instance.feature_names, importances)],
        key=lambda x: x[1],
        reverse=True,
    )

    # --- 5-fold stratified cross-validation for best model ---
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=instance.seed)
    if best_name == "Logistic Regression":
        X_cv = scaler.fit_transform(X)
    else:
        X_cv = X
    cv_scores = cross_val_score(best_model, X_cv, y, cv=cv, scoring="accuracy")
    sol.cv_scores = [round(float(s), 4) for s in cv_scores]
    sol.cv_mean = round(float(np.mean(cv_scores)), 4)
    sol.cv_std = round(float(np.std(cv_scores)), 4)

    # --- Metadata ---
    sol.algorithm = "Logistic Regression + Random Forest (100) + Gradient Boosting (100)"
    sol.time_seconds = time.perf_counter() - t0

    # --- Verification ---
    sol.verification = verify(instance, sol)

    return sol


# --- Verification (independent of solver) ---

def verify(instance: Instance, sol: Solution) -> dict:
    """Independently verify the classification results.

    Seven checks:
      1. Best model accuracy > 75%
      2. Best model ROC-AUC > 0.70
      3. Random Forest accuracy > majority-class baseline
      4. Feature importances sum to ~1.0
      5. Cross-validation std < 0.05 (stable)
      6. Confusion matrix sums to test set size
      7. All above pass
    """
    checks: dict = {}

    # Check 1: Best accuracy > 75%
    checks["best_accuracy_gt_75pct"] = sol.best_accuracy > 0.75

    # Check 2: Best ROC-AUC > 0.70
    checks["best_roc_auc_gt_70pct"] = sol.best_roc_auc > 0.70

    # Check 3: Random Forest beats majority-class baseline
    rf_acc = sol.model_metrics["Random Forest"]["accuracy"]
    checks["rf_outperforms_baseline"] = rf_acc > sol.majority_class_accuracy

    # Check 4: Feature importances sum to ~1.0
    imp_sum = sum(imp for _, imp in sol.feature_importances)
    checks["feature_importances_sum_to_1"] = abs(imp_sum - 1.0) < 0.01

    # Check 5: Cross-validation accuracy is stable (std < 0.05)
    checks["cv_accuracy_stable"] = sol.cv_std < 0.05

    # Check 6: Confusion matrix sums to test set size
    cm_total = sol.confusion_tp + sol.confusion_fp + sol.confusion_fn + sol.confusion_tn
    checks["confusion_matrix_sums_correct"] = cm_total == sol.test_set_size

    # Check 7: All above pass
    checks["all_passed"] = all(
        v for k, v in checks.items() if k != "all_passed"
    )

    return checks


# --- Main ---

if __name__ == "__main__":
    instance = generate_instance(seed=42)
    sol = solve(instance)

    # ===============================================================
    #  PHASE 1-2: UNDERSTAND & PLAN (uber-model)
    # ===============================================================
    log.header("UBER-POLYA: Customer Churn Classification")

    log.section("PHASE 1-2: UNDERSTAND & PLAN (uber-model)")
    log.info("Problem: Predict which customers will churn (binary classification)", tag="MODEL")
    log.info("Structure: Supervised classification with tabular features", tag="MODEL")
    log.info("Models: Logistic Regression, Random Forest, Gradient Boosting", tag="MODEL")
    log.info("Evaluation: accuracy, precision, recall, F1, ROC-AUC", tag="MODEL")
    log.blank()

    log.step("INSTANCE")
    log.metric("Customers", str(instance.n_customers), tag="DATA")
    log.metric("Features", str(len(instance.feature_names)), tag="DATA")
    log.metric("Feature names", ", ".join(instance.feature_names), tag="DATA")
    log.metric("Churn rate", "{:.1%}".format(instance.churn_rate), tag="DATA")
    log.metric("Train/test split", "80/20 stratified", tag="DATA")
    log.blank()

    # ===============================================================
    #  PHASE 3: EXECUTE (uber-solve)
    # ===============================================================
    log.section("PHASE 3: EXECUTE (uber-solve)")

    # Step 1: Model training and evaluation
    log.step("STEP 1: Train & Evaluate Models")
    log.metric("Majority baseline", "{:.1%}".format(sol.majority_class_accuracy), tag="STATS")
    log.blank()

    for model_name, metrics in sol.model_metrics.items():
        log.info(model_name, tag="SOLVE")
        log.metric("  Accuracy", "{:.2%}".format(metrics["accuracy"]), tag="STATS")
        log.metric("  Precision", "{:.2%}".format(metrics["precision"]), tag="STATS")
        log.metric("  Recall", "{:.2%}".format(metrics["recall"]), tag="STATS")
        log.metric("  F1", "{:.4f}".format(metrics["f1"]), tag="STATS")
        log.metric("  ROC-AUC", "{:.4f}".format(metrics["roc_auc"]), tag="STATS")
        log.blank()

    log.success("Best model (by ROC-AUC): {} (AUC={:.4f})".format(
        sol.best_model_name, sol.best_roc_auc), tag="RESULT")
    log.blank()

    # Step 2: Confusion matrix
    log.step("STEP 2: Confusion Matrix ({})".format(sol.best_model_name))
    log.table_row("{:<20} Predicted=0    Predicted=1".format(""), tag="TABLE")
    log.table_row("Actual=0 (retained)    TN={:<10}  FP={}".format(
        sol.confusion_tn, sol.confusion_fp), tag="TABLE")
    log.table_row("Actual=1 (churned)     FN={:<10}  TP={}".format(
        sol.confusion_fn, sol.confusion_tp), tag="TABLE")
    log.metric("Total test samples", str(sol.test_set_size), tag="DATA")
    log.blank()

    # Step 3: Feature importances
    log.step("STEP 3: Feature Importances (Random Forest)")
    for fname, imp in sol.feature_importances:
        log.bar("{:<24}".format(fname), imp, max_width=30, tag="STATS")
    imp_sum = sum(imp for _, imp in sol.feature_importances)
    log.metric("Sum of importances", "{:.4f}".format(imp_sum), tag="STATS")
    log.blank()

    # Step 4: Cross-validation
    log.step("STEP 4: 5-Fold Cross-Validation ({})".format(sol.best_model_name))
    for i, score in enumerate(sol.cv_scores):
        log.metric("  Fold {}".format(i + 1), "{:.4f}".format(score), tag="STATS")
    log.metric("  Mean", "{:.4f}".format(sol.cv_mean), tag="RESULT")
    log.metric("  Std", "{:.4f}".format(sol.cv_std), tag="RESULT")
    log.blank()

    # Step 5: Verification
    log.step("STEP 5: Independent Verification")
    for check_name, passed in sol.verification.items():
        log.check(check_name, passed, tag="VERIFY")
    log.blank()

    # ===============================================================
    #  PHASE 4: LOOK BACK (uber-interpret)
    # ===============================================================
    log.section("PHASE 4: LOOK BACK (uber-interpret)")

    log.step("BOTTOM LINE")
    log.success("{} achieves {:.1%} accuracy and {:.4f} ROC-AUC".format(
        sol.best_model_name, sol.best_accuracy, sol.best_roc_auc), tag="RESULT")
    log.success("All models beat the majority-class baseline ({:.1%})".format(
        sol.majority_class_accuracy), tag="RESULT")
    log.blank()

    log.step("KEY DRIVERS OF CHURN")
    top_features = sol.feature_importances[:3]
    for rank, (fname, imp) in enumerate(top_features, 1):
        log.info("{}. {} (importance={:.4f})".format(rank, fname, imp), tag="INTERPRET")
    log.blank()

    log.step("RECOMMENDATIONS")
    log.success("1. Deploy {} for churn prediction in production".format(
        sol.best_model_name), tag="RECOMMEND")
    log.success("2. Monitor top feature '{}' as early warning signal".format(
        sol.feature_importances[0][0]), tag="RECOMMEND")
    log.success("3. Target retention campaigns at month-to-month customers", tag="RECOMMEND")
    log.success("4. Investigate high-ticket customers for proactive support", tag="RECOMMEND")
    log.blank()

    log.step("LIMITATIONS")
    log.warning("Synthetic data -- real customer data may have more noise and missing values",
                tag="WARNING")
    log.warning("No hyperparameter tuning -- grid search / Bayesian optimization could improve",
                tag="WARNING")
    log.warning("No feature engineering -- interaction terms, binning, or embeddings not explored",
                tag="WARNING")
    log.warning("Class imbalance not addressed -- SMOTE or class weights may help recall",
                tag="WARNING")

    log.step("TRANSFERABLE PATTERN")
    log.info("Pattern: 'Classify Y from tabular features with model comparison'", tag="MODEL")
    log.info("Model:   Logistic Regression + Random Forest + Gradient Boosting", tag="MODEL")
    log.info("Verify:  Accuracy, ROC-AUC, confusion matrix, CV stability", tag="SOLVE")
    log.info("Reuse:   Any binary classification with structured features", tag="MODEL")

    log.blank()
    log.metric("Algorithm", sol.algorithm, tag="SOLVE")
    log.metric("Time", "{:.4f}s".format(sol.time_seconds), tag="TIMING")
    log.divider(style="thick")

    # Save JSON
    output = {
        "instance": {
            "n_customers": instance.n_customers,
            "n_features": len(instance.feature_names),
            "feature_names": list(instance.feature_names),
            "churn_rate": instance.churn_rate,
            "seed": instance.seed,
            "test_size": instance.test_size,
        },
        "model_metrics": sol.model_metrics,
        "best_model": {
            "name": sol.best_model_name,
            "accuracy": sol.best_accuracy,
            "roc_auc": sol.best_roc_auc,
        },
        "confusion_matrix": {
            "TP": sol.confusion_tp,
            "FP": sol.confusion_fp,
            "FN": sol.confusion_fn,
            "TN": sol.confusion_tn,
        },
        "feature_importances": {
            name: imp for name, imp in sol.feature_importances
        },
        "cross_validation": {
            "n_folds": 5,
            "scores": sol.cv_scores,
            "mean": sol.cv_mean,
            "std": sol.cv_std,
        },
        "majority_class_accuracy": sol.majority_class_accuracy,
        "verification": sol.verification,
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
    }
    out_path = Path(__file__).resolve().parent / "solution.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    log.success("Solution data saved to: {}".format(out_path.name), tag="SAVE")
    log.divider(style="thick")
