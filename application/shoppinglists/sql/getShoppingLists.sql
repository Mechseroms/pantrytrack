SELECT *,
    (SELECT COALESCE(array_agg(row_to_json(g)), '{}') FROM %%site_name%%_shopping_list_items g WHERE sl_id = %%site_name%%_shopping_lists.id) AS sl_items
 FROM %%site_name%%_shopping_lists LIMIT %s OFFSET %s;