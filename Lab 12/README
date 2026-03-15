## Lab: Architecting the Prediction Engine

**Domain:** Predictive Econometrics · Real Estate Valuation · Out-of-Sample Model Evaluation  
**Tools:** Python, Pandas, NumPy, Statsmodels (Patsy Formula API)  
**Dataset:** Zillow ZHVI 2026 Micro Dataset — Cross-Sectional U.S. Real Estate Market

---

### Objective

To architect a multivariate OLS prediction engine for real estate valuation that deliberately pivots the analytical frame from *explanation* to *prediction* — evaluating model performance not by in-sample fit statistics but by out-of-sample loss minimisation, with error quantified in actual U.S. dollars to make algorithmic risk legible to a business stakeholder.

---

### Methodology

- **Transition from Explanation to Prediction:** Reframed the standard econometric objective. In an explanatory model, the goal is unbiased coefficient estimation — each parameter tells a causal story about a feature's marginal effect on valuation. In a predictive model, the goal is minimising generalisation error on unseen data. These objectives are not equivalent: a model optimised for in-sample fit (high R², interpretable coefficients) can dramatically underperform out-of-sample, while a model that sacrifices coefficient interpretability for regularisation may generalise substantially better. This lab operationalises the distinction rather than assuming the two are interchangeable.

- **Feature Architecture via Patsy Formula API:** Specified the model structure using Statsmodels' Patsy formula interface, which enforces explicit, human-readable model declarations and eliminates ambiguity in how interactions, polynomial terms, and categorical encodings enter the design matrix. Feature construction was driven by domain reasoning about real estate valuation mechanics — location premia, size-price non-linearities, and property class interactions — rather than automated selection.

- **Train/Test Split & Out-of-Sample Evaluation:** Partitioned the cross-sectional Zillow dataset into training and held-out test partitions. Model parameters were estimated exclusively on the training partition; performance was evaluated exclusively on the test partition. This discipline is the minimum viable control against **overfitting** — the regime in which a model has memorised training-sample noise rather than learnt the underlying valuation function, producing optimistic in-sample metrics that collapse on deployment.

- **Loss Function Selection — RMSE in USD:** Evaluated out-of-sample performance using **Root Mean Squared Error** computed directly in U.S. dollars rather than in normalised or percentage terms. RMSE in the native outcome unit — dollars per property — is the operationally meaningful loss metric for a real estate valuation engine: it states, in the same currency as the business decision, the average magnitude of the model's prediction error. A model reporting R² = 0.87 tells a data scientist the model explains 87% of variance. A model reporting RMSE = $42,000 tells a risk manager the model's typical valuation error is $42,000 per asset — a directly actionable number for pricing insurance, setting appraisal margins, or calibrating automated underwriting thresholds.

- **In-Sample vs. Out-of-Sample Divergence Analysis:** Compared training R² against test RMSE to diagnose the degree of overfitting. A large gap between in-sample fit and out-of-sample loss is the empirical signature of a model that has not generalised — and the primary indicator that regularisation, dimensionality reduction, or feature pruning is required before deployment.

---

### Key Findings

- **The explanation-to-prediction transition exposed a material performance gap.** The model's in-sample R² presented a favourable fit statistic; out-of-sample RMSE, evaluated in USD, quantified the actual prediction uncertainty that would be incurred in a live valuation deployment — a number the R² alone could not provide.

- **RMSE in USD reframed model evaluation as risk assessment.** Expressing prediction error in the native currency of the outcome converts a statistical diagnostic into a financial risk estimate. This reframing is directly applicable to downstream business decisions: automated valuation model (AVM) calibration, algorithmic underwriting risk buffers, and property insurance pricing all require error bounds in dollars, not in explained variance.

- **The Patsy formula interface enforced modelling discipline.** Explicit formula specification prevented the inadvertent inclusion of post-treatment or collinear features that automated pipelines routinely admit, and produced a design matrix whose structure was directly auditable — a non-trivial property in any regulated valuation context.

- **The cross-sectional structure imposed identification constraints.** Without temporal or geographic instruments, causal identification of individual feature effects is limited; the model's comparative advantage is predictive rather than structural. This distinction — between a well-identified explanatory model and a well-calibrated predictive one — is the central methodological lesson the lab formalises.

---

### Economic Interpretation

The shift from explanation to prediction is not merely a modelling choice — it is a reorientation of what the analyst is accountable for. An explanatory model is evaluated against whether its coefficients are unbiased and consistent. A predictive model is evaluated against whether it makes good decisions on data it has never seen. In high-stakes automated systems — mortgage underwriting, algorithmic appraisal, collateral valuation for structured products — the relevant metric is always the latter. A model with a beautiful causal story and a $120,000 RMSE is not fit for production; a model with no interpretable causal story and a $28,000 RMSE might be.

Quantifying algorithmic risk in the native unit of the business decision — dollars per asset, not percentage of variance explained — is the analytical translation layer between statistical modelling and commercial deployment. This lab builds that translation explicitly.

---

*Part of ECON 5200: Applied Data Analytics in Economics*
