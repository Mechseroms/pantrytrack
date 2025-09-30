WITH passed_uuid AS (SELECT %(item_uuid)s::uuid AS passed_uuid),
    cte_conversions AS (
        SELECT *
        FROM %%site_name%%_conversions conversion
        WHERE conversion.item_uuid = (SELECT passed_uuid FROM passed_uuid)
    ),
    cte_item_info AS (SELECT item_info.*,
        COALESCE((SELECT json_agg(convs) FROM cte_conversions convs), '[]'::json) AS conversions,
        COALESCE((SELECT json_agg(p.*) FROM %%site_name%%_sku_prefix p WHERE p.sku_prefix_uuid = ANY(item_info.item_prefixes)), '[]'::json) as prefixes
        FROM %%site_name%%_item_info item_info
        WHERE item_info.item_uuid = (SELECT passed_uuid FROM passed_uuid) 
    ),
    cte_food_info AS (SELECT *
        FROM %%site_name%%_food_info food_info
        WHERE food_info.item_uuid = (SELECT passed_uuid FROM passed_uuid) 
    ),
    cte_logistics_info AS (SELECT *
        FROM %%site_name%%_logistics_info log_info
        WHERE log_info.item_uuid = (SELECT passed_uuid FROM passed_uuid) 
    ),
    cte_item_locations AS (
        SELECT * FROM %%site_name%%_item_locations item_locations
        LEFT JOIN %%site_name%%_locations locations ON locations.location_uuid = item_locations.location_uuid
        WHERE item_locations.item_uuid = (SELECT passed_uuid FROM passed_uuid)
    ),
    cte_barcodes AS (
        SELECT 
        barcode.barcode As barcode,
        barcode.in_exchange AS in_exchange,
        barcode.out_exchange AS out_exchange,
        barcode.descriptor AS descriptor
        FROM %%site_name%%_barcodes AS barcode
        LEFT JOIN %%site_name%%_items AS item ON item.item_uuid = (SELECT passed_uuid FROM passed_uuid)
        WHERE barcode.item_uuid = item.item_uuid
    )

SELECT item.*,
(SELECT COALESCE(row_to_json(ii), '{}') FROM cte_item_info ii) AS item_info,
(SELECT COALESCE(row_to_json(fi), '{}') FROM cte_food_info fi) AS food_info,
(SELECT COALESCE(row_to_json(li), '{}') FROM cte_logistics_info li) AS logistics_info,
(SELECT COALESCE(array_agg(row_to_json(ils)), '{}') FROM cte_item_locations ils) AS item_locations,
(SELECT COALESCE(array_agg(row_to_json(bar)), '{}') FROM cte_barcodes bar) AS item_barcodes
FROM %%site_name%%_items item
WHERE item.item_uuid=(SELECT passed_uuid FROM passed_uuid)
