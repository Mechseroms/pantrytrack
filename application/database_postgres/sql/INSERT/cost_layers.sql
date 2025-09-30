INSERT INTO %%site_name%%_cost_layers
(item_location_uuid, layer_aquisition_date, layer_quantity, layer_cost, layer_currency_type, layer_expires, layer_vendor) 
VALUES (%(item_location_uuid)s::uuid, %(layer_aquisition_date)s, %(layer_quantity)s, %(layer_cost)s, %(layer_currency_type)s, %(layer_expires)s, %(layer_vendor)s) 
RETURNING *;