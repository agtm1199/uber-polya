# Statistical Solver Ecosystem Reference

Guide to the solver libraries used by uber-solve for statistical inference problems. For each library: what it solves, installation, key APIs, and performance notes.

**Python**: Use your project's Python environment (venv, conda, or system Python 3.10+).
**Install**: `pip install <package>` (or `python3 -m pip install <package>`)

---

## 1. scipy.stats -- Distributions, Tests, and Descriptive Statistics

**Solves**: Hypothesis testing (t-tests, chi-squared, KS, ANOVA), confidence intervals, distribution fitting, descriptive statistics, correlation, probability distributions (100+ continuous and discrete).

**Install**: `pip install scipy` (usually pre-installed with scientific Python stacks)

**When to use**: First choice for all standard hypothesis tests and distribution operations. The statistical equivalent of NetworkX for graph problems -- battle-tested, well-documented, pure Python with C backends.

### Key APIs

```python
from scipy import stats
import numpy as np

# --- Descriptive ---
stats.describe(data)                    # n, mean, var, skewness, kurtosis, min, max
stats.sem(data)                         # standard error of the mean
stats.iqr(data)                         # interquartile range
stats.trim_mean(data, 0.1)             # 10% trimmed mean

# --- Hypothesis Tests ---
stats.ttest_1samp(data, popmean=0)      # one-sample t-test
stats.ttest_ind(a, b)                   # two-sample t-test (Welch's by default)
stats.ttest_rel(before, after)          # paired t-test
stats.mannwhitneyu(a, b)               # Mann-Whitney U (nonparametric)
stats.wilcoxon(d)                       # Wilcoxon signed-rank (paired nonparametric)
stats.f_oneway(g1, g2, g3)             # one-way ANOVA
stats.kruskal(g1, g2, g3)              # Kruskal-Wallis (nonparametric ANOVA)
stats.chi2_contingency(table)           # chi-squared test of independence
stats.fisher_exact(table_2x2)          # Fisher's exact test
stats.kstest(data, 'norm')             # Kolmogorov-Smirnov goodness-of-fit
stats.shapiro(data)                     # Shapiro-Wilk normality test
stats.levene(a, b)                      # Levene's test for equal variances
stats.pearsonr(x, y)                    # Pearson correlation + p-value
stats.spearmanr(x, y)                  # Spearman rank correlation
stats.kendalltau(x, y)                 # Kendall's tau

# --- Distributions ---
stats.norm.pdf(x, loc=0, scale=1)      # probability density
stats.norm.cdf(x)                       # cumulative distribution
stats.norm.ppf(q)                       # quantile (inverse CDF)
stats.norm.interval(0.95)              # 95% CI bounds
stats.norm.rvs(size=1000)              # random variates
stats.norm.fit(data)                    # MLE fit

# Available: norm, t, chi2, f, beta, gamma, expon, poisson, binom, uniform, lognorm, weibull_min, ...

# --- Confidence Intervals ---
stats.t.interval(0.95, df=n-1, loc=mean, scale=se)   # t-interval for mean
stats.norm.interval(0.95, loc=mean, scale=se)         # z-interval (large n)

# --- Resampling (scipy >= 1.7) ---
stats.bootstrap((data,), np.mean, confidence_level=0.95)   # bootstrap CI
stats.permutation_test((a, b), statistic)                   # permutation test

# --- Regression ---
stats.linregress(x, y)                 # simple linear regression
```

**Performance note**: Handles millions of observations for most tests. Distribution fitting is fast (MLE via analytical formulas where possible). Bootstrap/permutation tests scale linearly with n_resamples.

---

## 2. statsmodels -- Regression, GLM, ANOVA, and Detailed Statistical Summaries

**Solves**: Linear regression (OLS, WLS, GLS), generalized linear models (Poisson, logistic, Gamma), ANOVA, time series (ARIMA, VAR), nonparametric methods, survival analysis basics, multiple testing correction.

**Install**: `pip install statsmodels`

**When to use**: When you need **detailed statistical summaries** with p-values, confidence intervals, R², AIC/BIC, and diagnostic tests. Use statsmodels (not sklearn) for inference; use sklearn for prediction.

### Key APIs

