CREATE TABLE IF NOT EXISTS %%site_name%%_item_info (
    item_uuid UUID PRIMARY KEY REFERENCES %%site_name%%_items(item_uuid) ON DELETE CASCADE,
    item_uom INTEGER NOT NULL,
    item_packaging VARCHAR(255) DEFAULT '' NOT NULL,
    item_uom_quantity FLOAT8 DEFAULT 0.00 NOT NULL,
    item_cost FLOAT8 DEFAULT 0.00 NOT NULL,
    item_safety_stock FLOAT8 DEFAULT 0.00 NOT NULL,
    item_lead_time_days FLOAT8 DEFAULT 0.00 NOT NULL,
    item_ai_pick BOOLEAN DEFAULT false NOT NULL,
    item_prefixes INTEGER [] DEFAULT '{}' NOT NULL
);