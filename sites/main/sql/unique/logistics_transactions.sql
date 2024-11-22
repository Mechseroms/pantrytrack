UPDATE main_logistics_info 
SET quantity_on_hand = %s, location_data = %s 
WHERE id = %s;