```python
import statsmodels.api as sm
from statsmodels.formula.api import ols, logit, glm
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint, proportions_ztest
import numpy as np

# --- OLS Regression ---
X = sm.add_constant(X_data)            # ALWAYS add intercept
model = sm.OLS(y, X).fit()
print(model.summary())                 # full summary with coefficients, p-values, R², F-test
model.params                            # coefficient estimates
model.pvalues                           # p-values
model.conf_int()                        # confidence intervals for coefficients
model.rsquared                          # R²
model.rsquared_adj                      # adjusted R²
model.aic, model.bic                    # model selection criteria
model.resid                             # residuals

# --- Formula Interface (R-style) ---
model = ols('y ~ x1 + x2 + x1:x2', data=df).fit()  # interactions
model = ols('y ~ C(group)', data=df).fit()           # categorical variables

# --- Logistic Regression ---
model = sm.Logit(y_binary, X).fit(disp=0)
np.exp(model.params)                    # odds ratios
model.pred_table()                      # confusion matrix

# --- GLM ---
model = sm.GLM(y, X, family=sm.families.Poisson()).fit()
model = sm.GLM(y, X, family=sm.families.Gamma()).fit()
model = sm.GLM(y, X, family=sm.families.NegativeBinomial()).fit()

# --- ANOVA ---
from statsmodels.stats.anova import anova_lm
model = ols('score ~ C(group)', data=df).fit()
anova_table = anova_lm(model, typ=2)

# --- Quantile Regression ---
model = sm.QuantReg(y, X).fit(q=0.5)   # median regression

# --- Robust Regression ---
model = sm.RLM(y, X, M=sm.robust.norms.HuberT()).fit()

# --- Multiple Testing ---
reject, pvals_corrected, _, _ = multipletests(p_values, method='fdr_bh')

# --- Proportion Tests ---
z_stat, p_value = proportions_ztest([conv_a, conv_b], [n_a, n_b])
ci = proportion_confint(successes, trials, method='wilson')

# --- Power Analysis ---
from statsmodels.stats.power import TTestIndPower
analysis = TTestIndPower()
n = analysis.solve_power(effect_size=0.5, alpha=0.05, power=0.8)
```

**Performance note**: OLS scales to ~100K observations comfortably. GLM is iterative (IRLS), typically converges in 5-20 iterations. For >1M rows, consider sklearn or chunked processing.

---

## 3. scikit-learn -- Machine Learning, Model Selection, Preprocessing

**Solves**: Classification, regression, clustering, dimensionality reduction, feature selection, cross-validation, hyperparameter tuning, preprocessing (scaling, encoding, imputation), pipelines.

**Install**: `pip install scikit-learn`

**When to use**: Default library for all supervised/unsupervised ML on tabular data. When the goal is **prediction** rather than **inference**. Does NOT provide p-values or confidence intervals for coefficients — use statsmodels for those.

### Key APIs

```python
# --- Model Selection & Preprocessing ---
from sklearn.model_selection import (
    cross_val_score, cross_validate, KFold, StratifiedKFold,
    train_test_split, GridSearchCV, RandomizedSearchCV
)
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.compose import ColumnTransformer

# --- Linear Models ---
from sklearn.linear_model import (
    LinearRegression, Ridge, Lasso, ElasticNet,
    LogisticRegression, HuberRegressor, BayesianRidge
)

# --- Classification ---
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier, GradientBoostingClassifier,
    AdaBoostClassifier, BaggingClassifier
)
from sklearn.svm import SVC, LinearSVC
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.neural_network import MLPClassifier

# --- Regression ---
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor

# --- Clustering ---
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering, SpectralClustering
from sklearn.mixture import GaussianMixture

# --- Dimensionality Reduction ---
from sklearn.decomposition import PCA, FactorAnalysis
from sklearn.manifold import TSNE

# --- Feature Selection ---
from sklearn.feature_selection import SelectKBest, mutual_info_classif, RFE, SelectFromModel

# --- Metrics ---
from sklearn.metrics import (
    # Classification
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report, roc_curve,
    # Regression
    r2_score, mean_squared_error, mean_absolute_error,
    # Clustering
    silhouette_score, calinski_harabasz_score, davies_bouldin_score,
)

# --- Train/Test Split ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# --- Cross-Validation ---
scores = cross_val_score(RandomForestClassifier(random_state=42), X, y, cv=5, scoring='accuracy')

# --- Pipeline with Preprocessing ---
pipe = make_pipeline(StandardScaler(), SVC(probability=True, random_state=42))
pipe.fit(X_train, y_train)

# --- Hyperparameter Tuning ---
param_grid = {'n_estimators': [50, 100, 200], 'max_depth': [3, 5, 10]}
grid = GridSearchCV(RandomForestClassifier(random_state=42), param_grid, cv=5, scoring='accuracy')
grid.fit(X_train, y_train)

# --- Clustering with Evaluation ---
kmeans = KMeans(n_clusters=3, n_init=10, random_state=42).fit(X_scaled)
sil = silhouette_score(X_scaled, kmeans.labels_)

# --- Dimensionality Reduction ---
pca = PCA(n_components=2).fit_transform(X_scaled)
```

