WITH sum_cte AS (
  SELECT mi.id, SUM(mil.quantity_on_hand) AS total_sum
  FROM %%site_name%%_item_locations mil
  JOIN %%site_name%%_items mi ON mil.part_id = mi.id
  GROUP BY mi.id
)

SELECT items.*,
    COALESCE(row_to_json(item_info.*), '{}') AS item_info,
    COALESCE(sum_cte.total_sum, 0) AS total_sum
FROM %%site_name%%_items items
LEFT JOIN %%site_name%%_item_info item_info ON items.item_info_id = item_info.id
LEFT JOIN units ON units.id = item_info.uom
LEFT JOIN sum_cte ON items.id = sum_cte.id
WHERE items.item_uuid = %(item_uuid)s