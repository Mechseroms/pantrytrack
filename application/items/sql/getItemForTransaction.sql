WITH parameters AS (SELECT %(item_uuid)s::uuid AS item_uuid),
    cte_item_locations_qty AS (
            SELECT SUM(item_locations.item_quantity_on_hand) AS quantity_on_hand 
            FROM %%site_name%%_item_locations item_locations
            WHERE item_locations.item_uuid = (SELECT item_uuid FROM parameters)
        ),
    cte_item_locations AS (
            SELECT item_locations.item_location_uuid, item_locations.item_quantity_on_hand, locations.location_shortname, zones.zone_uuid, locations.location_uuid
            FROM %%site_name%%_item_locations item_locations
            LEFT JOIN %%site_name%%_locations locations ON locations.location_uuid = item_locations.location_uuid
            LEFT JOIN %%site_name%%_zones zones ON zones.zone_uuid = locations.zone_uuid
            WHERE item_locations.item_uuid = (SELECT item_uuid FROM parameters)
        )

SELECT 
    items.item_uuid, 
    items.item_name, 
    item_info.item_cost,
    (SELECT COALESCE(ilsq.quantity_on_hand, 0.00) FROM cte_item_locations_qty ilsq) AS item_quantity_on_hand,
    COALESCE(units.unit_fullname, 'ERROR') AS unit_fullname,
    (SELECT COALESCE(array_agg(row_to_json(ils)), '{}') FROM cte_item_locations ils) AS item_locations,
    (SELECT COALESCE(row_to_json(zones.*), '{}') FROM %%site_name%%_zones zones WHERE zones.zone_uuid = log_info.item_primary_zone) AS primary_zone,
    (SELECT COALESCE(row_to_json(locations.*), '{}') FROM %%site_name%%_locations locations WHERE locations.location_uuid = log_info.item_primary_location) AS primary_location
FROM %%site_name%%_items items
LEFT JOIN %%site_name%%_item_info item_info ON item_info.item_uuid = items.item_uuid
LEFT JOIN units ON item_info.item_uom = units.unit_uuid
LEFT JOIN %%site_name%%_logistics_info log_info ON log_info.item_uuid = items.item_uuid
WHERE items.item_uuid = (SELECT item_uuid FROM parameters);