### Gotchas

- Always scale features for distance-based methods (k-NN, SVM, PCA, k-Means)
- Use `stratify=y` in train_test_split for imbalanced classification
- Use pipelines to prevent data leakage in cross-validation
- `n_jobs=-1` parallelizes across CPU cores (model fitting, CV, grid search)
- For >100K rows: prefer LinearSVC over SVC, use `partial_fit` for incremental learning
- Random forest `oob_score=True` gives free cross-validation estimate

**Performance note**: Linear models handle millions of rows. Tree ensembles (RF, GB) handle 100K+ rows easily. SVM with RBF kernel is O(n²-n³), so keep n < 10K. Use `n_jobs=-1` for parallel CV.

---

## 4. PyMC (v5) -- Bayesian Modeling and MCMC

**Solves**: Bayesian parameter estimation, hierarchical/multilevel models, Bayesian regression, MCMC sampling (NUTS), variational inference (ADVI), posterior predictive checks, model comparison (WAIC, LOO).

**Install**: `pip install pymc`

**When to use**: When you have prior information, need full posterior distributions (not just point estimates), or the model is hierarchical. Slower than frequentist methods but provides richer uncertainty quantification.

### Key APIs

```python
import pymc as pm
import arviz as az
import numpy as np

# --- Basic Model ---
with pm.Model() as model:
    # Priors
    mu = pm.Normal("mu", mu=0, sigma=10)
    sigma = pm.HalfNormal("sigma", sigma=1)
    # Likelihood
    y_obs = pm.Normal("y_obs", mu=mu, sigma=sigma, observed=data)
    # Sample posterior
    trace = pm.sample(2000, random_seed=42, return_inferencedata=True)

# --- Diagnostics ---
az.summary(trace)                       # posterior summary (mean, sd, HDI, r_hat, ess)
az.plot_trace(trace)                    # trace plots (visual convergence check)
az.plot_posterior(trace)                # posterior distributions
az.rhat(trace).max()                    # R-hat convergence diagnostic (want < 1.01)

# --- Bayesian Regression ---
with pm.Model() as reg_model:
    alpha = pm.Normal("alpha", mu=0, sigma=10)
    betas = pm.Normal("betas", mu=0, sigma=10, shape=X.shape[1])
    sigma = pm.HalfNormal("sigma", sigma=1)
    mu = alpha + pm.math.dot(X, betas)
    y_obs = pm.Normal("y_obs", mu=mu, sigma=sigma, observed=y)
    trace = pm.sample(2000, random_seed=42, return_inferencedata=True)

# --- Model Comparison ---
az.compare({"model1": trace1, "model2": trace2}, ic="loo")  # LOO-CV comparison

# --- Posterior Predictive ---
with model:
    pp = pm.sample_posterior_predictive(trace)
az.plot_ppc(pp)                         # posterior predictive check

# --- Variational Inference (faster) ---
with model:
    approx = pm.fit(30000, method="advi")
    trace_vi = approx.sample(2000)
```

**Performance note**: NUTS sampler typically needs 1000-4000 samples per chain. 4 chains is standard. For n > 10K observations, consider variational inference (ADVI) as a faster alternative. GPU acceleration available via JAX backend (`pip install pymc[jax]`).

---

## 5. pingouin -- Clean API for Common Statistical Tests

**Solves**: t-tests, ANOVA (repeated measures, mixed), correlation, chi-squared, effect sizes, pairwise comparisons, normality tests, sphericity tests.

