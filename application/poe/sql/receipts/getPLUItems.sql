SELECT items.item_uuid, items.item_name, item_info.cost, item_info.uom
FROM %%site_name%%_items items
LEFT JOIN %%site_name%%_item_info item_info ON item_info.id = items.item_info_id
WHERE items.item_type = 'FOOD_PLU' ORDER BY items.item_name ASC
LIMIT %s OFFSET %s;