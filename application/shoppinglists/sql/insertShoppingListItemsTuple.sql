INSERT INTO %%site_name%%_shopping_list_items
(uuid, sl_id, item_type, item_name, uom, qty, item_id, links) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
RETURNING *;