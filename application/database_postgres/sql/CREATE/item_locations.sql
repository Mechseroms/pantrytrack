CREATE TABLE IF NOT EXISTS %%site_name%%_item_locations(
    item_location_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    item_uuid UUID REFERENCES %%site_name%%_items(item_uuid) ON DELETE SET NULL,
    location_uuid UUID REFERENCES %%site_name%%_locations(location_uuid) ON DELETE SET NULL,
    item_quantity_on_hand FLOAT8 DEFAULT 0.00 NOT NULL,
    UNIQUE(item_uuid, location_uuid)
);