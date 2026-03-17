## Lab: AI Capex Diagnostic Modeling

**Domain:** Applied Econometrics · Diagnostic Testing · Robust Inference  
**Tools:** Python, Pandas, Statsmodels, Matplotlib, Seaborn  
**Dataset:** 2026 Nvidia AI Capital Expenditure & Deployment Panel

---

### Objective

To diagnose and correct structural failures in a naive OLS model predicting AI software revenue — identifying heteroscedasticity and multicollinearity as the mechanisms producing false statistical confidence, and applying HC3 heteroscedasticity-consistent standard errors to recover valid inference from a specification that would otherwise generate systematically misleading significance tests.

---

### Methodology

- **Naive OLS Baseline:** Estimated the initial model regressing AI software revenue on capital expenditure and deployment metrics using standard OLS. Recorded coefficients, standard errors, and p-values as the contaminated baseline — the output a practitioner would act on if the model were deployed without diagnostic scrutiny.

- **Heteroscedasticity Detection:** Diagnosed non-constant error variance across the capital expenditure distribution using residual plots and formal statistical tests. The pattern was consistent with **proportional heteroscedasticity**: error variance expanding systematically at higher capex tiers, which is the expected DGP signature when the outcome variable scales with the regressor magnitude rather than shifting additively. In this structure, standard OLS standard errors are computed under the assumption of homoscedastic errors — an assumption the data violates — producing t-statistics and p-values that are arithmetically precise but inferentially invalid.

- **Multicollinearity Audit via VIF:** Computed Variance Inflation Factors across the full predictor set. Predictors with overlapping information content — capital expenditure tiers and deployment intensity metrics that co-move systematically across Nvidia's investment cycle — inflated VIF scores, signalling that coefficient estimates were unstable and standard errors artificially compressed by the correlated predictor structure. Documented which predictors were implicated and whether the multicollinearity was structural (inherent to the DGP) or incidental (resolvable by feature pruning).

- **HC3 Robust Standard Error Correction:** Re-estimated the model using **HC3 heteroscedasticity-consistent standard errors** via Statsmodels' `cov_type='HC3'` specification. HC3 — the MacKinnon-White (1985) heteroscedasticity-robust sandwich estimator with leverage correction — recomputes standard errors without assuming constant error variance, using each observation's squared residual weighted by its leverage in the design matrix. Unlike HC0 (which under-corrects in small samples with high-leverage points) or HC1 (which applies a degrees-of-freedom scalar), HC3's per-observation leverage adjustment makes it the most conservative and most reliable estimator in the presence of both heteroscedasticity and influential observations — conditions that both apply in a cross-sectional capex dataset dominated by a small number of very large deployment tiers.

- **Pre/Post Inference Comparison:** Constructed a side-by-side comparison of naive OLS versus HC3-corrected standard errors, t-statistics, and p-values. This comparison is the analytical product of the lab: it quantifies exactly how much the naive model overstated its own precision, and which coefficient-level conclusions would have been revised had the correction not been applied.

---

### Key Findings

**Heteroscedasticity Was Severe and Directional**

Residual diagnostics confirmed that error variance was not randomly distributed across the capex range — it expanded systematically with fitted values, producing a fan-shaped residual plot that is the visual signature of proportional heteroscedasticity. This structure has a direct interpretation in the AI capex context: the uncertainty in software revenue outcomes scales with the size of the capital commitment, reflecting the higher variance-of-returns environment at the frontier of large-scale AI infrastructure deployment. Standard OLS, treating this expanding variance as homoscedastic noise, compressed its standard error estimates artificially — generating p-values that reported significance the data did not actually support.

**HC3 Correction Widened Standard Errors Materially**

Applying HC3 robust estimation appropriately increased the standard errors on the deployment metric coefficients, with the magnitude of correction largest for the high-capex observations that exhibited the greatest leverage and the greatest residual variance. Several coefficients that registered as statistically significant under naive OLS lost significance after correction — meaning the naive model would have led an analyst to conclude that specific deployment metrics had a reliably detectable effect on revenue when the data, properly interrogated, could not support that conclusion.

**False Confidence Is the Failure Mode**

The critical finding is not that the model's point estimates were wrong — OLS coefficient estimates are unbiased under heteroscedasticity even when the assumption of constant variance is violated. The failure was entirely in the standard errors: the model knew approximately *how large* each effect was, but reported artificial certainty about *whether* the effect was real. An investment committee relying on the naive p-values would have made decisions under a false impression of inferential precision — a qualitatively different failure from a biased point estimate, and harder to detect without explicit diagnostic testing.

---

### Economic Interpretation

Heteroscedasticity in capital expenditure data is not a statistical anomaly to be corrected and forgotten — it is an economically meaningful property of the data-generating process. When error variance expands with capex magnitude, the model is recording the empirical reality that large-scale AI infrastructure investments are higher-variance propositions: the range of revenue outcomes at the frontier of deployment is wider than at the base. A homoscedastic model does not just misestimate its own uncertainty; it *mischaracterises the risk structure* of the investment landscape it is modelling.

HC3 correction does not change the model's view of the expected return. It corrects the model's view of its own confidence in that expectation — which is, for any decision-maker using the model to allocate capital, the more consequential number. Knowing the effect size is approximately $X is useful. Knowing whether that estimate is drawn from a tight or a dispersed distribution is what determines whether $X is actionable.

The broader lesson for AI infrastructure analytics: capital expenditure data at the frontier of technology deployment will almost always be heteroscedastic by construction, because high-investment environments are high-uncertainty environments. Any model in this domain that does not apply robust standard errors by default is not a conservative model — it is an overconfident one.

---

*Part of ECON 5200: Applied Data Analytics in Economics*
