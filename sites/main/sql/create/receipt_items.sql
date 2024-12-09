CREATE TABLE IF NOT EXISTS main_receipt_items (
    id SERIAL PRIMARY KEY, 
    type VARCHAR(255) NOT NULL,
    receipt_id INTEGER NOT NULL,
    barcode VARCHAR(255) NOT NULL, 
    name VARCHAR(255) NOT NULL, 
    qty FLOAT8 NOT NULL, 
    data JSONB, 
    status VARCHAR (64),
    CONSTRAINT fk_receipt
        FOREIGN KEY(receipt_id) 
        REFERENCES main_receipts(id)
);