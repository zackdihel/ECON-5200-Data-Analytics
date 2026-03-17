## Lab: The Architecture of Dimensionality — Hedonic Pricing & the Frisch-Waugh-Lovell Theorem

**Domain:** Applied Econometrics · Hedonic Pricing Theory · Linear Algebra of Regression  
**Tools:** Python 3.10+, Pandas, Statsmodels (`formula.api`), Matplotlib  
**Dataset:** 2026 California Real Estate Metrics — Zillow Synthetic Panel (`Sale_Price`, `Property_Age`, `Distance_to_Tech_Hub`)

---

### Objective

To execute a multivariate hedonic pricing model on California real estate data and manually prove the **Frisch-Waugh-Lovell (FWL) theorem** — demonstrating, through explicit residual extraction and sequential OLS, that multivariate regression is not a statistical convenience but a precise geometric operation that partials out shared covariance between predictors before estimating any individual coefficient.

---

### Methodology

- **Hedonic Pricing Model (Full OLS):** Estimated the baseline multivariate OLS model regressing `Sale_Price` on `Property_Age` and `Distance_to_Tech_Hub` simultaneously using Statsmodels' `formula.api`. In hedonic pricing theory, a property's market value is decomposed into the implicit prices of its constituent attributes — each coefficient represents the market's marginal willingness to pay for a unit change in that attribute, holding all other attributes constant. The full model establishes the benchmark coefficients against which the FWL proof is subsequently verified.

- **Omitted Variable Bias Demonstration:** Estimated a restricted model omitting `Distance_to_Tech_Hub` and recorded the resulting coefficient on `Property_Age`. The omitted variable is correlated with both the included regressor (properties near tech hubs tend to be newer, or conversely, older in historically developed urban cores) and the outcome (proximity to employment centres commands a location premium). OLS, unable to distinguish the source of the price variation, loads the location premium onto `Property_Age` — producing a coefficient that is neither the causal effect of age nor a useful descriptive statistic, but a contaminated mixture of both.

- **FWL Residual Extraction — Partialling Out:** Manually implemented the three-stage FWL procedure:
  1. Regressed `Property_Age` on `Distance_to_Tech_Hub`; extracted the residuals `ẽ_age` — the component of property age that is **orthogonal** to tech hub proximity.
  2. Regressed `Sale_Price` on `Distance_to_Tech_Hub`; extracted the residuals `ẽ_price` — the component of sale price that is similarly orthogonal to tech hub proximity.
  3. Regressed `ẽ_price` on `ẽ_age` — a simple bivariate OLS on two residualised series that, by construction, share no covariance with the omitted dimension.

- **Exact Coefficient Verification:** Compared the slope coefficient from the final FWL bivariate regression against the `Property_Age` coefficient from the full multivariate model. The FWL theorem guarantees these are numerically identical; the manual proof confirms this equality holds to floating-point precision — establishing that the geometry of multivariate OLS is not an approximation of partial effects but an exact algebraic implementation of them.

---

### Key Findings

**Omitted Variable Bias — The Misattribution**

The bivariate model omitting tech hub proximity produced a severely distorted coefficient on `Property_Age`. Because `Distance_to_Tech_Hub` is correlated with both property age and sale price, the restricted OLS model attributed a component of the location premium — the price increment commanded by proximity to tech employment — to the physical age of the structure. The direction and magnitude of the resulting bias were consistent with the standard OVB formula:

> *Bias = (coefficient of omitted variable) × (coefficient from regressing omitted on included)*

This is not a modelling error in the conventional sense — there was no coding mistake, no data error, no invalid assumption. The bias was introduced by the *decision to omit*, and the model faithfully reported the best linear estimate of the relationship *given the information it was provided*. The error was architectural, not computational.

**FWL Proof — Algorithmic Ceteris Paribus**

The manual residual procedure produced a `Property_Age` coefficient that matched the full multivariate OLS estimate to floating-point precision. This is the formal proof that multivariate regression implements *ceteris paribus* — holding all other regressors constant — not as an assumption or an approximation, but as an exact algebraic consequence of projecting the outcome and the regressor of interest onto the orthogonal complement of the remaining covariate space.

The practical implication is significant: when a multivariate OLS model returns a coefficient on `Property_Age`, it is not reporting the raw correlation between age and price. It is reporting the correlation between *the part of age that cannot be explained by any other regressor in the model* and *the part of price that cannot be explained by any other regressor in the model*. Every multivariate coefficient is, in this sense, already a residualised partial effect — the FWL theorem makes the geometry of that operation explicit.

---

### Economic Interpretation

The hedonic pricing framework operationalises a specific theory of value: that market prices are linear aggregations of attribute-specific implicit prices, and that isolating any single implicit price requires holding all other attribute prices constant. The FWL theorem is the mathematical proof that multivariate OLS accomplishes exactly this — not because the algorithm was designed to "control for covariates" in some intuitive sense, but because projection onto orthogonal subspaces is what the least-squares objective function produces when minimised over a multi-column design matrix.

The OVB finding in this lab is a direct demonstration of what happens when the hedonic model is mis-specified: the market's location premium does not disappear when `Distance_to_Tech_Hub` is omitted. It reallocates — onto whichever included variable is most correlated with the omitted one. In the California real estate context, that variable is property age, producing a coefficient that overstates (or understates, depending on the correlation sign) the market's implicit price of structural age by the full magnitude of the misattributed location effect.

The lesson generalises beyond real estate. In any hedonic or quasi-hedonic pricing context — executive compensation decomposition, consumer willingness-to-pay estimation, wage structure analysis — the validity of every coefficient in the model depends on the completeness of the attribute set. An omitted attribute is not a missing observation; it is a latent variable that contaminates every coefficient with which it shares covariance. The FWL theorem is the proof of why adding it back fixes the contamination exactly.

---

*Part of ECON 5200: Applied Data Analytics in Economics*
