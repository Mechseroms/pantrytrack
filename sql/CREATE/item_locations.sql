CREATE TABLE IF NOT EXISTS %%site_name%%_item_locations(
    id SERIAL PRIMARY KEY,
    part_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    quantity_on_hand FLOAT8 NOT NULL,
    cost_layers INTEGER[] DEFAULT '{}', 
    UNIQUE(part_id, location_id),
    CONSTRAINT fk_part_id
        FOREIGN KEY(part_id) 
        REFERENCES %%site_name%%_items(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_location_id
        FOREIGN KEY(location_id) 
        REFERENCES %%site_name%%_locations(id)
        ON DELETE CASCADE
);