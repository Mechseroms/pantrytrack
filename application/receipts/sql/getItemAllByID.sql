WITH passed_id AS (SELECT id AS passed_id, item_uuid as passed_uuid FROM %%site_name%%_items WHERE id=%s),
    logistics_id AS (SELECT logistics_info_id FROM %%site_name%%_items WHERE id=(SELECT passed_id FROM passed_id)),
    info_id AS (SELECT item_info_id FROM %%site_name%%_items WHERE id=(SELECT passed_id FROM passed_id)),
    cte_conversions AS (
        SELECT 
            %%site_name%%_conversions.id as conv_id,
            %%site_name%%_conversions.conv_factor as conv_factor,
            units.* as uom
        FROM %%site_name%%_conversions
        LEFT JOIN units ON %%site_name%%_conversions.uom_id = units.id
        WHERE %%site_name%%_conversions.item_id = (SELECT passed_id FROM passed_id)
    ),
    cte_item_info AS (
        SELECT 
        %%site_name%%_item_info.*,
        row_to_json(units.*) as uom,
        COALESCE((SELECT json_agg(convs) FROM cte_conversions convs), '[]'::json) AS conversions,
        COALESCE((SELECT json_agg(p.*) FROM %%site_name%%_sku_prefix as p WHERE p.id = ANY(%%site_name%%_item_info.prefixes)), '[]'::json) as prefixes 
        FROM %%site_name%%_item_info
        LEFT JOIN units ON %%site_name%%_item_info.uom = units.id
        WHERE %%site_name%%_item_info.id = (SELECT item_info_id FROM info_id)
    ),
    cte_groups AS (
        SELECT 
            %%site_name%%_groups.*, 
            %%site_name%%_group_items.uuid,
            %%site_name%%_group_items.item_type,
            %%site_name%%_group_items.qty
        FROM %%site_name%%_groups
        JOIN %%site_name%%_group_items ON %%site_name%%_groups.id = %%site_name%%_group_items.gr_id
        WHERE %%site_name%%_group_items.item_id = (SELECT passed_id FROM passed_id)
    ),
    cte_shopping_lists AS (
        SELECT 
            %%site_name%%_shopping_lists.*, 
            %%site_name%%_shopping_list_items.item_type,
            %%site_name%%_shopping_list_items.qty
        FROM %%site_name%%_shopping_lists
        JOIN %%site_name%%_shopping_list_items ON %%site_name%%_shopping_lists.list_uuid = %%site_name%%_shopping_list_items.list_uuid
        WHERE %%site_name%%_shopping_list_items.item_uuid = (SELECT passed_uuid FROM passed_id)
    ),
    cte_itemlinks AS (
        SELECT * FROM %%site_name%%_itemlinks WHERE link=(SELECT passed_id FROM passed_id)
    ),
    cte_item_locations AS (
        SELECT * FROM %%site_name%%_item_locations
        LEFT JOIN %%site_name%%_locations ON %%site_name%%_locations.id = %%site_name%%_item_locations.location_id
        WHERE part_id = (SELECT passed_id FROM passed_id)
    ),
    cte_logistics_info AS (
        SELECT 
        li.*, 
        row_to_json(pl) AS primary_location,
        row_to_json(ail) AS auto_issue_location,
        row_to_json(pz) AS primary_zone,
        row_to_json(aiz) AS auto_issue_zone
        FROM %%site_name%%_logistics_info AS li
        LEFT JOIN %%site_name%%_locations AS pl ON li.primary_location = pl.id
        LEFT JOIN %%site_name%%_locations AS ail ON li.auto_issue_location = ail.id
        LEFT JOIN %%site_name%%_zones AS pz ON li.primary_zone = pz.id
        LEFT JOIN %%site_name%%_zones AS aiz ON li.auto_issue_zone = aiz.id
        WHERE li.id=(SELECT logistics_info_id FROM logistics_id)
    )

SELECT
    (SELECT passed_id FROM passed_id) AS passed_id,
    %%site_name%%_items.*,
    (SELECT COALESCE(row_to_json(logis), '{}') FROM cte_logistics_info logis) AS logistics_info,
    row_to_json(%%site_name%%_food_info.*) as food_info, 
    row_to_json(%%site_name%%_brands.*) as brand,
    (SELECT COALESCE(row_to_json(ii), '{}') FROM cte_item_info ii) AS item_info,
    (SELECT COALESCE(array_agg(row_to_json(g)), '{}') FROM cte_groups g) AS item_groups,
    (SELECT COALESCE(array_agg(row_to_json(sl)), '{}') FROM cte_shopping_lists sl) AS item_shopping_lists,
    (SELECT COALESCE(array_agg(row_to_json(il)), '{}') FROM cte_itemlinks il) AS linked_items,
    (SELECT COALESCE(array_agg(row_to_json(ils)), '{}') FROM cte_item_locations ils) AS item_locations
FROM %%site_name%%_items
    LEFT JOIN %%site_name%%_item_info ON %%site_name%%_items.item_info_id = %%site_name%%_item_info.id 
    LEFT JOIN %%site_name%%_food_info ON %%site_name%%_items.food_info_id = %%site_name%%_food_info.id 
    LEFT JOIN %%site_name%%_brands ON %%site_name%%_items.brand = %%site_name%%_brands.id
    LEFT JOIN units ON %%site_name%%_item_info.uom = units.id 
    LEFT JOIN cte_groups ON %%site_name%%_items.id = cte_groups.id
    LEFT JOIN cte_shopping_lists ON %%site_name%%_items.id = cte_shopping_lists.id
WHERE %%site_name%%_items.id=(SELECT passed_id FROM passed_id)
GROUP BY 
    %%site_name%%_items.id, %%site_name%%_item_info.id, %%site_name%%_food_info.id, %%site_name%%_brands.id;