WITH passed_id AS (SELECT %s AS passed_id),
    cte_item_locations AS (
        SELECT DISTINCT ils.location_id FROM %%site_name%%_item_locations ils
        WHERE ils.part_id = (SELECT passed_id FROM passed_id)
    ),
    cte_locations AS (
        SELECT DISTINCT locations.zone_id FROM %%site_name%%_locations locations
        WHERE locations.id IN (SELECT location_id FROM cte_item_locations)
    )

SELECT COUNT(DISTINCT zone.*) FROM cte_locations cil
JOIN %%site_name%%_zones zone ON cil.zone_id = zone.id
LIMIT %s OFFSET %s;
