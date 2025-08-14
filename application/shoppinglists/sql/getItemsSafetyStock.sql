WITH sum_cte AS (
  SELECT mi.id, SUM(mil.quantity_on_hand) AS total_sum
  FROM %%site_name%%_item_locations mil
  JOIN %%site_name%%_items mi ON mil.part_id = mi.id
  GROUP BY mi.id
)
SELECT %%site_name%%_items.*,
    COALESCE(row_to_json(%%site_name%%_item_info.*), '{}') AS item_info,
    COALESCE(sum_cte.total_sum, 0) AS total_sum,
    units.fullname AS uom_fullname
FROM %%site_name%%_items
LEFT JOIN %%site_name%%_item_info ON %%site_name%%_items.item_info_id = %%site_name%%_item_info.id
LEFT JOIN units ON units.id = %%site_name%%_item_info.uom
LEFT JOIN sum_cte ON %%site_name%%_items.id = sum_cte.id
WHERE %%site_name%%_item_info.safety_stock > COALESCE(sum_cte.total_sum, 0);
