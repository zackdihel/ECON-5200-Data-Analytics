"""
forecast_evaluation.py
----------------------
Reusable forecast evaluation utilities for time series models.

Functions
---------
compute_mase          : Mean Absolute Scaled Error against a naive seasonal benchmark
backtest_expanding_window : Expanding-window backtest returning per-step error records
"""

from __future__ import annotations

import warnings
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# MASE
# ---------------------------------------------------------------------------

def compute_mase(
    actual: np.ndarray,
    forecast: np.ndarray,
    insample: np.ndarray,
    m: int = 1,
) -> float:
    """Compute Mean Absolute Scaled Error (MASE).

    MASE = MAE(forecast) / MAE(naive seasonal forecast on in-sample data)

    A naive seasonal forecast predicts each value as the observation m
    periods prior:  naive[t] = insample[t - m].

    MASE < 1  →  model beats the naive seasonal benchmark.
    MASE > 1  →  the naive benchmark is better.
    MASE = 1  →  model matches the naive benchmark exactly.

    Args:
        actual   : True values for the forecast period. Shape (h,).
        forecast : Predicted values for the forecast period. Shape (h,).
        insample : Historical (training) data used to compute the naive
                   baseline. Must have at least m + 1 observations.
        m        : Seasonal period for the naive forecast.
                   m=1  → random-walk benchmark (last value carried forward).
                   m=12 → monthly seasonal naive (same month last year).

    Returns:
        MASE value (float). Returns np.nan if the naive MAE is zero
        (perfectly flat in-sample history) to avoid division by zero.

    Raises:
        ValueError: If array lengths are inconsistent or m < 1.

    Examples
    --------
    >>> import numpy as np
    >>> actual   = np.array([102., 104., 106.])
    >>> forecast = np.array([101., 103., 107.])
    >>> insample = np.array([90., 92., 94., 96., 98., 100.])
    >>> compute_mase(actual, forecast, insample, m=1)
    0.6666...
    """
    actual   = np.asarray(actual,   dtype=float)
    forecast = np.asarray(forecast, dtype=float)
    insample = np.asarray(insample, dtype=float)

    if m < 1:
        raise ValueError(f"Seasonal period m must be >= 1, got {m}.")
    if len(actual) != len(forecast):
        raise ValueError(
            f"actual and forecast must have the same length "
            f"({len(actual)} vs {len(forecast)})."
        )
    if len(insample) <= m:
        raise ValueError(
            f"insample must have more than m={m} observations "
            f"to compute a naive baseline; got {len(insample)}."
        )

    # Forecast MAE
    mae_forecast = np.mean(np.abs(actual - forecast))

    # Naive in-sample MAE: mean |insample[t] - insample[t-m]|
    naive_errors = np.abs(insample[m:] - insample[:-m])
    mae_naive    = np.mean(naive_errors)

    if mae_naive == 0.0:
        warnings.warn(
            "Naive in-sample MAE is zero (constant series). "
            "Returning np.nan to avoid division by zero.",
            RuntimeWarning,
            stacklevel=2,
        )
        return np.nan

    return float(mae_forecast / mae_naive)


# ---------------------------------------------------------------------------
# Expanding-window backtest
# ---------------------------------------------------------------------------

