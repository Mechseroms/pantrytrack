INSERT INTO %%site_name%%_itemlinks
(barcode, link, data, conv_factor) 
VALUES (%s, %s, %s, %s) 
RETURNING *;