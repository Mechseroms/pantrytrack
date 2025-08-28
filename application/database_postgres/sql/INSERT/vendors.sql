INSERT INTO %%site_name%%_vendors
(vendor_name, vendor_address, vendor_creation_date, vendor_created_by, vendor_phone_number) 
VALUES (%(vendor_name)s, %(vendor_address)s, %(vendor_creation_date)s, %(vendor_created_by)s, %(vendor_phone_number)s) 
RETURNING *;