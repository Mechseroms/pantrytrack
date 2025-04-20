SELECT il.* FROM %%site_name%%_item_locations il
LEFT JOIN %%site_name%%_zones zone ON zone.id = il.zone_id
WHERE il.id = %s;