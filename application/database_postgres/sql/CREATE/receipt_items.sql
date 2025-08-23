CREATE TABLE IF NOT EXISTS %%site_name%%_receipt_items (
    receipt_item_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4() NOT NULL,
    receipt_uuid UUID REFERENCES %%site_name%%_receipts(receipt_uuid) ON DELETE CASCADE NOT NULL,
    receipt_item_type VARCHAR(255) DEFAULT 'unknown' NOT NULL,
    receipt_item_barcode VARCHAR(255) DEFAULT NULL,
    receipt_item_name VARCHAR(255) DEFAULT '' NOT NULL, 
    receipt_item_quantity FLOAT8 DEFAULT 0.00 NOT NULL,
    receipt_item_uom INTEGER DEFAULT 1 NOT NULL,
    receipt_item_data JSONB DEFAULT '{}' NOT NULL, 
    receipt_item_status VARCHAR (64) DEFAULT 'unknown' NOT NULL
);