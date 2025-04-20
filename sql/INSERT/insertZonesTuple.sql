INSERT INTO %%site_name%%_zones
(name, description, site_id) 
VALUES (%s, %s, %s) 
RETURNING *;