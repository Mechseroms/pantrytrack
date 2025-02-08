INSERT INTO %%site_name%%_logistics_info
(barcode, primary_location, auto_issue_location, dynamic_locations, 
location_data, quantity_on_hand) 
VALUES (%s, %s, %s, %s, %s, %s) 
RETURNING *;