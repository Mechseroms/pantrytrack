CREATE TABLE IF NOt EXISTS test_item_info (
    id SERIAL PRIMARY KEY,
    barcode VARCHAR(255) NOT NULL,
    linked_items INTEGER [],
    shopping_lists INTEGER [],
    recipes INTEGER [],
    groups INTEGER [],
    packaging VARCHAR(255),
    uom VARCHAR(255),
    cost FLOAT8,
    safety_stock FLOAT8,
    lead_time_days FLOAT8,
    ai_pick BOOLEAN,
    UNIQUE(barcode)
);