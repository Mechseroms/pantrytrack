SELECT item.id, item.barcode, item.item_name FROM %%site_name%%_items item
WHERE item.search_string LIKE '%%' || %s || '%%'
LIMIT %s OFFSET %s;