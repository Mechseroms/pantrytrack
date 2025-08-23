CREATE TABLE IF NOT EXISTS %%site_name%%_cost_layers (
    item_location_uuid UUID REFERENCES %%site_name%%_item_locations(item_location_uuid) ON DELETE SET NULL,
    layer_aquisition_date TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    layer_quantity FLOAT8 DEFAULT 0.00 NOT NULL,
    layer_cost FLOAT8 DEFAULT 0.00 NOT NULL,
    layer_currency_type VARCHAR(16) DEFAULT 'USD' NOT NULL,
    layer_expires TIMESTAMP DEFAULT NULL,
    layer_vendor INTEGER DEFAULT 0 NOT NULL
);