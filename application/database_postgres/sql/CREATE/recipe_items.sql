CREATE TABLE IF NOT EXISTS %%site_name%%_recipe_items (
    id SERIAL PRIMARY KEY,
    item_uuid UUID,
    rp_id INTEGER NOT NULL,
    item_type VARCHAR(32) NOT NULL,
    item_name TEXT NOT NULL,
    uom INTEGER NOT NULL,
    qty FLOAT8 NOT NULL,
    item_id INTEGER DEFAULT NULL,
    links JSONB DEFAULT '{"main": ""}',
    CONSTRAINT fk_rp_id
        FOREIGN KEY(rp_id) 
        REFERENCES %%site_name%%_recipes(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_item_id
        FOREIGN KEY(item_id) 
        REFERENCES %%site_name%%_items(id)
        ON DELETE CASCADE
);