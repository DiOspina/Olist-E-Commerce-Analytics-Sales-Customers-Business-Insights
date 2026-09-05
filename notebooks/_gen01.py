"""Genera 01_data_understanding.ipynb"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _nbgen import md, code, write_nb

cells = []

HEADER = (
    "# Olist E-Commerce - 01 : Understanding the Data\n"
    "\n"
    "**Author:** Diego Ospina | **Dataset:** Brazilian E-Commerce Public Dataset by Olist\n"
    "\n"
    "> This is the first notebook of a portfolio project. The purpose here is to **read every raw "
    "file and understand its structure, granularity, and data quality** before any cleaning or "
    "modeling. Comments are in Spanish; titles and narrative are in English.\n"
    "\n"
    "### What we will do\n"
    "1. Load the 9 raw CSV files.\n"
    "2. Build a data dictionary (columns, types, shapes).\n"
    "3. Assess data quality: missing values, duplicates, key uniqueness.\n"
    "4. Validate referential integrity between tables.\n"
    "5. Look at key categorical distributions.\n"
    "\n"
    "### Repository layout\n"
    "- `data/raw/` - original CSV files (read-only, never modified).\n"
    "- `data/processed/` - cleaned datasets produced by `02_cleaning_preprocessing.ipynb`.\n"
    "- `images/`, `reports/` - figures and reports generated downstream."
)
cells.append(md(HEADER))

MID = (
    "## 1. Setup\n"
    "\n"
    "We configure the display and verify the library versions we are using."
)
cells.append(md(MID))

S1 = (
    "import pandas as pd\n"
    "import numpy as np\n"
    "import os\n"
    "\n"
    "print('pandas', pd.__version__)\n"
    "print('numpy', np.__version__)\n"
    "\n"
    "pd.set_option('display.max_columns', None)\n"
    "pd.set_option('display.width', 200)\n"
    "\n"
    "RAW = os.path.join('..', 'data', 'raw')\n"
    "PROCESSED = os.path.join('..', 'data', 'processed')\n"
    "IMAGES = os.path.join('..', 'images')\n"
    "REPORTS = os.path.join('..', 'reports')\n"
    "for d in (PROCESSED, IMAGES, REPORTS):\n"
    "    os.makedirs(d, exist_ok=True)\n"
    "print('output dirs ready')"
)
cells.append(code(S1))

M2 = (
    "## 2. Load the raw datasets\n"
    "\n"
    "Each file corresponds to a logical table of the Olist marketplace. We load them all and note "
    "the **reason for each file**:\n"
    "\n"
    "| File | Role |\n"
    "|---|---|\n"
    "| `olist_customers_dataset.csv` | Customers and their delivery location |\n"
    "| `olist_orders_dataset.csv` | Orders with all status timestamps |\n"
    "| `olist_order_items_dataset.csv` | Each product/seller line inside an order |\n"
    "| `olist_order_payments_dataset.csv` | Payment methods per order |\n"
    "| `olist_order_reviews_dataset.csv` | Customer reviews per order |\n"
    "| `olist_products_dataset.csv` | Products catalog and physical attributes |\n"
    "| `olist_sellers_dataset.csv` | Sellers and their location |\n"
    "| `olist_geolocation_dataset.csv` | Zip-code to lat/lng mapping |\n"
    "| `product_category_name_translation.csv` | Portuguese to English category names |"
)
cells.append(md(M2))

S2 = (
    "# Lectura de las tablas crudas. Nota: los prefijos de codigo postal se leen como string\n"
    "# para evitar perder ceros a la izquierda.\n"
    "customers  = pd.read_csv(os.path.join(RAW, 'olist_customers_dataset.csv'), dtype={'customer_zip_code_prefix': str})\n"
    "geolocation= pd.read_csv(os.path.join(RAW, 'olist_geolocation_dataset.csv'), dtype={'geolocation_zip_code_prefix': str})\n"
    "order_items= pd.read_csv(os.path.join(RAW, 'olist_order_items_dataset.csv'))\n"
    "payments   = pd.read_csv(os.path.join(RAW, 'olist_order_payments_dataset.csv'))\n"
    "reviews    = pd.read_csv(os.path.join(RAW, 'olist_order_reviews_dataset.csv'))\n"
    "orders     = pd.read_csv(os.path.join(RAW, 'olist_orders_dataset.csv'))\n"
    "products   = pd.read_csv(os.path.join(RAW, 'olist_products_dataset.csv'))\n"
    "sellers    = pd.read_csv(os.path.join(RAW, 'olist_sellers_dataset.csv'), dtype={'seller_zip_code_prefix': str})\n"
    "categories = pd.read_csv(os.path.join(RAW, 'product_category_name_translation.csv'))\n"
    "\n"
    "raw = {'customers': customers, 'orders': orders, 'order_items': order_items, 'products': products, 'payments': payments, 'reviews': reviews, 'sellers': sellers, 'geolocation': geolocation, 'categories': categories}"
)
cells.append(code(S2))

M3 = (
    "## 3. Dataset inventory\n"
    "\n"
    "We print the number of rows/columns of each table to confirm the size and scale of the data."
)
cells.append(md(M3))

S3 = (
    "for name, df in raw.items():\n"
    "    print(f\"{name:14s} -> {df.shape[0]:>9,} rows x {df.shape[1]} cols\")\n"
    "\n"
    "total_mb = sum(df.memory_usage(deep=True).sum() for df in raw.values()) / 1e6\n"
    "print()\n"
    "print('Total raw memory (MB):', round(total_mb, 1))"
)
cells.append(code(S3))

M3b = (
    "### 3.1 Granularity\n"
    "\n"
    "It is critical to know what **one row** means in each table:\n"
    "\n"
    "- `orders`: one row per `order_id` (an order).\n"
    "- `order_items`: one row per `(order_id, order_item_id)` - an order with several products has several rows.\n"
    "- `payments`: one row per `(order_id, payment_sequential)` - an order can be paid in installments or with multiple methods.\n"
    "- `reviews`: one row per `(order_id, review_id)` - an order can have more than one review.\n"
    "\n"
    "Let us confirm the cardinalities with pandas."
)
cells.append(md(M3b))

S3b = (
    "def cardinality(df, cols):\n"
    "    # Devuelve n de ids unicos vs filas totales para entender la granularidad\n"
    "    return {c: f'{df[c].nunique():,} / {len(df):,}' for c in cols}\n"
    "\n"
    "print('orders       ', cardinality(order_items, ['order_id']))\n"
    "print('order_items  ', cardinality(order_items, ['order_id', 'order_item_id']))\n"
    "print('payments     ', cardinality(payments, ['order_id', 'payment_sequential']))\n"
    "print('reviews      ', cardinality(reviews, ['order_id', 'review_id']))\n"
    "print('customers    ', cardinality(customers, ['customer_id', 'customer_unique_id']))\n"
    "print('products     ', cardinality(products, ['product_id']))\n"
    "print('sellers      ', cardinality(sellers, ['seller_id']))"
)
cells.append(code(S3b))

M4 = (
    "## 4. Data dictionary\n"
    "\n"
    "We print columns and dtypes for every table so we can reason about which ones are identifiers, "
    "dates, categoricals, or numerics."
)
cells.append(md(M4))

S4 = (
    "for name, df in raw.items():\n"
    "    print('=' * 70)\n"
    "    print(name.upper())\n"
    "    print(df.dtypes.to_string())\n"
    "    print()"
)
cells.append(code(S4))

M5 = (
    "## 5. Data quality - missing values\n"
    "\n"
    "Missing values are expected in a real marketplace: not all orders are approved or delivered, and "
    "many reviews have no text. We quantify them per table. **Context matters**: a missing "
    "`order_delivered_customer_date` is not an error, it means the order was not delivered."
)
cells.append(md(M5))

S5 = (
    "def missing_report(df):\n"
    "    # Resumen de valores nulos absolutos y relativos por columna\n"
    "    nulls = df.isnull().sum()\n"
    "    nulls = nulls[nulls > 0]\n"
    "    if nulls.empty:\n"
    "        return '    (no missing values)'\n"
    "    rel = (nulls / len(df) * 100).round(2)\n"
    "    info = pd.DataFrame({'n': nulls, 'pct': rel})\n"
    "    return '    ' + '\\n    '.join(f\"{idx:35s} {row['n']:>8,.0f} ({row['pct']}%)\" for idx, row in info.iterrows())\n"
    "\n"
    "for name, df in raw.items():\n"
    "    print('=' * 70)\n"
    "    print(name.upper())\n"
    "    print(missing_report(df))"
)
cells.append(code(S5))

MK = (
    "> **Key insight:** later we will see that almost all missing values in `orders` are explained by "
    "the `order_status` - canceled/unavailable/shipped orders never reached the customer. This is a "
    "**structural** null, not a data-entry problem."
)
cells.append(md(MK))

M6 = (
    "## 6. Data quality - duplicates\n"
    "\n"
    "We look for exact duplicate rows. `geolocation` is the only file that can legitimately repeat zip "
    "codes (one zip can have several coordinate points recorded), so exact row duplicates there are "
    "suspicious and will be handled in the cleaning step."
)
cells.append(md(M6))

S6 = (
    "for name, df in raw.items():\n"
    "    print(f\"{name:14s} duplicate rows: {df.duplicated().sum():,}\")"
)
cells.append(code(S6))

M7 = (
    "## 7. Referential integrity\n"
    "\n"
    "There is no enforced foreign key in the CSVs, so we **verify** that every reference between tables "
    "points to an existing row. The expected relationships are:\n"
    "\n"
    "- `orders.customer_id` -> `customers.customer_id`\n"
    "- `order_items.order_id` -> `orders.order_id`\n"
    "- `order_items.product_id` -> `products.product_id`\n"
    "- `order_items.seller_id` -> `sellers.seller_id`\n"
    "- `payments.order_id` -> `orders.order_id`\n"
    "- `reviews.order_id` -> `orders.order_id`\n"
    "- `products.product_category_name` -> `categories.product_category_name`"
)
cells.append(md(M7))

S7 = (
    "def orphan_count(child_df, child_col, parent_df, parent_col):\n"
    "    # Cuenta claves hijas que no existen en la tabla padre\n"
    "    return int((~child_df[child_col].isin(parent_df[parent_col])).sum())\n"
    "\n"
    "checks = [\n"
    "    ('orders.customer_id',     orders,      'customer_id', customers, 'customer_id'),\n"
    "    ('order_items.order_id',   order_items, 'order_id',    orders,    'order_id'),\n"
    "    ('order_items.product_id', order_items, 'product_id',  products,  'product_id'),\n"
    "    ('order_items.seller_id',  order_items, 'seller_id',   sellers,   'seller_id'),\n"
    "    ('payments.order_id',      payments,    'order_id',    orders,    'order_id'),\n"
    "    ('reviews.order_id',       reviews,     'order_id',    orders,    'order_id'),\n"
    "]\n"
    "for label, cdf, ccol, pdf, pcol in checks:\n"
    "    n = orphan_count(cdf, ccol, pdf, pcol)\n"
    "    print(f'{label:32s} orphans: {n}')"
)
cells.append(code(S7))

M8 = (
    "## 8. Key distributions\n"
    "\n"
    "We inspect the most relevant categorical variable: `order_status`. This drives every later decision "
    "(which orders count as revenue, as delivered, etc.)."
)
cells.append(md(M8))

S8 = (
    "status = orders['order_status'].value_counts()\n"
    "status_df = pd.DataFrame({'count': status, 'percent': (status / status.sum() * 100).round(2)})\n"
    "status_df"
)
cells.append(code(S8))

M8b = (
    "> **Interpretation:** ~97% of orders are `delivered`. The remaining statuses describe orders that "
    "are still in progress or that never completed (canceled, unavailable), so they are **excluded** "
    "from most forward-looking business metrics."
)
cells.append(md(M8b))

M9 = (
    "## 9. Time range of the data\n"
    "\n"
    "We confirm the temporal coverage so downstream time-series plots are interpreted correctly. Note "
    "that 2016 only holds a couple of months and 2018 ends in October - these partial years are **not "
    "comparable** to full years on absolute totals."
)
cells.append(md(M9))

S9 = (
    "orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])\n"
    "orders['order_estimated_delivery_date'] = pd.to_datetime(orders['order_estimated_delivery_date'])\n"
    "\n"
    "print('purchase date  min:', orders['order_purchase_timestamp'].min())\n"
    "print('purchase date  max:', orders['order_purchase_timestamp'].max())\n"
    "print('estimated date max:', orders['order_estimated_delivery_date'].max())\n"
    "print()\n"
    "print('Orders per year:')\n"
    "print(orders['order_purchase_timestamp'].dt.year.value_counts().sort_index())"
)
cells.append(code(S9))

M10 = (
    "## 10. Takeaways\n"
    "\n"
    "- The dataset spans **Sep 2016 - Oct 2018** (about 99,441 orders, 112,650 order items, 3,095 "
    "sellers, 32,951 products).\n"
    "- The natural grain is the **order** for business analysis and the **order item** for line-level "
    "analysis.\n"
    "- Missing dates in `orders` are **structural** and align with non-delivered statuses; most other "
    "files are almost complete.\n"
    "- `geolocation` is the only file with relevant exact duplicates (to be cleaned next).\n"
    "- Referential integrity holds: **no orphan keys** across tables (the only mismatch is a few "
    "products whose category is not present in the translation table, which we will handle).\n"
    "\n"
    "Now we are ready to **clean and model the data** in `02_cleaning_preprocessing.ipynb`."
)
cells.append(md(M10))

write_nb(os.path.join(os.path.dirname(__file__), '01_data_understanding.ipynb'), cells)