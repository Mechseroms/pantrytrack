CREATE TABLE IF NOT EXISTS %%site_name%%_barcodes (
    barcode VARCHAR(32) PRIMARY KEY,
    item_uuid UUID,
    in_exchange FLOAT,
    out_exchange FLOAT
);