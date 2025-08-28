SELECT items.item_uuid, items.item_name, units.unit_uuid as uom FROM %%site_name%%_items items
LEFT JOIN %%site_name%%_item_info item_info ON item_info.item_uuid = items.item_uuid
LEFT JOIN units ON units.unit_uuid = item_info.item_uom
WHERE items.item_search_string LIKE '%%' || %(search_string)s || '%%'
    ANd items.item_inactive IS false
ORDER BY %%sort_order%%
LIMIT %(limit)s OFFSET %(offset)s;