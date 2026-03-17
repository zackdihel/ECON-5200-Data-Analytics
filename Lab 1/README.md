## Lab 1: Global Purchasing Power Parity Analysis via the Big Mac Index

**Domain:** International Economics · Exchange Rate Theory  
**Tools:** Python, Pandas  
**Dataset:** The Economist Big Mac Index (2015)

---

### Objective

To empirically test the **Law of One Price** using *Burgernomics* — evaluating whether observed nominal exchange rates reflect the purchasing power parity (PPP) implied by a standardized, globally traded consumer good.

---

### Methodology

- **Data Ingestion:** Manually constructed a structured dataset from The Economist's 2015 Big Mac Index using Python dictionaries, capturing local Big Mac prices and prevailing spot exchange rates across a cross-section of economies. Data was loaded into a Pandas DataFrame for analysis.

- **Implied PPP Calculation:** For each country, computed the implied PPP exchange rate as the ratio of the local currency price to the U.S. dollar price of a Big Mac — the rate at which currencies *should* trade if the Law of One Price held perfectly.

- **Currency Misalignment Estimation:** Calculated the percentage over- or under-valuation of each currency against the U.S. Dollar by comparing the implied PPP rate to the observed market exchange rate. A positive divergence indicates overvaluation; a negative divergence indicates undervaluation relative to PPP.

---

### Key Findings

Analysis of the 2015 cross-section revealed significant and systematic deviations from PPP parity across the sample:

- **Most overvalued currencies:** The **Norwegian Krone** and **Swiss Franc** emerged as the most overvalued currencies in the dataset — trading at substantial premiums above their implied PPP rates. This suggests that, relative to the U.S. Dollar benchmark, consumers in these economies face significantly higher real purchasing costs for equivalent goods. *[Replace with your exact % figures once computed.]*

- **Most undervalued currencies:** Emerging market currencies — particularly those in Southeast Asia and Latin America (e.g., the **Chinese Yuan**, **Malaysian Ringgit**) — clustered well below implied PPP, indicating that nominal exchange rates significantly overstated the real value of the U.S. Dollar in those markets. *[Replace with your exact % figures once computed.]*

- **Arbitrage implications:** The persistent and directional nature of these misalignments is consistent with well-documented structural barriers to price arbitrage in tradeable goods — including transportation costs, tariffs, non-tradeable service inputs (e.g., labour), and local market pricing power. The findings support the conclusion that the Law of One Price holds only as a long-run tendency, not a short-run equilibrium condition.

---

### Economic Interpretation

This lab operationalises a core concept from international macroeconomics: that **absolute PPP** rarely holds in practice, but the *direction* of deviations is economically meaningful. High-income, high-wage economies systematically appear overvalued under Big Mac PPP, a pattern consistent with the **Balassa-Samuelson effect** — wherein productivity differentials across tradeable and non-tradeable sectors drive persistent real exchange rate divergence.

---

*Part of ECON 5200: Applied Data Analytics in Economics*
