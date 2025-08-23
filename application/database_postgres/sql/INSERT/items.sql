INSERT INTO %%site_name%%_items
(barcode, item_name, brand, description, tags, links, item_info_id, item_info_uuid, 
logistics_info_id, logistics_info_uuid, food_info_id, food_info_uuid, row_type, item_type, search_string) 
VALUES(%(barcode)s, %(item_name)s, %(brand)s, %(description)s, %(tags)s, %(links)s, %(item_info_id)s, %(item_info_uuid)s, 
%(logistics_info_id)s, %(logistics_info_uuid)s, %(food_info_id)s, %(food_info_uuid)s, 
%(row_type)s, %(item_type)s, %(search_string)s) 
RETURNING *;