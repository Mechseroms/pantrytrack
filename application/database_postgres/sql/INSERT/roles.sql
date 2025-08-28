INSERT INTO roles
(role_name, role_description, role_site_uuid, role_flags) 
VALUES (%(role_name)s, %(role_description)s, %(role_site_uuid)s, %(role_flags)s) 
RETURNING *;