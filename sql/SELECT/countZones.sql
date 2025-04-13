SELECT COUNT(*)
FROM
(SELECT zones.id
FROM %%site_name%%_zones zones
LEFT JOIN %%site_name%%_locations locations ON zones.id = locations.zone_id
GROUP BY zones.id
HAVING COUNT(locations.id) > 0) AS subquery;