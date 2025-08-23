INSERT INTO %%site_name%%_receipts
(receipt_id, receipt_status, date_submitted, submitted_by, vendor_id, files) 
VALUES (%(receipt_id)s, %(receipt_status)s, %(date_submitted)s, %(submitted_by)s, %(vendor_id)s, %(files)s) 
RETURNING *;