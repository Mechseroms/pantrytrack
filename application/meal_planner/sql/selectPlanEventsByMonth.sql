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
        SELECT rp_item.rp_id, rp_item.qty, COALESCE(sum_cte.total_sum, 0) as quantity_on_hand FROM %%site_name%%_recipe_items rp_item
        LEFT JOIN sum_cte ON sum_cte.item_uuid = rp_item.item_uuid
    ), 
recipe_missing_items AS (
  SELECT
    rp_id, bool_or(qty > quantity_on_hand) AS has_missing_ingredients
  FROM cte_recipe_items
  GROUP BY rp_id
)

SELECT events.*,
      COALESCE(row_to_json(recipes.*), '{}') as recipe,
      COALESCE(recipe_missing_items.has_missing_ingredients, FALSE) AS has_missing_ingredients
FROM %%site_name%%_plan_events events
LEFT JOIN %%site_name%%_recipes recipes ON recipes.recipe_uuid = events.recipe_uuid
LEFT JOIN recipe_missing_items ON recipe_missing_items.rp_id = recipes.id
WHERE
  event_date_end >= make_date((SELECT year FROM arguments), (SELECT month FROM arguments), 1)
  AND
  event_date_start <  (make_date((SELECT year FROM arguments), (SELECT month FROM arguments), 1) + INTERVAL '1 month');
