INSERT INTO %%site_name%%_brands
(name) 
VALUES (%(name)s) 
RETURNING *;