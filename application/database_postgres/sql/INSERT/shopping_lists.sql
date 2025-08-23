INSERT INTO %%site_name%%_shopping_lists
(name, description, author, creation_date, sub_type, list_type) 
VALUES (%(name)s, %(description)s, %(author)s, %(creation_date)s, %(sub_type)s, %(list_type)s) 
RETURNING *;