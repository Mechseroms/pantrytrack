INSERT INTO %%site_name%%_food_info
(ingrediants, food_groups, nutrients, expires, default_expiration) 
VALUES (%(ingrediants)s, %(food_groups)s, %(nutrients)s, %(expires)s, %(default_expiration)s) 
RETURNING *;