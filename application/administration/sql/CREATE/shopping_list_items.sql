CREATE TABLE IF NOT EXISTS %%site_name%%_shopping_list_items (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(32) NOT NULL,
    sl_id INTEGER NOT NULL,
    item_type VARCHAR(32) NOT NULL,
    item_name TEXT NOT NULL,
    uom INTEGER NOT NULL,
    qty FLOAT8 NOT NULL,
    item_id INTEGER DEFAULT NULL,
    links JSONB DEFAULT '{"main": ""}',
    UNIQUE(uuid, sl_id),
    CONSTRAINT fk_sl_id
        FOREIGN KEY(sl_id) 
        REFERENCES %%site_name%%_shopping_lists(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_item_id
        FOREIGN KEY(item_id) 
        REFERENCES %%site_name%%_items(id)
        ON DELETE CASCADE
);