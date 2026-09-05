"""Genera notebooks/sql_python_demo.ipynb (complementario: SQL + pandas)"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _nbgen import md, code, write_nb

cells = []

cells.append(md(
    "# Olist E-Commerce - SQL + pandas interoperability demo\n"
    "\n"
    "**Author:** Diego Ospina\n"
    "\n"
    "> A short companion notebook showing SQL as a complementary tool inside a Python data workflow. "
    "We load the raw CSVs into an **in-memory SQLite** database, run real SQL analysis queries "
    "(equivalent to `sql/queries_analysis.sql`), and pull the results back into **pandas** for "
    "charting. This demonstrates the ETL + SQL + DataFrame blend that is common in analytics.\n"
    "\n"
    "> The `.sql` files in `sql/` define the schema and the full query set (PostgreSQL dialect); here we "
    "use SQLite syntax so the notebook runs with zero external dependencies."
))

cells.append(md("## 1. Create an in-memory SQLite database and load the raw CSVs"))
cells.append(code(
    "import pandas as pd\n"
    "import sqlite3\n"
    "import os\n"
    "\n"
    "RAW = os.path.join('..', 'data', 'raw')\n"
    "\n"
    "con = sqlite3.connect(':memory:')   # base de datos en memoria\n"
    "cur = con.cursor()\n"
    "\n"
    "# Cargar fixtures como tablas SQLite\n"
    "orders  = pd.read_csv(os.path.join(RAW, 'olist_orders_dataset.csv'))\n"
    "items   = pd.read_csv(os.path.join(RAW, 'olist_order_items_dataset.csv'))\n"
    "products= pd.read_csv(os.path.join(RAW, 'olist_products_dataset.csv'))\n"
    "customers=pd.read_csv(os.path.join(RAW, 'olist_customers_dataset.csv'))\n"
    "payments= pd.read_csv(os.path.join(RAW, 'olist_order_payments_dataset.csv'))\n"
    "reviews = pd.read_csv(os.path.join(RAW, 'olist_order_reviews_dataset.csv'))\n"
    "trans   = pd.read_csv(os.path.join(RAW, 'product_category_name_translation.csv'))\n"
    "\n"
    "orders.to_sql('orders', con, if_exists='replace', index=False)\n"
    "items.to_sql('order_items', con, if_exists='replace', index=False)\n"
    "products.to_sql('products', con, if_exists='replace', index=False)\n"
    "customers.to_sql('customers', con, if_exists='replace', index=False)\n"
    "payments.to_sql('order_payments', con, if_exists='replace', index=False)\n"
    "reviews.to_sql('order_reviews', con, if_exists='replace', index=False)\n"
    "trans.to_sql('category_translation', con, if_exists='replace', index=False)\n"
    "print('tabular loaded:', len(orders), 'orders,', len(items), 'items')"
))

cells.append(md("## 2. SQL query: monthly sales of delivered orders"))
cells.append(code(
    "q = \"\"\"\n"
    "SELECT strftime('%Y-%m', o.order_purchase_timestamp) AS purchase_month,\n"
    "       ROUND(SUM(oi.price), 2)                          AS sales_brl\n"
    "FROM orders o\n"
    "JOIN order_items oi ON oi.order_id = o.order_id\n"
    "WHERE o.order_status = 'delivered'\n"
    "GROUP BY 1\n"
    "ORDER BY 1\n"
    "\"\"\"\n"
    "monthly = pd.read_sql_query(q, con)\n"
    "print(monthly.head().to_string(index=False))\n"
    "print('...')\n"
    "print('months:', len(monthly))"
))

cells.append(md("## 3. SQL query: on-time vs late delivery (delivered orders)"))
cells.append(code(
    "q = \"\"\"\n"
    "SELECT CASE\n"
    "          WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date THEN 'On time'\n"
    "          ELSE 'Late' END AS delivery_status,\n"
    "       COUNT(*) AS orders\n"
    "FROM orders o\n"
    "WHERE o.order_status = 'delivered'\n"
    "  AND o.order_delivered_customer_date IS NOT NULL\n"
    "GROUP BY 1\n"
    "\"\"\"\n"
    "deliv = pd.read_sql_query(q, con)\n"
    "deliv['pct'] = (deliv['orders'] / deliv['orders'].sum() * 100).round(2)\n"
    "print(deliv.to_string(index=False))"
))

cells.append(md("## 4. SQL query: top categories by sales (with translation)"))
cells.append(code(
    "q = \"\"\"\n"
    "SELECT COALESCE(t.product_category_name_english, 'not_specified') AS category_en,\n"
    "       ROUND(SUM(oi.price), 2) AS sales_brl\n"
    "FROM order_items oi\n"
    "JOIN products p  ON p.product_id = oi.product_id\n"
    "JOIN orders o    ON o.order_id = oi.order_id\n"
    "LEFT JOIN category_translation t ON t.product_category_name = p.product_category_name\n"
    "WHERE o.order_status = 'delivered'\n"
    "GROUP BY 1\n"
    "ORDER BY sales_brl DESC\n"
    "LIMIT 8\n"
    "\"\"\"\n"
    "top_cat = pd.read_sql_query(q, con)\n"
    "print(top_cat.to_string(index=False))"
))

cells.append(md("## 5. SQL query: average review score by punctuality"))
cells.append(code(
    "q = \"\"\"\n"
    "SELECT CASE\n"
    "          WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date THEN 'On time'\n"
    "          ELSE 'Late' END AS delivery_status,\n"
    "       ROUND(AVG(r.review_score), 3) AS avg_review,\n"
    "       COUNT(*)                     AS n_reviews\n"
    "FROM orders o\n"
    "JOIN order_reviews r ON r.order_id = o.order_id\n"
    "WHERE o.order_status = 'delivered'\n"
    "  AND o.order_delivered_customer_date IS NOT NULL\n"
    "GROUP BY 1\n"
    "\"\"\"\n"
    "sc = pd.read_sql_query(q, con)\n"
    "print(sc.to_string(index=False))\n"
    "con.close()"
))

cells.append(md("## Takeaways\n"
    "\n"
    "- The exact same analytics can be expressed in SQL (`sql/queries_analysis.sql`) and fed back into "
    "pandas via `pd.read_sql_query` for charting.\n"
    "- This pattern (SQL for data querying + pandas for transformation/visualisation) matches a "
    "best-practice analytics workflow and is fully reproducible without a server.\n"
    "- Results agree with the pandas-only notebooks (e.g. ~92% on-time share, top categories dominated "
    "by health/beauty, on-time reviews higher than late)."
))

write_nb(os.path.join(os.path.dirname(__file__), 'sql_python_demo.ipynb'), cells)