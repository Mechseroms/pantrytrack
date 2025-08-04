INSERT INTO %%site_name%%_vendors
(vendor_name, vendor_address, creation_date, created_by, phone_number) 
VALUES (%s, %s, %s, %s, %s) 
RETURNING *;