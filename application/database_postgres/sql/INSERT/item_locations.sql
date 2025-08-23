INSERT INTO %%site_name%%_item_locations
(part_id, location_id, quantity_on_hand, cost_layers) 
VALUES (%(part_id)s, %(location_id)s, %(quantity_on_hand)s, %(cost_layers)s)
RETURNING *;