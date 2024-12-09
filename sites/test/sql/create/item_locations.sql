DO $$
BEGIN
   IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'cost_layer') THEN
      CREATE TYPE cost_layer AS (qty FLOAT8, cost FLOAT8);
   END IF;
END $$;

CREATE TABLE IF NOT EXISTS test_item_locations(
    id SERIAL PRIMARY KEY,
    part_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    quantity_on_hand FLOAT8 NOT NULL,
    cost_layers cost_layer[], 
    UNIQUE(part_id, location_id),
    CONSTRAINT fk_part_id
        FOREIGN KEY(part_id) 
        REFERENCES test_items(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_location_id
        FOREIGN KEY(location_id) 
        REFERENCES test_locations(id)
        ON DELETE CASCADE
);