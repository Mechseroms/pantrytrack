INSERT INTO %%site_name%%_logistics_info
(barcode, primary_location, primary_zone, auto_issue_location, auto_issue_zone) 
VALUES (%(barcode)s, %(primary_location)s, %(primary_zone)s, %(auto_issue_location)s, %(auto_issue_zone)s) 
RETURNING *;