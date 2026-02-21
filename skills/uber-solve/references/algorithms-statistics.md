# Statistical Inference Algorithm Catalog

Comprehensive catalog of 103 algorithms for statistical inference, time series analysis, stochastic processes, survival analysis, machine learning, Monte Carlo simulation, queuing theory, and discrete-event simulation. Organized by problem type, each entry includes complexity, solver library, correctness guarantee, and implementation guidance.

**Scope**: Statistical Inference (45 algorithms), Time Series Analysis (15 algorithms), Stochastic Processes (5 algorithms), Survival Analysis (3 new algorithms), Machine Learning (22 algorithms), Monte Carlo Methods (5 algorithms), Queuing Theory (5 algorithms), Discrete-Event Simulation (3 algorithms).

**Legend**:
- **T**: Time complexity | **S**: Space complexity
- **Lib**: Recommended Python library
- **Exact**: Closed-form or asymptotically exact | **Approx**: Approximate or simulation-based

**Verification paradigm**: Unlike discrete math (exhaustive check, optimality certificates), statistics verifies through alternative tests (parametric vs. nonparametric), assumption diagnostics, and cross-validation. Every result should include: point estimate, confidence/credible interval, effect size, and sample size.

---

## 1. Descriptive Statistics

### S1: Summary Statistics

**Problem**: Compute central tendency (mean, median, mode) and spread (variance, SD, IQR, range) of a dataset.
**T**: O(n) for mean/var, O(n log n) for median/quantiles | **S**: O(1) streaming, O(n) batch
**Lib**: `numpy.mean()`, `numpy.median()`, `numpy.std()`, `scipy.stats.describe()`
**Guarantee**: Exact (closed-form)

```python
import numpy as np
from scipy import stats

def summary_statistics(data: np.ndarray) -> dict:
    """Compute comprehensive summary statistics."""
    desc = stats.describe(data)
    return {
        "n": desc.nobs,
        "mean": desc.mean,
        "variance": desc.variance,
        "std": np.sqrt(desc.variance),
        "skewness": desc.skewness,
        "kurtosis": desc.kurtosis,
        "min": desc.minmax[0],
        "max": desc.minmax[1],
        "median": np.median(data),
        "q1": np.percentile(data, 25),
        "q3": np.percentile(data, 75),
        "iqr": np.percentile(data, 75) - np.percentile(data, 25),
    }
```

**Use when**: First step in any analysis. Always compute before running tests. Check for outliers (IQR rule: below Q1-1.5*IQR or above Q3+1.5*IQR).

---

### S2: Quantile / Percentile Estimation

**Problem**: Estimate the value below which a given fraction of observations fall.
**T**: O(n log n) sort-based, O(n) expected via quickselect | **S**: O(1) to O(n)
**Lib**: `numpy.percentile()`, `numpy.quantile()`, `scipy.stats.mstats.mquantiles()`
**Guarantee**: Exact for sample quantiles; confidence intervals via order statistics

```python
import numpy as np

def quantiles_with_ci(data: np.ndarray, q: float = 0.5, alpha: float = 0.05) -> dict:
    """Estimate quantile with nonparametric confidence interval using order statistics."""
    n = len(data)
    sorted_data = np.sort(data)
    estimate = np.quantile(data, q)
    # Binomial CI for quantile rank
    from scipy.stats import binom
    lower_rank = binom.ppf(alpha / 2, n, q)
    upper_rank = binom.ppf(1 - alpha / 2, n, q)
    ci_lower = sorted_data[max(0, int(lower_rank) - 1)]
    ci_upper = sorted_data[min(n - 1, int(upper_rank))]
    return {"quantile": q, "estimate": estimate, "ci": (ci_lower, ci_upper)}
```

**Use when**: Understanding distribution shape, setting thresholds, identifying outlier boundaries, salary/performance benchmarking.

---

### S3: Kernel Density Estimation (KDE)

**Problem**: Estimate the probability density function of a continuous random variable from a sample.
**T**: O(n * m) where m = evaluation grid points | **S**: O(n + m)
**Lib**: `scipy.stats.gaussian_kde()`, `sklearn.neighbors.KernelDensity()`
**Guarantee**: Consistent estimator (converges to true density as n → ∞). Bandwidth selection is critical.

```python
from scipy.stats import gaussian_kde
import numpy as np

def kde_estimate(data: np.ndarray, n_points: int = 200) -> tuple:
    """Estimate density using Gaussian KDE with Silverman bandwidth."""
    kde = gaussian_kde(data, bw_method="silverman")
    x_grid = np.linspace(data.min() - data.std(), data.max() + data.std(), n_points)
    density = kde(x_grid)
    return x_grid, density
```

**Use when**: Visualizing distribution shape without assuming parametric form. Better than histograms for smooth distributions. Use Scott's or Silverman's rule for bandwidth.

---

### S4: Robust Estimators

**Problem**: Estimate location and scale that are resistant to outliers.
**T**: O(n) for trimmed mean, O(n log n) for MAD | **S**: O(n)
**Lib**: `scipy.stats.trim_mean()`, `statsmodels.robust.mad()`, `scipy.stats.iqr()`
**Guarantee**: High breakdown point (resists up to 50% outliers for median).

```python
from scipy import stats
import numpy as np

def robust_estimates(data: np.ndarray) -> dict:
    """Compute outlier-resistant location and scale estimates."""
    return {
        "median": np.median(data),
        "trimmed_mean_10pct": stats.trim_mean(data, 0.1),
        "mad": stats.median_abs_deviation(data),
        "iqr": stats.iqr(data),
        "winsorized_mean": stats.mstats.winsorize(data, limits=[0.05, 0.05]).mean(),
    }
```

**Use when**: Data contains outliers or heavy tails. Financial data, sensor readings, any measurement with occasional errors. Use MAD as robust alternative to standard deviation.

---

### S5: Correlation Analysis

**Problem**: Measure the strength and direction of association between two continuous variables.
**T**: O(n) for Pearson, O(n log n) for Spearman/Kendall | **S**: O(n)
**Lib**: `scipy.stats.pearsonr()`, `scipy.stats.spearmanr()`, `scipy.stats.kendalltau()`
**Guarantee**: Exact p-values for Pearson (assuming normality), asymptotic for Spearman/Kendall.

```python
from scipy import stats

def correlation_analysis(x, y) -> dict:
    """Compute Pearson, Spearman, and Kendall correlations with p-values."""
    r_pearson, p_pearson = stats.pearsonr(x, y)
    r_spearman, p_spearman = stats.spearmanr(x, y)
    tau_kendall, p_kendall = stats.kendalltau(x, y)
    return {
        "pearson": {"r": r_pearson, "p": p_pearson},
        "spearman": {"rho": r_spearman, "p": p_spearman},
        "kendall": {"tau": tau_kendall, "p": p_kendall},
    }
```

**Use when**: Exploring bivariate relationships. Use Pearson for linear + normal, Spearman for monotonic or ordinal, Kendall for small samples or many ties.

---

## 2. Hypothesis Testing

### S6: One-Sample t-Test

**Problem**: Test whether the mean of a population equals a hypothesized value μ₀.
**T**: O(n) | **S**: O(1)
**Lib**: `scipy.stats.ttest_1samp()`
**Guarantee**: Exact under normality assumption. Robust to non-normality for n ≥ 30 (CLT).

```python
from scipy import stats
import numpy as np

def one_sample_t_test(data: np.ndarray, mu0: float = 0, alpha: float = 0.05) -> dict:
    """Test H0: μ = μ0 vs H1: μ ≠ μ0."""
    t_stat, p_value = stats.ttest_1samp(data, mu0)
    n = len(data)
    mean = np.mean(data)
    se = stats.sem(data)
    ci = stats.t.interval(1 - alpha, df=n - 1, loc=mean, scale=se)
    effect_size = (mean - mu0) / np.std(data, ddof=1)  # Cohen's d
    return {
        "t_statistic": t_stat, "p_value": p_value, "df": n - 1,
        "mean": mean, "ci": ci, "cohens_d": effect_size,
        "reject_h0": p_value < alpha,
    }
```

**Use when**: Comparing a sample mean to a known/hypothesized value. Quality control (is the mean within spec?), clinical trials (does the treatment differ from baseline?).

---

### S7: Two-Sample t-Test

