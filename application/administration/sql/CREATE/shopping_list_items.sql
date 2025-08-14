CREATE TABLE IF NOT EXISTS %%site_name%%_shopping_list_items (
    list_item_uuid UUID DEFAULT uuid_generate_v4() NOT NULL PRIMARY KEY,
    list_uuid UUID NOT NULL,
    item_type VARCHAR(32) NOT NULL,
    item_name TEXT NOT NULL,
    uom INTEGER NOT NULL,
    qty FLOAT8 NOT NULL,
    item_uuid UUID DEFAULT NULL,
    links JSONB DEFAULT '{"main": ""}',
    UNIQUE(list_uuid, item_uuid)
);