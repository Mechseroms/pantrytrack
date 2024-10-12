SELECT * FROM main_items 
    LEFT JOIN main_logistics_info ON main_items.logistics_info_id = main_logistics_info.id 
    LEFT JOIN main_item_info ON main_items.item_info_id = main_item_info.id 
    LEFT JOIN main_food_info ON main_items.food_info_id = main_food_info.id 
WHERE main_items.id=%s;

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