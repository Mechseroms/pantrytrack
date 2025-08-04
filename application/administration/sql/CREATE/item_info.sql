CREATE TABLE IF NOt EXISTS %%site_name%%_item_info (
    id SERIAL PRIMARY KEY,
    barcode VARCHAR(255) NOT NULL,
    packaging VARCHAR(255),
    uom_quantity FLOAT8,
    uom INTEGER,
    cost FLOAT8,
    safety_stock FLOAT8,
    lead_time_days FLOAT8,
    ai_pick BOOLEAN,
    prefixes INTEGER [],
    UNIQUE(barcode)
);