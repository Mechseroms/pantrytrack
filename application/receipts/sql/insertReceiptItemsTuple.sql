INSERT INTO %%site_name%%_receipt_items
(type, receipt_id, barcode, name, qty, uom, data, status) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
RETURNING *;