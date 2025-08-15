INSERT INTO %%site_name%%_shopping_lists
(name, description, author, creation_date, sub_type, list_type) 
VALUES (%s, %s, %s, %s, %s, %s) 
RETURNING *;