**Install**: `pip install pingouin`

**When to use**: When you want the **cleanest API** for common tests. Returns pandas DataFrames with all relevant statistics (test stat, p-value, effect size, CI, power) in one call. Great for quick analysis and reporting.

### Key APIs

```python
import pingouin as pg
import pandas as pd

# --- t-tests (returns DataFrame with everything) ---
pg.ttest(x, y, paired=False)           # two-sample, returns T, p, CI, d, power, BF10
pg.ttest(x, y, paired=True)            # paired
pg.ttest(x, 0)                          # one-sample

# --- ANOVA ---
pg.anova(dv='score', between='group', data=df)    # one-way
pg.rm_anova(dv='score', within='condition', subject='subject', data=df)  # repeated measures
pg.mixed_anova(dv='score', between='group', within='time', subject='id', data=df)

# --- Post-hoc ---
pg.pairwise_tests(dv='score', between='group', data=df, padjust='bonf')

# --- Correlation ---
pg.corr(x, y, method='pearson')         # Pearson + CI + power
pg.corr(x, y, method='spearman')        # Spearman
pg.partial_corr(data=df, x='x', y='y', covar='z')  # partial correlation

# --- Effect Sizes ---
pg.compute_effsize(x, y, eftype='cohen')    # Cohen's d
pg.compute_effsize(x, y, eftype='hedges')   # Hedges' g

# --- Normality & Assumptions ---
pg.normality(data, dv='score', group='group')    # Shapiro-Wilk per group
pg.homoscedasticity(data, dv='score', group='group')  # Levene's test
pg.sphericity(data, dv='score', within='condition', subject='subject')

# --- Chi-squared ---
expected, observed, stats_result = pg.chi2_independence(data, x='var1', y='var2')

# --- Power ---
pg.power_ttest(d=0.5, n=None, power=0.8, alpha=0.05)  # solve for n
```

**Performance note**: Thin wrapper around scipy and statsmodels. Same performance as underlying libraries. The advantage is the clean DataFrame output with all statistics in one row.

---

## 6. lifelines -- Survival Analysis

**Solves**: Kaplan-Meier estimation, Cox proportional hazards, parametric survival models (Weibull, exponential, log-normal), Nelson-Aalen estimator, log-rank test, time-varying covariates.

**Install**: `pip install lifelines`

**When to use**: Time-to-event data with censoring (customer churn, equipment failure, patient survival, subscription duration). Standard statistics can't handle censored observations -- lifelines can.

### Key APIs

```python
from lifelines import (
    KaplanMeierFitter, CoxPHFitter, WeibullFitter,
    NelsonAalenFitter, ExponentialFitter
)
from lifelines.statistics import logrank_test
import pandas as pd

# --- Kaplan-Meier ---
kmf = KaplanMeierFitter()
kmf.fit(durations, event_observed=events, label="Group A")
kmf.plot_survival_function()            # survival curve
kmf.median_survival_time_              # median survival
kmf.survival_function_at_times([30, 60, 90])  # S(t) at specific times

# --- Compare Groups ---
result = logrank_test(durations_a, durations_b, event_a, event_b)
result.p_value                          # are survival curves different?

# --- Cox Proportional Hazards ---
cph = CoxPHFitter()
cph.fit(df, duration_col='T', event_col='E')
cph.print_summary()                     # coefficients, HR, p-values, CI
cph.hazard_ratios_                     # exp(β) -- multiplicative effect on hazard
cph.plot()                              # forest plot of hazard ratios
cph.check_assumptions(df)              # test proportional hazards assumption

# --- Parametric Models ---
wf = WeibullFitter()
wf.fit(durations, event_observed=events)
wf.print_summary()
wf.median_survival_time_

# --- Prediction ---
cph.predict_survival_function(new_data)     # predicted S(t) for new subjects
cph.predict_median(new_data)                # predicted median survival
cph.concordance_index_                      # predictive accuracy (C-index)
```

**Performance note**: Kaplan-Meier handles millions of observations. Cox PH scales to ~100K observations comfortably. For very large datasets, use `CoxPHFitter(penalizer=0.01)` for regularization.

---

## 7. prophet -- Time Series Forecasting with Decomposable Models

