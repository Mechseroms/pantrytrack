INSERT INTO %%site_name%%_recipes
(name, author, description, creation_date, instructions, picture_path) 
VALUES (%s, %s, %s, %s, %s, %s) 
RETURNING *;