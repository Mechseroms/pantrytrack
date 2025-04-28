SELECT item.id, item.barcode, item.item_name, u.id as uom FROM %%site_name%%_items item
LEFT JOIN %%site_name%%_item_info item_info ON item_info.id = item.item_info_id
LEFT JOIN units u ON u.id = item_info.uom
WHERE item.search_string LIKE '%%' || %s || '%%'
LIMIT %s OFFSET %s;