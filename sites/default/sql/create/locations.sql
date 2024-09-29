CREATE TABLE IF NOT EXISTS %sitename%_locations(
    id SERIAL PRIMARY KEY,
    name VARCHAR(32) NOT NULL,
    zone_id INTEGER NOT NULL,
    UNIQUE(name),
    CONSTRAINT fk_zone
        FOREIGN KEY(zone_id)
        REFERENCES %sitename%_zones(id)
);