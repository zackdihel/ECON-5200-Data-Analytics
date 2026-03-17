## Lab 2: The Illusion of Growth & The Composition Effect

**Domain:** Labour Economics · Macroeconomic Measurement · Price Theory  
**Tools:** Python, fredapi, Pandas, Matplotlib  
**Data Source:** Federal Reserve Economic Data (FRED) API — Live ingestion

---

### Objective

To construct a reproducible, API-driven pipeline that retrieves live macroeconomic data from the Federal Reserve, corrects nominal wage series for inflation, and isolates a structural measurement bias — the **Composition Effect** — in order to demonstrate that the apparent 2020 wage boom was a statistical artifact rather than evidence of genuine labour market tightening.

---

### Methodology

- **Live Data Ingestion via FRED API:** Connected directly to the Federal Reserve's FRED API using the `fredapi` Python library to programmatically fetch two primary series: **AHETPI** (Average Hourly Earnings of All Private Employees) as the nominal wage proxy, and the **Consumer Price Index (CPI)** as the inflation deflator. This pipeline eliminates manual data entry and ensures reproducibility against live, revised data.

- **Real Wage Construction:** Deflated the nominal AHETPI series by the CPI to produce an inflation-adjusted real wage index, exposing the divergence between nominal and real compensation growth over a 50-year horizon — a direct empirical demonstration of **Money Illusion**.

- **Anomaly Detection — The Pandemic Spike (2020):** Identified a sharp discontinuity in the nominal wage series in Q2 2020, in which average hourly earnings appeared to surge by an anomalous magnitude inconsistent with concurrent macroeconomic conditions (record unemployment, suppressed demand). Flagged this as a candidate statistical artifact requiring further decomposition.

- **Composition Effect Correction via ECI:** Fetched the **Employment Cost Index (ECI)** from FRED as a composition-controlled wage benchmark. Unlike AHETPI — which is sensitive to changes in the *mix* of employed workers — the ECI tracks compensation for a fixed basket of occupations, holding workforce composition constant. Overlaying the ECI against AHETPI during the 2020 period isolates the divergence attributable purely to the exit of low-wage workers from the measured labour force, confirming the spike as a measurement artefact rather than a structural wage increase.

---

### Key Findings

**Finding 1 — The Money Illusion (50-Year Horizon)**  
After adjusting for CPI inflation, real wages for U.S. private-sector workers exhibited near-complete stagnation across the full sample period. Nominal wage growth — which appears substantial in unadjusted terms — is almost entirely absorbed by price-level increases, leaving real purchasing power effectively flat. This finding underscores the critical analytical distinction between nominal and real variables, and the risk of drawing policy conclusions from non-deflated series.

**Finding 2 — The Pandemic Paradox**  
The 2020 apparent wage surge, interpreted by some contemporaneous commentators as evidence of labour market rebalancing or increased worker bargaining power, is shown to be a **composition-driven illusion**. When approximately 20 million predominantly low-wage workers in hospitality, retail, and food services exited the measured labour force in March–April 2020, the *average* of the remaining workforce mechanically increased — with no underlying change in what any individual worker was actually paid. The ECI, by holding occupational composition fixed, remained stable through the same period, confirming that the AHETPI spike carries no structural signal about labour demand or compensation trends.

**Implication**  
The analysis demonstrates that **the choice of wage series is itself a methodological decision with material consequences for interpretation**. An analyst relying solely on AHETPI would overstate 2020 wage growth by a significant margin; one using the ECI would find no anomaly at all. This divergence is not noise — it is the Composition Effect in its most visible historical expression.

---

### Economic Interpretation

This lab sits at the intersection of **price theory**, **labour economics**, and **measurement statistics**. The core tension — between what a data series *appears* to show and what it *actually* measures — is one of the most consequential sources of analytical error in applied economics. The 2020 AHETPI episode serves as a near-perfect case study: a plausible narrative (workers are earning more), a compelling chart (a sharp upward spike), and a conclusion that is almost entirely wrong once the measurement mechanism is understood.

Correcting for the Composition Effect is not a technical footnote. It is the analysis.

---

*Part of ECON 5200: Applied Data Analytics in Economics*
