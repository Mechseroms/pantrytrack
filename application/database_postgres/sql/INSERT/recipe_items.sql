INSERT INTO %%site_name%%_recipe_items
(item_uuid, rp_id, item_type, item_name, uom, qty, item_id, links) 
VALUES (%(item_uuid)s, %(rp_id)s, %(item_type)s, %(item_name)s, %(uom)s, %(qty)s, %(item_id)s, %(links)s) 
RETURNING *;