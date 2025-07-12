WITH passed_id AS (SELECT %s AS passed_id),
    cte_sl_items AS (
            SELECT items.*, 
            (SELECT COALESCE(row_to_json(un), '{}') FROM units un WHERE un.id = items.uom LIMIT 1) AS uom
            FROM %%site_name%%_shopping_list_items items
            WHERE items.sl_id = (SELECT passed_id FROM passed_id)
        )

SELECT (SELECT passed_id FROM passed_id) AS passed_id,
     %%site_name%%_shopping_lists.*,
     logins.username as author,
     (SELECT COALESCE(array_agg(row_to_json(slis)), '{}') FROM cte_sl_items slis) AS sl_items  
FROM %%site_name%%_shopping_lists
JOIN logins ON %%site_name%%_shopping_lists.author = logins.id
WHERE %%site_name%%_shopping_lists.id=(SELECT passed_id FROM passed_id)