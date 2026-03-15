## Lab 11: Data Wrangling & Engineering Pipeline

**Domain:** Feature Engineering · Missing Data Theory · Econometric Data Preparation  
**Tools:** Python, Pandas, Statsmodels, Missingno, Category Encoders  
**Dataset:** `messy_hr_economics.csv` — Unstructured HR Economics Panel

---

### Objective

To transform a structurally chaotic HR dataset into an econometrically valid modelling input — diagnosing and resolving missingness mechanisms, encoding categorical variables without introducing rank deficiency, and compressing high-cardinality geographic features without discarding their predictive signal.

---

### Methodology

- **Missingness Audit via Missingno:** Visualised the full missingness structure of the raw dataset using matrix and heatmap diagnostics from the `missingno` library. Classified missing observations by mechanism — distinguishing **MCAR** (Missing Completely at Random), **MAR** (Missing at Random, where absence is conditional on observed covariates), and **MNAR** (Missing Not at Random, where absence is correlated with the unobserved value itself). The distinction is not cosmetic: imputing MNAR data with column means silently biases every downstream coefficient that touches the imputed variable, while MAR missingness can be addressed with conditional imputation strategies that are asymptotically unbiased.

- **Conditional Imputation:** Imputed MAR-classified variables using strategies informed by the observed conditioning covariates — preserving the conditional distribution of the imputed series rather than collapsing it to a point estimate. Documented which variables received imputation and under which missingness assumption, creating an auditable data provenance trail.

- **Dummy Variable Trap Avoidance:** One-hot encoded all nominal categorical variables with explicit reference class dropping — retaining K−1 dummies for each K-category variable. This is not a stylistic preference; including the full dummy set introduces **perfect multicollinearity** by construction (the dropped category is a linear combination of the retained dummies), causing the OLS design matrix to become singular and coefficient estimates to be undefined. The reference class selection was made on substantive grounds — choosing the most interpretively neutral category as the baseline — so that all retained coefficients read as marginal effects relative to a meaningful benchmark.

- **Target Encoding for High-Cardinality Geography:** Replaced raw geographic identifiers — which, if one-hot encoded, would have generated hundreds of sparse binary columns — with **Target Encoding**: replacing each geographic category with the mean of the outcome variable conditional on that category, computed on the training partition. This compresses the cardinality from O(N) binary columns to a single continuous feature while preserving the geographic signal, avoiding both the dimensionality explosion of full one-hot encoding and the ordinality assumption violation of label encoding.

- **Feature Engineering:** Constructed derived structural features from the raw variables — tenure bands, compensation ratios, and interaction terms — to represent economically meaningful relationships that are not linearly recoverable from the raw inputs alone.

---

### Key Findings

- **Missingness was not random.** Missingno diagnostics revealed systematic co-missingness patterns consistent with **MAR**: the probability of a value being absent was correlated with observed department and seniority covariates, not distributed uniformly across the dataset. Treating this as MCAR and applying listwise deletion would have silently introduced selection bias into the estimation sample.

- **The Dummy Variable Trap was present in the naive encoding.** Initial full one-hot encoding of the employment category variable produced a singular design matrix, confirmed by a near-zero minimum eigenvalue on the OLS regressor matrix. Dropping the reference class restored full rank and produced stable, interpretable coefficient estimates.

- **Target Encoding materially reduced dimensionality without sacrificing signal.** The geographic identifier variable carried hundreds of unique values. Full one-hot encoding would have produced a design matrix wider than the sample — a p > n regime in which OLS is unidentified. Target encoding compressed this to a single feature that retained geographic variation in the outcome, confirmed by a meaningful improvement in held-out fit relative to dropping geography entirely.

- **The pipeline generalises.** The documented sequence — missingness audit → conditional imputation → reference-class encoding → target encoding → feature construction — is a transferable template for any unstructured HR or administrative microdata panel, not a dataset-specific patch.

---

### Economic Interpretation

Raw administrative datasets are almost never analysis-ready, and the failure mode is rarely missing values or wrong data types — it is **latent structure that violates the assumptions of the estimator**. Perfect multicollinearity, non-random missingness, and cardinality explosion are not edge cases in HR economics data; they are the default. A pipeline that does not explicitly audit for and resolve each of these three failure modes will produce models that are either algebraically undefined or statistically biased in ways that are invisible to standard regression diagnostics.

The methodological contribution of this lab is not the imputation or the encoding technique in isolation — it is the discipline of diagnosing the *type* of failure before applying a correction, rather than applying corrections as reflexive defaults. Dropping a reference class without knowing why it is required, or applying mean imputation without testing the MAR assumption, produces the appearance of a clean dataset while preserving the underlying analytical hazard.

---

*Part of ECON 5200: Applied Data Analytics in Economics*
