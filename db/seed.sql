-- =============================================================
-- QueryShield AI — Demo Seed Data
-- =============================================================

-- ─────────────────────────────────────────
-- CUSTOMERS
-- ─────────────────────────────────────────
INSERT INTO customers (name, email, phone, city, country) VALUES
  ('Arjun Sharma',     'arjun.sharma@email.com',    '9876543210', 'Mumbai',    'India'),
  ('Priya Nair',       'priya.nair@email.com',      '9876543211', 'Chennai',   'India'),
  ('Rahul Verma',      'rahul.verma@email.com',     '9876543212', 'Delhi',     'India'),
  ('Sneha Reddy',      'sneha.reddy@email.com',     '9876543213', 'Hyderabad', 'India'),
  ('Kiran Patel',      'kiran.patel@email.com',     '9876543214', 'Ahmedabad', 'India'),
  ('Meera Iyer',       'meera.iyer@email.com',      '9876543215', 'Bangalore', 'India'),
  ('Vikram Singh',     'vikram.singh@email.com',    '9876543216', 'Pune',      'India'),
  ('Ananya Das',       'ananya.das@email.com',      '9876543217', 'Kolkata',   'India'),
  ('Rohan Mehta',      'rohan.mehta@email.com',     '9876543218', 'Jaipur',    'India'),
  ('Lakshmi Pillai',   'lakshmi.pillai@email.com',  '9876543219', 'Kochi',     'India')
ON CONFLICT DO NOTHING;

-- ─────────────────────────────────────────
-- PRODUCTS
-- ─────────────────────────────────────────
INSERT INTO products (name, category, price, stock_qty) VALUES
  ('Laptop Pro 15',       'Electronics',   75000.00, 50),
  ('Wireless Mouse',      'Electronics',    1200.00, 200),
  ('USB-C Hub 7-Port',    'Electronics',    2500.00, 150),
  ('Mechanical Keyboard', 'Electronics',    4500.00, 80),
  ('27" Monitor 4K',      'Electronics',   28000.00, 30),
  ('Office Chair',        'Furniture',     12000.00, 25),
  ('Standing Desk',       'Furniture',     22000.00, 15),
  ('Python Programming',  'Books',           499.00, 500),
  ('Data Science Guide',  'Books',           599.00, 300),
  ('Noise-Cancel Headset','Electronics',    8500.00, 60),
  ('Webcam HD 1080p',     'Electronics',    3200.00, 90),
  ('Desk Lamp LED',       'Furniture',      1800.00, 120)
ON CONFLICT DO NOTHING;

-- ─────────────────────────────────────────
-- ORDERS
-- ─────────────────────────────────────────
INSERT INTO orders (customer_id, order_date, status, total_amount) VALUES
  (1, '2025-01-05', 'delivered',   76200.00),
  (2, '2025-01-12', 'delivered',   13200.00),
  (3, '2025-02-03', 'delivered',   30200.00),
  (4, '2025-02-18', 'shipped',      9299.00),
  (5, '2025-03-01', 'processing',   8500.00),
  (6, '2025-03-14', 'delivered',   28500.00),
  (7, '2025-04-07', 'cancelled',    4500.00),
  (8, '2025-04-22', 'delivered',   24000.00),
  (9, '2025-05-09', 'pending',      3200.00),
  (10,'2025-05-20', 'delivered',   10300.00),
  (1, '2025-06-01', 'delivered',    5700.00),
  (2, '2025-06-18', 'shipped',     22000.00),
  (3, '2025-07-03', 'delivered',    1200.00),
  (4, '2025-07-19', 'processing',   2500.00),
  (5, '2025-08-05', 'delivered',   75000.00)
ON CONFLICT DO NOTHING;

-- ─────────────────────────────────────────
-- ORDER ITEMS
-- ─────────────────────────────────────────
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
  (1,  1, 1, 75000.00),  -- Laptop
  (1,  2, 1,  1200.00),  -- Mouse
  (2,  6, 1, 12000.00),  -- Chair
  (2,  4, 1,  4500.00),  -- Keyboard (corrected sum)
  (3,  5, 1, 28000.00),  -- Monitor
  (3,  3, 1,  2500.00),  -- Hub
  (4,  8, 3,   499.00),  -- Books
  (4, 12, 3,  1800.00),  -- Lamp
  (5, 10, 1,  8500.00),  -- Headset
  (6,  5, 1, 28000.00),  -- Monitor
  (6, 11, 1,  3200.00),  -- Webcam
  (7,  4, 1,  4500.00),  -- Keyboard
  (8,  7, 1, 22000.00),  -- Standing Desk
  (8, 12, 1,  1800.00),  -- Lamp
  (9, 11, 1,  3200.00),  -- Webcam
  (10, 10,1,  8500.00),  -- Headset
  (10, 9, 3,   599.00),  -- Books
  (11, 8, 5,   499.00),  -- Books
  (11, 9, 3,   599.00),  -- Books
  (12, 7, 1, 22000.00),  -- Standing Desk
  (13, 2, 1,  1200.00),  -- Mouse
  (14, 3, 1,  2500.00),  -- Hub
  (15, 1, 1, 75000.00)   -- Laptop
ON CONFLICT DO NOTHING;

-- ─────────────────────────────────────────
-- METADATA — register demo tables
-- ─────────────────────────────────────────
INSERT INTO uploaded_tables (table_name, uploaded_by, upload_time) VALUES
  ('customers',    'system', CURRENT_TIMESTAMP),
  ('products',     'system', CURRENT_TIMESTAMP),
  ('orders',       'system', CURRENT_TIMESTAMP),
  ('order_items',  'system', CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;
