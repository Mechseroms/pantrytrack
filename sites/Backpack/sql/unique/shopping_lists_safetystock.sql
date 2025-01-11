WITH sum_cte AS (
  SELECT mi.id, SUM(mil.quantity_on_hand) AS total_sum
  FROM Backpack_item_locations mil
  JOIN Backpack_items mi ON mil.part_id = mi.id
  GROUP BY mi.id
)
SELECT *
FROM Backpack_items
LEFT JOIN Backpack_item_info ON Backpack_items.item_info_id = Backpack_item_info.id
LEFT JOIN sum_cte ON Backpack_items.id = sum_cte.id
WHERE Backpack_item_info.safety_stock > COALESCE(sum_cte.total_sum, 0)
AND Backpack_item_info.shopping_lists @> ARRAY[%s];

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
13 - item_info_id
14 - barcode
15 - linked_items
16 - shopping_lists
17 - recipes
18 - groups
19 - packaging
20 - uom
21 - cost
22 - safety_stock
23 - lead_time_days
24 - ai_pick
25 - sum_cte_id
26 - total_sum/QOH
*/

