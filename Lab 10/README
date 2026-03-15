## Lab 10: Correlation, Causality, and Spurious Regression

**Domain:** Macroeconometrics · Causal Identification · Time Series Analysis  
**Tools:** Python, Pandas, Seaborn, Statsmodels, Matplotlib  
**Dataset:** U.S. Monthly Macroeconomic Panel — FRED API (CPI, Unemployment, Fed Funds Rate, Industrial Production, Retail Sales)

---

### Objective

To demonstrate that macroeconomic variables in levels are structurally hostile to naive regression inference — producing high R², plausible-looking coefficients, and statistically significant results that are artefacts of shared trends, multicollinearity, and policy reaction functions rather than genuine causal relationships — and to build the diagnostic and transformation toolkit that makes regression on macro data defensible.

---

### Methodology

**1. Raw Correlation Heatmap — Mapping the Illusion**

Constructed a full-panel correlation matrix across all series in level form. The resulting heatmap surfaces a dense web of statistically strong relationships — CPI with unemployment, retail sales with industrial production, interest rates with inflation — nearly all of which are driven by shared trending behaviour rather than structural economic linkages. This is the starting point, not the finding: the heatmap documents the problem that every subsequent step is designed to solve.

**2. Naive OLS — Demonstrating That Fit Is Not Truth**

Estimated a baseline OLS model on untransformed level variables. The model returns a high R² and multiple significant coefficients — a result that would pass a naive quality check in any standard analytical workflow. The diagnosis: macro levels are almost always **non-stationary**, meaning their statistical properties (mean, variance, autocorrelation) drift over time. Regressing one non-stationary series on another produces **spurious regression** — a phenomenon in which two completely unrelated trending series appear causally connected purely because both move in the same direction over time. High fit in this setting is a warning sign, not a validation signal.

**3. Multicollinearity Diagnosis via VIF**

Computed **Variance Inflation Factors (VIF)** across the predictor set to quantify the degree to which coefficient estimates are destabilised by inter-predictor correlation. Iteratively removed the highest-VIF predictors, tracking the effect on coefficient stability and standard errors. A coefficient that changes sign or doubles in magnitude when a correlated predictor is added or removed has no reliable causal interpretation regardless of its p-value — VIF analysis makes this instability legible.

**4. YoY Growth Rate Transformation — Breaking the Trend**

Transformed all level variables into Year-over-Year growth rates, removing the common stochastic trend that drove the spurious correlations in Step 1. This transformation approximately **stationarises** the series — a necessary precondition for valid OLS inference in time series settings — and reframes the research question from "do these levels co-move?" (almost always yes, and almost always meaningless) to "do unexpected accelerations in one variable predict unexpected accelerations in another?" (a genuinely informative causal question).

**5. DAG-Style Causal Critique**

Applied a directed acyclic graph (DAG) framework to articulate the structural sources of confounding in the macro panel: reverse causality (the Fed raises rates *because* inflation is high, not the other way around), policy reaction functions as endogenous mechanisms, and unobserved common causes (supply shocks simultaneously driving both inflation and unemployment). The DAG critique does not produce new estimates — it identifies which estimated relationships are identified and which are not, before any statistical test is run.

**6. AI Co-Pilot Workflow & Forensics Log (Extended Analysis)**

Expanded the analysis under a structured human-AI co-pilot workflow, using the model to generate transformation hypotheses and diagnostic checks while maintaining human ownership of all causal claims. Documented decisions, model outputs, and analytical judgements in an **AI forensics log** — a structured audit trail that distinguishes AI-generated pattern recognition from analyst-validated causal inference. The forensics log is the methodological control that prevents the co-pilot workflow from becoming black-box data grubbing.

---

### Key Findings

