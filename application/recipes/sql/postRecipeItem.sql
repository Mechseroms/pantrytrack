INSERT INTO %%site_name%%_recipe_items
(item_uuid, rp_id, item_type, item_name, uom, qty, item_id, links) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
RETURNING *;