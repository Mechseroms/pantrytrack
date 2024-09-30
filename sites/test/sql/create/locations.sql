CREATE TABLE IF NOT EXISTS test_locations(
    id SERIAL PRIMARY KEY,
    name VARCHAR(32) NOT NULL,
    zone_id INTEGER NOT NULL,
    items JSONB,
    UNIQUE(name),
    CONSTRAINT fk_zone
        FOREIGN KEY(zone_id)
        REFERENCES test_zones(id)
);