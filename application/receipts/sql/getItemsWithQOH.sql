WITH sum_cte AS (
      SELECT mi.id, SUM(mil.quantity_on_hand)::FLOAT8 AS total_sum
      FROM %%site_name%%_item_locations mil
      JOIN %%site_name%%_items mi ON mil.part_id = mi.id
      GROUP BY mi.id
    )

SELECT %%site_name%%_items.*,
    row_to_json(%%site_name%%_item_info.*) as item_info,
    sum_cte.total_sum as total_qoh,
    (SELECT COALESCE(row_to_json(u), '{}')  FROM units as u WHERE u.id=%%site_name%%_item_info.uom) as uom
FROM %%site_name%%_items
LEFT JOIN sum_cte ON %%site_name%%_items.id = sum_cte.id
LEFT JOIN %%site_name%%_item_info ON %%site_name%%_items.item_info_id = %%site_name%%_item_info.id
WHERE %%site_name%%_items.search_string LIKE '%%' || %s || '%%'
    AND %%site_name%%_items.inactive IS false
ORDER BY %%sort_order%%
LIMIT %s OFFSET %s;

