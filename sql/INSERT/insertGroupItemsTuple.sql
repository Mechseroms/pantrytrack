INSERT INTO %%site_name%%_group_items
(uuid, gr_id, item_type, item_name, uom, qty, item_id, links) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
RETURNING *;