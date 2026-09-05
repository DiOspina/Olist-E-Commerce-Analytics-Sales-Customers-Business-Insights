"""Genera 02_cleaning_preprocessing.ipynb"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _nbgen import md, code, write_nb

cells = []

cells.append(md(
    "# Olist E-Commerce - 02 : Cleaning & Preprocessing\n"
    "\n"
    "**Author:** Diego Ospina | **Dataset:** Brazilian E-Commerce Public Dataset by Olist\n"
    "\n"
    "> The raw data is almost clean, but it needs **structure** before analysis: useful timestamps must "
    "be parsed, zip codes must be treated as strings, category names must be translated, several tables "
    "must be aggregated to the order grain, and a couple of genuine inconsistencies must be fixed. This "
    "notebook turns the messy raw files into tidy datasets saved in `data/processed/`.\n"
    "\n"
    "### Pipeline summary\n"
    "1. Reload every raw file from `data/raw/` (idempotent).\n"
    "2. Clean the small tables: geolocation (de-duplicate), products (rename typos, translate categories).\n"
    "3. Parse order timestamps and derive delivery metrics for delivered orders.\n"
    "4. Aggregate payments and reviews to the order grain.\n"
    "5. Assemble the **master order-level dataset** and write all outputs to `data/processed/`.\n"
    "\n"
    "> **Note:** this notebook reproduces exactly the logic of `src/build_processed.py`, so the datasets "
    "can be regenerated at any time by running this notebook or that script."
))

cells.append(md(
    "## 1. Setup\n"
    "\n"
    "We import the libraries, configure the display, and declare the folder paths."
))

cells.append(code(
    "import pandas as pd\n"
    "import numpy as np\n"
    "import os\n"
    "\n"
    "pd.set_option('display.max_columns', None)\n"
    "pd.set_option('display.width', 200)\n"
    "\n"
    "RAW = os.path.join('..', 'data', 'raw')\n"
    "PROC = os.path.join('..', 'data', 'processed')\n"
    "os.makedirs(PROC, exist_ok=True)\n"
    "print('paths ok')"
))

cells.append(md(
    "## 2. Load raw data\n"
    "\n"
    "We read every raw CSV. **Zip-code prefixes are loaded as strings** so we never lose leading zeros "
    "(right-padding matters for geography)."
))

cells.append(code(
    "def load(name, **kw):\n"
    "    # Carga una tabla cruda desde data/raw\n"
    "    return pd.read_csv(os.path.join(RAW, name), **kw)\n"
    "\n"
    "customers  = load('olist_customers_dataset.csv', dtype={'customer_zip_code_prefix': str})\n"
    "geolocation= load('olist_geolocation_dataset.csv', dtype={'geolocation_zip_code_prefix': str})\n"
    "order_items= load('olist_order_items_dataset.csv')\n"
    "payments   = load('olist_order_payments_dataset.csv')\n"
    "reviews    = load('olist_order_reviews_dataset.csv')\n"
    "orders     = load('olist_orders_dataset.csv')\n"
    "products   = load('olist_products_dataset.csv')\n"
    "sellers    = load('olist_sellers_dataset.csv', dtype={'seller_zip_code_prefix': str})\n"
    "categories_tr = load('product_category_name_translation.csv')\n"
    "\n"
    "raw = {'customers': customers, 'orders': orders, 'order_items': order_items, 'products': products, 'payments': payments, 'reviews': reviews, 'sellers': sellers, 'geolocation': geolocation, 'categories_tr': categories_tr}\n"
    "for name, df in raw.items():\n"
    "    print(f\"{name:14s} -> {df.shape[0]:>9,} x {df.shape[1]}\")"
))

cells.append(md(
    "## 3. Clean the small tables\n"
    "\n"
    "### 3.1 Geolocation - remove duplicates\n"
    "\n"
    "`geolocation` contains ~1M rows but only ~19k distinct zip prefixes. The official dataset ships "
    "with many duplicate coordinate sheets recorded for the same zip. We keep **one representative point "
    "per zip** (median lat/lng) and drop exact duplicates first."
))

cells.append(code(
    "before = len(geolocation)\n"
    "geo_dedup = geolocation.drop_duplicates()\n"
    "after_dedup = len(geo_dedup)\n"
    "print(f'Filas originales: {before:,}')\n"
    "print(f'Tras eliminar duplicados exactos: {after_dedup:,}')\n"
    "print(f'Duplicados eliminados: {before - after_dedup:,}')\n"
    "\n"
    "# Una coordenada representativa por prefijo de zip (mediana)\n"
    "geo = (geo_dedup.groupby('geolocation_zip_code_prefix', as_index=False)\n"
    "              .agg(geolocation_lat=('geolocation_lat', 'median'),\n"
    "                   geolocation_lng=('geolocation_lng', 'median'),\n"
    "                   geolocation_state=('geolocation_state', 'last')))\n"
    "print('Zips unicos:', len(geo))"
))

cells.append(md(
    "### 3.2 Products - fix column typos and translate categories\n"
    "\n"
    "The product file has two columns with a typo (`lenght` instead of `length`). We rename them. "
    "We also handle the category field:\n"
    "- 610 products have a null category -> labelled `not_specified`.\n"
    "- 2 category names (`pc_gamer`, `portateis_cozinha...`) are missing from the translation table, so "
    "we add manual translations.\n"
    "- The remaining products use the official Portuguese-to-English translation."
))

cells.append(code(
    "products = products.rename(columns={\n"
    "    'product_name_lenght': 'product_name_length',\n"
    "    'product_description_lenght': 'product_description_length'})\n"
    "\n"
    "# Traducciones manuales para categorias ausentes en la tabla oficial\n"
    "EXTRA_TRANSLATIONS = pd.DataFrame({\n"
    "    'product_category_name': ['pc_gamer', 'portateis_cozinha_e_preparadores_de_alimentos'],\n"
    "    'product_category_name_english': ['pc_gamer', 'portable_kitchen_appliances']})\n"
    "cat_tr = pd.concat([categories_tr, EXTRA_TRANSLATIONS], ignore_index=True)\n"
    "\n"
    "cat_map = dict(zip(cat_tr['product_category_name'], cat_tr['product_category_name_english']))\n"
    "products['category_pt'] = products['product_category_name']\n"
    "products['category'] = products['product_category_name'].map(cat_map).fillna('not_specified')\n"
    "products.loc[products['product_category_name'].isna(), 'category'] = 'not_specified'\n"
    "\n"
    "print('Productos vacios en category:', products['category'].isna().sum())\n"
    "print('Ejemplos de traduccion:')\n"
    "print(products[['product_category_name', 'category']].drop_duplicates().head(6))\n"
    "print('products:', products.shape)"
))

cells.append(md(
    "## 4. Orders - timestamps and delivery metrics\n"
    "\n"
    "We parse every timestamp column and derive two useful delivery measures **only for delivered "
    "orders** (non-delivered orders legitimately have no delivery date):\n"
    "\n"
    "- `delivery_time_days`: days from purchase to customer delivery.\n"
    "- `delivery_delay_days`: days late vs the estimated date (positive = late).\n"
    "- `delivery_status`: `On time` (delay <= 0) or `Late` (delay > 0)."
))

cells.append(code(
    "date_cols = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date',\n"
    "             'order_delivered_customer_date', 'order_estimated_delivery_date']\n"
    "for c in date_cols:\n"
    "    orders[c] = pd.to_datetime(orders[c])\n"
    "\n"
    "orders['year'] = orders['order_purchase_timestamp'].dt.year\n"
    "orders['month'] = orders['order_purchase_timestamp'].dt.month\n"
    "orders['purchase_month'] = orders['order_purchase_timestamp'].dt.to_period('M').astype(str)\n"
    "\n"
    "delivered = orders['order_status'] == 'delivered'\n"
    "\n"
    "orders['delivery_time_days'] = np.nan\n"
    "orders.loc[delivered, 'delivery_time_days'] = (\n"
    "    (orders.loc[delivered, 'order_delivered_customer_date']\n"
    "     - orders.loc[delivered, 'order_purchase_timestamp']).dt.total_seconds() / 86400)\n"
    "\n"
    "orders['delivery_delay_days'] = np.nan\n"
    "orders.loc[delivered, 'delivery_delay_days'] = (\n"
    "    (orders.loc[delivered, 'order_delivered_customer_date']\n"
    "     - orders.loc[delivered, 'order_estimated_delivery_date']).dt.total_seconds() / 86400)\n"
    "\n"
    "orders['delivery_status'] = np.where(orders['delivery_delay_days'] > 0, 'Late', 'On time')\n"
    "orders.loc[~delivered, 'delivery_status'] = np.nan\n"
    "\n"
    "print('orders:', orders.shape)\n"
    "print()\n"
    "print('Distribucion de delivery_status:')\n"
    "print(orders['delivery_status'].value_counts(dropna=False))"
))

cells.append(md(
    "## 5. Aggregate payments and reviews to the order grain\n"
    "\n"
    "`payments` and `reviews` can hold several rows per order (installments, multiple methods, multiple "
    "reviews). We collapse them into **one row per order** so they can be joined into the master frame."
))

cells.append(code(
    "# --- Pagos: agregar por orden ---\n"
    "pay_agg = (payments.groupby('order_id', as_index=False)\n"
    "                   .agg(total_paid=('payment_value', 'sum'),\n"
    "                        n_payments=('order_id', 'count'),\n"
    "                        n_installments_max=('payment_installments', 'max'),\n"
    "                        payment_type_main=('payment_type', lambda x: x.value_counts().index[0])))\n"
    "print('pay_agg:', pay_agg.shape)\n"
    "\n"
    "# --- Resenas: agregar por orden ---\n"
    "reviews['review_creation_date'] = pd.to_datetime(reviews['review_creation_date'])\n"
    "rev_agg = (reviews.groupby('order_id', as_index=False)\n"
    "                   .agg(review_score_mean=('review_score', 'mean'),\n"
    "                        review_score_min=('review_score', 'min'),\n"
    "                        review_score_max=('review_score', 'max'),\n"
    "                        n_reviews=('order_id', 'count'),\n"
    "                        has_comment_title=('review_comment_title', lambda s: s.notna().any()),\n"
    "                        has_comment_message=('review_comment_message', lambda s: s.notna().any())))\n"
    "print('rev_agg:', rev_agg.shape)"
))

cells.append(md(
    "## 6. Items - enrich and aggregate\n"
    "\n"
    "`order_items` has the line-level detail. We enrich each line with the English category and compute "
    "`total_value` (price + freight), then aggregate to the order grain for the master dataset."
))

cells.append(code(
    "# Enriquecer cada item con la categoria y peso del producto\n"
    "items = order_items.copy()\n"
    "items['shipping_limit_date'] = pd.to_datetime(items['shipping_limit_date'])\n"
    "items['total_value'] = items['price'] + items['freight_value']\n"
    "items = items.merge(\n"
    "    products[['product_id', 'category', 'product_weight_g']].rename(columns={'category': 'item_category'}),\n"
    "    on='product_id', how='left')\n"
    "print('items:', items.shape)\n"
    "\n"
    "# Agregados a nivel de orden\n"
    "item_agg = (items.groupby('order_id', as_index=False)\n"
    "                   .agg(n_items=('order_item_id', 'count'),\n"
    "                        n_products=('product_id', 'nunique'),\n"
    "                        n_sellers=('seller_id', 'nunique'),\n"
    "                        product_value=('price', 'sum'),\n"
    "                        freight_value=('freight_value', 'sum'),\n"
    "                        order_value=('total_value', 'sum'),\n"
    "                        n_categories=('item_category', 'nunique')))\n"
    "print('item_agg:', item_agg.shape)"
))

cells.append(md(
    "## 7. Assemble the master order-level dataset\n"
    "\n"
    "We now join everything into `master_orders` at the **order grain**. This becomes the canonical "
    "table used by every downstream notebook (EDA, statistics, BI, ML)."
))

cells.append(code(
    "master = (orders\n"
    "    .merge(customers[['customer_id', 'customer_unique_id', 'customer_state']], on='customer_id', how='left')\n"
    "    .merge(pay_agg, on='order_id', how='left')\n"
    "    .merge(rev_agg, on='order_id', how='left')\n"
    "    .merge(item_agg, on='order_id', how='left'))\n"
    "\n"
    "print('master shape:', master.shape)\n"
    "print()\n"
    "print('Columnas:')\n"
    "print(list(master.columns))"
))

cells.append(md(
    "## 8. Write cleaned datasets\n"
    "\n"
    "Finally we persist every cleaned table as **parquet** under `data/processed/`. Parquet keeps "
    "dtypes, is fast to read, and compresses well. These files are the input for all later notebooks."
))

cells.append(code(
    "outputs = {\n"
    "    'olist_master_orders.parquet': master,\n"
    "    'olist_items.parquet': items,\n"
    "    'olist_catalog.parquet': products,\n"
    "    'olist_geolocation_clean.parquet': geo,\n"
    "    'product_category_name_translation.parquet': cat_tr,\n"
    "}\n"
    "\n"
    "for fname, df in outputs.items():\n"
    "    path = os.path.join(PROC, fname)\n"
    "    df.to_parquet(path)\n"
    "    print(f\"-> {fname}  ({df.shape[0]:,} x {df.shape[1]})\")\n"
    "\n"
    "print('\\nListo: todos los datasets limpios guardados en data/processed/')"
))

cells.append(md(
    "## 9. Takeaways\n"
    "\n"
    "- From 9 messy raw files we produced **5 tidy datasets** in `data/processed/`, with a canonical "
    "**master at the order grain** (99,441 rows) used by all later notebooks.\n"
    "- Explicit decisions were made and documented: zip codes as strings, median point per zip, "
    "`not_specified` category, delivery metrics only for delivered orders, two manual category "
    "translations.\n"
    "- The process is **reproducible**: re-running this notebook (or `src/build_processed.py`) "
    "regenerates the same outputs.\n"
    "\n"
    "Next: **`03_eda_visualizations.ipynb`** will explore the cleaned data and save figures to `images/`."
))

write_nb(os.path.join(os.path.dirname(__file__), '02_cleaning_preprocessing.ipynb'), cells)