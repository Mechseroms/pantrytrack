SELECT * FROM %%site_name%%_item_locations
LEFT JOIN %%site_name%%_locations ON %%site_name%%_locations.id = %%site_name%%_item_locations.location_id
WHERE part_id = %s
LIMIT %s
OFFSET %s;