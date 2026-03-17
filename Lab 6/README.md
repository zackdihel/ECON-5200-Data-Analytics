## Lab 5: The Architecture of Bias

**Domain:** Statistical Learning Theory · Causal Inference · Experimental Design  
**Tools:** Python, Pandas, NumPy, SciPy (`chi2_contingency`), Scikit-Learn  
**Dataset:** Titanic Passenger Manifest (demonstration corpus)

---

### Objective

To investigate the **Data Generating Process (DGP)** as the root cause of systemic bias in machine learning pipelines — demonstrating that model failure is frequently not an algorithmic problem, but a *data collection* problem — and to build the forensic toolkit to detect, diagnose, and correct for three distinct failure modes: sampling variance, covariate shift, and experimental integrity violations.

---

### Methodology

**1. Simple Random Sampling — Demonstrating Variance as a Feature, Not a Bug**

Implemented repeated Simple Random Sampling (SRS) draws on the Titanic dataset to empirically demonstrate **sampling error** under finite-sample conditions. By observing the distribution of sample survival rates across repeated draws, the lab quantifies how the *randomness* of SRS — its greatest theoretical virtue — becomes its principal liability in small or imbalanced populations: class-minority groups can be systematically under- or over-represented in any single draw purely by chance, producing a model that has never "seen" the true population it will be deployed against.

**2. Stratified Sampling — Eliminating Covariate Shift at the Source**

Replaced SRS with **Stratified Sampling** via Scikit-Learn's `StratifiedShuffleSplit`, partitioning the population along the survival class axis prior to sampling. This guarantees that the joint distribution P(class | sample) mirrors P(class | population) by construction — eliminating **Covariate Shift** before it can propagate into model training. The comparison between SRS and stratified draws makes the variance reduction concrete and measurable, not merely theoretical.

**3. Sample Ratio Mismatch (SRM) Audit — Chi-Square Forensics on A/B Tests**

Conducted a **forensic audit** of simulated A/B test data using SciPy's `chi2_contingency` to detect **Sample Ratio Mismatch** — one of the most consequential and underdiagnosed failure modes in production experimentation. An SRM occurs when the observed allocation ratio between treatment and control arms diverges from the intended ratio, signalling that the randomisation mechanism itself is broken. Because SRM corrupts the assignment process upstream of any outcome measurement, *all* downstream causal inferences are invalidated — including metrics that appear statistically significant. The Chi-Square test provides a principled, low-cost gate to catch these failures before results are acted on.

---

### Key Findings

- Repeated SRS draws produced survival rate estimates with **high inter-sample variance**, with minority class representation fluctuating substantially across draws — confirming that SRS is unsuitable as a default sampling strategy for imbalanced classification problems.
- Stratified sampling **eliminated the variance in class proportions** across all draws, with treatment and control splits reflecting the population distribution to within rounding error in every iteration.
- The SRM audit **successfully flagged** simulated engineering failures via Chi-Square rejection, demonstrating that a two-line statistical test can serve as a hard gate in any A/B testing pipeline — preventing misattributed business decisions before they occur.

---

### Theoretical Extension: Survivorship Bias, Ghost Data & the Heckman Correction

#### The Problem — Why TechCrunch Unicorn Analysis Is Structurally Invalid

Analysing only the startup companies that achieved Unicorn status (≥$1B valuation) from TechCrunch coverage introduces **Survivorship Bias** — a specific and severe form of **Selection Bias** in which the sample is conditioned on an *outcome*, not randomly drawn from the population of interest.

The target population for any meaningful study of startup success is: *all companies that attempted to raise venture capital*. The observed sample — TechCrunch Unicorns — is a heavily selected subset defined by the condition "reached $1B valuation." The selection mechanism is not random. It is systematically correlated with the very features you are trying to study: founder background, funding strategy, market timing, product quality, and capital structure. Any model trained on this sample learns the characteristics of *survivors*, not the characteristics of *success* — these are not the same thing.

The practical consequence is that coefficient estimates on every explanatory variable will be **biased in unknown directions**. A regression of "years to exit" on "total funding raised" trained only on Unicorns will produce a coefficient that conflates the genuine effect of capital with the survival selection effect — because underfunded companies that failed are absent from the data entirely.

#### The Ghost Data — What You Need But Don't Have

A **Heckman Correction** (sample selection model) requires you to model the selection mechanism explicitly before estimating the outcome equation. To apply it to the Unicorn problem, you would need the following **ghost data** — observations that exist in the true DGP but are absent from your TechCrunch sample:

| Ghost Data Type | Description | Why It's Missing |
|---|---|---|
| **Failed startups** | Companies that raised VC but shut down, were acqui-hired below threshold, or became zombies | No TechCrunch coverage; no CrunchBase exit record |
| **Selection-stage covariates** | Features recorded *at founding* or *at first raise* — before the survival outcome was determined | Survivorship databases only backfill known winners |
| **Exclusion restriction variable** | At least one variable that predicts *selection into the sample* (i.e., reaching Unicorn status) but has **no direct effect** on the outcome of interest (e.g., time-to-profitability) | Requires domain knowledge; cannot be derived from survivor data alone |

The third row is the hardest. A valid Heckman requires an **exclusion restriction** — an instrumental variable for selection. In the Unicorn context, a candidate might be: *proximity of founding city to a Tier-1 VC hub* (which affects the probability of raising enough to reach $1B, but has no direct effect on underlying business fundamentals). Without a credible exclusion restriction, the Heckman reduces to a model identified only by the non-linearity of the inverse Mills ratio — technically valid, but fragile.

#### The Correction Mechanism

The Heckman procedure operates in two stages:

1. **Selection equation (Probit):** Model the probability that a startup *enters the observed sample* (P(Unicorn = 1)) as a function of all available covariates including the exclusion restriction. From this, compute the **Inverse Mills Ratio (λ)** for each observation — a scalar that quantifies how unrepresentative each survivor is relative to the full population.

2. **Outcome equation (OLS + λ):** Re-run the substantive regression of interest (e.g., revenue growth ~ funding strategy), now including λ as a control variable. The coefficient on λ directly tests for selection bias: if it is statistically significant, the uncorrected OLS estimates were biased, and the corrected coefficients now account for the non-random selection mechanism.

The Heckman is not a magic fix — it is only as valid as the exclusion restriction and the selection model. But it transforms a structurally invalid analysis into a defensible one, by making the selection process an explicit part of the model rather than an ignored assumption.

> **The deeper lesson:** Survivorship Bias is not a data cleaning problem. It cannot be fixed by imputation, oversampling, or regularisation. It requires ghost data — observations the world chose not to record — and a credible model of *why* they are absent. That is the difference between a statistical correction and a causal one.

---

*Part of ECON 5200: Applied Data Analytics in Economics*