- The naive OLS model achieved an artificially inflated R² driven by non-stationarity. The result is consistent with **Granger's (1974)** spurious regression finding: two independent random walks will produce a statistically significant regression with probability approaching 1 as the sample grows.
- VIF analysis revealed severe multicollinearity in the level specification, with multiple predictors carrying VIF scores well above the conventional threshold of 10 — rendering individual coefficient estimates analytically meaningless as isolated causal claims.
- YoY transformation materially reduced inter-series correlations, with the revised heatmap showing a substantially sparser and more plausible correlation structure. The relationships that survived transformation are more likely to reflect genuine economic linkages; those that disappeared were artefacts of shared trend.
- The DAG critique identified the Fed Funds Rate–CPI relationship as the most structurally ambiguous in the dataset — a bidirectional endogeneity problem that OLS cannot resolve without an instrument or a structural model.

---

### Theoretical Extension: The Inflation–Interest Rate Paradox and Policy Reaction Functions

#### The Paradox

A scatter plot of U.S. historical data will show a **positive correlation** between the Federal Funds Rate and CPI inflation — periods of high inflation coincide with high interest rates. A naive analyst might interpret this as evidence that interest rate increases *cause* inflation, which is the opposite of the intended policy effect and the opposite of the theoretical prediction from the IS-LM framework. This is not a measurement error. It is a structural identification problem.

#### Why the Positive Correlation Is Consistent With Contractionary Policy

The confusion dissolves once the **data-generating process** is made explicit. The Fed does not set interest rates exogenously and then observe the inflation outcome. It sets interest rates *in response to* observed and anticipated inflation, according to a **policy reaction function** — most famously formalised as the **Taylor Rule**:

> *i = r\* + π + α(π − π\*) + β(y − y\*)*

Where *i* is the nominal interest rate, *π* is observed inflation, *π\** is the inflation target, and *(y − y\*)* is the output gap. The critical term is *α(π − π\*)* — the Fed raises rates *more than proportionally* when inflation exceeds target. This means that in the observed data, high inflation mechanically precedes high interest rates, because the rate increase is the policy *response* to the inflation reading.

The observational data therefore records a sequence that looks like: inflation rises → interest rates rise. The causal arrow in the reaction function runs from inflation to rates. But the *intended* causal effect of the policy runs from rates to inflation — a separate, slower-moving transmission mechanism operating through credit conditions, investment, and aggregate demand. In a short time-series window, the reaction function dominates the data, and the transmission mechanism is invisible.

#### The Reverse-Causality Architecture

This is a textbook case of **reverse causality** compounded by **temporal confounding**:

| What the data shows | What is actually happening |
|---|---|
| Inflation ↑ → Interest rates ↑ | Reaction function: Fed responds to inflation |
| Interest rates ↑ → Inflation ↑ (apparent) | Spurious: both driven by the same inflationary episode |
| Interest rates ↑ → Inflation ↓ (true effect) | Transmission lag: 12–18 months, obscured in short samples |

The transmission lag is the identification problem. Contractionary policy suppresses inflation, but with a delay of four to six quarters. In a monthly regression, the contemporaneous correlation picks up the reaction function (positive), not the transmission mechanism (negative). Without an instrument for exogenous rate variation — a shock to monetary policy that is *not* driven by inflation — the causal effect of rates on inflation cannot be identified from observational data alone.

#### The Broader Lesson for Macro Regression

Policy reaction functions create a generalised identification hazard across macroeconomic data. Wherever a policy authority is responding to an economic variable — the Fed to inflation, the Treasury to unemployment, a central bank to exchange rate movements — the observational data will encode the reaction, not the effect. Any regression that fails to account for this endogeneity will produce coefficients that measure a mixture of the policy response and the policy impact in proportions that are not separable without structural assumptions.

This is why the DAG framework matters: it forces the analyst to specify the causal direction *before* interpreting the coefficient, rather than reading the causal direction *off* the coefficient after the fact. A positive coefficient on interest rates in an inflation regression is not evidence of expansionary monetary policy. It is evidence that the analyst has not controlled for the reaction function.

---

*Part of ECON 5200: Applied Data Analytics in Economics*
