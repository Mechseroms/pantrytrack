INSERT INTO %%site_name%%_recipes
(name, author, description, creation_date, instructions, picture_path) 
VALUES (%(name)s, %(author)s, %(description)s, %(creation_date)s, %(instructions)s, %(picture_path)s) 
RETURNING *;