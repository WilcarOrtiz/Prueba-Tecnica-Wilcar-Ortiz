DROP TABLE IF EXISTS purchase_products;
DROP TABLE IF EXISTS purchases;
DROP TABLE IF EXISTS products;
DROP TYPE IF EXISTS purchase_status;

CREATE TYPE purchase_status AS ENUM ('pending', 'completed', 'cancelled');

CREATE TABLE IF NOT EXISTS products (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    price FLOAT,
    category VARCHAR(100),
    created_at DATE
);

CREATE TABLE IF NOT EXISTS purchases (
    id VARCHAR(50) PRIMARY KEY,
    status purchase_status,
    credit_card_type VARCHAR(50),
    purchase_date DATE,
    total FLOAT
);

CREATE TABLE IF NOT EXISTS purchase_products (
    purchase_id VARCHAR(50),
    product_id INT,
    quantity INT,
    PRIMARY KEY (purchase_id, product_id),
    FOREIGN KEY (purchase_id) REFERENCES purchases(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
