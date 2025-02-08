UPDATE %%site_name%%_item_locations
SET cost_layers = array_append(cost_layers, %s), quantity_on_hand = %s
WHERE location_id=%s AND part_id=%s
RETURNING *;