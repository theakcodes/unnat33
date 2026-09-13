# Machine Learning (ML) Recommendation Architecture & Roadmap

This directory is reserved for the future Machine Learning recommendation and ranking pipeline.
**Per design specifications, ML models must NOT be implemented until the backend foundation is established.**

---

## 1. Architectural Placement & Data Flow

The ML ranking layer operates **downstream** of the deterministic, rule-based Eligibility Engine and **upstream** of the LLM Explanation service:

```
                  ┌──────────────────────────────┐
                  │      User / MSME Profile     │
                  │ (Demographics, Sector, etc.) │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │      Eligibility Engine      │
                  │ (Deterministic, Statutory)   │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │    Eligible Schemes Subset   │
                  │   (Statutory Pass / Fail)    │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │   ML Recommendation Layer    │
                  │ (scikit-learn / Cosine Sim)  │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │        Ranked Schemes        │
                  │ (Personalized Relevance)     │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │    LLM Explanation Service   │
                  │ (Natural Language / Guidance)│
                  └──────────────────────────────┘
```

> **CRITICAL RULE**:
> ML algorithms and LLMs must **NEVER** determine legal or statutory eligibility.
> Legal eligibility is strictly deterministic (`app/services/eligibility_service.py`).
> The ML layer's sole responsibility is **ranking and scoring already-eligible schemes** according to relevance.

---

## 2. Data Sources & Feature Engineering

When implemented, the ML recommendation models will leverage:

1. **User / Business Profile**:
   - Organization type (Micro, Small, Medium)
   - Annual turnover, existing project costs, requested financing
   - Geographic classification (State, District, Urban/Rural)
   - Primary sector and NIC (National Industrial Classification) 2/4-digit codes

2. **Scheme Characteristics**:
   - Financial limits (`min_project_cost`, `max_project_cost`, `max_loan_amount`)
   - Subsidy percentages and collateral requirements
   - Focus domains (credit, infrastructure, technology upgradation, marketing)

3. **Macro MSME Demographic Data**:
   - `msme_state_data`: State-level MSME distribution (manufacturing vs. services, gender ownership, social categories)
   - `msme_district_data`: District-level concentration of enterprises
   - `msme_activity_data`: Sectoral employment and enterprise counts

---

## 3. Technology Stack & Planned Models

- **Primary Framework**: `scikit-learn`
- **Auxiliary Libraries**: `pandas`, `NumPy`, `joblib`
- **Initial Baseline Models**:
  - Content-based filtering using cosine similarity between business feature vectors and scheme feature vectors
  - Supervised ranking / classification based on historical scheme outcome datasets
  - Unsupervised clustering (e.g., K-Means) of MSME activity patterns across districts
- **Deep Learning / PyTorch**: Only if complex unstructured text matching or dense embeddings are required later.

---

## 4. Planned Directory Structure

```
app/ml/
├── README.md             # Architecture and guidelines (this file)
├── features/             # Feature extractors and preprocessing pipelines
│   ├── business_features.py
│   └── scheme_features.py
├── models/               # Saved model artifacts (.joblib)
├── training/             # Offline training scripts
└── ranker.py             # Inference class (SchemeRanker) consumed by scheme_service
```
