SELECT item.id, item.barcode, item.item_name, item.links, item_info.uom_quantity, item_info.uom
FROM %%site_name%%_items item
LEFT JOIN %%site_name%%_item_info item_info ON item_info.id = item.item_info_id
WHERE item.id = %s; 