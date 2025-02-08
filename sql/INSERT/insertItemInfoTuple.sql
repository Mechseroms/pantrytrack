INSERT INTO %%site_name%%_item_info
(barcode, linked_items, shopping_lists, recipes, groups, 
packaging, uom, cost, safety_stock, lead_time_days, ai_pick) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
RETURNING *;