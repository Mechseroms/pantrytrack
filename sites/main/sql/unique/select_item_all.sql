SELECT * FROM main_items 
    LEFT JOIN main_logistics_info ON main_items.logistics_info_id = main_logistics_info.id 
    LEFT JOIN main_item_info ON main_items.item_info_id = main_item_info.id 
    LEFT JOIN main_food_info ON main_items.food_info_id = main_food_info.id 
WHERE main_items.id=%s;