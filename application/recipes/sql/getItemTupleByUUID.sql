SELECT items.id AS item_id,
items.item_name as item_name,
items.logistics_info_id as logistics_info_id,
lginf.auto_issue_location as auto_issue_location
FROM %%site_name%%_items items 
LEFT JOIN %%site_name%%_logistics_info lginf ON lginf.id = items.logistics_info_id WHERE item_uuid=%s;