**Solves**: Time series forecasting with trend, multiple seasonalities, holidays, and changepoints. Designed for business forecasting at scale with interpretable components.

**Install**: `pip install prophet`

**When to use**: Business time series with daily/weekly data, holidays, and multiple seasonal patterns. When interpretability matters more than maximum accuracy. Handles missing data and outliers gracefully.

### Key APIs

```python
from prophet import Prophet
import pandas as pd

# --- Basic Forecasting ---
df = pd.DataFrame({"ds": dates, "y": values})  # MUST use 'ds' and 'y' columns
model = Prophet()
model.fit(df)
future = model.make_future_dataframe(periods=30)    # 30 days ahead
forecast = model.predict(future)
forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]  # point forecast + CI

# --- Seasonality Control ---
model = Prophet(
    yearly_seasonality=True,       # annual pattern
    weekly_seasonality=True,       # day-of-week pattern
    daily_seasonality=False,       # sub-daily pattern (for hourly data)
    seasonality_mode="multiplicative",  # vs "additive"
    changepoint_prior_scale=0.05,  # flexibility of trend changes (lower=smoother)
)

# --- Add Custom Seasonality ---
model.add_seasonality(name="monthly", period=30.5, fourier_order=5)

# --- Add Holidays ---
holidays = pd.DataFrame({
    "holiday": ["christmas", "christmas"],
    "ds": pd.to_datetime(["2025-12-25", "2024-12-25"]),
    "lower_window": -1, "upper_window": 1,  # days around holiday
})
model = Prophet(holidays=holidays)

# --- Components ---
model.plot_components(forecast)           # trend, weekly, yearly, holidays
model.plot(forecast)                      # data + forecast + CI

# --- Cross-Validation ---
from prophet.diagnostics import cross_validation, performance_metrics
cv = cross_validation(model, initial="365 days", period="90 days", horizon="30 days")
metrics = performance_metrics(cv)
metrics[["horizon", "mape", "rmse", "mae"]]
```

**Performance note**: Fits in seconds for <100K observations. Scales to millions with `stan_backend="CMDSTANPY"`. Cross-validation is the bottleneck for large datasets.

**Gotchas**:
- Input DataFrame MUST have columns named `ds` (datetime) and `y` (numeric) -- not negotiable
- Returns a DataFrame with many columns; key ones are `yhat`, `yhat_lower`, `yhat_upper`
- `changepoint_prior_scale` is the main tuning knob: lower=smoother, higher=more flexible
- For sub-daily data, set `daily_seasonality=True` and use `freq="H"` in `make_future_dataframe`
- Prophet may install its own C++ backend (cmdstan); installation can be tricky on some systems

---

## 8. arch -- Volatility Modeling (GARCH)

**Solves**: Time-varying volatility modeling, GARCH family models, value-at-risk estimation for financial return series.

**Install**: `pip install arch`

**When to use**: Financial return series with volatility clustering. Risk management, option pricing, VaR estimation.

### Key APIs

```python
from arch import arch_model

# --- GARCH(1,1) ---
model = arch_model(returns, vol="Garch", p=1, q=1, mean="Constant")
result = model.fit(disp="off")
result.summary()                               # coefficients, standard errors
result.conditional_volatility                  # time-varying volatility estimate
result.forecast(horizon=5)                     # 5-step ahead volatility forecast

# --- EGARCH (asymmetric) ---
model = arch_model(returns, vol="EGARCH", p=1, o=1, q=1)

# --- GJR-GARCH (leverage effect) ---
model = arch_model(returns, vol="Garch", p=1, o=1, q=1)
```

**Gotchas**:
- Input should be returns (percentage changes), not prices
- Returns should be multiplied by 100 for numerical stability
- Check persistence (alpha + beta < 1 for stationarity)

---

## 9. ruptures -- Change Point Detection

**Solves**: Detecting abrupt changes in the statistical properties of a time series (mean shifts, variance changes, trend breaks).

**Install**: `pip install ruptures`

**When to use**: "When did the trend change?" Manufacturing quality control, regime detection, A/B test timing validation.

### Key APIs

