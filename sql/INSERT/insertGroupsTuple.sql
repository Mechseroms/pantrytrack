INSERT INTO %%site_name%%_groups
(name, description, group_type) 
VALUES (%s, %s, %s) 
RETURNING *;