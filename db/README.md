# QueryShield AI — Database Setup Guide

## Prerequisites
- PostgreSQL 15+ installed and running
- `psql` available in your terminal

---

## Step 1 — Create the Database

```bash
psql -U postgres -c "CREATE DATABASE queryshield_db;"
```

---

## Step 2 — Run the Schema

```bash
psql -U postgres -d queryshield_db -f db/schema.sql
```

Creates these tables:
| Table | Purpose |
|-------|---------|
| `uploaded_tables` | Metadata tracking for all user-uploaded CSVs |
| `customers` | Demo customer data |
| `products` | Demo product catalog |
| `orders` | Demo orders linked to customers |
| `order_items` | Line items linking orders ↔ products |

And these indexes:
| Index | Column |
|-------|--------|
| `idx_orders_customer_id` | `orders.customer_id` |
| `idx_order_items_order_id` | `order_items.order_id` |
| `idx_order_items_product_id` | `order_items.product_id` |

---

## Step 3 — Load Demo Data

```bash
psql -U postgres -d queryshield_db -f db/seed.sql
```

Inserts: 10 customers, 12 products, 15 orders, 23 order items.

---

## Step 4 — Verify

```bash
psql -U postgres -d queryshield_db
```

Then inside psql:
```sql
\dt                          -- list all tables
\di idx_*                    -- list all indexes
SELECT * FROM uploaded_tables;
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM orders;
```

---

## Resetting the Database

```bash
psql -U postgres -c "DROP DATABASE IF EXISTS queryshield_db;"
psql -U postgres -c "CREATE DATABASE queryshield_db;"
psql -U postgres -d queryshield_db -f db/schema.sql
psql -U postgres -d queryshield_db -f db/seed.sql
```
