CREATE TABLE IF NOT EXISTS %%site_name%%_shopping_list_items (
    list_item_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    list_uuid UUID REFERENCES %%site_name%%_shopping_lists(list_uuid) ON DELETE CASCADE NOT NULL,
    list_item_type VARCHAR(32) NOT NULL,
    list_item_name VARCHAR(64) DEFAULT '' NOT NULL,
    list_item_uom INTEGER DEFAULT 1 NOT NULL,
    list_item_quantity FLOAT8 DEFAULT 0.00 NOT NULL,
    item_uuid UUID DEFAULT NULL,
    list_links JSONB DEFAULT '{"main": ""}',
    list_item_state BOOLEAN DEFAULT false,
    UNIQUE(list_uuid, item_uuid)
);