# Sales Forecast -- Monthly Retail Revenue

**Domain**: Time Series Analysis
**Algorithm**: SARIMA(1,1,1)(1,1,1,12) + Holt-Winters Exponential Smoothing (additive)
**Key Concepts**: ARIMA, SARIMA, exponential smoothing, stationarity, AIC/BIC, forecast confidence intervals, STL decomposition, residual diagnostics

## Problem

A retail store has 4 years (48 months) of monthly revenue data with a clear upward trend and strong seasonal pattern (peak in December, trough in February). The owner needs to forecast revenue for the next 12 months to plan inventory, staffing, and cash flow.

The data exhibits three classic time series components:
- **Trend**: ~5% annual revenue growth driven by expanding customer base
- **Seasonality**: 12-month cycle with holiday spike (Dec) and post-holiday dip (Jan-Feb)
- **Noise**: Random month-to-month variation from weather, promotions, local events

Two complementary forecasting methods are applied:
1. **SARIMA(1,1,1)(1,1,1,12)** -- a parametric model capturing autoregressive and moving-average structure in both the non-seasonal and seasonal components
2. **Holt-Winters (additive seasonal)** -- an exponential smoothing method that decomposes the series into level, trend, and seasonal components with exponentially decaying weights

## Files

| File | Description |
|------|-------------|
| `sales_forecast_solver.py` | Full solver: data generation, stationarity tests, STL decomposition, SARIMA fit, Holt-Winters fit, model comparison, residual diagnostics, verification |

## Requirements

```bash
pip install statsmodels numpy scipy pandas
```

## Quick Run

```bash
python3 sales_forecast_solver.py
```

## Expected Output

**Stationarity Tests (raw data)**:
- ADF test: p > 0.05 (non-stationary, as expected with trend + seasonality)
- KPSS test: p < 0.05 (confirms non-stationarity)

**After differencing (d=1, D=1, s=12)**:
- ADF test: p < 0.05 (stationary)

**STL Decomposition**:
- Trend: steadily increasing from ~$100K to ~$115K over 48 months
- Seasonal: December peak ~+$15-20K, February trough ~-$8-10K
- Residual: mean near zero, no obvious pattern

**SARIMA(1,1,1)(1,1,1,12)**:
- AIC and BIC reported for model selection
- 12-month forecast with 95% confidence intervals
- Residuals pass Ljung-Box test (no significant autocorrelation)

**Holt-Winters (additive)**:
- 12-month forecast with comparable accuracy
- Generally smoother forecast profile

**Model Comparison**:
- RMSE and MAPE on holdout (last 12 months)
- Both models achieve MAPE < 15%
- AIC/BIC favor SARIMA for this data

**Verification**: All 7 checks pass (stationarity, positive forecasts, CI containment, residual diagnostics, MAPE threshold, seasonal period).

## Algorithm

1. **Generate** synthetic monthly revenue data with trend, seasonality, and noise (48 months)
2. **Test stationarity** using Augmented Dickey-Fuller (ADF) and KPSS tests on the raw series
3. **Decompose** the series via STL (Seasonal-Trend decomposition using LOESS) to isolate trend, seasonal, and residual components
4. **Difference** the series (first difference + seasonal difference) to achieve stationarity
5. **Fit SARIMA(1,1,1)(1,1,1,12)** via maximum likelihood estimation and extract AIC/BIC
6. **Fit Holt-Winters** exponential smoothing with additive seasonal component
7. **Forecast** 12 months ahead with both models; compute 95% confidence intervals for SARIMA
8. **Compare** models on holdout data using RMSE and MAPE
9. **Diagnose** residuals via Ljung-Box test for remaining autocorrelation
10. **Verify** independently that all quality criteria are met

## Key Concepts

- **ARIMA(p,d,q)** -- AutoRegressive Integrated Moving Average; combines autoregression (p lags), differencing (d times), and moving average (q lags) for non-seasonal time series modeling
- **SARIMA(p,d,q)(P,D,Q,s)** -- Seasonal ARIMA; extends ARIMA with seasonal autoregressive (P), differencing (D), and moving average (Q) terms at seasonal period s
- **Exponential smoothing** -- a family of forecasting methods that assign exponentially decreasing weights to older observations; Holt-Winters adds trend and seasonal components
- **Stationarity** -- a time series property where statistical properties (mean, variance, autocorrelation) do not change over time; required by ARIMA-family models
- **ADF test** -- Augmented Dickey-Fuller test; null hypothesis is that the series has a unit root (non-stationary); reject at p < 0.05 to confirm stationarity
- **KPSS test** -- Kwiatkowski-Phillips-Schmidt-Shin test; null hypothesis is that the series is stationary; reject at p < 0.05 to confirm non-stationarity (complementary to ADF)
- **STL decomposition** -- Seasonal-Trend decomposition using LOESS; a robust method to separate trend, seasonal, and residual components
- **AIC/BIC** -- Akaike/Bayesian Information Criterion; model selection metrics that balance goodness-of-fit against model complexity; lower is better
- **RMSE** -- Root Mean Squared Error; measures average forecast deviation in the same units as the data
- **MAPE** -- Mean Absolute Percentage Error; scale-free accuracy metric; MAPE < 10% is excellent, < 20% is good for retail forecasting
- **Ljung-Box test** -- tests whether residual autocorrelations are jointly zero; p > 0.05 means no significant remaining structure
- **Confidence interval** -- a range around the point forecast that contains the true value with a specified probability (e.g., 95%); widens as the forecast horizon increases
