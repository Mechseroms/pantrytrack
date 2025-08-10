WITH passed_id AS (SELECT %s AS passed_id),
    sum_cte AS (
      SELECT mi.id, SUM(mil.quantity_on_hand)::FLOAT8 AS total_sum
      FROM %%site_name%%_item_locations mil
      JOIN %%site_name%%_items mi ON mil.part_id = mi.id
      GROUP BY mi.id
    ),
    cte_recipe_items AS (
            SELECT items.*,
            /*COALESCE(%%site_name%%_items.barcode, items.uuid) AS uuid,*/
            (SELECT COALESCE(row_to_json(units.*), '{}') FROM units WHERE units.id=%%site_name%%_item_info.uom) AS item_uom,
            COALESCE(%%site_name%%_items.item_name, items.item_name) AS item_name,
            COALESCE(%%site_name%%_items.links, items.links) AS links,
            row_to_json(units.*) as uom,
            (SELECT COALESCE(array_agg(jsonb_build_object('conversion', conv, 'unit', units)), '{}')
                FROM %%site_name%%_conversions conv
                LEFT JOIN units ON conv.uom_id = units.id
                WHERE conv.item_id = %%site_name%%_items.id) AS conversions,
            COALESCE(sum_cte.total_sum, 0.0) AS quantity_on_hand
            FROM %%site_name%%_recipe_items items
            LEFT JOIN %%site_name%%_items ON items.item_id = %%site_name%%_items.id
            LEFT JOIN %%site_name%%_item_info ON %%site_name%%_items.item_info_id = %%site_name%%_item_info.id
            LEFT JOIN units ON units.id =  items.uom
            LEFT JOIN sum_cte ON %%site_name%%_items.id = sum_cte.id
            WHERE items.rp_id = (SELECT passed_id FROM passed_id)
            ORDER BY items.item_name ASC
        )
    

SELECT (SELECT passed_id FROM passed_id) AS passed_id,
     %%site_name%%_recipes.*,
     logins.username as author,
     (SELECT COALESCE(array_agg(row_to_json(ris)), '{}') FROM cte_recipe_items ris) AS recipe_items
FROM %%site_name%%_recipes
JOIN logins ON %%site_name%%_recipes.author = logins.id
WHERE %%site_name%%_recipes.id=(SELECT passed_id FROM passed_id)