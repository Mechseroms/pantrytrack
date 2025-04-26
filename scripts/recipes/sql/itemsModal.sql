SELECT item.id, item.barcode, item.item_name FROM %%site_name%%_items item
LIMIT %s OFFSET %s;