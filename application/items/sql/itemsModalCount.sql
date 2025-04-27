SELECT COUNT(item.*) FROM %%site_name%%_items item
WHERE item.search_string LIKE '%%' || %s || '%%';