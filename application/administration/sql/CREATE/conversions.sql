CREATE TABLE IF NOT EXISTS %%site_name%%_conversions (
    id SERIAL PRIMARY KEY,
    item_id INTEGER NOT NULL,
    uom_id INTEGER NOT NULL,
    conv_factor FLOAT8 NOT NULL,
    UNIQUE(item_id, uom_id)
);