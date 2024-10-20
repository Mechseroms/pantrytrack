CREATE TABLE IF NOT EXISTS test2_locations(
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(255) NOT NULL,
    name VARCHAR(32) NOT NULL,
    zone_id INTEGER NOT NULL,
    items JSONB,
    UNIQUE(uuid),
    CONSTRAINT fk_zone
        FOREIGN KEY(zone_id)
        REFERENCES test2_zones(id)
);