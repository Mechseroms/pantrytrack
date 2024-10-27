SELECT * FROM test_items 
    LEFT JOIN test_logistics_info ON test_items.logistics_info_id = test_logistics_info.id 
    LEFT JOIN test_item_info ON test_items.item_info_id = test_item_info.id 
    LEFT JOIN test_food_info ON test_items.food_info_id = test_food_info.id 
WHERE test_items.id=%s;

/*
00 - item_id
01 - barcode
02 - item_name
03 - brand (id)
04 - description
05 - tags
06 - links
07 - item_info_id
08 - logistics_info_id
09 - food_info_id
10 - row_type
11 - item_type
12 - search_string
13 - logistics_info_id
14 - barcode
15 - primary_location
16 - auto_issue_location
17 - dynamic_locations
18 - location_data
19 - quantity_on_hand
20 - item_info_id
21 - barcode
22 - linked_items
23 - shopping_lists
24 - recipes
25 - groups
26 - packaging
27 - uom
28 - cost
29 - safety_stock
30 - lead_time_days
31 - ai_pick
32 - food_info_id
33 - food_groups
34 - ingrediants
35 - nutrients
36 - expires
*/