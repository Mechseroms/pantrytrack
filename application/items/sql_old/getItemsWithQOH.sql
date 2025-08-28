WITH sum_cte AS (
      SELECT mi.id, SUM(mil.quantity_on_hand)::FLOAT8 AS total_sum
      FROM %%site_name%%_item_locations mil
      JOIN %%site_name%%_items mi ON mil.part_id = mi.id
      GROUP BY mi.id
    )

SELECT item.id, item.description, item.item_name, sum_cte.total_sum as total_qoh, u.fullname
FROM %%site_name%%_items item
LEFT JOIN sum_cte ON item.id = sum_cte.id
LEFT JOIN %%site_name%%_item_info item_info ON item.item_info_id = item_info.id
LEFT JOIN units u ON item_info.uom = u.id
WHERE item.search_string LIKE '%%' || %s || '%%'
  AND item.inactive IS false
ORDER BY %%sort_order%%
LIMIT %s OFFSET %s;

