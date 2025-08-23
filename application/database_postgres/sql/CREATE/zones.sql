CREATE TABLE IF NOT EXISTS %%site_name%%_zones(
    zone_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    zone_name VARCHAR(32) NOT NULL,
    zone_description TEXT DEFAULT '' NOT NULL,
    UNIQUE(zone_name)
);
