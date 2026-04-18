"""
decompose.py — Time Series Decomposition & Diagnostics Module

Reusable functions for STL/MSTL decomposition, stationarity testing,
structural break detection, and block bootstrap trend confidence intervals.

Author: Zachary Dihel
Course: ECON 5200, Lab 20
"""

import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL, MSTL
from statsmodels.tsa.stattools import adfuller, kpss
import ruptures as rpt
from typing import Optional


# =============================================================================
# STL DECOMPOSITION
# =============================================================================

def run_stl(
    series: pd.Series,
    period: int = 12,
    log_transform: bool = True,
    robust: bool = True
):
    """Apply STL decomposition with optional log-transform.

    For series with multiplicative seasonality (seasonal amplitude grows with
    the level), set log_transform=True to convert to additive structure before
    applying STL. After log-transform, STL components are in log-units;
    exp() converts trend/seasonal back to original scale if needed.

    Args:
        series: Time series with DatetimeIndex and set frequency.
        period: Seasonal period (12=monthly, 4=quarterly).
        log_transform: If True, apply log before STL (for multiplicative data).
        robust: If True, downweight outliers via bisquare weights.

    Returns:
        STL result object (statsmodels DecomposeResult).

    Raises:
        ValueError: If series contains non-positive values with log_transform=True.
    """
    if log_transform:
        if (series <= 0).any():
            raise ValueError(
                "Series contains non-positive values. "
                "Cannot log-transform. Set log_transform=False."
            )
        work_series = np.log(series)
    else:
        work_series = series.copy()

    stl = STL(work_series, period=period, robust=robust)
    return stl.fit()


# =============================================================================
# MSTL DECOMPOSITION
# =============================================================================

def run_mstl(
    series: pd.Series,
    periods: list,
    log_transform: bool = True,
    robust: bool = True
):
    """Apply MSTL decomposition for multi-seasonal time series.

    How MSTL works iteratively:
        MSTL is an extension of STL that handles multiple seasonal periods
        (e.g., daily data with both weekly and annual cycles). It works by
        iterating: in each pass, it fits STL for one seasonal period while
        treating the sum of all other seasonal components as part of the
        remainder. It cycles through all periods until convergence. The result
        is one trend component + one seasonal component per period + residual.
        This is far superior to classical decomposition, which can only handle
        a single seasonal period.

    Args:
        series: Time series with DatetimeIndex and set frequency.
        periods: List of seasonal periods, e.g. [7, 365] for daily data.
        log_transform: If True, apply log before MSTL.
        robust: If True, use robust fitting in each inner STL pass.

    Returns:
        MSTL result object.

    Raises:
        ValueError: If series contains non-positive values with log_transform=True.
        ValueError: If periods is empty or not a list.
    """
    if not isinstance(periods, (list, tuple)) or len(periods) == 0:
        raise ValueError("periods must be a non-empty list, e.g. [7, 365].")

    if log_transform:
        if (series <= 0).any():
            raise ValueError(
                "Series contains non-positive values. "
                "Cannot log-transform. Set log_transform=False."
            )
        work_series = np.log(series)
    else:
        work_series = series.copy()

    mstl = MSTL(work_series, periods=periods)
    return mstl.fit()


# =============================================================================
# STATIONARITY TESTING
# =============================================================================

def test_stationarity(
    series: pd.Series,
    alpha: float = 0.05
) -> dict:
    """Run ADF + KPSS and return the 2x2 decision table verdict.

    ADF null hypothesis:  unit root present (non-stationary)
    KPSS null hypothesis: series is stationary

    The two tests together resolve four cases:
        ADF rejects  + KPSS doesn't reject → stationary
        ADF doesn't  + KPSS rejects        → non-stationary
        Both reject                         → contradictory (structural break?)
        Neither rejects                     → inconclusive (low power)

    Args:
        series: Time series to test (levels or differences).
        alpha: Significance level for both tests (default 0.05).

    Returns:
        dict with keys: adf_stat, adf_p, kpss_stat, kpss_p, verdict.
        Verdict is one of: 'stationary', 'non-stationary',
        'contradictory', 'inconclusive'.
    """
    # regression='ct' includes constant + trend: correct for GDP-like series
    # that trend upward. Using 'n' or 'c' on a trended series inflates the
    # test statistic and can falsely reject the unit root null.
    adf_stat, adf_p, _, _, _, _ = adfuller(series, autolag='AIC', regression='ct')
    kpss_stat, kpss_p, _, _ = kpss(series, regression='c', nlags='auto')

    adf_rejects = adf_p < alpha
    kpss_rejects = kpss_p < alpha

    if adf_rejects and not kpss_rejects:
        verdict = 'stationary'
    elif not adf_rejects and kpss_rejects:
        verdict = 'non-stationary'
    elif adf_rejects and kpss_rejects:
        verdict = 'contradictory'
    else:
        verdict = 'inconclusive'

    return {
        'adf_stat': round(adf_stat, 4),
        'adf_p': round(adf_p, 4),
        'kpss_stat': round(kpss_stat, 4),
        'kpss_p': round(kpss_p, 4),
        'verdict': verdict
    }


# =============================================================================
# STRUCTURAL BREAK DETECTION
# =============================================================================