**Problem**: Test whether two independent groups have equal means. Variants: equal variance (pooled), unequal variance (Welch's).
**T**: O(n₁ + n₂) | **S**: O(1)
**Lib**: `scipy.stats.ttest_ind()`, `pingouin.ttest()`
**Guarantee**: Exact under normality + equal variance (Student's), approximate for Welch's.

```python
from scipy import stats
import numpy as np

def two_sample_t_test(group1, group2, equal_var: bool = False, alpha: float = 0.05) -> dict:
    """Two-sample t-test. Default: Welch's (unequal variance)."""
    t_stat, p_value = stats.ttest_ind(group1, group2, equal_var=equal_var)
    # Effect size: Cohen's d
    n1, n2 = len(group1), len(group2)
    pooled_std = np.sqrt(((n1-1)*np.var(group1, ddof=1) + (n2-1)*np.var(group2, ddof=1)) / (n1+n2-2))
    cohens_d = (np.mean(group1) - np.mean(group2)) / pooled_std
    # Levene's test for equal variance assumption
    _, p_levene = stats.levene(group1, group2)
    return {
        "t_statistic": t_stat, "p_value": p_value,
        "cohens_d": cohens_d, "equal_var_assumed": equal_var,
        "levene_p": p_levene, "reject_h0": p_value < alpha,
        "mean_diff": np.mean(group1) - np.mean(group2),
    }
```

**Use when**: Comparing two groups (A/B testing, treatment vs. control, before vs. after on different subjects). Use Welch's (equal_var=False) by default -- it's robust.

---

### S8: Paired t-Test

**Problem**: Test whether the mean difference between paired observations is zero.
**T**: O(n) | **S**: O(n)
**Lib**: `scipy.stats.ttest_rel()`, `pingouin.ttest(paired=True)`
**Guarantee**: Exact under normality of differences.

```python
from scipy import stats
import numpy as np

def paired_t_test(before, after, alpha: float = 0.05) -> dict:
    """Test H0: mean difference = 0 for paired observations."""
    differences = np.array(after) - np.array(before)
    t_stat, p_value = stats.ttest_rel(before, after)
    mean_diff = np.mean(differences)
    se_diff = stats.sem(differences)
    n = len(differences)
    ci = stats.t.interval(1 - alpha, df=n - 1, loc=mean_diff, scale=se_diff)
    cohens_d = mean_diff / np.std(differences, ddof=1)
    return {
        "t_statistic": t_stat, "p_value": p_value, "df": n - 1,
        "mean_diff": mean_diff, "ci": ci, "cohens_d": cohens_d,
        "reject_h0": p_value < alpha,
    }
```

**Use when**: Same subjects measured before/after, matched pairs, repeated measures. More powerful than two-sample test when pairing is valid.

---

### S9: Mann-Whitney U Test

**Problem**: Nonparametric test for whether one group tends to have larger values than another.
**T**: O(n log n) | **S**: O(n)
**Lib**: `scipy.stats.mannwhitneyu()`, `pingouin.mwu()`
**Guarantee**: Exact for small samples, asymptotic for large. Distribution-free.

```python
from scipy import stats

def mann_whitney_test(group1, group2, alternative: str = "two-sided") -> dict:
    """Nonparametric alternative to two-sample t-test."""
    u_stat, p_value = stats.mannwhitneyu(group1, group2, alternative=alternative)
    n1, n2 = len(group1), len(group2)
    # Rank-biserial correlation as effect size
    r = 1 - (2 * u_stat) / (n1 * n2)
    return {
        "u_statistic": u_stat, "p_value": p_value,
        "rank_biserial_r": r, "n1": n1, "n2": n2,
    }
```

**Use when**: Comparing two groups when normality assumption is violated, data is ordinal, or sample is small with heavy tails.

---

### S10: Chi-Squared Test of Independence

**Problem**: Test whether two categorical variables are independent.
**T**: O(r * c * n) where r, c = table dimensions | **S**: O(r * c)
**Lib**: `scipy.stats.chi2_contingency()`, `pingouin.chi2_independence()`
**Guarantee**: Asymptotic (valid when all expected frequencies ≥ 5). Use Fisher's exact for small samples.

```python
from scipy import stats
import numpy as np

def chi_squared_test(observed: np.ndarray) -> dict:
    """Chi-squared test of independence on contingency table."""
    chi2, p_value, dof, expected = stats.chi2_contingency(observed)
    n = observed.sum()
    # Cramer's V as effect size
    k = min(observed.shape)
    cramers_v = np.sqrt(chi2 / (n * (k - 1)))
    return {
        "chi2": chi2, "p_value": p_value, "dof": dof,
        "expected": expected, "cramers_v": cramers_v,
        "min_expected": expected.min(),
        "valid": expected.min() >= 5,
    }
```

**Use when**: Testing association between two categorical variables (survey responses vs. demographics, treatment vs. outcome category). Check min expected ≥ 5.

---

### S11: Fisher's Exact Test

**Problem**: Exact test of independence for 2×2 contingency tables.
**T**: O(min(a,b,c,d)) for hypergeometric computation | **S**: O(1)
**Lib**: `scipy.stats.fisher_exact()`
**Guarantee**: Exact (no large-sample approximation needed).

```python
from scipy import stats
import numpy as np

def fisher_exact_test(table: np.ndarray) -> dict:
    """Fisher's exact test for 2x2 contingency table."""
    odds_ratio, p_value = stats.fisher_exact(table)
    return {
        "odds_ratio": odds_ratio, "p_value": p_value,
        "table": table.tolist(),
    }
```

**Use when**: 2×2 contingency tables with small sample sizes (any expected frequency < 5). Gold standard for small-sample categorical tests.

---

### S12: One-Way ANOVA

**Problem**: Test whether 3+ group means are equal. Omnibus test -- does not tell which groups differ.
**T**: O(n) | **S**: O(k) where k = number of groups
**Lib**: `scipy.stats.f_oneway()`, `pingouin.anova()`, `statsmodels.stats.anova.anova_lm()`
**Guarantee**: Exact under normality + equal variance. Use Kruskal-Wallis for nonparametric alternative.

```python
from scipy import stats

def one_way_anova(*groups, alpha: float = 0.05) -> dict:
    """One-way ANOVA: test equality of k group means."""
    f_stat, p_value = stats.f_oneway(*groups)
    k = len(groups)
    ns = [len(g) for g in groups]
    n_total = sum(ns)
    # Eta-squared effect size
    grand_mean = sum(sum(g) for g in groups) / n_total
    ss_between = sum(n * (g.mean() - grand_mean)**2 for n, g in zip(ns, groups))
    ss_total = sum(sum((x - grand_mean)**2 for x in g) for g in groups)
    eta_squared = ss_between / ss_total if ss_total > 0 else 0
    return {
        "f_statistic": f_stat, "p_value": p_value,
        "k_groups": k, "n_total": n_total,
        "eta_squared": eta_squared, "reject_h0": p_value < alpha,
    }
```

**Use when**: Comparing 3+ groups. Follow up with post-hoc tests (Tukey HSD, Bonferroni) to find which pairs differ.

---

### S13: Kruskal-Wallis Test

**Problem**: Nonparametric alternative to one-way ANOVA for 3+ groups.
**T**: O(n log n) | **S**: O(n)
**Lib**: `scipy.stats.kruskal()`, `pingouin.kruskal()`
**Guarantee**: Asymptotic. Distribution-free.

```python
from scipy import stats

def kruskal_wallis(*groups) -> dict:
    """Nonparametric test for 3+ group comparison."""
    h_stat, p_value = stats.kruskal(*groups)
    n_total = sum(len(g) for g in groups)
    # Epsilon-squared effect size
    epsilon_sq = (h_stat - len(groups) + 1) / (n_total - len(groups))
    return {
        "h_statistic": h_stat, "p_value": p_value,
        "epsilon_squared": max(0, epsilon_sq),
    }
```

**Use when**: Comparing 3+ groups when ANOVA assumptions (normality, equal variance) are violated. Follow up with Dunn's test for pairwise comparisons.

---

### S14: Kolmogorov-Smirnov Test

**Problem**: Test whether a sample comes from a specific distribution, or whether two samples come from the same distribution.
**T**: O(n log n) | **S**: O(n)
**Lib**: `scipy.stats.kstest()` (1-sample), `scipy.stats.ks_2samp()` (2-sample)
**Guarantee**: Exact for continuous distributions. Distribution-free.

```python
from scipy import stats

def ks_test(data, distribution: str = "norm", **dist_params) -> dict:
    """Test if data follows a given distribution."""
    stat, p_value = stats.kstest(data, distribution, args=tuple(dist_params.values()))
    return {"ks_statistic": stat, "p_value": p_value, "distribution": distribution}

def ks_two_sample(sample1, sample2) -> dict:
    """Test if two samples come from the same distribution."""
    stat, p_value = stats.ks_2samp(sample1, sample2)
    return {"ks_statistic": stat, "p_value": p_value}
```

**Use when**: Checking distributional assumptions (normality, exponentiality), comparing two empirical distributions. Sensitive to location, scale, and shape differences.

---

### S15: Shapiro-Wilk Normality Test

**Problem**: Test whether a sample comes from a normal distribution.
**T**: O(n log n) | **S**: O(n)
**Lib**: `scipy.stats.shapiro()`
**Guarantee**: Exact. Most powerful normality test for n ≤ 5000.

```python
from scipy import stats

def normality_check(data, alpha: float = 0.05) -> dict:
    """Comprehensive normality assessment."""
    w_stat, p_shapiro = stats.shapiro(data)
    _, p_dagostino = stats.normaltest(data)  # D'Agostino-Pearson
    return {
        "shapiro_w": w_stat, "shapiro_p": p_shapiro,
        "dagostino_p": p_dagostino,
        "is_normal": p_shapiro > alpha,
        "recommendation": "parametric" if p_shapiro > alpha else "nonparametric",
    }
```

**Use when**: Before running parametric tests (t-test, ANOVA). If rejected, switch to nonparametric alternatives. For n > 5000, use D'Agostino-Pearson or visual QQ plot.

---

### S16: Permutation Test

**Problem**: Exact or Monte Carlo test of any test statistic under H0 by randomly permuting group labels.
**T**: O(n! ) exact or O(B * n) Monte Carlo with B permutations | **S**: O(n)
**Lib**: `scipy.stats.permutation_test()` (scipy ≥1.8)
**Guarantee**: Exact if all permutations enumerated. Monte Carlo: accuracy ±1/√B.

```python
from scipy import stats
import numpy as np

def permutation_test_means(group1, group2, n_permutations: int = 10000, seed: int = 42) -> dict:
    """Permutation test for difference in means."""
    def statistic(x, y, axis):
        return np.mean(x, axis=axis) - np.mean(y, axis=axis)
    result = stats.permutation_test(
        (group1, group2), statistic, n_resamples=n_permutations,
        random_state=seed, alternative="two-sided",
    )
    return {
        "observed_diff": np.mean(group1) - np.mean(group2),
        "p_value": result.pvalue,
        "n_permutations": n_permutations,
    }
```

**Use when**: No distributional assumptions needed. Small samples. Any test statistic (not limited to mean). Gold standard for A/B tests when sample size permits.

---

### S17: Multiple Testing Correction

**Problem**: Adjust p-values when performing multiple simultaneous hypothesis tests to control false discovery rate.
**T**: O(m log m) for BH, O(m) for Bonferroni, where m = number of tests | **S**: O(m)
**Lib**: `statsmodels.stats.multitest.multipletests()`
**Guarantee**: Bonferroni controls FWER exactly. BH controls FDR at level q.

```python
from statsmodels.stats.multitest import multipletests

def correct_multiple_tests(p_values: list[float], alpha: float = 0.05, method: str = "fdr_bh") -> dict:
    """Adjust p-values for multiple comparisons.
    Methods: 'bonferroni', 'holm', 'fdr_bh' (Benjamini-Hochberg), 'fdr_by'.
    """
    reject, pvals_corrected, _, _ = multipletests(p_values, alpha=alpha, method=method)
    return {
        "original_p": p_values,
        "corrected_p": pvals_corrected.tolist(),
        "reject": reject.tolist(),
        "method": method, "n_rejected": sum(reject),
    }
```

**Use when**: Running multiple tests (pairwise comparisons after ANOVA, testing many features, multiple endpoints). Use BH for discovery, Bonferroni for strict control.

---

## 3. Confidence Intervals

### S18: Normal (Z) Confidence Interval

**Problem**: Estimate a confidence interval for a population mean when σ is known or n is large (≥30).
**T**: O(n) | **S**: O(1)
**Lib**: `scipy.stats.norm.interval()`
**Guarantee**: Exact when σ known and population is normal. Approximate via CLT for large n.

```python
from scipy import stats
import numpy as np

def z_confidence_interval(data: np.ndarray, confidence: float = 0.95) -> dict:
    """CI for mean using normal distribution (large sample or known σ)."""
    n = len(data)
    mean = np.mean(data)
    se = np.std(data, ddof=1) / np.sqrt(n)
    ci = stats.norm.interval(confidence, loc=mean, scale=se)
    return {"mean": mean, "ci": ci, "se": se, "n": n, "confidence": confidence}
```

**Use when**: Large samples (n ≥ 30). For small samples, use t-interval instead.

---

### S19: Student's t Confidence Interval

**Problem**: CI for population mean when σ is unknown and sample is small.
**T**: O(n) | **S**: O(1)
**Lib**: `scipy.stats.t.interval()`
**Guarantee**: Exact under normality.

```python
from scipy import stats
import numpy as np

def t_confidence_interval(data: np.ndarray, confidence: float = 0.95) -> dict:
    """CI for mean using t-distribution (unknown σ, small sample)."""
    n = len(data)
    mean = np.mean(data)
    se = stats.sem(data)
    ci = stats.t.interval(confidence, df=n - 1, loc=mean, scale=se)
    margin = ci[1] - mean
    return {"mean": mean, "ci": ci, "se": se, "margin": margin, "df": n - 1}
```

**Use when**: Default choice for mean CI. Works for any sample size; converges to Z interval for large n.

---

### S20: Bootstrap Confidence Interval

**Problem**: Nonparametric CI for any statistic (mean, median, correlation, custom function).
**T**: O(B * n) where B = bootstrap replicates (1000-10000) | **S**: O(B)
**Lib**: `scipy.stats.bootstrap()` (scipy ≥1.7)
**Guarantee**: Asymptotically correct. Distribution-free. Works for any statistic.

```python
from scipy import stats
import numpy as np

def bootstrap_ci(data: np.ndarray, statistic=np.mean, confidence: float = 0.95,
                 n_bootstrap: int = 10000, seed: int = 42, method: str = "BCa") -> dict:
    """Bootstrap CI using BCa (bias-corrected and accelerated) method."""
    result = stats.bootstrap(
        (data,), statistic, n_resamples=n_bootstrap,
        confidence_level=confidence, random_state=seed, method=method.lower(),
    )
    return {
        "estimate": statistic(data),
        "ci": (result.confidence_interval.low, result.confidence_interval.high),
        "n_bootstrap": n_bootstrap, "method": method,
    }
```

**Use when**: CI for non-standard statistics (median, trimmed mean, ratio, custom metric), non-normal data, or when parametric assumptions are questionable. BCa is the recommended method.

---

### S21: Proportion Confidence Interval

**Problem**: CI for a population proportion p from a binary outcome.
**T**: O(1) | **S**: O(1)
**Lib**: `statsmodels.stats.proportion.proportion_confint()`
**Guarantee**: Multiple methods with different coverage properties. Wilson is recommended.

```python
from statsmodels.stats.proportion import proportion_confint

def proportion_ci(successes: int, n: int, confidence: float = 0.95,
                  method: str = "wilson") -> dict:
    """CI for proportion. Methods: 'wilson', 'normal', 'agresti_coull', 'jeffreys'."""
    ci = proportion_confint(successes, n, alpha=1 - confidence, method=method)
    p_hat = successes / n
    return {"p_hat": p_hat, "ci": ci, "n": n, "method": method}
```

**Use when**: Estimating conversion rates, success rates, defect rates, poll results. Wilson interval is preferred (better coverage than normal approximation, especially near 0 or 1).

---

### S22: Prediction Interval

**Problem**: Interval that will contain a single future observation with specified probability.
**T**: O(n) | **S**: O(1)
**Lib**: Custom (scipy-based), `statsmodels` for regression prediction intervals
**Guarantee**: Exact under normality. Wider than confidence interval (accounts for individual variation).

```python
from scipy import stats
import numpy as np

def prediction_interval(data: np.ndarray, confidence: float = 0.95) -> dict:
    """Prediction interval for a new observation from the same population."""
    n = len(data)
    mean = np.mean(data)
    s = np.std(data, ddof=1)
    t_crit = stats.t.ppf((1 + confidence) / 2, df=n - 1)
    margin = t_crit * s * np.sqrt(1 + 1/n)
    return {
        "mean": mean, "interval": (mean - margin, mean + margin),
        "margin": margin, "note": "Wider than CI -- covers individual obs, not just mean",
    }
```

**Use when**: Forecasting a single value (next month's sales, individual patient outcome). Always wider than a confidence interval for the mean.

---

## 4. Regression

### S23: Simple Linear Regression (OLS)

**Problem**: Model relationship Y = β₀ + β₁X + ε between one predictor and one response.
**T**: O(n) | **S**: O(n)
**Lib**: `scipy.stats.linregress()`, `statsmodels.OLS()`
**Guarantee**: Best Linear Unbiased Estimator (BLUE) under Gauss-Markov conditions.

```python
from scipy import stats
import numpy as np

def simple_linear_regression(x, y) -> dict:
    """OLS regression: y = β₀ + β₁x + ε."""
    result = stats.linregress(x, y)
    y_pred = result.intercept + result.slope * np.array(x)
    residuals = np.array(y) - y_pred
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((np.array(y) - np.mean(y))**2)
    return {
        "slope": result.slope, "intercept": result.intercept,
        "r_squared": result.rvalue**2, "p_value": result.pvalue,
        "std_err": result.stderr, "residuals": residuals,
    }
```

**Use when**: Single predictor, linear relationship expected. Always check residual plots.

---

### S24: Multiple Linear Regression

**Problem**: Model Y = Xβ + ε with multiple predictors.
**T**: O(np²) for normal equations, O(np min(n,p)) for QR decomposition | **S**: O(np)
**Lib**: `statsmodels.OLS()`, `sklearn.linear_model.LinearRegression()`
**Guarantee**: BLUE under Gauss-Markov. statsmodels gives p-values, CIs, diagnostics.

```python
import statsmodels.api as sm
import numpy as np

def multiple_regression(X: np.ndarray, y: np.ndarray) -> dict:
    """Multiple OLS regression with full diagnostics."""
    X_const = sm.add_constant(X)
    model = sm.OLS(y, X_const).fit()
    return {
        "coefficients": model.params.tolist(),
        "p_values": model.pvalues.tolist(),
        "r_squared": model.rsquared,
        "adj_r_squared": model.rsquared_adj,
        "f_statistic": model.fvalue,
        "f_p_value": model.f_pvalue,
        "aic": model.aic, "bic": model.bic,
        "residuals": model.resid.tolist(),
        "summary": str(model.summary()),
    }
```

**Use when**: Multiple predictors. Use statsmodels (not sklearn) when you need p-values, confidence intervals, and diagnostic statistics.

---

### S25: Logistic Regression

**Problem**: Model P(Y=1|X) = sigmoid(Xβ) for binary outcomes.
**T**: O(np) per iteration, typically 10-50 iterations | **S**: O(np)
**Lib**: `statsmodels.Logit()`, `sklearn.linear_model.LogisticRegression()`
**Guarantee**: MLE. Asymptotically normal coefficients. Convergence not guaranteed for separable data.

```python
import statsmodels.api as sm
import numpy as np

def logistic_regression(X: np.ndarray, y: np.ndarray) -> dict:
    """Logistic regression with odds ratios and diagnostics."""
    X_const = sm.add_constant(X)
    model = sm.Logit(y, X_const).fit(disp=0)
    return {
        "coefficients": model.params.tolist(),
        "odds_ratios": np.exp(model.params).tolist(),
        "p_values": model.pvalues.tolist(),
        "conf_int": model.conf_int().tolist(),
        "pseudo_r_squared": model.prsquared,
        "aic": model.aic, "bic": model.bic,
        "summary": str(model.summary()),
    }
```

**Use when**: Binary outcome (churn/retain, buy/skip, pass/fail). Report odds ratios, not just coefficients. Check for separation.

---

### S26: Polynomial Regression

**Problem**: Model Y = β₀ + β₁X + β₂X² + ... + βₖXᵏ + ε.
**T**: O(nk²) | **S**: O(nk)
**Lib**: `numpy.polyfit()`, `sklearn.preprocessing.PolynomialFeatures()` + OLS
**Guarantee**: OLS on polynomial features. Risk of overfitting for high degree.

```python
import numpy as np
import statsmodels.api as sm

def polynomial_regression(x, y, degree: int = 2) -> dict:
    """Polynomial regression of specified degree."""
    X_poly = np.column_stack([np.array(x)**d for d in range(1, degree + 1)])
    X_const = sm.add_constant(X_poly)
    model = sm.OLS(y, X_const).fit()
    return {
        "degree": degree, "coefficients": model.params.tolist(),
        "r_squared": model.rsquared, "adj_r_squared": model.rsquared_adj,
        "aic": model.aic, "bic": model.bic,
    }
```

**Use when**: Nonlinear relationship but want to stay in the linear model framework. Use cross-validation to select degree. Prefer degree ≤ 3.

---

### S27: Ridge and Lasso Regression

**Problem**: Regularized regression to prevent overfitting when p is large or predictors are correlated.
**T**: O(np²) for Ridge (closed form), O(np * iterations) for Lasso (coordinate descent) | **S**: O(np)
**Lib**: `sklearn.linear_model.Ridge()`, `sklearn.linear_model.Lasso()`, `sklearn.linear_model.ElasticNet()`
**Guarantee**: Biased but lower MSE than OLS when multicollinearity exists. Lasso performs feature selection.

```python
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
import numpy as np

def regularized_regression(X, y, method: str = "ridge", alpha: float = 1.0) -> dict:
    """Ridge (L2), Lasso (L1), or ElasticNet regularized regression."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    models = {"ridge": Ridge, "lasso": Lasso, "elastic_net": ElasticNet}
    model = models[method](alpha=alpha)
    model.fit(X_scaled, y)
    cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring="r2")
    return {
        "method": method, "alpha": alpha,
        "coefficients": model.coef_.tolist(),
        "r_squared_train": model.score(X_scaled, y),
        "r_squared_cv_mean": cv_scores.mean(),
        "r_squared_cv_std": cv_scores.std(),
        "n_nonzero": np.sum(np.abs(model.coef_) > 1e-8),
    }
```

**Use when**: Many predictors (p > 20), multicollinearity, overfitting risk. Use Lasso for feature selection, Ridge for correlated predictors, ElasticNet for both.

---

### S28: Generalized Linear Models (GLM)

**Problem**: Extend regression to non-normal response distributions (Poisson, Gamma, Binomial) via link function.
**T**: O(np) per IRLS iteration | **S**: O(np)
**Lib**: `statsmodels.GLM()`, `sklearn.linear_model.PoissonRegressor()`
**Guarantee**: MLE. Asymptotically normal coefficients.

```python
import statsmodels.api as sm

def glm_regression(X, y, family: str = "poisson") -> dict:
    """GLM with specified family. Families: 'poisson', 'gamma', 'binomial'."""
    families = {
        "poisson": sm.families.Poisson(),
        "gamma": sm.families.Gamma(),
        "binomial": sm.families.Binomial(),
    }
    X_const = sm.add_constant(X)
    model = sm.GLM(y, X_const, family=families[family]).fit()
    return {
        "family": family, "link": str(model.family.link),
        "coefficients": model.params.tolist(),
        "p_values": model.pvalues.tolist(),
        "deviance": model.deviance,
        "aic": model.aic, "bic": model.bic,
        "summary": str(model.summary()),
    }
```

**Use when**: Count data (Poisson), positive continuous data (Gamma), rate data, overdispersed counts (Negative Binomial). Always check deviance residuals.

---

### S29: Quantile Regression

**Problem**: Model conditional quantiles (e.g., median, 90th percentile) instead of conditional mean.
**T**: O(np) per linear programming iteration | **S**: O(np)
**Lib**: `statsmodels.QuantReg()`
**Guarantee**: Asymptotically normal. Robust to outliers and heteroscedasticity.

```python
import statsmodels.api as sm
import numpy as np

def quantile_regression(X, y, quantile: float = 0.5) -> dict:
    """Quantile regression at specified quantile."""
    X_const = sm.add_constant(X)
    model = sm.QuantReg(y, X_const).fit(q=quantile)
    return {
        "quantile": quantile, "coefficients": model.params.tolist(),
        "p_values": model.pvalues.tolist(),
        "conf_int": model.conf_int().tolist(),
    }
```

**Use when**: Interested in extremes (90th percentile risk), heteroscedastic data, outlier-robust alternative to OLS. Useful for "worst case" or "best case" modeling.

---

### S30: Robust Regression

**Problem**: Regression resistant to outliers and influential observations.
**T**: O(np * iterations) | **S**: O(np)
**Lib**: `statsmodels.RLM()`, `sklearn.linear_model.HuberRegressor()`
**Guarantee**: M-estimators with bounded influence. Huber: 95% efficiency at normal, robust to outliers.

```python
import statsmodels.api as sm

def robust_regression(X, y) -> dict:
    """Robust regression using Huber's T norm (M-estimator)."""
    X_const = sm.add_constant(X)
    model = sm.RLM(y, X_const, M=sm.robust.norms.HuberT()).fit()
    return {
        "coefficients": model.params.tolist(),
        "p_values": model.pvalues.tolist(),
        "weights": model.weights.tolist(),  # observations with low weight are outliers
    }
```

**Use when**: Data contains outliers or influential points. Compare with OLS -- large differences indicate outlier sensitivity.

---

## 5. Bayesian Methods

### S31: Conjugate Prior Bayesian Estimation

**Problem**: Update prior beliefs with observed data using conjugate prior families (closed-form posteriors).
**T**: O(n) for sufficient statistic computation | **S**: O(1)
**Lib**: `scipy.stats` (for distribution evaluation)
**Guarantee**: Exact posterior (no approximation when using conjugate priors).

```python
from scipy import stats
import numpy as np

def bayesian_normal_mean(data: np.ndarray, prior_mean: float = 0,
                         prior_var: float = 100, known_var: float = 1) -> dict:
    """Bayesian estimation of normal mean with normal prior (conjugate)."""
    n = len(data)
    data_mean = np.mean(data)
    # Posterior parameters (conjugate update)
    post_var = 1 / (1/prior_var + n/known_var)
    post_mean = post_var * (prior_mean/prior_var + n*data_mean/known_var)
    post_std = np.sqrt(post_var)
    ci = (post_mean - 1.96*post_std, post_mean + 1.96*post_std)
    return {
        "prior": {"mean": prior_mean, "var": prior_var},
        "posterior": {"mean": post_mean, "var": post_var},
        "credible_interval_95": ci,
        "data_mean": data_mean, "n": n,
    }

def bayesian_proportion(successes: int, trials: int,
                        prior_alpha: float = 1, prior_beta: float = 1) -> dict:
    """Bayesian estimation of proportion with Beta prior (conjugate)."""
    post_alpha = prior_alpha + successes
    post_beta = prior_beta + trials - successes
    post_mean = post_alpha / (post_alpha + post_beta)
    ci = stats.beta.interval(0.95, post_alpha, post_beta)
    return {
        "prior": {"alpha": prior_alpha, "beta": prior_beta},
        "posterior": {"alpha": post_alpha, "beta": post_beta},
        "posterior_mean": post_mean,
        "credible_interval_95": ci,
    }
```

**Use when**: Standard scenarios with conjugate pairs (Normal-Normal, Beta-Binomial, Gamma-Poisson). Fast and exact. Good starting point before MCMC.

---

### S32: Maximum A Posteriori (MAP) Estimation

**Problem**: Find the mode of the posterior distribution (point estimate that combines prior and likelihood).
**T**: O(n * p) for optimization | **S**: O(p)
**Lib**: `scipy.optimize.minimize()`, `sklearn.linear_model.BayesianRidge()`
**Guarantee**: Point estimate only (no uncertainty quantification). Equivalent to regularized MLE.

```python
from scipy import optimize, stats
import numpy as np

def map_estimate_normal(data: np.ndarray, prior_mean: float = 0,
                        prior_std: float = 10) -> dict:
    """MAP estimate for normal mean with normal prior."""
    def neg_log_posterior(mu):
        log_likelihood = np.sum(stats.norm.logpdf(data, loc=mu, scale=np.std(data, ddof=1)))
        log_prior = stats.norm.logpdf(mu, loc=prior_mean, scale=prior_std)
        return -(log_likelihood + log_prior)
    result = optimize.minimize(neg_log_posterior, x0=np.mean(data))
    return {
        "map_estimate": result.x[0],
        "mle_estimate": np.mean(data),
        "prior_mean": prior_mean,
    }
```

**Use when**: Quick Bayesian point estimate. Ridge regression is MAP with normal prior. Lasso is MAP with Laplace prior.

---

### S33: Markov Chain Monte Carlo (MCMC)

**Problem**: Sample from the posterior distribution when conjugate forms don't exist.
**T**: O(n_samples * n * p) | **S**: O(n_samples * p)
**Lib**: `pymc.sample()`, `emcee.EnsembleSampler()`
**Guarantee**: Converges to true posterior with enough samples. Check convergence diagnostics (R-hat, ESS).

```python
import pymc as pm
import numpy as np

def bayesian_regression_mcmc(X, y, n_samples: int = 2000, seed: int = 42) -> dict:
    """Bayesian linear regression via MCMC (PyMC/NUTS)."""
    with pm.Model() as model:
        # Priors
        alpha = pm.Normal("intercept", mu=0, sigma=10)
        betas = pm.Normal("slopes", mu=0, sigma=10, shape=X.shape[1])
        sigma = pm.HalfNormal("sigma", sigma=1)
        # Likelihood
        mu = alpha + pm.math.dot(X, betas)
        y_obs = pm.Normal("y_obs", mu=mu, sigma=sigma, observed=y)
        # Sample
        trace = pm.sample(n_samples, random_seed=seed, return_inferencedata=True)
    summary = pm.summary(trace)
    return {
        "summary": summary.to_dict(),
        "r_hat_max": summary["r_hat"].max(),  # should be < 1.01
        "ess_min": summary["ess_bulk"].min(),  # should be > 400
        "converged": summary["r_hat"].max() < 1.01,
    }
```

**Use when**: Complex models without conjugate posteriors, hierarchical models, nonlinear models. Always check R-hat < 1.01 and ESS > 400.

---

### S34: Bayesian A/B Testing

**Problem**: Compare two proportions (conversion rates) with full posterior inference.
**T**: O(n + grid_size) for Beta posteriors | **S**: O(grid_size)
**Lib**: `scipy.stats.beta`
**Guarantee**: Exact posteriors for Beta-Binomial model.

```python
from scipy import stats
import numpy as np

def bayesian_ab_test(n_a: int, conv_a: int, n_b: int, conv_b: int,
                     prior_alpha: float = 1, prior_beta: float = 1,
                     n_simulations: int = 100000, seed: int = 42) -> dict:
    """Bayesian A/B test with Beta-Binomial model."""
    rng = np.random.default_rng(seed)
    # Posterior distributions
    post_a = stats.beta(prior_alpha + conv_a, prior_beta + n_a - conv_a)
    post_b = stats.beta(prior_alpha + conv_b, prior_beta + n_b - conv_b)
    # Monte Carlo probability that B > A
    samples_a = post_a.rvs(n_simulations, random_state=rng)
    samples_b = post_b.rvs(n_simulations, random_state=rng)
    prob_b_better = np.mean(samples_b > samples_a)
    lift = samples_b - samples_a
    return {
        "rate_a": conv_a / n_a, "rate_b": conv_b / n_b,
        "posterior_mean_a": post_a.mean(), "posterior_mean_b": post_b.mean(),
        "prob_b_better": prob_b_better,
        "expected_lift": np.mean(lift),
        "lift_ci_95": (np.percentile(lift, 2.5), np.percentile(lift, 97.5)),
        "credible_interval_a": post_a.interval(0.95),
        "credible_interval_b": post_b.interval(0.95),
    }
```

**Use when**: A/B test analysis. Gives "probability B is better than A" directly (more intuitive than p-values). No need for predetermined sample size.

---

### S35: Variational Inference

**Problem**: Approximate posterior by optimizing a simpler distribution (faster than MCMC).
**T**: O(iterations * n * p) | **S**: O(p²) for mean-field approximation
**Lib**: `pymc.fit(method='advi')`, `sklearn.linear_model.BayesianRidge()`
**Guarantee**: Approximate. Minimizes KL divergence to true posterior. May underestimate uncertainty.

```python
import pymc as pm

def variational_inference(X, y, n_iterations: int = 30000) -> dict:
    """Bayesian regression via variational inference (ADVI)."""
    with pm.Model() as model:
        alpha = pm.Normal("intercept", mu=0, sigma=10)
        betas = pm.Normal("slopes", mu=0, sigma=10, shape=X.shape[1])
        sigma = pm.HalfNormal("sigma", sigma=1)
        mu = alpha + pm.math.dot(X, betas)
        y_obs = pm.Normal("y_obs", mu=mu, sigma=sigma, observed=y)
        approx = pm.fit(n=n_iterations, method="advi")
        trace = approx.sample(2000)
    return {
        "method": "ADVI",
        "n_iterations": n_iterations,
        "elbo_loss": float(approx.hist[-1]),
    }
```

**Use when**: Same model as MCMC but need faster results. Large datasets where MCMC is too slow. Trade-off: faster but less accurate uncertainty estimates.

---

## 6. Estimation

### S36: Maximum Likelihood Estimation (MLE)

**Problem**: Find parameter values that maximize the likelihood of observed data.
**T**: O(n * iterations) for iterative methods | **S**: O(p)
**Lib**: `scipy.stats.fit()` (scipy ≥1.9), `scipy.optimize.minimize()`, `statsmodels`
**Guarantee**: Asymptotically unbiased, efficient, and normal. May find local optima.

```python
from scipy import stats, optimize
import numpy as np

def mle_fit(data: np.ndarray, distribution: str = "norm") -> dict:
    """Fit distribution parameters via MLE."""
    dist = getattr(stats, distribution)
    params = dist.fit(data)
    # Goodness of fit
    ks_stat, ks_p = stats.kstest(data, distribution, args=params)
    log_likelihood = np.sum(dist.logpdf(data, *params))
    k = len(params)
    n = len(data)
    aic = 2*k - 2*log_likelihood
    bic = k*np.log(n) - 2*log_likelihood
    return {
        "distribution": distribution, "params": params,
        "log_likelihood": log_likelihood,
        "aic": aic, "bic": bic,
        "ks_statistic": ks_stat, "ks_p_value": ks_p,
    }
```

**Use when**: Fitting parametric distributions to data, estimating model parameters. Foundation of most statistical inference.

---

### S37: Method of Moments Estimation

**Problem**: Estimate parameters by equating sample moments to population moments.
**T**: O(n) for moment computation + O(p) for solving equations | **S**: O(1)
**Lib**: `scipy.stats` (moments), `scipy.optimize` (equation solving)
**Guarantee**: Consistent but generally less efficient than MLE.

```python
import numpy as np

def method_of_moments_gamma(data: np.ndarray) -> dict:
    """Method of moments for Gamma(α, β) distribution."""
    mean = np.mean(data)
    var = np.var(data, ddof=1)
    # Gamma: E[X] = α/β, Var[X] = α/β²
    beta_hat = mean / var
    alpha_hat = mean * beta_hat
    return {"alpha": alpha_hat, "beta": beta_hat, "mean": mean, "variance": var}
```

**Use when**: Quick initial estimates, especially when MLE is computationally expensive. Good starting point for iterative MLE.

---

### S38: Expectation-Maximization (EM)

**Problem**: MLE when data has missing values or latent (hidden) variables.
**T**: O(n * k * iterations) for k components | **S**: O(n * k)
**Lib**: `sklearn.mixture.GaussianMixture()`, custom EM loops
**Guarantee**: Converges to local maximum of likelihood. Multiple restarts recommended.

```python
from sklearn.mixture import GaussianMixture
import numpy as np

def gaussian_mixture_em(data: np.ndarray, n_components: int = 2,
                        n_init: int = 10, seed: int = 42) -> dict:
    """Gaussian Mixture Model via EM algorithm."""
    gmm = GaussianMixture(n_components=n_components, n_init=n_init, random_state=seed)
    gmm.fit(data.reshape(-1, 1) if data.ndim == 1 else data)
    return {
        "n_components": n_components,
        "means": gmm.means_.flatten().tolist(),
        "variances": gmm.covariances_.flatten().tolist(),
        "weights": gmm.weights_.tolist(),
        "aic": gmm.aic(data.reshape(-1, 1) if data.ndim == 1 else data),
        "bic": gmm.bic(data.reshape(-1, 1) if data.ndim == 1 else data),
        "converged": gmm.converged_,
    }
```

**Use when**: Mixture models, clustering with soft assignments, handling missing data. Always run with multiple initializations.

---

### S39: Kaplan-Meier Survival Estimation

**Problem**: Estimate survival function S(t) = P(T > t) from censored time-to-event data.
**T**: O(n log n) | **S**: O(n)
**Lib**: `lifelines.KaplanMeierFitter()`
**Guarantee**: Nonparametric. Consistent. Greenwood's formula for confidence bands.

```python
from lifelines import KaplanMeierFitter

def kaplan_meier(durations, event_observed, label: str = "KM Estimate") -> dict:
    """Kaplan-Meier survival curve estimation."""
    kmf = KaplanMeierFitter()
    kmf.fit(durations, event_observed=event_observed, label=label)
    median_survival = kmf.median_survival_time_
    return {
        "median_survival": median_survival,
        "survival_at_times": kmf.survival_function_.to_dict(),
        "confidence_interval": kmf.confidence_interval_.to_dict(),
    }
```

**Use when**: Time-to-event data with censoring (customer churn, equipment failure, patient survival). Cannot use standard statistics because of censored observations.

---

### S40: Cox Proportional Hazards

**Problem**: Model the effect of covariates on hazard (risk) rate: h(t|X) = h₀(t) * exp(Xβ).
**T**: O(np + n log n) per Newton-Raphson iteration | **S**: O(np)
**Lib**: `lifelines.CoxPHFitter()`
**Guarantee**: Semiparametric. Partial likelihood MLE. Check proportional hazards assumption.

```python
from lifelines import CoxPHFitter
import pandas as pd

def cox_regression(df: pd.DataFrame, duration_col: str, event_col: str) -> dict:
    """Cox proportional hazards regression."""
    cph = CoxPHFitter()
    cph.fit(df, duration_col=duration_col, event_col=event_col)
    return {
        "hazard_ratios": cph.hazard_ratios_.to_dict(),
        "p_values": cph.summary["p"].to_dict(),
        "concordance": cph.concordance_index_,
        "summary": str(cph.summary),
    }
```

**Use when**: Survival analysis with covariates (which factors predict churn? which features predict failure?). Report hazard ratios.

---

## 7. Resampling & Validation

### S41: Bootstrap Estimation

**Problem**: Estimate the sampling distribution of any statistic by resampling with replacement.
**T**: O(B * n) for B bootstrap samples of size n | **S**: O(B)
**Lib**: `scipy.stats.bootstrap()`, `sklearn.utils.resample()`
**Guarantee**: Asymptotically valid for smooth statistics. Minimum B = 1000, recommended B = 10000.

```python
from scipy import stats
import numpy as np

def bootstrap_statistic(data: np.ndarray, statistic_fn, n_bootstrap: int = 10000,
                        seed: int = 42) -> dict:
    """Bootstrap distribution of any statistic."""
    rng = np.random.default_rng(seed)
    boot_stats = np.array([
        statistic_fn(rng.choice(data, size=len(data), replace=True))
        for _ in range(n_bootstrap)
    ])
    return {
        "estimate": statistic_fn(data),
        "bootstrap_mean": np.mean(boot_stats),
        "bootstrap_se": np.std(boot_stats, ddof=1),
        "ci_percentile": (np.percentile(boot_stats, 2.5), np.percentile(boot_stats, 97.5)),
    }
```

**Use when**: Any statistic (median, ratio, custom metric) where analytical SE is hard. Model-free uncertainty quantification.

---

### S42: Jackknife Estimation

**Problem**: Estimate bias and variance of a statistic by systematically leaving one observation out.
**T**: O(n²) for n leave-one-out recomputes | **S**: O(n)
**Lib**: Custom (numpy-based)
**Guarantee**: First-order bias correction. Less flexible than bootstrap but more systematic.

```python
import numpy as np

def jackknife(data: np.ndarray, statistic_fn) -> dict:
    """Jackknife estimate of bias and variance."""
    n = len(data)
    theta_hat = statistic_fn(data)
    theta_jack = np.array([
        statistic_fn(np.delete(data, i)) for i in range(n)
    ])
    theta_bar = np.mean(theta_jack)
    bias = (n - 1) * (theta_bar - theta_hat)
    variance = (n - 1) / n * np.sum((theta_jack - theta_bar)**2)
    return {
        "estimate": theta_hat,
        "bias": bias,
        "bias_corrected": theta_hat - bias,
        "se": np.sqrt(variance),
    }
```

**Use when**: Estimating bias and SE. Identifying influential observations (large jackknife pseudovalues = influential points).

---

### S43: K-Fold Cross-Validation

**Problem**: Estimate out-of-sample prediction performance by splitting data into k folds.
**T**: O(k * T_model) where T_model = model training time | **S**: O(n)
**Lib**: `sklearn.model_selection.cross_val_score()`, `sklearn.model_selection.KFold()`
**Guarantee**: Nearly unbiased estimator of generalization error. k=5 or k=10 is standard.

```python
from sklearn.model_selection import cross_val_score, KFold
from sklearn.linear_model import LinearRegression
import numpy as np

def cross_validate(X, y, model=None, k: int = 5, scoring: str = "r2",
                   seed: int = 42) -> dict:
    """K-fold cross-validation with specified metric."""
    if model is None:
        model = LinearRegression()
    cv = KFold(n_splits=k, shuffle=True, random_state=seed)
    scores = cross_val_score(model, X, y, cv=cv, scoring=scoring)
    return {
        "k": k, "scoring": scoring,
        "scores": scores.tolist(),
        "mean": scores.mean(), "std": scores.std(),
        "ci_95": (scores.mean() - 1.96*scores.std(), scores.mean() + 1.96*scores.std()),
    }
```

**Use when**: Evaluating any predictive model. Always use cross-validation instead of train-only metrics. Use stratified CV for classification.

---

### S44: Power Analysis

**Problem**: Determine the sample size needed to detect an effect of specified size with specified probability.
**T**: O(1) for analytical, O(iterations) for simulation-based | **S**: O(1)
**Lib**: `statsmodels.stats.power` (TTestPower, NormalIndPower, etc.)
**Guarantee**: Exact for standard tests. Approximate for complex designs.

```python
from statsmodels.stats.power import TTestIndPower, NormalIndPower

def sample_size_ttest(effect_size: float, alpha: float = 0.05, power: float = 0.8,
                      ratio: float = 1.0) -> dict:
    """Required sample size for two-sample t-test."""
    analysis = TTestIndPower()
    n = analysis.solve_power(effect_size=effect_size, alpha=alpha, power=power, ratio=ratio)
    return {
        "effect_size_d": effect_size, "alpha": alpha, "power": power,
        "n_per_group": int(np.ceil(n)),
        "n_total": int(np.ceil(n)) + int(np.ceil(n * ratio)),
    }

def sample_size_proportion(p1: float, p2: float, alpha: float = 0.05,
                           power: float = 0.8) -> dict:
    """Required sample size for two-proportion z-test."""
    from statsmodels.stats.power import NormalIndPower
    import numpy as np
    effect_size = 2 * (np.arcsin(np.sqrt(p1)) - np.arcsin(np.sqrt(p2)))  # Cohen's h
    analysis = NormalIndPower()
    n = analysis.solve_power(effect_size=abs(effect_size), alpha=alpha, power=power)
    return {
        "p1": p1, "p2": p2, "cohens_h": effect_size,
        "n_per_group": int(np.ceil(n)),
    }
```

**Use when**: Before running an experiment. "How many users do I need in my A/B test?" Always compute power before collecting data.

---

### S45: Effect Size Computation

**Problem**: Quantify the magnitude of a difference or relationship, independent of sample size.
**T**: O(n) | **S**: O(1)
**Lib**: `pingouin.compute_effsize()`, custom
**Guarantee**: Exact computation. Effect size is not affected by sample size (unlike p-values).

```python
import numpy as np

def effect_sizes(group1, group2) -> dict:
    """Compute multiple effect size measures."""
    n1, n2 = len(group1), len(group2)
    m1, m2 = np.mean(group1), np.mean(group2)
    s1, s2 = np.std(group1, ddof=1), np.std(group2, ddof=1)
    # Cohen's d (pooled SD)
    pooled_sd = np.sqrt(((n1-1)*s1**2 + (n2-1)*s2**2) / (n1+n2-2))
    cohens_d = (m1 - m2) / pooled_sd
    # Hedges' g (bias-corrected)
    correction = 1 - 3 / (4*(n1+n2) - 9)
    hedges_g = cohens_d * correction
    # Glass's delta (use control group SD)
    glass_delta = (m1 - m2) / s2
    # Common Language Effect Size (probability superiority)
    from scipy import stats
    cles = stats.norm.cdf(cohens_d / np.sqrt(2))
    return {
        "cohens_d": cohens_d, "hedges_g": hedges_g,
        "glass_delta": glass_delta, "cles": cles,
        "interpretation": _interpret_d(abs(cohens_d)),
    }

def _interpret_d(d: float) -> str:
    if d < 0.2: return "negligible"
    elif d < 0.5: return "small"
    elif d < 0.8: return "medium"
    else: return "large"
```

**Use when**: Always. Every hypothesis test should report effect size alongside p-value. P-values depend on sample size; effect sizes do not.

---

## 8. Time Series Analysis

### S46: ARIMA (AutoRegressive Integrated Moving Average)

**Problem**: Forecast a univariate time series using autoregressive, differencing, and moving average components.
**T**: O(n · p²) for fitting via MLE | **S**: O(n)
**Lib**: `statsmodels.tsa.arima.model.ARIMA`
**Guarantee**: MLE estimates are asymptotically efficient. Forecast uncertainty via analytic confidence intervals.

```python
from statsmodels.tsa.arima.model import ARIMA
import numpy as np

def arima_forecast(data: np.ndarray, order: tuple[int,int,int] = (1,1,1),
                   steps: int = 12) -> dict:
    """Fit ARIMA(p,d,q) and produce forecasts with confidence intervals."""
    model = ARIMA(data, order=order)
    result = model.fit()
    forecast = result.get_forecast(steps=steps)
    ci = forecast.conf_int(alpha=0.05)
    return {
        "order": order, "aic": result.aic, "bic": result.bic,
        "forecast_mean": forecast.predicted_mean.values,
        "ci_lower": ci.iloc[:, 0].values,
        "ci_upper": ci.iloc[:, 1].values,
        "residual_std": np.std(result.resid),
        "ljung_box_pvalue": float(result.test_serial_correlation("ljungbox")[0][0, 1]),
    }
```

**Use when**: Univariate time series with trend and/or autocorrelation. First-line forecasting method. Use AIC/BIC for order selection or `pmdarima.auto_arima()` for automatic selection.

---

### S47: SARIMA (Seasonal ARIMA)

**Problem**: Forecast a univariate time series with both trend and seasonal patterns.
**T**: O(n · (p+P)²) for fitting | **S**: O(n)
**Lib**: `statsmodels.tsa.statespace.sarimax.SARIMAX`
**Guarantee**: MLE estimates; analytic forecast intervals account for both trend and seasonal uncertainty.

```python
from statsmodels.tsa.statespace.sarimax import SARIMAX
import numpy as np

def sarima_forecast(data: np.ndarray, order: tuple = (1,1,1),
                    seasonal_order: tuple = (1,1,1,12),
                    steps: int = 12) -> dict:
    """Fit SARIMA(p,d,q)(P,D,Q,s) and forecast."""
    model = SARIMAX(data, order=order, seasonal_order=seasonal_order,
                    enforce_stationarity=False, enforce_invertibility=False)
    result = model.fit(disp=False)
    forecast = result.get_forecast(steps=steps)
    ci = forecast.conf_int(alpha=0.05)
    return {
        "order": order, "seasonal_order": seasonal_order,
        "aic": result.aic, "bic": result.bic,
        "forecast_mean": forecast.predicted_mean.values,
        "ci_lower": ci.iloc[:, 0].values,
        "ci_upper": ci.iloc[:, 1].values,
    }
```

**Use when**: Monthly/quarterly/weekly data with clear seasonality (sales, temperature, energy usage). The `s` parameter is the seasonal period (12=monthly, 4=quarterly, 7=daily-weekly).

---

### S48: Exponential Smoothing (SES, Holt, Holt-Winters)

**Problem**: Forecast a time series using weighted averages of past observations with exponentially decaying weights.
**T**: O(n) per iteration, O(n · iterations) total | **S**: O(n)
**Lib**: `statsmodels.tsa.holtwinters.ExponentialSmoothing`
**Guarantee**: MLE/least-squares parameter estimation. Prediction intervals via simulation or analytical approximation.

```python
from statsmodels.tsa.holtwinters import ExponentialSmoothing, SimpleExpSmoothing
import numpy as np

def exponential_smoothing_forecast(data: np.ndarray, seasonal_periods: int | None = 12,
                                    trend: str | None = "add",
                                    seasonal: str | None = "add",
                                    steps: int = 12) -> dict:
    """Fit Holt-Winters exponential smoothing and forecast."""
    if seasonal_periods and seasonal:
        model = ExponentialSmoothing(data, trend=trend, seasonal=seasonal,
                                      seasonal_periods=seasonal_periods)
    elif trend:
        model = ExponentialSmoothing(data, trend=trend, seasonal=None)
    else:
        model = SimpleExpSmoothing(data)
    result = model.fit(optimized=True)
    fcast = result.forecast(steps)
    return {
        "smoothing_level": result.params.get("smoothing_level"),
        "smoothing_trend": result.params.get("smoothing_trend"),
        "smoothing_seasonal": result.params.get("smoothing_seasonal"),
        "aic": result.aic, "bic": result.bic,
        "forecast": fcast.values,
        "sse": result.sse,
    }
```

**Use when**: Simple, interpretable forecasts. SES for level-only data, Holt for trend, Holt-Winters for trend+seasonality. Often competitive with ARIMA for short horizons.

---

### S49: Time Series Decomposition

**Problem**: Decompose a time series into trend, seasonal, and residual components.
**T**: O(n · window) for classical, O(n log n) for STL | **S**: O(n)
**Lib**: `statsmodels.tsa.seasonal.seasonal_decompose`, `statsmodels.tsa.seasonal.STL`
**Guarantee**: Deterministic decomposition. STL is robust to outliers.

```python
from statsmodels.tsa.seasonal import seasonal_decompose, STL
import numpy as np

def decompose_series(data, period: int = 12, method: str = "stl") -> dict:
    """Decompose time series into trend, seasonal, residual."""
    if method == "stl":
        stl = STL(data, period=period, robust=True)
        result = stl.fit()
    else:
        result = seasonal_decompose(data, model="additive", period=period)
    return {
        "trend": result.trend, "seasonal": result.seasonal,
        "residual": result.resid, "method": method,
        "seasonal_strength": 1 - np.nanvar(result.resid) / np.nanvar(result.seasonal + result.resid),
        "trend_strength": 1 - np.nanvar(result.resid) / np.nanvar(result.trend + result.resid),
    }
```

**Use when**: Understanding what drives a time series before modeling. STL (Seasonal and Trend decomposition using LOESS) is preferred over classical decomposition -- handles varying seasonality and is robust.

---

### S50: ACF / PACF Analysis

**Problem**: Identify autocorrelation structure to determine appropriate model orders (p, q for ARIMA).
**T**: O(n · max_lag) | **S**: O(max_lag)
**Lib**: `statsmodels.tsa.stattools.acf`, `statsmodels.tsa.stattools.pacf`
**Guarantee**: Exact sample autocorrelation. Confidence bands under white noise null.

```python
from statsmodels.tsa.stattools import acf, pacf
import numpy as np

def autocorrelation_analysis(data: np.ndarray, nlags: int = 40) -> dict:
    """Compute ACF and PACF with confidence intervals."""
    acf_vals, acf_ci = acf(data, nlags=nlags, alpha=0.05)
    pacf_vals, pacf_ci = pacf(data, nlags=nlags, alpha=0.05)
    n = len(data)
    sig_threshold = 1.96 / np.sqrt(n)
    significant_acf = [i for i in range(1, nlags+1) if abs(acf_vals[i]) > sig_threshold]
    significant_pacf = [i for i in range(1, nlags+1) if abs(pacf_vals[i]) > sig_threshold]
    return {
        "acf": acf_vals, "pacf": pacf_vals,
        "acf_ci": acf_ci, "pacf_ci": pacf_ci,
        "significant_acf_lags": significant_acf,
        "significant_pacf_lags": significant_pacf,
        "suggested_q": max(significant_acf) if significant_acf else 0,
        "suggested_p": max(significant_pacf) if significant_pacf else 0,
    }
```

**Use when**: Before fitting ARIMA. ACF tailing off + PACF cutting off at lag p → AR(p). ACF cutting off at lag q + PACF tailing off → MA(q). Both tailing off → ARMA(p,q).

---

### S51: Stationarity Tests (ADF, KPSS)

**Problem**: Test whether a time series is stationary (constant mean and variance over time).
**T**: O(n · max_lag) | **S**: O(n)
**Lib**: `statsmodels.tsa.stattools.adfuller`, `statsmodels.tsa.stattools.kpss`
**Guarantee**: Asymptotic p-values. ADF tests null=unit root; KPSS tests null=stationary. Use both for confirmation.

```python
from statsmodels.tsa.stattools import adfuller, kpss
import numpy as np

def stationarity_tests(data: np.ndarray) -> dict:
    """Run ADF and KPSS tests for stationarity."""
    adf_stat, adf_p, adf_lags, adf_nobs, adf_cv, _ = adfuller(data, autolag="AIC")
    kpss_stat, kpss_p, kpss_lags, kpss_cv = kpss(data, regression="c", nlags="auto")
    return {
        "adf_statistic": adf_stat, "adf_pvalue": adf_p, "adf_lags": adf_lags,
        "adf_critical_values": adf_cv,
        "adf_stationary": adf_p < 0.05,
        "kpss_statistic": kpss_stat, "kpss_pvalue": kpss_p,
        "kpss_critical_values": kpss_cv,
        "kpss_stationary": kpss_p > 0.05,
        "consensus": "stationary" if (adf_p < 0.05 and kpss_p > 0.05)
                     else "non-stationary" if (adf_p >= 0.05 and kpss_p <= 0.05)
                     else "trend-stationary" if (adf_p < 0.05 and kpss_p <= 0.05)
                     else "inconclusive",
    }
```

**Use when**: Before fitting ARIMA. If non-stationary, difference the series (d=1 or d=2). ADF and KPSS can disagree -- the consensus logic resolves this.

---

### S52: Granger Causality Test

**Problem**: Test whether one time series is useful for forecasting another (predictive causality, not true causality).
**T**: O(n · max_lag · k²) for VAR estimation | **S**: O(n · k)
**Lib**: `statsmodels.tsa.stattools.grangercausalitytests`
**Guarantee**: Asymptotic F-test or chi-squared test. Requires stationarity.

```python
from statsmodels.tsa.stattools import grangercausalitytests
import numpy as np

def granger_causality(x: np.ndarray, y: np.ndarray, max_lag: int = 12) -> dict:
    """Test if x Granger-causes y (i.e., past x helps predict y)."""
    data = np.column_stack([y, x])  # target first, predictor second
    results = grangercausalitytests(data, maxlag=max_lag, verbose=False)
    best_lag = min(results, key=lambda k: results[k][0]["ssr_ftest"][1])
    f_stat, p_value, df_denom, df_num = results[best_lag][0]["ssr_ftest"]
    return {
        "best_lag": best_lag, "f_statistic": f_stat, "p_value": p_value,
        "granger_causes": p_value < 0.05,
        "all_lags": {k: results[k][0]["ssr_ftest"][1] for k in results},
    }
```

**Use when**: "Does advertising spend predict sales?" "Does weather predict energy usage?" Requires both series to be stationary first. Does NOT imply true causation.

---

### S53: Vector Autoregression (VAR)

**Problem**: Model and forecast multiple interrelated time series simultaneously.
**T**: O(n · k² · p) for fitting k series with p lags | **S**: O(n · k)
**Lib**: `statsmodels.tsa.api.VAR`
**Guarantee**: OLS estimates are consistent and asymptotically normal for stationary data.

```python
from statsmodels.tsa.api import VAR
import numpy as np
import pandas as pd

def var_forecast(data: pd.DataFrame, max_lag: int = 12, steps: int = 12) -> dict:
    """Fit VAR model and forecast all variables jointly."""
    model = VAR(data)
    lag_order = model.select_order(maxlags=max_lag)
    best_p = lag_order.selected_orders["aic"]
    result = model.fit(best_p)
    forecast = result.forecast(data.values[-best_p:], steps=steps)
    irf = result.irf(periods=20)
    return {
        "lag_order": best_p, "aic": result.aic, "bic": result.bic,
        "forecast": pd.DataFrame(forecast, columns=data.columns),
        "granger_causality": {col: result.test_causality(col, verbose=False).pvalue
                              for col in data.columns},
        "impulse_response": irf.irfs,
    }
```

**Use when**: Multiple related time series where cross-variable effects matter. "Sales and advertising," "GDP, inflation, interest rates." All series must be stationary.

---

### S54: GARCH (Generalized Autoregressive Conditional Heteroskedasticity)

**Problem**: Model and forecast time-varying volatility (variance) in a time series.
**T**: O(n · iterations) for MLE | **S**: O(n)
**Lib**: `arch.arch_model`
**Guarantee**: Quasi-MLE estimates. Robust standard errors available.

```python
from arch import arch_model
import numpy as np

def garch_volatility(returns: np.ndarray, p: int = 1, q: int = 1) -> dict:
    """Fit GARCH(p,q) model to return series and forecast volatility."""
    model = arch_model(returns, vol="Garch", p=p, q=q, mean="Constant")
    result = model.fit(disp="off")
    forecast = result.forecast(horizon=5)
    return {
        "omega": result.params["omega"],
        "alpha": [result.params[f"alpha[{i+1}]"] for i in range(q)],
        "beta": [result.params[f"beta[{i+1}]"] for i in range(p)],
        "conditional_volatility": result.conditional_volatility.values,
        "forecast_variance": forecast.variance.values[-1],
        "aic": result.aic, "bic": result.bic,
        "persistence": sum(result.params[f"alpha[{i+1}]"] for i in range(q))
                      + sum(result.params[f"beta[{i+1}]"] for i in range(p)),
    }
```

**Use when**: Financial return series, risk management. Volatility clustering ("calm and stormy periods"). Persistence close to 1 = highly persistent volatility.

---

### S55: Prophet (Time Series Forecasting)

**Problem**: Forecast time series with strong seasonal effects and multiple seasonalities, handling missing data and holidays.
**T**: O(n · iterations) for MAP estimation | **S**: O(n)
**Lib**: `prophet.Prophet`
**Guarantee**: Bayesian MAP estimation. Uncertainty intervals via posterior sampling.

```python
from prophet import Prophet
import pandas as pd

def prophet_forecast(df: pd.DataFrame, periods: int = 30,
                     freq: str = "D") -> dict:
    """Forecast with Prophet. Input df must have 'ds' (date) and 'y' (value) columns."""
    model = Prophet(yearly_seasonality=True, weekly_seasonality=True,
                    daily_seasonality=False, changepoint_prior_scale=0.05)
    model.fit(df)
    future = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)
    return {
        "forecast": forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]],
        "trend": forecast["trend"],
        "seasonal_components": {col: forecast[col] for col in forecast.columns
                                if "weekly" in col or "yearly" in col},
        "changepoints": model.changepoints.tolist(),
        "growth": model.growth,
    }
```

**Use when**: Business forecasting with daily/weekly data, holidays, and multiple seasonalities. Handles missing data and outliers gracefully. Good for non-technical stakeholders (interpretable components).

---

### S56: Change Point Detection

**Problem**: Identify points in a time series where the statistical properties (mean, variance, trend) change abruptly.
**T**: O(n²) for exact (PELT), O(n log n) for approximate | **S**: O(n)
**Lib**: `ruptures` (PELT, BinSeg, BottomUp, Window)
**Guarantee**: PELT finds exact solution for penalized cost. BinSeg is approximate but faster.

```python
import ruptures as rpt
import numpy as np

def detect_changepoints(data: np.ndarray, method: str = "pelt",
                        model: str = "rbf", pen: float | None = None) -> dict:
    """Detect change points using ruptures library."""
    n = len(data)
    if pen is None:
        pen = np.log(n) * np.var(data)  # BIC-like penalty
    if method == "pelt":
        algo = rpt.Pelt(model=model, min_size=2).fit(data)
        bkps = algo.predict(pen=pen)
    elif method == "binseg":
        algo = rpt.Binseg(model=model).fit(data)
        bkps = algo.predict(pen=pen)
    else:
        algo = rpt.BottomUp(model=model).fit(data)
        bkps = algo.predict(pen=pen)
    return {
        "changepoints": bkps[:-1],  # exclude last (= n)
        "n_changes": len(bkps) - 1,
        "segments": [(0 if i == 0 else bkps[i-1], bkps[i])
                     for i in range(len(bkps))],
        "method": method, "penalty": pen,
    }
```

**Use when**: "When did the trend shift?" "When did the process go out of control?" Manufacturing quality control, website traffic regime changes, financial regime detection.

---

### S57: Time Series Anomaly Detection

**Problem**: Identify unusual observations (outliers) or unusual segments in a time series.
**T**: O(n) for statistical methods, O(n log n) for Isolation Forest | **S**: O(n)
**Lib**: `scipy.stats`, `sklearn.ensemble.IsolationForest`, custom
**Guarantee**: Statistical methods have known false positive rates. ML methods are approximate.

```python
import numpy as np
from scipy import stats

def detect_anomalies(data: np.ndarray, window: int = 20,
                     z_threshold: float = 3.0) -> dict:
    """Detect anomalies using rolling statistics and z-scores."""
    rolling_mean = np.convolve(data, np.ones(window)/window, mode="same")
    rolling_std = np.array([np.std(data[max(0,i-window):i+1]) for i in range(len(data))])
    rolling_std[rolling_std < 1e-10] = 1e-10  # avoid division by zero
    z_scores = (data - rolling_mean) / rolling_std
    anomaly_mask = np.abs(z_scores) > z_threshold
    # IQR method
    q1, q3 = np.percentile(data, [25, 75])
    iqr = q3 - q1
    iqr_mask = (data < q1 - 1.5 * iqr) | (data > q3 + 1.5 * iqr)
    return {
        "z_score_anomalies": np.where(anomaly_mask)[0].tolist(),
        "iqr_anomalies": np.where(iqr_mask)[0].tolist(),
        "z_scores": z_scores,
        "n_zscore_anomalies": int(anomaly_mask.sum()),
        "n_iqr_anomalies": int(iqr_mask.sum()),
    }
```

**Use when**: Monitoring systems (server metrics, sensor data, fraud detection). Combine statistical methods (z-score, IQR) with ML methods (Isolation Forest) for robustness.

---

### S58: Moving Average / Smoothing

**Problem**: Smooth a noisy time series to reveal underlying trends and patterns.
**T**: O(n · window) for simple, O(n) for exponential | **S**: O(n)
**Lib**: `pandas.Series.rolling`, `scipy.signal.savgol_filter`
**Guarantee**: Deterministic transformation. Window size controls bias-variance tradeoff.

```python
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

def smooth_series(data: np.ndarray, window: int = 7,
                  method: str = "sma") -> dict:
    """Smooth time series using various methods."""
    series = pd.Series(data)
    if method == "sma":
        smoothed = series.rolling(window=window, center=True).mean().values
    elif method == "ema":
        smoothed = series.ewm(span=window, adjust=False).mean().values
    elif method == "savgol":
        smoothed = savgol_filter(data, window_length=window if window % 2 == 1 else window+1,
                                  polyorder=2)
    else:
        raise ValueError(f"Unknown method: {method}")
    residual = data - np.nan_to_num(smoothed, nan=data.mean())
    return {
        "smoothed": smoothed, "residual": residual, "method": method,
        "window": window, "residual_std": np.nanstd(residual),
    }
```

**Use when**: Noise reduction before visual analysis or feature extraction. SMA for equal weighting, EMA for recency weighting, Savitzky-Golay for preserving peaks/shapes.

---

### S59: Spectral Analysis (Periodogram)

**Problem**: Identify dominant frequencies and periodicities in a time series.
**T**: O(n log n) via FFT | **S**: O(n)
**Lib**: `scipy.signal.periodogram`, `scipy.signal.welch`
**Guarantee**: Consistent spectral density estimation with Welch's method.

```python
from scipy.signal import periodogram, welch
import numpy as np

def spectral_analysis(data: np.ndarray, fs: float = 1.0) -> dict:
    """Compute power spectral density and dominant periods."""
    freqs, psd = welch(data, fs=fs, nperseg=min(256, len(data)))
    # Find dominant frequencies (peaks in PSD)
    from scipy.signal import find_peaks
    peaks, properties = find_peaks(psd, height=np.median(psd) * 3)
    dominant_freqs = freqs[peaks]
    dominant_periods = 1.0 / dominant_freqs[dominant_freqs > 0]
    return {
        "frequencies": freqs, "psd": psd,
        "dominant_frequencies": dominant_freqs.tolist(),
        "dominant_periods": sorted(dominant_periods.tolist(), reverse=True),
        "spectral_entropy": -np.sum((psd/psd.sum()) * np.log2(psd/psd.sum() + 1e-12)),
    }
```

**Use when**: "What's the cycle length?" Identifying seasonality periods before SARIMA. Signal processing, vibration analysis, biological rhythms.

---

### S60: Intervention Analysis

**Problem**: Assess the causal impact of a known event or intervention on a time series.
**T**: O(n · p²) for ARIMA with intervention | **S**: O(n)
**Lib**: `statsmodels.tsa.arima.model.ARIMA` with exogenous variables, `causalimpact`
**Guarantee**: Conditional on correct model specification. Bayesian structural time series provides uncertainty.

```python
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

def intervention_analysis(data: np.ndarray, intervention_point: int,
                          order: tuple = (1,0,0)) -> dict:
    """Assess impact of intervention using ARIMA with step dummy variable."""
    n = len(data)
    step = np.zeros(n)
    step[intervention_point:] = 1.0
    model = ARIMA(data, order=order, exog=step)
    result = model.fit()
    intervention_effect = result.params[-1]
    se = result.bse[-1]
    p_value = result.pvalues[-1]
    return {
        "intervention_effect": intervention_effect,
        "standard_error": se, "p_value": p_value,
        "significant": p_value < 0.05,
        "ci_lower": intervention_effect - 1.96 * se,
        "ci_upper": intervention_effect + 1.96 * se,
        "pre_mean": np.mean(data[:intervention_point]),
        "post_mean": np.mean(data[intervention_point:]),
        "aic": result.aic,
    }
```

**Use when**: "Did the marketing campaign increase sales?" "Did the policy change affect crime rates?" Requires knowing WHEN the intervention happened. Pre-post comparison with temporal modeling.

---

## 9. Stochastic Processes

### S61: Continuous-Time Markov Chain (CTMC)

**Problem**: Model a system that transitions between discrete states at random times with memoryless (exponential) holding times.
**T**: O(k³) for matrix exponential (k states) | **S**: O(k²)
**Lib**: `scipy.linalg.expm`, `numpy.linalg.eig`
**Guarantee**: Exact transient and steady-state probabilities via matrix exponential and generator matrix.

```python
import numpy as np
from scipy.linalg import expm

def ctmc_analysis(Q: np.ndarray, initial_state: int, t: float) -> dict:
    """Analyze CTMC with generator matrix Q at time t."""
    k = Q.shape[0]
    # Transient probabilities: P(t) = exp(Qt)
    P_t = expm(Q * t)
    # Steady-state: solve pi @ Q = 0, sum(pi) = 1
    A = np.vstack([Q.T, np.ones(k)])
    b = np.zeros(k + 1)
    b[-1] = 1.0
    pi = np.linalg.lstsq(A, b, rcond=None)[0]
    # Expected holding times
    holding_times = -1.0 / np.diag(Q)
    return {
        "transient_probs": P_t[initial_state],
        "steady_state": pi,
        "holding_times": holding_times,
        "transition_matrix_at_t": P_t,
    }
```

**Use when**: Queuing systems (M/M/1, M/M/c), reliability (component up/down), biological models. Generator matrix Q has non-negative off-diagonals and rows summing to 0.

---

### S62: Birth-Death Process

**Problem**: Model a population or queue that changes by +1 (birth/arrival) or -1 (death/departure) at exponential rates.
**T**: O(k) for steady-state, O(k³) for transient | **S**: O(k)
**Lib**: Custom + `scipy.linalg.expm`
**Guarantee**: Exact steady-state via balance equations. Transient via matrix exponential.

```python
import numpy as np

def birth_death_steady_state(birth_rates: list[float],
                              death_rates: list[float]) -> dict:
    """Compute steady-state distribution of a birth-death process."""
    k = len(birth_rates) + 1  # states 0, 1, ..., k-1
    # Balance equations: pi[n+1] = (lambda_n / mu_{n+1}) * pi[n]
    pi = np.zeros(k)
    pi[0] = 1.0
    for n in range(k - 1):
        pi[n + 1] = pi[n] * birth_rates[n] / death_rates[n]
    pi /= pi.sum()  # normalize
    # Performance metrics
    mean_pop = sum(n * pi[n] for n in range(k))
    return {
        "steady_state": pi, "mean_population": mean_pop,
        "prob_empty": pi[0], "prob_full": pi[-1],
        "utilization": 1 - pi[0],
    }
```

**Use when**: M/M/1 and M/M/c queuing models, population dynamics with immigration/emigration. Birth rates = arrival rates, death rates = service rates.

---

### S63: Poisson Process Analysis

**Problem**: Model events occurring randomly in time at a constant (or varying) average rate.
**T**: O(n) for estimation, O(1) for probabilities | **S**: O(n)
**Lib**: `scipy.stats.poisson`, `scipy.stats.expon`, custom
**Guarantee**: Exact under Poisson assumptions. Goodness-of-fit via chi-squared or KS test.

```python
import numpy as np
from scipy import stats

def poisson_process_analysis(event_times: np.ndarray,
                              observation_period: float) -> dict:
    """Analyze a Poisson process from observed event times."""
    n_events = len(event_times)
    rate = n_events / observation_period  # MLE of lambda
    inter_arrivals = np.diff(np.sort(event_times))
    # Test exponentiality of inter-arrival times
    ks_stat, ks_p = stats.kstest(inter_arrivals, "expon", args=(0, 1/rate))
    # Probability computations
    return {
        "estimated_rate": rate,
        "mean_inter_arrival": 1.0 / rate if rate > 0 else float("inf"),
        "n_events": n_events,
        "exponentiality_test_p": ks_p,
        "is_poisson": ks_p > 0.05,
        "prob_0_in_unit": stats.poisson.pmf(0, rate),
        "prob_geq_5_in_unit": 1 - stats.poisson.cdf(4, rate),
        "rate_ci_lower": rate - 1.96 * np.sqrt(rate / observation_period),
        "rate_ci_upper": rate + 1.96 * np.sqrt(rate / observation_period),
    }
```

**Use when**: Customer arrivals, server requests, accidents, radioactive decay. Key assumption: events are independent and rate is constant. Test with inter-arrival exponentiality.

---

### S64: Random Walk Analysis

**Problem**: Determine if a time series follows a random walk (unpredictable, unit root process).
**T**: O(n) for analysis | **S**: O(n)
**Lib**: `statsmodels.tsa.stattools.adfuller`, custom
**Guarantee**: ADF test has known asymptotic distribution. Variance ratio test detects departures.

```python
import numpy as np
from statsmodels.tsa.stattools import adfuller

def random_walk_analysis(data: np.ndarray) -> dict:
    """Test if series is a random walk and analyze properties."""
    n = len(data)
    # ADF test (null = unit root = random walk)
    adf_stat, adf_p, _, _, _, _ = adfuller(data, autolag="AIC")
    # Variance ratio test (ratio of var(k-diff) to k*var(1-diff) should be ~1)
    diffs = np.diff(data)
    var_1 = np.var(diffs)
    ratios = {}
    for k in [2, 4, 8, 16]:
        if k < n // 2:
            k_diffs = data[k:] - data[:-k]
            var_k = np.var(k_diffs)
            ratios[k] = var_k / (k * var_1) if var_1 > 0 else float("nan")
    return {
        "adf_statistic": adf_stat, "adf_pvalue": adf_p,
        "is_random_walk": adf_p > 0.05,
        "variance_ratios": ratios,
        "drift": np.mean(diffs),
        "volatility": np.std(diffs),
        "total_displacement": data[-1] - data[0],
    }
```

**Use when**: "Is this stock price predictable?" "Is this truly random?" Financial time series, efficient market hypothesis testing. Random walk = no predictable pattern.

---

### S65: Renewal Process Analysis

**Problem**: Analyze a process where events occur and inter-event times are i.i.d. (generalizing Poisson process to non-exponential inter-arrivals).
**T**: O(n log n) for distribution fitting | **S**: O(n)
**Lib**: `scipy.stats` (distribution fitting), custom
**Guarantee**: Asymptotic results from renewal theory. Central limit theorem for renewal counts.

```python
import numpy as np
from scipy import stats

def renewal_analysis(inter_arrival_times: np.ndarray) -> dict:
    """Analyze a renewal process from inter-arrival times."""
    n = len(inter_arrival_times)
    mean_ia = np.mean(inter_arrival_times)
    var_ia = np.var(inter_arrival_times, ddof=1)
    cv = np.sqrt(var_ia) / mean_ia  # coefficient of variation
    # Fit candidate distributions
    fits = {}
    for dist_name in ["expon", "gamma", "weibull_min", "lognorm"]:
        dist = getattr(stats, dist_name)
        params = dist.fit(inter_arrival_times)
        ks_stat, ks_p = stats.kstest(inter_arrival_times, dist_name, args=params)
        fits[dist_name] = {"params": params, "ks_stat": ks_stat, "ks_pvalue": ks_p}
    best_fit = max(fits, key=lambda d: fits[d]["ks_pvalue"])
    return {
        "n_events": n, "mean_inter_arrival": mean_ia,
        "variance": var_ia, "cv": cv,
        "renewal_rate": 1 / mean_ia,
        "is_poisson": abs(cv - 1.0) < 0.1,
        "best_fit_distribution": best_fit,
        "fits": fits,
    }
```

**Use when**: Equipment replacements, maintenance cycles, customer returns. Generalizes Poisson: CV=1 is Poisson, CV<1 is more regular, CV>1 is more bursty.

---

## 10. Survival Analysis (Extended)

### S66: Log-Rank Test

**Problem**: Compare survival curves of two or more groups to test if they are statistically different.
**T**: O(n log n) for sorting events | **S**: O(n)
**Lib**: `lifelines.statistics.logrank_test`, `scipy.stats`
**Guarantee**: Asymptotic chi-squared distribution under null (no difference). Nonparametric.

```python
from lifelines.statistics import logrank_test
import numpy as np

def compare_survival(durations_a: np.ndarray, events_a: np.ndarray,
                     durations_b: np.ndarray, events_b: np.ndarray) -> dict:
    """Log-rank test comparing two survival curves."""
    result = logrank_test(durations_a, durations_b, event_observed_A=events_a,
                          event_observed_B=events_b)
    return {
        "test_statistic": result.test_statistic,
        "p_value": result.p_value,
        "significant": result.p_value < 0.05,
        "median_a": float(np.median(durations_a[events_a == 1])) if events_a.sum() > 0 else None,
        "median_b": float(np.median(durations_b[events_b == 1])) if events_b.sum() > 0 else None,
    }
```

**Use when**: "Do treatment and control groups have different survival?" The survival analog of the t-test. Use Kaplan-Meier (S39) for estimation, log-rank for comparison.

---

### S67: Accelerated Failure Time (AFT) Model

**Problem**: Model survival time as a function of covariates, where covariates accelerate or decelerate failure.
**T**: O(n · p · iterations) for MLE | **S**: O(n · p)
**Lib**: `lifelines.WeibullAFTFitter`, `lifelines.LogNormalAFTFitter`, `lifelines.LogLogisticAFTFitter`
**Guarantee**: MLE estimates with standard errors and confidence intervals.

```python
from lifelines import WeibullAFTFitter, LogNormalAFTFitter
import pandas as pd

def aft_model(df: pd.DataFrame, duration_col: str, event_col: str,
              distribution: str = "weibull") -> dict:
    """Fit an Accelerated Failure Time model."""
    if distribution == "weibull":
        fitter = WeibullAFTFitter()
    else:
        fitter = LogNormalAFTFitter()
    fitter.fit(df, duration_col=duration_col, event_col=event_col)
    return {
        "coefficients": fitter.params_.to_dict(),
        "confidence_intervals": fitter.confidence_intervals_.to_dict(),
        "aic": fitter.AIC_,
        "concordance_index": fitter.concordance_index_,
        "median_survival": fitter.median_survival_time_,
        "summary": fitter.summary.to_dict(),
    }
```

**Use when**: When you want to model HOW MUCH covariates speed up or slow down time to event (vs. Cox PH which models hazard ratios). Coefficients are directly interpretable as acceleration factors.

---

### S68: Competing Risks Analysis

**Problem**: Analyze time-to-event data where multiple distinct event types can occur, and occurrence of one precludes the others.
**T**: O(n log n) for CIF estimation | **S**: O(n)
**Lib**: `lifelines.AalenJohansenFitter`, custom
**Guarantee**: Aalen-Johansen estimator is nonparametric and consistent.

```python
from lifelines import AalenJohansenFitter
import numpy as np
import pandas as pd

def competing_risks(durations: np.ndarray, events: np.ndarray) -> dict:
    """Estimate cumulative incidence functions for competing risks.
    events: 0=censored, 1=event type 1, 2=event type 2, etc."""
    event_types = sorted(set(events) - {0})
    cifs = {}
    for event_type in event_types:
        ajf = AalenJohansenFitter()
        ajf.fit(durations, events, event_of_interest=event_type)
        cifs[f"event_{event_type}"] = {
            "cumulative_incidence": ajf.cumulative_density_.values.flatten().tolist(),
            "timeline": ajf.cumulative_density_.index.tolist(),
        }
    return {
        "event_types": event_types,
        "cumulative_incidence_functions": cifs,
        "n_total": len(durations),
        "n_censored": int((events == 0).sum()),
        "n_per_event": {et: int((events == et).sum()) for et in event_types},
    }
```

**Use when**: Customer churn (voluntary vs. involuntary), cause-specific mortality (cancer vs. heart disease), employment (quit vs. fired vs. retired). Standard Kaplan-Meier overestimates each risk.

---

## 11. Classification

### S69: k-Nearest Neighbors (k-NN)

**Problem**: Classify a sample by majority vote of its k nearest neighbors in feature space.
**T**: O(nd) per query (brute force), O(n log n) with KD-tree | **S**: O(nd) for training data
**Lib**: `sklearn.neighbors.KNeighborsClassifier()`
**Guarantee**: Approx (nonparametric; Bayes-optimal as n→∞, k→∞, k/n→0)

```python
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score

def knn_classify(X_train, y_train, X_test, k: int = 5) -> dict:
    """k-NN classification with standardized features."""
    scaler = StandardScaler()
    X_tr = scaler.fit_transform(X_train)
    X_te = scaler.transform(X_test)
    model = KNeighborsClassifier(n_neighbors=k)
    model.fit(X_tr, y_train)
    cv_scores = cross_val_score(model, X_tr, y_train, cv=5, scoring='accuracy')
    return {
        "predictions": model.predict(X_te).tolist(),
        "probabilities": model.predict_proba(X_te).tolist(),
        "cv_accuracy": float(cv_scores.mean()),
        "cv_std": float(cv_scores.std()),
    }
```

**Use when**: Small-to-medium datasets, no assumptions about decision boundary shape, interpretable neighborhood-based reasoning. Always scale features first. Use odd k to avoid ties in binary classification.

---

### S70: Decision Tree Classifier

**Problem**: Classify samples by learning axis-aligned splits that maximize information gain (or Gini impurity reduction).
**T**: O(n·p·log n) training, O(depth) prediction | **S**: O(nodes)
**Lib**: `sklearn.tree.DecisionTreeClassifier()`
**Guarantee**: Exact fit on training data (can overfit); pruning controls complexity.

```python
from sklearn.tree import DecisionTreeClassifier, export_text

def decision_tree_classify(X_train, y_train, X_test, max_depth: int = 5) -> dict:
    """Decision tree with depth control and feature importance."""
    model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    model.fit(X_train, y_train)
    return {
        "predictions": model.predict(X_test).tolist(),
        "probabilities": model.predict_proba(X_test).tolist(),
        "feature_importances": model.feature_importances_.tolist(),
        "tree_depth": model.get_depth(),
        "n_leaves": model.get_n_leaves(),
        "tree_rules": export_text(model, max_depth=3),
    }
```

**Use when**: Need interpretable rules ("if feature X > threshold, then class A"). Good for feature selection. Limit depth to prevent overfitting. Single trees are unstable — prefer Random Forest for accuracy.

---

### S71: Random Forest Classifier

**Problem**: Ensemble of decision trees trained on bootstrap samples with random feature subsets; classify by majority vote.
**T**: O(n·p·log n · n_trees) training, O(depth · n_trees) prediction | **S**: O(n_trees · nodes)
**Lib**: `sklearn.ensemble.RandomForestClassifier()`
**Guarantee**: Approx (reduced variance vs. single tree; Breiman's OOB error estimate is nearly unbiased)

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

def random_forest_classify(X_train, y_train, X_test, n_trees: int = 100) -> dict:
    """Random forest with OOB score and feature importance."""
    model = RandomForestClassifier(
        n_estimators=n_trees, oob_score=True, random_state=42, n_jobs=-1
    )
    model.fit(X_train, y_train)
    return {
        "predictions": model.predict(X_test).tolist(),
        "probabilities": model.predict_proba(X_test).tolist(),
        "oob_accuracy": float(model.oob_score_),
        "feature_importances": model.feature_importances_.tolist(),
    }
```

**Use when**: Default first-choice classifier. Handles mixed feature types, missing values (with imputation), nonlinear boundaries. OOB score provides free cross-validation estimate. Feature importance for interpretability.

---

### S72: Support Vector Machine (SVM)

**Problem**: Find the maximum-margin hyperplane separating classes; kernel trick for nonlinear boundaries.
**T**: O(n²·p) to O(n³) training (SMO), O(n_sv · p) prediction | **S**: O(n_sv · p)
**Lib**: `sklearn.svm.SVC()`, `sklearn.svm.LinearSVC()`
**Guarantee**: Global optimum of the convex dual problem (for given kernel and C).

```python
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

def svm_classify(X_train, y_train, X_test, kernel: str = "rbf", C: float = 1.0) -> dict:
    """SVM classification with scaling pipeline."""
    pipe = make_pipeline(StandardScaler(), SVC(kernel=kernel, C=C, probability=True, random_state=42))
    pipe.fit(X_train, y_train)
    svc = pipe.named_steps['svc']
    return {
        "predictions": pipe.predict(X_test).tolist(),
        "probabilities": pipe.predict_proba(X_test).tolist(),
        "n_support_vectors": int(sum(svc.n_support_)),
        "support_per_class": svc.n_support_.tolist(),
    }
```

**Use when**: Medium-sized datasets (n < 10K works well), high-dimensional spaces, clear margin of separation. RBF kernel for nonlinear; LinearSVC for large sparse data (text classification). Always scale features.

---

### S73: Naive Bayes Classifier

**Problem**: Apply Bayes' theorem with strong feature independence assumption; compute P(class|features) ∝ P(features|class)·P(class).
**T**: O(n·p) training, O(p·k) prediction (k classes) | **S**: O(p·k)
**Lib**: `sklearn.naive_bayes.GaussianNB()`, `MultinomialNB()`, `BernoulliNB()`
**Guarantee**: Exact posterior under independence assumption (biased but low variance).

```python
from sklearn.naive_bayes import GaussianNB, MultinomialNB

def naive_bayes_classify(X_train, y_train, X_test, variant: str = "gaussian") -> dict:
    """Naive Bayes classification."""
    models = {"gaussian": GaussianNB, "multinomial": MultinomialNB}
    model = models[variant]()
    model.fit(X_train, y_train)
    return {
        "predictions": model.predict(X_test).tolist(),
        "probabilities": model.predict_proba(X_test).tolist(),
        "class_prior": model.class_prior_.tolist(),
    }
```

**Use when**: Text classification (MultinomialNB with TF-IDF), very large datasets, real-time prediction, baseline model. Fast training and prediction. Probabilities are poorly calibrated but ranking is often good.

---

### S74: Gradient Boosting Classifier

**Problem**: Sequentially fit weak learners (trees) to residuals of the ensemble; combine via gradient descent in function space.
**T**: O(n·p·log n · n_rounds) training | **S**: O(n_rounds · nodes)
**Lib**: `sklearn.ensemble.GradientBoostingClassifier()`, `xgboost.XGBClassifier()`, `lightgbm.LGBMClassifier()`
**Guarantee**: Approx (converges to Bayes-optimal as n_rounds→∞ with proper regularization; state-of-the-art on tabular data)

```python
from sklearn.ensemble import GradientBoostingClassifier

def gradient_boosting_classify(X_train, y_train, X_test, n_estimators: int = 200,
                                learning_rate: float = 0.1, max_depth: int = 3) -> dict:
    """Gradient boosting classification."""
    model = GradientBoostingClassifier(
        n_estimators=n_estimators, learning_rate=learning_rate,
        max_depth=max_depth, random_state=42,
    )
    model.fit(X_train, y_train)
    return {
        "predictions": model.predict(X_test).tolist(),
        "probabilities": model.predict_proba(X_test).tolist(),
        "feature_importances": model.feature_importances_.tolist(),
        "train_score": float(model.score(X_train, y_train)),
    }
```

**Use when**: Best accuracy on structured/tabular data. Use XGBoost or LightGBM for large datasets (faster, GPU support). Tune learning_rate, n_estimators, max_depth together. Early stopping prevents overfitting.

---

### S75: Multi-Layer Perceptron (MLP) Classifier

**Problem**: Feedforward neural network with backpropagation; learns nonlinear decision boundaries via hidden layers.
**T**: O(n · Σ(l_i · l_{i+1}) · epochs) | **S**: O(Σ(l_i · l_{i+1}))
**Lib**: `sklearn.neural_network.MLPClassifier()`
**Guarantee**: Approx (universal approximation theorem; local optima possible; sensitive to hyperparameters)

```python
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

def mlp_classify(X_train, y_train, X_test, hidden_layers: tuple = (100, 50)) -> dict:
    """MLP neural network classification."""
    pipe = make_pipeline(
        StandardScaler(),
        MLPClassifier(hidden_layer_sizes=hidden_layers, max_iter=500,
                      early_stopping=True, random_state=42),
    )
    pipe.fit(X_train, y_train)
    mlp = pipe.named_steps['mlpclassifier']
    return {
        "predictions": pipe.predict(X_test).tolist(),
        "probabilities": pipe.predict_proba(X_test).tolist(),
        "n_iterations": mlp.n_iter_,
        "loss": float(mlp.loss_),
        "n_layers": mlp.n_layers_,
    }
```

**Use when**: Complex nonlinear patterns, sufficient data (n > 1K), can tolerate less interpretability. Always scale features. Use early_stopping to prevent overfitting. For serious deep learning, use PyTorch/TensorFlow instead.

---

## 12. ML Regression

### S76: Decision Tree / Random Forest Regressor

**Problem**: Predict continuous values using tree-based models; ensemble of trees (Random Forest) reduces variance.
**T**: O(n·p·log n · n_trees) training | **S**: O(n_trees · nodes)
**Lib**: `sklearn.tree.DecisionTreeRegressor()`, `sklearn.ensemble.RandomForestRegressor()`
**Guarantee**: Approx (consistent estimator; OOB error is nearly unbiased for RF)

```python
from sklearn.ensemble import RandomForestRegressor

def rf_regress(X_train, y_train, X_test, n_trees: int = 100) -> dict:
    """Random forest regression with OOB score."""
    model = RandomForestRegressor(
        n_estimators=n_trees, oob_score=True, random_state=42, n_jobs=-1
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    return {
        "predictions": preds.tolist(),
        "oob_r2": float(model.oob_score_),
        "feature_importances": model.feature_importances_.tolist(),
    }
```

**Use when**: Nonlinear regression, mixed feature types, robustness to outliers. Default choice for tabular regression when interpretability of individual coefficients is not required.

---

### S77: Gradient Boosting Regressor

**Problem**: Sequential tree ensemble for regression; minimizes squared error (or other loss) via gradient descent in function space.
**T**: O(n·p·log n · n_rounds) | **S**: O(n_rounds · nodes)
**Lib**: `sklearn.ensemble.GradientBoostingRegressor()`, `xgboost.XGBRegressor()`
**Guarantee**: Approx (state-of-the-art on tabular regression tasks)

```python
from sklearn.ensemble import GradientBoostingRegressor

def gb_regress(X_train, y_train, X_test, n_estimators: int = 200,
               learning_rate: float = 0.1) -> dict:
    """Gradient boosting regression."""
    model = GradientBoostingRegressor(
        n_estimators=n_estimators, learning_rate=learning_rate,
        max_depth=3, random_state=42,
    )
    model.fit(X_train, y_train)
    return {
        "predictions": model.predict(X_test).tolist(),
        "feature_importances": model.feature_importances_.tolist(),
        "train_r2": float(model.score(X_train, y_train)),
    }
```

**Use when**: Best predictive accuracy for tabular regression. Use XGBoost/LightGBM for speed. Tune via early stopping on validation set.

---

## 13. Clustering

### S78: K-Means Clustering

**Problem**: Partition n observations into k clusters minimizing within-cluster sum of squares (inertia).
**T**: O(n·k·p·iterations) | **S**: O(n·p + k·p)
**Lib**: `sklearn.cluster.KMeans()`
**Guarantee**: Converges to local optimum; k-means++ initialization gives O(log k)-competitive solution in expectation.

```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

def kmeans_cluster(X, k: int = 3) -> dict:
    """K-Means clustering with silhouette evaluation."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    model = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels = model.fit_predict(X_scaled)
    sil = silhouette_score(X_scaled, labels) if k > 1 else 0.0
    return {
        "labels": labels.tolist(),
        "centroids": scaler.inverse_transform(model.cluster_centers_).tolist(),
        "inertia": float(model.inertia_),
        "silhouette_score": float(sil),
        "n_iterations": model.n_iter_,
    }
```

**Use when**: Default first-choice for clustering. Requires specifying k (use elbow plot or silhouette analysis). Assumes spherical clusters of similar size. Always scale features.

---

### S79: DBSCAN (Density-Based Spatial Clustering)

**Problem**: Group points in high-density regions; mark low-density points as noise. No need to specify k.
**T**: O(n log n) with spatial index, O(n²) worst case | **S**: O(n)
**Lib**: `sklearn.cluster.DBSCAN()`
**Guarantee**: Deterministic (for given eps and min_samples); identifies clusters of arbitrary shape.

```python
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

def dbscan_cluster(X, eps: float = 0.5, min_samples: int = 5) -> dict:
    """DBSCAN density-based clustering."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    model = DBSCAN(eps=eps, min_samples=min_samples)
    labels = model.fit_predict(X_scaled)
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = int((labels == -1).sum())
    return {
        "labels": labels.tolist(),
        "n_clusters": n_clusters,
        "n_noise": n_noise,
        "core_sample_indices": model.core_sample_indices_.tolist(),
    }
```

**Use when**: Unknown number of clusters, clusters of arbitrary shape, data with noise/outliers. Sensitive to eps — use k-distance plot to choose. Struggles with varying-density clusters.

---

### S80: Agglomerative (Hierarchical) Clustering

**Problem**: Bottom-up merging of clusters based on linkage criterion; produces dendrogram.
**T**: O(n³) naive, O(n² log n) with efficient linkage | **S**: O(n²) for distance matrix
**Lib**: `sklearn.cluster.AgglomerativeClustering()`, `scipy.cluster.hierarchy`
**Guarantee**: Deterministic; single-linkage produces MST of distance graph.

```python
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage

def hierarchical_cluster(X, n_clusters: int = 3, linkage_type: str = "ward") -> dict:
    """Agglomerative hierarchical clustering."""
    model = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage_type)
    labels = model.fit_predict(X)
    Z = linkage(X, method=linkage_type)
    return {
        "labels": labels.tolist(),
        "n_clusters": n_clusters,
        "linkage_matrix": Z.tolist(),
        "n_leaves": int(model.n_leaves_),
    }
```

**Use when**: Want dendrogram visualization of cluster hierarchy, don't know k in advance (cut dendrogram at desired level), small-to-medium data (n < 10K due to O(n²) memory). Ward linkage for compact spherical clusters.

---

### S81: Gaussian Mixture Model (GMM)

**Problem**: Fit k Gaussian components via EM algorithm; soft cluster assignment (probabilistic membership).
**T**: O(n·k·p²·iterations) | **S**: O(k·p²)
**Lib**: `sklearn.mixture.GaussianMixture()`
**Guarantee**: Converges to local optimum of log-likelihood; BIC/AIC for model selection.

```python
from sklearn.mixture import GaussianMixture
import numpy as np

def gmm_cluster(X, n_components: int = 3) -> dict:
    """Gaussian mixture model with BIC model selection."""
    # Try different k values for BIC comparison
    bics = {}
    for k in range(2, min(n_components + 3, len(X))):
        gmm = GaussianMixture(n_components=k, random_state=42)
        gmm.fit(X)
        bics[k] = gmm.bic(X)
    best_k = min(bics, key=bics.get)
    model = GaussianMixture(n_components=best_k, random_state=42)
    model.fit(X)
    return {
        "labels": model.predict(X).tolist(),
        "probabilities": model.predict_proba(X).tolist(),
        "means": model.means_.tolist(),
        "bic": float(model.bic(X)),
        "aic": float(model.aic(X)),
        "best_k": best_k,
        "bic_by_k": {str(k): float(v) for k, v in bics.items()},
    }
```

**Use when**: Clusters are elliptical with different shapes/orientations, want soft assignments (probability of belonging to each cluster), automatic k selection via BIC. Generalizes K-Means (K-Means = GMM with spherical, equal-variance components).

---

### S82: Spectral Clustering

**Problem**: Use eigenvalues of the graph Laplacian of the similarity matrix to reduce dimensionality, then cluster in spectral space.
**T**: O(n³) for eigendecomposition, O(n²) for affinity matrix | **S**: O(n²)
**Lib**: `sklearn.cluster.SpectralClustering()`
**Guarantee**: Relaxation of the normalized graph cut problem; near-optimal under planted partition models.

```python
from sklearn.cluster import SpectralClustering

def spectral_cluster(X, n_clusters: int = 3) -> dict:
    """Spectral clustering for non-convex cluster shapes."""
    model = SpectralClustering(
        n_clusters=n_clusters, affinity='rbf', random_state=42, n_jobs=-1
    )
    labels = model.fit_predict(X)
    return {
        "labels": labels.tolist(),
        "n_clusters": n_clusters,
        "affinity_matrix_shape": list(model.affinity_matrix_.shape),
    }
```

**Use when**: Clusters are non-convex (e.g., concentric rings, spirals), graph-structured data. Limited to medium datasets (n < 10K) due to O(n²) affinity matrix. Use 'nearest_neighbors' affinity for larger data.

---

## 14. Dimensionality Reduction

### S83: Principal Component Analysis (PCA)

**Problem**: Find orthogonal directions of maximum variance; project data onto top-k principal components.
**T**: O(min(n·p², p³)) | **S**: O(p²) for covariance matrix
**Lib**: `sklearn.decomposition.PCA()`
**Guarantee**: Exact (optimal rank-k approximation in Frobenius norm, Eckart-Young theorem).

```python
from sklearn.decomposition import PCA
import numpy as np

def pca_reduce(X, n_components: int = 2) -> dict:
    """PCA with explained variance analysis."""
    pca = PCA(n_components=n_components)
    X_reduced = pca.fit_transform(X)
    return {
        "X_reduced": X_reduced.tolist(),
        "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
        "cumulative_variance": np.cumsum(pca.explained_variance_ratio_).tolist(),
        "components": pca.components_.tolist(),
        "singular_values": pca.singular_values_.tolist(),
        "n_components_for_95pct": int(np.searchsorted(
            np.cumsum(PCA().fit(X).explained_variance_ratio_), 0.95) + 1),
    }
```

**Use when**: Feature reduction before modeling, visualization (project to 2D/3D), multicollinearity removal, noise filtering. Choose n_components to explain ≥ 90% variance (scree plot). Linear method — for nonlinear structure use t-SNE or UMAP.

---

### S84: t-SNE (t-distributed Stochastic Neighbor Embedding)

**Problem**: Nonlinear dimensionality reduction preserving local neighborhood structure; map high-D to 2D/3D for visualization.
**T**: O(n² log n) with Barnes-Hut approximation | **S**: O(n²) exact, O(n) Barnes-Hut
**Lib**: `sklearn.manifold.TSNE()`
**Guarantee**: Approx (stochastic; preserves local structure, distorts global distances; non-convex optimization)

```python
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

def tsne_embed(X, perplexity: float = 30.0, n_components: int = 2) -> dict:
    """t-SNE embedding for visualization."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    model = TSNE(n_components=n_components, perplexity=perplexity, random_state=42)
    X_embedded = model.fit_transform(X_scaled)
    return {
        "X_embedded": X_embedded.tolist(),
        "kl_divergence": float(model.kl_divergence_),
        "n_iterations": model.n_iter_,
    }
```

**Use when**: Visualization of clusters in high-dimensional data (e.g., image embeddings, gene expression). Do NOT interpret distances between distant clusters. Perplexity ≈ 5-50; try multiple values. Not suitable for new-point projection (use UMAP instead).

---

### S85: UMAP (Uniform Manifold Approximation and Projection)

**Problem**: Nonlinear dimensionality reduction preserving both local and global structure; faster than t-SNE with support for transform on new data.
**T**: O(n^1.14) empirical | **S**: O(n·k) for neighbor graph
**Lib**: `umap.UMAP()`
**Guarantee**: Approx (based on Riemannian geometry and fuzzy simplicial sets; preserves topological structure)

```python
import umap

def umap_embed(X, n_neighbors: int = 15, min_dist: float = 0.1, n_components: int = 2) -> dict:
    """UMAP embedding with transform support."""
    reducer = umap.UMAP(
        n_neighbors=n_neighbors, min_dist=min_dist,
        n_components=n_components, random_state=42,
    )
    X_embedded = reducer.fit_transform(X)
    return {
        "X_embedded": X_embedded.tolist(),
        "n_neighbors": n_neighbors,
        "min_dist": min_dist,
    }
```

**Use when**: Preferred over t-SNE for larger datasets (faster), when you need to project new points (`.transform()`), or want to preserve more global structure. Use n_neighbors=15 (local), 50+ (global). Install: `pip install umap-learn`.

---

### S86: Factor Analysis

**Problem**: Model observed variables as linear combinations of latent factors plus noise; identify underlying constructs.
**T**: O(p³ · iterations) | **S**: O(p²)
**Lib**: `sklearn.decomposition.FactorAnalysis()`
**Guarantee**: MLE under the factor model; rotation (varimax) aids interpretability.

```python
from sklearn.decomposition import FactorAnalysis
import numpy as np

def factor_analysis(X, n_factors: int = 3) -> dict:
    """Factor analysis with loadings matrix."""
    fa = FactorAnalysis(n_components=n_factors, random_state=42)
    X_scores = fa.fit_transform(X)
    loadings = fa.components_.T  # (features x factors)
    return {
        "scores": X_scores.tolist(),
        "loadings": loadings.tolist(),
        "noise_variance": fa.noise_variance_.tolist(),
        "log_likelihood": float(fa.score(X)),
    }
```

**Use when**: Survey/questionnaire data (identify latent constructs), psychology (personality factors), finance (factor models). Unlike PCA, assumes a generative model with noise. Use varimax rotation for interpretable loadings.

---

## 15. Model Selection & Feature Engineering

### S87: Feature Selection (Filter, Wrapper, Embedded)

**Problem**: Select the most informative features to improve model performance and interpretability.
**T**: Filter O(n·p), Wrapper O(2^p worst case), Embedded O(model fitting) | **S**: O(p)
**Lib**: `sklearn.feature_selection` (SelectKBest, RFE, SelectFromModel)
**Guarantee**: Filter methods are optimal for their criterion; wrapper/embedded depend on base model.

```python
from sklearn.feature_selection import SelectKBest, mutual_info_classif, RFE
from sklearn.ensemble import RandomForestClassifier

def select_features(X, y, method: str = "mutual_info", k: int = 10) -> dict:
    """Feature selection using filter or wrapper methods."""
    if method == "mutual_info":
        selector = SelectKBest(mutual_info_classif, k=k)
        X_selected = selector.fit_transform(X, y)
        scores = selector.scores_
        mask = selector.get_support()
    elif method == "rfe":
        estimator = RandomForestClassifier(n_estimators=50, random_state=42)
        rfe = RFE(estimator, n_features_to_select=k)
        X_selected = rfe.fit_transform(X, y)
        scores = rfe.ranking_
        mask = rfe.support_
    return {
        "selected_features": mask.tolist(),
        "scores": scores.tolist(),
        "n_selected": int(mask.sum()),
    }
```

**Use when**: Too many features (p > 50), remove noise features, improve training speed, prevent overfitting. Use mutual info for general-purpose, chi-squared for categorical targets, RFE for model-based selection, Lasso (S27) for embedded selection.

---

### S88: Hyperparameter Tuning (Grid / Random / Bayesian)

**Problem**: Find optimal hyperparameters by searching over a parameter space with cross-validated performance.
**T**: O(|grid| · k_folds · model_fit) for grid; O(n_iter · k · fit) for random | **S**: O(|grid| · k)
**Lib**: `sklearn.model_selection.GridSearchCV()`, `RandomizedSearchCV()`, `optuna`
**Guarantee**: Grid search is exhaustive (for given grid); random search finds near-optimal with high probability.

```python
from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from scipy.stats import randint, uniform

def tune_hyperparameters(X, y, n_iter: int = 50) -> dict:
    """Randomized hyperparameter search for Random Forest."""
    param_dist = {
        "n_estimators": randint(50, 300),
        "max_depth": randint(3, 20),
        "min_samples_split": randint(2, 20),
        "min_samples_leaf": randint(1, 10),
        "max_features": uniform(0.1, 0.9),
    }
    search = RandomizedSearchCV(
        RandomForestClassifier(random_state=42),
        param_dist, n_iter=n_iter, cv=5, scoring='accuracy',
        random_state=42, n_jobs=-1,
    )
    search.fit(X, y)
    return {
        "best_params": search.best_params_,
        "best_score": float(search.best_score_),
        "cv_results": {
            "mean_test_score": search.cv_results_['mean_test_score'].tolist(),
            "std_test_score": search.cv_results_['std_test_score'].tolist(),
        },
    }
```

**Use when**: After selecting a model, before final evaluation. Random search is more efficient than grid search for > 3 hyperparameters. Use Optuna/Bayesian optimization for expensive models. Always use cross-validation, never tune on test set.

---

### S89: Model Comparison & Selection

**Problem**: Compare multiple models using cross-validated metrics and statistical tests; select the best model.
**T**: O(n_models · k_folds · model_fit) | **S**: O(n_models · k)
**Lib**: `sklearn.model_selection.cross_validate()`, `scipy.stats.friedmanchisquare()`
**Guarantee**: Cross-validation provides nearly unbiased estimate of generalization error.

```python
from sklearn.model_selection import cross_validate
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
import numpy as np

def compare_models(X, y) -> dict:
    """Compare multiple classifiers via cross-validation."""
    models = {
        "LogisticRegression": LogisticRegression(max_iter=500, random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
        "GradientBoosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
        "SVM": SVC(probability=True, random_state=42),
    }
    results = {}
    for name, model in models.items():
        cv = cross_validate(model, X, y, cv=5,
                           scoring=['accuracy', 'f1_weighted', 'roc_auc_ovr_weighted'],
                           return_train_score=True, n_jobs=-1)
        results[name] = {
            "test_accuracy": float(np.mean(cv['test_accuracy'])),
            "test_f1": float(np.mean(cv['test_f1_weighted'])),
            "test_roc_auc": float(np.mean(cv['test_roc_auc_ovr_weighted'])),
            "train_accuracy": float(np.mean(cv['train_accuracy'])),
            "fit_time": float(np.mean(cv['fit_time'])),
        }
    best = max(results, key=lambda m: results[m]['test_accuracy'])
    return {"model_results": results, "best_model": best}
```

**Use when**: Always compare at least 2-3 models before selecting. Use the same CV splits (same random_state). Report mean ± std. If models are close, prefer simpler (Occam's razor). Use paired t-test or Wilcoxon on fold scores to check if difference is significant.

---

### S90: Pipeline Construction & Preprocessing

**Problem**: Chain preprocessing steps (scaling, encoding, imputation) with model fitting into a reproducible pipeline.
**T**: Sum of individual step complexities | **S**: Sum of individual step storage
**Lib**: `sklearn.pipeline.Pipeline()`, `sklearn.compose.ColumnTransformer()`
**Guarantee**: Prevents data leakage (preprocessing fitted only on training data within each CV fold).

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier

def build_pipeline(numeric_features: list, categorical_features: list) -> Pipeline:
    """Build preprocessing + model pipeline."""
    numeric_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
    ])
    categorical_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(handle_unknown='ignore')),
    ])
    preprocessor = ColumnTransformer([
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features),
    ])
    return Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42)),
    ])
```

**Use when**: Always use pipelines in production ML. Prevents data leakage in cross-validation. Enables easy model serialization (pickle the whole pipeline). Use ColumnTransformer for mixed feature types.

---

## 16. Monte Carlo Methods

### S91: Monte Carlo Integration

**Problem**: Estimate integrals or expected values by random sampling: E[f(X)] ≈ (1/N)Σf(xᵢ).
**T**: O(N·f_eval) | **S**: O(N) for samples
**Lib**: `numpy.random`, `scipy.stats`
**Guarantee**: Converges at O(1/√N) regardless of dimension (curse of dimensionality avoided).

```python
import numpy as np

def monte_carlo_integrate(f, bounds: list[tuple], n_samples: int = 100000, seed: int = 42) -> dict:
    """Monte Carlo integration over hyperrectangle."""
    rng = np.random.default_rng(seed)
    dim = len(bounds)
    volume = np.prod([b[1] - b[0] for b in bounds])
    samples = np.column_stack([rng.uniform(lo, hi, n_samples) for lo, hi in bounds])
    values = np.array([f(x) for x in samples])
    estimate = volume * np.mean(values)
    std_err = volume * np.std(values) / np.sqrt(n_samples)
    return {"estimate": float(estimate), "std_error": float(std_err),
            "n_samples": n_samples, "ci_95": [float(estimate - 1.96*std_err), float(estimate + 1.96*std_err)]}
```

**Use when**: High-dimensional integrals (d > 3), irregular domains, expected value computations. Standard error decreases as 1/√N regardless of dimensionality.

---

### S92: Monte Carlo Risk Simulation

**Problem**: Estimate distribution of outcomes (profit, loss, NPV) by simulating many scenarios with random inputs.
**T**: O(N·model_eval) | **S**: O(N·outputs)
**Lib**: `numpy.random`, `scipy.stats`
**Guarantee**: Approx (convergence at 1/√N). Percentiles converge slower than means.

```python
import numpy as np
from scipy import stats

def risk_simulation(model_func, param_distributions: dict, n_simulations: int = 10000, seed: int = 42) -> dict:
    """Monte Carlo risk simulation with correlated inputs."""
    rng = np.random.default_rng(seed)
    results = []
    for _ in range(n_simulations):
        params = {name: dist.rvs(random_state=rng) for name, dist in param_distributions.items()}
        results.append(model_func(**params))
    results = np.array(results)
    return {
        "mean": float(np.mean(results)), "std": float(np.std(results)),
        "percentiles": {str(p): float(np.percentile(results, p)) for p in [5, 25, 50, 75, 95]},
        "prob_negative": float(np.mean(results < 0)),
        "var_95": float(np.percentile(results, 5)),  # Value at Risk
        "cvar_95": float(np.mean(results[results <= np.percentile(results, 5)])),
    }
```

**Use when**: Project risk analysis, financial modeling, "what-if" scenarios, insurance pricing, portfolio risk (VaR/CVaR). Always report confidence intervals and tail risk.

---

### S93: Importance Sampling

**Problem**: Reduce variance of Monte Carlo estimates by sampling from a proposal distribution that emphasizes important regions.
**T**: O(N·f_eval) | **S**: O(N)
**Lib**: `numpy.random`, `scipy.stats`
**Guarantee**: Unbiased if proposal has support everywhere target does. Variance reduction depends on proposal quality.

```python
import numpy as np
from scipy import stats

def importance_sampling(f, target_dist, proposal_dist, n_samples: int = 100000, seed: int = 42) -> dict:
    """Importance sampling: E_target[f(X)] using samples from proposal."""
    rng = np.random.default_rng(seed)
    samples = proposal_dist.rvs(n_samples, random_state=rng)
    weights = target_dist.pdf(samples) / proposal_dist.pdf(samples)
    weighted_values = f(samples) * weights
    estimate = float(np.mean(weighted_values))
    ess = float(np.sum(weights)**2 / np.sum(weights**2))  # effective sample size
    return {"estimate": estimate, "effective_sample_size": ess,
            "std_error": float(np.std(weighted_values) / np.sqrt(n_samples))}
```

**Use when**: Estimating rare event probabilities (P < 0.01), tail risk, where standard MC is inefficient. Choose proposal to concentrate samples where f(x)·p(x) is large.

---

### S94: Variance Reduction Techniques

**Problem**: Improve MC efficiency using antithetic variates, control variates, or stratified sampling.
**T**: O(N·f_eval) same as basic MC | **S**: O(N)
**Lib**: `numpy.random`
**Guarantee**: Provably reduces variance (antithetic: up to 2x; control variate: depends on correlation).

```python
import numpy as np

def antithetic_mc(f, n_samples: int = 50000, seed: int = 42) -> dict:
    """Antithetic variates: use pairs (U, 1-U) to reduce variance."""
    rng = np.random.default_rng(seed)
    u = rng.uniform(0, 1, n_samples)
    y1 = np.array([f(ui) for ui in u])
    y2 = np.array([f(1 - ui) for ui in u])
    estimate = float(np.mean((y1 + y2) / 2))
    std_err = float(np.std((y1 + y2) / 2) / np.sqrt(n_samples))
    return {"estimate": estimate, "std_error": std_err,
            "variance_reduction": float(np.var(y1) / np.var((y1 + y2) / 2))}
```

**Use when**: Need more precision from same number of samples. Antithetic for monotone functions. Control variate when a correlated analytical quantity is available.

---

### S95: Scenario Generation (Correlated Random Variables)

**Problem**: Generate random scenarios with specified marginal distributions and correlation structure (Copula/Cholesky).
**T**: O(N·d²) for Cholesky, O(N·d) for sampling | **S**: O(N·d)
**Lib**: `numpy.random`, `scipy.stats`, `scipy.linalg.cholesky`
**Guarantee**: Exact correlation for normal marginals; approximate for non-normal (via Gaussian copula).

```python
import numpy as np
from scipy.stats import norm
from scipy.linalg import cholesky

def generate_correlated_scenarios(means, stds, correlation_matrix, n_scenarios: int = 10000, seed: int = 42) -> dict:
    """Generate correlated scenarios via Cholesky decomposition."""
    rng = np.random.default_rng(seed)
    d = len(means)
    L = cholesky(correlation_matrix, lower=True)
    Z = rng.standard_normal((n_scenarios, d))
    correlated = Z @ L.T
    scenarios = correlated * np.array(stds) + np.array(means)
    return {
        "scenarios": scenarios.tolist(),
        "realized_means": scenarios.mean(axis=0).tolist(),
        "realized_corr": np.corrcoef(scenarios.T).tolist(),
    }
```

**Use when**: Financial portfolio simulation (correlated asset returns), supply chain (correlated demands), multi-factor risk models. Use Gaussian copula for non-normal marginals.

---

## 17. Queuing Theory

### S96: M/M/1 Queue

**Problem**: Single-server queue with Poisson arrivals (rate λ) and exponential service (rate μ). Compute steady-state metrics.
**T**: O(1) closed-form | **S**: O(1)
**Lib**: Custom (closed-form formulas)
**Guarantee**: Exact (steady-state, requires ρ = λ/μ < 1 for stability).

```python
def mm1_queue(arrival_rate: float, service_rate: float) -> dict:
    """M/M/1 queue: Poisson arrivals, exponential service, 1 server."""
    rho = arrival_rate / service_rate
    if rho >= 1:
        return {"error": "Unstable: arrival rate >= service rate", "utilization": rho}
    L = rho / (1 - rho)           # avg number in system
    Lq = rho**2 / (1 - rho)      # avg number in queue
    W = 1 / (service_rate - arrival_rate)  # avg time in system
    Wq = rho / (service_rate - arrival_rate)  # avg wait time
    return {
        "utilization": rho, "avg_in_system": L, "avg_in_queue": Lq,
        "avg_time_in_system": W, "avg_wait_time": Wq,
        "prob_idle": 1 - rho, "prob_n_or_more": lambda n: rho**n,
    }
```

**Use when**: Single checkout lane, single help desk agent, single machine processing jobs. Simplest queue model; use for quick estimates.

---

### S97: M/M/c Queue (Multi-Server)

**Problem**: c identical servers, Poisson arrivals, exponential service. Compute metrics including Erlang C formula.
**T**: O(c) for Erlang C computation | **S**: O(1)
**Lib**: Custom (Erlang C formula)
**Guarantee**: Exact (steady-state, requires ρ = λ/(cμ) < 1).

```python
import math

def mmc_queue(arrival_rate: float, service_rate: float, c: int) -> dict:
    """M/M/c queue with Erlang C formula."""
    rho = arrival_rate / (c * service_rate)
    if rho >= 1:
        return {"error": "Unstable", "utilization": rho}
    a = arrival_rate / service_rate  # offered load
    # Erlang C: P(wait) = probability of queueing
    sum_terms = sum(a**k / math.factorial(k) for k in range(c))
    last_term = (a**c / math.factorial(c)) * (1 / (1 - rho))
    erlang_c = last_term / (sum_terms + last_term)
    Wq = erlang_c / (c * service_rate - arrival_rate)
    W = Wq + 1 / service_rate
    Lq = arrival_rate * Wq
    L = arrival_rate * W
    return {
        "servers": c, "utilization": rho, "erlang_c": erlang_c,
        "avg_wait_time": Wq, "avg_time_in_system": W,
        "avg_in_queue": Lq, "avg_in_system": L,
        "prob_waiting": erlang_c,
    }
```

**Use when**: Call center staffing, hospital ER, bank tellers, multi-lane toll booth. "How many servers do I need to keep wait time under X?"

---

### S98: M/G/1 Queue (General Service)

**Problem**: Single server with general (non-exponential) service time distribution. Uses Pollaczek-Khinchine formula.
**T**: O(1) closed-form | **S**: O(1)
**Lib**: Custom (P-K formula)
**Guarantee**: Exact (steady-state, uses only mean and variance of service time).

```python
def mg1_queue(arrival_rate: float, service_mean: float, service_var: float) -> dict:
    """M/G/1 queue using Pollaczek-Khinchine formula."""
    rho = arrival_rate * service_mean
    if rho >= 1:
        return {"error": "Unstable", "utilization": rho}
    # P-K formula: Lq = (λ²σ² + ρ²) / (2(1 - ρ))
    Lq = (arrival_rate**2 * service_var + rho**2) / (2 * (1 - rho))
    Wq = Lq / arrival_rate
    W = Wq + service_mean
    L = arrival_rate * W
    return {
        "utilization": rho, "avg_in_queue": Lq, "avg_in_system": L,
        "avg_wait_time": Wq, "avg_time_in_system": W,
        "service_cv": (service_var**0.5) / service_mean,
    }
```

**Use when**: Service times are not exponential (e.g., deterministic, uniform, bimodal). The P-K formula only needs mean and variance of service time.

---

### S99: Little's Law

**Problem**: Relate average number in system (L), average arrival rate (λ), and average time in system (W): L = λW.
**T**: O(1) | **S**: O(1)
**Lib**: Custom
**Guarantee**: Exact (holds for any stable queue, regardless of arrival/service distribution).

```python
def littles_law(known: dict) -> dict:
    """Apply Little's Law: L = λW. Provide any two of {L, lambda, W}."""
    L = known.get("L")
    lam = known.get("lambda")
    W = known.get("W")
    if L is not None and lam is not None:
        W = L / lam
    elif L is not None and W is not None:
        lam = L / W
    elif lam is not None and W is not None:
        L = lam * W
    else:
        return {"error": "Provide exactly two of L, lambda, W"}
    return {"L": L, "lambda": lam, "W": W}
```

**Use when**: Quick sanity check on any queuing result. Remarkably general — works for any stable system in steady state. Also applies to inventory (average inventory = demand rate × lead time).

---

### S100: Jackson Network (Network of Queues)

**Problem**: Network of M/M/c queues where output of one feeds into another. Solve for steady-state via traffic equations.
**T**: O(n³) for traffic equations (n = number of nodes) | **S**: O(n²)
**Lib**: `numpy.linalg.solve()`, custom
**Guarantee**: Exact (product-form solution under Jackson's theorem: independent queues in steady state).

```python
import numpy as np

def jackson_network(external_arrivals: list, routing_matrix: list, service_rates: list, servers: list) -> dict:
    """Solve Jackson network for total arrival rates and per-node metrics."""
    n = len(external_arrivals)
    P = np.array(routing_matrix)
    gamma = np.array(external_arrivals, dtype=float)
    # Traffic equations: λ = γ + P^T λ  =>  (I - P^T)λ = γ
    lam = np.linalg.solve(np.eye(n) - P.T, gamma)
    nodes = {}
    for i in range(n):
        rho_i = lam[i] / (servers[i] * service_rates[i])
        nodes[f"node_{i}"] = {
            "total_arrival_rate": float(lam[i]),
            "utilization": float(rho_i),
            "stable": rho_i < 1,
        }
    return {"arrival_rates": lam.tolist(), "nodes": nodes}
```

**Use when**: Manufacturing lines, computer networks, supply chains with multiple stages. Each stage modeled as a queue; outputs route to next stages.

---

## 18. Discrete-Event Simulation

### S101: Event-Driven Simulation Engine

**Problem**: Simulate a system by processing events in time order: arrivals, service completions, failures, etc.
**T**: O(E·log E) for E events (priority queue) | **S**: O(E)
**Lib**: `simpy`
**Guarantee**: Exact (given the model). Results converge as simulation length → ∞.

```python
import simpy
import numpy as np

def simulate_queue(arrival_rate, service_rate, n_servers, sim_time, seed=42):
    """Simulate M/M/c queue with SimPy."""
    rng = np.random.default_rng(seed)
    wait_times = []

    def customer(env, server):
        arrive = env.now
        with server.request() as req:
            yield req
            wait = env.now - arrive
            wait_times.append(wait)
            yield env.timeout(rng.exponential(1/service_rate))

    def arrivals(env, server):
        while True:
            yield env.timeout(rng.exponential(1/arrival_rate))
            env.process(customer(env, server))

    env = simpy.Environment()
    server = simpy.Resource(env, capacity=n_servers)
    env.process(arrivals(env, server))
    env.run(until=sim_time)
    return {
        "n_served": len(wait_times),
        "avg_wait": float(np.mean(wait_times)) if wait_times else 0,
        "max_wait": float(np.max(wait_times)) if wait_times else 0,
        "pct_waited": float(np.mean([w > 0 for w in wait_times])) if wait_times else 0,
    }
```

**Use when**: Complex systems that don't have closed-form solutions: multi-stage manufacturing, hospitals with different patient types, airports, logistics hubs. SimPy handles resource contention, priorities, and preemption.

---

### S102: Resource Allocation Simulation

**Problem**: Simulate resource contention with multiple resource types, priorities, and preemption.
**T**: O(E·log E) | **S**: O(E + R) where R = resource states
**Lib**: `simpy` (Resource, PriorityResource, PreemptiveResource)
**Guarantee**: Exact (given the model). Report utilization, throughput, bottleneck identification.

```python
import simpy
import numpy as np

def simulate_manufacturing(n_machines, n_inspectors, processing_time, inspection_time,
                           arrival_rate, sim_time, seed=42):
    """Simulate manufacturing line with machine + inspector resources."""
    rng = np.random.default_rng(seed)
    throughput_times = []

    def job(env, machines, inspectors):
        arrive = env.now
        with machines.request() as req:
            yield req
            yield env.timeout(rng.exponential(processing_time))
        with inspectors.request() as req:
            yield req
            yield env.timeout(rng.exponential(inspection_time))
        throughput_times.append(env.now - arrive)

    def source(env, machines, inspectors):
        while True:
            yield env.timeout(rng.exponential(1/arrival_rate))
            env.process(job(env, machines, inspectors))

    env = simpy.Environment()
    machines = simpy.Resource(env, capacity=n_machines)
    inspectors = simpy.Resource(env, capacity=n_inspectors)
    env.process(source(env, machines, inspectors))
    env.run(until=sim_time)
    return {
        "n_completed": len(throughput_times),
        "avg_throughput_time": float(np.mean(throughput_times)) if throughput_times else 0,
        "throughput_rate": len(throughput_times) / sim_time,
    }
```

**Use when**: Multi-stage processes, shared resources (machines, staff, rooms), bottleneck identification, capacity planning.

---

### S103: Warm-Up Period Detection

**Problem**: Detect when a simulation reaches steady state; discard transient initial data.
**T**: O(n) for MSER (marginal standard error rule) | **S**: O(n)
**Lib**: Custom (numpy)
**Guarantee**: Heuristic (MSER minimizes MSE of mean estimate; Welch's graphical method for visual check).

```python
import numpy as np

def detect_warmup(data: list, method: str = "mser") -> dict:
    """Detect warm-up period using MSER-5 rule."""
    y = np.array(data)
    n = len(y)
    if method == "mser":
        # MSER-5: batch into groups of 5, find d that minimizes var of truncated mean
        batch_size = 5
        batched = [np.mean(y[i:i+batch_size]) for i in range(0, n - batch_size + 1, batch_size)]
        batched = np.array(batched)
        m = len(batched)
        mser_values = []
        for d in range(m // 2):
            truncated = batched[d:]
            mser_values.append(np.var(truncated) / len(truncated))
        warmup_batches = int(np.argmin(mser_values))
        warmup_obs = warmup_batches * batch_size
    return {
        "warmup_observations": warmup_obs,
        "warmup_fraction": warmup_obs / n,
        "steady_state_mean": float(np.mean(y[warmup_obs:])),
        "steady_state_std": float(np.std(y[warmup_obs:])),
    }
```

**Use when**: Any simulation that starts empty. Discard warm-up period before computing performance statistics. Critical for reliable simulation output analysis.

---

## Algorithm Selection Flowchart

```
Question about data?
├── Describe the data → S1-S5 (Descriptive Statistics)
│
├── Compare groups?
│   ├── 2 groups?
│   │   ├── Paired? → S8 (Paired t) or Wilcoxon signed-rank
│   │   ├── Normal? → S7 (Two-sample t, Welch's)
│   │   └── Non-normal? → S9 (Mann-Whitney U)
│   └── 3+ groups?
│       ├── Normal? → S12 (ANOVA) → post-hoc (Tukey HSD)
│       └── Non-normal? → S13 (Kruskal-Wallis) → post-hoc (Dunn's)
│
├── Test association?
│   ├── Both continuous? → S5 (Correlation)
│   ├── Both categorical? → S10 (Chi-squared) or S11 (Fisher's exact)
│   └── Mixed? → S12 (ANOVA) or S25 (Logistic regression)
│
├── Predict outcome? (statistical inference emphasis)
│   ├── Continuous Y?
│   │   ├── 1 predictor → S23 (Simple regression)
│   │   ├── Many predictors → S24 (Multiple regression)
│   │   ├── Nonlinear? → S26 (Polynomial) or S28 (GLM)
│   │   ├── Regularization needed? → S27 (Ridge/Lasso)
│   │   └── Outliers? → S30 (Robust regression)
│   └── Binary Y? → S25 (Logistic regression)
│
├── Classify / predict class? (ML emphasis)
│   ├── Need interpretable rules? → S70 (Decision Tree)
│   ├── Best accuracy on tabular data? → S74 (Gradient Boosting) or S71 (Random Forest)
│   ├── Small dataset, simple baseline? → S69 (k-NN) or S73 (Naive Bayes)
│   ├── High-dimensional, clear margin? → S72 (SVM)
│   ├── Complex nonlinear patterns? → S75 (MLP Neural Network)
│   └── Compare all? → S89 (Model Comparison)
│
├── Predict continuous value? (ML emphasis)
│   ├── Nonlinear relationships? → S76 (RF Regressor) or S77 (GB Regressor)
│   └── Need feature importances? → S76 (RF) with S87 (Feature Selection)
│
├── Find groups / clusters?
│   ├── Know number of clusters?
│   │   ├── Spherical clusters → S78 (K-Means)
│   │   ├── Elliptical / overlapping → S81 (GMM)
│   │   └── Non-convex shapes → S82 (Spectral Clustering)
│   └── Unknown number?
│       ├── Noise / outliers present → S79 (DBSCAN)
│       └── Want hierarchy / dendrogram → S80 (Agglomerative)
│
├── Reduce dimensions / visualize?
│   ├── Linear reduction → S83 (PCA)
│   ├── 2D visualization (small data) → S84 (t-SNE)
│   ├── 2D visualization (large data) → S85 (UMAP)
│   └── Latent constructs → S86 (Factor Analysis)
│
├── Feature selection / model tuning?
│   ├── Too many features → S87 (Feature Selection)
│   ├── Tune hyperparameters → S88 (Grid/Random/Bayesian Search)
│   ├── Compare models → S89 (Model Comparison)
│   └── Build production pipeline → S90 (Pipeline Construction)
│
├── Forecast over time?
│   ├── Single series?
│   │   ├── Stationary? → S51 (stationarity test) → S46 (ARIMA)
│   │   ├── Seasonal? → S47 (SARIMA) or S48 (Holt-Winters)
│   │   ├── Multiple seasonalities / holidays? → S55 (Prophet)
│   │   └── Simple trend? → S48 (Exponential Smoothing)
│   ├── Multiple related series? → S53 (VAR)
│   ├── Volatility forecasting? → S54 (GARCH)
│   └── Understand components? → S49 (Decomposition) + S50 (ACF/PACF)
│
├── Detect change or anomaly?
│   ├── When did it change? → S56 (Change Point Detection)
│   ├── What's unusual? → S57 (Anomaly Detection)
│   ├── Did intervention help? → S60 (Intervention Analysis)
│   └── Does X predict Y over time? → S52 (Granger Causality)
│
├── Model random events over time?
│   ├── Events at constant rate? → S63 (Poisson Process)
│   ├── System switching states? → S61 (CTMC) or S62 (Birth-Death)
│   ├── Is it a random walk? → S64 (Random Walk Analysis)
│   └── Recurring events (non-exponential)? → S65 (Renewal Process)
│
├── Estimate parameter?
│   ├── Know the distribution? → S36 (MLE) or S37 (Method of moments)
│   ├── Want uncertainty? → S19 (t CI) or S20 (Bootstrap CI)
│   ├── Have prior information? → S31-S35 (Bayesian methods)
│   └── Censored data? → S39 (Kaplan-Meier) or S40 (Cox PH)
│
├── Survival / time-to-event?
│   ├── Estimate survival curve → S39 (Kaplan-Meier)
│   ├── Compare groups → S66 (Log-Rank Test)
│   ├── Effect of covariates (hazard)? → S40 (Cox PH)
│   ├── Effect of covariates (time)? → S67 (AFT Model)
│   └── Multiple event types? → S68 (Competing Risks)
│
├── Check assumptions?
│   ├── Normal? → S15 (Shapiro-Wilk)
│   ├── Distribution fit? → S14 (KS test) or S36 (MLE + GOF)
│   ├── Stationary? → S51 (ADF + KPSS)
│   └── Equal variance? → Levene's test (in S7)
│
├── Simulate / what-if analysis?
│   ├── Estimate integral or probability → S91 (Monte Carlo Integration)
│   ├── Risk / uncertainty propagation → S92 (Monte Carlo Risk Simulation)
│   ├── Rare event estimation → S93 (Importance Sampling)
│   ├── Reduce variance of MC estimate → S94 (Variance Reduction)
│   ├── Generate future scenarios → S95 (Scenario Generation)
│   └── Model process with resources / queues → S101-S103 (Discrete-Event Simulation)
│
├── Analyze queuing / service system?
│   ├── Single server, Poisson arrivals → S96 (M/M/1)
│   ├── Multiple servers → S97 (M/M/c)
│   ├── General service times → S98 (M/G/1)
│   ├── Relate throughput, time, inventory → S99 (Little's Law)
│   └── Network of queues → S100 (Jackson Network)
│
├── Validate model?
│   ├── Prediction accuracy → S43 (Cross-validation)
│   ├── Sample size needed → S44 (Power analysis)
│   ├── Uncertainty of statistic → S41 (Bootstrap) or S42 (Jackknife)
│   └── Smooth noisy data → S58 (Moving Average) + S59 (Spectral Analysis)
│
└── Model dynamics / ODEs? → See algorithms.md §29 (A165-A174)
    ├── Simple initial-value problem → A165 (Euler) or A166 (RK4)
    ├── Stiff system → A167 (BDF/Radau)
    ├── Visualize trajectories → A168 (Phase Portrait)
    ├── Find / classify equilibria → A169 (Equilibrium & Stability)
    ├── Parameter changes behavior → A170 (Bifurcation)
    ├── Fit ODE to data → A171 (Parameter Estimation)
    ├── Epidemic modeling → A173 (SIR/SEIR)
    └── Predator-prey dynamics → A174 (Lotka-Volterra)
```
