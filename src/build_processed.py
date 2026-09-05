"""Construye los datasets limpios de Olist en data/processed.

Pipeline de limpieza y transformacion replicable:
  1. Relee las tablas crudas desde data/raw (idempotente).
  2. Limpia geolocation (dedup + una coordenada por zip), products
     (renombra columnas 'lenght', traduce categorias PT->EN con 2
     traducciones manuales y marca 'not_specified'), orders (fechas,
     anio/mes y metricas de entrega solo para entregados).
  3. Agrega pagos y resenas a grano de orden.
  4. Ensambla el dataset maestro a grano de orden y guarda parquet.

Uso:
    python src/build_processed.py

Esta logica es la misma que reproduce `02_cleaning_preprocessing.ipynb`.
"""
import os
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
PROC = os.path.join(ROOT, "data", "processed")

DATE_ORDER_COLS = [
    "order_purchase_timestamp", "order_approved_at",
    "order_delivered_carrier_date", "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

# Traducciones manuales para categorias ausentes en la tabla de traduccion
EXTRA_TRANSLATIONS = {
    "pc_gamer": "pc_gamer",
    "portateis_cozinha_e_preparadores_de_alimentos": "portable_kitchen_appliances",
}


def load(name, **kw):
    return pd.read_csv(os.path.join(RAW, name), **kw)


def clean_geolocation():
    geo = load("olist_geolocation_dataset.csv", dtype={"geolocation_zip_code_prefix": str})
    geo = geo.drop_duplicates()
    geo_agg = (geo.groupby("geolocation_zip_code_prefix", as_index=False)
                 .agg(geolocation_lat=("geolocation_lat", "median"),
                      geolocation_lng=("geolocation_lng", "median"),
                      geolocation_state=("geolocation_state", "last")))
    return geo_agg


def clean_orders():
    orders = load("olist_orders_dataset.csv")
    for c in DATE_ORDER_COLS:
        orders[c] = pd.to_datetime(orders[c])
    orders["year"] = orders["order_purchase_timestamp"].dt.year
    orders["month"] = orders["order_purchase_timestamp"].dt.month
    orders["purchase_month"] = orders["order_purchase_timestamp"].dt.to_period("M").astype(str)

    delivered = orders["order_status"] == "delivered"
    orders["delivery_time_days"] = np.nan
    orders.loc[delivered, "delivery_time_days"] = (
        (orders.loc[delivered, "order_delivered_customer_date"]
         - orders.loc[delivered, "order_purchase_timestamp"]).dt.total_seconds() / 86400
    )
    orders["delivery_delay_days"] = np.nan
    orders.loc[delivered, "delivery_delay_days"] = (
        (orders.loc[delivered, "order_delivered_customer_date"]
         - orders.loc[delivered, "order_estimated_delivery_date"]).dt.total_seconds() / 86400
    )
    orders["delivery_status"] = np.where(orders["delivery_delay_days"] > 0, "Late", "On time")
    orders.loc[~delivered, "delivery_status"] = np.nan
    return orders


def aggregate_payments():
    pay = load("olist_order_payments_dataset.csv")
    pay_agg = (pay.groupby("order_id", as_index=False)
                 .agg(total_paid=("payment_value", "sum"),
                      n_payments=("order_id", "count"),
                      n_installments_max=("payment_installments", "max"),
                      payment_type_main=("payment_type", lambda x: x.value_counts().index[0])))
    return pay_agg


def aggregate_reviews():
    rev = load("olist_order_reviews_dataset.csv")
    rev["review_creation_date"] = pd.to_datetime(rev["review_creation_date"])
    rev_agg = (rev.groupby("order_id", as_index=False)
                 .agg(review_score_mean=("review_score", "mean"),
                      review_score_min=("review_score", "min"),
                      review_score_max=("review_score", "max"),
                      n_reviews=("order_id", "count"),
                      has_comment_title=("review_comment_title", lambda s: s.notna().any()),
                      has_comment_message=("review_comment_message", lambda s: s.notna().any())))
    return rev_agg


def clean_products():
    products = load("olist_products_dataset.csv")
    products = products.rename(columns={
        "product_name_lenght": "product_name_length",
        "product_description_lenght": "product_description_length"})

    cat_tr = load("product_category_name_translation.csv")
    extra = pd.DataFrame(
        list(EXTRA_TRANSLATIONS.items()),
        columns=["product_category_name", "product_category_name_english"])
    cat_tr = pd.concat([cat_tr, extra], ignore_index=True)

    cat_map = dict(zip(cat_tr["product_category_name"], cat_tr["product_category_name_english"]))
    products["category_pt"] = products["product_category_name"]
    products["category"] = products["product_category_name"].map(cat_map).fillna("not_specified")
    products.loc[products["product_category_name"].isna(), "category"] = "not_specified"
    return products, cat_tr


def enrich_items(products):
    oi = load("olist_order_items_dataset.csv")
    oi["shipping_limit_date"] = pd.to_datetime(oi["shipping_limit_date"])
    oi["total_value"] = oi["price"] + oi["freight_value"]
    oi = oi.merge(
        products[["product_id", "category", "product_weight_g"]].rename(columns={"category": "item_category"}),
        on="product_id", how="left")
    return oi


def aggregate_items(oi):
    item_agg = (oi.groupby("order_id", as_index=False)
                  .agg(n_items=("order_item_id", "count"),
                       n_products=("product_id", "nunique"),
                       n_sellers=("seller_id", "nunique"),
                       product_value=("price", "sum"),
                       freight_value=("freight_value", "sum"),
                       order_value=("total_value", "sum"),
                       n_categories=("item_category", "nunique")))
    return item_agg


def assemble_master(orders, oi):
    customers = load("olist_customers_dataset.csv", dtype={"customer_zip_code_prefix": str})
    pay_agg = aggregate_payments()
    rev_agg = aggregate_reviews()
    item_agg = aggregate_items(oi)
    master = (orders
        .merge(customers[["customer_id", "customer_unique_id", "customer_state"]],
               on="customer_id", how="left")
        .merge(pay_agg, on="order_id", how="left")
        .merge(rev_agg, on="order_id", how="left")
        .merge(item_agg, on="order_id", how="left"))
    return master


def main():
    os.makedirs(PROC, exist_ok=True)
    print("Construyendo datasets limpios...")

    geo = clean_geolocation()
    orders = clean_orders()
    products, cat_tr = clean_products()
    oi = enrich_items(products)
    master = assemble_master(orders, oi)

    outputs = {
        "olist_master_orders.parquet": master,
        "olist_items.parquet": oi,
        "olist_catalog.parquet": products,
        "olist_geolocation_clean.parquet": geo,
        "product_category_name_translation.parquet": cat_tr,
    }
    for fname, df in outputs.items():
        path = os.path.join(PROC, fname)
        df.to_parquet(path)
        print(f"  -> {fname}  ({df.shape[0]:,} x {df.shape[1]})")

    print("\nListo. Todos los archivos guardados en data/processed/")


if __name__ == "__main__":
    main()