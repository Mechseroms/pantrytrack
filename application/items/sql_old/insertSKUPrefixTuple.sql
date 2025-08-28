INSERT INTO %%site_name%%_sku_prefix
(uuid, name, description) 
VALUES (%s, %s, %s) 
RETURNING *;