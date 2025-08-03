CREATE TABLE IF NOT EXISTS %%site_name%%_receipt_items (
    id SERIAL PRIMARY KEY, 
    type VARCHAR(255) NOT NULL,
    receipt_id INTEGER NOT NULL,
    barcode VARCHAR(255) NOT NULL, 
    name VARCHAR(255) NOT NULL, 
    qty FLOAT8 NOT NULL,
    uom VARCHAR(32) NOT NULL,
    data JSONB, 
    status VARCHAR (64),
    CONSTRAINT fk_receipt
        FOREIGN KEY(receipt_id) 
        REFERENCES %%site_name%%_receipts(id)
        ON DELETE CASCADE
);