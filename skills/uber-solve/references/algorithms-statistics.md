# Statistical Inference Algorithm Catalog

Comprehensive catalog of 45+ algorithms for statistical inference. Organized by problem type, each entry includes complexity, solver library, correctness guarantee, and implementation guidance.

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
├── Predict outcome?
│   ├── Continuous Y?
│   │   ├── 1 predictor → S23 (Simple regression)
│   │   ├── Many predictors → S24 (Multiple regression)
│   │   ├── Nonlinear? → S26 (Polynomial) or S28 (GLM)
│   │   ├── Regularization needed? → S27 (Ridge/Lasso)
│   │   └── Outliers? → S30 (Robust regression)
│   └── Binary Y? → S25 (Logistic regression)
│
├── Estimate parameter?
│   ├── Know the distribution? → S36 (MLE) or S37 (Method of moments)
│   ├── Want uncertainty? → S19 (t CI) or S20 (Bootstrap CI)
│   ├── Have prior information? → S31-S35 (Bayesian methods)
│   └── Censored data? → S39 (Kaplan-Meier) or S40 (Cox PH)
│
├── Check assumptions?
│   ├── Normal? → S15 (Shapiro-Wilk)
│   ├── Distribution fit? → S14 (KS test) or S36 (MLE + GOF)
│   └── Equal variance? → Levene's test (in S7)
│
└── Validate model?
    ├── Prediction accuracy → S43 (Cross-validation)
    ├── Sample size needed → S44 (Power analysis)
    └── Uncertainty of statistic → S41 (Bootstrap) or S42 (Jackknife)
```
