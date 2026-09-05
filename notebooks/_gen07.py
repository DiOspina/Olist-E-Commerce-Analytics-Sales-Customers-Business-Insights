"""Genera 07_conclusions.ipynb"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _nbgen import md, code, write_nb

cells = []

cells.append(md(
    "# Olist E-Commerce - 07 : Conclusions & Executive Summary\n"
    "\n"
    "**Author:** Diego Ospina | **Dataset:** Brazilian E-Commerce Public Dataset by Olist\n"
    "\n"
    "> This final notebook condenses the whole project into an **executive summary**: the KPIs, the key "
    "insights from each stage (EDA, statistics, BI, ML), and actionable recommendations. Figures are "
    "recomputed inline (from the cleaned datasets) so every number below is reproducible."
))

cells.append(md("## 1. Snapshot of the business"))
cells.append(code(
    "import pandas as pd\n"
    "import os\n"
    "\n"
    "PROC = os.path.join('..', 'data', 'processed')\n"
    "m = pd.read_parquet(os.path.join(PROC, 'olist_master_orders.parquet'))\n"
    "it = pd.read_parquet(os.path.join(PROC, 'olist_items.parquet'))\n"
    "d = m[m['order_status'] == 'delivered']\n"
    "\n"
    "kpi = {\n"
    "    'Total orders': f\"{len(m):,}\",\n"
    "    'Delivered orders': f\"{len(d):,}\",\n"
    "    'Unique customers': f\"{m['customer_unique_id'].nunique():,}\",\n"
    "    'Sellers': f\"{it['seller_id'].nunique():,}\",\n"
    "    'Products in catalog': f\"{it['product_id'].nunique():,}\",\n"
    "    'Total revenue (BRL)': f\"{d['order_value'].sum():,.0f}\",\n"
    "    'Average order value (BRL)': f\"{d['order_value'].mean():,.2f}\",\n"
    "    'Avg items per order': f\"{d['n_items'].mean():.2f}\",\n"
    "    'Late deliveries (%)': f\"{(d['delivery_status']=='Late').mean()*100:.2f}\",\n"
    "    'Avg review score': f\"{m.dropna(subset=['review_score_mean'])['review_score_mean'].mean():.2f}\",\n"
    "    'States covered': f\"{m['customer_state'].nunique()}\",\n"
    "}\n"
    "pd.DataFrame(kpi.items(), columns=['KPI', 'Value']).set_index('KPI')"
))

cells.append(md("## 2. Key insights by analysis stage"))
cells.append(md(
    "### Understanding (01) and Cleaning (02)\n"
    "- The data spans **Sep 2016 - Oct 2018**; ~97% of orders are `delivered`.\n"
    "- Zip codes are strings; category names were translated to English and missing ones labelled "
    "`not_specified`; geolocation was de-duplicated to one point per zip.\n"
    "\n"
    "### EDA (03)\n"
    "- Sales grow strongly over time (best month ~988k BRL).\n"
    "- Order values are heavily right-skewed (median ~105 BRL vs mean ~160 BRL).\n"
    "- ~92% of delivered orders arrive on time (8.11% late).\n"
    "- Reviews are positive overall (mean ~4.1) with a notable 1-star cluster.\n"
    "- São Paulo animates the marketplace; credit card is the dominant payment method.\n"
    "\n"
    "### Statistics (04)\n"
    "- `order_value` is **non-normal**, so non-parametric tests were used.\n"
    "- Price and delivery delay are practically uncorrelated.\n"
    "- **Late deliveries earn significantly lower review scores** (Mann-Whitney U, p<0.001).\n"
    "- Payment method and punctuality are statistically (but not practically) associated.\n"
    "\n"
    "### Business intelligence (05)\n"
    "- RFM finds a **Champion/VIP** group that drives a disproportionate share of revenue plus a large "
    "**Lost/At-risk** tail (most customers buy once).\n"
    "- Cohort retention is front-loaded: many customers purchase once and never return.\n"
    "- Average CLV per cohort is stable; repeat purchase is the main lever to raise it.\n"
    "\n"
    "### Predictive modeling (06)\n"
    "- **Classification** (late order): Random Forest reaches ROC-AUC ~0.74-0.75; composition features "
    "(`n_items`, `freight_value`, `weight_total_g`, `customer_state`) matter most.\n"
    "- **Regression** (order value): Random Forest explains a moderate share of variance (R2 ~0.37) and "
    "beats a median baseline, reflecting the difficulty of forecasting basket size.\n"
))

cells.append(md("## 3. Sanity checks on the cleaned data"))
cells.append(code(
    "# Verificacion final: integridad y rangos del dataset limpio\n"
    "assert len(m) == 99441, 'master order count'\n"
    "assert m['order_value'].notna().sum() > 0\n"
    "assert m['delivery_status'].eq('On time').any() and m['delivery_status'].eq('Late').any()\n"
    "print('Range of purchase dates:', m['order_purchase_timestamp'].min().date(), 'a', m['order_purchase_timestamp'].max().date())\n"
    "print('Master rows:', len(m), '| cols:', m.shape[1])\n"
    "print('Todos los chequeos pasaron OK.')"
))

cells.append(md("## 4. Executive recommendations"))
cells.append(md(
    "1. **Logistics (impactful & cheap):** the ~8% late orders are strongly associated with lower "
    "review scores. Prioritizing on-time delivery for the largest/weight-heaviest orders should lift "
    "average satisfaction.\n"
    "2. **Customer retention:** most customers buy once. A reactivation program aimed at the "
    "`Lost` / `At-risk` RFM segments and post-purchase incentives could raise repeat rates and "
    "average CLV more than acquiring new customers.\n"
    "3. **Category strategy:** concentrate merchandising on the top revenue categories (led by "
    "bed_bath_table and health_beauty) while using the long tail for assortment depth.\n"
    "4. **Forecasting:** the regression model gives a useful (if imperfect) baseline for expected basket "
    "size; combining it with logistics features would support stock and fleet planning.\n"
))

cells.append(md(
    "## 5. What is included in this portfolio\n"
    "\n"
    "| Notebook | Deliverable |\n"
    "|---|---|\n"
    "| `01_data_understanding` | Raw data inventory, granularity, data quality, referential integrity |\n"
    "| `02_cleaning_preprocessing` | Reproducible pipeline -> 5 tidy datasets in `data/processed/` |\n"
    "| `03_eda_visualizations` | Full EDA with 8+ figures saved in `images/` |\n"
    "| `04_statistical_analysis` | scipy hypothesis tests & inference |\n"
    "| `05_business_intelligence` | KPIs, RFM, cohort retention, CLV |\n"
    "| `06_predictive_modeling` | scikit-learn classification + regression pipelines |\n"
    "| `07_conclusions` | Executive summary & recommendations |\n"
    "| `sql_python_demo` | SQL + pandas interoperability (SQL scripts in `sql/`) |\n"
    "\n"
    "**Stack:** Python, pandas, NumPy, matplotlib, seaborn, SciPy, scikit-learn, SQL."
))

cells.append(md(
    "## 6. How to reproduce\n"
    "\n"
    "```bash\n"
    "python -m venv .venv && .venv\\Scripts\\activate\n"
    "pip install -r requirements.txt\n"
    "python src/build_processed.py      # -> data/processed/*.parquet\n"
    "# then open the notebooks in order (01 to 07, plus sql_python_demo)\n"
    "```"
))

write_nb(os.path.join(os.path.dirname(__file__), '07_conclusions.ipynb'), cells)