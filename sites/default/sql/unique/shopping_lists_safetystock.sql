WITH sum_cte AS (
  SELECT mi.id, SUM(mil.quantity_on_hand) AS total_sum
  FROM %sitename%_item_locations mil
  JOIN %sitename%_items mi ON mil.part_id = mi.id
  GROUP BY mi.id
)
SELECT *
FROM %sitename%_items
LEFT JOIN %sitename%_item_info ON %sitename%_items.item_info_id = %sitename%_item_info.id
LEFT JOIN sum_cte ON %sitename%_items.id = sum_cte.id
WHERE %sitename%_item_info.safety_stock > COALESCE(sum_cte.total_sum, 0)
AND %sitename%_item_info.shopping_lists @> ARRAY[%s];

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

