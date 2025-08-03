INSERT INTO %%site_name%%_locations
(uuid, name, zone_id) 
VALUES (%s, %s, %s) 
RETURNING *;