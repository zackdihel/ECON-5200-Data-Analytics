## Lab 9: Recovering Experimental Truths via Propensity Score Matching

**Domain:** Causal Inference · Programme Evaluation · Selection Bias Correction  
**Tools:** Python, Scikit-Learn (`LogisticRegression`), Pandas, NumPy  
**Dataset:** Lalonde (1986) — Observational Supplement (CPS/PSID)

---

### Objective

To demonstrate that a naive observational estimate of programme impact is not merely imprecise — it is structurally wrong — and to recover the true Average Treatment Effect by explicitly modelling and neutralising the selection mechanism that corrupts it.

---

### Methodology

- **Diagnosing the Selection Problem:** Established the baseline failure of the raw observational comparison. Without adjustment, participants and non-participants differ systematically on pre-treatment covariates — age, education, prior earnings, race — because programme enrolment was not random. The naive difference-in-means estimate absorbs both the treatment effect and the selection effect, rendering it causally uninterpretable.

- **Propensity Score Estimation via Logistic Regression:** Modelled the conditional probability of programme participation P(D = 1 | X) using logistic regression on the full pre-treatment covariate vector. This **propensity score** — a scalar summary of each individual's observable selection probability — collapses the multi-dimensional confounding problem into a single balancing dimension, enabling like-for-like comparison across the treatment boundary.

- **Nearest-Neighbour Matching:** For each treated unit, identified the closest untreated counterpart in propensity score space using nearest-neighbour matching. This constructs a reweighted comparison group whose covariate distribution mirrors the treated group's — approximating the counterfactual that a randomised experiment would have produced by design, using only observational data.

- **Balance Verification:** Confirmed post-matching covariate balance across treatment and matched control groups, validating that the matched sample satisfies the **Common Support** assumption and that residual covariate differences were materially reduced.

---

### Key Findings

<br>

| Estimator | ATE Estimate | Interpretation |
|---|---|---|
| Naive (Unmatched) | **−$15,204** | Selection bias dominates; non-participants earn more in baseline |
| PSM (Matched) | **+$1,800** *(approx.)* | Selection bias removed; result converges to RCT benchmark |
| RCT Benchmark (Lab 6) | **+$1,795** | Ground truth from randomised experiment |

<br>

The naive estimate is not merely attenuated — it is **inverted**. A decision-maker relying on the raw observational comparison would conclude that job training actively destroys earnings, a finding that is an artefact of selection entirely. High-baseline earners are systematically less likely to enrol; the unmatched control group is therefore drawn from a higher-earning population by construction, producing a negative gap with no causal content whatsoever.

Post-matching, the PSM estimate converges to within $5 of the randomised benchmark — a recovery of approximately **$17,000 of analytical error** in a single methodological correction. The result validates both the propensity model specification and the identifying assumption that selection operates entirely through observable covariates (conditional independence / unconfoundedness).

---

### Economic Interpretation

This lab operationalises one of the central arguments in the programme evaluation literature: that observational data is not inherently inferior to experimental data — it is inferior *when the selection mechanism is ignored*. Propensity Score Matching makes the selection mechanism explicit, models it, and conditions it away. What remains is variation in treatment assignment that is, conditional on the propensity score, as good as random.

The practical implication for applied work is direct. In most real-world settings — hiring interventions, policy roll-outs, product feature launches without clean A/B infrastructure — a randomised experiment is either infeasible or retrospectively unavailable. PSM is the toolkit that makes causal inference possible in those conditions, provided the unconfoundedness assumption holds and the propensity model is correctly specified. The Lalonde dataset is the canonical stress test for exactly this claim — and the recovery demonstrated here clears it.

---

*Part of ECON 5200: Applied Data Analytics in Economics*
