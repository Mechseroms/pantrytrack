SELECT *,
    (SELECT COALESCE(array_agg(row_to_json(g)), '{}') FROM %%site_name%%_group_items g WHERE gr_id = %%site_name%%_groups.id) AS gr_items
 FROM %%site_name%%_groups LIMIT %s OFFSET %s;