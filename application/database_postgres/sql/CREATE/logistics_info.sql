CREATE TABLE IF NOT EXISTS %%site_name%%_logistics_info(
    item_uuid UUID PRIMARY KEY REFERENCES %%site_name%%_items(item_uuid) ON DELETE CASCADE,
    item_primary_location UUID REFERENCES %%site_name%%_locations(location_uuid) ON DELETE SET NULL,
    item_primary_zone UUID REFERENCES %%site_name%%_zones(zone_uuid) ON DELETE SET NULL,
    item_auto_issue_location UUID REFERENCES %%site_name%%_locations(location_uuid) ON DELETE SET NULL,
    item_auto_issue_zone UUID REFERENCES %%site_name%%_zones(zone_uuid) ON DELETE SET NULL
);