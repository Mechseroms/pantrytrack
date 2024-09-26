CREATE TABLE IF NOT EXISTS Transactions (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    barcode VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    transaction_type VARCHAR(255) NOT NULL,
    quantity FLOAT8 NOT NULL,
    description TEXT,
    user_id INTEGER NOT NULL,
    data JSONB
);