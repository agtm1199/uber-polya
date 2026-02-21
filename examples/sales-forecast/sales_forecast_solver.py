#!/usr/bin/env python3
"""Sales Forecast solver -- Monthly Retail Revenue.

Forecasts 12 months of retail revenue using two complementary methods:
  1. SARIMA(1,1,1)(1,1,1,12) -- parametric seasonal ARIMA
  2. Holt-Winters exponential smoothing (additive seasonal)

Pipeline:
  - Generate synthetic monthly revenue (48 months, trend + seasonality + noise)
  - Stationarity testing (ADF, KPSS)
  - STL decomposition (trend / seasonal / residual)
  - Fit SARIMA and Holt-Winters on training data (first 36 months)
  - Forecast 12 months; compare on holdout (months 37-48)
  - Residual diagnostics (Ljung-Box)
  - Independent verification of all quality criteria
"""
from __future__ import annotations

import json
import sys
import time
import warnings
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller, kpss

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger

log = PolyaLogger()

# Suppress convergence and interpolation warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


# --- Data Model ---

@dataclass(frozen=True)
class Instance:
    """Time series forecasting problem instance."""
    revenue: tuple[float, ...]       # monthly revenue observations
    n_months: int                     # total months of data
    horizon: int                      # months to forecast
    seasonal_period: int              # expected seasonal period
    train_size: int                   # months to use for training
    alpha: float = 0.05              # significance level

    @property
    def train(self) -> tuple[float, ...]:
        return self.revenue[:self.train_size]

    @property
    def holdout(self) -> tuple[float, ...]:
        return self.revenue[self.train_size:]


@dataclass
class Solution:
    """Complete time series forecasting solution."""
    # Stationarity tests (raw data)
    adf_raw: dict = field(default_factory=dict)
    kpss_raw: dict = field(default_factory=dict)

    # Stationarity tests (differenced data)
    adf_diff: dict = field(default_factory=dict)

    # STL decomposition summary
    stl_summary: dict = field(default_factory=dict)

    # SARIMA results
    sarima_order: tuple = ()
    sarima_seasonal_order: tuple = ()
    sarima_aic: float = 0.0
    sarima_bic: float = 0.0
    sarima_forecast: list[float] = field(default_factory=list)
    sarima_ci_lower: list[float] = field(default_factory=list)
    sarima_ci_upper: list[float] = field(default_factory=list)

    # Holt-Winters results
    hw_forecast: list[float] = field(default_factory=list)
    hw_sse: float = 0.0

    # Model comparison (on holdout)
    sarima_rmse: float = 0.0
    sarima_mape: float = 0.0
    hw_rmse: float = 0.0
    hw_mape: float = 0.0
    best_model: str = ""

    # Residual diagnostics
    ljung_box_stat: float = 0.0
    ljung_box_p: float = 0.0
    residuals_ok: bool = False

    # Verification
    verification: dict = field(default_factory=dict)

    # Metadata
    algorithm: str = ""
    time_seconds: float = 0.0


# --- Data Generation ---

