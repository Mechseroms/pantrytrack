CREATE TABLE IF NOT EXISTS %%site_name%%_conversions (
    conversion_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    item_uuid uuid REFERENCES %%site_name%%_items(item_uuid) ON DELETE CASCADE NOT NULL,
    conversion_uom_id INTEGER DEFAULT 1 NOT NULL,
    conversion_conv_factor FLOAT8 DEFAULT 0.00 NOT NULL,
    UNIQUE(item_uuid, conversion_uom_id)
);