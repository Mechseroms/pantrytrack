INSERT INTO %%site_name%%_sku_prefix
(uuid, name, description) 
VALUES (%(uuid)s, %(name)s, %(description)s) 
RETURNING *;