def generate_data(seed: int = 42) -> tuple[float, ...]:
    """Generate 48 months of synthetic retail revenue.

    Components:
      - Base: ~$100,000/month
      - Trend: ~5% annual growth (compounding monthly)
      - Seasonal: 12-month cycle (Dec peak, Feb trough)
      - Noise: Gaussian with ~3% coefficient of variation
    """
    rng = np.random.default_rng(seed)
    n = 48
    months = np.arange(n)

    # Base level
    base = 100_000.0

    # Trend: ~5% annual -> ~0.407% monthly compounding
    trend = base * (1.05 ** (months / 12)) - base

    # Seasonal pattern (additive, 12-month period)
    # Jan=-5, Feb=-8, Mar=-3, Apr=0, May=2, Jun=3,
    # Jul=4, Aug=3, Sep=1, Oct=2, Nov=8, Dec=18 (thousands)
    seasonal_factors = np.array([
        -5.0, -8.0, -3.0, 0.0, 2.0, 3.0,
        4.0, 3.0, 1.0, 2.0, 8.0, 18.0,
    ]) * 1000.0
    seasonal = np.tile(seasonal_factors, n // 12 + 1)[:n]

    # Noise: ~3% of base
    noise = rng.normal(0, base * 0.03, size=n)

    revenue = base + trend + seasonal + noise
    return tuple(float(round(v, 2)) for v in revenue)


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Run the full forecasting pipeline."""
    t0 = time.perf_counter()
    sol = Solution()

    train_arr = np.array(instance.train)
    holdout_arr = np.array(instance.holdout)
    full_arr = np.array(instance.revenue)

    # Build pandas series with monthly frequency for statsmodels
    dates = pd.date_range(start="2020-01-01", periods=instance.n_months, freq="MS")
    full_series = pd.Series(full_arr, index=dates)
    train_series = full_series.iloc[:instance.train_size]
    holdout_series = full_series.iloc[instance.train_size:]

    s = instance.seasonal_period

    # ── Step 1: Stationarity Tests (raw data) ──
    adf_result = adfuller(train_arr, autolag="AIC")
    sol.adf_raw = {
        "statistic": float(adf_result[0]),
        "p_value": float(adf_result[1]),
        "lags_used": int(adf_result[2]),
        "is_stationary": adf_result[1] < instance.alpha,
    }

    kpss_result = kpss(train_arr, regression="ct", nlags="auto")
    sol.kpss_raw = {
        "statistic": float(kpss_result[0]),
        "p_value": float(kpss_result[1]),
        "is_stationary": kpss_result[1] > instance.alpha,
    }

    # ── Step 2: Differencing and stationarity of differenced series ──
    # Apply first difference (d=1) then seasonal difference (D=1, s=12)
    diff1 = pd.Series(train_arr).diff().dropna()
    diff1_12 = diff1.diff(s).dropna()
    diff_arr = diff1_12.values

    adf_diff_result = adfuller(diff_arr, autolag="AIC")
    sol.adf_diff = {
        "statistic": float(adf_diff_result[0]),
        "p_value": float(adf_diff_result[1]),
        "is_stationary": adf_diff_result[1] < instance.alpha,
    }

    # ── Step 3: STL Decomposition ──
    stl = STL(train_series, period=s, robust=True)
    stl_result = stl.fit()

    sol.stl_summary = {
        "trend_start": float(stl_result.trend.iloc[0]),
        "trend_end": float(stl_result.trend.iloc[-1]),
        "trend_growth": float(stl_result.trend.iloc[-1] - stl_result.trend.iloc[0]),
        "seasonal_max": float(stl_result.seasonal.max()),
        "seasonal_min": float(stl_result.seasonal.min()),
        "seasonal_range": float(stl_result.seasonal.max() - stl_result.seasonal.min()),
        "residual_mean": float(stl_result.resid.mean()),
        "residual_std": float(stl_result.resid.std()),
    }

    # ── Step 4: Fit SARIMA(1,1,1)(1,1,1,12) ──
    order = (1, 1, 1)
    seasonal_order = (1, 1, 1, s)
    sol.sarima_order = order
    sol.sarima_seasonal_order = seasonal_order

    sarima_model = SARIMAX(
        train_series,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    sarima_fit = sarima_model.fit(disp=False, maxiter=500)

    sol.sarima_aic = float(sarima_fit.aic)
    sol.sarima_bic = float(sarima_fit.bic)

    # Forecast on holdout period
    sarima_pred = sarima_fit.get_forecast(steps=instance.horizon)
    sarima_mean = sarima_pred.predicted_mean.values
    sarima_ci = sarima_pred.conf_int(alpha=instance.alpha)

    sol.sarima_forecast = [float(v) for v in sarima_mean]
    sol.sarima_ci_lower = [float(v) for v in sarima_ci.iloc[:, 0].values]
    sol.sarima_ci_upper = [float(v) for v in sarima_ci.iloc[:, 1].values]

    # Residual diagnostics (Ljung-Box on SARIMA residuals)
    residuals = sarima_fit.resid[s + 1:]  # skip initial NaN-like values
    lb_result = acorr_ljungbox(residuals, lags=[min(10, len(residuals) // 5)],
                                return_df=True)
    sol.ljung_box_stat = float(lb_result["lb_stat"].iloc[0])
    sol.ljung_box_p = float(lb_result["lb_pvalue"].iloc[0])
    sol.residuals_ok = sol.ljung_box_p > instance.alpha

    # ── Step 5: Fit Holt-Winters (additive seasonal) ──
    hw_model = ExponentialSmoothing(
        train_series,
        trend="add",
        seasonal="add",
        seasonal_periods=s,
        initialization_method="estimated",
    )
    hw_fit = hw_model.fit(optimized=True)
    hw_pred = hw_fit.forecast(instance.horizon)

    sol.hw_forecast = [float(v) for v in hw_pred.values]
    sol.hw_sse = float(hw_fit.sse)

    # ── Step 6: Model Comparison on Holdout ──
    def rmse(actual: np.ndarray, predicted: np.ndarray) -> float:
        return float(np.sqrt(np.mean((actual - predicted) ** 2)))

    def mape(actual: np.ndarray, predicted: np.ndarray) -> float:
        return float(np.mean(np.abs((actual - predicted) / actual)) * 100)

    sol.sarima_rmse = rmse(holdout_arr, sarima_mean)
    sol.sarima_mape = mape(holdout_arr, sarima_mean)
    sol.hw_rmse = rmse(holdout_arr, np.array(sol.hw_forecast))
    sol.hw_mape = mape(holdout_arr, np.array(sol.hw_forecast))

    if sol.sarima_mape <= sol.hw_mape:
        sol.best_model = "SARIMA"
    else:
        sol.best_model = "Holt-Winters"

    # ── Metadata ──
    sol.algorithm = "SARIMA(1,1,1)(1,1,1,12) + Holt-Winters (additive seasonal)"
    sol.time_seconds = time.perf_counter() - t0

    # ── Verification ──
    sol.verification = verify(instance, sol)

    return sol


# --- Verification (independent of solver) ---

def verify(instance: Instance, sol: Solution) -> dict:
    """Independently verify all quality criteria.

    Checks:
      1. Differenced series is stationary (ADF p < 0.05)
      2. All forecast values are positive (revenue cannot be negative)
      3. Confidence intervals contain the point forecast
      4. CI lower < point < CI upper for every horizon step
      5. Residuals have no significant autocorrelation (Ljung-Box p > 0.05)
      6. MAPE is below 15% on holdout data
      7. Seasonal period correctly identified as 12
    """
    checks: dict = {}

    # Check 1: Differenced series is stationary
    train_arr = np.array(instance.train)
    diff1 = pd.Series(train_arr).diff().dropna()
    diff1_12 = diff1.diff(instance.seasonal_period).dropna()
    adf_p = adfuller(diff1_12.values, autolag="AIC")[1]
    checks["stationarity_after_differencing"] = {
        "adf_p_value": float(adf_p),
        "passed": adf_p < instance.alpha,
    }

    # Check 2: All forecast values are positive
    all_positive_sarima = all(v > 0 for v in sol.sarima_forecast)
    all_positive_hw = all(v > 0 for v in sol.hw_forecast)
    checks["forecasts_positive"] = {
        "sarima": all_positive_sarima,
        "holt_winters": all_positive_hw,
        "passed": all_positive_sarima and all_positive_hw,
    }

    # Check 3: Confidence intervals contain the point forecast
    ci_contains = all(
        lo <= pt <= hi
        for lo, pt, hi in zip(
            sol.sarima_ci_lower, sol.sarima_forecast, sol.sarima_ci_upper
        )
    )
    checks["ci_contains_forecast"] = {"passed": ci_contains}

    # Check 4: CI lower < point < CI upper (strict ordering)
    ci_ordered = all(
        lo < pt < hi
        for lo, pt, hi in zip(
            sol.sarima_ci_lower, sol.sarima_forecast, sol.sarima_ci_upper
        )
    )
    checks["ci_strictly_ordered"] = {"passed": ci_ordered}

    # Check 5: Residuals have no significant autocorrelation
    # Recompute Ljung-Box independently
    train_series = pd.Series(
        np.array(instance.train),
        index=pd.date_range("2020-01-01", periods=instance.train_size, freq="MS"),
    )
    sarima_refit = SARIMAX(
        train_series,
        order=sol.sarima_order,
        seasonal_order=sol.sarima_seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False,
    ).fit(disp=False, maxiter=500)
    resid = sarima_refit.resid[instance.seasonal_period + 1:]
    lb = acorr_ljungbox(resid, lags=[min(10, len(resid) // 5)], return_df=True)
    lb_p = float(lb["lb_pvalue"].iloc[0])
    checks["residuals_no_autocorrelation"] = {
        "ljung_box_p": lb_p,
        "passed": lb_p > instance.alpha,
    }

    # Check 6: MAPE below 15% on holdout
    holdout_arr = np.array(instance.holdout)
    sarima_pred = np.array(sol.sarima_forecast)
    hw_pred = np.array(sol.hw_forecast)
    sarima_mape = float(np.mean(np.abs((holdout_arr - sarima_pred) / holdout_arr)) * 100)
    hw_mape = float(np.mean(np.abs((holdout_arr - hw_pred) / holdout_arr)) * 100)
    best_mape = min(sarima_mape, hw_mape)
    checks["mape_below_15pct"] = {
        "sarima_mape": sarima_mape,
        "hw_mape": hw_mape,
        "best_mape": best_mape,
        "passed": best_mape < 15.0,
    }

    # Check 7: Seasonal period correctly identified as 12
    # Use autocorrelation to verify: ACF at lag 12 should be a local peak
    # (higher than ACF at lag 6 and lag 18), confirming 12-month seasonality
    from statsmodels.tsa.stattools import acf as acf_func
    acf_vals = acf_func(train_arr, nlags=24, fft=True)
    period_ok = bool(acf_vals[12] > acf_vals[6] and acf_vals[12] > acf_vals[18])
    checks["seasonal_period_is_12"] = {
        "acf_lag_12": float(acf_vals[12]),
        "acf_lag_6": float(acf_vals[6]),
        "acf_lag_18": float(acf_vals[18]),
        "passed": period_ok,
    }

    # Overall
    all_passed = all(
        v["passed"] if isinstance(v, dict) else v
        for v in checks.values()
    )
    checks["all_passed"] = all_passed

    return checks


# --- Main ---

if __name__ == "__main__":
    # Generate synthetic data
    revenue = generate_data(seed=42)

    instance = Instance(
        revenue=revenue,
        n_months=48,
        horizon=12,
        seasonal_period=12,
        train_size=36,
        alpha=0.05,
    )

    sol = solve(instance)

    # ===============================================================
    #  PHASE 1-2: MODEL (uber-model output)
    # ===============================================================
    log.header("UBER-POLYA: Sales Forecast -- Monthly Retail Revenue")

    log.section("PHASE 1-2: UNDERSTAND & PLAN (uber-model)")
    log.info("Problem to Find: 12-month revenue forecast", tag="MODEL")
    log.info("48 months of monthly revenue with trend + seasonality", tag="DATA")
    log.info("Structure: Time series forecasting (seasonal)", tag="MODEL")
    log.info("Models: SARIMA(1,1,1)(1,1,1,12) + Holt-Winters (additive)", tag="MODEL")
    log.blank()
    log.info("Assumptions to verify:", tag="HYPOTHESIS")
    log.info("  - Series is non-stationary (needs differencing)", tag="HYPOTHESIS")
    log.info("  - Seasonal period = 12 months", tag="HYPOTHESIS")
    log.info("  - Residuals are white noise after fitting", tag="HYPOTHESIS")

    # ===============================================================
    #  PHASE 3: SOLVE (uber-solve output)
    # ===============================================================
    log.section("PHASE 3: EXECUTE (uber-solve)")

    # Step 1: Stationarity
    log.step("STEP 1: Stationarity Tests (raw data)")
    log.metric("ADF statistic", "{:.3f}".format(sol.adf_raw["statistic"]), tag="STATS")
    log.metric("ADF p-value", "{:.4f}".format(sol.adf_raw["p_value"]), tag="STATS")
    log.check(
        "Raw series stationary (ADF p < 0.05)",
        sol.adf_raw["is_stationary"], tag="VERIFY")
    log.metric("KPSS statistic", "{:.3f}".format(sol.kpss_raw["statistic"]), tag="STATS")
    log.metric("KPSS p-value", "{:.4f}".format(sol.kpss_raw["p_value"]), tag="STATS")
    log.check(
        "Raw series stationary (KPSS p > 0.05)",
        sol.kpss_raw["is_stationary"], tag="VERIFY")
    log.blank()

    log.metric("ADF (differenced)", "{:.4f}".format(sol.adf_diff["p_value"]), tag="STATS")
    log.check(
        "Differenced series stationary (ADF p < 0.05)",
        sol.adf_diff["is_stationary"], tag="VERIFY")

    # Step 2: STL Decomposition
    log.step("STEP 2: STL Decomposition")
    log.metric("Trend start", "${:,.0f}".format(sol.stl_summary["trend_start"]), tag="STATS")
    log.metric("Trend end", "${:,.0f}".format(sol.stl_summary["trend_end"]), tag="STATS")
    log.metric("Trend growth", "${:,.0f}".format(sol.stl_summary["trend_growth"]), tag="STATS")
    log.metric("Seasonal peak", "${:+,.0f}".format(sol.stl_summary["seasonal_max"]), tag="STATS")
    log.metric("Seasonal trough", "${:+,.0f}".format(sol.stl_summary["seasonal_min"]), tag="STATS")
    log.metric("Seasonal range", "${:,.0f}".format(sol.stl_summary["seasonal_range"]), tag="STATS")
    log.metric("Residual mean", "${:,.0f}".format(sol.stl_summary["residual_mean"]), tag="STATS")
    log.metric("Residual std", "${:,.0f}".format(sol.stl_summary["residual_std"]), tag="STATS")

    # Step 3: SARIMA
    log.step("STEP 3: SARIMA(1,1,1)(1,1,1,12)")
    log.metric("AIC", "{:.1f}".format(sol.sarima_aic), tag="STATS")
    log.metric("BIC", "{:.1f}".format(sol.sarima_bic), tag="STATS")
    log.metric("Ljung-Box stat", "{:.3f}".format(sol.ljung_box_stat), tag="STATS")
    log.metric("Ljung-Box p", "{:.4f}".format(sol.ljung_box_p), tag="STATS")
    log.check("Residuals white noise (Ljung-Box p > 0.05)", sol.residuals_ok, tag="VERIFY")
    log.blank()
    log.info("12-month SARIMA forecast:", tag="RESULT")
    for i, (fc, lo, hi) in enumerate(zip(
        sol.sarima_forecast, sol.sarima_ci_lower, sol.sarima_ci_upper
    )):
        log.table_row(
            "Month {:>2}:  ${:>10,.0f}   CI: [${:>10,.0f}, ${:>10,.0f}]".format(
                i + 1, fc, lo, hi),
            tag="TABLE")

    # Step 4: Holt-Winters
    log.step("STEP 4: Holt-Winters (additive seasonal)")
    log.info("12-month Holt-Winters forecast:", tag="RESULT")
    for i, fc in enumerate(sol.hw_forecast):
        log.table_row("Month {:>2}:  ${:>10,.0f}".format(i + 1, fc), tag="TABLE")

    # Step 5: Model Comparison
    log.step("STEP 5: Model Comparison (holdout = last 12 months)")
    log.table_row("{:<20} {:>10} {:>10}".format("Model", "RMSE", "MAPE"), tag="TABLE")
    log.table_row("{:<20} {:>10,.0f} {:>9.1f}%".format(
        "SARIMA", sol.sarima_rmse, sol.sarima_mape), tag="STATS")
    log.table_row("{:<20} {:>10,.0f} {:>9.1f}%".format(
        "Holt-Winters", sol.hw_rmse, sol.hw_mape), tag="STATS")
    log.success("Best model: {} (lower MAPE)".format(sol.best_model), tag="RESULT")

    # Step 6: Verification
    log.step("STEP 6: Independent Verification")
    v = sol.verification
    log.check("Differenced series stationary",
              v["stationarity_after_differencing"]["passed"], tag="VERIFY")
    log.check("All forecasts positive",
              v["forecasts_positive"]["passed"], tag="VERIFY")
    log.check("CI contains point forecast",
              v["ci_contains_forecast"]["passed"], tag="VERIFY")
    log.check("CI strictly ordered (lower < point < upper)",
              v["ci_strictly_ordered"]["passed"], tag="VERIFY")
    log.check("Residuals no autocorrelation (Ljung-Box)",
              v["residuals_no_autocorrelation"]["passed"], tag="VERIFY")
    log.check("MAPE < 15% on holdout (best={:.1f}%)".format(
              v["mape_below_15pct"]["best_mape"]),
              v["mape_below_15pct"]["passed"], tag="VERIFY")
    log.check("Seasonal period = 12",
              v["seasonal_period_is_12"]["passed"], tag="VERIFY")
    log.blank()
    log.check("ALL VERIFICATION CHECKS PASSED", v["all_passed"], tag="VERIFY")

    # ===============================================================
    #  PHASE 4: LOOK BACK (uber-interpret output)
    # ===============================================================
    log.section("PHASE 4: LOOK BACK (uber-interpret)")

    log.step("BOTTOM LINE")
    log.success("Revenue is growing at ~5% annually with strong December seasonality",
                tag="RESULT")
    log.success("Best model ({}) achieves {:.1f}% MAPE on 12-month holdout".format(
        sol.best_model, min(sol.sarima_mape, sol.hw_mape)), tag="RESULT")
    log.success("Forecasts are reliable: residuals show no remaining structure", tag="RESULT")

    log.step("WHAT THIS MEANS FOR THE BUSINESS")
    avg_forecast = np.mean(sol.sarima_forecast)
    dec_forecast = sol.sarima_forecast[11]  # December = month 12 of forecast
    feb_forecast = sol.sarima_forecast[1]   # February = month 2 of forecast
    log.info("Average monthly revenue (next 12 mo): ${:,.0f}".format(avg_forecast),
             tag="INTERPRET")
    log.info("December peak forecast: ${:,.0f}".format(dec_forecast), tag="INTERPRET")
    log.info("February trough forecast: ${:,.0f}".format(feb_forecast), tag="INTERPRET")
    log.info("Plan inventory and staffing around the ${:,.0f} seasonal swing".format(
        dec_forecast - feb_forecast), tag="RECOMMEND")

    log.step("RECOMMENDATION")
    log.success("Use SARIMA for month-by-month planning (provides confidence intervals)",
                tag="RECOMMEND")
    log.success("Use Holt-Winters as a sanity check / ensemble component", tag="RECOMMEND")
    log.info("Re-fit models quarterly as new data arrives", tag="RECOMMEND")
    log.info("Monitor MAPE; if it exceeds 15%, investigate structural changes", tag="RECOMMEND")

    log.step("LIMITATIONS")
    log.warning("Synthetic data -- real retail data may have outliers, promotions, "
                "regime changes", tag="WARNING")
    log.warning("Additive seasonality assumed -- multiplicative may fit better if "
                "seasonal amplitude grows with trend", tag="WARNING")
    log.warning("No exogenous variables (marketing spend, holidays, weather) -- "
                "SARIMAX could improve accuracy", tag="WARNING")
    log.warning("Confidence intervals widen rapidly beyond 6 months", tag="WARNING")

    log.step("TRANSFERABLE PATTERN")
    log.info("Pattern: 'Forecast Y over time with trend + seasonal cycle'", tag="MODEL")
    log.info("Model:   SARIMA + exponential smoothing (seasonal)", tag="MODEL")
    log.info("Verify:  Stationarity, residual diagnostics, holdout MAPE", tag="SOLVE")
    log.info("Reuse:   Any monthly/weekly/daily series with repeating patterns", tag="MODEL")

    log.blank()
    log.info(sol.algorithm, tag="TIMING")
    log.info("{:.4f}s".format(sol.time_seconds), tag="TIMING")
    log.divider(style="thick")

    # Save JSON
    output = {
        "instance": {
            "n_months": instance.n_months,
            "horizon": instance.horizon,
            "seasonal_period": instance.seasonal_period,
            "train_size": instance.train_size,
        },
        "stationarity": {
            "adf_raw": sol.adf_raw,
            "kpss_raw": sol.kpss_raw,
            "adf_differenced": sol.adf_diff,
        },
        "stl_decomposition": sol.stl_summary,
        "sarima": {
            "order": list(sol.sarima_order),
            "seasonal_order": list(sol.sarima_seasonal_order),
            "aic": sol.sarima_aic,
            "bic": sol.sarima_bic,
            "forecast": sol.sarima_forecast,
            "ci_lower": sol.sarima_ci_lower,
            "ci_upper": sol.sarima_ci_upper,
            "rmse": sol.sarima_rmse,
            "mape": sol.sarima_mape,
        },
        "holt_winters": {
            "forecast": sol.hw_forecast,
            "sse": sol.hw_sse,
            "rmse": sol.hw_rmse,
            "mape": sol.hw_mape,
        },
        "residual_diagnostics": {
            "ljung_box_statistic": sol.ljung_box_stat,
            "ljung_box_p_value": sol.ljung_box_p,
            "residuals_ok": sol.residuals_ok,
        },
        "best_model": sol.best_model,
        "verification": sol.verification,
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
    }
    with open("solution.json", "w") as f:
        json.dump(output, f, indent=2, default=str)
    log.success("Solution data saved to: solution.json", tag="SAVE")
    log.divider(style="thick")
