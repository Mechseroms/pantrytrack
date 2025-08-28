INSERT INTO %%site_name%%_items
(barcode, item_name, brand, description, tags, links, item_info_id, item_info_uuid, 
logistics_info_id, logistics_info_uuid, food_info_id, food_info_uuid, row_type, item_type, search_string) 
VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
RETURNING *;