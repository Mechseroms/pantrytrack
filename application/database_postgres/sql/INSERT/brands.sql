INSERT INTO %%site_name%%_brands
(brand_name) 
VALUES (%(brand_name)s) 
RETURNING *;