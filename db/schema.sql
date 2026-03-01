-- =============================================================
-- QueryShield AI — Schema DDL
-- Database: queryshield_db
-- =============================================================

-- ─────────────────────────────────────────
-- METADATA TABLE (tracks uploaded CSV tables)
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS uploaded_tables (
    id          SERIAL PRIMARY KEY,
    table_name  TEXT          NOT NULL,
    uploaded_by TEXT          NOT NULL DEFAULT 'system',
    upload_time TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────
-- DEMO SCHEMA
-- ─────────────────────────────────────────

-- Customers
CREATE TABLE IF NOT EXISTS customers (
    id         SERIAL PRIMARY KEY,
    name       TEXT        NOT NULL,
    email      TEXT        UNIQUE,
    phone      TEXT,
    city       TEXT,
    country    TEXT        DEFAULT 'India',
    created_at TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);

-- Products
CREATE TABLE IF NOT EXISTS products (
    id          SERIAL PRIMARY KEY,
    name        TEXT           NOT NULL,
    category    TEXT,
    price       NUMERIC(10,2)  NOT NULL,
    stock_qty   INTEGER        DEFAULT 0,
    created_at  TIMESTAMP      DEFAULT CURRENT_TIMESTAMP
);

-- Orders
CREATE TABLE IF NOT EXISTS orders (
    id          SERIAL PRIMARY KEY,
    customer_id INTEGER        NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    order_date  DATE           NOT NULL DEFAULT CURRENT_DATE,
    status      TEXT           NOT NULL DEFAULT 'pending'
                               CHECK (status IN ('pending','processing','shipped','delivered','cancelled')),
    total_amount NUMERIC(12,2) DEFAULT 0.00,
    created_at  TIMESTAMP      DEFAULT CURRENT_TIMESTAMP
);

-- Order Items
CREATE TABLE IF NOT EXISTS order_items (
    id          SERIAL PRIMARY KEY,
    order_id    INTEGER        NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id  INTEGER        NOT NULL REFERENCES products(id),
    quantity    INTEGER        NOT NULL CHECK (quantity > 0),
    unit_price  NUMERIC(10,2)  NOT NULL,
    subtotal    NUMERIC(12,2)  GENERATED ALWAYS AS (quantity * unit_price) STORED
);

-- ─────────────────────────────────────────
-- INDEXES ON FOREIGN KEYS
-- ─────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_orders_customer_id      ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id    ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id  ON order_items(product_id);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_orders_status           ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_order_date       ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_products_category       ON products(category);
CREATE INDEX IF NOT EXISTS idx_customers_country       ON customers(country);
