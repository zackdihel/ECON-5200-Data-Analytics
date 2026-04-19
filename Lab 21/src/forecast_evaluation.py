# %%writefile forecast_evaluation.py
"""
forecast_evaluation.py — Forecast Evaluation & Backtesting Module

Reusable functions for computing MASE and running expanding-window
backtests on time series forecasting models.

Author: Zachary Dihel
Course: ECON 5200, Lab 21
"""

import numpy as np
import pandas as pd
from typing import Callable


def compute_mase(
    actual: np.ndarray,
    forecast: np.ndarray,
    insample: np.ndarray,
    m: int = 1
) -> float:
    """Compute Mean Absolute Scaled Error.
    
    MASE < 1: model beats naive seasonal benchmark.
    MASE > 1: naive benchmark is better.
    
    Args:
        actual: True out-of-sample values
        forecast: Model predictions (same length as actual)
        insample: In-sample (training) data for naive baseline
        m: Seasonal period (1=random walk, 12=monthly seasonal)
    
    Returns:
        MASE score (float)
    """
    # YOUR IMPLEMENTATION HERE
    # Hint:
    mae_forecast = np.mean(np.abs(actual - forecast))
    naive_errors = insample[m:] - insample[:-m]
    mae_naive = np.mean(np.abs(naive_errors))
    return mae_forecast / mae_naive


def backtest_expanding_window(
    series: pd.Series,
    model_fn: Callable,
    min_train: int = 120,
    horizon: int = 12,
    step: int = 12
) -> pd.DataFrame:
    """Expanding-window time series backtest.
    
    Args:
        series: Full series with DatetimeIndex
        model_fn: Callable(train) -> np.ndarray of length horizon
        min_train: Minimum training observations
        horizon: Forecast horizon per iteration
        step: Observations added per iteration
    
    Returns:
        DataFrame with backtest results
    """
    # YOUR IMPLEMENTATION HERE
    # Hint: loop from min_train to len(series)-horizon, stepping by step
    # For each origin:
    #   train = series[:origin]
    #   actual = series[origin:origin+horizon].values
    #   forecast = model_fn(train)
    #   compute errors and MASE
    records = []
    for origin in range(min_train, len(series) - horizon+1, step):
        train = series[:origin]
        actual = series[origin:origin+horizon].values

        forecast = model_fn(train)

        errors = np.array(forecast)-actual
        mase_val = compute_mase(actual, forecast, train.values, m=12)

        for h in range(horizon):
            records.append({
                'origin'   : series.index[origin - 1],  # last training date
                'horizon'  : h + 1,
                'actual'   : actual[h],
                'forecast' : forecast[h],
                'error'    : errors[h],
                'abs_error': abs(errors[h]),
                'mase'     : mase_val
            })
    return pd.DataFrame(records, columns=[
        'origin', 'horizon', 'actual', 'forecast', 'error', 'abs_error', 'mase'
    ])


# --- Quick self-test ---
if __name__ == '__main__':
    print('forecast_evaluation.py loaded successfully.')
    # Add your own test calls here
    # ================================================================
# TEST CALLS: compute_mase and backtest_expanding_window
# Using real CPI data from this session
# ================================================================

print("=" * 60)
print("TEST 1: compute_mase — SARIMA vs naive seasonal")
print("=" * 60)

# Split CPI into insample / holdout
insample = cpi.iloc[:-12].values
holdout  = cpi.iloc[-12:].values

# SARIMA forecast over holdout
sarima_test = SARIMAX(cpi.iloc[:-12], order=(2,1,1),
                      seasonal_order=(1,0,1,12)).fit(disp=False)
sarima_fc = sarima_test.forecast(steps=12).values

mase_sarima = compute_mase(holdout, sarima_fc, insample, m=12)
mase_naive  = compute_mase(holdout, insample[-12:], insample, m=12)

print(f"  SARIMA MASE : {mase_sarima:.4f}  (< 1 = beats naive)")
print(f"  Naive  MASE : {mase_naive:.4f}   (should be ≈ 1.0)")
assert mase_naive < 1.5,  "naive MASE sanity check failed"
assert mase_sarima >= 0,  "MASE must be non-negative"
print("  PASSED\n")

# ----------------------------------------------------------------
print("=" * 60)
print("TEST 2: compute_mase — perfect forecast → MASE = 0")
print("=" * 60)

mase_perfect = compute_mase(holdout, holdout, insample, m=12)
print(f"  Perfect forecast MASE: {mase_perfect:.4f}  (expect 0.0)")
assert mase_perfect == 0.0, f"Expected 0.0, got {mase_perfect}"
print("  PASSED\n")

# ----------------------------------------------------------------
print("=" * 60)
print("TEST 3: compute_mase — flat insample → returns nan")
print("=" * 60)

mase_flat = compute_mase(holdout, sarima_fc, np.ones(len(insample)), m=12)
print(f"  Flat insample MASE: {mase_flat}  (expect nan)")
assert np.isnan(mase_flat) or np.isinf(mase_flat), f"Expected nan, got {mase_flat}"
print("  PASSED\n")

# ----------------------------------------------------------------
print("=" * 60)
print("TEST 4: backtest_expanding_window — SARIMA on CPI")
print("=" * 60)

def sarima_fn(train: pd.Series) -> np.ndarray:
    m = SARIMAX(train, order=(2,1,1),
                seasonal_order=(1,0,1,12)).fit(disp=False)
    return m.forecast(steps=12).values

results = backtest_expanding_window(
    series    = cpi,
    model_fn  = sarima_fn,
    min_train = 120,
    horizon   = 12,
    step      = 12
)

print(f"  Rows returned : {len(results)}")
print(f"  Origins       : {results['origin'].nunique()}")
print(f"  Columns       : {results.columns.tolist()}")
print(f"\n  MASE by origin:")
print(results.groupby('origin')['mase'].first().round(4).to_string())
print(f"\n  MAE by horizon step:")
print(results.groupby('horizon')['abs_error'].mean().round(4).to_string())
print(f"\n  Mean MASE across all origins: {results['mase'].mean():.4f}")

assert set(results.columns) == {'origin','horizon','actual',
                                 'forecast','error','abs_error','mase'}
assert results['horizon'].max() == 12
assert (results['abs_error'] >= 0).all()
print("\n  PASSED")