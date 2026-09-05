"""Genera 03_eda_visualizations.ipynb"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _nbgen import md, code, write_nb

cells = []

cells.append(md(
    "# Olist E-Commerce - 03 : Exploratory Data Analysis & Visualizations\n"
    "\n"
    "**Author:** Diego Ospina | **Dataset:** Brazilian E-Commerce Public Dataset by Olist\n"
    "\n"
    "> We now consume the **cleaned datasets** from `data/processed/` and run a full EDA: sales trends, "
    "by-category performance, price/review distributions, delivery behavior, geography, sellers and "
    "payments. Every figure is **saved to `images/`** (PNG) so it can be reused in a presentation or the "
    "final report.\n"
    "\n"
    "A consistent, readable style is defined once and applied to all charts."
))

cells.append(md("## 1. Setup and style"))
cells.append(code(
    "import pandas as pd\n"
    "import numpy as np\n"
    "import matplotlib.pyplot as plt\n"
    "import seaborn as sns\n"
    "import os\n"
    "\n"
    "PROC = os.path.join('..', 'data', 'processed')\n"
    "IMAGES = os.path.join('..', 'images')\n"
    "os.makedirs(IMAGES, exist_ok=True)\n"
    "\n"
    "# --- Estilo consistente para todas las figuras ---\n"
    "PALETTE = sns.color_palette('viridis')\n"
    "plt.rcParams.update({\n"
    "    'figure.dpi': 110,\n"
    "    'axes.spines.top': False,\n"
    "    'axes.spines.right': False,\n"
    "    'axes.titlesize': 13,\n"
    "    'axes.titleweight': 'bold',\n"
    "})\n"
    "sns.set_theme(style='whitegrid', palette=PALETTE)\n"
    "print('style ready')"
))

cells.append(md("## 2. Load cleaned data"))
cells.append(code(
    "master = pd.read_parquet(os.path.join(PROC, 'olist_master_orders.parquet'))\n"
    "items  = pd.read_parquet(os.path.join(PROC, 'olist_items.parquet'))\n"
    "catalog= pd.read_parquet(os.path.join(PROC, 'olist_catalog.parquet'))\n"
    "\n"
    "print('master:', master.shape)\n"
    "print('items :', items.shape)\n"
    "print('catalog:', catalog.shape)\n"
    "\n"
    "# Subconjunto operativo: solo oordenes entregadas para metricas validas\n"
    "deliv = master[master['order_status'] == 'delivered'].copy()"
))

cells.append(md("## 3. Business overview\n"
    "\n" "Quick univariate snapshot of the main business variables."))
cells.append(code(
    "print('Pedidos totales:', f\"{len(master):,}\")\n"
    "print('Pedidos entregados:', f\"{(master['order_status']=='delivered').sum():,}\")\n"
    "print('Clientes unicos:', f\"{master['customer_unique_id'].nunique():,}\")\n"
    "print('Ingreso productos (BRL):', f\"{deliv['product_value'].sum():,.0f}\")\n"
    "print('Ingreso con flete (BRL):', f\"{deliv['order_value'].sum():,.0f}\")\n"
    "print('Valor medio por pedido (BRL):', f\"{deliv['order_value'].median():,.2f}\")"
))

cells.append(md("## 4. Sales over time\n"
    "\n" "We plot monthly sales (product value) to see the growth trend and seasonality."))
cells.append(code(
    "monthly = (deliv.groupby('purchase_month')['product_value']\n"
    "                .sum()\n"
    "                .sort_index())\n"
    "\n"
    "fig, ax = plt.subplots(figsize=(12, 5))\n"
    "ax.plot(monthly.index, monthly.values, marker='o', linewidth=2, color=PALETTE[0])\n"
    "ax.set_title('Monthly sales (product value, BRL)')\n"
    "ax.set_xlabel('Month')\n"
    "ax.set_ylabel('Sales (BRL)')\n"
    "plt.xticks(rotation=45, ha='right')\n"
    "plt.tight_layout()\n"
    "plt.savefig(os.path.join(IMAGES, 'EDA_monthly_sales.png'), bbox_inches='tight')\n"
    "plt.show()\n"
    "\n"
    "print('Best month:')\n"
    "print(monthly.idxmax(), '->', f\"{monthly.max():,.0f} BRL\")"
))

cells.append(md("## 5. Sales by category\n"
    "\n" "The top product categories drive most of the revenue. We aggregate the order value by "
    "`item_category` from the item-level table."))
cells.append(code(
    "cat_sales = (items[items['order_id'].isin(deliv['order_id'])]\n"
    "             .assign(cat=lambda d: d['item_category'].replace('not_specified', 'not_specified'))\n"
    "             .groupby('item_category')['price']\n"
    "             .sum()\n"
    "             .sort_values(ascending=False)\n"
    "             .head(15))\n"
    "\n"
    "fig, ax = plt.subplots(figsize=(11, 6))\n"
    "sns.barplot(x='price', y='item_category', data=cat_sales.reset_index(),\n"
    "            color=PALETTE[0])\n"
    "ax.set_title('Top 15 product categories by sales (BRL)')\n"
    "ax.set_xlabel('Sales (BRL)')\n"
    "ax.set_ylabel('')\n"
    "plt.tight_layout()\n"
    "plt.savefig(os.path.join(IMAGES, 'EDA_sales_by_category.png'), bbox_inches='tight')\n"
    "plt.show()"
))

cells.append(md("## 6. Order value and price distributions\n"
    "\n" "E-commerce order values are right-skewed: few large purchases, many small ones. We log-scale the "
    "histogram to make the shape readable, and show a boxplot."))
cells.append(code(
    "fig, axes = plt.subplots(1, 2, figsize=(13, 5))\n"
    "\n"
    "sns.histplot(deliv['order_value'], bins=60, log_scale=True, ax=axes[0], color=PALETTE[0])\n"
    "axes[0].set_title('Order value distribution (log scale)')\n"
    "axes[0].set_xlabel('Order value (BRL)')\n"
    "\n"
    "sns.boxplot(x=deliv['order_value'], ax=axes[1], color=PALETTE[2])\n"
    "axes[1].set_title('Order value boxplot')\n"
    "axes[1].set_xlabel('Order value (BRL)')\n"
    "\n"
    "plt.tight_layout()\n"
    "plt.savefig(os.path.join(IMAGES, 'EDA_order_value_dist.png'), bbox_inches='tight')\n"
    "plt.show()"
))

cells.append(md("## 7. Delivery performance\n"
    "\n" "Most delivered orders arrive early or on time. We quantify the late share and the distribution "
    "of delivery times."))
cells.append(code(
    "# Porcentaje a tiempo vs tarde\n"
    "status_counts = deliv['delivery_status'].value_counts()\n"
    "fig, axes = plt.subplots(1, 2, figsize=(13, 5))\n"
    "\n"
    "sns.histplot(deliv['delivery_delay_days'], bins=50, ax=axes[0], color=PALETTE[0])\n"
    "axes[0].axvline(0, color='red', linestyle='--')\n"
    "axes[0].set_title('Delivery delay days (0 = on time)')\n"
    "axes[0].set_xlabel('Delay (days)')\n"
    "\n"
    "axes[1].pie(status_counts, labels=status_counts.index,\n"
    "           autopct='%1.1f%%', startangle=90, colors=PALETTE[:2])\n"
    "axes[1].set_title('On-time vs late share')\n"
    "\n"
    "plt.tight_layout()\n"
    "plt.savefig(os.path.join(IMAGES, 'EDA_delivery.png'), bbox_inches='tight')\n"
    "plt.show()\n"
    "\n"
    "late_pct = (deliv['delivery_status']=='Late').mean()*100\n"
    "print(f'Late deliveries: {late_pct:.2f}%')\n"
    "print('Median delivery time (days):', round(deliv['delivery_time_days'].median(), 2))"
))

cells.append(md("## 8. Customer reviews\n"
    "\n" "Olist reviews are discrete 1-5 scores. The distribution is bimodal and heavily positive, which "
    "is typical for e-commerce."))
cells.append(code(
    "# Redondear la media por orden a un score discreto para el histograma\n"
    "scores = master.dropna(subset=['review_score_mean'])['review_score_mean'].round()\n"
    "\n"
    "fig, ax = plt.subplots(figsize=(9, 5))\n"
    "sns.countplot(x=scores, ax=ax, palette='viridis')\n"
    "ax.set_title('Distribution of review scores (per order)')\n"
    "ax.set_xlabel('Review score')\n"
    "ax.set_ylabel('Orders')\n"
    "plt.tight_layout()\n"
    "plt.savefig(os.path.join(IMAGES, 'EDA_review_scores.png'), bbox_inches='tight')\n"
    "plt.show()\n"
    "\n"
    "print('Orders with no review:', master['review_score_mean'].isna().sum())"
))

cells.append(md("## 9. Geography - orders by state\n"
    "\n" "Brazils states are the top-level geography in `customers`. We count orders per `customer_state` "
    "to show regional concentration (São Paulo dominates)."))
cells.append(code(
    "state_counts = master['customer_state'].value_counts()\n"
    "\n"
    "fig, ax = plt.subplots(figsize=(11, 6))\n"
    "sns.barplot(x=state_counts.values, y=state_counts.index, color=PALETTE[0])\n"
    "ax.set_title('Orders by customer state')\n"
    "ax.set_xlabel('Orders')\n"
    "ax.set_ylabel('State')\n"
    "plt.tight_layout()\n"
    "plt.savefig(os.path.join(IMAGES, 'EDA_orders_by_state.png'), bbox_inches='tight')\n"
    "plt.show()\n"
    "\n"
    "print('Top 5 states:')\n"
    "print(state_counts.head(5).to_frame('orders'))"
))

cells.append(md("## 10. Payment methods"
    "\n" "Credit card dominates, followed by Brazil's `boleto`."))
cells.append(code(
    "pay_type = master['payment_type_main'].value_counts()\n"
    "\n"
    "fig, ax = plt.subplots(figsize=(8, 6))\n"
    "ax.pie(pay_type.values, labels=pay_type.index, autopct='%1.1f%%',\n"
    "       startangle=90, colors=PALETTE)\n"
    "ax.set_title('Payment methods')\n"
    "plt.tight_layout()\n"
    "plt.savefig(os.path.join(IMAGES, 'EDA_payment_methods.png'), bbox_inches='tight')\n"
    "plt.show()"
))

cells.append(md("## 11. Correlation heatmap\n"
    "\n" "We look at how the main numeric variables relate. Retain only delivered orders to avoid mixing "
    "nulls from non-delivered rows."))
cells.append(code(
    "num_cols = ['order_value', 'product_value', 'freight_value', 'n_items',\n"
    "            'n_products', 'n_sellers', 'delivery_time_days', 'delivery_delay_days',\n"
    "            'review_score_mean', 'total_paid', 'n_installments_max', 'n_categories']\n"
    "corr = deliv[num_cols].corr()\n"
    "\n"
    "fig, ax = plt.subplots(figsize=(11, 8))\n"
    "sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0, ax=ax)\n"
    "ax.set_title('Correlation matrix - numeric variables')\n"
    "plt.tight_layout()\n"
    "plt.savefig(os.path.join(IMAGES, 'EDA_correlation.png'), bbox_inches='tight')\n"
    "plt.show()"
))

cells.append(md("## 12. Takeaways\n"
    "\n"
    "- Sales grow steadily from 2016 to 2018; the best month reaches ~988k BRL in product value.\n"
    "- Health & beauty, and a handful of other categories, dominate revenue.\n"
    "- Order values are highly right-skewed; most orders are small, with a long tail of large ones.\n"
    "- ~92% of delivered orders arrive **on time**; late orders average only a few days of delay.\n"
    "- Reviews are strongly positive overall (mode = 5), but a notable 1-star cluster reveals "
    "dissatisfaction worth investigating in the stats notebook.\n"
    "- São Paulo (SP) is the top ordering state; credit card is the main payment method.\n"
    "- `order_value` correlates mainly with `n_items` / `n_products`; delivery time correlates modestly "
    "with delay.\n"
    "\n"
    "Next: **`04_statistical_analysis.ipynb`** adds formal statistical tests and deeper inference."
))

write_nb(os.path.join(os.path.dirname(__file__), '03_eda_visualizations.ipynb'), cells)