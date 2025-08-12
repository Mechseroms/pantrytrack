CREATE TABLE IF NOT EXISTS %%site_name%%_Transactions (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    logistics_info_id INTEGER NOT NULL,
    barcode VARCHAR(255),
    name VARCHAR(255),
    transaction_type VARCHAR(255) NOT NULL,
    quantity FLOAT8 NOT NULL,
    description TEXT,
    user_id INTEGER NOT NULL,
    data JSONB,
    CONSTRAINT fk_logistics_info
        FOREIGN KEY(logistics_info_id) 
        REFERENCES %%site_name%%_logistics_info(id)
        ON DELETE CASCADE
);