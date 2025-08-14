SELECT items.*, 
    (SELECT COALESCE(row_to_json(un), '{}') FROM units un WHERE un.id = items.uom LIMIT 1) AS uom
FROM %%site_name%%_shopping_list_items items
WHERE items.list_item_uuid = %s::uuid; 