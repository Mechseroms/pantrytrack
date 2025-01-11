WITH sum_cte AS (
  SELECT mi.id, SUM(mil.quantity_on_hand) AS total_sum
  FROM main_item_locations mil
  JOIN main_items mi ON mil.part_id = mi.id
  GROUP BY mi.id
)
SELECT COUNT(*)
FROM main_items
LEFT JOIN main_item_info ON main_items.item_info_id = main_item_info.id
LEFT JOIN sum_cte ON main_items.id = sum_cte.id
WHERE main_item_info.safety_stock > COALESCE(sum_cte.total_sum, 0)
AND main_item_info.shopping_lists @> ARRAY[%s];