INSERT INTO %%site_name%%_vendors
(vendor_name, vendor_address, creation_date, created_by, phone_number) 
VALUES (%(vendor_name)s, %(vendor_address)s, %(creation_date)s, %(created_by)s, %(phone_number)s) 
RETURNING *;