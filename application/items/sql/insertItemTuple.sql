INSERT INTO %%site_name%%_items
(barcode, item_name, brand, description, tags, links, item_info_id, logistics_info_id, 
food_info_id, row_type, item_type, search_string) 
VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
RETURNING *;