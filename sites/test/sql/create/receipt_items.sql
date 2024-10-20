CREATE TABLE IF NOT EXISTS test_receipt_items (
    id SERIAL PRIMARY KEY, 
    type VARCHAR(255) NOT NULL, 
    barcode VARCHAR(255) NOT NULL, 
    name VARCHAR(255) NOT NULL, 
    qty FLOAT8 NOT NULL, 
    data JSONB, 
    status VARCHAR (64)
);