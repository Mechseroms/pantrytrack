WITH sum_cte AS (
  SELECT mi.id, SUM(mil.quantity_on_hand) AS total_sum
  FROM %sitename%_item_locations mil
  JOIN %sitename%_items mi ON mil.part_id = mi.id
  GROUP BY mi.id
)
SELECT COUNT(*)
FROM %sitename%_items
LEFT JOIN %sitename%_item_info ON %sitename%_items.item_info_id = %sitename%_item_info.id
LEFT JOIN sum_cte ON %sitename%_items.id = sum_cte.id
WHERE %sitename%_item_info.safety_stock > COALESCE(sum_cte.total_sum, 0)
AND %sitename%_item_info.shopping_lists @> ARRAY[%s];