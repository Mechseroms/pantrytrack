SELECT items.item_uuid as item_uuid,
    items.item_name as item_name,
    units.fullname AS fullname,
    units.id AS unit_id,
    items.links AS links
FROM %%site_name%%_items items
LEFT JOIN %%site_name%%_item_info item_info ON item_info.id = items.item_info_id
LEFT JOIN units ON item_info.uom = units.id
WHERE items.search_string LIKE '%%' || %s || '%%' 
ORDER BY items.item_name 
LIMIT %s OFFSET %s;