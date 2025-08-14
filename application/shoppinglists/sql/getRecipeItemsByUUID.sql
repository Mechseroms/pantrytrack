WITH passed_id AS (SELECT recipes.id AS passed_id FROM %%site_name%%_recipes recipes WHERE recipes.recipe_uuid = %s::uuid)
SELECT
     COALESCE(item_info.uom, recipe_items.uom) as uom,
     COALESCE(items.links, recipe_items.links) as links,
     COALESCE(items.item_uuid, recipe_items.item_uuid) as item_uuid,
     COALESCE(items.item_name, recipe_items.item_name) as item_name,
     recipe_items.qty as qty
FROM %%site_name%%_recipe_items recipe_items
LEFT JOIN %%site_name%%_items items ON items.item_uuid = recipe_items.item_uuid
LEFT JOIN %%site_name%%_item_info item_info ON item_info.id = items.item_info_id
WHERE recipe_items.rp_id=(SELECT passed_id FROM passed_id);