```python
import ruptures as rpt

# --- PELT (exact, fast for large n) ---
algo = rpt.Pelt(model="rbf", min_size=2).fit(signal)
bkps = algo.predict(pen=10)                   # penalty controls number of changes

# --- Binary Segmentation (faster, approximate) ---
algo = rpt.Binseg(model="l2").fit(signal)
bkps = algo.predict(n_bkps=3)                 # specify number of change points

# --- Bottom-Up (merging approach) ---
algo = rpt.BottomUp(model="l2").fit(signal)
bkps = algo.predict(n_bkps=3)

# --- Visualization ---
rpt.display(signal, bkps)
```

**Gotchas**:
- Penalty (`pen`) or number of breakpoints (`n_bkps`) must be specified -- there's no automatic selection
- Model options: `"l2"` (mean shift), `"l1"` (median shift), `"rbf"` (general), `"linear"` (trend)
- PELT is optimal but only works with penalty, not `n_bkps`

---

## 10. xgboost -- Gradient Boosting (High Performance)

**Solves**: Classification, regression, ranking via gradient-boosted decision trees. State-of-the-art on structured/tabular data.

**Install**: `pip install xgboost`

**When to use**: Best predictive accuracy for tabular data. Faster than sklearn's GradientBoosting (histogram-based, GPU support). Default choice for Kaggle-style ML tasks.

### Key APIs

```python
import xgboost as xgb
from sklearn.model_selection import cross_val_score

# --- Classification ---
model = xgb.XGBClassifier(
    n_estimators=200, max_depth=6, learning_rate=0.1,
    use_label_encoder=False, eval_metric='logloss', random_state=42,
)
model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
preds = model.predict(X_test)
probs = model.predict_proba(X_test)

# --- Regression ---
model = xgb.XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42)
model.fit(X_train, y_train)

# --- Feature Importance ---
importances = model.feature_importances_
xgb.plot_importance(model)

# --- Early Stopping ---
model.fit(X_train, y_train,
          eval_set=[(X_val, y_val)],
          callbacks=[xgb.callback.EarlyStopping(rounds=20)])

# --- Cross-Validation ---
scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
```

**Gotchas**:
- Always use early stopping to prevent overfitting
- Set `use_label_encoder=False` and explicit `eval_metric` to silence warnings
- For imbalanced data: use `scale_pos_weight = n_neg / n_pos`
- LightGBM (`lightgbm`) is a drop-in alternative that's often faster on large datasets

---

## 11. umap-learn -- UMAP Dimensionality Reduction

**Solves**: Nonlinear dimensionality reduction preserving both local and global structure. Faster than t-SNE, supports transform on new data.

**Install**: `pip install umap-learn`

**When to use**: Visualizing high-dimensional data in 2D/3D, preprocessing before clustering, faster alternative to t-SNE that supports new-point projection.

### Key APIs

```python
import umap

# --- Basic 2D embedding ---
reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, n_components=2, random_state=42)
embedding = reducer.fit_transform(X)

# --- Transform new data (unlike t-SNE!) ---
new_embedding = reducer.transform(X_new)

# --- Supervised UMAP (use labels to guide embedding) ---
reducer = umap.UMAP(n_neighbors=15, random_state=42)
embedding = reducer.fit_transform(X, y=labels)

# --- Tuning ---
# n_neighbors: 5-15 (local) to 50-200 (global structure)
# min_dist: 0.0 (tight clusters) to 0.99 (spread out)
# metric: 'euclidean', 'cosine', 'manhattan', 'correlation'
```

**Gotchas**:
- Import as `import umap`, not `import umap_learn`
- Set `random_state` for reproducibility
- Always scale features before UMAP (StandardScaler)
- For very large data (>100K): use `umap.UMAP(low_memory=True)`

---

## 12. simpy -- Discrete-Event Simulation

**Install**: `pip install simpy`
**Import**: `import simpy`

### Key APIs

| Function | Purpose |
|---|---|
| `simpy.Environment()` | Create simulation environment |
| `env.process(generator)` | Register a process (generator function) |
| `env.run(until=T)` | Run simulation until time T |
| `env.timeout(duration)` | Delay a process for a duration |
| `simpy.Resource(env, capacity=c)` | Shared resource with limited capacity |
| `resource.request()` | Request access to a resource (blocks if full) |
| `resource.release(req)` | Release a resource |
| `simpy.Store(env, capacity=c)` | FIFO buffer for passing items between processes |
| `simpy.PriorityResource(env, capacity=c)` | Resource with priority-based queuing |
| `simpy.PreemptiveResource(env, capacity=c)` | Resource that allows preemption |

