INSERT INTO %%site_name%%_shopping_list_items
(list_uuid, item_type, item_name, uom, qty, item_uuid, links) 
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (list_uuid, item_uuid) DO UPDATE
SET qty = %%site_name%%_shopping_list_items.qty + EXCLUDED.qty
RETURNING *;