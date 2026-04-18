# Time Series Forecasting — ARIMA, GARCH & Bootstrap

**Objective:** Build and validate a production-grade time series forecasting pipeline for U.S. CPI and S&P 500 volatility, emphasizing rigorous model diagnostics, reusable evaluation tooling, and distribution-free uncertainty quantification.

## Methodology

- **Pipeline diagnosis & repair:** Identified and corrected three compounding errors in a broken ARIMA specification — unit root ignored (`d=0` on non-stationary CPI), monthly seasonality omitted entirely, and residual diagnostics skipped before forecasting
- **SARIMA specification:** Iteratively arrived at `SARIMA(2,1,1)(1,0,1,12)` via ADF stationarity testing, ACF/PACF inspection, and Ljung-Box validation; confirmed white-noise residuals at lags 12 and 24 (p ≈ 1.0)
- **Volatility modeling:** Fit `GARCH(1,1)` to S&P 500 daily returns using the `arch` library, with variance stationarity verified via the `alpha + beta < 1` condition
- **Forecast evaluation module:** Authored `forecast_evaluation.py` with two production-ready functions — `compute_mase()` for scale-independent accuracy benchmarking and `backtest_expanding_window()` for walk-forward out-of-sample validation
- **Bootstrap uncertainty quantification:** Implemented moving block bootstrap (block size = 6) to generate distribution-free 95% forecast intervals, preserving residual autocorrelation structure without parametric assumptions

## Key Findings

- SARIMA achieved a mean MASE of **0.449** across 16 expanding-window origins (2010–2025), beating the seasonal naive benchmark by ~55% during stable inflation regimes
- Model performance degraded sharply during the COVID inflation shock: MASE reached **1.94** at the 2021-12 origin, confirming that no parametric model reliably handles structural breaks of that magnitude
- Forecast error grows monotonically with horizon — from **0.53 CPI points** at step 1 to **3.20 points** at step 12 — consistent with uncertainty propagation expected from an integrated process
- S&P 500 conditional volatility exhibits high persistence: `alpha + beta ≈ 0.9826`, implying a half-life of **39.5 days** for volatility shocks to decay to baseline