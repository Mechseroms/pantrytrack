CREATE TABLE IF NOT EXISTS main_item_locations(
    id SERIAL PRIMARY KEY,
    part_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    quantity_on_hand FLOAT8 NOT NULL,
    cost_layers INTEGER[] DEFAULT '{}', 
    UNIQUE(part_id, location_id),
    CONSTRAINT fk_part_id
        FOREIGN KEY(part_id) 
        REFERENCES main_items(id),
    CONSTRAINT fk_location_id
        FOREIGN KEY(location_id) 
        REFERENCES main_locations(id)
);