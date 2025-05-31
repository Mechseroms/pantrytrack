INSERT INTO %%site_name%%_item_locations
(part_id, location_id, quantity_on_hand, cost_layers) 
VALUES (%s, %s, %s, %s)
RETURNING *;