CREATE TABLE IF NOT EXISTS %%site_name%%_locations(
    location_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    location_shortname VARCHAR(255) NOT NULL,
    location_name VARCHAR(32) NOT NULL,
    zone_uuid UUID REFERENCES %%site_name%%_zones(zone_uuid) ON DELETE SET NULL
);