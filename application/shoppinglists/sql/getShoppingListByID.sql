WITH passed_uuid AS (SELECT %s AS passed_uuid),
    cte_sl_items AS (
            SELECT items.*, 
            (SELECT COALESCE(row_to_json(un), '{}') FROM units un WHERE un.id = items.uom LIMIT 1) AS uom
            FROM %%site_name%%_shopping_list_items items
            WHERE items.list_uuid = (SELECT passed_uuid::uuid FROM passed_uuid)
        )

SELECT (SELECT passed_uuid FROM passed_uuid) AS passed_uuid,
     %%site_name%%_shopping_lists.*,
     logins.username as author,
     (SELECT COALESCE(array_agg(row_to_json(slis)), '{}') FROM cte_sl_items slis) AS sl_items  
FROM %%site_name%%_shopping_lists
JOIN logins ON %%site_name%%_shopping_lists.author = logins.id
WHERE %%site_name%%_shopping_lists.list_uuid=(SELECT passed_uuid::uuid FROM passed_uuid)