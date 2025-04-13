INSERT INTO %%site_name%%_conversions
(item_id, uom_id, conv_factor) 
VALUES (%s, %s, %s) 
RETURNING *;