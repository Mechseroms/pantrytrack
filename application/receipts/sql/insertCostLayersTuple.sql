INSERT INTO %%site_name%%_cost_layers
(aquisition_date, quantity, cost, currency_type, expires, vendor) 
VALUES (%s, %s, %s, %s, %s, %s) 
RETURNING *;