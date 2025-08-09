SELECT items.item_uuid, items.item_name 
FROM %%site_name%%_items items 
WHERE items.item_type = 'FOOD_PLU' ORDER BY items.item_name ASC
LIMIT %s OFFSET %s;