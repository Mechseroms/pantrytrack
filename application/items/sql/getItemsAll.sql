WITH sum_cte AS (
      SELECT mi.id, SUM(mil.quantity_on_hand)::FLOAT8 AS total_sum
      FROM %%site_name%%_item_locations mil
      JOIN %%site_name%%_items mi ON mil.part_id = mi.id
      GROUP BY mi.id
    )

SELECT * FROM %%site_name%%_items items
LEFT JOIN %%site_name%%_item_info item_info ON item_info.id = items.item_info_id
LEFT JOIN %%site_name%%_food_info food_info ON food_info.id = items.food_info_id
LEFT JOIN %%site_name%%_logistics_info logistics_info ON logistics_info.id = items.logistics_info_id
LEFT JOIN %%site_name%%_brands brands ON brands.id = items.brand
LEFT JOIN sum_cte ON items.id = sum_cte.id;
