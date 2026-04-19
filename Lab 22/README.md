# Unsupervised Learning – Clustering & Dimensionality Reduction

## Objective
Diagnose and reconstruct a broken unsupervised learning pipeline, then apply 
K-Means and hierarchical clustering to World Development Indicator (WDI) and 
synthetic customer behavioral data to identify meaningful country and customer segments.

## Methodology
- Identified and fixed four pipeline errors: missing standardization, incorrect 
  KMeans parameter name (`k` vs `n_clusters`), PCA applied before scaling, and 
  absent `random_state` causing non-reproducible results
- Loaded and reshaped WDI data for 238 countries across 9 socioeconomic indicators 
  using the `wbgapi` API with multi-year backfill to handle sparse coverage
- Built reusable `run_kmeans_pipeline()`, `evaluate_k_range()`, and 
  `plot_pca_clusters()` utility functions
- Applied `StandardScaler` prior to K-Means and PCA to ensure equal feature contribution
- Evaluated K from 2–7 using WCSS and silhouette score
- Compared K-Means against Agglomerative (Ward linkage) clustering
- Compared PCA and UMAP for dimensionality reduction visualization

## Key Findings
- **Optimal K = 3** by silhouette score (0.704), though K=4 was used for 
  interpretability, producing four economically coherent country tiers:
  - Cluster 0 (5 countries): ultra-high income, GDP/cap $103,385, life exp 83.4
  - Cluster 1 (53 countries): high income, GDP/cap $54,635, life exp 79.6
  - Cluster 2 (112 countries): middle income, GDP/cap $16,969, life exp 71.4
  - Cluster 3 (68 countries): low income, GDP/cap $4,593, life exp 62.5
- **PC1 (45.4% variance)** captured a human development axis — life expectancy, 
  internet access, and inverse infant mortality; PC2 captured 13.5%
- **K-Means outperformed Agglomerative clustering** on WDI data (silhouette 
  0.2239 vs 0.1691); cross-tabulation showed broad agreement on the largest clusters
- **UMAP provided sharper visual separation** than PCA for the synthetic customer 
  data, better preserving local non-linear structure
- On synthetic customer data (K=3, silhouette 0.704), clusters were well-separated 
  in PCA space with PC1 and PC2 explaining 56.0% and 37.2% of variance respectively
  