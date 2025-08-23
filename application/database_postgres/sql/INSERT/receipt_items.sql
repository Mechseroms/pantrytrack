INSERT INTO %%site_name%%_receipt_items
(type, receipt_id, barcode, item_uuid, name, qty, uom, data, status) 
VALUES (%(type)s, %(receipt_id)s, %(barcode)s, %(item_uuid)s, %(name)s, %(qty)s, 
%(uom)s, %(data)s, %(status)s) 
RETURNING *;