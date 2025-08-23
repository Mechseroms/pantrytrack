INSERT INTO %%site_name%%_cost_layers
(aquisition_date, quantity, cost, currency_type, expires, vendor) 
VALUES (%(aquisition_date)s, %(quantity)s, %(cost)s, %(currency_type)s, %(expires)s, %(vendor)s) 
RETURNING *;