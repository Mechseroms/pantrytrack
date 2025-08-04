INSERT INTO roles
(role_name, role_description, site_id, flags) 
VALUES (%s, %s, %s, %s) 
RETURNING *;