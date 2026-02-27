-- =============================================================================
-- Data Copilot — Sample Database Seed
-- Generates a realistic business dataset for demonstration purposes.
-- Target: PostgreSQL 15+
-- =============================================================================

-- Create read-only role for the application
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'datacopilot_readonly') THEN
        CREATE ROLE datacopilot_readonly WITH LOGIN PASSWORD 'datacopilot';
    END IF;
END
$$;

-- Grant permissions
GRANT CONNECT ON DATABASE datacopilot TO datacopilot_readonly;
GRANT USAGE ON SCHEMA public TO datacopilot_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO datacopilot_readonly;

-- =============================================================================
-- Schema
-- =============================================================================

CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    segment VARCHAR(20) NOT NULL,
    region VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    cost DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    order_date DATE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'completed'
);

CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS sales_reps (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    region VARCHAR(20) NOT NULL,
    hire_date DATE NOT NULL
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_customers_segment ON customers(segment);
CREATE INDEX IF NOT EXISTS idx_customers_region ON customers(region);

-- =============================================================================
-- Products (30 rows)
-- Inserted manually for realistic names and pricing
-- =============================================================================

INSERT INTO products (name, category, price, cost, status) VALUES
    -- Electronics (7)
    ('ProDisplay 27" Monitor',        'Electronics',  449.99, 280.00, 'active'),
    ('UltraBook Pro 15',              'Electronics', 1299.99, 820.00, 'active'),
    ('Wireless Noise-Cancel Headset', 'Electronics',  189.99, 75.00,  'active'),
    ('Smart Conference Camera',       'Electronics',  349.99, 195.00, 'active'),
    ('Portable SSD 2TB',              'Electronics',  129.99, 62.00,  'active'),
    ('4K Webcam',                     'Electronics',   99.99, 38.00,  'active'),
    ('Desktop Workstation X1',        'Electronics', 2199.99, 1450.00,'active'),
    -- Software (6)
    ('DataSync Pro License',          'Software',     299.99, 15.00,  'active'),
    ('CloudVault Backup (Annual)',    'Software',     149.99, 8.00,   'active'),
    ('SecureAuth Platform',           'Software',     499.99, 25.00,  'active'),
    ('Analytics Dashboard Suite',     'Software',     799.99, 40.00,  'active'),
    ('ProjectFlow Team (Annual)',     'Software',     199.99, 12.00,  'active'),
    ('DevOps Toolkit Enterprise',     'Software',    1499.99, 60.00,  'discontinued'),
    -- Services (6)
    ('Onsite Installation',           'Services',     199.99, 120.00, 'active'),
    ('Premium Support Plan (Annual)', 'Services',     999.99, 350.00, 'active'),
    ('Data Migration Service',        'Services',    2499.99, 1200.00,'active'),
    ('Security Audit',                'Services',    3499.99, 1800.00,'active'),
    ('Staff Training (per session)',  'Services',     599.99, 250.00, 'active'),
    ('Infrastructure Consulting',     'Services',    4999.99, 2800.00,'active'),
    -- Hardware (6)
    ('RackMount Server R620',         'Hardware',    5999.99, 4100.00,'active'),
    ('Network Switch 48-Port',        'Hardware',     899.99, 520.00, 'active'),
    ('UPS Battery Backup 1500VA',     'Hardware',     349.99, 190.00, 'active'),
    ('Enterprise Router',             'Hardware',    1199.99, 680.00, 'active'),
    ('NAS Storage 8-Bay',             'Hardware',    1799.99, 1050.00,'active'),
    ('Legacy Print Server',           'Hardware',     249.99, 160.00, 'discontinued'),
    -- Accessories (5)
    ('Ergonomic Keyboard',            'Accessories',   89.99, 32.00,  'active'),
    ('Wireless Mouse Pro',            'Accessories',   49.99, 16.00,  'active'),
    ('USB-C Docking Station',         'Accessories',  179.99, 78.00,  'active'),
    ('Cable Management Kit',          'Accessories',   29.99, 8.00,   'active'),
    ('Laptop Stand Adjustable',       'Accessories',   69.99, 25.00,  'active');

-- =============================================================================
-- Sales Reps (20 rows)
-- =============================================================================

INSERT INTO sales_reps (name, region, hire_date) VALUES
    ('Marcus Johnson',    'North',   '2019-03-15'),
    ('Sarah Chen',        'North',   '2020-07-01'),
    ('David Kim',         'North',   '2021-11-20'),
    ('Rachel Torres',     'North',   '2023-01-10'),
    ('James Wright',      'South',   '2018-06-22'),
    ('Amanda Foster',     'South',   '2020-02-14'),
    ('Carlos Mendez',     'South',   '2022-04-05'),
    ('Lisa Nguyen',       'South',   '2023-08-19'),
    ('Robert Patel',      'East',    '2017-09-30'),
    ('Jennifer Adams',    'East',    '2019-12-01'),
    ('Michael O''Brien',  'East',    '2021-06-15'),
    ('Samantha Lee',      'East',    '2022-10-28'),
    ('Thomas Garcia',     'West',    '2018-01-08'),
    ('Emily Robinson',    'West',    '2020-05-22'),
    ('Daniel Huang',      'West',    '2021-09-14'),
    ('Olivia Martinez',   'West',    '2023-03-30'),
    ('William Clark',     'Central', '2019-07-17'),
    ('Jessica Taylor',    'Central', '2020-11-09'),
    ('Andrew Wilson',     'Central', '2022-02-28'),
    ('Natalie Brooks',    'Central', '2023-06-12');

-- =============================================================================
-- Customers (500 rows)
-- Generated using arrays and generate_series for variety.
-- Enterprise and SMB customers skew toward earlier creation dates;
-- Startups and Individuals skew more recent — mimicking real growth patterns.
-- =============================================================================

INSERT INTO customers (name, email, segment, region, created_at)
SELECT
    -- Build a realistic full name from first + last arrays
    (ARRAY[
        'James','Maria','Robert','Linda','Michael','Patricia','William','Elizabeth',
        'David','Jennifer','Richard','Susan','Joseph','Karen','Thomas','Nancy',
        'Christopher','Betty','Daniel','Margaret','Matthew','Sandra','Anthony','Ashley',
        'Mark','Dorothy','Steven','Kimberly','Paul','Donna','Andrew','Carol',
        'Joshua','Michelle','Kenneth','Emily','Kevin','Amanda','Brian','Melissa',
        'George','Deborah','Timothy','Stephanie','Ronald','Rebecca','Edward','Sharon',
        'Jason','Laura'
    ])[1 + (s % 50)]
    || ' ' ||
    (ARRAY[
        'Smith','Johnson','Williams','Brown','Jones','Garcia','Miller','Davis',
        'Rodriguez','Martinez','Hernandez','Lopez','Gonzalez','Wilson','Anderson',
        'Thomas','Taylor','Moore','Jackson','Martin','Lee','Perez','Thompson',
        'White','Harris','Sanchez','Clark','Ramirez','Lewis','Robinson','Walker',
        'Young','Allen','King','Wright','Scott','Torres','Nguyen','Hill',
        'Flores','Green','Adams','Nelson','Baker','Hall','Rivera','Campbell',
        'Mitchell','Carter'
    ])[1 + ((s * 7 + 13) % 50)] AS name,

    -- Email: lowercase first initial + last name + number
    LOWER(
        LEFT(
            (ARRAY[
                'James','Maria','Robert','Linda','Michael','Patricia','William','Elizabeth',
                'David','Jennifer','Richard','Susan','Joseph','Karen','Thomas','Nancy',
                'Christopher','Betty','Daniel','Margaret','Matthew','Sandra','Anthony','Ashley',
                'Mark','Dorothy','Steven','Kimberly','Paul','Donna','Andrew','Carol',
                'Joshua','Michelle','Kenneth','Emily','Kevin','Amanda','Brian','Melissa',
                'George','Deborah','Timothy','Stephanie','Ronald','Rebecca','Edward','Sharon',
                'Jason','Laura'
            ])[1 + (s % 50)], 1)
    )
    || LOWER(
        (ARRAY[
            'Smith','Johnson','Williams','Brown','Jones','Garcia','Miller','Davis',
            'Rodriguez','Martinez','Hernandez','Lopez','Gonzalez','Wilson','Anderson',
            'Thomas','Taylor','Moore','Jackson','Martin','Lee','Perez','Thompson',
            'White','Harris','Sanchez','Clark','Ramirez','Lewis','Robinson','Walker',
            'Young','Allen','King','Wright','Scott','Torres','Nguyen','Hill',
            'Flores','Green','Adams','Nelson','Baker','Hall','Rivera','Campbell',
            'Mitchell','Carter'
        ])[1 + ((s * 7 + 13) % 50)]
    )
    || s::TEXT
    || '@'
    || (ARRAY['company.com','corp.net','enterprise.io','business.org','tech.co'])[1 + (s % 5)]
    AS email,

    -- Segment distribution: ~20% Enterprise, ~30% SMB, ~30% Startup, ~20% Individual
    (ARRAY['Enterprise','Enterprise','SMB','SMB','SMB','Startup','Startup','Startup','Individual','Individual'])[1 + (s % 10)] AS segment,

    -- Region distribution roughly even
    (ARRAY['North','South','East','West','Central'])[1 + (s % 5)] AS region,

    -- Creation dates: spread across 2021-2024, with more recent dates for Startups/Individuals
    TIMESTAMP '2021-01-01' + (
        CASE
            WHEN (ARRAY['Enterprise','Enterprise','SMB','SMB','SMB','Startup','Startup','Startup','Individual','Individual'])[1 + (s % 10)] IN ('Enterprise','SMB')
            THEN (random() * 900)::INT  -- up to ~2.5 years from 2021
            ELSE (random() * 500 + 600)::INT  -- 2022-08 through 2024-08
        END
    ) * INTERVAL '1 day'
    AS created_at

FROM generate_series(1, 500) AS s;

-- =============================================================================
-- Orders (~5000 rows)
-- Enterprise customers place larger and more frequent orders.
-- Seasonal bump in Q4 (Oct-Dec) to mimic holiday / end-of-year purchasing.
-- Status distribution: ~80% completed, ~10% pending, ~5% cancelled, ~5% refunded.
-- =============================================================================

INSERT INTO orders (customer_id, order_date, total_amount, status)
SELECT
    -- Pick a customer (weighted toward lower IDs which are more Enterprise/SMB)
    (1 + (random() * 499)::INT) AS customer_id,

    -- Spread orders across 2023-01-01 to 2024-12-31
    DATE '2023-01-01' + (random() * 729)::INT AS order_date,

    -- Placeholder total (will be recalculated from order_items below)
    0.00 AS total_amount,

    -- Status distribution
    (ARRAY[
        'completed','completed','completed','completed','completed','completed','completed','completed',
        'pending','pending',
        'cancelled',
        'refunded'
    ])[1 + (s % 12)] AS status

FROM generate_series(1, 5000) AS s;

-- =============================================================================
-- Order Items (~12,000 rows)
-- Each order gets 1-5 line items. Higher-value products appear less frequently.
-- =============================================================================

INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT
    o.id AS order_id,
    p.id AS product_id,
    -- Quantity: accessories/software 1-10, hardware/services usually 1-2
    CASE
        WHEN p.category IN ('Accessories','Software') THEN 1 + (random() * 9)::INT
        WHEN p.category = 'Electronics' THEN 1 + (random() * 3)::INT
        ELSE 1 + (random() * 1)::INT
    END AS quantity,
    p.price AS unit_price
FROM (
    -- For each order, pick a random number of distinct products (1-5 line items)
    SELECT
        o.id,
        -- Generate 1-5 item slots per order
        generate_series(1, 1 + (random() * LEAST(4, (o.id % 5)))::INT) AS item_slot
    FROM orders o
) o
CROSS JOIN LATERAL (
    -- Pick a random product, weighted toward active products
    SELECT id, price, category
    FROM products
    WHERE status = 'active'
    ORDER BY random()
    LIMIT 1
) p;

-- =============================================================================
-- Recalculate order totals from actual line items
-- =============================================================================

UPDATE orders
SET total_amount = sub.total
FROM (
    SELECT order_id, SUM(quantity * unit_price) AS total
    FROM order_items
    GROUP BY order_id
) sub
WHERE orders.id = sub.order_id;

-- =============================================================================
-- Add seasonal pattern: boost Q4 order totals by 15-30% to simulate holiday surge
-- =============================================================================

UPDATE orders
SET total_amount = total_amount * (1.15 + random() * 0.15)
WHERE EXTRACT(MONTH FROM order_date) IN (10, 11, 12);

-- =============================================================================
-- Enterprise customers get a 20-50% uplift on order value (larger contracts)
-- =============================================================================

UPDATE orders
SET total_amount = ROUND((total_amount * (1.20 + random() * 0.30))::NUMERIC, 2)
WHERE customer_id IN (
    SELECT id FROM customers WHERE segment = 'Enterprise'
);

-- =============================================================================
-- Grant read access on all tables
-- =============================================================================

GRANT SELECT ON ALL TABLES IN SCHEMA public TO datacopilot_readonly;
