WITH arguments AS (
  SELECT %s AS year, %s AS month
),
sum_cte AS (
      SELECT mi.item_uuid, SUM(mil.quantity_on_hand)::FLOAT8 AS total_sum
      FROM %%site_name%%_item_locations mil
      JOIN %%site_name%%_items mi ON mil.part_id = mi.id
      GROUP BY mi.id
    ),
cte_recipe_items AS (
        SELECT items.id AS item_id, rp_item.rp_id, rp_item.qty, rp_item.uom AS ingrediant_uom, item_info.uom AS item_uom, COALESCE(sum_cte.total_sum, 0) as quantity_on_hand FROM %%site_name%%_recipe_items rp_item
        LEFT JOIN sum_cte ON sum_cte.item_uuid = rp_item.item_uuid
        LEFT JOIN %%site_name%%_items items ON rp_item.item_uuid = items.item_uuid
        LEFT JOIN %%site_name%%_item_info item_info ON items.item_info_id = item_info.id 
    )
  
SELECT events.*,
      COALESCE(row_to_json(recipes.*), '{}') as recipe,
      COALESCE(ritems.recipe_items, '{}') as recipe_items
FROM %%site_name%%_plan_events events
LEFT JOIN %%site_name%%_recipes recipes ON recipes.recipe_uuid = events.recipe_uuid
LEFT JOIN LATERAL (
  SELECT array_agg(row_to_json(ri.*)) AS recipe_items
  FROM cte_recipe_items ri
  WHERE ri.rp_id = recipes.id
) ritems ON TRUE
WHERE
  event_date_end >= make_date((SELECT year FROM arguments), (SELECT month FROM arguments), 1)
  AND
  event_date_start <  (make_date((SELECT year FROM arguments), (SELECT month FROM arguments), 1) + INTERVAL '1 month');