### Typical Usage

```python
import simpy
import numpy as np

def customer(env, name, server, service_time_fn, wait_times):
    """Customer arrives, waits for server, gets served."""
    arrival = env.now
    with server.request() as req:
        yield req                          # wait for server
        wait = env.now - arrival
        wait_times.append(wait)
        yield env.timeout(service_time_fn())  # service

def source(env, server, arrival_rate, service_rate, wait_times, n_customers):
    """Generate customers at Poisson arrival rate."""
    for i in range(n_customers):
        yield env.timeout(np.random.exponential(1.0 / arrival_rate))
        env.process(customer(env, f"C{i}", server,
                             lambda: np.random.exponential(1.0 / service_rate),
                             wait_times))

# Run
env = simpy.Environment()
server = simpy.Resource(env, capacity=1)
wait_times = []
env.process(source(env, server, arrival_rate=4.0, service_rate=5.0,
                   wait_times=wait_times, n_customers=10000))
env.run()
print(f"Mean wait: {np.mean(wait_times):.3f}")
```

### Gotchas

- Processes are Python generators (`yield` required); forgetting `yield` causes silent errors
- `env.run()` without `until=` runs until no more events (may run forever if source is infinite)
- Resource requests MUST use `with` block or explicit `release()`, otherwise deadlock
- simpy is single-threaded; for parallel replications, use `multiprocessing`
- Random number generation: set `np.random.seed()` for reproducibility per replication
- Warm-up period: discard initial transient observations before collecting steady-state stats

---

## 13. dowhy -- Causal Inference Framework

**Install**: `pip install dowhy econml`
**Import**: `import dowhy`

### Key APIs

| Function | Purpose |
|---|---|
| `dowhy.CausalModel(data, treatment, outcome, graph)` | Define causal model with DAG |
| `model.identify_effect()` | Find identification strategy (backdoor, IV, frontdoor) |
| `model.estimate_effect(method_name=...)` | Estimate causal effect via chosen method |
| `model.refute_estimate(method_name=...)` | Test robustness (placebo, random cause, subset) |
| `econml.dml.DML()` | Double Machine Learning estimator |
| `econml.dr.DRLearner()` | Doubly Robust Learner |
| `econml.metalearners.TLearner()` | T-Learner for heterogeneous effects |

### Typical Usage

```python
import dowhy
import pandas as pd

# Define causal model with DAG
model = dowhy.CausalModel(
    data=df,
    treatment="treatment",
    outcome="outcome",
    graph="digraph { confounder -> treatment; confounder -> outcome; treatment -> outcome; }"
)

# Identify causal effect
identified = model.identify_effect()
print(identified)  # Shows backdoor adjustment set

# Estimate effect
estimate = model.estimate_effect(
    identified,
    method_name="backdoor.propensity_score_matching"
)
print(f"ATE = {estimate.value:.3f}")

# Refute: placebo treatment (should give ~0)
refutation = model.refute_estimate(
    identified, estimate,
    method_name="placebo_treatment_refuter"
)
print(f"Placebo effect = {refutation.new_effect:.3f}")
```

### Gotchas

- Requires specifying the causal DAG as a DOT string; results depend entirely on DAG correctness
- `identify_effect()` may find no valid identification if DAG has no adjustment set
- Refutation tests (placebo, random common cause) are necessary — a "significant" estimate may be spurious
- EconML methods (DML, DRLearner) are better for heterogeneous treatment effects but need larger samples
- propensity score methods need overlap (common support) — check propensity distributions

---

## Library Selection Guide

