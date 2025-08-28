INSERT INTO %%site_name%%_zones
(zone_name, zone_description) 
VALUES (%(zone_name)s, %(zone_description)s) 
RETURNING *;