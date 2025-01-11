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
WHERE Backpack_item_info.shopping_lists @> ARRAY[%s];