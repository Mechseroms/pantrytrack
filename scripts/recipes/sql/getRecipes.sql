SELECT *,
    (SELECT COALESCE(array_agg(row_to_json(g)), '{}') FROM %%site_name%%_recipe_items g WHERE rp_id = %%site_name%%_recipes.id) AS rp_items
 FROM %%site_name%%_recipes LIMIT %s OFFSET %s;