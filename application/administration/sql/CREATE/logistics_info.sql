CREATE TABLE IF NOT EXISTS %%site_name%%_logistics_info(
    id SERIAL PRIMARY KEY,
    logistics_info_uuid UUID gen_random_uuid(),
    barcode VARCHAR(255),
    primary_location INTEGER NOT NULL,
    primary_zone INTEGER NOT NULL,
    auto_issue_location INTEGER NOT NULL,
    auto_issue_zone INTEGER NOT NULL,
    UNIQUE(logistics_info_uuid),
    CONSTRAINT fk_primary_location
        FOREIGN KEY(primary_location) 
        REFERENCES %%site_name%%_locations(id),
    CONSTRAINT fk_primary_zone
        FOREIGN KEY(primary_zone) 
        REFERENCES %%site_name%%_zones(id),
    CONSTRAINT fk_auto_issue_location
        FOREIGN KEY(auto_issue_location) 
        REFERENCES %%site_name%%_locations(id),
    CONSTRAINT fk_auto_issue_zone
        FOREIGN KEY(auto_issue_zone) 
        REFERENCES %%site_name%%_zones(id)
);