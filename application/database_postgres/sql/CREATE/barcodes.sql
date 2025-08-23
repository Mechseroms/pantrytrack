CREATE TABLE IF NOT EXISTS %%site_name%%_barcodes (
    item_uuid UUID PRIMARY KEY REFERENCES %%site_name%%_items(item_uuid) ON DELETE CASCADE,
    barcode VARCHAR(32) NOT NULL,
    in_exchange FLOAT DEFAULT 0.00 NOT NULL,
    out_exchange FLOAT DEFAULT 0.00 NOT NULL,
    descriptor VARCHAR(255) DEFAULT '' NOT NULL,
    UNIQUE(barcode)
);