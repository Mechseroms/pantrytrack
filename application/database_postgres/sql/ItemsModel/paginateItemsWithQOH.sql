WITH sum_cte AS (
      SELECT items.item_uuid, SUM(items_locations.item_quantity_on_hand)::FLOAT8 AS total_sum
      FROM %%site_name%%_item_locations items_locations
      JOIN %%site_name%%_items items ON items_locations.item_uuid = items.item_uuid
      GROUP BY items.item_uuid
    )

SELECT items.item_uuid, items.item_description, items.item_name, sum_cte.total_sum as quantity_on_hand, units.unit_fullname
FROM %%site_name%%_items items
LEFT JOIN sum_cte ON items.item_uuid = sum_cte.item_uuid
LEFT JOIN %%site_name%%_item_info item_info ON items.item_uuid = item_info.item_uuid
LEFT JOIN units ON item_info.item_uom = units.unit_uuid
WHERE items.item_search_string LIKE '%%' || %(search_string)s || '%%'
  AND items.item_inactive IS false
ORDER BY %%sort_order%%
LIMIT %(limit)s OFFSET %(offset)s;

