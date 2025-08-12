CREATE TABLE IF NOt EXISTS %%site_name%%_item_info (
    id SERIAL PRIMARY KEY,
    item_info_uuid UUID gen_random_uuid(),
    barcode VARCHAR(255),
    packaging VARCHAR(255),
    uom_quantity FLOAT8,
    uom INTEGER,
    cost FLOAT8,
    safety_stock FLOAT8,
    lead_time_days FLOAT8,
    ai_pick BOOLEAN,
    prefixes INTEGER []
    UNIQUE(item_info_uuid)
);