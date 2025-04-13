INSERT INTO %%site_name%%_food_info
(ingrediants, food_groups, nutrients, expires, default_expiration) 
VALUES (%s, %s, %s, %s, %s) 
RETURNING *;