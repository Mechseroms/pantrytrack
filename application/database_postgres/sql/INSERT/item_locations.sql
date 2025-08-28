INSERT INTO %%site_name%%_item_locations
(item_uuid, location_uuid, item_quantity_on_hand) 
VALUES (%(item_uuid)s, %(location_uuid)s, %(item_quantity_on_hand)s)
RETURNING *;