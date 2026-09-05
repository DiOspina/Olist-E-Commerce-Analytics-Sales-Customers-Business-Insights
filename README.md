# Olist E-Commerce Analysis — Portfolio Project

Medium-to-complex **data analytics portfolio** built on the public
[Brazilian E-Commerce Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).
It goes from raw CSVs to a reproducible cleaning pipeline, a full EDA, formal statistical inference,
business-intelligence metrics (RFM, cohorts, CLV) and two supervised-machine-learning models — all
organized as numbered notebooks with a short SQL companion.

> **Author:** Diego Ospina · **Stack:** Python · pandas · NumPy · matplotlib · seaborn · SciPy ·
> scikit-learn · SQL

---

## Table of contents

- [Why this project](#why-this-project)
- [Repository layout](#repository-layout)
- [The data](#the-data)
- [Pipeline & reproducibility](#pipeline--reproducibility)
- [Notebooks](#notebooks)
- [Key findings](#key-findings)
- [Set up & run](#set-up--run)
- [Skills demonstrated](#skills-demonstrated)

---

## Why this project

This project showcases a complete, professional data-analysis workflow on ~100k orders:

1. **Understand** messy, under-normalized CSVs (granularity, keys, quality).
2. **Clean & engineer** features into tidy datasets with a reproducible pipeline.
3. **Explore** with purposeful visualizations and save publication-ready figures.
4. **Infer** with hypothesis tests and attention to assumptions (non-normality → non-parametric tests).
5. **Translate** findings into business metrics (RFM, cohorts, CLV, KPIs).
6. **Predict** with scikit-learn, avoiding data leakage and reporting balanced metrics.
7. **Communicate** with an executive summary.

Comments are written in **Spanish** for a personal touch; titles, narrative and this README are in
**English**.

---

## Repository layout

```
ecommerce-data-analysis/
├── data/
│   ├── raw/          # original Olist CSVs (read-only, not versioned)
│   └── processed/    # tidy parquet datasets produced by src/build_processed.py
├── notebooks/        # numbered notebooks (01..07) + SQL demo
├── images/           # all figures produced by the notebooks (PNG)
├── sql/              # schema.sql + queries_analysis.sql
├── src/
│   └── build_processed.py   # reproducible cleaning pipeline
├── reports/          # (reserved for report output)
├── requirements.txt
└── README.md
```

---

## The data

| File | Role | Rows (raw) |
|---|---|---|
| `olist_customers_dataset.csv` | customers + location | 99,441 |
| `olist_orders_dataset.csv` | orders + status timestamps | 99,441 |
| `olist_order_items_dataset.csv` | product/seller lines per order | 112,650 |
| `olist_order_payments_dataset.csv` | payment methods | 103,886 |
| `olist_order_reviews_dataset.csv` | reviews | 99,224 |
| `olist_products_dataset.csv` | product catalog | 32,951 |
| `olist_sellers_dataset.csv` | sellers | 3,095 |
| `olist_geolocation_dataset.csv` | zip → lat/lng | 1,000,163 |
| `product_category_name_translation.csv` | PT → EN categories | 71 |

Covers **Sep 2016 – Oct 2018**.

---

## Pipeline & reproducibility

`src/build_processed.py` turns the raw CSVs into **5 tidy parquet datasets** in `data/processed/`:

| Output | Description |
|---|---|
| `olist_master_orders.parquet` | 99,441 × 33, **order grain** (dates, delivery metrics, payments, reviews, items) |
| `olist_items.parquet` | 112,650 × 10, order-item grain with English category |
| `olist_catalog.parquet` | 32,951 × 11, clean catalog |
| `olist_geolocation_clean.parquet` | 19,015 zip → median lat/lng |
| `product_category_name_translation.parquet` | 73 translations (incl. 2 manual) |

Key cleaning decisions:
- Zip prefixes loaded as **strings** (preserve leading zeros).
- Geolocation de-duplicated to **one median point per zip**.
- Category names translated to English; missing → `not_specified`; two missing translations added.
- Delivery metrics computed **only for delivered orders**.
- Reproducible: `python src/build_processed.py` regenerates everything from `data/raw/`.

---

## Notebooks

| # | Notebook | Deliverable |
|---|---|---|
| 01 | `01_data_understanding.ipynb` | Raw inventory, granularity, data-quality, referential integrity |
| 02 | `02_cleaning_preprocessing.ipynb` | Reproducible cleaning → `data/processed/` |
| 03 | `03_eda_visualizations.ipynb` | Full EDA + 8+ figures in `images/` |
| 04 | `04_statistical_analysis.ipynb` | SciPy hypothesis tests & non-parametric inference |
| 05 | `05_business_intelligence.ipynb` | KPIs, RFM, cohort retention, CLV |
| 06 | `06_predictive_modeling.ipynb` | scikit-learn classification + regression |
| 07 | `07_conclusions.ipynb` | Executive summary & recommendations |
| — | `sql_python_demo.ipynb` | SQL + pandas interoperability (SQLite in-memory) |

---

## Key findings

- **Business snapshot:** ~99.4k orders, 96.1k customers, ~R$15.4M revenue, AOV ≈ R$159.8, ~1.14 items
  per order. São Paulo dominates orders; credit card dominates payments.
- **Delivery:** ~8.1% of delivered orders arrive **late**; late deliveries earn **significantly lower
  review scores** (Mann-Whitney U, p<0.001).
- **Distribution:** order values are strongly right-skewed; review scores are positive overall (mean
  ≈ 4.1) with a notable 1-star cluster.
- **Customers:** most buy once. RFM reveals a small **VIP/Champion** group plus a large
  **Lost / At-risk** tail — the main **retention opportunity**. Cohort retention is front-loaded;
  average CLV is stable across cohorts.
- **ML classification** (predict late delivery): random forest ROC-AUC ≈ 0.74–0.75; composition
  features (`n_items`, `freight_value`, `weight_total_g`, `customer_state`) matter most.
- **ML regression** (predict order value): random forest R² ≈ 0.37, beating a median baseline — a
  useful but imperfect forecast of basket size.

---

## Set up & run

```bash
# 1. Environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt

# 2. Regenerate the cleaned datasets from raw/
python src/build_processed.py

# 3. Run the notebooks in order (01 → 07, plus sql_python_demo)
jupyter notebook
```

The notebooks are executed in place; every figure is saved to `images/`.

---

## Skills demonstrated

- **Data cleaning & transformation** (pandas): zip codes, typos, translations, de-duplication,
  aggregation to order grain.
- **Exploratory data analysis** (pandas, matplotlib, seaborn): time series, distributions, geographies,
  correlations — with reproducible, saved figures.
- **Statistical analysis** (SciPy): normality, Spearman, Mann-Whitney U, chi-square, Kruskal-Wallis.
- **Business intelligence** (pandas): KPIs, RFM segmentation, cohort retention, CLV.
- **Machine learning** (scikit-learn): `ColumnTransformer` pipelines, imputation, scaling, one-hot
  encoding, stratified sampling, cross-validation, ROC/PR evaluation, feature importance, leakage
  awareness.
- **SQL**: schema design and analytical queries, plus pandas + SQLite interoperability.
- **Engineering**: reproducible pipeline, deterministic notebook ids, requirement pinning.

---

> Figures referenced across the project live in `images/` (e.g. `EDA_monthly_sales.png`,
> `BI_rfm_segments.png`, `ML_classification.png`).