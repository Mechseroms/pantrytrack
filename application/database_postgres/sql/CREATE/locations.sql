CREATE TABLE IF NOT EXISTS %%site_name%%_locations(
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(255) NOT NULL,
    name VARCHAR(32) NOT NULL,
    zone_id INTEGER NOT NULL,
    UNIQUE(uuid),
    CONSTRAINT fk_zone
        FOREIGN KEY(zone_id)
        REFERENCES %%site_name%%_zones(id)
);