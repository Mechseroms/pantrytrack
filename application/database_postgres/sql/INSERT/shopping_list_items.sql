INSERT INTO %%site_name%%_shopping_list_items
(list_uuid, item_type, item_name, uom, qty, item_uuid, links) 
VALUES (%(list_uuid)s, %(item_type)s, %(item_name)s, %(uom)s, %(qty)s, %(item_uuid)s, %(links)s)
ON CONFLICT (list_uuid, item_uuid) DO UPDATE
SET qty = %%site_name%%_shopping_list_items.qty + EXCLUDED.qty
RETURNING *;