INSERT INTO %%site_name%%_zones
(name, site_id) 
VALUES (%s, %s) 
RETURNING *;