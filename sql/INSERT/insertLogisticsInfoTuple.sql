INSERT INTO %%site_name%%_logistics_info
(barcode, primary_location, primary_zone, auto_issue_location, auto_issue_zone) 
VALUES (%s, %s, %s, %s, %s) 
RETURNING *;