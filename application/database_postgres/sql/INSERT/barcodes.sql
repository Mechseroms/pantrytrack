INSERT INTO %%site_name%%_barcodes 
(barcode, item_uuid, in_exchange, out_exchange, descriptor) 
VALUES (%(barcode)s, %(item_uuid)s, %(in_exchange)s, %(out_exchange)s, %(descriptor)s) 
RETURNING *;