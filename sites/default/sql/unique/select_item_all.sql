SELECT * FROM %sitename%_items 
    LEFT JOIN %sitename%_logistics_info ON %sitename%_items.logistics_info_id = %sitename%_logistics_info.id 
    LEFT JOIN %sitename%_item_info ON %sitename%_items.item_info_id = %sitename%_item_info.id 
    LEFT JOIN %sitename%_food_info ON %sitename%_items.food_info_id = %sitename%_food_info.id 
WHERE %sitename%_items.id=%s;

/*
00 - item_id
01 - barcode
02 - item_name
03 - brand (id)
04 - tags
05 - links
06 - item_info_id
07 - logistics_info_id
08 - food_info_id
09 - row_type
10 - item_type
11 - search_string
12 - logistics_info_id
13 - barcode
14 - primary_location
15 - auto_issue_location
16 - dynamic_locations
17 - location_data
18 - quantity_on_hand
19 - item_info_id
20 - barcode
21 - linked_items
22 - shopping_lists
23 - recipes
24 - groups
25 - packaging
26 - uom
27 - cost
28 - safety_stock
29 - lead_time_days
30 - ai_pick
31 - food_info_id
32 - food_groups
33 - ingrediants
34 - nutrients
35 - expires
*/