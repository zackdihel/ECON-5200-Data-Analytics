## Lab: NY Fed Yield Curve Recession Model Replication

**Domain:** Macroeconomic Forecasting · Binary Classification · Financial Econometrics  
**Tools:** Python, Pandas, NumPy, Scikit-Learn (`LogisticRegression`, `TimeSeriesSplit`), Statsmodels (`Logit`), Matplotlib, `fredapi`  
**Dataset:** FRED — `T10Y3M` (10Y–3M Treasury yield spread, daily → monthly) · `USREC` (NBER recession indicator), 1970–present

---

### Objective

To replicate the Federal Reserve Bank of New York's yield curve recession probability model — fitting a logistic regression on the 10Y–3M Treasury spread lagged 12 months against NBER recession indicators, demonstrating why the Linear Probability Model is structurally invalid for binary economic outcomes, extracting the odds ratio with confidence intervals, and generating a full recession probability time series through the contested 2022–2024 inversion period.

---

### Methodology

- **Live Data Ingestion via FRED API:** Fetched `T10Y3M` (daily) and `USREC` (monthly) directly from the Federal Reserve's FRED API using `fredapi`. Resampled the daily yield spread to a monthly average to align with the recession indicator's frequency, producing a consistent panel spanning over five decades of U.S. business cycle data from 1970 to present.

- **12-Month Lag Construction:** Applied a 12-month backward lag to the yield spread before alignment with the recession indicator — encoding the NY Fed's original model specification, in which the spread observed today is the predictor of recession status 12 months forward. This lag structure is the empirical finding that motivated the NY Fed model: the yield curve has historically inverted (spread < 0) well in advance of NBER-dated recessions, making it a leading rather than coincident indicator.

- **Linear Probability Model Failure Demonstration:** Fitted a standard OLS `LinearRegression` directly on the binary `USREC` outcome as a diagnostic baseline. Recorded predicted probabilities exceeding 1.0 and falling below 0.0 on real data — logically impossible values that confirm the LPM is misspecified for binary outcomes by construction. The OLS estimator, unconstrained to the [0,1] interval, treats a binary dependent variable as a continuous one, producing fitted values that violate the axioms of probability whenever the linear fit extends beyond the boundary of the feasible probability space.

- **Logistic Regression — S-Curve Estimation:** Fitted Scikit-Learn's `LogisticRegression` on the same feature-outcome pair, constraining predicted probabilities to (0, 1) via the logistic sigmoid function. The resulting S-curve maps the full historical range of yield spread values to recession probabilities, with steep probability transitions clustered around the inversion threshold (spread ≈ 0) that marks the empirically identified recession signal region.

- **Odds Ratio Extraction with 95% Confidence Intervals:** Re-estimated the logistic model using Statsmodels' `Logit` to access the full inference machinery — coefficient standard errors, z-statistics, and confidence intervals — which Scikit-Learn does not expose natively. Exponentiated the yield spread coefficient to recover the **odds ratio**: the multiplicative change in the recession odds per unit decrease in the spread. Extracted the 95% CI on the odds ratio to quantify estimation uncertainty and establish the precision of the spread's predictive signal.

- **Time-Series Cross-Validation via `TimeSeriesSplit`:** Evaluated out-of-sample model performance using Scikit-Learn's `TimeSeriesSplit` rather than standard K-Fold — a methodologically critical choice for temporal data. Standard K-Fold randomly shuffles observations across folds, which allows future data to appear in the training set when evaluating past periods, constituting **look-ahead bias** and producing optimistic performance estimates that would not be achievable in a real-time forecasting deployment. `TimeSeriesSplit` enforces strictly forward-expanding train windows, ensuring each validation fold sees only data that would have been available at that point in history.

- **Full Probability Time Series — Including the 2022–2024 Inversion:** Generated the complete historical recession probability series by running the fitted model over the full dataset, including the 2022–2024 period during which the yield curve inverted deeply and for an extended duration. This period constitutes a live out-of-sample test of the model's signal quality: the spread-based model assigned elevated recession probabilities throughout 2023, but no NBER recession materialised — making it one of the most scrutinised episodes in the yield curve forecasting literature.

---

### Key Findings

**The Linear Probability Model Is Structurally Broken for Binary Outcomes**

The LPM fitted values produced predicted recession probabilities below 0% and above 100% at multiple points in the historical sample — not as edge-case outliers but as a direct consequence of the model's unconstrained linear form. This is not a data quality problem or a coefficient estimation error; it is the inherent failure mode of applying OLS to a binary dependent variable. The demonstration is not merely pedagogical: production risk models in financial institutions that use linear probability specifications for binary default, recession, or stress indicators are embedding this failure into their inference by construction.

**The Logistic Model Reproduced the NY Fed's Core Signal**

The fitted S-curve assigned high recession probabilities to negative spread regimes (yield curve inversion) and low probabilities to positive spread regimes (normal upward-sloping curve), consistent with the NY Fed's published model outputs. The odds ratio on the spread — with its 95% confidence interval bounded away from 1.0 — confirmed that the yield spread carries statistically significant and quantitatively meaningful predictive information about recession risk 12 months forward.

**The 2022–2024 Inversion: Elevated Signal, No Recession — The Debate**

The model assigned recession probabilities well above historical warning thresholds throughout 2023 and into 2024, driven by the most severe and prolonged 10Y–3M inversion since the early 1980s. No NBER recession materialised. This episode sits at the centre of an active debate in macroeconomic forecasting literature, with three competing interpretations:

1. **False positive:** The yield curve's predictive power has degraded in the post-QE monetary environment, where the Federal Reserve's balance sheet operations structurally suppressed long-term yields, reducing the information content of the spread as a monetary policy signal.

2. **Long and variable lags:** The transmission from inversion to recession operates through credit contraction and investment pullback over a horizon that, in this cycle, may extend beyond the model's 12-month window — consistent with the "soft landing" narrative in which the lagged effects are still propagating.

3. **Model-correct, realisation-pending:** The NBER recession dating is backward-looking and subject to revision; the near-miss of several negative quarters and significant labour market softening suggests the counterfactual without fiscal stimulus may have satisfied recession criteria.

The replication does not resolve this debate — it reproduces the model faithfully enough to participate in it with the same tools the NY Fed analysts use.

---

### Economic Interpretation

The NY Fed yield curve model is one of the most cited and most contested single-variable recession forecasting tools in macroeconomics. Its continued relevance after 50 years of quarterly business cycles is not because the yield spread has a direct causal effect on output — it does not — but because it is a compressed summary of monetary policy stance, credit market conditions, and aggregate expectations, all encoded in the shape of the Treasury curve at a single moment in time.

The logistic regression framework is appropriate precisely because the outcome — NBER recession — is binary and the predictor — yield spread — is continuous with a known threshold interpretation. The S-curve is not a modelling convenience; it is the correct functional form for a probability model over a binary event, and the LPM comparison makes this necessity concrete rather than theoretical.

The 2022–2024 episode is the methodologically richest case study the lab could have encountered. A model that performs perfectly in-sample and fails to predict the most prominent recent episode is not a failed model — it is a model that has identified a genuine structural question about whether its data-generating process has changed. That is the difference between a model that has been stress-tested and one that has only been validated.

---

*Part of ECON 5200: Applied Data Analytics in Economics*
