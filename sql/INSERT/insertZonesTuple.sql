INSERT INTO %%site_name%%_zones
(name, description) 
VALUES (%s, %s) 
RETURNING *;