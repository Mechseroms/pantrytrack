WITH sum_cte AS (
      SELECT mi.item_uuid, SUM(mil.quantity_on_hand)::FLOAT8 AS total_sum
      FROM %%site_name%%_item_locations mil
      JOIN %%site_name%%_items mi ON mil.part_id = mi.id
      GROUP BY mi.id
    ),
    cte_recipe_items AS (
        SELECT rp_item.*, COALESCE(sum_cte.total_sum, 0) as quantity_on_hand FROM %%site_name%%_recipe_items rp_item
        LEFT JOIN sum_cte ON sum_cte.item_uuid = rp_item.item_uuid
    )



SELECT *,
    (SELECT COALESCE(array_agg(row_to_json(g)), '{}') FROM cte_recipe_items g WHERE g.rp_id = recipes.id) AS rp_items
FROM %%site_name%%_recipes recipes
LIMIT %s OFFSET %s;