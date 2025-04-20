SELECT %%site_name%%_locations.*,
row_to_json(%%site_name%%_zones.*) as zone 
FROM %%site_name%%_locations
LEFT JOIN %%site_name%%_zones ON %%site_name%%_zones.id = %%site_name%%_locations.zone_id
LIMIT %s OFFSET %s;