## Time Series Diagnostics & Advanced Decomposition

**Objective:** Diagnose and resolve common misspecifications in economic time series
decomposition pipelines, implementing production-grade STL/MSTL decomposition,
stationarity testing, and structural break detection on FRED macroeconomic data.

---

### Methodology

- Identified and corrected a multiplicative seasonality violation in retail sales
  (RSXFSN) by applying a log-transform prior to STL, converting the decomposition
  from an invalid additive specification to a correctly-specified one — confirmed
  via seasonal amplitude ratio diagnostics
- Corrected a misspecified ADF test (`regression='n'`) on Real GDP (GDPC1),
  replacing it with the theoretically appropriate `regression='ct'` specification
  and cross-validating with KPSS to produce a robust 2×2 stationarity verdict
- Extended single-period STL to MSTL for hourly electricity demand, decomposing
  simultaneous daily (period=24) and weekly (period=168) seasonal cycles that a
  standard STL cannot resolve
- Quantified GDP trend uncertainty via moving block bootstrap (500 replications,
  block size=12), preserving autocorrelation structure that i.i.d. resampling
  would destroy
- Detected structural breaks using the PELT algorithm with RBF cost, calibrating
  the penalty parameter to isolate genuine regime shifts (2008 financial crisis,
  2020 COVID shock) from noise
- Encapsulated all functionality into a reusable `decompose.py` module exposing
  `run_stl()`, `run_mstl()`, `test_stationarity()`, `detect_breaks()`, and
  `block_bootstrap_trend()` with full type hints, docstrings, and error handling

---

### Key Findings

- U.S. retail sales exhibit **multiplicative seasonality** — log-transformation
  stabilizes the seasonal amplitude ratio to ~1.0x across the 2000–2024 sample,
  validating the additive assumption
- Real GDP (GDPC1) is **integrated of order one, I(1)**: non-stationary in levels
  (ADF p > 0.05, KPSS rejects) and stationary in first differences — consistent
  with the macroeconomic literature
- PELT identifies structural breaks near the **2008–2009 recession trough** and
  **April 2020**, with per-regime stationarity tests confirming the post-2020
  recovery period exhibits distinct trend dynamics
- Decomposition results are materially sensitive to parameter choices: an incorrect
  seasonal period, missing log-transform, or miscalibrated break penalty each
  produce qualitatively different and potentially misleading conclusions about
  trend and cycle behavior