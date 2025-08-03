INSERT INTO %%site_name%%_receipts
(receipt_id, receipt_status, date_submitted, submitted_by, vendor_id, files) 
VALUES (%s, %s, %s, %s, %s, %s) 
RETURNING *;