### Tree-Based Models — Random Forests

**Objective:** 
Benchmarked ensemble tree methods against linear baselines on the California Housing dataset to evaluate predictive performance, diagnose feature attribution bias, and deliver an interactive model exploration tool.

**Methodology:**

Compared Decision Tree, Ridge Regression, and Random Forest regressors across 20,640 observations and 8 engineered features, with correct train/test evaluation protocols Tuned Random Forest hyperparameters (n_estimators, max_depth, max_features) via GridSearchCV with 5-fold cross-validation Diagnosed MDI feature importance bias toward high-cardinality features; validated rankings against permutation importance on held-out data Extended the pipeline to a classification task, benchmarking RF against Logistic Regression on AUC Built an interactive four-panel Plotly dashboard with ipywidgets sliders exposing the relationship between hyperparameters, train/test R², and feature attribution in real time

**Key Findings:**

Random Forest (tuned) achieved R² = 0.8147 vs Ridge R² = 0.5759, demonstrating the performance ceiling of linear methods on spatially structured housing data MDI and SHAP/permutation rankings diverged meaningfully for geographic features (Longitude, Latitude), confirming cardinality bias as a practical concern in production feature selection Marginal R² gains from additional trees plateaued beyond ~150–200 estimators, establishing a cost-performance threshold relevant for deployment decisions Gradient Boosting matched or exceeded tuned RF performance, consistent with its bias-reduction mechanism outperforming variance-averaging on this dataset
