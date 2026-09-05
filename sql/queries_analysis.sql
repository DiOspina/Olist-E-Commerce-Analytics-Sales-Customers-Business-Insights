-- =============================================================================
-- Olist E-Commerce - Analysis queries (PostgreSQL dialect)
--
-- Consultas de analisis que replican los hallazgos de los notebooks usando SQL,
-- como herramienta complementaria (ETL/analitico). Asumen el esquema de
-- schema.sql cargado con los datos crudos.
-- =============================================================================

-- ----------------------------------------------------------------------------
-- 1) Pedidos y estado
-- ----------------------------------------------------------------------------
SELECT order_status, COUNT(*) AS orders
FROM orders
GROUP BY order_status
ORDER BY orders DESC;

-- ----------------------------------------------------------------------------
-- 2) Ventas mensuales (product value) de pedidos entregados
-- ----------------------------------------------------------------------------
SELECT
    TO_CHAR(o.order_purchase_timestamp, 'YYYY-MM') AS purchase_month,
    ROUND(SUM(oi.price), 2)                        AS sales_brl
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY 1
ORDER BY 1;

-- ----------------------------------------------------------------------------
-- 3) Top 10 categorias por ventas (product value)
-- ----------------------------------------------------------------------------
SELECT
    COALESCE(t.product_category_name_english, 'not_specified') AS category_en,
    ROUND(SUM(oi.price), 2)                                     AS sales_brl
FROM order_items oi
JOIN products p         ON p.product_id = oi.product_id
JOIN orders o           ON o.order_id = oi.order_id
LEFT JOIN product_category_name_translation t
       ON t.product_category_name = p.product_category_name
WHERE o.order_status = 'delivered'
GROUP BY 1
ORDER BY sales_brl DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- 4) Puntualidad de entrega (% a tiempo vs tarde) para pedidos entregados
-- ----------------------------------------------------------------------------
SELECT
    CASE
        WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date THEN 'On time'
        ELSE 'Late'
    END AS delivery_status,
    COUNT(*)                                              AS orders,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2)     AS pct
FROM orders o
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
GROUP BY 1;

-- ----------------------------------------------------------------------------
-- 5) Valor medio por pedido (AOV) y pedidos por cliente
-- ----------------------------------------------------------------------------
WITH order_value AS (
    SELECT o.order_id,
           o.customer_id,
           SUM(oi.price + oi.freight_value) AS value
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY o.order_id, o.customer_id
)
SELECT
    ROUND(AVG(value), 2)                    AS avg_order_value,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT customer_id), 3) AS orders_per_customer
FROM order_value;

-- ----------------------------------------------------------------------------
-- 6) Pedidos por estado del cliente (top 10)
-- ----------------------------------------------------------------------------
SELECT c.customer_state AS state, COUNT(*) AS orders
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
GROUP BY 1
ORDER BY orders DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- 7) Metodos de pago
-- ----------------------------------------------------------------------------
SELECT payment_type, COUNT(*) AS rows_count
FROM order_payments
GROUP BY 1
ORDER BY rows_count DESC;

-- ----------------------------------------------------------------------------
-- 8) Media de review score por estado de entrega (pedidos entregados)
-- ----------------------------------------------------------------------------
SELECT
    CASE
        WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date THEN 'On time'
        ELSE 'Late'
    END AS delivery_status,
    ROUND(AVG(r.review_score), 3) AS avg_review
FROM orders o
JOIN order_reviews r ON r.order_id = o.order_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
GROUP BY 1;

-- ----------------------------------------------------------------------------
-- 9) Cohortes: primer mes de compra por cliente y retencion simple
--    (porcentaje de clientes con mas de un pedido)
-- ----------------------------------------------------------------------------
WITH first_order AS (
    SELECT
        customer_id,
        MIN(DATE_TRUNC('month', order_purchase_timestamp)) AS first_month
    FROM orders
    GROUP BY customer_id
)
SELECT
    first_month::date,
    COUNT(*)                                           AS customers,
    ROUND(COUNT(*) FILTER (WHERE repeat_orders >= 2) * 100.0 / COUNT(*), 2) AS pct_repeat
FROM (
    SELECT fo.customer_id, fo.first_month, COUNT(o.order_id) AS repeat_orders
    FROM first_order fo
    JOIN orders o ON o.customer_id = fo.customer_id
    GROUP BY fo.customer_id, fo.first_month
) t
GROUP BY 1
ORDER BY 1;