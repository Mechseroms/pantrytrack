SELECT %%site_name%%_items.*,
    row_to_json(%%site_name%%_item_info.*) as item_info
FROM %%site_name%%_items
LEFT JOIN %%site_name%%_item_info ON %%site_name%%_items.item_info_id = %%site_name%%_item_info.id 
WHERE %%site_name%%_items.search_string LIKE '%%' || %s || '%%' 
AND %%site_name%%_items.row_type <> 'link'
ORDER BY %%site_name%%_items.id ASC
LIMIT %s OFFSET %s;

