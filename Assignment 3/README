Here's the full script and rendered plot. Let me walk you through the key design decisions and the econometric interpretation framework baked in.

---

### Script Architecture

The script is structured in three clean layers:

**`_smd()`** — Computes SMD using the correct formula per variable type: pooled-variance for continuous covariates and the pooled-proportion formula for binary indicators (e.g., `Smoker`). This distinction matters — many implementations incorrectly apply the continuous formula to dummies, inflating their apparent imbalance.

**`compute_balance()`** — Produces a tidy DataFrame sorted by pre-matching |SMD| ascending, so the worst confounders appear at the *top* of the plot where the eye naturally goes first.

**`plot_love()`** — Renders the full publication-quality figure with connector lines (showing the direction of change per covariate), dual threshold bands, annotated SMD values, and a summary statistics inset.

---

### Theoretical Visual Evidence Required to Prove Bias Mitigation

To *conclusively* claim that PSM successfully mitigated selection bias, your Love Plot must satisfy all five of these criteria:

1. **Convergence to zero.** Post-matching dots (◆) must cluster tightly around the vertical zero line. This is the core visual claim — it signals that the matched groups are *exchangeable on observables*.

2. **Monotone magnitude reduction.** Every connector line should point *leftward* (toward zero). If any covariate's |SMD| *increases* after matching, your PS model is misspecified — likely missing an interaction term or a non-linear transformation.

3. **Threshold compliance.** All post-matching |SMDs| must fall within |SMD| < 0.10 (the green shaded zone). The gold standard is < 0.05. The demo output shows BMI (0.174) and Exercise (0.226) still outside — in a real study, this would prompt PS model re-specification before proceeding.

4. **No residual directional skew.** Pre-matching SMDs often skew uniformly positive or negative, revealing systematic recruitment confounding. Post-matching, the signs should be random and near-zero — no persistent directional pull.

5. **Worst offenders most improved.** The covariates with the largest pre-matching imbalance (here: Age at 0.82, Exercise at 0.68) must show the greatest absolute reduction. If a primary confounder is stubborn post-match, it likely wasn't captured well in the logistic PS model.

The summary inset at the bottom of the plot quantifies all of this automatically — mean |SMD| before/after, covariate count within threshold, and percentage improvement — giving you a single paragraph of defensible evidence for a methods section.


