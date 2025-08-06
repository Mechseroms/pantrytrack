WITH passed_id AS (SELECT items.id AS passed_id, barcodes.barcode AS passed_barcode FROM %%site_name%%_barcodes barcodes
                    LEFT JOIN %%site_name%%_items items ON items.item_uuid = barcodes.item_uuid 
                    WHERE barcodes.barcode=%s),
    cte_item_locations AS (
            SELECT %%site_name%%_locations.uuid AS location_uuid, %%site_name%%_locations.id AS location_id FROM %%site_name%%_item_locations
            LEFT JOIN %%site_name%%_locations ON %%site_name%%_locations.id = %%site_name%%_item_locations.location_id
            WHERE part_id = (SELECT passed_id FROM passed_id)
        )

SELECT barcodes.*,
    item.id as item_id,
    item.logistics_info_id as logistics_info_id,
    item.item_name as item_name,
    primary_location.id as primary_location_id,
    primary_location.uuid as primary_location_uuid,
    auto_issue_location.id as auto_issue_location_id,
    auto_issue_location.uuid as auto_issue_location_uuid,
    item_info.cost as cost,
    item_info.uom_quantity as uom_quantity,
    (SELECT COALESCE(array_agg(row_to_json(ils)), '{}') FROM cte_item_locations ils) AS item_locations
FROM %%site_name%%_barcodes barcodes
LEFT JOIN %%site_name%%_items item ON barcodes.item_uuid = item.item_uuid
LEFT JOIN %%site_name%%_item_info as item_info ON item_info.id = item.item_info_id
LEFT JOIN %%site_name%%_logistics_info logistics_info ON logistics_info.id = item.logistics_info_id
LEFT JOIN %%site_name%%_locations primary_location ON logistics_info.primary_location = primary_location.id
LEFT JOIN %%site_name%%_locations auto_issue_location ON logistics_info.auto_issue_location = auto_issue_location.id
WHERE barcodes.barcode = (SELECT passed_barcode FROM passed_id);