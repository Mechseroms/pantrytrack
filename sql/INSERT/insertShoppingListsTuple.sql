INSERT INTO %%site_name%%_shopping_lists
(name, description, author, creation_date, type) 
VALUES (%s, %s, %s, %s, %s) 
RETURNING *;