| Question | First Choice | Alternative |
|---|---|---|
| Run a standard hypothesis test | scipy.stats | pingouin (cleaner API) |
| Get p-values + CI for regression coefficients | statsmodels | pingouin (for simple tests) |
| Cross-validate a prediction model | scikit-learn | -- |
| Regularized regression (Ridge/Lasso) | scikit-learn | statsmodels (for inference) |
| Full Bayesian posterior | PyMC | scipy.stats (conjugate priors only) |
| Quick test with all statistics in one call | pingouin | -- |
| Survival / time-to-event analysis | lifelines | statsmodels (basic) |
| Distribution fitting (MLE) | scipy.stats | statsmodels |
| Bootstrap confidence interval | scipy.stats.bootstrap | custom numpy |
| Multiple testing correction | statsmodels.multipletests | -- |
| Power analysis / sample size | statsmodels.stats.power | pingouin |
| Forecast univariate time series | statsmodels (ARIMA/ETS) | prophet (holidays/multi-seasonal) |
| Business forecast with holidays | prophet | statsmodels (SARIMAX with exog) |
| Multi-series forecasting | statsmodels (VAR) | -- |
| Volatility / risk modeling | arch (GARCH) | -- |
| Change point detection | ruptures | -- |
| Spectral analysis / frequencies | scipy.signal | -- |
| Classification (tabular data) | scikit-learn (RF, SVM) | xgboost (best accuracy) |
| Regression prediction (ML) | scikit-learn (RF, GB) | xgboost |
| Clustering | scikit-learn (KMeans, DBSCAN) | -- |
| Dimensionality reduction (linear) | scikit-learn (PCA) | -- |
| Dimensionality reduction (nonlinear) | umap-learn | scikit-learn (t-SNE) |
| Feature selection | scikit-learn (SelectKBest, RFE) | -- |
| Hyperparameter tuning | scikit-learn (GridSearchCV) | optuna |
| Build ML pipeline | scikit-learn (Pipeline) | -- |
| Monte Carlo simulation | numpy (random sampling) | scipy.stats (distributions) |
| Queuing theory (analytical) | scipy (formulas) | custom |
| Discrete-event simulation | simpy | custom |
| ODE / dynamical system | scipy.integrate.solve_ivp | SymPy (dsolve, symbolic) |
| Epidemic modeling (SIR/SEIR) | scipy.integrate.solve_ivp | custom |
| Causal effect (observational) | dowhy | econml (DML, DRLearner) |
| Propensity score matching | scikit-learn + custom | dowhy |
| Causal DAG / identification | dowhy | networkx |

### Decision Flow

```
Need to test a hypothesis or estimate a parameter?
├── Standard test (t, chi², ANOVA, correlation)?
│   ├── Quick with all stats → pingouin
│   └── More control → scipy.stats
├── Regression with inference (p-values, CI)?
│   └── statsmodels
├── Regression for prediction (cross-validated)?
│   └── scikit-learn
├── Bayesian analysis?
│   ├── Conjugate prior → scipy.stats (manual)
│   └── Complex model → PyMC
├── Survival analysis?
│   └── lifelines
├── Forecast time series?
│   ├── Simple trend/seasonal → statsmodels (ARIMA, ETS)
│   ├── Multiple seasonalities / holidays → prophet
│   ├── Multiple related series → statsmodels (VAR)
│   └── Volatility → arch (GARCH)
├── Detect changes?
│   └── ruptures
├── Classify / predict category?
│   ├── Best accuracy (tabular) → xgboost or scikit-learn (RF, GB)
│   ├── Need interpretability → scikit-learn (Decision Tree, Logistic)
│   └── Text data → scikit-learn (Naive Bayes + TF-IDF)
├── Cluster / segment?
│   └── scikit-learn (KMeans, DBSCAN, GMM)
├── Reduce dimensions / visualize?
│   ├── Linear → scikit-learn (PCA)
│   └── Nonlinear → umap-learn (UMAP) or scikit-learn (t-SNE)
├── Build ML pipeline?
│   └── scikit-learn (Pipeline + ColumnTransformer)
├── Simulate / Monte Carlo?
│   ├── Random sampling / risk → numpy + scipy.stats
│   └── Process with queues / resources → simpy
├── Queuing analysis (analytical)?
│   └── scipy (closed-form M/M/1, M/M/c, M/G/1)
├── Solve ODE / model dynamics?
│   ├── Symbolic / exact solution → SymPy (dsolve)
│   └── Numerical / complex system → scipy.integrate.solve_ivp
└── Estimate causal effect?
    ├── Specify DAG + identify strategy → dowhy
    ├── Propensity score matching → scikit-learn + custom
    ├── Heterogeneous treatment effects → econml (DML, DRLearner)
    └── Simple DiD / IV / RDD → statsmodels
```
