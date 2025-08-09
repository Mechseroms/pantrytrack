INSERT INTO %%site_name%%_receipt_items
(type, receipt_id, barcode, item_uuid, name, qty, uom, data, status) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
RETURNING *;