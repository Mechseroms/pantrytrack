INSERT INTO %%site_name%%_groups
(name, description, included_items, group_type) 
VALUES (%s, %s, %s, %s) 
RETURNING *;