def backtest_expanding_window(
    series: pd.Series,
    model_fn,
    min_train: int = 120,
    horizon: int = 12,
    step: int = 12,
) -> pd.DataFrame:
    """Expanding-window backtest for time series models.

    Starting from ``min_train`` observations, fits the model on the
    training slice, forecasts ``horizon`` steps ahead, records errors,
    then expands the training window by ``step`` observations and repeats.

    The MASE for each iteration is computed against the in-sample naive
    seasonal baseline using m = ``horizon`` (seasonal naive at the
    forecast frequency).  Pass a different ``m`` by wrapping ``model_fn``
    or post-processing the returned DataFrame.

    Args:
        series    : Full time series including both train and test periods.
                    Must be a ``pd.Series`` with a ``DatetimeIndex``.
        model_fn  : ``Callable(train: pd.Series) -> np.ndarray`` of length
                    ``horizon``.  The function receives the current training
                    slice and must return exactly ``horizon`` point forecasts
                    in chronological order.
        min_train : Minimum number of observations in the first training
                    window. Default 120 (10 years of monthly data).
        horizon   : Number of steps to forecast at each iteration.
                    Default 12.
        step      : Number of observations to add to the training window
                    between iterations.  Default 12 (annual step for monthly
                    data).

    Returns:
        ``pd.DataFrame`` with columns:

        ============  ======================================================
        origin        Last date of the training window for this iteration.
        horizon       Step number within the forecast (1 … horizon).
        actual        True value at the forecast date.
        forecast      Model's point forecast.
        error         ``forecast - actual`` (signed).
        abs_error     ``|forecast - actual|``.
        mase          MASE for the full horizon at this origin.
                      Repeated for every horizon-step row of the same origin.
        ============  ======================================================

        Returns an empty DataFrame with the correct columns if no complete
        forecast window fits in the series.

    Raises:
        ValueError : If ``min_train`` or ``horizon`` are non-positive, or if
                     ``min_train + horizon > len(series)``.

    Examples
    --------
    >>> import pandas as pd, numpy as np
    >>> from forecast_evaluation import backtest_expanding_window
    >>> idx  = pd.date_range('2000-01', periods=180, freq='MS')
    >>> ts   = pd.Series(np.random.randn(180).cumsum(), index=idx)
    >>> def naive(train): return np.full(12, train.iloc[-1])
    >>> results = backtest_expanding_window(ts, naive, min_train=120, horizon=12)
    >>> results.columns.tolist()
    ['origin', 'horizon', 'actual', 'forecast', 'error', 'abs_error', 'mase']
    """
    _COLUMNS = ["origin", "horizon", "actual", "forecast",
                "error", "abs_error", "mase"]

    if min_train < 1:
        raise ValueError(f"min_train must be >= 1, got {min_train}.")
    if horizon < 1:
        raise ValueError(f"horizon must be >= 1, got {horizon}.")
    if min_train + horizon > len(series):
        raise ValueError(
            f"min_train ({min_train}) + horizon ({horizon}) = "
            f"{min_train + horizon} exceeds series length ({len(series)})."
        )

    records: list[dict] = []

    train_end = min_train  # exclusive index into series

    while train_end + horizon <= len(series):
        train  = series.iloc[:train_end]
        test   = series.iloc[train_end : train_end + horizon]

        # ------------------------------------------------------------------
        # Fit and forecast
        # ------------------------------------------------------------------
        try:
            fc_array = np.asarray(model_fn(train), dtype=float)
        except Exception as exc:          # noqa: BLE001
            warnings.warn(
                f"model_fn raised at origin index {train_end}: {exc}. "
                "Skipping this window.",
                RuntimeWarning,
                stacklevel=2,
            )
            train_end += step
            continue

        if len(fc_array) != horizon:
            warnings.warn(
                f"model_fn returned {len(fc_array)} values but horizon="
                f"{horizon}. Skipping this window.",
                RuntimeWarning,
                stacklevel=2,
            )
            train_end += step
            continue

        # ------------------------------------------------------------------
        # Compute MASE for this origin (m = horizon as seasonal period)
        # ------------------------------------------------------------------
        mase_val = compute_mase(
            actual   = test.values,
            forecast = fc_array,
            insample = train.values,
            m        = min(horizon, len(train) - 1),  # guard short windows
        )

        origin_date = train.index[-1]

        for h in range(horizon):
            actual_val   = test.iloc[h]
            forecast_val = fc_array[h]
            err          = forecast_val - actual_val
            records.append(
                {
                    "origin"   : origin_date,
                    "horizon"  : h + 1,
                    "actual"   : actual_val,
                    "forecast" : forecast_val,
                    "error"    : err,
                    "abs_error": abs(err),
                    "mase"     : mase_val,
                }
            )

        train_end += step

    if not records:
        return pd.DataFrame(columns=_COLUMNS)

    return pd.DataFrame(records, columns=_COLUMNS)
