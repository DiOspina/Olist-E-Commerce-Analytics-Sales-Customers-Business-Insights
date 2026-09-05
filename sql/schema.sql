-- =============================================================================
-- Olist E-Commerce - SQL schema (PostgreSQL dialect)
-- 
-- Definicion del esquema relacional que reproduzco en PostgreSQL a partir de
-- las tablas crudas. Este script documenta la estructura de datos y es la base
-- sobre la que corren las consultas de analisis (queries_analysis.sql).
--
-- Nota: los prefijos de codigo postal se modelan como VARCHAR para no perder
-- ceros a la izquierda. Las fechas se guardan en TIMESTAMP.
-- =============================================================================

CREATE TABLE customers (
    customer_id            VARCHAR(64) PRIMARY KEY,
    customer_unique_id     VARCHAR(64) NOT NULL,
    customer_zip_code_prefix VARCHAR(8) NOT NULL,
    customer_city          VARCHAR(64),
    customer_state         CHAR(2)
);

CREATE TABLE sellers (
    seller_id              VARCHAR(64) PRIMARY KEY,
    seller_zip_code_prefix VARCHAR(8) NOT NULL,
    seller_city            VARCHAR(64),
    seller_state           CHAR(2)
);

CREATE TABLE orders (
    order_id                        VARCHAR(64) PRIMARY KEY,
    customer_id                     VARCHAR(64) NOT NULL REFERENCES customers(customer_id),
    order_status                    VARCHAR(16) NOT NULL,
    order_purchase_timestamp        TIMESTAMP,
    order_approved_at               TIMESTAMP,
    order_delivered_carrier_date    TIMESTAMP,
    order_delivered_customer_date   TIMESTAMP,
    order_estimated_delivery_date   TIMESTAMP
);

CREATE TABLE products (
    product_id                  VARCHAR(64) PRIMARY KEY,
    product_category_name       VARCHAR(128),
    product_name_length         INTEGER,
    product_description_length  INTEGER,
    product_photos_qty          INTEGER,
    product_weight_g            NUMERIC,
    product_length_cm           NUMERIC,
    product_height_cm           NUMERIC,
    product_width_cm            NUMERIC
);

CREATE TABLE order_items (
    order_id            VARCHAR(64) REFERENCES orders(order_id),
    order_item_id       SMALLINT,
    product_id          VARCHAR(64) REFERENCES products(product_id),
    seller_id           VARCHAR(64) REFERENCES sellers(seller_id),
    shipping_limit_date TIMESTAMP,
    price               NUMERIC(12,2) NOT NULL,
    freight_value       NUMERIC(12,2) NOT NULL,
    PRIMARY KEY (order_id, order_item_id)
);

CREATE TABLE order_payments (
    order_id            VARCHAR(64) REFERENCES orders(order_id),
    payment_sequential  SMALLINT,
    payment_type        VARCHAR(16),
    payment_installments SMALLINT,
    payment_value       NUMERIC(12,2),
    PRIMARY KEY (order_id, payment_sequential)
);

CREATE TABLE order_reviews (
    review_id                 VARCHAR(64) PRIMARY KEY,
    order_id                  VARCHAR(64) REFERENCES orders(order_id),
    review_score              SMALLINT NOT NULL CHECK (review_score BETWEEN 1 AND 5),
    review_comment_title      TEXT,
    review_comment_message    TEXT,
    review_creation_date      TIMESTAMP,
    review_answer_timestamp   TIMESTAMP
);

CREATE TABLE product_category_name_translation (
    product_category_name        VARCHAR(128) PRIMARY KEY,
    product_category_name_english VARCHAR(128)
);

CREATE TABLE geolocation (
    geolocation_zip_code_prefix VARCHAR(8),
    geolocation_lat             NUMERIC(10,7),
    geolocation_lng             NUMERIC(10,7),
    geolocation_city            VARCHAR(64),
    geolocation_state           CHAR(2)
);

-- Indices de apoyo para las consultas de analisis
CREATE INDEX idx_orders_customer    ON orders(customer_id);
CREATE INDEX idx_orders_status      ON orders(order_status);
CREATE INDEX idx_orders_date        ON orders(order_purchase_timestamp);
CREATE INDEX idx_items_order        ON order_items(order_id);
CREATE INDEX idx_items_product      ON order_items(product_id);
CREATE INDEX idx_reviews_order      ON order_reviews(order_id);