INSERT INTO %%site_name%%_conversions
(item_id, uom_id, conv_factor) 
VALUES (%(item_id)s, %(uom_id)s, %(conv_factor)s) 
RETURNING *;