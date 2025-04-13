UPDATE %%site_name%%_item_locations
SET cost_layers = %s, quantity_on_hand = %s
WHERE part_id=%s AND location_id=%s
RETURNING *;