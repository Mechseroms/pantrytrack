CREATE TABLE IF NOT EXISTS test2_receipts (
    id SERIAL PRIMARY KEY,
    receipt_id INTEGER NOT NULL,
    receipt_status VARCHAR (64) NOT NULL,
    date_submitted TIMESTAMP NOT NULL,
    submitted_by INTEGER NOT NULL,
    vendor_id INTEGER,
    files JSONB,
    UNIQUE(receipt_id)
);