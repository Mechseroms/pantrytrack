INSERT INTO %%site_name%%_zones
(name, description) 
VALUES (%(name)s, %(description)s) 
RETURNING *;