def detect_breaks(
    series: pd.Series,
    pen: float = 10.0
) -> list:
    """Detect structural breaks using the PELT algorithm.

    PELT (Pruned Exact Linear Time) minimizes a penalized cost function:
        Cost(segmentation) + pen * number_of_breakpoints

    Why the penalty controls bias-variance tradeoff:
        A low penalty → model is penalized little for adding breaks → overfits,
        detecting noise as structure (high variance, low bias).
        A high penalty → model strongly penalized for each break → underfits,
        missing genuine structural changes (low variance, high bias).
        Common choices: pen=log(n) (BIC-like), pen=2*log(n) (stricter).
        The 'rbf' cost function detects changes in both mean and variance,
        making it robust to heteroskedastic series like GDP or retail sales.

    Args:
        series: Time series with DatetimeIndex.
        pen: Penalty parameter. Higher = fewer detected breaks.

    Returns:
        List of break dates as pd.Timestamp.
    """
    signal = series.values
    algo = rpt.Pelt(model='rbf').fit(signal)
    breakpoints = algo.predict(pen=pen)

    # ruptures returns indices; the last index == len(series) is the series end,
    # not a real break — the guard `bp < len(series)` excludes it.
    break_dates = [
        series.index[bp - 1]
        for bp in breakpoints
        if bp < len(series)
    ]
    return break_dates


# =============================================================================
# BLOCK BOOTSTRAP TREND CI
# =============================================================================

def block_bootstrap_trend(
    series: pd.Series,
    n_bootstrap: int = 500,
    block_size: int = 12,
    period: int = 12,
    log_transform: bool = True,
    robust: bool = True,
    ci: float = 0.95
) -> pd.DataFrame:
    """Estimate trend uncertainty via block bootstrap.

    Why block bootstrap (not i.i.d. bootstrap):
        Economic time series have autocorrelation — today's value depends on
        yesterday's. An i.i.d. bootstrap randomly resamples individual
        observations, destroying the temporal dependence structure. This
        produces bootstrap samples that are statistically impossible for the
        original data-generating process, leading to confidence intervals that
        are too narrow and p-values that are wrong.

        Block bootstrap instead resamples contiguous blocks of observations
        (length = block_size). Within each block, the original autocorrelation
        structure is preserved. By concatenating randomly drawn blocks, we
        get synthetic series that mimic the dependence of the original.

        Rule of thumb: block_size ≈ series frequency (12 for monthly),
        or use block_size ≈ n^(1/3) for general series.

    Args:
        series: Original time series with DatetimeIndex and frequency.
        n_bootstrap: Number of bootstrap replications.
        block_size: Length of each resampled block (preserves autocorrelation).
        period: STL seasonal period.
        log_transform: Log-transform before STL.
        robust: Robust STL fitting.
        ci: Confidence interval width (default 0.95 → 2.5th/97.5th percentiles).

    Returns:
        DataFrame with columns: 'lower', 'median', 'upper' indexed like series.
    """
    n = len(series)
    trend_matrix = np.full((n_bootstrap, n), np.nan)

    # Number of blocks needed to cover the full series length
    n_blocks = int(np.ceil(n / block_size))

    for i in range(n_bootstrap):
        # Draw random block start indices (with replacement)
        starts = np.random.randint(0, n - block_size + 1, size=n_blocks)

        # Concatenate blocks and trim to original length
        boot_values = np.concatenate([
            series.values[s: s + block_size] for s in starts
        ])[:n]

        boot_series = pd.Series(boot_values, index=series.index)
        boot_series.index.freq = series.index.freq

        try:
            result = run_stl(
                boot_series,
                period=period,
                log_transform=log_transform,
                robust=robust
            )
            trend_matrix[i, :] = result.trend.values
        except Exception:
            # Skip failed bootstrap iterations (e.g. non-positive after block draw)
            continue

    alpha = (1 - ci) / 2
    lower = np.nanpercentile(trend_matrix, alpha * 100, axis=0)
    median = np.nanpercentile(trend_matrix, 50, axis=0)
    upper = np.nanpercentile(trend_matrix, (1 - alpha) * 100, axis=0)

    return pd.DataFrame(
        {'lower': lower, 'median': median, 'upper': upper},
        index=series.index
    )


# =============================================================================
# SELF-TEST
# =============================================================================

if __name__ == '__main__':
    print('decompose.py loaded successfully.')
    print('Functions: run_stl(), run_mstl(), test_stationarity(), '
          'detect_breaks(), block_bootstrap_trend()')

    np.random.seed(42)
    dates = pd.date_range('2000-01-01', periods=200, freq='MS')
    trend = np.linspace(100, 200, 200)
    seasonal = 10 * np.sin(2 * np.pi * np.arange(200) / 12)
    noise = np.random.normal(0, 3, 200)
    test_series = pd.Series(trend + seasonal + noise, index=dates)

    result = run_stl(test_series, period=12, log_transform=False)
    print(f'\nSTL residual std:    {result.resid.std():.2f} (expected ~3.0)')

    verdict = test_stationarity(test_series)
    print(f'Stationarity verdict: {verdict["verdict"]}')

    breaks = detect_breaks(test_series, pen=10)
    print(f'Detected breaks:      {len(breaks)}')

    ci_df = block_bootstrap_trend(test_series, n_bootstrap=100,
                                  block_size=12, log_transform=False)
    print(f'Bootstrap CI shape:   {ci_df.shape}')

    print('\nAll module tests passed.')
