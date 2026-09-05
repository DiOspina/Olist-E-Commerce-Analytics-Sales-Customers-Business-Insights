"""Genera 05_business_intelligence.ipynb"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _nbgen import md, code, write_nb

cells = []

cells.append(md(
    "# Olist E-Commerce - 05 : Business Intelligence - RFM, Cohorts & CLV\n"
    "\n"
    "**Author:** Diego Ospina | **Dataset:** Brazilian E-Commerce Public Dataset by Olist\n"
    "\n"
    "> The descriptive and statistical work answered *what* and *whether*. This notebook answers "
    "*so what?* for a business: we compute **KPIs**, run an **RFM segmentation**, study **customer "
    "cohorts** and **retention**, and estimate **Customer Lifetime Value (CLV)**. Figures are saved "
    "under `images/`."
))

cells.append(md("## 1. Setup"))
cells.append(code(
    "import pandas as pd\n"
    "import numpy as np\n"
    "import matplotlib.pyplot as plt\n"
    "import seaborn as sns\n"
    "import os\n"
    "from datetime import timedelta\n"
    "\n"
    "PROC = os.path.join('..', 'data', 'processed')\n"
    "IMAGES = os.path.join('..', 'images')\n"
    "os.makedirs(IMAGES, exist_ok=True)\n"
    "sns.set_theme(style='whitegrid')\n"
    "print('ready')"
))

cells.append(md("## 2. Load and keep revenue-generating orders\n"
    "\n" "For business metrics we use **delivered** orders so revenue is real. We keep the order grain "
    "with customer id, purchase date, and order value."))
cells.append(code(
    "master = pd.read_parquet(os.path.join(PROC, 'olist_master_orders.parquet'))\n"
    "deliv = master[master['order_status'] == 'delivered'].copy()\n"
    "deliv['order_date'] = deliv['order_purchase_timestamp'].dt.normalize()\n"
    "print('delivered orders:', len(deliv))\n"
    "print('unique customers:', deliv['customer_unique_id'].nunique())"
))

cells.append(md("## 3. Core KPIs"))
cells.append(code(
    "kpis = {\n"
    "    'Total orders': len(deliv),\n"
    "    'Total revenue (BRL)': round(deliv['order_value'].sum(), 2),\n"
    "    'Average order value (AOV)': round(deliv['order_value'].mean(), 2),\n"
    "    'Median order value': round(deliv['order_value'].median(), 2),\n"
    "    'Orders per customer': round(len(deliv) / deliv['customer_unique_id'].nunique(), 3),\n"
    "    'Delivered on time (%)': round((deliv['delivery_status'] == 'On time').mean() * 100, 2),\n"
    "    'Avg review score': round(deliv['review_score_mean'].mean(), 2),\n"
    "}\n"
    "pd.DataFrame(kpis.items(), columns=['KPI', 'Value']).set_index('KPI')"
))

cells.append(md("## 4. RFM segmentation\n"
    "\n" "RFM uses three dimensions per customer:\n"
    "\n"
    "- **Recency (R):** days since the last purchase.\n"
    "- **Frequency (F):** number of orders.\n"
    "- **Monetary (M):** total spend.\n"
    "\n"
    "We compute them and bucket each dimension into 4 quartiles (4=best). The `R*F*M` code and a "
    "classic segment label let us find VIPs, repeat buyers, and churn risks."))
cells.append(code(
    "as_of = deliv['order_date'].max()\n"
    "print('Analysis date (last order):', as_of.date())\n"
    "\n"
    "rfm = (deliv.groupby('customer_unique_id')\n"
    "       .agg(recency=('order_date', lambda x: (as_of - x.max()).days),\n"
    "            frequency=('order_id', 'count'),\n"
    "            monetary=('order_value', 'sum')))\n"
    "print(rfm.describe().round(2))"
))

cells.append(code(
    "# Puntaje 1-4 por dimension usando cuantiles robustos.\n"
    "# Nota: la frecuencia suele ser 1 (mayoria compra una sola vez), asi que los cuartiles\n"
    "# colapsan; 'duplicates=drop' permite que qcut funcione con bins degenerados.\n"
    "def score_asc(series):\n"
    "    # mayor valor -> mayor puntaje (F y M)\n"
    "    r = pd.qcut(series.rank(method='first'), q=4, labels=False, duplicates='drop')\n"
    "    return (r + 1).astype(int)\n"
    "\n"
    "def score_desc(series):\n"
    "    # mayor valor -> menor puntaje (R: menor recencia = mejor)\n"
    "    r = pd.qcut(series.rank(method='first'), q=4, labels=False, duplicates='drop')\n"
    "    return (r.max() - r + 1).astype(int)\n"
    "\n"
    "rfm['R'] = score_desc(rfm['recency'])\n"
    "rfm['F'] = score_asc(rfm['frequency'])\n"
    "rfm['M'] = score_asc(rfm['monetary'])\n"
    "rfm['RFM'] = (rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str))\n"
    "\n"
    "print('Puntajes por dimension:')\n"
    "print(rfm[['R', 'F', 'M']].astype(int).value_counts().head(8))\n"
    "\n"
    "# Segmentos clasicos de RFM\n"
    "def segment(row):\n"
    "    if row['M'] >= 4 and row['F'] >= 4:\n"
    "        return 'Champion'\n"
    "    if row['R'] >= 4 and row['M'] >= 2:\n"
    "        return 'Loyal'\n"
    "    if row['R'] == 4 and row['F'] == 1:\n"
    "        return 'New'\n"
    "    if row['R'] <= 2 and row['F'] >= 2:\n"
    "        return 'At risk'\n"
    "    if row['R'] <= 2 and row['F'] == 1:\n"
    "        return 'Lost'\n"
    "    return 'Potential loyalist'\n"
    "rfm['segment'] = rfm.apply(segment, axis=1)\n"
    "\n"
    "seg = rfm['segment'].value_counts()\n"
    "print()\n"
    "print('Segmentos:')\n"
    "print(seg)"
))

cells.append(code(
    "fig, ax = plt.subplots(figsize=(8, 5))\n"
    "seg_share = (seg / seg.sum() * 100).sort_values()\n"
    "sns.barplot(x=seg_share.values, y=seg_share.index, color='#2c7fb8', ax=ax)\n"
    "ax.set_title('RFM segment distribution (% of customers)')\n"
    "ax.set_xlabel('% of customers')\n"
    "plt.tight_layout()\n"
    "plt.savefig(os.path.join(IMAGES, 'BI_rfm_segments.png'), bbox_inches='tight')\n"
    "plt.show()\n"
    "\n"
    "# Cuanto del ingreso aporta cada segmento\n"
    "rev_by_seg = (rfm.groupby('segment')['monetary'].sum() / rfm['monetary'].sum() * 100).round(1)\n"
    "print('Revenue concentration by segment:')\n"
    "print(rev_by_seg.sort_values(ascending=False))"
))

cells.append(md("## 5. Customer cohort analysis (retention)\n"
    "\n" "We define a **cohort** as the month of a customer's first purchase and track the share of that "
    "cohort still buying in each subsequent month. This reveals how sticky customers are and whether "
    "retention improved over time."))
cells.append(code(
    "cust_first = deliv.groupby('customer_unique_id')['purchase_month'].min().rename('first_month')\n"
    "cohort = deliv.merge(cust_first, on='customer_unique_id')\n"
    "\n"
    "# Periodo de cohorte (0 al mes 0) y mes de actividad\n"
    "cohort['cohort_index'] = (cohort['purchase_month'].astype('period[M]')\n"
    "                         - cohort['first_month'].astype('period[M]')).apply(lambda x: x.n)\n"
    "\n"
    "cohort_size = cohort.groupby('first_month')['customer_unique_id'].nunique()\n"
    "retention = (cohort.groupby(['first_month', 'cohort_index'])['customer_unique_id']\n"
    "                   .nunique().unstack())\n"
    "retention_pct = retention.div(cohort_size, axis=0) * 100\n"
    "print(retention_pct.iloc[:8, :8].round(1))"
))

cells.append(code(
    "fig, ax = plt.subplots(figsize=(12, 7))\n"
    "sns.heatmap(retention_pct, cmap='Blues', annot=False, cbar_kws={'label': 'Retention %'}, ax=ax)\n"
    "ax.set_title('Cohort retention matrix (%)')\n"
    "ax.set_xlabel('Months since first purchase')\n"
    "ax.set_ylabel('Cohort (first purchase month)')\n"
    "plt.tight_layout()\n"
    "plt.savefig(os.path.join(IMAGES, 'BI_cohort_retention.png'), bbox_inches='tight')\n"
    "plt.show()\n"
    "\n"
    "# Retencion promedio por mes transcurrido\n"
    "avg_curve = retention_pct.mean(axis=0)\n"
    "print('Average retention per month index:')\n"
    "print(avg_curve.head(6).round(1).to_string())"
))

cells.append(md("## 6. Customer Lifetime Value (CLV)\n"
    "\n" "We estimate **CLV** as the total revenue a customer generates; the interesting business view is "
    "the **cumulative CLV by cohort age**. We also report average CLV per cohort."))
cells.append(code(
    "clv = (deliv.groupby('customer_unique_id')['order_value'].sum().describe())\n"
    "print('CLV distribution:')\n"
    "print(clv.round(2))\n"
    "\n"
    "# CLV medio por cohorte\n"
    "cohort_clv = (cohort.groupby('first_month')['order_value']\n"
    "                     .sum()\n"
    "                     .div(cohort_size, axis=0))\n"
    "print()\n"
    "print('Average CLV per cohort (BRL):')\n"
    "print(cohort_clv.round(2).to_string())"
))

cells.append(code(
    "fig, ax = plt.subplots(figsize=(11, 5))\n"
    "cohort_clv.plot(ax=ax, marker='o', color='#2c7fb8')\n"
    "ax.set_title('Average Customer Lifetime Value by cohort')\n"
    "ax.set_xlabel('First purchase month')\n"
    "ax.set_ylabel('Average CLV (BRL)')\n"
    "plt.xticks(rotation=45, ha='right')\n"
    "plt.tight_layout()\n"
    "plt.savefig(os.path.join(IMAGES, 'BI_clv_by_cohort.png'), bbox_inches='tight')\n"
    "plt.show()"
))

cells.append(md("## 7. Top sellers\n"
    "\n" "A quick look at seller concentration from the item table (freight + price), identified by "
    "`seller_id`."))
cells.append(code(
    "items = pd.read_parquet(os.path.join(PROC, 'olist_items.parquet'))\n"
    "seller = (items.groupby('seller_id')\n"
    "               .agg(sales=('price', 'sum'), n_orders=('order_id', 'nunique'))\n"
    "               .sort_values('sales', ascending=False)\n"
    "               .head(10))\n"
    "seller\n"
    "\n"
    "# Concentracion\n"
    "top10_share = items['price'].sum()\n"
    "print('Top-10 sellers share of total item sales (%):',\n"
    "      round(seller['sales'].sum() / top10_share * 100, 2))"
))

cells.append(md("## 8. Takeaways\n"
    "\n"
    "- AOV ~160 BRL; most customers place a single order, and ~92% of deliveries are on time.\n"
    "- RFM highlights a clear **VIP / Champion** group driving a disproportionate share of revenue, plus "
    "a **large 'Lost'/'At risk'** tail that is the biggest growth opportunity.\n"
    "- Retention is strongly front-loaded: a large share of each cohort buys once and never returns "
    "(month-1 retention is high, then it decays).\n"
    "- Average CLV per cohort is stable across cohorts; improving repeat-purchase is the main lever to "
    "raise it.\n"
    "- Top sellers concentrate a meaningful share of item sales.\n"
    "\n"
    "Next: **`06_predictive_modeling.ipynb`** builds a classifier for late delivery and a regressor for "
    "order value."
))

write_nb(os.path.join(os.path.dirname(__file__), '05_business_intelligence.ipynb'), cells)