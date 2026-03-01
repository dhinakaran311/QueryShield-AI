-- Phase 1 Verification Queries
SELECT 'TABLES:' AS check_type, table_name AS value
FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;

SELECT 'INDEXES:' AS check_type, indexname AS value
FROM pg_indexes WHERE schemaname='public' ORDER BY indexname;

SELECT 'META_ROWS' AS check_type, CAST(COUNT(*) AS TEXT) AS value FROM uploaded_tables;
SELECT 'CUSTOMERS' AS check_type, CAST(COUNT(*) AS TEXT) AS value FROM customers;
SELECT 'PRODUCTS'  AS check_type, CAST(COUNT(*) AS TEXT) AS value FROM products;
SELECT 'ORDERS'    AS check_type, CAST(COUNT(*) AS TEXT) AS value FROM orders;
SELECT 'ORDER_ITEMS' AS check_type, CAST(COUNT(*) AS TEXT) AS value FROM order_items;
