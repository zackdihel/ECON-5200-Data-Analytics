# FedSpeak 2.0 — NLP Pipeline for Central Bank Communications

## Objective
A production-ready NLP pipeline for extracting sentiment, semantic structure,
and monetary policy signals from Federal Reserve FOMC meeting minutes.

## Methodology
- **Pipeline Diagnosis & Repair:** Identified and corrected three compounding
  errors in the baseline pipeline — a whitespace-only tokenizer that left
  punctuation attached to tokens, a Harvard General Inquirer sentiment
  dictionary that misclassifies neutral financial terms (capital, debt, tax)
  as negative, and TF-IDF parameters (min_df=1, max_df=1.0) that admitted
  both OCR noise and corpus-wide stopwords into the feature matrix
- **Preprocessing:** Replaced naive split() tokenization with
  nltk.word_tokenize, adding lemmatization and alpha-only filtering to
  produce clean, linguistically valid token streams
- **Sentiment Scoring:** Implemented Loughran-McDonald (LM) dictionary-based
  scoring across three dimensions — negativity, positivity, and uncertainty —
  purpose-built for financial and regulatory text
- **Representation Learning:** Encoded FOMC sentences using
  all-MiniLM-L6-v2 sentence transformers to capture semantic meaning beyond
  bag-of-words, and built a corrected TF-IDF matrix (min_df=5, max_df=0.85,
  bigrams) as a lexical baseline
- **Clustering:** Applied K-Means (K=3) to both embedding and TF-IDF
  representations and evaluated cluster quality via silhouette score
- **Predictive Evaluation:** Assessed both representations as features for
  predicting Fed tightening cycles using logistic regression with
  expanding-window time-series cross-validation (5 splits)
- **Module Packaging:** Delivered a reusable fomc_sentiment.py module
  exposing preprocess_fomc(), compute_lm_sentiment(), and
  build_tfidf_matrix() for downstream research use

## Key Findings
Both TF-IDF (AUC: 0.51 ± 0.03) and sentence embeddings (AUC: 0.52 ± 0.06)
performed near chance level when predicting Fed tightening cycles, with
embeddings nominally winning by a margin within the noise of both estimates.
This result reflects a constraint of the experimental design — the binary
tightening label is derived from calendar year rather than actual policy rate
changes — rather than a failure of the representations themselves. The LM
dictionary correction meaningfully reduced false-positive negative sentiment
classifications by eliminating neutral financial vocabulary, and the TF-IDF
parameter corrections produced a substantially cleaner feature space. With
ground-truth rate change labels, the semantic richness of transformer
embeddings would be expected to outperform lexical TF-IDF features given the
Fed's reliance on carefully hedged, context-dependent forward guidance language.